import streamlit as st
import pandas as pd
import math
from datetime import date

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EMI Calculator",
    page_icon="📉",
    layout="centered",
)

st.title("📉 EMI (Loan) Calculator")
st.write("Calculate your monthly EMI, total interest, and see an amortization schedule.")


# -------------------------------------------------
# INPUT FORM
# -------------------------------------------------
st.subheader("🔢 Loan Details")

with st.form("emi_form"):
    col1, col2 = st.columns(2)

    with col1:
        principal = st.number_input(
            "Loan Amount (₹)",
            min_value=0.0,
            value=500000.0,
            step=10000.0,
            help="Total amount of loan (principal).",
        )

        annual_rate = st.number_input(
            "Annual Interest Rate (% p.a.)",
            min_value=0.0,
            value=8.0,
            step=0.25,
            help="Nominal annual interest rate (fixed).",
        )

    with col2:
        tenure_type = st.radio(
            "Tenure Type",
            options=["Years", "Months"],
            index=0,
            help="Choose if you want to enter tenure in years or months.",
        )

        if tenure_type == "Years":
            tenure_input = st.number_input(
                "Tenure (Years)",
                min_value=0.0,
                value=10.0,
                step=0.5,
            )
            total_months = int(tenure_input * 12)
        else:
            tenure_input = st.number_input(
                "Tenure (Months)",
                min_value=0.0,
                value=120.0,
                step=1.0,
            )
            total_months = int(tenure_input)

    start_date = st.date_input(
        "Loan Start Date (optional, for schedule)",
        value=date.today(),
    )

    submitted = st.form_submit_button("Calculate EMI")


# -------------------------------------------------
# CALCULATION LOGIC
# -------------------------------------------------
def calculate_emi(principal, annual_rate, total_months):
    if total_months <= 0:
        return 0.0

    monthly_rate = annual_rate / 12 / 100

    # If interest rate is 0%, simple division
    if monthly_rate == 0:
        return principal / total_months

    emi = principal * monthly_rate * (math.pow(1 + monthly_rate, total_months)) / (
        math.pow(1 + monthly_rate, total_months) - 1
    )
    return emi


def generate_schedule(principal, annual_rate, total_months, start_date, emi):
    """
    Generates amortization schedule as a DataFrame.
    """
    if total_months <= 0 or principal <= 0:
        return pd.DataFrame()

    monthly_rate = annual_rate / 12 / 100
    balance = principal

    rows = []

    # Generate monthly dates
    try:
        dates = pd.date_range(start=start_date, periods=total_months, freq="MS")
    except Exception:
        dates = [None] * total_months

    for i in range(total_months):
        if monthly_rate > 0:
            interest_component = balance * monthly_rate
            principal_component = emi - interest_component
        else:
            # Zero interest
            principal_component = principal / total_months
            interest_component = 0.0

        # Last instalment adjustment if rounding issues
        if principal_component > balance:
            principal_component = balance
            emi_actual = principal_component + interest_component
        else:
            emi_actual = emi

        closing_balance = balance - principal_component

        rows.append(
            {
                "Month #": i + 1,
                "Date": dates[i].date() if dates[i] is not None else None,
                "Opening Balance (₹)": round(balance, 2),
                "EMI (₹)": round(emi_actual, 2),
                "Principal Component (₹)": round(principal_component, 2),
                "Interest Component (₹)": round(interest_component, 2),
                "Closing Balance (₹)": round(closing_balance, 2),
            }
        )

        balance = closing_balance

        if balance <= 0:
            break

    df_schedule = pd.DataFrame(rows)
    return df_schedule


# -------------------------------------------------
# DISPLAY RESULTS
# -------------------------------------------------
if submitted:
    if principal <= 0:
        st.error("Loan Amount must be greater than 0.")
    elif total_months <= 0:
        st.error("Tenure must be greater than 0.")
    else:
        emi = calculate_emi(principal, annual_rate, total_months)
        total_payment = emi * total_months
        total_interest = total_payment - principal

        st.subheader("📊 EMI Result")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Monthly EMI (₹)", f"{emi:,.2f}")
        col_b.metric("Total Interest (₹)", f"{total_interest:,.2f}")
        col_c.metric("Total Payment (₹)", f"{total_payment:,.2f}")

        with st.expander("See formula details"):
            st.markdown(
                f"""
**EMI Formula (for fixed-rate loans):**

\[
EMI = P \\times r \\times \\frac{{(1 + r)^n}}{{(1 + r)^n - 1}}
\]

Where:

- \( P \) = Principal = ₹{principal:,.2f}  
- \( r \) = Monthly Interest Rate = {annual_rate:.2f}% / 12 = {annual_rate/12:.4f}%  
- \( n \) = Number of Months = {total_months}

For 0% interest, EMI = Principal / Number of Months.
"""
            )

        # Amortization Schedule
        st.subheader("📅 Amortization Schedule")

        df_schedule = generate_schedule(principal, annual_rate, total_months, start_date, emi)

        if df_schedule.empty:
            st.info("Schedule could not be generated. Please check inputs.")
        else:
            st.dataframe(df_schedule, use_container_width=True, height=400)

            # Download schedule
            csv_data = df_schedule.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Schedule as CSV",
                data=csv_data,
                file_name="emi_amortization_schedule.csv",
                mime="text/csv",
            )

            # Simple charts
            st.subheader("📈 Principal vs Interest Over Time")

            chart_df = df_schedule[["Month #", "Principal Component (₹)", "Interest Component (₹)"]].set_index(
                "Month #"
            )
            st.area_chart(chart_df)


# -------------------------------------------------
# FOOTER / HELP
# -------------------------------------------------
st.markdown("---")
st.markdown(
    """
### ℹ️ About This App

This EMI Calculator helps you:

- Compute **monthly EMI** based on loan amount, interest rate, and tenure  
- See **total interest** and **total amount payable**  
- View a **month-wise amortization schedule**  
- Download the schedule as a **CSV file**  

Useful for **home loans, personal loans, car loans, education loans**, etc.
"""
)
