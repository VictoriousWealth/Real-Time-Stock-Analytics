from dash import html, dcc

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

layout = html.Div([
    html.H1("Single Ticker Dashboard"),

    dcc.Dropdown(
        id="ticker",
        options=[{"label": t, "value": t} for t in TICKERS],
        value="AAPL",
        clearable=False
    ),

    dcc.Graph(id="price-chart"),
    dcc.Graph(id="volume-chart"),

    html.H3("Company Fundamentals"),
    html.Div(id="stats"),

    html.H3("Latest News"),
    html.Div(id="news", style={"maxHeight": "200px", "overflowY": "scroll",
                               "border": "1px solid #ccc", "padding": "0.5em"})
])

