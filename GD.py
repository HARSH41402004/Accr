# world_gdp_app.py
# -------------------------------------------
# Simple World GDP Calculation App
# -------------------------------------------
# How to run locally:
#   1) pip install streamlit pandas plotly
#   2) streamlit run world_gdp_app.py
#
# Then upload this file to your GitHub repo.

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# ----------------- Page config -----------------
st.set_page_config(
    page_title="World GDP Calculator",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 World GDP Calculation App")
st.write(
    "This app helps you calculate **World GDP** by summing up GDP of all countries "
    "for each year. You can use sample data or upload your own CSV file."
)

# ----------------- Helper: sample data -----------------
@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """
    Returns a simple sample GDP dataset.
    Columns:
      - Country
      - Year
      - GDP (in billion USD)
    """
    csv_text = """Country,Year,GDP
USA,2018,20580
USA,2019,21433
USA,2020,20937
USA,2021,23150
USA,2022,25462
China,2018,13608
China,2019,14343
China,2020,14723
China,2021,17734
China,2022,17963
India,2018,2713
India,2019,2875
India,2020,2668
India,2021,3173
India,2022,3385
Japan,2018,4971
Japan,2019,5082
Japan,2020,5058
Japan,2021,4939
Japan,2022,4231
Germany,2018,3997
Germany,2019,3861
Germany,2020,3800
Germany,2021,4257
Germany,2022,4082
"""
    return pd.read_csv(StringIO(csv_text))


REQUIRED_COLUMNS = ["Country", "Year", "GDP"]

# ----------------- Sidebar controls -----------------
st.sidebar.header("Data Options")

data_source = st.sidebar.radio(
    "Choose GDP data source:",
    ("Use sample data", "Upload CSV"),
)

st.sidebar.markdown(
    """
**CSV format required:**

- Must have columns:
  - `Country`
  - `Year`
  - `GDP`
- `Year` = integer (e.g. 2021)  
- `GDP` = numeric (e.g. 1234.56)
"""
)

# ----------------- Load data -----------------
df = None
error_msg = None

if data_source == "Use sample data":
    df = load_sample_data()
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload your GDP CSV file", type=["csv"]
    )
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            error_msg = f"❌ Error reading CSV file: {e}"

# Validate dataframe
if df is not None:
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        error_msg = (
            "❌ Missing required column(s): "
            + ", ".join(missing_cols)
            + "\n\nYour file must contain columns: Country, Year, GDP."
        )

if error_msg:
    st.error(error_msg)
    st.stop()

if df is None:
    st.info("Please upload a CSV file or select sample data from the sidebar.")
    st.stop()

# Clean up & enforce dtypes
df = df.copy()
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")

df = df.dropna(subset=["Year", "GDP"])

# ----------------- Display raw data -----------------
st.subheader("📊 Country-wise GDP Data")
with st.expander("Show / Edit Data", expanded=True):
    st.write(
        "You can edit GDP values directly in this table. "
        "Changes will be used for world GDP calculations."
    )
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        key="country_gdp_editor",
    )

# Use edited data for calculations
df = edited_df

# ----------------- World GDP calculation -----------------
st.subheader("🌐 World GDP by Year")

# Group by year to compute world GDP
world_gdp = (
    df.groupby("Year", as_index=False)["GDP"]
    .sum()
    .rename(columns={"GDP": "World_GDP"})
    .sort_values("Year")
)

# Sidebar filters: year range
min_year = int(world_gdp["Year"].min())
max_year = int(world_gdp["Year"].max())

year_range = st.slider(
    "Select year range for analysis:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
)

filtered_world_gdp = world_gdp[
    (world_gdp["Year"] >= year_range[0]) & (world_gdp["Year"] <= year_range[1])
]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Latest Year in Data",
        value=int(world_gdp["Year"].max()),
    )

with col2:
    latest_year = int(world_gdp["Year"].max())
    latest_value = float(world_gdp.loc[world_gdp["Year"] == latest_year, "World_GDP"].iloc[0])
    st.metric(
        label=f"World GDP in {latest_year} (sum of all countries)",
        value=f"{latest_value:,.2f}",
    )

st.write("### World GDP Table")
st.dataframe(filtered_world_gdp, use_container_width=True)

# ----------------- Charts -----------------
st.write("### 📈 World GDP Trend")

fig_world = px.line(
    filtered_world_gdp,
    x="Year",
    y="World_GDP",
    markers=True,
    labels={"World_GDP": "World GDP", "Year": "Year"},
    title="World GDP Trend (Summed from Country Data)",
)
st.plotly_chart(fig_world, use_container_width=True)

st.write("### 🌎 Country-wise GDP (Selected Year)")

selected_year = st.selectbox(
    "Select a year to view country-wise GDP:",
    sorted(world_gdp["Year"].unique()),
    index=len(world_gdp["Year"].unique()) - 1,
)

df_year = df[df["Year"] == selected_year].sort_values("GDP", ascending=False)

col1, col2 = st.columns([2, 3])

with col1:
    st.write(f"Top countries by GDP in **{selected_year}**")
    st.dataframe(df_year, use_container_width=True)

with col2:
    if not df_year.empty:
        fig_country = px.bar(
            df_year,
            x="Country",
            y="GDP",
            title=f"GDP by Country in {selected_year}",
            labels={"GDP": "GDP", "Country": "Country"},
        )
        st.plotly_chart(fig_country, use_container_width=True)
    else:
        st.info("No data available for this year.")

# ----------------- Download results -----------------
st.subheader("⬇️ Download Calculated World GDP")

csv_world = filtered_world_gdp.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download World GDP CSV",
    data=csv_world,
    file_name="world_gdp_by_year.csv",
    mime="text/csv",
)

st.success("✅ World GDP calculation complete. Adjust data above to recalculate automatically.")
