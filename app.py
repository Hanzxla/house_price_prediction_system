
import os
import joblib
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="HomeValue | House Price Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_artifacts():
    model = joblib.load(os.path.join(BASE_DIR, "random_forest.pkl"))
    saved_features = joblib.load(os.path.join(BASE_DIR, "features.pkl"))

    # Your original training code excluded these two columns
    # before fitting the Random Forest.
    model_features = [
        f for f in saved_features
        if f not in ["street", "country"]
    ]

    return model, model_features


try:
    model, features = load_artifacts()
except Exception as e:
    st.error(f"Could not load the model files: {e}")
    st.stop()

# ---------------- STYLING ----------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 1.8rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #173b67, #277da1);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        color: white;
        margin-bottom: 0.4rem;
        font-size: 2.2rem;
    }

    .hero p {
        color: #e5f2ff;
        margin-bottom: 0;
        font-size: 1rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }

    .result-card {
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #b7dfc6;
        background: #f0faf4;
        color: #164b2c;
        text-align: center;
    }

    .result-label {
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .result-price {
        font-size: 2.3rem;
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .small-note {
        font-size: 0.85rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>🏡 HomeValue</h1>
    <p>Smart House Price Prediction · Enter your property details
    to estimate its value.</p>
</div>
""", unsafe_allow_html=True)

# Illustrative conversion only; update when needed.
USD_TO_INR = 95.0

with st.sidebar:
    st.title("🏡 HomeValue")
    st.caption("House Price Prediction System")
    st.divider()

    st.markdown("### How it works")
    st.write("1. Enter the house details.")
    st.write("2. Click Predict House Price.")
    st.write("3. View the estimated price in INR.")

    st.divider()
    st.caption("Model trained on US housing data.")
    st.caption("The INR amount is a currency conversion, not an Indian-market valuation.")

# ---------------- INPUT FORM ----------------
st.subheader("🏠 Property Details")
st.write("Fill in the details below to get your estimate.")

with st.form("house_prediction_form"):

    st.markdown(
        '<div class="section-title">🛏️ Rooms & Layout</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        bedrooms = st.number_input(
            "Bedrooms",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )

    with col2:
        bathrooms = st.number_input(
            "Bathrooms",
            min_value=1,
            max_value=8,
            value=2,
            step=1
        )

    with col3:
        floors = st.selectbox(
            "Number of Floors",
            options=[1, 2, 3],
            index=0
        )

    st.divider()

    st.markdown(
        '<div class="section-title">📐 Property Size</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        sqft_living = st.number_input(
            "Living Area (sq ft)",
            min_value=370,
            max_value=13540,
            value=2000,
            step=50
        )

        sqft_above = st.number_input(
            "Area Above Ground (sq ft)",
            min_value=0,
            max_value=10000,
            value=1500,
            step=50
        )

    with col2:
        sqft_lot = st.number_input(
            "Total Lot Size (sq ft)",
            min_value=638,
            max_value=1074218,
            value=5000,
            step=100
        )

        sqft_basement = st.number_input(
            "Basement Area (sq ft)",
            min_value=0,
            max_value=4820,
            value=0,
            step=50
        )

    st.divider()

    st.markdown(
        '<div class="section-title">✨ Quality & Features</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        condition_labels = {
            "Poor": 1,
            "Fair": 2,
            "Average": 3,
            "Good": 4,
            "Very Good": 5
        }

        selected_condition = st.selectbox(
            "House Condition",
            options=list(condition_labels.keys()),
            index=2,
            help="Choose the overall physical condition of the house."
        )

    with col2:
        view = st.select_slider(
            "View Quality",
            options=[0, 1, 2, 3, 4],
            value=0,
            help="0 = No notable view, 4 = Best view rating"
        )

    with col3:
        waterfront_label = st.selectbox(
            "Waterfront Property",
            options=["No", "Yes"],
            index=0
        )

    st.divider()

    st.markdown(
        '<div class="section-title">📅 Property Age</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        yr_built = st.number_input(
            "Year Built",
            min_value=1900,
            max_value=2014,
            value=2000,
            step=1
        )

    with col2:
        yr_renovated = st.number_input(
            "Year Renovated (0 = Never)",
            min_value=0,
            max_value=2014,
            value=0,
            step=1
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
        "waterfront": 1 if waterfront_label == "Yes" else 0,
        "view": view,
        "condition": condition_labels[selected_condition],
        "sqft_above": sqft_above,
        "sqft_basement": sqft_basement,
        "yr_built": yr_built,
        "yr_renovated": yr_renovated,
        "house_age": 2026 - yr_built,
        "renovated": 1 if yr_renovated > 0 else 0
    }

    # Create dummy columns for all locations.
    # No location is selected in this interface, so all remain zero.
    for feature in features:
        if feature.startswith("city_") or feature.startswith("statezip_"):
            input_data[feature] = 0

    # Match the exact feature order expected by the model.
    df = pd.DataFrame([input_data])
    df = df.reindex(columns=features, fill_value=0)

    # Never silently remove model features.
    if df.shape[1] != model.n_features_in_:
        st.error(
            f"Model expects {model.n_features_in_} features, "
            f"but the app prepared {df.shape[1]}. "
            "Please check your saved model and features.pkl."
        )
        st.stop()

    try:
        prediction_usd = float(model.predict(df)[0])

        if not pd.notna(prediction_usd):
            st.error("The model returned an invalid prediction.")
            st.stop()

        prediction_inr = prediction_usd * USD_TO_INR

        st.markdown("---")
        st.subheader("📊 Your Prediction")

        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Estimated House Price</div>
            <div class="result-price">₹{prediction_inr:,.0f}</div>
            <div class="small-note">
                Approx. ${prediction_usd:,.0f} USD before conversion
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            f"Illustrative conversion: $1 = ₹{USD_TO_INR:.2f}. "
            "The actual exchange rate may differ."
        )

        with st.expander("View entered property details"):
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

st.markdown("---")
st.caption(
    "HomeValue · Machine Learning Project · "
    "Estimates are model outputs and should not be treated as formal valuations."
)
