import pandas as pd
import joblib
import numpy as np
from data_load import data_load

X_test, X_calib, y_test, y_calib = data_load()

model = joblib.load("xgboost_model.pkl")

# Generating the q_hat
y_calib_pred = model.predict(X_calib)
residuals = np.abs(y_calib - y_calib_pred)

alpha = 0.1
q_hat = np.quantile(residuals, 1 - alpha)

# Testing the q_hat on the test set
y_test_pred = model.predict(X_test)
# The logic whether the test values fell into the predicted intervals
within_bounds = np.logical_and(
    y_test>=y_test_pred - q_hat,
    y_test<=y_test_pred + q_hat,
)
#residuals_test = np.abs(y_test - y_test_pred)

portion_within = np.mean(within_bounds)
print(f"Portion of y_test within ±{q_hat} of prediction: {portion_within:.2%}")

# Saving the q_hat in a csv file
pd.DataFrame({'q_hat': [q_hat]}).to_csv('q_hat.csv', index=False)