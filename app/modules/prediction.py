import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from app.modules.visualization import predicted_plot
"""
The goal of this module is to implement a multiple linear regression model
to predict stock prices based on the features in the dataset.

Features(x) = [Open, High, Low, Volume]
Target(y) = [Close]

Predicted Close Price = b0 + b1*Open + b2*High + b3*Low + b4*Volume

To ensure that the model is accurate, we must split this process into two main parts: Validation and Forecasting

----------------------------------------------------------------------------------------------------------------
VALIDATION - Our goal in validation is to get an evaluation of how accurate our model is

Step 1: Prepare the data
    - Extract features (x) and target (y) from the DataFrame

Step 2: Split the data
    - Split the dataset into training (80%) and testing (20%) sets
    - train_x, train_y for training (80%)
    - test_x, test_y for testing (20%)

Step 3: Train the Model (Find Coefficients)
    - Use train_x and train_y to calculate the coefficients (b0, b1, b2, b3, b4) using Normal Equation method

Step 4: Validate the Model
    - Make predictions based on test_x and test_y
    - Calculate evaluation metrics (MSE, R²)
         - Mean Squared Error (MSE): Measures how wrong the predictions are. e.g Actual Close = 150, Predicted Close = 145, Error = 5, MSE = 25. 
                                     Lower is better (min 0.0)
         - R-Squared (R²): Describes the % of data the model can explain. 0.6 = Explains 60% of the data, 40% unexplained
                           Higher is better (max 1.0)

Step 5: Plot Actual vs. Predicted Values
    - Visualize the performance of the model by plotting actual vs. predicted stock prices

----------------------------------------------------------------------------------------------------------------
FORECASTING - Our goal in forecasting is to predict the next day's stock price / future stock prices

Step 1: Prepare the data
    - Extract features (X) and target (y) from the DataFrame

Step 2: Train the Model (Find Coefficients)
    - Use the entire dataset (X and y) to calculate the coefficients (b0, b1, b2, b3, b4) using Normal Equation method

Step 3: Predict the Next Day's Value
    - Use the most recent data point (last row of X) to predict the next day's stock price

"""

def add_intercept(features):
    """
    Add an intercept column (a column of ones) to the feature matrix.
    This is necessary for calculating the intercept term (b0) in the regression.

    Parameters:
        features (np.array): The input features for training

    Returns:
        features_with_intercept (np.array): The feature matrix with an added intercept column.

    """
    try:
        if not isinstance(features, np.ndarray):
            raise TypeError("Features must be a numpy array.")
        if features.ndim != 2:
            raise ValueError("Features must be a 2D array")
        if features.shape[0] == 0:
            raise ValueError("Features array is empty.")
        # Intercept is needed for b0, to ensure the matrix has the correct dimensions
        # Prediction = b0*intercept + b1*x1 + b2*x2 + ...
        intercept = np.ones((features.shape[0], 1))
        # Add intercept column to the features matrix with np.hstack
        features_with_intercept = np.hstack((intercept, features))
        return features_with_intercept
    except (TypeError, ValueError) as e:
        print(f"Error in add_intercept(): {e}")
        raise
    except Exception as e:
        print(f"Error in add_intercept(): Error adding intercept column. {e}")
        raise


def calculate_coefficients(features, target):
    """
    Calculate regression coefficients using the Normal Equation method.
    Formula: coefficients = ((x_transpose)*X)^-1 * (x_transpose)*y
    Parameters:
        features (np.array): The input features for training
        target (np.array): The target for prediction

    Returns:
        coefficients (np.array): coefficients [b0, b1, b2, ...]
    """
    try:
        if not isinstance(features, np.ndarray) or not isinstance(target, np.ndarray):
            raise TypeError("Features and target must be numpy arrays.")
        if features.ndim != 2 or target.ndim != 1:
            raise ValueError("Features shape must be 2D and target shape must be 1D.")
        if features.shape[0] != target.shape[0]:
            raise ValueError("Features and target must have the same number of rows.")
        # Add intercept column to the features matrix
        features_with_intercept = add_intercept(features)
        # Apply the Normal Equation: coefficients = ((x_transpose)*X)^-1 * (x_transpose)*y
        x_transpose = features_with_intercept.T
        coefficients = np.linalg.pinv(x_transpose @ features_with_intercept) @ x_transpose @ target
        return coefficients
    except (TypeError, ValueError) as e:
        print(f"Error in calculate_coefficients(): {e}")
        raise
    except np.linalg.LinAlgError as e:
        print(f"Error in calculate_coefficients(): Error can happen due to perfect correlation in features. {e}")
        raise
    except Exception as e:
        print(f"Error in calculate_coefficients(): Unexpected Error. {e}")
        raise

def predict(features, coefficients):
    """
    Predict values given a feature matrix and fitted coefficients.
    Parameters:
        features (np.array): The input features for prediction.
        coefficients (np.array): The fitted coefficients from the model.

    Returns:
        predictions (np.array): The predicted values

    """
    try:
        if not isinstance(features, np.ndarray) or not isinstance(coefficients, np.ndarray):
            raise TypeError("Features and coefficients must be numpy arrays.")
        if features.ndim != 2 or coefficients.ndim != 1:
            raise ValueError("Features shape must be 2D and coefficients shapemust be 1D.")
        # Add intercept column to the features matrix
        features_with_intercept = add_intercept(features)
        # Ensure same number of features and coefficients
        if features_with_intercept.shape[1] != coefficients.shape[0]:
            raise ValueError(f"Feature and coefficient dimensions do not match. Feature: {features_with_intercept.shape[1]}, Coefficients: {len(coefficients)}")

        # Make predictions: predictions = X * coefficients
        predictions = features_with_intercept @ coefficients
        return predictions
    except (TypeError, ValueError) as e:
        print(f"Error in predict(): {e}")
    except Exception as e:
        print(f"Error in predict(). Unexpected Error. {e}")

def validate_model(data, target_column, test_size=0.2):
    """
    Splits data, trains the model, and evaluates its performance on unseen data.
    Parameters:
        data (pd.DataFrame): The input dataframe containing features and target
        target_column (str): The name of the target column in the dataframe
        test_size (float): Proportion of the dataset to include in the test split (default is 0.2)

    Returns:
        date_test (pd.Series): test set dates for plotting
        target_test (np.array): Actual target values from test set
        predictions_test (np.array): Predicted target values for test set

    """
    print("--- Starting Model Validation ---")
    try:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame.")
        if data.empty:
            raise ValueError("Input dataframe is empty.")
        # Ensure required columns are present
        required_cols = ['date', target_column]
        if not all(col in data.columns for col in required_cols):
            raise KeyError(f"Dataframe is missing one of the columns: {required_cols}")
        if not 0 < test_size < 1:
            raise ValueError("Test size must be a float between 0 and 1.")
        
        # Step 1: Prepare features and target from the dataframe
        # Features are the inputs (e.g., Open, High, Low, Volume)
        # Target is the output we want to predict (e.g., Close)
        dates = data['date']
        features = data.drop(columns=['date', target_column]).values
        target = data[target_column].values

        # Step 2: Split the data into training and testing sets. Date is also splitted for plotting later
        # random_state=123 to ensure data is split the same way every time
        features_train, features_test, target_train, target_test, date_train, date_test = train_test_split(
            features, target, dates, test_size=test_size, random_state=123
        )
        print(f"Data split into {len(features_train)} training samples and {len(features_test)} testing samples.")

        # Step 3: Train the model by calculating coefficients using only training data(features_train and target_train).
        coefficients = calculate_coefficients(features_train, target_train)

        # Step 4: Make predictions on the test data.
        predictions_test = predict(features_test, coefficients)

        # Step 5: Evaluate the model by comparing predictions to the actual values.
        mse = mean_squared_error(target_test, predictions_test)
        r2 = r2_score(target_test, predictions_test)
        
        print("\n--- Model Validation Metrics ---")
        print(f"Mean Squared Error (MSE): {mse:.3f}")
        print(f"R-Squared (R²): {r2:.3f}")
        print("------------------------------\n")

        # Return values needed for plotting
        return date_test, target_test, predictions_test
    
    except (TypeError, ValueError, KeyError) as e:
        print(f"Error in validate_model(): {e}")
    except Exception as e:
        print(f"Error in validate_model(): Unexpected Error. {e}")

def forecast_prices(data, target_column, n_days: int):
    """
    Predicts future prices for a given number of days and plots the result.

    Parameters:
        data (pd.DataFrame): The historical data to train the model on.
        target_column (str): The name of the column we want to predict.
        n_days (int): The number of future days to predict.

    Outputs:
        Next n_days predictions: Shown in console
        predicted_plot: Plot showing historical and predicted prices
    """
    try:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame.")
        if not isinstance(n_days, int) or n_days < 1:
            raise ValueError("Number of days for forecast must be >= 1.")
        if data.empty:
            raise ValueError("Input dataframe is empty.")
        required_cols = ['date', target_column, 'volume']
        if not all(col in data.columns for col in required_cols):
            raise KeyError(f"Dataframe is missing one of the columns: {required_cols}")
            
        print(f"\n--- Predicting Next {n_days} Day(s) ---")

        # Step 1: Train the model on the entire historical dataset
        features = data.drop(columns=['date', target_column]).values
        target = data[target_column].values
        coefficients = calculate_coefficients(features, target)

        # Step 2: Get the last row of real features to start the prediction loop
        last_known_features = features[-1].reshape(1, -1)
        average_volume = data['volume'].mean()
        last_date = data['date'].iloc[-1]

        # Step 3: Generate future dates for plotting
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=n_days).to_pydatetime().tolist()

        # Step 4: Iteratively predict for n_days
        future_predictions = []
        current_features = last_known_features

        for day in range(n_days):
            next_prediction = predict(current_features, coefficients)[0]
            future_predictions.append(next_prediction)
            print(f"Day {day + 1}: Predicted {target_column} = {next_prediction:.2f}")

            # Make previous day's close prediction into next day's features
            next_features = np.array([[
                next_prediction, #Open
                next_prediction, #High
                next_prediction, #Low
                average_volume #Volume
            ]])
            current_features = next_features

        print("----------------------------------\n")
        
        # Call the plotting function
        predicted_plot(data, future_dates, future_predictions)
    
    except (TypeError, ValueError, KeyError) as e:
        print(f"Error in forecast_prices(): {e}")
    except Exception as e:
        print(f"An unexpected error occurred during forecasting: {e}")
    
"""
Notes

add_intercept(features)
    - Calculates intercept column for features matrix
    - Uses features (independent variables)

calculate_coefficients(features, target)
    - Calculates regression coefficients using Normal Equation method
    - Uses features (independent variables) and target (dependent variable)

predict(features, coefficients)
    - Makes predictions using features and coefficients
    - Uses features (independent variables) and coefficients (model parameters)
    - Interdependent functions
        - add_intercept(features)
        - calculate_coefficients(features, target)

validate_model(data, target_column, test_size=0.2)
    - Splits data into train/test, then uses previous functions to calculate predicted values
    - Interdependent functions
        - add_intercept(features)
        - calculate_coefficients(features, target)
        - predict(features, coefficients)

forecast_prices(data, target_column)
    - Predicts future prices for 'n' days
    - Interdependent functions
        - add_intercept(features)
        - calculate_coefficients(features, target)
        - predict(features, coefficients)s
"""