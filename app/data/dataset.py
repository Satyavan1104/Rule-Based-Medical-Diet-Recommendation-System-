from __future__ import annotations
from typing import Dict, List, Optional
import pandas as pd

from .schema import from_dict, UserProfile

# Flat CSV schema for batch user profiles
CSV_COLUMNS: List[str] = [
    # Personal
    "age", "gender", "height_cm", "weight_kg", "bmi", "body_type",
    # Medical
    "conditions", "allergies", "medications", "blood_sugar_mgdl",
    "bp_sys", "bp_dia", "cholesterol_mgdl", "hemoglobin_gdl",
    # Dietary
    "diet_type", "likes", "dislikes", "preferred_cuisine", "meal_frequency", "snacking_preference",
    # Lifestyle
    "activity_level", "exercise_routine", "sleep_hours", "stress_level",
    # Nutrition overrides
    "daily_calories", "protein_g", "carbs_g", "fats_g", "salt_limit_g", "sugar_limit_g", "water_liters",
    # Specials (boolean flags)
    "low_gi", "low_sodium", "high_fiber", "renal", "high_protein", "anti_inflammatory", "weight_gain", "weight_loss", "gluten_free", "lactose_free",
]


def _split_list(cell: Optional[str]) -> List[str]:
    if not isinstance(cell, str) or not cell.strip():
        return []
    return [x.strip() for x in cell.split(",") if x.strip()]


def _to_bool(val) -> bool:
    import pandas as pd
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    s = str(val).strip().lower()
    if s in {"1", "true", "yes", "y", "t"}:
        return True
    if s in {"0", "false", "no", "n", "f", ""}:
        return False
    try:
        return bool(int(s))
    except Exception:
        return bool(val)


def load_users_csv(path: str) -> List[UserProfile]:
    """Load user profiles from a CSV with columns above."""
    df = pd.read_csv(path)
    profiles: List[UserProfile] = []
    for _, r in df.iterrows():
        data = {
            "personal": {
                "age": int(r.get("age", 0) or 0),
                "gender": str(r.get("gender", "other")),
                "height": float(r.get("height_cm", 0) or 0),
                "weight": float(r.get("weight_kg", 0) or 0),
                "bmi": float(r.get("bmi")) if pd.notna(r.get("bmi")) else None,
                "body_type": str(r.get("body_type")) if pd.notna(r.get("body_type")) else None,
            },
            "medical": {
                "conditions": _split_list(r.get("conditions")),
                "allergies": _split_list(r.get("allergies")),
                "medications": _split_list(r.get("medications")),
                "blood_sugar_mgdl": float(r.get("blood_sugar_mgdl")) if pd.notna(r.get("blood_sugar_mgdl")) else None,
                "blood_pressure": [
                    int(r.get("bp_sys")) if pd.notna(r.get("bp_sys")) else None,
                    int(r.get("bp_dia")) if pd.notna(r.get("bp_dia")) else None,
                ] if pd.notna(r.get("bp_sys")) and pd.notna(r.get("bp_dia")) else None,
                "cholesterol_mgdl": float(r.get("cholesterol_mgdl")) if pd.notna(r.get("cholesterol_mgdl")) else None,
                "hemoglobin_gdl": float(r.get("hemoglobin_gdl")) if pd.notna(r.get("hemoglobin_gdl")) else None,
            },
            "dietary": {
                "diet_type": str(r.get("diet_type", "veg")),
                "likes": _split_list(r.get("likes")),
                "dislikes": _split_list(r.get("dislikes")),
                "preferred_cuisine": _split_list(r.get("preferred_cuisine")),
                "meal_frequency": int(r.get("meal_frequency", 3) or 3),
                "snacking_preference": str(r.get("snacking_preference", "moderate")),
            },
            "lifestyle": {
                "activity_level": str(r.get("activity_level", "sedentary")),
                "exercise_routine": str(r.get("exercise_routine", "none")),
                "sleep_hours": float(r.get("sleep_hours", 7.0) or 7.0),
                "stress_level": str(r.get("stress_level", "moderate")),
            },
            "nutrition": {
                "daily_calories": int(r.get("daily_calories")) if pd.notna(r.get("daily_calories")) else None,
                "protein_g": float(r.get("protein_g")) if pd.notna(r.get("protein_g")) else None,
                "carbs_g": float(r.get("carbs_g")) if pd.notna(r.get("carbs_g")) else None,
                "fats_g": float(r.get("fats_g")) if pd.notna(r.get("fats_g")) else None,
                "salt_limit_g": float(r.get("salt_limit_g")) if pd.notna(r.get("salt_limit_g")) else None,
                "sugar_limit_g": float(r.get("sugar_limit_g")) if pd.notna(r.get("sugar_limit_g")) else None,
                "water_liters": float(r.get("water_liters")) if pd.notna(r.get("water_liters")) else None,
            },
            "special": {
                "low_gi": _to_bool(r.get("low_gi")),
                "low_sodium": _to_bool(r.get("low_sodium")),
                "high_fiber": _to_bool(r.get("high_fiber")),
                "renal": _to_bool(r.get("renal")),
                "high_protein": _to_bool(r.get("high_protein")),
                "anti_inflammatory": _to_bool(r.get("anti_inflammatory")),
                "weight_gain": _to_bool(r.get("weight_gain")),
                "weight_loss": _to_bool(r.get("weight_loss")),
                "gluten_free": _to_bool(r.get("gluten_free")),
                "lactose_free": _to_bool(r.get("lactose_free")),
            },
        }
        profiles.append(from_dict(data))
    return profiles


def write_csv_template(path: str) -> None:
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
