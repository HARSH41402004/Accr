import streamlit as st
import pandas as pd

st.title("🌍 World GDP Calculator (No Plotly Version)")

st.write("Upload GDP data and calculate total World GDP by year.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["Country", "Year", "GDP"]
    if not all(c in df.columns for c in required_cols):
        st.error("CSV must contain columns: Country, Year, GDP")
        st.stop()

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")

    st.subheader("Uploaded Data")
    st.dataframe(df)

    world_gdp = df.groupby("Year")["GDP"].sum().reset_index()
    world_gdp.rename(columns={"GDP": "World_GDP"}, inplace=True)

    st.subheader("🌐 World GDP by Year")
    st.dataframe(world_gdp)

    st.line_chart(world_gdp, x="Year", y="World_GDP")
else:
    st.info("Please upload a CSV file to continue.")
