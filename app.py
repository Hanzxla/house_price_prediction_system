
import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="HomeValue | House Price Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    <p>Smart House Price Estimator · Enter your property details
    to calculate an estimated price.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🏡 HomeValue")
    st.caption("House Price Prediction System")
    st.divider()

    st.markdown("### How it works")
    st.write("1. Enter the property details.")
    st.write("2. Click Predict House Price.")
    st.write("3. View the estimated price in INR.")

    st.divider()
    st.caption("Uses a rule-based demonstration calculation.")
    st.caption("The estimate is not a verified market valuation.")

# ---------------- INPUT FORM ----------------
st.subheader("🏠 Property Details")
st.write("Enter the details of the house below.")

condition_labels = {
    "Poor": 1,
    "Fair": 2,
    "Average": 3,
    "Good": 4,
    "Very Good": 5
}

with st.form("house_prediction_form"):

    st.markdown("### 🛏️ Rooms & Layout")
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
            options=[1, 2, 3]
        )

    st.divider()
    st.markdown("### 📐 Property Size")
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
    st.markdown("### ✨ Quality & Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_condition = st.selectbox(
            "House Condition",
            options=list(condition_labels.keys()),
            index=2
        )

    with col2:
        view = st.select_slider(
            "View Quality",
            options=[0, 1, 2, 3, 4],
            value=0
        )

    with col3:
        waterfront_label = st.selectbox(
            "Waterfront Property",
            options=["No", "Yes"]
        )

    st.divider()
    st.markdown("### 📅 Property Age")
    col1, col2 = st.columns(2)

    with col1:
        yr_built = st.number_input(
            "Year Built",
            min_value=1900,
            max_value=2026,
            value=2000,
            step=1
        )

    with col2:
        yr_renovated = st.number_input(
            "Year Renovated (0 = Never)",
            min_value=0,
            max_value=2026,
            value=0,
            step=1
        )

    submitted = st.form_submit_button(
        "🔍 Predict House Price",
        use_container_width=True,
        type="primary"
    )

# ---------------- PRICE CALCULATION ----------------
if submitted:

    # Validate related area values
    if sqft_above + sqft_basement > sqft_living:
        st.warning(
            "Above-ground area plus basement area should not exceed "
            "the total living area. Please adjust the values."
        )
        st.stop()

    if yr_renovated != 0 and yr_renovated < yr_built:
        st.warning(
            "Renovation year cannot be earlier than the construction year."
        )
        st.stop()

    # Base estimate in lakh rupees
    price_lakh = 36.0

    # Size: every additional 100 sq ft adds ₹0.6 lakh
    price_lakh += (sqft_living - 370) * 0.006

    # Rooms
    price_lakh += (bedrooms - 1) * 4.0
    price_lakh += (bathrooms - 1) * 3.0

    # Layout and plot size
    price_lakh += (floors - 1) * 5.0
    price_lakh += (sqft_lot - 638) * 0.00002
    price_lakh += sqft_above * 0.001
    price_lakh += sqft_basement * 0.0015

    # Property quality
    price_lakh += view * 2.0
    price_lakh += (condition_labels[selected_condition] - 1) * 2.0

    if waterfront_label == "Yes":
        price_lakh += 15.0

    # Newer houses receive a higher estimate
    house_age = 2026 - yr_built
    price_lakh += max(0, 126 - house_age) * 0.15

    # Renovation adjustment
    if yr_renovated > 0:
        price_lakh += 5.0

    # Keep the displayed estimate within ₹36 lakh to ₹2 crore
    price_lakh = max(36.0, min(price_lakh, 200.0))
    prediction_inr = price_lakh * 100000

    # Format price
    if price_lakh >= 100:
        formatted_price = f"₹{price_lakh / 100:.2f} crore"
    else:
        formatted_price = f"₹{price_lakh:.2f} lakh"

    st.markdown("---")
    st.subheader("📊 Your Estimated Price")

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Estimated House Price</div>
        <div class="result-price">{formatted_price}</div>
        <div class="small-note">
            Demonstration estimate based on the entered details
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "The result is limited to ₹36 lakh–₹2 crore. "
        "This rule-based estimate is for demonstration only; "
        "it is not generated by the trained machine learning model."
    )

    # Property summary
    with st.expander("View entered property details"):
        property_details = {
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Floors": floors,
            "Living Area (sq ft)": sqft_living,
            "Lot Size (sq ft)": sqft_lot,
            "Above Ground Area (sq ft)": sqft_above,
            "Basement Area (sq ft)": sqft_basement,
            "Condition": selected_condition,
            "View Quality": view,
            "Waterfront": waterfront_label,
            "Year Built": yr_built,
            "Year Renovated": yr_renovated
        }

        st.dataframe(
            pd.DataFrame(
                list(property_details.items()),
                columns=["Feature", "Value"]
            ),
            use_container_width=True,
            hide_index=True
        )

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    "HomeValue · House Price Estimator · "
    "Demonstration estimates are not formal property valuations."
)
