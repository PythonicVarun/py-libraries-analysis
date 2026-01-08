#!/bin/bash

set -u

# Configuration
JSON_FILE="${1:-repos.json}"
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
}
trap cleanup EXIT

# Checks
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required.${NC}"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is required.${NC}"
    exit 1
fi

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
    output_file="$OUTPUT_DIR/${folder_name}.json"

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
    fi

    # Run Analysis
    echo "   Running ty check..."

    temp_file=$(mktemp)
    uv run ty check --output-format gitlab "$clone_path" > "$temp_file" 2> /dev/null
    tool_exit_code=$?

    # Check if the file contains valid JSON
    if jq -c . "$temp_file" > "$output_file" 2>/dev/null; then
        if [ $tool_exit_code -eq 0 ]; then
             echo -e "${YELLOW}   Success: Report generated (No typos found).${NC}"
        else
             echo -e "${GREEN}   Success: Report generated (Typos found).${NC}"
        fi
        ((success++))
    else
        echo -e "${RED}   Failed: Tool crashed or produced invalid output.${NC}"
        ((failed++))
        failed_repos+=("$project (Invalid Output)")
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
