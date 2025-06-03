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

model = joblib.load("xgboost_model.pkl")

y_calib_pred = model.predict(X_calib)
residuals = np.abs(y_calib - y_calib_pred)

alpha = 0.1
q_hat = np.quantile(residuals, 1 - alpha)

pd.DataFrame({'q_hat': [q_hat]}).to_csv('q_hat.csv', index=False)