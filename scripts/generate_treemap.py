import json
import os

import pandas as pd
import plotly.express as px

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
                            "check_name": item.get("check_name", "Unknown"),
                            "severity": item.get("severity", "Unknown"),
                        }
                    )
    except Exception as e:
        print(f"Error reading {js}: {e}")

if not data:
    print("No data found.")
    exit()

df = pd.DataFrame(data)
df_counts = (
    df.groupby(["severity", "check_name", "package"]).size().reset_index(name="count")
)

color_discrete_map = {
    "major": "#8B0000",  # Dark Red
    "minor": "#FF0000",  # Red
    "info": "#FFC0CB",  # Pink
    "Unknown": "#808080",
}

print("Generating treemap...")

# Hierarchy: Severity -> Check Name -> Package
# Size: count (Frequency)
# Color: severity
fig = px.treemap(
    df_counts,
    path=[px.Constant("All Errors"), "severity", "check_name", "package"],
    values="count",
    color="severity",
    color_discrete_map=color_discrete_map,
    title="Error Frequency Treemap (Size=Frequency, Color=Severity)",
    hover_data=["package", "count"],
)

fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

output_file = "output/index.html"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
fig.write_html(output_file)
print(f"Treemap saved to {output_file}")
