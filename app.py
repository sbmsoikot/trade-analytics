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

    # Rectangular layout - use consistent positioning regardless of visible lines
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
    
    for metric in show_lines:
        for _, row in df.iterrows():
            country = row["Country"]
            value = row[metric]
            if value is not None and country in positions:
                tx, ty = positions[country]
                # Scale line length by value relative to max for this metric
                if max_vals[metric] > 0:
                    tx *= abs(value) / max_vals[metric]
                    ty *= abs(value) / max_vals[metric]
                traces.append(line_trace_for_country(metric, color_map[metric], f"{country}: {value:,.0f}", tx, ty, value))

    # Country name labels
    name_traces = []
    annotations = []
    for _, row in df.iterrows():
        country = row["Country"]
        if country in positions:
            x, y = positions[country]
            name_traces.append(go.Scatter(
                x=[x], y=[y], mode="markers+text",
                text=[country], textposition="middle center",
                marker=dict(size=8, symbol="circle", line=dict(width=1, color="white"), color="lightgray"),
                hoverinfo="text", hovertext=[country],
                showlegend=False
            ))
            # Add text annotation for better positioning
            annotations.append(dict(
                x=x, y=y, text=country,
                showarrow=False, xanchor="center", yanchor="middle",
                font=dict(size=10, color="black"),
                bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1
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
        margin=dict(l=20,r=20,t=20,b=20),  # increased left/right margins for better spacing
        legend=dict(orientation="h", x=0.3, y=1.05),
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
    html.H2("US Trade Network — Rectangular Layout"),
    html.Div(style={"display":"flex","gap":"20px","alignItems":"center"}, children=[
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
