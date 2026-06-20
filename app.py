import streamlit as st
import pandas as pd
import joblib
import os

# Load model and feature list
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "random_forest.pkl"))
features = joblib.load(os.path.join(BASE_DIR, "features.pkl"))

st.title("House Price Prediction System")

# Create dictionary with all features initialized to 0
input_data = {feature: 0 for feature in features}

# User Inputs
input_data["bedrooms"] = st.number_input("Bedrooms", min_value=1, max_value=10, value=3)
input_data["bathrooms"] = st.number_input("Bathrooms", min_value=1.0, max_value=10.0, value=2.0)
input_data["sqft_living"] = st.number_input("Living Area (sqft)", min_value=500, max_value=10000, value=2000)
input_data["sqft_lot"] = st.number_input("Lot Size (sqft)", min_value=1000, max_value=100000, value=5000)
input_data["floors"] = st.number_input("Floors", min_value=1.0, max_value=5.0, value=1.0)
input_data["waterfront"] = st.selectbox("Waterfront", [0, 1])
input_data["view"] = st.slider("View", 0, 4, 0)
input_data["condition"] = st.slider("Condition", 1, 5, 3)
input_data["sqft_above"] = st.number_input("Sqft Above Ground", min_value=0, max_value=10000, value=1500)
input_data["sqft_basement"] = st.number_input("Sqft Basement", min_value=0, max_value=5000, value=0)
input_data["yr_built"] = st.number_input("Year Built", min_value=1900, max_value=2025, value=2000)
input_data["yr_renovated"] = st.number_input("Year Renovated", min_value=0, max_value=2025, value=0)

# Derived features
input_data["house_age"] = 2026 - input_data["yr_built"]
input_data["renovated"] = 1 if input_data["yr_renovated"] > 0 else 0

if st.button("Predict Price"):

    df = pd.DataFrame([input_data])

    # Match training columns
    for col in features:
        if col not in df.columns:
            df[col] = 0

    df = df.reindex(columns=features, fill_value=0)

    # Temporary fix for mismatch
    expected_features = model.n_features_in_

    if df.shape[1] > expected_features:
        df = df.iloc[:, :expected_features]

    st.write("Model expects:", expected_features)
    st.write("Input features:", df.shape[1])

    prediction = model.predict(df)

    st.success(
        f"Predicted House Price: ${prediction[0]:,.2f}"
    )