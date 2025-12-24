from __future__ import annotations
from dataclasses import dataclass
from typing import List
from pathlib import Path
import json


@dataclass(frozen=True)
class FoodItem:
    """
    A minimal, curated food catalog item with nutrition per typical serving.

    Notes:
    - tags: semantic labels used by the rule engine and planner
      Examples: low_gi, high_gi, high_fiber, lean_protein, whole_grain, low_sodium,
      high_sodium, processed, fried, spicy, anti_inflammatory, omega3, iron_rich,
      gluten_free, lactose_free, high_saturated_fat, low_saturated_fat,
      high_potassium, low_potassium, high_phosphorus, refined_sugar, refined_carbs
    - diet_types: ["veg" | "vegan" | "non-veg"] supported diet categories
    - meal_types: ["breakfast", "lunch", "dinner", "snack"] recommended use
    - cuisines: high-level cuisine labels used to better match preferences
    """

    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: int
    gi: str  # "low" | "medium" | "high"
    tags: List[str]
    diet_types: List[str]
    meal_types: List[str]
    cuisines: List[str]
    allergens: List[str]


def _load_catalog_json() -> List[FoodItem]:
    """Try to load foods_catalog.json from the same directory. Return [] on failure."""
    try:
        here = Path(__file__).resolve().parent
        catalog_path = here / "foods_catalog.json"
        if not catalog_path.exists():
            return []
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        items: List[FoodItem] = []
        for d in data:
            items.append(
                FoodItem(
                    name=d["name"],
                    calories=int(d["calories"]),
                    protein_g=float(d["protein_g"]),
                    carbs_g=float(d["carbs_g"]),
                    fat_g=float(d["fat_g"]),
                    fiber_g=float(d.get("fiber_g", 0)),
                    sodium_mg=int(d.get("sodium_mg", 0)),
                    gi=(d.get("gi") or "").lower(),
                    tags=[str(t).lower() for t in d.get("tags", [])],
                    diet_types=[str(t).lower() for t in d.get("diet_types", [])],
                    meal_types=[str(t).lower() for t in d.get("meal_types", [])],
                    cuisines=[str(t).lower() for t in d.get("cuisines", [])],
                    allergens=[str(t).lower() for t in d.get("allergens", [])],
                )
            )
        return items
    except Exception:
        return []


def get_foods() -> List[FoodItem]:
    # Try external catalog first
    from_catalog = _load_catalog_json()
    if from_catalog:
        return from_catalog
    # Fallback: Core grains and alternatives
    foods: List[FoodItem] = [
        FoodItem(
            name="Oats porridge (water)", calories=180, protein_g=6, carbs_g=30, fat_g=3,
            fiber_g=5, sodium_mg=120, gi="low",
            tags=["low_gi", "high_fiber", "whole_grain", "low_sodium"],
            diet_types=["veg", "vegan"], meal_types=["breakfast"], cuisines=["global"],
            allergens=["may_contain_gluten"],
        ),
        FoodItem(
            name="Whole wheat roti (2)", calories=200, protein_g=6, carbs_g=40, fat_g=2,
            fiber_g=6, sodium_mg=200, gi="medium",
            tags=["whole_grain", "high_fiber"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["indian"],
            allergens=["gluten"],
        ),
        FoodItem(
            name="Brown rice (1 cup)", calories=215, protein_g=5, carbs_g=45, fat_g=2,
            fiber_g=3.5, sodium_mg=10, gi="medium",
            tags=["whole_grain", "moderate_gi", "low_sodium"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["indian", "asian"],
            allergens=[],
        ),
        FoodItem(
            name="Quinoa (1 cup)", calories=222, protein_g=8, carbs_g=39, fat_g=4,
            fiber_g=5, sodium_mg=13, gi="low",
            tags=["gluten_free", "low_gi", "high_fiber", "whole_grain", "low_sodium"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Millet roti (2)", calories=210, protein_g=6, carbs_g=40, fat_g=3,
            fiber_g=5, sodium_mg=120, gi="low",
            tags=["gluten_free", "low_gi", "high_fiber"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["indian"],
            allergens=[],
        ),
        # Proteins
        FoodItem(
            name="Grilled chicken breast (120g)", calories=198, protein_g=36, carbs_g=0, fat_g=5,
            fiber_g=0, sodium_mg=80, gi="low",
            tags=["lean_protein", "low_sodium", "low_saturated_fat"],
            diet_types=["non-veg"], meal_types=["lunch", "dinner"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Baked salmon (120g)", calories=233, protein_g=25, carbs_g=0, fat_g=14,
            fiber_g=0, sodium_mg=75, gi="low",
            tags=["omega3", "anti_inflammatory", "lean_protein", "low_sodium"],
            diet_types=["non-veg"], meal_types=["lunch", "dinner"], cuisines=["global"],
            allergens=["seafood"],
        ),
        FoodItem(
            name="Egg omelette (2 eggs, less oil)", calories=160, protein_g=12, carbs_g=2, fat_g=11,
            fiber_g=0, sodium_mg=150, gi="low",
            tags=["protein", "moderate_saturated_fat"],
            diet_types=["non-veg"], meal_types=["breakfast", "lunch"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Tofu stir-fry (150g)", calories=180, protein_g=18, carbs_g=6, fat_g=9,
            fiber_g=2, sodium_mg=15, gi="low",
            tags=["lean_protein", "low_sodium", "vegan"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["asian"],
            allergens=["soy"],
        ),
        FoodItem(
            name="Paneer bhurji (100g, low oil)", calories=220, protein_g=14, carbs_g=6, fat_g=15,
            fiber_g=1, sodium_mg=200, gi="low",
            tags=["protein"],
            diet_types=["veg"], meal_types=["lunch", "dinner"], cuisines=["indian"],
            allergens=["lactose"],
        ),
        # Legumes
        FoodItem(
            name="Chickpea salad (1 cup)", calories=210, protein_g=11, carbs_g=35, fat_g=3,
            fiber_g=9, sodium_mg=180, gi="low",
            tags=["low_gi", "high_fiber", "plant_protein", "anti_inflammatory"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner", "snack"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Moong dal (1 cup)", calories=210, protein_g=14, carbs_g=36, fat_g=2,
            fiber_g=8, sodium_mg=140, gi="low",
            tags=["low_gi", "high_fiber", "plant_protein"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["indian"],
            allergens=[],
        ),
        FoodItem(
            name="Rajma (kidney beans) curry (1 cup)", calories=240, protein_g=13, carbs_g=40, fat_g=3,
            fiber_g=10, sodium_mg=300, gi="low",
            tags=["low_gi", "high_fiber", "plant_protein", "high_potassium"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["indian"],
            allergens=[],
        ),
        # Vegetables
        FoodItem(
            name="Mixed salad (spinach, cucumber, tomato)", calories=80, protein_g=4, carbs_g=12, fat_g=2,
            fiber_g=5, sodium_mg=100, gi="low",
            tags=["low_gi", "high_fiber", "anti_inflammatory", "low_sodium"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner", "snack"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Steamed broccoli (1 cup)", calories=55, protein_g=4, carbs_g=11, fat_g=0.6,
            fiber_g=5, sodium_mg=50, gi="low",
            tags=["low_gi", "high_fiber", "anti_inflammatory", "low_sodium"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Stir-fried mixed veg (low oil)", calories=120, protein_g=3, carbs_g=18, fat_g=4,
            fiber_g=5, sodium_mg=170, gi="low",
            tags=["low_gi", "high_fiber"],
            diet_types=["veg", "vegan"], meal_types=["lunch", "dinner"], cuisines=["asian"],
            allergens=[],
        ),
        # Fruits
        FoodItem(
            name="Apple (1)", calories=95, protein_g=0.5, carbs_g=25, fat_g=0.3,
            fiber_g=4.5, sodium_mg=2, gi="low",
            tags=["low_gi", "high_fiber", "low_potassium"],
            diet_types=["veg", "vegan"], meal_types=["breakfast", "snack"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Banana (1)", calories=105, protein_g=1.3, carbs_g=27, fat_g=0.4,
            fiber_g=3.1, sodium_mg=1, gi="medium",
            tags=["moderate_gi", "high_potassium"],
            diet_types=["veg", "vegan"], meal_types=["breakfast", "snack"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Mixed berries (1 cup)", calories=65, protein_g=1, carbs_g=16, fat_g=0.5,
            fiber_g=7, sodium_mg=2, gi="low",
            tags=["low_gi", "high_fiber", "anti_inflammatory"],
            diet_types=["veg", "vegan"], meal_types=["breakfast", "snack"], cuisines=["global"],
            allergens=[],
        ),
        # Dairy & alternatives
        FoodItem(
            name="Low-fat yogurt (200g)", calories=140, protein_g=12, carbs_g=12, fat_g=4,
            fiber_g=0, sodium_mg=90, gi="low",
            tags=["probiotic"],
            diet_types=["veg"], meal_types=["breakfast", "snack"], cuisines=["global"],
            allergens=["lactose"],
        ),
        FoodItem(
            name="Unsweetened soy milk (250ml)", calories=90, protein_g=7, carbs_g=4, fat_g=5,
            fiber_g=2, sodium_mg=90, gi="low",
            tags=["vegan"],
            diet_types=["veg", "vegan"], meal_types=["breakfast", "snack"], cuisines=["global"],
            allergens=["soy"],
        ),
        # Snacks
        FoodItem(
            name="Almonds (20g)", calories=116, protein_g=4, carbs_g=4, fat_g=10,
            fiber_g=2.5, sodium_mg=1, gi="low",
            tags=["healthy_fat", "anti_inflammatory"],
            diet_types=["veg", "vegan"], meal_types=["snack"], cuisines=["global"],
            allergens=["nuts"],
        ),
        FoodItem(
            name="Roasted chana (30g)", calories=120, protein_g=6, carbs_g=18, fat_g=2,
            fiber_g=5, sodium_mg=120, gi="low",
            tags=["low_gi", "high_fiber", "plant_protein"],
            diet_types=["veg", "vegan"], meal_types=["snack"], cuisines=["indian"],
            allergens=[],
        ),
        FoodItem(
            name="Hummus with carrot sticks", calories=150, protein_g=5, carbs_g=15, fat_g=8,
            fiber_g=4, sodium_mg=180, gi="low",
            tags=["low_gi", "high_fiber", "plant_protein"],
            diet_types=["veg", "vegan"], meal_types=["snack"], cuisines=["mediterranean"],
            allergens=["sesame"],
        ),
        # Beverages
        FoodItem(
            name="Green tea (unsweetened)", calories=2, protein_g=0, carbs_g=0, fat_g=0,
            fiber_g=0, sodium_mg=0, gi="low",
            tags=["anti_inflammatory"],
            diet_types=["veg", "vegan", "non-veg"], meal_types=["breakfast", "snack", "dinner"], cuisines=["global"],
            allergens=[],
        ),
        FoodItem(
            name="Lemon water (unsweetened)", calories=4, protein_g=0, carbs_g=1, fat_g=0,
            fiber_g=0, sodium_mg=0, gi="low",
            tags=["hydration"],
            diet_types=["veg", "vegan", "non-veg"], meal_types=["breakfast", "snack", "dinner"], cuisines=["global"],
            allergens=[],
        ),
    ]

    return foods
