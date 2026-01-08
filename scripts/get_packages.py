import json
import os
from pathlib import Path

import requests


def get_top_packages(n: int) -> dict:
    params = {"user": "demo", "default_format": "JSON"}

    query = f"""
        SELECT 
            SUM(t1.count) AS downloads, 
            t1.project, 
            CONCAT('https://github.com/', t2.repo_name) as repo
        FROM pypi.pypi_downloads AS t1
        JOIN pypi.project_to_repo_name AS t2 
            ON t1.project = t2.project
        GROUP BY t1.project, t2.repo_name
        ORDER BY downloads DESC
        LIMIT {n}
    """

    response = requests.post(
        "https://sql-clickhouse.clickhouse.com", params=params, data=query
    )
    response.raise_for_status()
    return response.json()


def save_to_json(data: dict, filename: str) -> None:
    dir, _ = os.path.split(filename)
    Path(dir).mkdir(parents=True, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(data, f)


def main() -> None:
    data = get_top_packages(10)
    save_to_json(data["data"], "dataset/top-pypi-packages.json")


if __name__ == "__main__":
    main()
