# app.py
import pandas as pd
import yfinance as yf
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import urllib.parse
import feedparser

from single_view import layout as single_layout
from comparison_view import layout as comparison_layout

# --- Setup ---
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Mini Bloomberg"

# --- App Shell ---
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        dcc.Link("Single View | ", href="/"),
        dcc.Link("Comparison View", href="/compare")
    ], style={"marginBottom": "20px"}),

    html.Div(id="page-content")
])

# --- Router ---
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/compare":
        return comparison_layout
    return single_layout

# ---- Helpers ----
def render_news_list(items):
    if not items:
        return html.Ul([html.Li("No news available right now.")])
    return html.Ul([html.Li(html.A(title, href=link, target="_blank")) for title, link in items])

def get_headlines_yfinance(tk, limit=5):
    try:
        items = tk.news or []
        out = []
        for it in items[:limit]:
            title = it.get("title")
            link = it.get("link")
            if title and link:
                out.append((title, link))
        return out
    except Exception:
        return []

def get_headlines_google_rss(ticker, limit=5):
    # Ex: https://news.google.com/rss/search?q=AAPL%20stock&hl=en-GB&gl=GB&ceid=GB:en
    q = f"{ticker} stock"
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(q)
        + "&hl=en-GB&gl=GB&ceid=GB:en"
    )
    try:
        feed = feedparser.parse(url)
        out = []
        for entry in feed.entries[:limit]:
            title = getattr(entry, "title", None)
            link = getattr(entry, "link", None)
            if title and link:
                out.append((title, link))
        return out
    except Exception:
        return []

# --- Callbacks for Single View ---
@app.callback(
    [Output("price-chart", "figure"),
     Output("volume-chart", "figure"),
     Output("stats", "children"),
     Output("news", "children")],
    Input("ticker", "value")
)
def update_single(ticker):
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1mo", interval="1d")

    # Price chart
    fig_price = px.line(
        hist, x=hist.index, y="Close",
        title=f"{ticker} Closing Price (1M)"
    )

    # Volume chart
    fig_volume = px.bar(
        hist, x=hist.index, y="Volume",
        title=f"{ticker} Daily Trading Volume (1M)"
    )

    # Fundamentals (defensive: some tickers miss fields)
    info = tk.info
    net_income, revenue = None, None
    try:
        net_income = tk.financials.loc["Net Income"].iloc[0]
        revenue = tk.financials.loc["Total Revenue"].iloc[0]
    except Exception:
        pass

    stats = html.Ul([
        html.Li(f"Company: {info.get('shortName', 'N/A')}"),
        html.Li(f"Current Price: {info.get('currentPrice', 'N/A')}"),
        html.Li(f"Market Cap: {info.get('marketCap', 'N/A')}"),
        html.Li(f"Revenue: {revenue if revenue is not None else 'N/A'}"),
        html.Li(f"Net Income: {net_income if net_income is not None else 'N/A'}"),
    ])

    # News: yfinance first, then Google News RSS
    news_items = get_headlines_yfinance(tk, limit=5)
    if not news_items:
        news_items = get_headlines_google_rss(ticker, limit=5)

    return fig_price, fig_volume, stats, render_news_list(news_items)

# --- Callbacks for Comparison View ---
@app.callback(
    [Output("comparison-chart", "figure"),
     Output("comparison-stats", "children")],
    [Input("ticker1", "value"),
     Input("ticker2", "value")]
)
def update_compare(t1, t2):
    t1_data, t2_data = yf.Ticker(t1), yf.Ticker(t2)
    hist1 = t1_data.history(period="1mo", interval="1d")
    hist2 = t2_data.history(period="1mo", interval="1d")

    # Align on date index just in case
    df = pd.DataFrame({t1: hist1["Close"], t2: hist2["Close"]})
    df = df.sort_index()

    fig = px.line(
        df, x=df.index, y=[t1, t2],
        title=f"{t1} vs {t2} Closing Prices (1M)"
    )

    def stats_block(tk, ticker):
        info = tk.info
        return html.Div([
            html.H4(ticker),
            html.Ul([
                html.Li(f"Price: {info.get('currentPrice', 'N/A')}"),
                html.Li(f"Market Cap: {info.get('marketCap', 'N/A')}"),
            ])
        ], style={"border": "1px solid #ccc", "padding": "10px", "width": "45%"})

    panel = html.Div(
        [stats_block(t1_data, t1), stats_block(t2_data, t2)],
        style={"display": "flex", "gap": "10px", "justifyContent": "space-between"}
    )

    return fig, panel

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)

