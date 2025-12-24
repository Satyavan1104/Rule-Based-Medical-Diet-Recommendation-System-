from __future__ import annotations
from typing import Dict, Tuple

from app.config import ACTIVITY_FACTORS, STRESS_MULTIPLIER
from app.data.schema import UserProfile


def _activity_factor(level: str) -> float:
    level = (level or "sedentary").strip().lower()
    return ACTIVITY_FACTORS.get(level, ACTIVITY_FACTORS["sedentary"])


def _stress_factor(level: str) -> float:
    level = (level or "moderate").strip().lower()
    return STRESS_MULTIPLIER.get(level, STRESS_MULTIPLIER["moderate"])


def _bmr_mifflin_st_jeor(profile: UserProfile) -> float:
    w = profile.personal.weight_kg
    h = profile.personal.height_cm
    a = profile.personal.age
    g = profile.personal.gender
    base = 10 * w + 6.25 * h - 5 * a
    if g == "male":
        return base + 5
    if g == "female":
        return base - 161
    # For 'other', use midpoint between male and female constants
    return base - 78


def estimate_daily_calories(profile: UserProfile) -> int:
    """
    Estimate daily calories (TDEE).
    - Use user's provided requirement if present.
    - Otherwise, BMR (Mifflin-St Jeor) * activity * stress factor.
    - Apply goal modifiers for weight loss/gain if toggled.
    """
    if profile.nutrition.daily_calories:
        return int(profile.nutrition.daily_calories)

    bmr = _bmr_mifflin_st_jeor(profile)
    tdee = bmr * _activity_factor(profile.lifestyle.activity_level)
    tdee *= _stress_factor(profile.lifestyle.stress_level)

    # Goal adjustments
    if profile.special.weight_loss and not profile.special.weight_gain:
        tdee *= 0.85  # ~15% deficit
    elif profile.special.weight_gain and not profile.special.weight_loss:
        tdee *= 1.15  # ~15% surplus

    return int(round(tdee))


def compute_macros(profile: UserProfile, calories: int) -> Dict[str, float]:
    """
    Compute macro targets in grams given total calories and health context.
    Baseline ratios:
    - default: P/C/F = 20% / 50% / 30%
    Adjustments:
    - diabetes/low GI: 25/45/30
    - high protein: 30/40/30
    - weight loss: prioritize protein ~30%
    - renal: moderate protein ~15-18%
    - heart disease/high cholesterol: reduce saturated fat; keep fats ~25-30%
    If user-provided macros exist, respect them.
    """
    if profile.nutrition.protein_g and profile.nutrition.carbs_g and profile.nutrition.fats_g:
        return {
            "protein_g": float(profile.nutrition.protein_g),
            "carbs_g": float(profile.nutrition.carbs_g),
            "fats_g": float(profile.nutrition.fats_g),
        }

    # Start with default ratios
    p_pct, c_pct, f_pct = 0.20, 0.50, 0.30

    conditions = {c.lower() for c in profile.medical.conditions}

    if "diabetes" in conditions or profile.special.low_gi:
        p_pct, c_pct, f_pct = 0.25, 0.45, 0.30

    if profile.special.high_protein:
        p_pct, c_pct, f_pct = 0.30, 0.40, 0.30

    if profile.special.weight_loss:
        p_pct = max(p_pct, 0.30)  # keep protein higher for satiety
        c_pct = min(c_pct, 0.45)
        f_pct = 1.0 - p_pct - c_pct

    if "kidney disease" in conditions or profile.special.renal:
        p_pct = min(p_pct, 0.18)  # moderate protein
        c_pct = max(c_pct, 0.47)
        f_pct = 1.0 - p_pct - c_pct

    if "heart disease" in conditions or (profile.medical.cholesterol_mgdl and profile.medical.cholesterol_mgdl >= 200):
        f_pct = min(f_pct, 0.30)
        c_pct = min(c_pct, 0.50)
        p_pct = 1.0 - f_pct - c_pct

    # Convert to grams (4 kcal/g for protein & carbs; 9 kcal/g for fats)
    protein_g = (calories * p_pct) / 4.0
    carbs_g = (calories * c_pct) / 4.0
    fats_g = (calories * f_pct) / 9.0

    return {
        "protein_g": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "fats_g": round(fats_g, 1),
    }


def estimate_water_salt_sugar(profile: UserProfile, calories: int) -> Dict[str, float]:
    """
    Estimate hydration need, salt and sugar limits.
    - Water: ~30 ml/kg baseline + 0.5 L if active; cap 2.0–4.0 L for safety.
    - Sodium: 1500 mg/day for hypertension/low sodium; else 2000 mg default.
    - Free sugar: ~25 g/day for diabetes/weight loss; else ~30–36 g.
    If user provided values, respect them.
    """
    # Water
    if profile.nutrition.water_liters is not None:
        water_l = float(profile.nutrition.water_liters)
    else:
        base = 0.03 * profile.personal.weight_kg  # 30 ml/kg
        active_bonus = 0.5 if _activity_factor(profile.lifestyle.activity_level) >= 1.55 else 0.0
        water_l = max(2.0, min(4.0, base + active_bonus))

    # Sodium and Sugar
    if profile.nutrition.salt_limit_g is not None:
        # Convert salt (NaCl) grams to approx sodium mg (40% sodium by mass)
        sodium_mg_limit = float(profile.nutrition.salt_limit_g) * 1000 * 0.4
    else:
        if "hypertension" in {c.lower() for c in profile.medical.conditions} or profile.special.low_sodium:
            sodium_mg_limit = 1500.0
        else:
            sodium_mg_limit = 2000.0

    if profile.nutrition.sugar_limit_g is not None:
        sugar_g_limit = float(profile.nutrition.sugar_limit_g)
    else:
        if "diabetes" in {c.lower() for c in profile.medical.conditions} or profile.special.weight_loss:
            sugar_g_limit = 25.0
        else:
            # Use sex-based differentiation lightly; otherwise 30 g default
            sugar_g_limit = 36.0 if profile.personal.gender == "male" else 30.0

    return {
        "water_liters": round(water_l, 2),
        "sodium_mg_limit": round(sodium_mg_limit),
        "sugar_g_limit": round(sugar_g_limit),
    }
