import numpy as np
import pandas as pd
from src.prediction import add_intercept, calculate_coefficients

# # Step 1: Generate a test DataFrame
# # INPUT: None (randomly generated data)
# print("# Step 1: INPUT: None (randomly generated data)")
# np.random.seed(42)
# dates = pd.date_range(start='2024-01-01', periods=10)
# data = {
#     'date': dates,
#     'open': np.random.uniform(100, 200, size=10),
#     'high': np.random.uniform(100, 200, size=10),
#     'low': np.random.uniform(100, 200, size=10),
#     'close': np.random.uniform(100, 200, size=10),
#     'volume': np.random.randint(1000, 5000, size=10)
# }
# df = pd.DataFrame(data)
# print("# Step 1: OUTPUT: DataFrame df")
# print(df)

# # Step 2: Extract features and target
# print("\n# Step 2: INPUT: DataFrame df")
# print(df)
# features = df.drop(columns=['date', 'close']).values
# target = df['close'].values
# dates_series = df['date']
# print("# Step 2: OUTPUT: features (np.array)")
# print(features)
# print("# Step 2: OUTPUT: target (np.array)")
# print(target)
# print("# Step 2: OUTPUT: dates_series (pd.Series)")
# print(dates_series)

# # Step 3: Split into train/test (manual split for demonstration)
# print("\n# Step 3: INPUT: features, target, dates_series")
# print("features:\n", features)
# print("target:\n", target)
# print("dates_series:\n", dates_series)
# split = int(len(features) * 0.7)
# features_train, features_test = features[:split], features[split:]
# target_train, target_test = target[:split], target[split:]
# dates_train, dates_test = dates_series[:split], dates_series[split:]
# print("# Step 3: OUTPUT: features_train")
# print(features_train)
# print("# Step 3: OUTPUT: features_test")
# print(features_test)
# print("# Step 3: OUTPUT: target_train")
# print(target_train)
# print("# Step 3: OUTPUT: target_test")
# print(target_test)
# print("# Step 3: OUTPUT: dates_train")
# print(dates_train)
# print("# Step 3: OUTPUT: dates_test")
# print(dates_test)

# # Step 4: Add intercept to training features
# print("\n# Step 4: INPUT: features_train")
# print(features_train)
# intercept = np.ones((features_train.shape[0], 1))
# features_train_with_intercept = np.hstack((intercept, features_train))
# print("# Step 4: OUTPUT: intercept")
# print(intercept)
# print("features_train_with_intercept")
# print(features_train_with_intercept)

# # Step 5: Calculate coefficients (Normal Equation)
# print("\n# Step 5: INPUT: features_train_with_intercept, target_train")
# print("features_train_with_intercept:\n", features_train_with_intercept)
# print("target_train:\n", target_train)
# x_transpose = features_train_with_intercept.T
# coefficients = np.linalg.pinv(x_transpose @ features_train_with_intercept) @ x_transpose @ target_train
# print("# Step 5: OUTPUT: x_transpose")
# print(x_transpose)
# print("# Step 5: OUTPUT: coefficients")
# print(coefficients)

# # Step 6: Predict on test set
# print("\n# Step 6: INPUT: features_test, coefficients")
# print("features_test:\n", features_test)
# print("coefficients:\n", coefficients)
# intercept_test = np.ones((features_test.shape[0], 1))
# features_test_with_intercept = np.hstack((intercept_test, features_test))
# predictions = features_test_with_intercept @ coefficients
# print("Predicted Values")
# print(predictions)

# # Step 7: Calculate Mean Squared Error and R2 Score manually
# print("\n# Step 7: INPUT: target_test, predictions")
# print("target_test:\n", target_test)
# print("predictions:\n", predictions)
# mse = np.mean((target_test - predictions) ** 2)
# ss_res = np.sum((target_test - predictions) ** 2)
# ss_tot = np.sum((target_test - np.mean(target_test)) ** 2)
# r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
# print("# Step 7: OUTPUT: Mean Squared Error:", mse)
# print("# Step 7: OUTPUT: R2 Score:", r2)

#Empty Features Array


df_empty = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
# This will fail when extracting features and adding intercept (features.shape[0] == 0)
try:
    features_empty = df_empty.drop(columns=['date', 'close']).values
    target_empty = df_empty['close'].values
    print("Testing Empty Features Array...")
    add_intercept(features_empty)
except Exception as e:
    print("Edge Case 1 (Empty Features) PASSED:", e)
df_mismatch = pd.DataFrame({
    'date': pd.date_range(start='2024-01-01', periods=3),
    'open': [100, 101, 102],
    'high': [105, 106, 107],
    'low': [99, 98, 97],
    'close': [102, 103],  # Only 2 values instead of 3
    'volume': [3000, 3100, 3200]
})
try:
    features_mismatch = df_mismatch.drop(columns=['date', 'close']).values
    target_mismatch = df_mismatch['close'].values
    print("Testing Features and Target Length Mismatch...")
    calculate_coefficients(features_mismatch, target_mismatch)
except Exception as e:
    print("Edge Case 2 (Length Mismatch) PASSED:", e)
# This will fail when you try to extract target and features, as their lengths do not match.

df_1d = pd.DataFrame({
    'date': ['2024-01-01'],
    'open': [100],
    'high': [105],
    'low': [99],
    'close': [102],
    'volume': [3000]
})
features_1d = df_1d.drop(columns=['date', 'close']).values.flatten()
try:
    print("Testing Non-2D Features (1D Array)...")
    add_intercept(features_1d)
except Exception as e:
    print("Edge Case 3 (Non-2D Features) PASSED:", e)  # This makes it 1D
# This will fail when adding intercept, as the code expects a 2D array.