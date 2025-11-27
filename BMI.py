import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="BMI Calculator",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ BMI (Body Mass Index) Calculator")
st.write("Calculate your BMI and understand your weight category based on WHO guidelines.")


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI given weight in kg and height in cm."""
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return bmi


def bmi_category(bmi: float) -> str:
    """Return BMI category based on WHO classification."""
    if bmi <= 0:
        return "Invalid"
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def category_advice(category: str) -> str:
    """Simple advice text based on BMI category."""
    if category == "Underweight":
        return "You are under the normal weight range. Consider a balanced diet with sufficient calories and talk to a healthcare professional."
    elif category == "Normal weight":
        return "Great! You are in the normal range. Maintain a healthy lifestyle with balanced diet and regular exercise."
    elif category == "Overweight":
        return "You are slightly above the normal range. Regular exercise and a controlled diet may help you move towards a healthier weight."
    elif category == "Obese":
        return "Your BMI is in the obese range. It’s a good idea to consult a doctor or nutritionist and focus on lifestyle changes."
    else:
        return "Please enter valid values for height and weight."


# -------------------------------------------------
# INPUT FORM
# -------------------------------------------------
st.subheader("🔢 Enter Your Details")

with st.form("bmi_form"):
    col1, col2 = st.columns(2)

    with col1:
        unit_system = st.radio(
            "Unit System",
            options=["Metric (kg, cm)", "Imperial (lbs, feet+inches)"],
            index=0,
        )

    if unit_system == "Metric (kg, cm)":
        with col1:
            weight = st.number_input(
                "Weight (kg)",
                min_value=1.0,
                value=70.0,
                step=0.5,
            )
        with col2:
            height = st.number_input(
                "Height (cm)",
                min_value=50.0,
                value=170.0,
                step=0.5,
            )
    else:
        # Imperial input, converted to metric internally
        with col1:
            weight_lbs = st.number_input(
                "Weight (lbs)",
                min_value=1.0,
                value=154.0,
                step=1.0,
            )
        with col2:
            height_feet = st.number_input(
                "Height (feet)",
                min_value=1.0,
                value=5.0,
                step=1.0,
            )
            height_inches = st.number_input(
                "Additional Height (inches)",
                min_value=0.0,
                value=7.0,
                step=1.0,
            )

        # Convert to metric
        weight = weight_lbs * 0.45359237  # lbs to kg
        total_inches = height_feet * 12 + height_inches
        height = total_inches * 2.54  # inches to cm

    submitted = st.form_submit_button("Calculate BMI")


# -------------------------------------------------
# CALCULATE & DISPLAY RESULTS
# -------------------------------------------------
if submitted:
    bmi = calculate_bmi(weight, height)
    category = bmi_category(bmi)

    if bmi <= 0:
        st.error("Please enter valid height and weight values.")
    else:
        st.subheader("📊 Your BMI Result")

        col_a, col_b = st.columns(2)
        col_a.metric("BMI Value", f"{bmi:.2f}")
        col_b.metric("Category", category)

        # Simple visual scale using progress bar (0–40 mapped to 0–1)
        st.markdown("**BMI Position on Scale (approximate)**")
        scale_bmi = min(max(bmi, 0), 40)  # clamp between 0 and 40
        st.progress(scale_bmi / 40)

        # Colorful category highlight
        if category == "Underweight":
            color = "#3498db"  # blue
        elif category == "Normal weight":
            color = "#2ecc71"  # green
        elif category == "Overweight":
            color = "#f1c40f"  # yellow
        elif category == "Obese":
            color = "#e74c3c"  # red
        else:
            color = "#7f8c8d"  # grey

        st.markdown(
            f"""
            <div style="
                padding: 12px;
                border-radius: 8px;
                border: 1px solid {color};
                background-color: {color}20;
                margin-top: 10px;
            ">
            <strong>Interpretation:</strong> {category}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 💡 Suggestions")
        st.write(category_advice(category))


# -------------------------------------------------
# INFO SECTION
# -------------------------------------------------
st.markdown("---")
st.markdown(
    """
### ℹ️ What is BMI?

Body Mass Index (BMI) is a simple number calculated from your **weight** and **height**:

\[
BMI = \\frac{\\text{weight (kg)}}{(\\text{height (m)})^2}
\]

**Common BMI categories (WHO):**

- **Underweight:** BMI \< 18.5  
- **Normal weight:** 18.5 ≤ BMI \< 25  
- **Overweight:** 25 ≤ BMI \< 30  
- **Obese:** BMI ≥ 30  

> ⚠️ BMI is a general guideline and does **not** account for muscle mass, body composition, age, or gender.  
> For health decisions, always consult a medical professional.
"""
)
