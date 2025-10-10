# INF1002 Stock Market Analysis Project 

## Overview

The **Stock Market Analysis Project** is a web application built with **Python Flask** and deployed on **Vercel** that allows users to perform historical and predictive analysis on any given stock ticker. Users can input a ticker symbol and a time period to instantly generate a dashboard with various technical analysis visualizations, including Moving Averages, Daily Returns, Market Price Runs, Maximum Profit calculation, and a next-day price prediction.

## Features

* **Historical Data Fetching:** Utilizes the `yfinance` API to fetch accurate historical stock data.
* **Multiple Timeframes:** Supports analysis periods of up to 6 months, 1 year, 2 years, or 3 years.
* **Next-Day Price Prediction:** Features a dedicated predictive model to forecast the next day's closing price.
* **Technical Analysis Tools:**
    * Simple Moving Average (SMA) with 20, 50, and 200-day window options.
    * Daily Percentage Returns.
    * Market Price Runs (identifying consecutive up/down days).
    * Maximum Profit calculation over the analysis period.
* **Interactive Visualizations:** Generates clear and insightful charts for all selected metrics.

## Project Structure

The application logic is organized into several modules, each handling a specific part of the data flow.

| File | Role | Key Functions |
| :--- | :--- | :--- |
| `app.py` | Main Flask Application entry point. | `Flask(__name__)` |
| **`routes.py`** | **Core application logic and URL routing.** | `@app.route('/')`, `@app.route('/metrics')`, `@app.route('/results')` |
| `data_fetcher.py` | Fetches raw data from the `yfinance` API. | `get_hist_data(ticker, period)` |
| `data_handler.py` | Cleans and transforms the raw fetched data. | `api_data_handler(data)` (Example) |
| `prediction.py` | Handles the next-day price prediction model. | `predict_next_day(data)`, `validate_and_plot(data)` |
| `metrics.py` | Calculates technical metrics based on cleaned data. | `calculate_daily_returns(data)`, `calculate_sma(data, window_sizes)`, `calculate_runs(data)`, `calculate_max_profit(data)` |
| `visualization.py` | Generates all necessary charts and plots. | `plot_sma()`, `plot_runs()`, `plot_daily_returns()`, `plot_max_profit()` |
| `index.html` | User input form (Ticker, Period). | |
| `metrics.html` | User selection of analysis methodologies (SMA, Runs, etc.). | |
| `results.html` | Final dashboard displaying all charts and prediction. | |

---

## Installation and Setup

### Prerequisites

You need **Python 3.8+** installed on your system.

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    cd stock-analysis-dashboard
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/Mac
    venv\Scripts\activate     # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
   

4.  **Run the application:**
    ```bash
    python app.py
    ```


---

## Usage Flow

The application follows a three-step routing process:

### Step I: Input (`index.html` -> `/`)

* **Action:** User inputs a stock **Ticker** (e.g., `AAPL`, `GOOGL`) and selects an analysis **Time Period** (6mo, 1yr, 2yr, 3yr).
* **Logic:**
    * `routes.py` calls `data_fetcher.py`'s `get_hist_data(ticker, period)` using the `yfinance` API.
    * If the Ticker is invalid, an error is returned to `index.html`.
    * If successful, `data_handler.py` cleans the raw data.

### Step II: Metric Selection (`metrics.html` -> `/metrics`)

* **Action:** User is prompted to select which analysis methodologies they want to view:
    * **Predictive Model** (Always applied first)
    * **SMA** (Requires selection of window size: 20-day, 50-day, or 200-day).
    * **Daily Returns**
    * **Market Price Runs**
    * **Max Profit**
* **Logic:**
    * The cleaned data from Step I is held in session/cache.
    * Based on selections, `metrics.py` functions (e.g., `calculate_sma`, `calculate_runs`) are prepared for execution.

### Step III: Results Dashboard (`results.html` -> `/results`)

* **Action:** The user is presented with the final dashboard.
* **Logic:**
    * `metrics.py` functions calculate the necessary metrics.
    * `prediction.py` runs `predict_next_day(data)` to get the forecast.
    * `visualization.py` functions (`plot_sma()`, `plot_runs()`, etc.) generate charts using the calculated results.
    * **Display Order:**
        1.  **`<STOCK TICKER>`** (Title)
        2.  **Prediction Model** (with predicted close price)
        3.  SMA Chart
        4.  Daily Returns Chart
        5.  Max Profit Chart
        6.  Market Price Runs Chart

---

## Contributing

We welcome contributions! If you have suggestions or would like to improve the codebase, please feel free to:

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

