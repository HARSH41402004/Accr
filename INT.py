import streamlit as st
from datetime import date

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Accrued Interest Calculator",
    page_icon="📈",
    layout="centered",
)

st.title("📈 Accrued Interest Calculator")
st.write(
    "Calculate accrued interest between two dates using simple interest with different day-count conventions."
)

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
st.subheader("🔢 Input Details")

with st.form("accrued_interest_form"):
    col1, col2 = st.columns(2)

    with col1:
        principal = st.number_input(
            "Principal / Face Value (₹)",
            min_value=0.0,
            value=10000.0,
            step=100.0,
            help="The amount on which interest is calculated.",
        )

    with col2:
        annual_rate = st.number_input(
            "Annual Interest Rate (%)",
            min_value=0.0,
            value=8.0,
            step=0.25,
            help="Nominal yearly interest rate.",
        )

    col3, col4 = st.columns(2)

    with col3:
        start_date = st.date_input(
            "Start Date (Interest begins)",
            value=date(date.today().year, 1, 1),
            help="Date from which interest starts accruing.",
        )

    with col4:
        end_date = st.date_input(
            "End Date (As of)",
            value=date.today(),
            help="Date till which interest is accrued.",
        )

    day_count_basis = st.selectbox(
        "Day Count Convention",
        options=["Actual/365", "Actual/360"],
        index=0,
        help="Financial convention for number of days in a year.",
    )

    submitted = st.form_submit_button("Calculate")

# -------------------------------------------------
# CALCULATION LOGIC
# -------------------------------------------------
if submitted:
    if end_date < start_date:
        st.error("❌ End Date cannot be earlier than Start Date.")
    elif principal == 0 or annual_rate == 0:
        st.warning("Please enter a Principal and Interest Rate greater than 0.")
    else:
        # Number of days between dates
        delta_days = (end_date - start_date).days

        if day_count_basis == "Actual/365":
            year_days = 365
        else:  # "Actual/360"
            year_days = 360

        # Simple interest accrued
        accrued_interest = principal * (annual_rate / 100) * (delta_days / year_days)
        total_amount = principal + accrued_interest

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------
        st.subheader("📊 Result")

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Days Between", f"{delta_days} days")
        col_res2.metric("Accrued Interest (₹)", f"{accrued_interest:,.2f}")
        col_res3.metric("Principal + Interest (₹)", f"{total_amount:,.2f}")

        with st.expander("See formula and details"):
            st.markdown(
                f"""
**Formula used (Simple Interest):**

- Number of days = `End Date - Start Date` = **{delta_days} days**  
- Year basis = **{year_days} days** (from **{day_count_basis}**)  

**Accrued Interest** = Principal × (Annual Rate / 100) × (Days / Year Basis)

= ₹{principal:,.2f} × ({annual_rate:.2f} / 100) × ({delta_days} / {year_days})  
= **₹{accrued_interest:,.2f}**
"""
            )

# -------------------------------------------------
# EXTRA INFO / HELP
# -------------------------------------------------
st.markdown("---")
st.markdown(
    """
### ℹ️ What is Accrued Interest?

Accrued interest is the amount of interest that has accumulated on a principal amount between two dates, 
but has not yet been paid.  
This is commonly used for:

- Loans and advances  
- Bonds and debentures  
- Fixed deposits (for interim calculations)  

This app uses **simple interest** with a chosen **day-count convention** (Actual/365 or Actual/360).
"""
)
