from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from app.config import DEFAULT_MEAL_SPLIT
from app.data.foods import FoodItem, get_foods
from app.data.schema import UserProfile
from app.rules.engine import build_constraints, filter_foods
from app.utils.helpers import round_nearest


@dataclass
class MealItem:
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float
    sodium_mg: int


@dataclass
class DayPlan:
    meals: Dict[str, List[MealItem]]  # breakfast/lunch/dinner/snacks
    totals: Dict[str, float]  # calories, protein_g, carbs_g, fats_g, fiber_g, sodium_mg
    meal_split: Dict[str, float]


def _to_item(f: FoodItem) -> MealItem:
    return MealItem(
        name=f.name,
        calories=f.calories,
        protein_g=f.protein_g,
        carbs_g=f.carbs_g,
        fats_g=f.fat_g,
        fiber_g=f.fiber_g,
        sodium_mg=f.sodium_mg,
    )


def _pick_items_for_meal(cands: List[FoodItem], target_cal: int, sodium_budget: int) -> List[MealItem]:
    # Greedy pick: choose best single item near target, optionally add a light add-on
    if not cands:
        return []

    def cal_diff(food: FoodItem) -> int:
        return abs(food.calories - target_cal)

    cands_sorted = sorted(cands, key=lambda f: (cal_diff(f), f.sodium_mg))
    picked: List[MealItem] = []

    # First choice
    for f in cands_sorted:
        if f.sodium_mg <= sodium_budget:
            picked.append(_to_item(f))
            sodium_budget -= f.sodium_mg
            break

    if not picked:
        return []

    # Optional add-on: if below 60% of target, try add a small item
    current_cal = sum(i.calories for i in picked)
    if current_cal < 0.6 * target_cal:
        for f in cands_sorted:
            if f.calories <= target_cal - current_cal and f.sodium_mg <= sodium_budget and f.name != picked[0].name:
                picked.append(_to_item(f))
                break

    return picked


def _compute_meal_split(profile: UserProfile) -> Dict[str, float]:
    """Return {breakfast,lunch,dinner,snacks} that sum to 1.0 based on frequency and snacking preference."""
    freq = max(3, min(6, int(profile.dietary.meal_frequency or 3)))
    snack_pref = (profile.dietary.snacking_preference or "moderate").lower()
    # Base split for 3 meals
    split = dict(DEFAULT_MEAL_SPLIT)
    # Adjust snacks share by preference
    snack_base = {"low": 0.07, "moderate": 0.10, "high": 0.15}.get(snack_pref, 0.10)
    # Adjust for frequency > 3 by increasing snack share and reducing lunch/dinner
    if freq >= 4:
        extra = 0.03 * (freq - 3)  # +3% per extra meal
        snack_share = min(0.20, snack_base + extra)
        # Distribute reduction proportionally from lunch/dinner
        reduce = snack_share - split["snacks"]
        lunch_dinner_total = split["lunch"] + split["dinner"]
        split["snacks"] = snack_share
        split["lunch"] -= reduce * (split["lunch"] / lunch_dinner_total)
        split["dinner"] -= reduce * (split["dinner"] / lunch_dinner_total)
        # Keep breakfast as is
    else:
        # Only adjust snack share per preference (for freq=3)
        delta = snack_base - split["snacks"]
        if abs(delta) > 1e-6:
            # take from lunch proportionally
            split["snacks"] = snack_base
            split["lunch"] -= delta
    # Normalize minor drift
    total = sum(split.values())
    for k in split:
        split[k] = round(split[k] / total, 4)
    return split


def assemble_day_plan(profile: UserProfile, calories: int, sodium_limit: int) -> Tuple[DayPlan, List[str]]:
    """
    Build a pragmatic daily plan: choose 1-2 items per main meal and 1-2 snacks.
    Sodium is apportioned by meal split for simplicity.
    Returns (DayPlan, planner_notes)
    """
    constraints, _ = build_constraints(profile)

    all_foods = get_foods()
    filtered = filter_foods(all_foods, profile, constraints)

    split = _compute_meal_split(profile)
    sodium_by_meal = {m: int(sodium_limit * split[m]) for m in split}

    planner_notes: List[str] = []

    def candidates(meal: str) -> List[FoodItem]:
        return [f for f in filtered if meal in f.meal_types]

    meals: Dict[str, List[MealItem]] = {m: [] for m in split}

    for meal in ["breakfast", "lunch", "dinner"]:
        target_cal = int(round(split[meal] * calories))
        picks = _pick_items_for_meal(candidates(meal), target_cal, sodium_by_meal[meal])
        meals[meal] = picks
        if not picks:
            planner_notes.append(f"No candidates found for {meal} meeting constraints; consider relaxing dislikes or cuisines.")

    # Snacks: aim for 1 light snack
    snack_cands = candidates("snacks") or candidates("snack")
    if snack_cands:
        target_cal = int(round(split["snacks"] * calories))
        picks = _pick_items_for_meal(snack_cands, target_cal, sodium_by_meal["snacks"])
        meals["snacks"] = picks
    else:
        meals["snacks"] = []
        planner_notes.append("No snack candidates available under current constraints.")

    # Totals
    def agg(meal_items: List[MealItem]) -> Dict[str, float]:
        tot = {
            "calories": 0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fats_g": 0.0,
            "fiber_g": 0.0,
            "sodium_mg": 0,
        }
        for i in meal_items:
            tot["calories"] += i.calories
            tot["protein_g"] += i.protein_g
            tot["carbs_g"] += i.carbs_g
            tot["fats_g"] += i.fats_g
            tot["fiber_g"] += i.fiber_g
            tot["sodium_mg"] += i.sodium_mg
        return tot

    totals = {"calories": 0, "protein_g": 0.0, "carbs_g": 0.0, "fats_g": 0.0, "fiber_g": 0.0, "sodium_mg": 0}
    for m, items in meals.items():
        mtot = agg(items)
        for k, v in mtot.items():
            totals[k] += v

    # Rounding for display neatness
    for k in ["protein_g", "carbs_g", "fats_g", "fiber_g"]:
        totals[k] = round_nearest(totals[k], 0.1)

    plan = DayPlan(meals=meals, totals=totals, meal_split=split)
    return plan, planner_notes


def generate_weekly_plan(day_plan: DayPlan) -> Dict[str, Dict[str, List[MealItem]]]:
    """
    Create a simple weekly rotation from a single day plan.
    We rotate meal selections for variety if multiple items exist per meal.
    """
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly: Dict[str, Dict[str, List[MealItem]]] = {}
    for idx, day in enumerate(week_days):
        day_meals: Dict[str, List[MealItem]] = {}
        for meal, items in day_plan.meals.items():
            if not items:
                day_meals[meal] = []
                continue
            # rotate by day index
            rot = idx % len(items)
            day_meals[meal] = [items[rot]]
        weekly[day] = day_meals
    return weekly
