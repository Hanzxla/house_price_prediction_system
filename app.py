
# ---------------- PREDICTION ----------------
if submitted:

    # Convert the selected inputs into numerical values
    condition_score = condition_labels[selected_condition]
    waterfront_score = 1 if waterfront_label == "Yes" else 0

    # Calculate a simulated price using the property details.
    # The base price is ₹36 lakh.
    price_lakh = 36.0

    # Larger houses cost more
    price_lakh += (sqft_living - 370) * 0.006

    # More bedrooms and bathrooms increase the estimate
    price_lakh += (bedrooms - 1) * 4
    price_lakh += (bathrooms - 1) * 3

    # Additional property features
    price_lakh += (floors - 1) * 5
    price_lakh += (sqft_lot - 638) * 0.00002
    price_lakh += sqft_above * 0.001
    price_lakh += sqft_basement * 0.0015
    price_lakh += view * 2
    price_lakh += (condition_score - 1) * 2
    price_lakh += waterfront_score * 15

    # Newer houses get a higher estimate
    house_age = 2026 - yr_built
    price_lakh += max(0, 126 - house_age) * 0.15

    # Renovation adds a small amount
    if yr_renovated > 0:
        price_lakh += 5

    # Keep the result within the requested range
    price_lakh = max(36.0, min(price_lakh, 200.0))

    prediction_inr = price_lakh * 100_000

    st.markdown("---")
    st.subheader("📊 Your Prediction")

    if prediction_inr >= 1_00_00_000:
        formatted_price = f"₹{prediction_inr / 1_00_00_000:.2f} crore"
    else:
        formatted_price = f"₹{prediction_inr / 1_00_000:.2f} lakh"

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Estimated House Price</div>
        <div class="result-price">{formatted_price}</div>
        <div class="small-note">
            Simulated estimate based on the entered property details
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "This is a rule-based demonstration estimate, not a prediction "
        "from the trained Random Forest model or a verified market price."
    )

    with st.expander("View entered property details"):
        input_data = {
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Living Area (sq ft)": sqft_living,
            "Lot Size (sq ft)": sqft_lot,
            "Floors": floors,
            "Condition": selected_condition,
            "View": view,
            "Waterfront": waterfront_label,
            "Area Above Ground": sqft_above,
            "Basement Area": sqft_basement,
            "Year Built": yr_built,
            "Year Renovated": yr_renovated
        }

        st.dataframe(
            pd.DataFrame(
                list(input_data.items()),
                columns=["Feature", "Value"]
            ),
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")
st.caption(
    "HomeValue · Machine Learning Project · "
    "Simulated estimates are not formal property valuations."
)
