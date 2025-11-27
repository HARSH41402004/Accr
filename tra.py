import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide"
)

st.title("💸 Expense Tracker App")
st.write("Track your expenses, categorize them, monitor totals, and download your reports easily.")


# ---------------------------------------------------
# INITIALIZE DATA STORAGE
# ---------------------------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Note"]
    )


# ---------------------------------------------------
# SIDEBAR ACTIONS
# ---------------------------------------------------
st.sidebar.header("📂 Options")

uploaded_file = st.sidebar.file_uploader("Upload existing expense CSV", type=["csv"])

if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        required = {"Date", "Category", "Amount", "Note"}
        if required.issubset(df_uploaded.columns):
            st.session_state.expenses = df_uploaded
            st.sidebar.success("Data uploaded successfully!")
        else:
            st.sidebar.error("CSV missing required columns.")
    except Exception as e:
        st.sidebar.error(f"Upload error: {e}")


if st.sidebar.button("Reset All Data"):
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
    st.sidebar.success("All expenses cleared!")


# ---------------------------------------------------
# ADD EXPENSE ENTRY
# ---------------------------------------------------
st.subheader("➕ Add New Expense")

with st.form("expense_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date", datetime.today())

    with col2:
        category = st.text_input("Category (Food, Travel, Shopping, etc.)")

    with col3:
        amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)

    note = st.text_input("Note (optional)")

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if category.strip() == "":
            category = "Uncategorized"

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Category": category,
            "Amount": amount,
            "Note": note
        }

        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("Expense added!")


# ---------------------------------------------------
# SUMMARY SECTION
# ---------------------------------------------------
st.subheader("📊 Summary")

df = st.session_state.expenses.copy()

if df.empty:
    st.info("No expenses yet. Add some above!")
else:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    total_expense = df["Amount"].sum()
    monthly_expense = df.groupby(df["Date"].str.slice(0, 7))["Amount"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Expense (₹)", f"{total_expense:,.2f}")

    # Monthly chart
    col2.line_chart(monthly_expense)


# ---------------------------------------------------
# SHOW ALL EXPENSES TABLE
# ---------------------------------------------------
st.subheader("📒 All Expenses")

if df.empty:
    st.info("Your expense list is empty!")
else:
    df["Date"] = pd.to_datetime(df["Date"])
    df_sorted = df.sort_values("Date", ascending=False)

    st.dataframe(df_sorted, use_container_width=True)

    # Download button
    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Expense Report (CSV)",
        data=csv,
        file_name="expense_report.csv",
        mime="text/csv"
    )


# ---------------------------------------------------
# EXPENSES BY CATEGORY (BAR CHART)
# ---------------------------------------------------
if not df.empty:
    st.subheader("📂 Expense by Category")

    df_cat = df.groupby("Category")["Amount"].sum()

    st.bar_chart(df_cat)


# ---------------------------------------------------
# EXTRA HELP SECTION
# ---------------------------------------------------
st.markdown("---")
st.markdown("""
### ℹ️ About This App
This simple Expense Tracker helps you:
- Add expenses with date, category, amount, and notes  
- View total and monthly expenses  
- Download CSV reports  
- Visualize category-wise spending  
- Upload previous data to continue tracking  

Perfect for personal budgeting!  
""")
