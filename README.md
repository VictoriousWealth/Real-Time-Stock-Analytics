This document outlines the architecture and functionality of the `Real-Time-Stock-Analytics` codebase.

## Project Overview

This project is a web-based financial dashboard built using the Python **Dash** framework. Its purpose is to provide a "Mini Bloomberg" style interface for analyzing stock market data. The application pulls data from **Yahoo Finance** (via the `yfinance` library) and presents it in two distinct views:

1.  **Single View:** A detailed dashboard for analyzing one stock ticker at a time, showing price history, trading volume, key fundamentals, and recent news.
2.  **Comparison View:** A simplified page for comparing the 1-month price performance and key stats of two different stock tickers side-by-side.

The application is structured as a multi-page Dash app, where `app.py` acts as the central server and controller, and the page layouts are cleanly separated into their own modules (`single_view.py` and `comparison_view.py`).

---

## File Structure & Purpose

The codebase consists of four primary files, excluding the Python virtual environment (`venv`).

### 1. `requirements.txt`

This file lists all the Python dependencies required to run the project. This allows anyone to replicate the environment using `pip install -r requirements.txt`.

**Key Libraries:**
* **`dash`**: The core web framework for building the interactive user interface.
* **`pandas`**: Used for organizing and manipulating the time-series stock data retrieved from `yfinance`.
* **`plotly`**: The charting library (which `dash` is built on) used to create all interactive graphs (line and bar charts).
* **`yfinance`**: The critical library used to fetch all financial data, including historical prices, company info (like market cap), fundamentals (like revenue), and news headlines.
* **`feedparser`**: Used as a fallback news source. It parses Google News RSS feeds when `yfinance` fails to provide news.

### 2. `single_view.py`

This file defines the **static layout** for the main dashboard page (the `/` route). It does not contain any application logic (callbacks); it only describes what components should be on the page.

* **Components:**
    * An `H1` title: "Single Ticker Dashboard".
    * A `dcc.Dropdown` (ID: **`ticker`**): A dropdown menu allowing the user to select one stock from a predefined list (`AAPL`, `MSFT`, etc.).
    * Graph placeholders:
        * `dcc.Graph` (ID: **`price-chart`**)
        * `dcc.Graph` (ID: **`volume-chart`**)
    * Data/News placeholders:
        * `html.Div` (ID: **`stats`**): To be filled with fundamental data.
        * `html.Div` (ID: **`news`**): A scrollable box to be filled with news headlines.

### 3. `comparison_view.py`

Similar to `single_view.py`, this file defines the **static layout** for the comparison page (the `/compare` route).

* **Components:**
    * An `H1` title: "Comparison Dashboard".
    * Two `dcc.Dropdown` components (IDs: **`ticker1`** and **`ticker2`**) to select the two stocks to compare.
    * Placeholders:
        * `dcc.Graph` (ID: **`comparison-chart`**)
        * `html.Div` (ID: **`comparison-stats`**)

### 4. `app.py`

This is the main entry point and the "brain" of the entire application. It initializes the Dash server, defines the overall app structure, handles URL routing, and contains all the logic (callbacks) to make the components interactive.

**Key Sections:**

* **Setup:** Imports all libraries and, crucially, imports the `layout` variables from `single_view.py` and `comparison_view.py`. It initializes the Dash app instance.
* **App Shell Layout:** Defines the persistent part of the UI:
    * `dcc.Location(id="url")`: Tracks the browser's URL bar.
    * Navigation Links: Provides links to switch between "Single View" (`/`) and "Comparison View" (`/compare`).
    * `html.Div(id="page-content")`: An empty container that will be filled by the router.
* **Router (`display_page` callback):** This is the core of the multi-page functionality. It listens for changes to the **`url`** component. When the URL pathname changes (e.g., user clicks a link), this function returns the appropriate layout (`single_layout` or `comparison_layout`) to be rendered inside the **`page-content`** div.
* **Helper Functions:**
    * `get_headlines_yfinance` & `get_headlines_google_rss`: These functions are responsible for fetching news. The app always tries `yfinance` first. If that fails or returns no news, it falls back to parsing a Google News RSS feed for the ticker.
    * `render_news_list`: A utility to convert the list of news tuples (title, link) into a clickable HTML list (`html.Ul`).

---

## How It Works: Callback Logic

All interactivity in Dash is handled by callbacks. `app.py` defines two main callbacks, one for each view.

### Single View Callback (`update_single`)

* **Trigger (Input):** This function runs automatically whenever the value of the **`ticker`** dropdown (in `single_view.py`) changes.
* **Outputs:** It updates four components: **`price-chart`**, **`volume-chart`**, **`stats`**, and **`news`**.
* **Process:**
    1.  It takes the selected ticker symbol (e.g., "AAPL").
    2.  Uses `yf.Ticker(ticker)` to create a ticker object.
    3.  Fetches 1 month of daily history: `tk.history(period="1mo", interval="1d")`.
    4.  Generates a Plotly line chart for "Close" price and a Plotly bar chart for "Volume".
    5.  Fetches company fundamentals (`tk.info`, `tk.financials`) and formats them into an HTML list for the **`stats`** div. It includes error handling (`try...except`) in case data fields like "Net Income" are missing.
    6.  Calls the news helper functions to get headlines and renders them using `render_news_list`.
    7.  Returns all four elements, which Dash injects into the corresponding component IDs on the page.

### Comparison View Callback (`update_compare`)

* **Triggers (Inputs):** This function runs whenever the value of *either* the **`ticker1`** or **`ticker2`** dropdown changes.
* **Outputs:** It updates two components: **`comparison-chart`** and **`comparison-stats`**.
* **Process:**
    1.  Gets both selected ticker symbols (e.g., "AAPL" and "MSFT").
    2.  Fetches 1-month history for *both* tickers.
    3.  Combines their "Close" prices into a single Pandas DataFrame. This is crucial as it automatically aligns both datasets by date.
    4.  Generates a single Plotly line chart containing *two lines* (one for each ticker) plotted on the same axes.
    5.  Creates a side-by-side stats panel by fetching the `tk.info` for both tickers and styling them using a helper function (`stats_block`) and CSS flexbox.
    6.  Returns the chart and the stats panel to the page.
