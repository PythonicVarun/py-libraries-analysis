# Python Libraries Analysis

> [!Note]
> **Data Attribution:** Top PyPI packages data sourced from the [ClickHouse's ClickPy](https://clickpy.clickhouse.com/).


Static code quality audit of the most-downloaded PyPI libraries. Code quality analysis done using [ty (Astral)](https://docs.astral.sh/ty/) and severity mapping, visualized via interactive error-density treemaps.

## Project Structure

- `dataset/`: Contains the list of top PyPI packages.
- `scripts/`: Scripts to fetch package data, run analysis, and generate visualization data.
- `ty_outputs/`: Raw JSON output from `ty` analysis for each package.
- `visualizer/`: Web-based visualization of the analysis results.

## Requirements

- Python >= 3.12
- `uv` (for package management)
- `jq` (required for `generate_json_report.sh`)

## Setup & Usage

1.  **Install System Dependencies**

    ```bash
    sudo apt-get update && sudo apt-get install -y jq
    ```

2.  **Install Python Dependencies**

    ```bash
    uv sync
    ```

    *All python scripts should be run using `uv run script_name.py` to ensure dependencies are available.*

3.  **Fetch Top Packages** (Optional)

    The `dataset/top-pypi-packages.json` is already provided. To refresh it using the public ClickHouse PyPI dataset:

    ```bash
    uv run scripts/get_packages.py
    ```

4.  **Run Static Analysis**

    This script clones each repository listed in the dataset, runs `ty`, and saves the output to `ty_outputs/`.

    ```bash
    # Ensure usage permissions
    chmod +x scripts/generate_json_report.sh
    
    # Run the script
    ./scripts/generate_json_report.sh
    ```

5.  **Generate Visualization Data**

    Process the raw analysis results into a format suitable for the visualization.

    ```bash
    uv run scripts/generate_treemap_data.py
    ```

6.  **View Visualization**

    View the [live demo](https://pythonicvarun.github.io/py-libraries-analysis/) or open [`visualizer/index.html`](visualizer/index.html) locally to explore the interactive error-density treemap.
