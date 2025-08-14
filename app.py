
import math
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

CSV_PATH = "Tariff.csv"

def to_float(x):
    if pd.isna(x):
        return None
    x = str(x).replace(",", "").replace("%", "").strip()
    try:
        return float(x)
    except:
        return None

def load_data():
    # Read CSV with error handling for malformed lines
    try:
        df = pd.read_csv(CSV_PATH, delimiter=";", engine="python", on_bad_lines='skip')
    except:
        # Fallback: read with different approach
        df = pd.read_csv(CSV_PATH, delimiter=";", engine="python", error_bad_lines=False, warn_bad_lines=True)
    
    df["deficit"] = df["US 2024 Deficit"].apply(to_float)
    df["exports"] = df["US 2024 Exports"].apply(to_float)
    df["imports"] = df["US 2024 Imports (Customs Basis)"].apply(to_float)
    df["tariff_pct"] = df["Adjusted Reciprocal Tariff"].apply(to_float)
    df["response_pct"] = df["Trump Response"].apply(to_float)
    df = df.dropna(subset=["Country"]).reset_index(drop=True)
    return df

def perimeter_positions(n, width=16, height=15):
    """Return n points along a rectangle perimeter (clockwise, starting left-top)."""
    w, h = width, height
    perim = 2*(w+h)
    step = perim / n
    pts, angles = [], []  # also return a text angle for label legibility
    for i in range(n):
        t = i*step
        if t <= h:
            x = -w/2; y = h/2 - t; ang = -90  # left side, rotate vertical
        elif t <= h + w:
            u = t - h; x = -w/2 + u; y = -h/2; ang = 0  # bottom side
        elif t <= h + w + h:
            u = t - (h + w); x = w/2; y = -h/2 + u; ang = 90  # right side
        else:
            u = t - (h + w + h); x = w/2 - u; y = h/2; ang = 0  # top side
        pts.append((x, y)); angles.append(ang)
    return pts, angles

def line_trace_for_country(metric, color, name, tx, ty, value):
    """Return a single line trace from center toward (tx,ty) scaled by |value|."""
    if value is None:
        Lx, Ly = 0, 0
    else:
        dist = (tx**2 + ty**2) ** 0.5
        if dist == 0:
            Lx, Ly = 0, 0
        else:
            # scale length by value relative to max for this metric
            Lx, Ly = tx, ty
    # We scale later when we know global max; placeholder segment (0-> unit vec), then scale via transform
    return go.Scatter(
        x=[0, tx], y=[0, ty],
        mode="lines",
        line=dict(width=3, color=color),
        name=name,
        hoverinfo="text",
        hovertext=name,
        showlegend=False
    )

def build_figure(sort_metric="deficit", show_lines=("deficit","exports","imports")):
    df = load_data()
    # Sort by chosen metric (deficit: ascending -> most negative first; others: descending)
    if sort_metric == "deficit":
        df = df.sort_values(by="deficit", ascending=True)
    elif sort_metric == "tariff_pct":
        df = df.sort_values(by="tariff_pct", ascending=False)
    else:
        df = df.sort_values(by=sort_metric, ascending=False)
    df = df.reset_index(drop=True)

    # Use consistent positioning regardless of visible lines
    pts, text_angles = perimeter_positions(len(df))
    positions = {row["Country"]: pts[i] for i, (_, row) in enumerate(df.iterrows())}

    # Determine global scales for line lengths per metric
    max_vals = {
        "deficit": df["deficit"].abs().max(),
        "exports": df["exports"].abs().max(),
        "imports": df["imports"].abs().max(),
    }

    traces = []

    # For each metric selected, add one trace per country so hover shows value+country
    color_map = {"deficit":"#d62728", "exports":"#2ca02c", "imports":"#1f77b4"}
    for metric in ["deficit","exports","imports"]:
        if metric not in show_lines:
            continue
        for i, row in df.iterrows():
            tx, ty = positions[row["Country"]]
            dist = (tx**2 + ty**2)**0.5 or 1.0
            # unit direction
            ux, uy = tx/dist, ty/dist
            val = row[metric]
            if pd.isna(val) or max_vals[metric] in (0, None) or pd.isna(max_vals[metric]):
                L = 0.0
            else:
                L = dist * (abs(val)/max_vals[metric])
            xs = [0, ux*L]; ys = [0, uy*L]
            hover = f"{row['Country']} — {metric.title()}: ${val:,.1f}K"
            traces.append(go.Scatter(
                x=xs, y=ys, mode="lines",
                line=dict(width=3, color=color_map[metric]),
                opacity=0.5,
                hoverinfo="text", hovertext=hover,
                name=metric.title(), showlegend=False
            ))
            
            # Add small ball at the end of each line
            traces.append(go.Scatter(
                x=[xs[1]], y=[ys[1]], mode="markers",
                marker=dict(size=4, color=color_map[metric], symbol="circle"),
                hoverinfo="skip",
                showlegend=False
            ))

    # Labels: country names with tariff percentages
    xs = [positions[r["Country"]][0] for _, r in df.iterrows()]
    ys = [positions[r["Country"]][1] for _, r in df.iterrows()]
    names = [r["Country"] for _, r in df.iterrows()]
    tariffs = [r["tariff_pct"] if not pd.isna(r["tariff_pct"]) else None for _, r in df.iterrows()]
    
    # Create consistent country positions that don't change when lines are toggled
    country_positions = [(r["Country"], positions[r["Country"]], text_angles[i]) for i, (_, r) in enumerate(df.iterrows())]
    
    # Combine country names with tariff percentages
    combined_labels = []
    for i, (name, tariff, angle) in enumerate(zip(names, tariffs, text_angles)):
        if tariff is not None:
            # For left side labels (angle == -90), put tariff first
            if angle == -90:
                combined_labels.append(f"({int(tariff)}%) {name}")
            else:
                combined_labels.append(f"{name} ({int(tariff)}%)")
        else:
            combined_labels.append(name)
    
    # Create text traces with proper rotation
    name_traces = []
    annotations = []
    
    for i, (country, (x, y), angle) in enumerate(country_positions):
        # Get the label for this country
        row = df.iloc[i]
        name = row["Country"]
        tariff = row["tariff_pct"] if not pd.isna(row["tariff_pct"]) else None
        
        # Create the label
        if tariff is not None:
            if angle == -90:  # left side
                label = f"({int(tariff)}%) {name}"
            else:
                label = f"{name} ({int(tariff)}%)"
        else:
            label = name
        # Create hover text with all values for this country
        row = df.iloc[i]
        deficit_val = row["deficit"] if not pd.isna(row["deficit"]) else 0
        exports_val = row["exports"] if not pd.isna(row["exports"]) else 0
        imports_val = row["imports"] if not pd.isna(row["imports"]) else 0
        tariff_val = row["tariff_pct"] if not pd.isna(row["tariff_pct"]) else 0
        
        hover_text = f"{row['Country']}<br>"
        hover_text += f"Deficit: ${deficit_val:,.1f}K<br>"
        hover_text += f"Exports: ${exports_val:,.1f}K<br>"
        hover_text += f"Imports: ${imports_val:,.1f}K<br>"
        hover_text += f"Adjusted Tariff: {tariff_val:.0f}%"
        # Color based on tariff percentage
        if tariffs[i] is not None:
            if tariffs[i] >= 35:
                color = "#ff4444"  # bright red for high tariffs
            elif tariffs[i] >= 25:
                color = "#ff8800"  # orange for medium tariffs
            elif tariffs[i] >= 15:
                color = "#9370DB"  # purple for medium tariffs
            else:
                color = "#44aa44"  # green for low tariffs
        else:
            color = "#111111"
        
        # Handle text positioning and rotation based on position
        if abs(angle) == 90:  # left or right side
            # Left side: left aligned, Right side: right aligned
            textposition = "middle right" if angle == -90 else "middle left"
            name_traces.append(go.Scatter(
                x=[x], y=[y], mode="text",
                text=[label],
                textposition=textposition,
                textfont=dict(size=12, color=color),  # increased font size
                hoverinfo="text",
                hovertext=[hover_text],
                showlegend=False,
            ))
        else:  # top or bottom side - use annotations for rotation
            # Calculate rotation angle for top/bottom labels
            rotation_angle = 0 if abs(y) < 0.1 else (90 if y > 0 else -90)
            
            # Adjust position to avoid overlap - reduce spacing for top/bottom
            if abs(x) > 8:  # extreme left/right positions
                offset_x = 0.4 if x > 0 else -0.4  # reduced from 0.8
                offset_y = 0.2 if y > 0 else -0.2  # reduced from 0.3
            else:  # middle positions
                offset_x = 0.1  # reduced from 0.2
                offset_y = 0.3 if y > 0 else -0.3  # reduced from 0.6
            
            # Set proper alignment: top labels bottom-aligned, bottom labels top-aligned
            yanchor = "bottom" if y > 0 else "top"
            
            annotations.append(dict(
                x=x + offset_x,
                y=y + offset_y,
                text=label,
                showarrow=False,
                font=dict(size=12, color=color),  # increased font size to match left/right
                textangle=rotation_angle,
                xanchor="center",
                yanchor=yanchor,
                hovertext=hover_text
            ))

    # USA map background image
    us_map = dict(
        source="usa_map_PNG2.png",
        x=0, y=0,
        sizex=12, sizey=8,  # larger size to be more visible
        xanchor="center", yanchor="middle",
        layer="below",  # put it behind everything
        opacity=0.3  # make it semi-transparent
    )
    
    us_node = go.Scatter(
        x=[0], y=[0], mode="markers+text",
        text=["United States"],
        textposition="bottom center",
        marker=dict(size=10, symbol="circle", line=dict(width=0), color="gray"),
        hoverinfo="text", hovertext=["United States"],
        showlegend=False
    )

    # Legend proxies for toggling lines by clicking
    legend_proxies = []
    for metric in ["deficit","exports","imports"]:
        legend_proxies.append(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(width=6, color=color_map[metric]),
            name=metric.title(),
            visible=True,
            legendgroup=metric,
            showlegend=True
        ))

    fig = go.Figure(data=traces + [us_node] + name_traces + legend_proxies)
    fig.update_layout(
        title=f"US Trade Network — Sorted by {sort_metric.title()}",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20,r=20,t=60,b=20),  # increased top margin to make room for legend
        legend=dict(orientation="h", x=0.55, y=1.05),
        width=1200, height=1200,
        annotations=annotations,
        images=[us_map],  # add the USA map background
        # Add animation only for sorting changes
        transition={
            'duration': 500,
            'easing': 'cubic-in-out'
        }
    )
    
    # Enable legend click functionality
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad={"r": 10, "t": 87},
                showactive=False,
                x=0.1,
                xanchor="right",
                y=0,
                yanchor="top"
            )
        ]
    )
    return fig

app = Dash(__name__)
app.layout = html.Div([
    html.H2("US Trade Network"),
    html.Div(style={"display":"flex","gap":"20px","alignItems":"center","justifyContent":"center"}, children=[
        html.Div([html.Label("Sort by"), dcc.Dropdown(
            id="sort_metric",
            options=[{"label":"Deficit (high→low)","value":"deficit"},
                     {"label":"Exports (high→low)","value":"exports"},
                     {"label":"Imports (high→low)","value":"imports"},
                     {"label":"Adjusted Tariff (high→low)","value":"tariff_pct"}],
            value="tariff_pct", clearable=False, style={"width":"260px"}
        )]),
        html.Div([html.Label("Show lines"),
                  dcc.Checklist(
                      id="line_types",
                      options=[{"label":" Deficit","value":"deficit"},
                               {"label":" Exports","value":"exports"},
                               {"label":" Imports","value":"imports"}],
                      value=["deficit","exports","imports"],
                      inline=True
                  )]),
    ]),
    dcc.Graph(id="graph")
], style={"maxWidth":"1280px","margin":"0 auto"})

@app.callback(Output("graph","figure"),
              Input("sort_metric","value"),
              Input("line_types","value"))
def update(sort_metric, line_types):
    return build_figure(sort_metric, tuple(line_types))

# For App Runner deployment
server = app.server

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8050)
