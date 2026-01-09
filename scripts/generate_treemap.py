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
df_counts = (
    df.groupby(["severity", "check_name", "package"])
    .agg(
        count=("package", "size"),
        examples=(
            "description",
            lambda x: "<br>".join(
                [f"    • {d}" for d in x.unique()[:5]]
            ),
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
    custom_data=["severity", "examples"],
)

fig.update_traces(
    hovertemplate="<b>%{label}</b><br><br><b>Count:</b> %{value}<br><b>Severity:</b> %{customdata[0]}<br><b>Examples:</b><br>%{customdata[1]}<extra></extra>",
    marker=dict(
        cornerradius=3,
        line=dict(width=1, color='white')
    ),
)

fig.update_layout(
    margin=dict(t=80, l=25, r=25, b=25),
    title=dict(
        text="Error Frequency Treemap (Size=Frequency, Color=Severity)",
        font=dict(size=24, family="Arial, sans-serif", color="#2d3748"),
        x=0.5,
        xanchor='center',
        y=0.98,
        yanchor='top'
    ),
    font=dict(family="Arial, sans-serif", size=12, color="#2d3748"),
    paper_bgcolor='white',
    plot_bgcolor='white',
    height=1000,
)

# statistics
total_errors = df_counts['count'].sum()
unique_packages = df_counts['package'].nunique()
unique_error_types = df_counts['check_name'].nunique()
severity_counts = df_counts.groupby('severity')['count'].sum().to_dict()

existing_severities = df_counts['severity'].unique()

# Severity descriptions
severity_info = {
    "blocker": {
        "label": "Blocker",
        "color": color_discrete_map["blocker"],
        "description": "Critical blocker issues - must be fixed immediately",
        "icon": "🚫"
    },
    "critical": {
        "label": "Critical",
        "color": color_discrete_map["critical"],
        "description": "Critical errors requiring immediate attention",
        "icon": "🔴"
    },
    "major": {
        "label": "Major",
        "color": color_discrete_map["major"],
        "description": "Major issues that should be addressed soon",
        "icon": "🟠"
    },
    "minor": {
        "label": "Minor",
        "color": color_discrete_map["minor"],
        "description": "Minor issues - recommended fixes",
        "icon": "🟡"
    },
    "info": {
        "label": "Info",
        "color": color_discrete_map["info"],
        "description": "Informational messages and suggestions",
        "icon": "ℹ️"
    },
    "unknown": {
        "label": "unknown",
        "color": color_discrete_map["unknown"],
        "description": "Unclassified or unknown severity",
        "icon": "❓"
    }
}

stats_cards_html = f"""
    <div class="stat-card primary">
        <h3>Total Errors</h3>
        <p>{total_errors:,}</p>
        <span>Across all packages</span>
    </div>
"""

# severity-specific cards
for severity in ["blocker", "critical", "major", "minor", "info", "unknown"]:
    if severity in severity_counts:
        info = severity_info[severity]
        count = severity_counts[severity]
        stats_cards_html += f"""
    <div class="stat-card severity-{severity}">
        <h3>{info['icon']} {info['label']}</h3>
        <p>{count:,}</p>
        <span>{count/total_errors*100:.1f}% of total</span>
    </div>
"""

stats_cards_html += f"""
    <div class="stat-card info-card">
        <h3>📦 Packages</h3>
        <p>{unique_packages:,}</p>
        <span>Unique packages analyzed</span>
    </div>
    <div class="stat-card info-card">
        <h3>🔍 Error Types</h3>
        <p>{unique_error_types:,}</p>
        <span>Distinct error categories</span>
    </div>
"""

legend_items_html = ""
for severity in ["blocker", "critical", "major", "minor", "info", "unknown"]:
    if severity in existing_severities:
        info = severity_info[severity]
        legend_items_html += f"""
    <div class="severity-item">
        <div class="severity-color" style="background: {info['color']};"></div>
        <span>{info['icon']} <strong>{info['label']}</strong> - {info['description']}</span>
    </div>
"""

# CSS Styling
css_style = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        min-height: 100vh;
    }

    .visualization-container {
        max-width: 1600px;
        margin: 0 auto;
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }

    .viz-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px 40px;
        color: white;
    }

    .viz-header h1 {
        margin: 0 0 12px 0;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .viz-header p {
        margin: 0;
        font-size: 16px;
        opacity: 0.95;
        font-weight: 300;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        padding: 30px 40px;
        background: #f7fafc;
        border-bottom: 1px solid #e2e8f0;
    }

    .stat-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    .stat-card.primary { border-left-color: #667eea; }
    .stat-card.severity-blocker { border-left-color: #C62828; }
    .stat-card.severity-critical { border-left-color: #E53935; }
    .stat-card.severity-major { border-left-color: #EF7B7B; }
    .stat-card.severity-minor { border-left-color: #FFB74D; }
    .stat-card.severity-info { border-left-color: #64B5F6; }
    .stat-card.severity-unknown { border-left-color: #9E9E9E; }
    .stat-card.info-card { border-left-color: #48bb78; }

    .stat-card h3 {
        margin: 0 0 10px 0;
        font-size: 13px;
        color: #718096;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stat-card p {
        margin: 0;
        font-size: 32px;
        color: #2d3748;
        font-weight: 700;
        line-height: 1;
    }

    .stat-card span {
        display: block;
        margin-top: 8px;
        font-size: 13px;
        color: #a0aec0;
        font-weight: 400;
    }

    .chart-container {
        padding: 40px;
        background: white;
    }

    .severity-legend {
        display: flex;
        gap: 15px;
        padding: 25px 40px;
        background: white;
        border-top: 1px solid #e2e8f0;
        flex-wrap: wrap;
        align-items: flex-start;
    }

    .severity-legend-title {
        font-weight: 600;
        color: #2d3748;
        margin-right: 15px;
        font-size: 15px;
        padding-top: 10px;
    }

    .severity-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13px;
        color: #4a5568;
        padding: 10px 16px;
        background: #f7fafc;
        border-radius: 8px;
        transition: background 0.2s;
        max-width: 400px;
    }

    .severity-item:hover {
        background: #edf2f7;
    }

    .severity-color {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
        flex-shrink: 0;
    }

    .footer {
        padding: 20px 40px;
        background: #f7fafc;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        color: #718096;
        font-size: 13px;
    }

    .footer a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }

    .footer a:hover {
        text-decoration: underline;
    }

    /* Plotly specific overrides */
    .js-plotly-plot .plotly .main-svg {
        border-radius: 8px;
    }

    @media (max-width: 768px) {
        body { padding: 10px; }
        .viz-header { padding: 25px 20px; }
        .viz-header h1 { font-size: 24px; }
        .stats-grid { padding: 20px; grid-template-columns: 1fr; }
        .chart-container { padding: 20px; }
        .severity-legend { padding: 20px; flex-direction: column; }
        .severity-item { max-width: 100%; }
    }

    @media print {
        body {
            background: white;
            padding: 0;
        }
        .visualization-container {
            box-shadow: none;
            border: 1px solid #e2e8f0;
        }
    }
</style>
"""

html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Package Error Analysis - Treemap Visualization</title>
    {css_style}
</head>
<body>
    <div class="visualization-container">
        <!-- Header Section -->
        <div class="viz-header">
            <h1>Python Package Error Analysis</h1>
            <p>Comprehensive error frequency distribution across top Python packages</p>
        </div>

        <!-- Statistics Cards -->
        <div class="stats-grid">
            {stats_cards_html}
        </div>

        <!-- Treemap Chart -->
        <div class="chart-container">
            {{{{PLOTLY_CHART}}}}
        </div>

        <!-- Severity Legend -->
        <div class="severity-legend">
            <span class="severity-legend-title">Severity Levels:</span>
            {legend_items_html}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><a href="https://github.com/PythonicVarun/py-libraries-analysis" target="_blank" rel="noopener noreferrer">Generated from analysis of top downloaded Python packages</a> • Click on sections to drill down • Hover for detailed information</p>
        </div>
    </div>
</body>
</html>
"""

output_file = "output/index.html"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

chart_html = fig.to_html(include_plotlyjs='cdn', div_id='treemap', full_html=False)
final_html = html_template.replace('{{PLOTLY_CHART}}', chart_html)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"Treemap saved to {output_file}")
print(f"  - Total Errors: {total_errors:,}")
print(f"  - Packages: {unique_packages}")
print(f"  - Error Types: {unique_error_types}")
print(f"  - Severity Breakdown:")
for severity in ["blocker", "critical", "major", "minor", "info", "unknown"]:
    if severity in severity_counts:
        count = severity_counts[severity]
        print(f"     * {severity_info[severity]['label']}: {count:,} ({count/total_errors*100:.1f}%)")
