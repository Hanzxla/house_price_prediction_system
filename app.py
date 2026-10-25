
import os
import joblib
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="HomeValue | House Price Predictor",
    page_icon="🏡",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_artifacts():
    model = joblib.load(os.path.join(BASE_DIR, "random_forest.pkl"))
    features = joblib.load(os.path.join(BASE_DIR, "features.pkl"))
    return model, features


try:
    model, features = load_artifacts()
except Exception as e:
    st.error(f"Could not load model files: {e}")
    st.stop()

# ---------------- STYLING ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #173b67, #277da1);
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 2.3rem;
}
.hero p {
    color: #e5f2ff;
    font-size: 1rem;
}
div.stButton > button,
div.stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 600;
}
.result-card {
    background: #effaf3;
    color: #164b2c;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #b7dfc6;
    text-align: center;
}
.result-label {
    font-size: 1.05rem;
}
.result-price {
    font-size: 2.3rem;
    font-weight: 750;
    overflow-wrap: anywhere;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>🏡 HomeValue</h1>
    <p>Smart House Price Prediction System</p>
    <p>Enter your property details to estimate its price.</p>
</div>
""", unsafe_allow_html=True)

# Illustrative exchange rate; update as needed.
USD_TO_INR = 95.0

with st.sidebar:
    st.title("🏡 HomeValue")
    st.caption("House Price Prediction System")
    st.divider()
    st.subheader("How it works")
    st.write("1. Enter property details.")
    st.write("2. Click Predict House Price.")
    st.write("3. View the estimated price.")
    st.divider()
    st.caption("The model uses US housing data.")
    st.caption("INR is a currency conversion, not an Indian-market valuation.")

# ---------------- INPUT FORM ----------------
st.subheader("🏠 Property Details")
st.write("Complete the sections below.")

with st.form("house_prediction_form"):

    st.markdown("### 🛏️ Rooms & Layout")
    col1, col2, col3 = st.columns(3)

    with col1:
        bedrooms = st.number_input(
            "Bedrooms (BHK)",
            min_value=1, max_value=10,
            value=3, step=1
        )

    with col2:
        bathrooms = st.number_input(
            "Bathrooms",
            min_value=1, max_value=8,
            value=2, step=1
        )

    with col3:
        floors = st.selectbox(
            "Number of Floors",
            options=[1, 2, 3]
        )

    st.divider()
    st.markdown("### 📐 Property Size")
    col1, col2 = st.columns(2)

    with col1:
        sqft_living = st.number_input(
            "Living Area (sq ft)",
            min_value=370, max_value=13540,
            value=2000, step=50
        )

        sqft_above = st.number_input(
            "Area Above Ground (sq ft)",
            min_value=0, max_value=10000,
            value=1500, step=50
        )

    with col2:
        sqft_lot = st.number_input(
            "Total Lot Size (sq ft)",
            min_value=638, max_value=1074218,
            value=5000, step=100
        )

        sqft_basement = st.number_input(
            "Basement Area (sq ft)",
            min_value=0, max_value=4820,
            value=0, step=50
        )

    st.divider()
    st.markdown("### ✨ Quality & Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        condition_options = {
            "Poor": 1,
            "Fair": 2,
            "Average": 3,
            "Good": 4,
            "Very Good": 5
        }

        selected_condition = st.selectbox(
            "House Condition",
            options=list(condition_options.keys()),
            index=2
        )

    with col2:
        view = st.select_slider(
            "View Quality",
            options=[0, 1, 2, 3, 4],
            value=0
        )

    with col3:
        waterfront = st.selectbox(
            "Waterfront Property",
            options=["No", "Yes"]
        )

    st.divider()
    st.markdown("### 📅 Property Age")
    col1, col2 = st.columns(2)

    with col1:
        yr_built = st.number_input(
            "Year Built",
            min_value=1900, max_value=2014,
            value=2000, step=1
        )

    with col2:
        yr_renovated = st.number_input(
            "Year Renovated (0 = Never)",
            min_value=0, max_value=2014,
            value=0, step=1
        )

    submitted = st.form_submit_button(
        "🔍 Predict House Price",
        use_container_width=True,
        type="primary"
    )

# ---------------- PREDICTION ----------------
if submitted:

    input_data = {
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sqft_living": sqft_living,
        "sqft_lot": sqft_lot,
        "floors": floors,
        "waterfront": 1 if waterfront == "Yes" else 0,
        "view": view,
        "condition": condition_options[selected_condition],
        "sqft_above": sqft_above,
        "sqft_basement": sqft_basement,
        "yr_built": yr_built,
        "yr_renovated": yr_renovated,
        "house_age": 2026 - yr_built,
        "renovated": 1 if yr_renovated > 0 else 0
    }

    # Location features are currently not selected by the user.
    # They remain zero until city/ZIP selectors are added.
    for feature in features:
        if feature.startswith("city_") or feature.startswith("statezip_"):
            input_data[feature] = 0

    df = pd.DataFrame([input_data])
    df = df.reindex(columns=features, fill_value=0)

    # Check feature compatibility instead of dropping columns.
    if df.shape[1] != model.n_features_in_:
        st.error(
            f"Model expects {model.n_features_in_} features, "
            f"but the app prepared {df.shape[1]}. "
            "Retrain the model and replace model and feature files together."
        )
        st.stop()

    try:
        prediction_usd = float(model.predict(df)[0])

        if not pd.notna(prediction_usd):
            st.error("The model returned an invalid prediction.")
            st.stop()

        # Convert USD to INR.
        prediction_inr = prediction_usd * USD_TO_INR

        # Format automatically in lakhs or crores.
        if prediction_inr >= 1_00_00_000:
            formatted_price = (
                f"₹{prediction_inr / 1_00_00_000:.2f} crore"
            )
        else:
            formatted_price = (
                f"₹{prediction_inr / 1_00_000:.2f} lakh"
            )

        st.divider()
        st.subheader("📊 Your Prediction")

        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Estimated House Price</div>
            <div class="result-price">{formatted_price}</div>
            <p>Approx. ${prediction_usd:,.0f} USD before conversion</p>
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            f"Illustrative conversion rate: $1 = ₹{USD_TO_INR:.2f}. "
            "Actual exchange rates vary. The model uses US housing data, "
            "so this is not an Indian-market property valuation."
        )

        with st.expander("View entered features"):
            st.dataframe(
                pd.DataFrame(
                    list(input_data.items()),
                    columns=["Feature", "Value"]
                ),
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        st.error(f"Prediction failed: {e}")

st.divider()
st.caption(
    "HomeValue | Machine Learning Project | "
    "Predictions are estimates, not formal property valuations."
)
