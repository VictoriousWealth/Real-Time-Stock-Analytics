from dash import html, dcc

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

layout = html.Div([
    html.H1("Comparison Dashboard"),

    html.Div([
        dcc.Dropdown(
            id="ticker1",
            options=[{"label": t, "value": t} for t in TICKERS],
            value="AAPL", clearable=False,
            style={"width": "45%", "display": "inline-block", "marginRight": "5%"}
        ),
        dcc.Dropdown(
            id="ticker2",
            options=[{"label": t, "value": t} for t in TICKERS],
            value="MSFT", clearable=False,
            style={"width": "45%", "display": "inline-block"}
        ),
    ]),

    dcc.Graph(id="comparison-chart"),
    html.Div(id="comparison-stats")
])

