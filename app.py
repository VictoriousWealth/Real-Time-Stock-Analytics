import yfinance as yf
from dash import Dash, html, dcc, Input, Output, dash_table

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "V", "JPM",
    "JNJ", "WMT", "PG", "UNH", "MA", "HD", "BAC", "XOM", "PFE", "KO",
    "PEP", "LLY", "COST", "ABBV", "MRK", "T", "DIS", "CVX", "ADBE", "NFLX",
    "INTC", "CMCSA", "VZ", "AVGO", "CRM", "ACN", "TXN", "NEE", "PM", "NKE",
    "AMD", "IBM", "QCOM", "AMGN", "TMO", "LOW", "ORCL", "MDT", "HON", "GE"
]

app = Dash(__name__)

app.title = "Stock analysis"
app.layout = html.Div(
    children = [
        html.Div(children=[
            html.H2("Revenue and Earnings for year 2024"),
            dash_table.DataTable(
                id="revenue",
                columns=[
                    {"name": "Date Time", "id": "index"},
                    {"name": "Revenue", "id": "Total Revenue"},
                ],
                sort_action="native",
                filter_action="native",
            ),
            dash_table.DataTable(
                id="earnings",
                columns=[
                    {"name": "Date Time", "id": "index"},
                    {"name": "Net Income", "id": "Net Income"},
                ],
                sort_action="native",
                filter_action="native",
            ),
            html.P(
                id="earnings",
            ),
            html.P(
                id="eps",
            ),
            html.P(
                id="price_to_earnings_ratio",
            ),
        ]),
        dcc.Dropdown(
            id="dropDown",
            options = [
                {"label" : yf.Ticker(t).info["shortName"], "value" : t} for t in tickers
            ],
            value="AAPL",
            clearable=False,
        ),
        dcc.Graph(
            id="history"
        ),
        dcc.Graph(
            id="volume"
        ),
        dcc.Graph(
            id="dividends"
        ),
        dcc.Graph(
            id="stock splits"
        ),
    ]
)

@app.callback(
    Output("history", "figure"),
    Output("volume", "figure"),
    Output("dividends", "figure"),
    Output("stock splits", "figure"),
    Output("revenue", "data"),
    Output("earnings", "children"),
    Output("eps", "children"),
    Output("price_to_earnings_ratio", "children"),
    Input("dropDown", "value"),
)

def updateGraphs(stock):
    selected_ticker = yf.Ticker(stock)
    data = selected_ticker.history(period="1mo", interval="1h")
    longName = selected_ticker.info['longName']

    traces = [
        {
            "x" : data.index,
            "y" : data["Open"],
            "type" : "lines",
            "name": "Open"
        },
        {
            "x" : data.index,
            "y" : data["Close"],
            "type" : "lines",
            "name": "Close"
        },
        {
            "x" : data.index,
            "y" : data["Low"],
            "type" : "lines",
            "name": "Low"
        },
        {
            "x" : data.index,
            "y" : data["High"],
            "type" : "lines",
            "name": "High"
        },
    ]

    history_graph = {
        "data": traces,
        "layout" : {
            "title": {"text": f"{longName}'s Metrics Over Time", "x": 0.5}, 
            "xaxis" : {"title": "Date",},
            "yaxis" : {"title": "Value",},
            "legend": {"title": {"text": "Metrics"}}
        }
    }

    volume_graph = {
        "data" : [{
            "x" : data.index,
            "y" : data["Volume"],
            "type" : "lines",
            "name": "Volume"
        },],
        "layout": {
            "title": {"text": f"{longName}'s Volume Over Time", "x": 0.5}, 
            "xaxis" : {"title": "Date",},
            "yaxis" : {"title": "Volume",},
        }
    }

    dividens_graph = {
        "data": [
            {
                "x": data.index,
                "y": data["Dividends"],
                "type": "lines",
                "name": "Dividends"
            }
        ],
        "layout" : {
            "title": {"text": f"{longName}'s Dividends Over Time", "x": 0.5}, 
            "xaxis" : {"title": "Date",},
            "yaxis" : {"title": "Volume",},
        }
    }

    stock_splits_graph = {
        "data": [
            {
                "x": data.index,
                "y": data["Dividends"],
                "type": "lines",
                "name": "Dividends"
            }
        ],
        "layout" : {
            "title": {"text": f"{longName}'s Stock Splits Over Time", "x": 0.5}, 
            "xaxis" : {"title": "Date",},
            "yaxis" : {"title": "Stock Splits",},
        }
    }

    print("Revenue = ", selected_ticker.financials.loc["Total Revenue"].reset_index().to_dict(orient="records"))

    revenue = selected_ticker.financials.loc["Total Revenue"].reset_index().to_dict(orient="records")
    earnings = "Earnings (Net Income): "+str(selected_ticker.financials.loc["Net Income"].iloc[0])

    net_income = selected_ticker.financials.loc["Net Income"].iloc[0]
    shares_outstanding = selected_ticker.info["sharesOutstanding"]
    eps = "EPS = " + str(net_income/shares_outstanding)

    price = selected_ticker.info["currentPrice"]
    price_to_earnings_ratio = "P/E Ratio: "+str(price / (net_income/shares_outstanding))

    return history_graph, volume_graph, dividens_graph, stock_splits_graph, revenue, earnings, eps, price_to_earnings_ratio


if "__main__" == __name__:
    app.run_server(debug=True)