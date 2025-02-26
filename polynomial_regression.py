#!/usr/bin/env python3
# Polynomial Regression Script

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

# Function to generate sample data (x, y) with some noise
def generate_sample_data(n_samples=50, noise=0.5):
    """
    Generate sample data for regression.
    
    Parameters:
        n_samples: Number of data points to generate
        noise: Level of random noise to add
        
    Returns:
        x: Independent variable array
        y: Dependent variable array with noise
    """
    # Generate evenly spaced x values
    x = np.linspace(0, 1, n_samples).reshape(-1, 1)
    
    # Generate y values following a polynomial pattern with noise
    # Here we use a polynomial: y = 2 + 3x - 2x² + 0.5x³ + noise
    y_true = 2 + 3 * x - 2 * x**2 + 0.5 * x**3
    y = y_true + noise * np.random.randn(n_samples, 1)
    
    return x, y

# Function to fit polynomial regression model
def fit_polynomial_regression(x, y, degree=3):
    """
    Fit a polynomial regression model to the data.
    
    Parameters:
        x: Independent variable array
        y: Dependent variable array
        degree: Degree of the polynomial
        
    Returns:
        model: Fitted polynomial regression model
        x_test: Array of x values for prediction curve
        y_pred: Predicted y values
    """
    # Create a polynomial regression model
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    
    # Fit the model to the data
    model.fit(x, y)
    
    # Generate points for a smooth curve
    x_test = np.linspace(0, 1, 100).reshape(-1, 1)
    y_pred = model.predict(x_test)
    
    return model, x_test, y_pred

# Function to get the polynomial equation as a string
def get_polynomial_equation(model, degree=3):
    """
    Get the polynomial equation as a formatted string.
    
    Parameters:
        model: Fitted polynomial regression model
        degree: Degree of the polynomial
        
    Returns:
        equation: String representation of the polynomial equation
    """
    # Extract coefficients from the model
    coefficients = model.named_steps['linearregression'].coef_[0]
    intercept = model.named_steps['linearregression'].intercept_[0]
    
    # Start building the equation string
    equation = f"y = {intercept:.4f}"
    
    # Add each term of the polynomial
    for i in range(1, len(coefficients)):
        coef = coefficients[i]
        
        # Skip terms with coefficient = 0
        if abs(coef) < 1e-10:
            continue
            
        # Add + sign for positive coefficients (except the first term)
        if coef > 0:
            equation += " + "
        else:
            equation += " - "
            coef = abs(coef)  # Make coefficient positive for display
        
        # Add the coefficient and variable
        if i == 1:
            equation += f"{coef:.4f}x"
        else:
            equation += f"{coef:.4f}x^{i}"
    
    return equation

# Function to visualize the data and regression curve
def visualize_regression(x, y, x_test, y_pred, equation):
    """
    Create a visualization of the data points and the regression curve.
    
    Parameters:
        x: Original x data points
        y: Original y data points
        x_test: Array of x values for prediction curve
        y_pred: Predicted y values
        equation: String representation of the polynomial equation
    """
    plt.figure(figsize=(10, 6))
    
    # Plot original data points
    plt.scatter(x, y, color='blue', alpha=0.6, label='Data points')
    
    # Plot the regression curve
    plt.plot(x_test, y_pred, color='red', linewidth=2, label='Polynomial regression')
    
    # Add labels and title
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'Polynomial Regression\n{equation}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

# Main function
def main():
    # Generate sample data
    # You can replace this with your own data loading code
    x, y = generate_sample_data(n_samples=30, noise=0.8)
    
    # Set the degree of the polynomial
    degree = 3
    
    # Fit the polynomial regression model
    model, x_test, y_pred = fit_polynomial_regression(x, y, degree)
    
    # Get the polynomial equation
    equation = get_polynomial_equation(model, degree)
    
    # Print the equation
    print("Polynomial Regression Equation:")
    print(equation)
    
    # Visualize the regression
    visualize_regression(x, y, x_test, y_pred, equation)

# Execute main function when script is run directly
if __name__ == "__main__":
    main()

