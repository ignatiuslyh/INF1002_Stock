from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app
)
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.io as pio

# 1. DEFINE THE BLUEPRINT OBJECT
main_bp = Blueprint('main', __name__)

from app.modules.data_fetcher import get_hist_data
from app.modules.data_handler import api_data_handler, handle_backup_csv

from app.modules.prediction import forecast_prices
from app.modules.visualization import (
    predicted_plot,
    plot_price_and_sma,
    plot_daily_returns_plotly,
    plot_max_profit_segments,
    plot_runs
)
from app.modules.metrics import (
    calculate_sma,
    calculate_daily_returns,
    calculate_max_profit,
    calculate_runs
)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Index route: Collect and validate ticker + period

    The data validation logic (which calls the potentially failing API)
    has been moved to the /metrics route to consolidate the primary fetch
    and the new fallback mechanism.
    """
    if request.method == 'GET':
        # Render the input form
        return render_template('index.html', error=None)

    if request.method == 'POST':
        # Get form data
        ticker = request.form.get('ticker', '').strip().upper()
        period = request.form.get('period', '')

        # Basic validation
        if not ticker or not period:
            return render_template('index.html',
                                     error="Please fill in both ticker and period.")

        # Store in session and proceed directly to metrics route for data fetch
        session['ticker'] = ticker
        session['period'] = period

        # Clear any previous analysis data
        session.pop('clean_data', None)
        session.pop('selected_methods', None)
        session.pop('sma_window', None)

        return redirect(url_for('main.metrics'))


@main_bp.route('/metrics', methods=['GET', 'POST'])
def metrics():
    """
    Metrics route: Select analysis methods and fetch/clean data.
    Implements API fetch with fallback to backup data.
    """
    # Check if user has ticker/period in session
    if 'ticker' not in session or 'period' not in session:
        return redirect(url_for('main.index'))

    # --- GET Request Handling ---
    if request.method == 'GET':
        # Render the metrics selection page
        return render_template('metrics.html',
                               ticker=session['ticker'],
                               period=session['period'],
                               error=None)

    # --- POST Request Handling (Data Fetching and Selection) ---
    if request.method == 'POST':
        # Get selected analysis methods
        selected_methods = []

        # Check which methods were selected (logic remains the same)
        if request.form.get('predictive_model'):
            selected_methods.append('predictive_model')
            prediction_window = request.form.get('prediction_window')
            if not prediction_window:
                return render_template('metrics.html',
                                       ticker=session['ticker'],
                                       period=session['period'],
                                       error="Please select a window size for Prediction before continuing.")
            session['prediction_window'] = int(prediction_window)

        if request.form.get('sma'):
            selected_methods.append('sma')
            sma_window = request.form.get('sma_window')
            if not sma_window:
                return render_template('metrics.html',
                                       ticker=session['ticker'],
                                       period=session['period'],
                                       error="Please select a window size for SMA before continuing.")
            session['sma_window'] = sma_window

        if request.form.get('daily_returns'):
            selected_methods.append('daily_returns')

        if request.form.get('runs'):
            selected_methods.append('runs')

        if request.form.get('max_profit'):
            selected_methods.append('max_profit')

        if not selected_methods:
            return render_template('metrics.html',
                                   ticker=session['ticker'],
                                   period=session['period'],
                                   error="Please select at least one analysis method.")

        # --- Data Fetching Logic with Fallback ---
        try:
            ticker = session['ticker']
            period = session['period']

            try:
                # Attempt 1: Fetch data from yfinance API
                raw_data = get_hist_data(ticker, period)

                if raw_data is None or raw_data.empty:
                    # Treat empty API response as a soft failure, forcing fallback
                    raise ValueError("API returned no data.")

                # Clean the API data (Data Frame -> Clean Data Frame)
                clean_data = api_data_handler(raw_data, ticker=ticker)

            except Exception as api_e:
                # If API fails, use backup CSV handler
                current_app.logger.error(f"API data fetch failed for {ticker}: {api_e}. Falling back to backup CSV handler.")

                # Attempt 2: Load and Process Backup Data using the dedicated handler
                clean_data = handle_backup_csv(ticker, period)

                # Update session to indicate backup use and notify user
                session['ticker'] = f"{ticker} (BACKUP)"
                flash(f"Warning: Failed to fetch live data for {ticker}. Using backup historical dataset instead.", 'warning')


            if clean_data is None or clean_data.empty:
                raise ValueError("Both API fetch/clean and backup data processing failed.")

            # Store clean data and selections in session
            session['clean_data'] = clean_data.to_json(date_format='iso', orient='split')
            session['selected_methods'] = selected_methods

            return redirect(url_for('main.results'))

        except Exception as e:
            # Handle data fetching/cleaning errors
            error_msg = f"Error processing data: {str(e)}. Please try again."
            current_app.logger.error(f"Error processing data: {e}")
            return render_template('metrics.html',
                                   ticker=session['ticker'],
                                   period=session['period'],
                                   error=error_msg)


@main_bp.route('/results')
def results():
    """
    Results route: Generate analyses and display dashboard
    """
    # Validate session data exists
    required_keys = ['ticker', 'period', 'clean_data', 'selected_methods']
    for key in required_keys:
        if key not in session:
            return redirect(url_for('main.index'))

    try:
        # Retrieve data from session
        ticker = session['ticker']
        period = session['period']
        selected_methods = session['selected_methods']

        # Convert JSON back to DataFrame
        # Ensure we read the date column correctly
        clean_data = pd.read_json(session['clean_data'], orient='split')
        clean_data['date'] = pd.to_datetime(clean_data['date'])

        # Initialize results dictionary
        analysis_results = {
            'ticker': ticker,
            'period': period,
            'plots': {},
            'metrics': {}
        }

        # --- Run analyses and generate plots ---

        # 1. Predictive Model (Forecasting)
        if 'predictive_model' in selected_methods:
            try:
                window_size = session.get('prediction_window', 10)
                forecast_data = forecast_prices(clean_data, 'close', window_size)
                if forecast_data:
                    forecast_dates, forecast_values = forecast_data
                    fig = predicted_plot(clean_data, forecast_dates, forecast_values)
                    # FIX: Convert Plotly figure to HTML
                    analysis_results['plots']['prediction'] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
                else:
                    analysis_results['plots']['prediction'] = None
            except Exception as e:
                current_app.logger.error(f"Prediction model error: {e}")
                analysis_results['plots']['prediction'] = None
                analysis_results['metrics']['prediction_error'] = str(e)


        # 2. SMA (Simple Moving Average)
        if 'sma' in selected_methods:
            try:
                sma_input = session.get('sma_window', '20')
                if isinstance(sma_input, str):
                    window_sizes = [int(w.strip()) for w in sma_input.split(',') if w.strip().isdigit()]
                elif isinstance(sma_input, int):
                    window_sizes = [sma_input]
                else:
                    window_sizes = [20]

                fig = plot_price_and_sma(clean_data, window_sizes)
                if fig:
                    # FIX: Convert Plotly figure to HTML
                    analysis_results['plots']['sma'] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
                    analysis_results['metrics']['sma_window'] = ", ".join(map(str, window_sizes))
                else:
                    analysis_results['plots']['sma'] = None
            except Exception as e:
                current_app.logger.error(f"SMA error: {e}")
                analysis_results['plots']['sma'] = None
                analysis_results['metrics']['sma_error'] = str(e)

        # 3. Daily Returns
        if 'daily_returns' in selected_methods:
            try:
                returns_data = calculate_daily_returns(clean_data)
                fig = plot_daily_returns_plotly(returns_data, ticker)
                if fig:
                    # FIX: Convert Plotly figure to HTML
                    analysis_results['plots']['daily_returns'] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

                    if not returns_data.empty and 'Daily_Return' in returns_data.columns:
                        analysis_results['metrics']['avg_daily_return'] = f"{returns_data['Daily_Return'].mean():.4f}"
                        analysis_results['metrics']['return_volatility'] = f"{returns_data['Daily_Return'].std():.4f}"
                    else:
                        analysis_results['metrics']['avg_daily_return'] = 0.0
                        analysis_results['metrics']['return_volatility'] = 0.0
            except Exception as e:
                current_app.logger.error(f"Daily returns error: {e}")
                analysis_results['plots']['daily_returns'] = None
                analysis_results['metrics']['daily_returns_error'] = str(e)

        # 4. Max Profit
        if 'max_profit' in selected_methods:
            try:
                fig = plot_max_profit_segments(clean_data, ticker)
                if fig:
                    # FIX: Convert Plotly figure to HTML
                    analysis_results['plots']['max_profit'] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
                else:
                    analysis_results['plots']['max_profit'] = None

                analysis_results['metrics']['total_max_profit'] = calculate_max_profit(clean_data)
            except Exception as e:
                current_app.logger.error(f"Max profit error: {e}")
                analysis_results['plots']['max_profit'] = None
                analysis_results['metrics']['max_profit_error'] = str(e)

        # 5. Runs Analysis
        if 'runs' in selected_methods:
            try:
                runs_data = calculate_runs(clean_data)
                runs_df = runs_data[0]
                prices = runs_data[2]

                fig = plot_runs(runs_df, prices)
                if fig:
                    # FIX: Convert Plotly figure to HTML
                    analysis_results['plots']['runs'] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
                else:
                    analysis_results['plots']['runs'] = None

                if not runs_df.empty:
                    analysis_results['metrics']['total_runs'] = len(runs_df)
                    analysis_results['metrics']['avg_run_length'] = f"{runs_df['length'].mean():.2f}"
                    analysis_results['metrics']['longest_run'] = runs_df['length'].max()
                else:
                    analysis_results['metrics']['total_runs'] = 0
                    analysis_results['metrics']['avg_run_length'] = 0.0
                    analysis_results['metrics']['longest_run'] = 0
            except Exception as e:
                current_app.logger.error(f"Runs analysis error: {e}")
                analysis_results['plots']['runs'] = None
                analysis_results['metrics']['runs_error'] = str(e)

        # Render results page with all analyses
        return render_template('results.html',
                               results=analysis_results,
                               selected_methods=selected_methods)

    except Exception as e:
        # If any critical error occurs, redirect to index with error message
        current_app.logger.error(f"Critical error generating results: {e}")
        flash(f"Critical error generating results: {str(e)}", 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/reset')
def reset():
    """
    Optional route to clear session and start over
    """
    session.clear()
    return redirect(url_for('main.index'))


@main_bp.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors (uses main_bp.errorhandler now)
    """
    return render_template('404.html'), 404


@main_bp.errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 errors (uses main_bp.errorhandler now)
    """
    return render_template('500.html'), 500
