import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

df = pd.read_json('words_2025-05-02.json')

#print(df.head())

categorical_vars = [
    'estate_status_types',
    'bathroom_type',
    'project_type',
    'heating_type',
    'parking_type',
    'storeroom_type',
    'material_type',
    'swimming_pool_type',
    'hot_water_type',
    'condition',
    'living_room_type',
    'build_year',
    'user_type',
    'urban'
]

df['build_year'] = df['build_year'].replace({
    '>2000': '+2000',
    '<1955': '-1955'
})

df_encoded = pd.get_dummies(df, columns=categorical_vars, drop_first=False)

df_encoded = df_encoded.rename(columns={'price_2_price_square': 'price_per_square'})

X = df_encoded.drop('price_per_square', axis =1)
y = df_encoded['price_per_square']

X_train, X_calib, y_train, y_calib = train_test_split(X, y, test_size=0.2, random_state=42)

X_test, X_calib, y_test, y_calib = train_test_split(X_calib, y_calib, test_size=0.2, random_state=42)

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

import matplotlib.pyplot as plt

#residuals = y_calib - y_calib_pred

plt.figure(figsize=(8, 5))
plt.hist(residuals, bins=30, edgecolor='black')
plt.title("Histogram of Residuals")
plt.xlabel("Residual")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()