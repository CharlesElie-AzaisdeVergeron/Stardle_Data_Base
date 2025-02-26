"""
Demonstrating the correct way to use scikit-learn's LinearRegression.fit() method

This script shows both incorrect and correct approaches to using LinearRegression.fit(),
with explanations of common errors and proper feature formatting.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load the data from CSV file
print("Loading data from 'NE PAS TOUCHER.csv'...")
try:
    df = pd.read_csv("NE PAS TOUCHER.csv")
    print("Data loaded successfully!")
    
    # Display basic information about the dataframe
    print("\nDataFrame shape:", df.shape)
    print("\nColumn names:", df.columns.tolist())
    
except Exception as e:
    print(f"Error loading the file: {e}")
    exit(1)

# Clean column names (remove trailing spaces)
df.columns = df.columns.str.strip()
print("\nCleaned column names:", df.columns.tolist())

# Check if the required columns exist
required_columns = ['price', 'price_ingame']
for col in required_columns:
    if col not in df.columns:
        closest_matches = [c for c in df.columns if col in c]
        print(f"Column '{col}' not found. Closest matches: {closest_matches}")
        # Try to use the closest match
        if closest_matches:
            new_col = closest_matches[0]
            print(f"Using '{new_col}' instead of '{col}'")
            df[col] = df[new_col]

# Extract the features and target
X = df['price'].values  # Independent variable
y = df['price_ingame'].values  # Dependent variable

# Drop any rows with NaN values
valid_indices = ~(np.isnan(X) | np.isnan(y))
X = X[valid_indices]
y = y[valid_indices]

print(f"\nUsing {len(X)} valid data points after removing NaN values")

# ----------------------------------------------------------
# INCORRECT WAY (similar to the user's code)
# ----------------------------------------------------------
print("\n" + "="*50)
print("INCORRECT APPROACH - Will Raise an Error")
print("="*50)

print("\nIncorrect approach (using 1D arrays):")
print("X shape:", X.shape)
print("y shape:", y.shape)

try:
    # Initialize the model
    incorrect_model = LinearRegression()
    
    # This will raise an error because X needs to be 2D
    incorrect_model.fit(X, y)
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nExplanation: LinearRegression.fit() expects X to be a 2D array with shape [n_samples, n_features].")
    print("When you have a single feature, you need to reshape it to [n_samples, 1].")

# ----------------------------------------------------------
# CORRECT WAY
# ----------------------------------------------------------
print("\n" + "="*50)
print("CORRECT APPROACH")
print("="*50)

# Reshape X to a 2D array (this is the key fix)
X_reshaped = X.reshape(-1, 1)
print("\nCorrect approach (reshaping X to 2D):")
print("X_reshaped shape:", X_reshaped.shape)
print("y shape:", y.shape)

# Initialize the model
correct_model = LinearRegression()

# Fit the model correctly
correct_model.fit(X_reshaped, y)

# Get model coefficients
print(f"\nModel coefficients: Slope = {correct_model.coef_[0]:.4f}, Intercept = {correct_model.intercept_:.4f}")

# Make predictions
y_pred = correct_model.predict(X_reshaped)

# Evaluate the model
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)
print(f"Mean Squared Error: {mse:.4f}")
print(f"R² Score: {r2:.4f}")

# ----------------------------------------------------------
# Visualization
# ----------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='blue', alpha=0.5, label='Actual data points')
plt.plot(X, y_pred, color='red', linewidth=2, label='Regression line')
plt.title('Linear Regression: Price vs Price In-Game')
plt.xlabel('Price')
plt.ylabel('Price In-Game')
plt.legend()
plt.grid(True, alpha=0.3)

# Add equation to the plot
equation = f"y = {correct_model.coef_[0]:.4f}x + {correct_model.intercept_:.4f}"
plt.annotate(equation, xy=(0.05, 0.95), xycoords='axes fraction', 
            fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

plt.tight_layout()
plt.savefig('linear_regression_result.png')
print("\nPlot saved as 'linear_regression_result.png'")
plt.show()

# ----------------------------------------------------------
# COMMON MISTAKES SUMMARY
# ----------------------------------------------------------
print("\n" + "="*50)
print("SUMMARY OF COMMON MISTAKES WITH LinearRegression.fit()")
print("="*50)
print("""
1. Using 1D arrays for X: 
- LinearRegression.fit(X, y) requires X to be a 2D array of shape [n_samples, n_features]
- For a single feature, use X.reshape(-1, 1) to convert a 1D array to a 2D array

2. Using lists instead of numpy arrays:
- Convert lists to numpy arrays before reshaping: X = np.array(your_list).reshape(-1, 1)

3. Not handling NaN values:
- NaN values can cause errors during fitting
- Use pandas' dropna() or filter out NaN values before fitting

4. Column name issues:
- Be careful with trailing spaces in column names
- Use df.columns = df.columns.str.strip() to clean column names

5. DataFrame columns vs values:
- Use df['column'].values to get a numpy array from a DataFrame column
- Don't pass df['column'] directly to fit() as it's a pandas Series, not a numpy array
""")

