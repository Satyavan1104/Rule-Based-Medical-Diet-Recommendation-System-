from __future__ import annotations
from typing import Any, Dict, List

from app.data.foods import get_foods
from app.data.schema import UserProfile
from app.rules.engine import build_constraints, filter_foods, explain_rules
from app.services.calculators import estimate_daily_calories, compute_macros, estimate_water_salt_sugar
from app.services.planner import assemble_day_plan, generate_weekly_plan


def _foods_to_include(filtered_names: List[str]) -> List[str]:
    # Return top-N filtered items for a compact include list
    return filtered_names[:12]


def _foods_to_avoid(profile: UserProfile) -> List[str]:
    # Heuristic avoid list combining common avoid tags/names/allergens
    cset = {c.lower() for c in profile.medical.conditions}
    avoids: List[str] = []
    if "diabetes" in cset or profile.special.low_gi:
        avoids += ["refined sugar", "sweetened beverages", "white bread", "refined flour", "desserts"]
    if "hypertension" in cset or profile.special.low_sodium:
        avoids += ["pickles", "papad", "salted snacks", "processed meats", "instant noodles"]
    if "heart disease" in cset:
        avoids += ["fried foods", "trans fat", "butter-heavy dishes"]
    if "kidney disease" in cset or profile.special.renal:
        avoids += ["banana", "coconut water", "tomato puree", "colas"]
    if "gastric" in cset or "gastric issues" in cset:
        avoids += ["very spicy curries", "deep-fried snacks", "carbonated drinks"]
    if profile.special.gluten_free:
        avoids += ["wheat roti", "atta", "barley"]
    if profile.special.lactose_free:
        avoids += ["milk", "paneer", "yogurt"]
    # Deduplicate while preserving order
    seen = set()
    out = []
    for x in avoids:
        key = x.lower()
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


def _prep_tips(profile: UserProfile) -> List[str]:
    tips = [
        "Prefer steaming, grilling, baking, sautéing with minimal oil.",
        "Use herbs, lemon, and spices for flavor; avoid heavy sauces.",
        "Portion control: use smaller plates and measure grains.",
    ]
    if "hypertension" in {c.lower() for c in profile.medical.conditions} or profile.special.low_sodium:
        tips.append("Cook without added salt; add salt at table only if necessary and minimal.")
    if "diabetes" in {c.lower() for c in profile.medical.conditions} or profile.special.low_gi:
        tips.append("Choose whole grains and pair carbs with protein/fiber to lower glycemic impact.")
    if profile.special.renal:
        tips.append("Leach vegetables where appropriate and mind portion sizes for potassium management.")
    return tips


def _lifestyle_tips(profile: UserProfile, water_l: float) -> List[str]:
    tips = [f"Hydration: target ~{water_l} L/day spread evenly (more around activity)."]
    if profile.lifestyle.sleep_hours < 7:
        tips.append("Aim for 7–8 hours of sleep for metabolic health.")
    if profile.lifestyle.activity_level in {"sedentary", "light"}:
        tips.append("Add 30–45 minutes of brisk activity on most days.")
    if profile.lifestyle.stress_level == "high":
        tips.append("Incorporate 10–15 minutes of relaxation (breathing, meditation) daily.")
    return tips


def recommend(profile: UserProfile) -> Dict[str, Any]:
    # Compute targets
    calories = estimate_daily_calories(profile)
    macros = compute_macros(profile, calories)
    water_salt_sugar = estimate_water_salt_sugar(profile, calories)

    # Rules -> constraints
    constraints, rule_notes = build_constraints(profile)

    # Meal plan
    sodium_limit = int(water_salt_sugar["sodium_mg_limit"])
    day_plan, planner_notes = assemble_day_plan(profile, calories, sodium_limit)
    weekly = generate_weekly_plan(day_plan)

    # Foods include/avoid
    catalog = get_foods()
    filtered = filter_foods(catalog, profile, constraints)
    include_list = _foods_to_include([f.name for f in filtered])
    avoid_list = _foods_to_avoid(profile)

    # Explanations
    rule_explanations = explain_rules(rule_notes, constraints)

    # Calorie breakdown by meal (target vs actual)
    breakdown = {
        m: {
            "target_cal": int(round(day_plan.meal_split[m] * calories)),
            "actual_cal": sum(i.calories for i in day_plan.meals.get(m, [])),
        }
        for m in day_plan.meal_split
    }

    # Assemble response
    result: Dict[str, Any] = {
        "personalized_meal_plan": {
            "breakfast": [i.__dict__ for i in day_plan.meals.get("breakfast", [])],
            "lunch": [i.__dict__ for i in day_plan.meals.get("lunch", [])],
            "dinner": [i.__dict__ for i in day_plan.meals.get("dinner", [])],
        },
        "snacks_recommendation": [i.__dict__ for i in day_plan.meals.get("snacks", [])],
        "foods_to_include": include_list,
        "foods_to_avoid": avoid_list,
        "calorie_breakdown": {
            "daily_calories": calories,
            "macros": macros,
            "by_meal": breakdown,
            "totals": day_plan.totals,
        },
        "weekly_diet_plan": {d: {m: [i.name for i in ml] for m, ml in meals.items()} for d, meals in weekly.items()},
        "hydration_and_lifestyle_tips": _lifestyle_tips(profile, water_salt_sugar["water_liters"]),
        "preparation_tips": _prep_tips(profile),
        "nutrition_targets": water_salt_sugar,
        "explanations": rule_explanations + planner_notes,
        "constraints_summary": {
            "required_tags": sorted(list(constraints.required_tags)),
            "prefer_tags": sorted(list(constraints.prefer_tags)),
            "avoid_tags": sorted(list(constraints.avoid_tags)),
            "exclude_allergens": sorted(list(constraints.exclude_allergens)),
            "diet_types_allowed": sorted(list(constraints.diet_types_allowed)),
            "cuisine_preferences": constraints.cuisine_preferences,
            "max_sodium_mg": constraints.max_sodium_mg,
        },
    }

    return result
