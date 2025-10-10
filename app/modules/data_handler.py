import pandas as pd
import os
from typing import List, Tuple, Optional

# --- 1. Function for Cleaning Live API Data (Takes a DataFrame) ---
def clean_api_data(
    df_raw: pd.DataFrame, 
    ticker: str, 
    filterTime: Optional[Tuple[int, int]] = None
) -> pd.DataFrame:
    """
    Data Handler for cleaning and standardizing the DataFrame returned by yfinance API.
    
    Parameters:
        df_raw (pd.DataFrame): Raw DataFrame from get_hist_data (yfinance).
        ticker (str): The single ticker requested (used to add the 'name' column).
        filterTime (tuple[int, int]): Optional input, allows filtering by specific time (start, end) in years.
        
    Output:
        pd.DataFrame: Cleaned, filtered, and standardized DataFrame.
    """
    df = df_raw.copy()
    
    # 1. Standardize column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    # Ensure date column is named 'date' and set to datetime
    if 'date' not in df.columns and 'Date' in df_raw.columns:
        df = df.rename(columns={'Date': 'date'})
        
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    
    # 2. Add 'name' column (yfinance does not provide this column)
    df['name'] = ticker
    df['name'] = df['name'].astype(str)
        
    # 3. Remove Missing Values
    df.dropna(inplace=True)

    # 4. Ensure correct data-types for numeric columns
    for col in ['open','close','high','low','volume']:
         if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='raise')

    # 5. Filter by time (years) - this is redundant if yfinance was filtered, but safe.
    if filterTime:
        start, end = filterTime
        df = df[(df['date'].dt.year >= start) & (df['date'].dt.year <= end)]

    # 6. Ensure 2 decimal points for $
    df = df.round({col: 2 for col in ['open', 'high', 'low', 'close'] if col in df.columns})

    # 7. Sort and return required columns
    df.sort_values(by=['date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Ensure all required columns are present before returning
    required_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 'name']
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA 

    return df[required_cols]


# --- 2. Function for Handling Backup CSV Data (Takes a file path and cleans it) ---
def handle_backup_csv(
    ticker: str, 
    period: str, # Period is not used for CSV filtering here, but we keep the signature for routes.py
    filterTime: Optional[Tuple[int, int]] = None
) -> pd.DataFrame:
    """
    Handles the backup data path by reading the CSV from a fixed path and applying 
    the full cleaning and filtering logic based on the user's original data_handler.
    
    Parameters:
        ticker (str): The specific ticker requested by the user.
        period (str): The period requested by the user.
        filterTime (tuple[int, int]): Optional input, allows filtering by specific time (start, end) in years.
        
    Output:
        pd.DataFrame: Cleaned, filtered, and standardized DataFrame for the requested ticker.
    """
    
    # Define the relative path to the backup CSV file
    backup_file_path = os.path.join('data', 'test_data.csv')
    print(f"DEBUG: Attempting to load and process backup data from: {backup_file_path}")
    
    try:
        # Load data from the contingency CSV
        df = pd.read_csv(backup_file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Backup data file not found at: {backup_file_path}. Please ensure it exists in the 'data/' folder.")
    except Exception as e:
        raise Exception(f"Error reading backup CSV file: {e}")

    
    # Standardize column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    # Remove Missing Values
    df.dropna(inplace=True)

    # Filter specific Names (using the single ticker requested by the user)
    if 'name' not in df.columns:
        raise ValueError("Backup CSV is missing the required 'name' column for ticker filtering.")
        
    # We use a list to filter by the single requested ticker
    filterName = [ticker] 
    if filterName:
         # Filter by the single requested ticker
        df = df[df['name'].isin(filterName)] 

    # Ensure correct data-types, raise errors if encountered
    df['name'] = df['name'].astype(str)
    df['date'] = pd.to_datetime(df['date'], errors='raise')
    for col in 'open','close','high','low','volume':
        df[col] = pd.to_numeric(df[col],errors='raise')

    # Filter by time (years)
    if filterTime:
        start, end = filterTime
        df = df[(df['date'].dt.year >= start) & (df['date'].dt.year <= end)]

    # Ensure 2 decimal points for $
    df = df.round({'open': 2, 'high': 2, 'low': 2, 'close': 2})

    # Sort by name and date, then reset index & drop previous dataframe
    df.sort_values(by=['name', 'date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Ensure all required columns are present before returning
    required_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 'name']
    return df[required_cols]


# This alias is kept for the API route logic's use
api_data_handler = clean_api_data


# this handles pd dataframes from API 
def api_data_handler(
        y_data, 
        filterTime: tuple[int, int] | None = None
    ) -> pd.DataFrame:
    # Parameters:
    #   filepath: path to CSV file
    #   filterName: List of Names to filter, e.g filterName = ['AAPL', 'AMZN', 'GOOG', 'MSFT']
    #   filterTime: Tuple of (start_year, end_year) to filter, e.g filterTime = (2015, 2020)
    df = y_data
    # Standardize column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    # Remove Missing Values
    df.dropna(inplace=True)

    # Ensure correct data-types, raise errors if encountered
    df['date'] = pd.to_datetime(df['date'], errors='raise')
    for col in 'open','close','high','low','volume':
        df[col] = pd.to_numeric(df[col],errors='raise')

    # Filter by time (years)
    if filterTime:
        start, end = filterTime
        df = df[(df['date'].dt.year >= start) & (df['date'].dt.year <= end)]

    # Ensure 2 decimal points for $
    df = df.round({'open': 2, 'high': 2, 'low': 2, 'close': 2})

    # Sort by name and date, then reset index & drop previous dataframe
    df.sort_values(by=[ 'date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df