import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import numpy as np
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# 1. Load & Prepare Data
# ---------------------------------------------------------------------------
DATA_PATH = "weatherAUS.csv"

# Load data
df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"])
df["RainToday"] = df["RainToday"].map({"No": 0, "Yes": 1})
df["RainTomorrow"] = df["RainTomorrow"].map({"No": 0, "Yes": 1})
df["year"] = df["Date"].dt.year
df["month"] = df["Date"].dt.month
df["month_name"] = df["Date"].dt.month_name()

# Engineered features
df["TempAverage"] = (df["MinTemp"] + df["MaxTemp"]) / 2
df["TempRange"] = df["MaxTemp"] - df["MinTemp"]
df["HumidityAverage"] = (df["Humidity9am"] + df["Humidity3pm"]) / 2
df["PressureAverage"] = (df["Pressure9am"] + df["Pressure3pm"]) / 2
df["WindSpeedAverage"] = (df["WindSpeed9am"] + df["WindSpeed3pm"]) / 2

YEARS = sorted(df["year"].dropna().unique().tolist())
LOCATIONS = sorted(df["Location"].dropna().unique().tolist())
MONTHS = list(range(1, 13))

# Color Palette - Professional Dark Theme
COLOR_DRY = "#e67e22"
COLOR_RAIN = "#3498db"
COLOR_WIND = "#9b59b6"
COLOR_TEMP = "#e74c3c"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f1c40f"
BG_COLOR = "#1a1a2e"
CARD_BG = "#16213e"
TEXT_MAIN = "#ecf0f1"
TEXT_MUTED = "#95a5a6"
ACCENT_COLOR = "#00d2ff"

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "Australia Weather Analytics | Full Historical Analysis"

def classify(rate_pct: float):
    if pd.isna(rate_pct): return "No Data", TEXT_MUTED, "❓"
    if rate_pct >= 50: return "Likely to Rain", "#e74c3c", "🌧️"
    if rate_pct >= 30: return "Possible Rain", "#f39c12", "⛅"
    return "Unlikely to Rain", "#27ae60", "☀️"

def empty_plot(message="Not enough data"):
    return go.Figure().update_layout(
        title=dict(text=message, font=dict(color=TEXT_MUTED, size=14)),
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_MAIN),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(t=40, b=20, l=20, r=20)
    )

def create_kpi_card(title, value, subtitle, icon, color, width=3):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Span(icon, style={"fontSize": "2rem", "marginRight": "10px"}),
                    html.Div([
                        html.H5(title, className="card-title", style={"color": TEXT_MUTED, "fontSize": "0.9rem", "marginBottom": "5px"}),
                        html.H3(value, style={"color": color, "fontWeight": "bold", "marginBottom": "5px"}),
                        html.P(subtitle, style={"color": TEXT_MUTED, "fontSize": "0.8rem", "margin": "0"})
                    ], style={"flex": "1"})
                ], style={"display": "flex", "alignItems": "center"})
            ])
        ], style={"backgroundColor": CARD_BG, "border": f"1px solid {color}", "borderRadius": "12px", "boxShadow": "0 4px 15px rgba(0,0,0,0.3)"}),
        width=width, className="mb-3"
    )

# ---------------------------------------------------------------------------
# 2. App Layout
# ---------------------------------------------------------------------------
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🌦️ Australia Weather Analytics", style={
                    "color": ACCENT_COLOR, "textAlign": "center", 
                    "fontWeight": "bold", "marginBottom": "5px",
                    "textShadow": "0 0 20px rgba(0,210,255,0.3)"
                }),
                html.P("Full Historical Analysis: Wind, Temperature & Climate Trends", style={
                    "color": TEXT_MUTED, "textAlign": "center", "fontSize": "1.1rem"
                }),
                html.Hr(style={"borderColor": "#34495e", "margin": "20px 0"})
            ])
        ], width=12)
    ]),

    # Global Controls
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("📍 Select Location:", style={"fontWeight": "bold", "color": TEXT_MAIN, "marginBottom": "8px", "display": "block"}),
                            dcc.Dropdown(
                                id="location-dropdown",
                                options=[{"label": loc, "value": loc} for loc in LOCATIONS],
                                value=LOCATIONS[0],
                                clearable=False,
                                style={"color": "#000"}
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("📅 Select Year:", style={"fontWeight": "bold", "color": TEXT_MAIN, "marginBottom": "8px", "display": "block"}),
                            dcc.Dropdown(
                                id="year-dropdown",
                                options=[{"label": "All Years", "value": "All"}] + [{"label": str(y), "value": y} for y in YEARS],
                                value="All",
                                clearable=False,
                                style={"color": "#000"}
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("📆 Select Month:", style={"fontWeight": "bold", "color": TEXT_MAIN, "marginBottom": "8px", "display": "block"}),
                            dcc.Dropdown(
                                id="month-dropdown",
                                options=[{"label": "All Months", "value": "All"}] + [{"label": pd.to_datetime(f"2020-{m:02d}-01").strftime("%B"), "value": m} for m in MONTHS],
                                value="All",
                                clearable=False,
                                style={"color": "#000"}
                            )
                        ], width=4)
                    ])
                ])
            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
        ], width=12)
    ]),

    # KPI Cards Row
    dbc.Row(id="kpi-row", className="mb-4"),

    # Main Content Tabs
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                # TAB 1: Overview & Trends
                dbc.Tab(label="📊 Overview & Trends", tab_id="tab-1", children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌧️ Annual Rain Rate by Location", style={"color": TEXT_MAIN, "marginBottom": "15px"}),
                                    dcc.Graph(id="location-bar", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("📅 Rain Rate Over Years", style={"color": TEXT_MAIN, "marginBottom": "15px"}),
                                    dcc.Graph(id="year-trend", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌡️ Temperature Trends Over Years", style={"color": TEXT_MAIN, "marginBottom": "15px"}),
                                    dcc.Graph(id="temp-trend", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=12)
                    ])
                ]),

                # TAB 2: Wind Analysis
                dbc.Tab(label="💨 Wind Analysis", tab_id="tab-2", children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🧭 Wind Rose - Direction vs Rain Probability", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    html.P("Wind direction impact on next-day rain probability", style={"color": TEXT_MUTED, "fontSize": "0.9rem"}),
                                    dcc.Graph(id="wind-rose", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("💨 Wind Speed Distribution by Rain Status", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="wind-box", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("📈 Average Wind Speed Over Years", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="wind-year-trend", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🧭 Dominant Wind Direction by Year", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="wind-dir-year", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ])
                ]),

                # TAB 3: Temperature & Climate
                dbc.Tab(label="🌡️ Temperature & Climate", tab_id="tab-3", children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌡️ Min/Max/Avg Temperature by Year", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="temp-minmax-year", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("📊 Temperature Range vs. Rain", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="temp-violin", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("☀️ Sunshine vs Cloud Cover", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="cloud-sun-scatter", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌡️💧 Avg Temp vs Avg Humidity", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="avg-scatter", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ])
                ]),

                # TAB 4: Rain Drivers
                dbc.Tab(label="☁️ Rain Drivers", tab_id="tab-4", children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("💧 Humidity Distribution", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="humidity-hist", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("📊 Atmospheric Pressure", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="pressure-box", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("💨 Evaporation Levels", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="evaporation-box", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("📈 Humidity & Pressure Over Years", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="climate-year-trend", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ])
                ]),

                # TAB 5: Monthly Patterns
                dbc.Tab(label="📅 Monthly Patterns", tab_id="tab-5", children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌧️ Monthly Rain Pattern", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="monthly-rain", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("🌡️ Monthly Temperature Pattern", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="monthly-temp", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("💨 Monthly Wind Pattern", style={"color": TEXT_MAIN, "marginBottom": "10px"}),
                                    dcc.Graph(id="monthly-wind", config={"displayModeBar": False})
                                ])
                            ], style={"backgroundColor": CARD_BG, "borderRadius": "12px", "marginBottom": "20px"})
                        ], width=12)
                    ])
                ])
            ], id="tabs", active_tab="tab-1", style={"marginBottom": "20px"})
        ], width=12)
    ])
], fluid=True, style={"backgroundColor": BG_COLOR, "minHeight": "100vh", "padding": "20px", "fontFamily": "Segoe UI, Tahoma, Geneva, Verdana, sans-serif"})

# ---------------------------------------------------------------------------
# 3. Helper Functions
# ---------------------------------------------------------------------------

def get_filtered_data(location, year, month):
    df_filtered = df[df["Location"] == location]
    if year != "All":
        df_filtered = df_filtered[df_filtered["year"] == int(year)]
    if month != "All":
        df_filtered = df_filtered[df_filtered["month"] == int(month)]
    return df_filtered

def style_chart(fig):
    fig.update_layout(
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_MAIN),
        xaxis=dict(gridcolor="#34495e", linecolor="#34495e"),
        yaxis=dict(gridcolor="#34495e", linecolor="#34495e"),
        legend=dict(bgcolor=CARD_BG, bordercolor="#34495e", borderwidth=1),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# ---------------------------------------------------------------------------
# 4. Callbacks
# ---------------------------------------------------------------------------

# --- KPI Cards Callback ---
@app.callback(Output("kpi-row", "children"), 
              [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_kpis(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["RainTomorrow"])

    if sub.empty:
        return [dbc.Col(html.Div("No Data Available", style={"color": TEXT_MUTED, "textAlign": "center"}), width=12)]

    rate = sub["RainTomorrow"].mean() * 100
    n = len(sub)
    label, color, icon = classify(rate)
    year_text = f"in {year}" if year != "All" else "historically"
    month_text = f" ({pd.to_datetime(f'2020-{int(month):02d}-01').strftime('%B')})" if month != "All" else ""

    # Rain Today Impact
    sub_rain = get_filtered_data(location, year, month).dropna(subset=["RainToday", "RainTomorrow"])
    if len(sub_rain) >= 5:
        rain_given_rain = sub_rain[sub_rain["RainToday"] == 1]["RainTomorrow"].mean() * 100
        rain_given_dry = sub_rain[sub_rain["RainToday"] == 0]["RainTomorrow"].mean() * 100
    else:
        rain_given_rain = rain_given_dry = 0

    # Wind stats
    sub_wind = get_filtered_data(location, year, month).dropna(subset=["WindGustSpeed"])
    avg_wind = sub_wind["WindGustSpeed"].mean() if len(sub_wind) > 0 else 0

    # Humidity
    sub_hum = get_filtered_data(location, year, month).dropna(subset=["Humidity3pm"])
    avg_hum = sub_hum["Humidity3pm"].mean() if len(sub_hum) > 0 else 0

    # Temperature
    sub_temp = get_filtered_data(location, year, month).dropna(subset=["TempAverage"])
    avg_temp = sub_temp["TempAverage"].mean() if len(sub_temp) > 0 else 0

    return [
        create_kpi_card("Rain Forecast", f"{rate:.1f}%", f"{label}{month_text}", icon, color),
        create_kpi_card("If Rain Today", f"{rain_given_rain:.1f}%", "Chance tomorrow if raining", "☔", COLOR_RAIN),
        create_kpi_card("If Dry Today", f"{rain_given_dry:.1f}%", "Chance tomorrow if dry", "☀️", COLOR_DRY),
        create_kpi_card("Avg Wind Speed", f"{avg_wind:.1f} km/h", "Gust speed average", "💨", COLOR_WIND),
        create_kpi_card("Avg Humidity", f"{avg_hum:.1f}%", "3PM humidity level", "💧", COLOR_TEMP),
        create_kpi_card("Avg Temperature", f"{avg_temp:.1f}°C", "Daily average", "🌡️", ACCENT_COLOR),
        create_kpi_card("Observations", f"{n}", "Total data points", "📊", "#9b59b6"),
    ]

# --- TAB 1: Overview Charts ---

@app.callback(Output("location-bar", "figure"), Input("location-dropdown", "value"))
def update_location_bar(selected_location):
    loc_stats = df.groupby("Location")["RainTomorrow"].mean().mul(100).reset_index().sort_values("RainTomorrow", ascending=True)
    colors = [COLOR_RAIN if loc == selected_location else "#34495e" for loc in loc_stats["Location"]]

    fig = px.bar(loc_stats, y="Location", x="RainTomorrow", orientation='h', 
                 labels={"RainTomorrow": "Rain Likelihood (%)", "Location": ""},
                 color_discrete_sequence=[COLOR_RAIN])
    fig.update_traces(marker_color=colors)
    fig.add_vline(x=df["RainTomorrow"].mean()*100, line_dash="dash", line_color=COLOR_WARNING, 
                  annotation_text="National Avg", annotation_font_color=COLOR_WARNING)
    fig.update_layout(height=600, margin=dict(t=20, b=40, l=20, r=20))
    return style_chart(fig)

@app.callback(Output("year-trend", "figure"), [Input("location-dropdown", "value"), Input("month-dropdown", "value")])
def update_trend(location, month):
    sub = df[df["Location"] == location]
    if month != "All":
        sub = sub[sub["month"] == int(month)]
    sub = sub.groupby("year")["RainTomorrow"].mean().mul(100).reset_index()
    if sub.empty: return empty_plot()

    fig = px.line(sub, x="year", y="RainTomorrow", markers=True, 
                  labels={"RainTomorrow": "Rain Likelihood (%)", "year": "Year"})
    fig.update_traces(line_color=COLOR_RAIN, marker=dict(size=10, color=COLOR_RAIN, line=dict(width=2, color="white")))
    fig.update_layout(xaxis=dict(dtick=1, gridcolor="#34495e"), height=500)
    return style_chart(fig)

@app.callback(Output("temp-trend", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_temp_trend(location, year):
    sub = get_filtered_data(location, year, "All")
    if sub.empty: return empty_plot()
    
    temp_stats = sub.groupby("year").agg({
        "MinTemp": "mean",
        "MaxTemp": "mean",
        "TempAverage": "mean"
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MinTemp"], mode='lines+markers', name='Min Temp', line=dict(color="#3498db")))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MaxTemp"], mode='lines+markers', name='Max Temp', line=dict(color="#e74c3c")))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["TempAverage"], mode='lines+markers', name='Avg Temp', line=dict(color="#2ecc71", width=3)))
    fig.update_layout(
        xaxis_title="Year", yaxis_title="Temperature (°C)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450
    )
    return style_chart(fig)

# --- TAB 2: Wind Analysis ---

@app.callback(Output("wind-rose", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_wind_rose(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["WindGustDir", "RainTomorrow", "WindGustSpeed"])
    if len(sub) < 5: return empty_plot("Not enough Wind data")

    wind_stats = sub.groupby('WindGustDir').agg({
        'RainTomorrow': 'mean',
        'WindGustSpeed': 'mean',
        'Date': 'count'
    }).reset_index()
    wind_stats.columns = ['WindGustDir', 'RainProb', 'AvgSpeed', 'Count']
    wind_stats['RainProb'] = wind_stats['RainProb'] * 100

    compass_order = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    wind_stats['WindGustDir'] = pd.Categorical(wind_stats['WindGustDir'], categories=compass_order, ordered=True)
    wind_stats = wind_stats.sort_values('WindGustDir')

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=wind_stats['RainProb'],
        theta=wind_stats['WindGustDir'],
        name='Rain Probability (%)',
        marker_color=wind_stats['RainProb'],
        marker_colorscale='Blues',
        opacity=0.8,
        text=[f"Dir: {d}<br>Rain: {r:.1f}%<br>Speed: {s:.1f} km/h<br>Count: {c}" 
              for d, r, s, c in zip(wind_stats['WindGustDir'], wind_stats['RainProb'], 
                                    wind_stats['AvgSpeed'], wind_stats['Count'])],
        hovertemplate="%{text}<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#34495e"),
            angularaxis=dict(gridcolor="#34495e"),
            bgcolor=CARD_BG
        ),
        showlegend=False,
        title=dict(text="Rain Probability by Wind Direction", font=dict(color=TEXT_MAIN, size=14)),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    fig.update_layout(paper_bgcolor=CARD_BG)
    return fig

@app.callback(Output("wind-box", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_wind_speed(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["WindGustSpeed", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Wind Speed data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.box(sub, x="Status", y="WindGustSpeed", color="Status", 
                 color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN})
    fig.update_layout(showlegend=False, yaxis_title="Wind Gust Speed (km/h)")
    return style_chart(fig)

@app.callback(Output("wind-year-trend", "figure"), [Input("location-dropdown", "value"), Input("month-dropdown", "value")])
def update_wind_year_trend(location, month):
    sub = df[df["Location"] == location]
    if month != "All":
        sub = sub[sub["month"] == int(month)]
    sub = sub.dropna(subset=["WindGustSpeed", "year"])
    if sub.empty: return empty_plot()
    
    wind_stats = sub.groupby("year")["WindGustSpeed"].mean().reset_index()
    
    fig = px.line(wind_stats, x="year", y="WindGustSpeed", markers=True,
                  labels={"WindGustSpeed": "Avg Wind Gust Speed (km/h)", "year": "Year"})
    fig.update_traces(line_color=COLOR_WIND, marker=dict(size=10, color=COLOR_WIND, line=dict(width=2, color="white")))
    fig.update_layout(xaxis=dict(dtick=1, gridcolor="#34495e"), height=450)
    return style_chart(fig)

@app.callback(Output("wind-dir-year", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_wind_dir_year(location, year):
    sub = get_filtered_data(location, year, "All").dropna(subset=["WindGustDir", "year"])
    if sub.empty: return empty_plot()
    
    dir_counts = sub.groupby(["year", "WindGustDir"]).size().reset_index(name="Count")
    
    fig = px.bar(dir_counts, x="year", y="Count", color="WindGustDir", 
                 labels={"Count": "Frequency", "year": "Year", "WindGustDir": "Direction"})
    fig.update_layout(height=450, barmode='stack')
    return style_chart(fig)

# --- TAB 3: Temperature & Climate ---

@app.callback(Output("temp-minmax-year", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_temp_minmax_year(location, year):
    sub = get_filtered_data(location, year, "All")
    if sub.empty: return empty_plot()
    
    temp_stats = sub.groupby("year").agg({
        "MinTemp": ["mean", "min", "max"],
        "MaxTemp": ["mean", "min", "max"],
        "TempAverage": "mean"
    }).reset_index()
    temp_stats.columns = ["year", "MinTemp_mean", "MinTemp_min", "MinTemp_max",
                          "MaxTemp_mean", "MaxTemp_min", "MaxTemp_max", "TempAvg_mean"]

    fig = go.Figure()
    # MinTemp range
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MinTemp_max"], mode='lines', line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MinTemp_min"], mode='lines', fill='tonexty', fillcolor='rgba(52, 152, 219, 0.2)', line=dict(width=0), name='Min Temp Range'))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MinTemp_mean"], mode='lines+markers', name='Avg Min Temp', line=dict(color="#3498db")))
    
    # MaxTemp range
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MaxTemp_max"], mode='lines', line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MaxTemp_min"], mode='lines', fill='tonexty', fillcolor='rgba(231, 76, 60, 0.2)', line=dict(width=0), name='Max Temp Range'))
    fig.add_trace(go.Scatter(x=temp_stats["year"], y=temp_stats["MaxTemp_mean"], mode='lines+markers', name='Avg Max Temp', line=dict(color="#e74c3c")))
    
    fig.update_layout(xaxis_title="Year", yaxis_title="Temperature (°C)", height=450,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return style_chart(fig)

@app.callback(Output("temp-violin", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_temp_violin(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["TempRange", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Temperature data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.violin(sub, x="Status", y="TempRange", color="Status", box=True, 
                    color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN})
    fig.update_layout(showlegend=False, yaxis_title="Temperature Range (°C)")
    return style_chart(fig)

@app.callback(Output("cloud-sun-scatter", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_cloud_sun(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["Cloud3pm", "Sunshine", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Cloud/Sunshine data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.scatter(sub, x="Sunshine", y="Cloud3pm", color="Status", 
                     color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN},
                     opacity=0.7, size_max=15)
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
    return style_chart(fig)

@app.callback(Output("avg-scatter", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_avg_scatter(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["TempAverage", "HumidityAverage", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Averages data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.scatter(sub, x="TempAverage", y="HumidityAverage", color="Status", 
                     color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN},
                     opacity=0.7, size_max=15)
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
    return style_chart(fig)

# --- TAB 4: Rain Drivers ---

@app.callback(Output("humidity-hist", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_humidity(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["Humidity3pm", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Humidity data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.histogram(sub, x="Humidity3pm", color="Status", barmode="overlay", 
                       color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN},
                       opacity=0.7)
    return style_chart(fig)

@app.callback(Output("pressure-box", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_pressure(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["Pressure3pm", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Pressure data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.box(sub, x="Status", y="Pressure3pm", color="Status", 
                 color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN})
    fig.update_layout(showlegend=False)
    return style_chart(fig)

@app.callback(Output("evaporation-box", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value"), Input("month-dropdown", "value")])
def update_evaporation(location, year, month):
    sub = get_filtered_data(location, year, month).dropna(subset=["Evaporation", "RainTomorrow"])
    if len(sub) < 5: return empty_plot("Not enough Evaporation data")
    sub["Status"] = sub["RainTomorrow"].map({0: "Dry Next Day", 1: "Rain Next Day"})

    fig = px.box(sub, x="Status", y="Evaporation", color="Status", 
                 color_discrete_map={"Dry Next Day": COLOR_DRY, "Rain Next Day": COLOR_RAIN})
    fig.update_layout(showlegend=False)
    return style_chart(fig)

@app.callback(Output("climate-year-trend", "figure"), [Input("location-dropdown", "value"), Input("month-dropdown", "value")])
def update_climate_year_trend(location, month):
    sub = df[df["Location"] == location]
    if month != "All":
        sub = sub[sub["month"] == int(month)]
    sub = sub.dropna(subset=["Humidity3pm", "Pressure3pm", "year"])
    if sub.empty: return empty_plot()
    
    climate_stats = sub.groupby("year").agg({
        "Humidity3pm": "mean",
        "Pressure3pm": "mean",
        "Evaporation": "mean"
    }).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=climate_stats["year"], y=climate_stats["Humidity3pm"], mode='lines+markers', name='Humidity 3pm', line=dict(color="#3498db")), secondary_y=False)
    fig.add_trace(go.Scatter(x=climate_stats["year"], y=climate_stats["Pressure3pm"], mode='lines+markers', name='Pressure 3pm', line=dict(color="#e74c3c")), secondary_y=True)
    fig.add_trace(go.Scatter(x=climate_stats["year"], y=climate_stats["Evaporation"], mode='lines+markers', name='Evaporation', line=dict(color="#2ecc71")), secondary_y=False)
    
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Humidity (%) / Evaporation (mm)", secondary_y=False)
    fig.update_yaxes(title_text="Pressure (hPa)", secondary_y=True)
    fig.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return style_chart(fig)

# --- TAB 5: Monthly Patterns ---

@app.callback(Output("monthly-rain", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_monthly_rain(location, year):
    sub = get_filtered_data(location, year, "All")
    if sub.empty: return empty_plot()
    
    monthly = sub.groupby("month")["RainTomorrow"].mean().mul(100).reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: pd.to_datetime(f"2020-{x:02d}-01").strftime("%b"))

    fig = px.bar(monthly, x="month_name", y="RainTomorrow", 
                 labels={"RainTomorrow": "Rain Likelihood (%)", "month_name": "Month"},
                 color_discrete_sequence=[COLOR_RAIN])
    fig.update_layout(height=450)
    return style_chart(fig)

@app.callback(Output("monthly-temp", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_monthly_temp(location, year):
    sub = get_filtered_data(location, year, "All")
    if sub.empty: return empty_plot()
    
    monthly = sub.groupby("month").agg({
        "MinTemp": "mean",
        "MaxTemp": "mean",
        "TempAverage": "mean"
    }).reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: pd.to_datetime(f"2020-{x:02d}-01").strftime("%b"))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["MinTemp"], mode='lines+markers', name='Min Temp', line=dict(color="#3498db")))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["MaxTemp"], mode='lines+markers', name='Max Temp', line=dict(color="#e74c3c")))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["TempAverage"], mode='lines+markers', name='Avg Temp', line=dict(color="#2ecc71", width=3)))
    fig.update_layout(xaxis_title="Month", yaxis_title="Temperature (°C)", height=450,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return style_chart(fig)

@app.callback(Output("monthly-wind", "figure"), [Input("location-dropdown", "value"), Input("year-dropdown", "value")])
def update_monthly_wind(location, year):
    sub = get_filtered_data(location, year, "All").dropna(subset=["WindGustSpeed", "month"])
    if sub.empty: return empty_plot()
    
    monthly = sub.groupby("month").agg({
        "WindGustSpeed": "mean",
        "WindSpeed9am": "mean",
        "WindSpeed3pm": "mean"
    }).reset_index()
    monthly["month_name"] = monthly["month"].apply(lambda x: pd.to_datetime(f"2020-{x:02d}-01").strftime("%b"))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["WindGustSpeed"], mode='lines+markers', name='Gust Speed', line=dict(color=COLOR_WIND, width=3)))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["WindSpeed9am"], mode='lines+markers', name='9am Speed', line=dict(color="#3498db")))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["WindSpeed3pm"], mode='lines+markers', name='3pm Speed', line=dict(color="#e74c3c")))
    fig.update_layout(xaxis_title="Month", yaxis_title="Wind Speed (km/h)", height=450,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return style_chart(fig)

if __name__ == "__main__":
    app.run(debug=True)