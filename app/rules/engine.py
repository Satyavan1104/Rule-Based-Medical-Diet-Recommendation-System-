from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from app.data.foods import FoodItem
from app.data.schema import UserProfile


@dataclass
class ConstraintSpec:
    required_tags: Set[str]
    prefer_tags: Set[str]
    avoid_tags: Set[str]
    avoid_names: Set[str]
    exclude_allergens: Set[str]
    diet_types_allowed: Set[str]
    cuisine_preferences: List[str]
    max_sodium_mg: Optional[int]


def _contains_any(text: str, needles: Set[str]) -> bool:
    t = text.lower()
    return any(n in t for n in needles)


def build_constraints(profile: UserProfile) -> Tuple[ConstraintSpec, List[str]]:
    """
    Translate medical conditions, allergies, preferences, and special rules into
    concrete constraints the planner can use. Returns (constraints, explanations).

    High-level rule principles:
    - Diabetes: prefer low GI, high fiber; avoid refined sugar/refined carbs.
    - Hypertension: prefer low sodium; avoid high-sodium/processed foods.
    - Heart disease / high cholesterol: prefer omega-3, anti-inflammatory, low saturated fat; avoid fried/processed.
    - Kidney disease (renal): prefer low potassium/phosphorus, moderate protein; avoid high-potassium foods (e.g., banana, some legumes).
    - PCOD/PCOS: low GI + anti-inflammatory + higher fiber and lean protein.
    - Gastric issues: avoid spicy/fried; prefer gentle fiber and cooked veg.
    - Thyroid: be cautious with soy-heavy items close to medication time (conservative limit here).
    - Special toggles extend/override (low_gi, low_sodium, high_fiber, etc.).
    """
    conditions = {c.lower() for c in profile.medical.conditions}

    required: Set[str] = set()
    prefer: Set[str] = set()
    avoid: Set[str] = {"fried", "processed", "refined_sugar", "refined_carbs"}
    avoid_names: Set[str] = set()
    allergens: Set[str] = {a.lower() for a in profile.medical.allergies}
    cuisines = [c.lower() for c in profile.dietary.preferred_cuisine]
    diet_allowed = {profile.dietary.diet_type}
    sodium_limit: Optional[int] = None

    explanations: List[str] = []

    # Diseases
    if "diabetes" in conditions:
        required.add("low_gi")
        prefer.update({"high_fiber"})
        avoid.update({"high_gi", "refined_sugar", "refined_carbs"})
        explanations.append("Applied diabetes rules: prefer low GI, high fiber; avoid refined sugar/carbs.")

    if "hypertension" in conditions or profile.special.low_sodium:
        prefer.add("low_sodium")
        avoid.add("high_sodium")
        sodium_limit = 1500 if sodium_limit is None else min(sodium_limit, 1500)
        explanations.append("Applied hypertension/low sodium rules: limit sodium ~1500 mg/day, avoid high-sodium foods.")

    if "heart disease" in conditions or (profile.medical.cholesterol_mgdl and profile.medical.cholesterol_mgdl >= 200):
        prefer.update({"omega3", "anti_inflammatory", "low_saturated_fat"})
        avoid.update({"high_saturated_fat", "fried", "processed"})
        explanations.append("Applied heart/cholesterol rules: prefer omega-3 and anti-inflammatory; avoid fried/processed/high saturated fat.")

    if "kidney disease" in conditions or profile.special.renal:
        prefer.update({"low_potassium", "low_phosphorus"})
        avoid.update({"high_potassium", "high_phosphorus"})
        # Conservative: avoid banana and certain legumes in our small catalog
        avoid_names.update({"banana", "rajma"})
        explanations.append("Applied renal rules: limit potassium/phosphorus; avoid banana/rajma in this catalog.")

    if "pcod" in conditions or "pcos" in conditions:
        required.add("low_gi")
        prefer.update({"anti_inflammatory", "high_fiber", "lean_protein"})
        avoid.update({"refined_sugar", "refined_carbs", "fried"})
        explanations.append("Applied PCOD/PCOS rules: low GI, anti-inflammatory, high fiber, lean protein.")

    if "gastric" in conditions or "gastric issues" in conditions:
        avoid.update({"spicy", "fried"})
        prefer.update({"high_fiber"})
        explanations.append("Applied gastric rules: avoid spicy/fried; emphasize gentle fiber and cooked veg.")

    if "thyroid" in conditions:
        # Conservative handling: limit soy-heavy items
        avoid_names.update({"tofu"})
        explanations.append("Applied thyroid caution: limited soy-heavy items (e.g., tofu).")

    # Special toggles
    if profile.special.low_gi:
        required.add("low_gi")
        explanations.append("Special: Low GI enabled.")
    if profile.special.high_fiber:
        prefer.add("high_fiber")
        explanations.append("Special: High fiber enabled.")
    if profile.special.high_protein:
        prefer.add("lean_protein")
        explanations.append("Special: High protein enabled.")
    if profile.special.anti_inflammatory:
        prefer.add("anti_inflammatory")
        explanations.append("Special: Anti-inflammatory enabled.")
    if profile.special.gluten_free:
        allergens.add("gluten")
        explanations.append("Special: Gluten-free enabled.")
    if profile.special.lactose_free:
        allergens.add("lactose")
        explanations.append("Special: Lactose-free enabled.")

    # General dislikes and allergies are enforced downstream in the filter.

    c = ConstraintSpec(
        required_tags=required,
        prefer_tags=prefer,
        avoid_tags=avoid,
        avoid_names=avoid_names,
        exclude_allergens=allergens,
        diet_types_allowed=diet_allowed,
        cuisine_preferences=cuisines,
        max_sodium_mg=sodium_limit,
    )
    return c, explanations


def filter_foods(foods: List[FoodItem], profile: UserProfile, constraints: ConstraintSpec) -> List[FoodItem]:
    dislikes = {d.lower() for d in profile.dietary.dislikes}
    likes = {d.lower() for d in profile.dietary.likes}

    def allowed(food: FoodItem) -> bool:
        # Diet type gate
        if profile.dietary.diet_type not in food.diet_types:
            return False
        # Allergens
        if any(a in constraints.exclude_allergens for a in food.allergens):
            return False
        # Avoid names
        if _contains_any(food.name, constraints.avoid_names):
            return False
        # Avoid tags
        if any(tag in constraints.avoid_tags for tag in food.tags):
            return False
        # Avoid high GI via GI attribute if requested
        if "high_gi" in constraints.avoid_tags and getattr(food, "gi", "").lower() == "high":
            return False
        # Required tags
        if constraints.required_tags:
            req = set(constraints.required_tags)
            # Treat 'low_gi' specially: accept if GI attribute is low OR tag present
            if "low_gi" in req:
                low_gi_ok = getattr(food, "gi", "").lower() == "low" or any(t == "low_gi" for t in food.tags)
                if not low_gi_ok:
                    return False
                req.discard("low_gi")
            if req and not any(tag in req for tag in food.tags):
                return False
        # Dislikes by substring
        if any(sub in food.name.lower() for sub in dislikes):
            return False
        return True

    filtered = [f for f in foods if allowed(f)]

    # Soft preference by cuisine and prefer_tags: stable sort with keys
    def score(food: FoodItem) -> int:
        s = 0
        if constraints.cuisine_preferences and any(c in food.cuisines for c in constraints.cuisine_preferences):
            s += 2
        if any(tag in constraints.prefer_tags for tag in food.tags):
            s += 1
        if any(like in food.name.lower() for like in likes):
            s += 1
        return -s  # for ascending sort, negative score sorts higher

    filtered.sort(key=score)
    return filtered


def explain_rules(explanations: List[str], constraints: ConstraintSpec) -> List[str]:
    notes = list(explanations)
    if constraints.max_sodium_mg is not None:
        notes.append(f"Sodium target set to ~{constraints.max_sodium_mg} mg/day.")
    if constraints.required_tags:
        notes.append("Required tags: " + ", ".join(sorted(constraints.required_tags)))
    if constraints.prefer_tags:
        notes.append("Preferred tags: " + ", ".join(sorted(constraints.prefer_tags)))
    if constraints.exclude_allergens:
        notes.append("Allergen filters: " + ", ".join(sorted(constraints.exclude_allergens)))
    return notes
