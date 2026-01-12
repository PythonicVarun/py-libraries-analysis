#!/bin/bash

set -u

# Configuration
JSON_FILE="${1:-dataset/top-pypi-packages.json}"
OUTPUT_DIR="${2:-ty_outputs}"
CLONE_DIR="${3:-cloned_repos}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Cleanup function to run on exit or interrupt
cleanup() {
    if [[ -d "$CLONE_DIR" ]] && [[ -z "$(ls -A $CLONE_DIR)" ]]; then
        rm -r "$CLONE_DIR"
    fi

    # Deactivate any active virtual environment
    if [[ "${VIRTUAL_ENV:-}" != "" ]]; then
        deactivate 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Checks
for cmd in jq uv git; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is required.${NC}"
        exit 1
    fi
done

if [[ ! -f "$JSON_FILE" ]]; then
    echo -e "${RED}Error: JSON file '$JSON_FILE' not found.${NC}"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$CLONE_DIR"

echo -e "${GREEN}Starting repository processing...${NC}"
echo "-----------------------------------------"

# Counters
total=0
success=0
failed=0
failed_repos=()

# Read JSON and process each repo
while read -r repo_obj; do
    ((total++))

    project=$(echo "$repo_obj" | jq -r '.project')
    repo=$(echo "$repo_obj" | jq -r '.repo')

    echo -e "${BLUE}[$total] Processing: $project${NC}"

    folder_name=$(echo "$project" | sed 's/[^a-zA-Z0-9._-]/_/g')
    clone_path="$CLONE_DIR/$folder_name"
    output_file="$(pwd)/$OUTPUT_DIR/${folder_name}.json"

    # Clone or Pull
    if [[ -d "$clone_path" ]]; then
        echo "   Updating existing repository..."
        if ! (cd "$clone_path" && git pull --quiet); then
             echo -e "${RED}   Failed to pull changes.${NC}"
             ((failed++)); failed_repos+=("$project (Git Pull)"); continue
        fi
    else
        echo "   Cloning repository..."
        if ! git clone --quiet "$repo" "$clone_path"; then
            echo -e "${RED}   Failed to clone repository.${NC}"
            ((failed++)); failed_repos+=("$project (Git Clone)"); continue
        fi

        echo "   Initializing submodules..."
        git submodule update --quiet --init
    fi

    # Start Subshell for Environment Isolation
    (
        cd "$clone_path" || exit 1

        # create a fresh venv to ensure no contamination and correct dependency resolution
        if ! uv venv .venv > /dev/null 2>&1; then
            echo -e "${RED}   Failed to create venv.${NC}"
            exit 101 # Custom error code for venv failure
        fi

        # Activate the environment
        source .venv/bin/activate

        echo "   Installing build tools..."
        uv pip install --upgrade setuptools wheel meson ninja > /dev/null 2>&1

        # Build Package & Install Dependencies
        echo "   Building and installing dependencies..."

        # try to install the package 
        if ! uv pip install . > /dev/null 2>&1; then
             # Fallback: Try installing requirements.txt if present
             echo -e "${YELLOW}   Standard install failed, trying to find requirements...${NC}"
             if [[ -f "requirements.txt" ]]; then
                uv pip install -r requirements.txt > /dev/null 2>&1
             else
                echo -e "${RED}   Build/Install failed (No setup.py or requirements found).${NC}"
                exit 102 # Custom error code for build failure
             fi
        fi

        # run Analysis
        echo "   Running ty check..."

        temp_file=$(mktemp)
        timeout 5m uv run ty check --ignore unresolved-import --output-format gitlab . > "$temp_file" 2> /dev/null
        tool_exit_code=$?

        if [ $tool_exit_code -eq 124 ]; then
            echo -e "${RED}   Failed: Operation timed out.${NC}"
            exit 124
        fi

        # Validate JSON output
        if jq -c . "$temp_file" > "$output_file" 2>/dev/null; then
            if [ $tool_exit_code -eq 0 ]; then
                 echo -e "${YELLOW}   Success: Report generated (No issues found).${NC}"
            else
                 echo -e "${GREEN}   Success: Report generated (Issues found).${NC}"
            fi
            exit 0
        else
            echo -e "${RED}   Failed: Tool crashed or produced invalid output.${NC}"
            exit 103
        fi

        # Remove temp file
        rm -f "$temp_file"
    )

    subshell_exit=$?

    if [ $subshell_exit -eq 0 ]; then
        ((success++))
    elif [ $subshell_exit -eq 101 ]; then
        ((failed++)); failed_repos+=("$project (Venv Creation)")
    elif [ $subshell_exit -eq 102 ]; then
        ((failed++)); failed_repos+=("$project (Build/Install Failed)")
    elif [ $subshell_exit -eq 103 ]; then
        ((failed++)); failed_repos+=("$project (Invalid Output)")
    elif [ $subshell_exit -eq 124 ]; then
        ((failed++)); failed_repos+=("$project (Timeout)")
    else
        ((failed++)); failed_repos+=("$project (Unknown Error)")
    fi

    # Cleanup specific repo
    rm -rf "$clone_path"

    echo ""

done < <(jq -c '.[]' "$JSON_FILE")

# Summary
echo "-----------------------------------------"
echo -e "${GREEN}Processing Complete!${NC}"
echo -e "Total: $total | Success: $success | Failed: $failed"

if [[ ${#failed_repos[@]} -gt 0 ]]; then
    echo -e "\n${RED}Failed Repositories:${NC}"
    for item in "${failed_repos[@]}"; do
        echo " - $item"
    done
fi
