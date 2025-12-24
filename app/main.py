import sys
from pathlib import Path
import json
import pandas as pd
import streamlit as st

# Ensure project root on sys.path when running via 'streamlit run app/main.py'
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data.schema import from_dict
from app.services import recommend
from app.utils.validators import parse_bp

st.set_page_config(page_title="Medical Diet Recommender", layout="wide")

st.title("Rule-Based Medical Diet Recommendation System")
st.caption("Educational tool. Not medical advice. Consult a healthcare professional.")

with st.sidebar:
    st.header("Profile Input")
    with st.expander("Personal Details", expanded=True):
        age = st.number_input("Age", min_value=1, max_value=100, value=30)
        gender = st.selectbox("Gender", ["male", "female", "other"], index=0)
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=170.0, step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        body_type = st.text_input("Body Type (optional)")

    with st.expander("Medical / Health Parameters", expanded=True):
        conditions = st.multiselect(
            "Existing conditions",
            [
                "diabetes",
                "hypertension",
                "thyroid",
                "heart disease",
                "kidney disease",
                "pcod",
                "pcos",
                "gastric issues",
            ],
        )
        allergies = st.multiselect("Allergies", ["lactose", "gluten", "nuts", "seafood", "soy", "sesame"]) 
        medications_text = st.text_input("Current medications (comma-separated)")
        blood_sugar = st.number_input("Blood Sugar (mg/dL)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        bp_text = st.text_input("Blood Pressure (e.g., 120/80)")
        cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=25.0, value=0.0, step=0.1)

    with st.expander("Dietary Preferences", expanded=True):
        diet_type = st.radio("Diet type", ["veg", "non-veg", "vegan"], index=0, horizontal=True)
        likes = st.text_input("Food likes (comma-separated)")
        dislikes = st.text_input("Food dislikes (comma-separated)")
        preferred_cuisine = st.multiselect("Preferred cuisines", ["indian", "asian", "mediterranean", "global"]) 
        meal_frequency = st.slider("Meal frequency", 3, 6, 3)
        snacking_pref = st.radio("Snacking preference", ["low", "moderate", "high"], index=1, horizontal=True)

    with st.expander("Lifestyle Parameters", expanded=True):
        activity = st.selectbox("Activity level", ["sedentary", "light", "moderate", "active", "athlete"], index=0)
        exercise = st.text_input("Exercise routine", value="none")
        sleep = st.number_input("Sleep (hours)", min_value=0.0, max_value=14.0, value=7.0, step=0.5)
        stress = st.selectbox("Stress level", ["low", "moderate", "high"], index=1)

    with st.expander("Nutritional Requirements (optional overrides)", expanded=False):
        daily_cals = st.number_input("Daily calories (override)", min_value=0, max_value=6000, value=0, step=50)
        protein_g = st.number_input("Protein (g)", min_value=0.0, max_value=400.0, value=0.0, step=1.0)
        carbs_g = st.number_input("Carbs (g)", min_value=0.0, max_value=800.0, value=0.0, step=1.0)
        fats_g = st.number_input("Fats (g)", min_value=0.0, max_value=300.0, value=0.0, step=1.0)
        salt_limit_g = st.number_input("Salt limit (g NaCl)", min_value=0.0, max_value=20.0, value=0.0, step=0.5)
        sugar_limit_g = st.number_input("Sugar limit (g)", min_value=0.0, max_value=200.0, value=0.0, step=1.0)
        water_l = st.number_input("Water (liters)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

    with st.expander("Special Diet Rules", expanded=True):
        low_gi = st.checkbox("Low GI diet", value=False)
        low_sodium = st.checkbox("Low sodium diet", value=False)
        high_fiber = st.checkbox("High fiber diet", value=False)
        renal = st.checkbox("Renal diet", value=False)
        high_protein = st.checkbox("High protein diet", value=False)
        anti_inflam = st.checkbox("Anti-inflammatory diet", value=False)
        weight_gain = st.checkbox("Weight gain diet", value=False)
        weight_loss = st.checkbox("Weight loss diet", value=False)
        gluten_free = st.checkbox("Gluten-free diet", value=False)
        lactose_free = st.checkbox("Lactose-free diet", value=False)

    run_btn = st.button("Get Recommendations", type="primary")

if run_btn:
    meds = [m.strip() for m in medications_text.split(",") if m.strip()]
    likes_list = [x.strip() for x in likes.split(",") if x.strip()]
    dislikes_list = [x.strip() for x in dislikes.split(",") if x.strip()]

    bp_parsed = parse_bp(bp_text)

    data = {
        "personal": {
            "age": age,
            "gender": gender,
            "height": height_cm,
            "weight": weight_kg,
            "body_type": body_type,
        },
        "medical": {
            "conditions": conditions,
            "allergies": allergies,
            "medications": meds,
            "blood_sugar_mgdl": blood_sugar or None,
            "blood_pressure": list(bp_parsed) if bp_parsed else None,
            "cholesterol_mgdl": cholesterol or None,
            "hemoglobin_gdl": hemoglobin or None,
        },
        "dietary": {
            "diet_type": diet_type,
            "likes": likes_list,
            "dislikes": dislikes_list,
            "preferred_cuisine": preferred_cuisine,
            "meal_frequency": meal_frequency,
            "snacking_preference": snacking_pref,
        },
        "lifestyle": {
            "activity_level": activity,
            "exercise_routine": exercise,
            "sleep_hours": sleep,
            "stress_level": stress,
        },
        "nutrition": {
            "daily_calories": int(daily_cals) if daily_cals else None,
            "protein_g": protein_g or None,
            "carbs_g": carbs_g or None,
            "fats_g": fats_g or None,
            "salt_limit_g": salt_limit_g or None,
            "sugar_limit_g": sugar_limit_g or None,
            "water_liters": water_l or None,
        },
        "special": {
            "low_gi": low_gi,
            "low_sodium": low_sodium,
            "high_fiber": high_fiber,
            "renal": renal,
            "high_protein": high_protein,
            "anti_inflammatory": anti_inflam,
            "weight_gain": weight_gain,
            "weight_loss": weight_loss,
            "gluten_free": gluten_free,
            "lactose_free": lactose_free,
        },
    }

    profile = from_dict(data)
    result = recommend(profile)

    st.success("Recommendations generated.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Calories & Macros")
        _summary_row = {
            "daily_calories": result["calorie_breakdown"]["daily_calories"],
            "protein_g": result["calorie_breakdown"]["macros"]["protein_g"],
            "carbs_g": result["calorie_breakdown"]["macros"]["carbs_g"],
            "fats_g": result["calorie_breakdown"]["macros"]["fats_g"],
            "water_liters": result["nutrition_targets"]["water_liters"],
            "sodium_mg_limit": result["nutrition_targets"]["sodium_mg_limit"],
            "sugar_g_limit": result["nutrition_targets"]["sugar_g_limit"],
        }
        st.dataframe(pd.DataFrame([_summary_row]), use_container_width=True)
        st.subheader("Foods to include")
        st.dataframe(pd.DataFrame({"food": result["foods_to_include"]}), use_container_width=True)
        st.subheader("Foods to avoid")
        st.dataframe(pd.DataFrame({"food": result["foods_to_avoid"]}), use_container_width=True)

    with col2:
        st.subheader("Personalized Meal Plan")
        for meal in ["breakfast", "lunch", "dinner"]:
            items = result["personalized_meal_plan"].get(meal, [])
            st.markdown(f"**{meal.title()}**")
            if items:
                st.dataframe(items, use_container_width=True)
            else:
                st.write("No items selected under current constraints.")
        st.markdown("**Snacks**")
        snacks = result.get("snacks_recommendation", [])
        if snacks:
            st.dataframe(snacks, use_container_width=True)
        else:
            st.write("No snack selected.")

    st.subheader("Calorie breakdown by meal")
    _by_meal = [
        {"meal": m, "target_cal": v.get("target_cal", 0), "actual_cal": v.get("actual_cal", 0)}
        for m, v in result["calorie_breakdown"]["by_meal"].items()
    ]
    st.dataframe(pd.DataFrame(_by_meal), use_container_width=True)

    st.subheader("Weekly Diet Plan (names)")
    _rows = []
    for _day, _meals in result["weekly_diet_plan"].items():
        _rows.append({
            "day": _day,
            "breakfast": ", ".join(_meals.get("breakfast", [])),
            "lunch": ", ".join(_meals.get("lunch", [])),
            "dinner": ", ".join(_meals.get("dinner", [])),
            "snacks": ", ".join(_meals.get("snacks", [])),
        })
    st.dataframe(pd.DataFrame(_rows), use_container_width=True)

    st.subheader("Preparation & Lifestyle Tips")
    st.markdown("**Preparation tips**")
    st.dataframe(pd.DataFrame({"tip": result["preparation_tips"]}), use_container_width=True)
    st.markdown("**Hydration & lifestyle tips**")
    st.dataframe(pd.DataFrame({"tip": result["hydration_and_lifestyle_tips"]}), use_container_width=True)

    st.subheader("Rule Explanations")
    st.dataframe(pd.DataFrame({"explanation": result["explanations"]}), use_container_width=True)

    st.download_button(
        label="Download recommendations (JSON)",
        data=json.dumps(result, indent=2),
        file_name="diet_recommendations.json",
        mime="application/json",
    )
