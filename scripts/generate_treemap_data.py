import json
import os

import pandas as pd

OUTPUT_DIR = "ty_outputs"
json_files = [
    pos_json for pos_json in os.listdir(OUTPUT_DIR) if pos_json.endswith(".json")
]

data = []

print(f"Processing {len(json_files)} files...")

for js in json_files:
    package_name = os.path.splitext(js)[0]
    file_path = os.path.join(OUTPUT_DIR, js)
    try:
        with open(file_path, "r") as f:
            content = json.load(f)
            if isinstance(content, list):
                for item in content:
                    data.append(
                        {
                            "package": package_name,
                            "check_name": item.get("check_name", "unknown"),
                            "severity": item.get("severity", "unknown"),
                            "description": item.get("description", "No description"),
                        }
                    )
    except Exception as e:
        print(f"Error reading {js}: {e}")

if not data:
    print("No data found.")
    exit()

df = pd.DataFrame(data)

# Get unique values for filters
all_packages = sorted(df["package"].unique().tolist())
all_error_types = sorted(df["check_name"].unique().tolist())
df_counts = (
    df.groupby(["severity", "check_name", "package"])
    .agg(
        count=("package", "size"),
        examples=(
            "description",
            lambda x: "<br>".join([f"    • {d}" for d in x.unique()[:5]]),
        ),
    )
    .reset_index()
)

color_discrete_map = {
    "blocker": "#C62828",  # Deep red
    "critical": "#E53935",  # Bright red
    "major": "#EF7B7B",  # Coral
    "minor": "#FFB74D",  # Warm amber
    "info": "#64B5F6",  # Soft blue
    "unknown": "#9E9E9E",  # Neutral gray
}

print("Generating treemap data...")

# statistics
total_errors = df_counts["count"].sum()
unique_packages = df_counts["package"].nunique()
unique_error_types = df_counts["check_name"].nunique()
severity_counts = df_counts.groupby("severity")["count"].sum().to_dict()

existing_severities = df_counts["severity"].unique()

# Severity descriptions
severity_info = {
    "blocker": {
        "label": "Blocker",
        "color": color_discrete_map["blocker"],
        "description": "Critical blocker issues - must be fixed immediately",
        "icon": "🚫",
    },
    "critical": {
        "label": "Critical",
        "color": color_discrete_map["critical"],
        "description": "Critical errors requiring immediate attention",
        "icon": "🔴",
    },
    "major": {
        "label": "Major",
        "color": color_discrete_map["major"],
        "description": "Major issues that should be addressed soon",
        "icon": "🟠",
    },
    "minor": {
        "label": "Minor",
        "color": color_discrete_map["minor"],
        "description": "Minor issues - recommended fixes",
        "icon": "🟡",
    },
    "info": {
        "label": "Info",
        "color": color_discrete_map["info"],
        "description": "Informational messages and suggestions",
        "icon": "ℹ️",
    },
    "unknown": {
        "label": "unknown",
        "color": color_discrete_map["unknown"],
        "description": "Unclassified or unknown severity",
        "icon": "❓",
    },
}


# Prepare data for export
export_data = {
    "records": df_counts.to_dict(orient="records"),
    "stats": {
        "total_errors": int(total_errors),
        "unique_packages": int(unique_packages),
        "unique_error_types": int(unique_error_types),
        "severity_counts": {k: int(v) for k, v in severity_counts.items()},
    },
    "meta": {
        "color_map": color_discrete_map,
        "severity_info": severity_info,
        "existing_severities": existing_severities.tolist(),
    },
}

output_json = "visualizer/data.json"
os.makedirs(os.path.dirname(output_json), exist_ok=True)

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(export_data, f)

print(f"Data saved to {output_json}")
print(f"  - Total Errors: {total_errors:,}")
print(f"  - Packages: {unique_packages}")
print(f"  - Error Types: {unique_error_types}")
print(f"  - Severity Breakdown:")
for severity in ["blocker", "critical", "major", "minor", "info", "unknown"]:
    if severity in severity_counts:
        count = severity_counts[severity]
        print(
            f"     * {severity_info[severity]['label']}: {count:,} ({count/total_errors*100:.1f}%)"
        )
