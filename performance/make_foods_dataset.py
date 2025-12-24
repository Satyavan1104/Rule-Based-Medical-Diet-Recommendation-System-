import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any

SEEDS: List[Dict[str, Any]] = [
    {"name":"Oats porridge (water)","calories":180,"protein_g":6,"carbs_g":30,"fat_g":3,"fiber_g":5,"sodium_mg":120,"gi":"low","tags":["low_gi","high_fiber","whole_grain","low_sodium"],"diet_types":["veg","vegan"],"meal_types":["breakfast"],"cuisines":["global"],"allergens":["may_contain_gluten"]},
    {"name":"Whole wheat roti (2)","calories":200,"protein_g":6,"carbs_g":40,"fat_g":2,"fiber_g":6,"sodium_mg":200,"gi":"medium","tags":["whole_grain","high_fiber"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["indian"],"allergens":["gluten"]},
    {"name":"Brown rice (1 cup)","calories":215,"protein_g":5,"carbs_g":45,"fat_g":2,"fiber_g":3.5,"sodium_mg":10,"gi":"medium","tags":["whole_grain","moderate_gi","low_sodium"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["indian","asian"],"allergens":[]},
    {"name":"Quinoa (1 cup)","calories":222,"protein_g":8,"carbs_g":39,"fat_g":4,"fiber_g":5,"sodium_mg":13,"gi":"low","tags":["gluten_free","low_gi","high_fiber","whole_grain","low_sodium"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["global"],"allergens":[]},
    {"name":"Millet roti (2)","calories":210,"protein_g":6,"carbs_g":40,"fat_g":3,"fiber_g":5,"sodium_mg":120,"gi":"low","tags":["gluten_free","low_gi","high_fiber"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["indian"],"allergens":[]},
    {"name":"Grilled chicken breast (120g)","calories":198,"protein_g":36,"carbs_g":0,"fat_g":5,"fiber_g":0,"sodium_mg":80,"gi":"low","tags":["lean_protein","low_sodium","low_saturated_fat"],"diet_types":["non-veg"],"meal_types":["lunch","dinner"],"cuisines":["global"],"allergens":[]},
    {"name":"Baked salmon (120g)","calories":233,"protein_g":25,"carbs_g":0,"fat_g":14,"fiber_g":0,"sodium_mg":75,"gi":"low","tags":["omega3","anti_inflammatory","lean_protein","low_sodium"],"diet_types":["non-veg"],"meal_types":["lunch","dinner"],"cuisines":["global"],"allergens":["seafood"]},
    {"name":"Egg omelette (2 eggs, less oil)","calories":160,"protein_g":12,"carbs_g":2,"fat_g":11,"fiber_g":0,"sodium_mg":150,"gi":"low","tags":["protein","moderate_saturated_fat"],"diet_types":["non-veg"],"meal_types":["breakfast","lunch"],"cuisines":["global"],"allergens":[]},
    {"name":"Tofu stir-fry (150g)","calories":180,"protein_g":18,"carbs_g":6,"fat_g":9,"fiber_g":2,"sodium_mg":15,"gi":"low","tags":["lean_protein","low_sodium","vegan"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["asian"],"allergens":["soy"]},
    {"name":"Paneer bhurji (100g, low oil)","calories":220,"protein_g":14,"carbs_g":6,"fat_g":15,"fiber_g":1,"sodium_mg":200,"gi":"low","tags":["protein"],"diet_types":["veg"],"meal_types":["lunch","dinner"],"cuisines":["indian"],"allergens":["lactose"]},
    {"name":"Chickpea salad (1 cup)","calories":210,"protein_g":11,"carbs_g":35,"fat_g":3,"fiber_g":9,"sodium_mg":180,"gi":"low","tags":["low_gi","high_fiber","plant_protein","anti_inflammatory"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner","snack"],"cuisines":["global"],"allergens":[]},
    {"name":"Moong dal (1 cup)","calories":210,"protein_g":14,"carbs_g":36,"fat_g":2,"fiber_g":8,"sodium_mg":140,"gi":"low","tags":["low_gi","high_fiber","plant_protein"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["indian"],"allergens":[]},
    {"name":"Rajma (kidney beans) curry (1 cup)","calories":240,"protein_g":13,"carbs_g":40,"fat_g":3,"fiber_g":10,"sodium_mg":300,"gi":"low","tags":["low_gi","high_fiber","plant_protein","high_potassium"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["indian"],"allergens":[]},
    {"name":"Mixed salad (spinach, cucumber, tomato)","calories":80,"protein_g":4,"carbs_g":12,"fat_g":2,"fiber_g":5,"sodium_mg":100,"gi":"low","tags":["low_gi","high_fiber","anti_inflammatory","low_sodium"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner","snack"],"cuisines":["global"],"allergens":[]},
    {"name":"Steamed broccoli (1 cup)","calories":55,"protein_g":4,"carbs_g":11,"fat_g":0.6,"fiber_g":5,"sodium_mg":50,"gi":"low","tags":["low_gi","high_fiber","anti_inflammatory","low_sodium"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["global"],"allergens":[]},
    {"name":"Stir-fried mixed veg (low oil)","calories":120,"protein_g":3,"carbs_g":18,"fat_g":4,"fiber_g":5,"sodium_mg":170,"gi":"low","tags":["low_gi","high_fiber"],"diet_types":["veg","vegan"],"meal_types":["lunch","dinner"],"cuisines":["asian"],"allergens":[]},
    {"name":"Apple (1)","calories":95,"protein_g":0.5,"carbs_g":25,"fat_g":0.3,"fiber_g":4.5,"sodium_mg":2,"gi":"low","tags":["low_gi","high_fiber","low_potassium"],"diet_types":["veg","vegan"],"meal_types":["breakfast","snack"],"cuisines":["global"],"allergens":[]},
    {"name":"Banana (1)","calories":105,"protein_g":1.3,"carbs_g":27,"fat_g":0.4,"fiber_g":3.1,"sodium_mg":1,"gi":"medium","tags":["moderate_gi","high_potassium"],"diet_types":["veg","vegan"],"meal_types":["breakfast","snack"],"cuisines":["global"],"allergens":[]},
    {"name":"Mixed berries (1 cup)","calories":65,"protein_g":1,"carbs_g":16,"fat_g":0.5,"fiber_g":7,"sodium_mg":2,"gi":"low","tags":["low_gi","high_fiber","anti_inflammatory"],"diet_types":["veg","vegan"],"meal_types":["breakfast","snack"],"cuisines":["global"],"allergens":[]},
    {"name":"Low-fat yogurt (200g)","calories":140,"protein_g":12,"carbs_g":12,"fat_g":4,"fiber_g":0,"sodium_mg":90,"gi":"low","tags":["probiotic"],"diet_types":["veg"],"meal_types":["breakfast","snack"],"cuisines":["global"],"allergens":["lactose"]},
    {"name":"Unsweetened soy milk (250ml)","calories":90,"protein_g":7,"carbs_g":4,"fat_g":5,"fiber_g":2,"sodium_mg":90,"gi":"low","tags":["vegan"],"diet_types":["veg","vegan"],"meal_types":["breakfast","snack"],"cuisines":["global"],"allergens":["soy"]},
    {"name":"Almonds (20g)","calories":116,"protein_g":4,"carbs_g":4,"fat_g":10,"fiber_g":2.5,"sodium_mg":1,"gi":"low","tags":["healthy_fat","anti_inflammatory"],"diet_types":["veg","vegan"],"meal_types":["snack"],"cuisines":["global"],"allergens":["nuts"]},
    {"name":"Roasted chana (30g)","calories":120,"protein_g":6,"carbs_g":18,"fat_g":2,"fiber_g":5,"sodium_mg":120,"gi":"low","tags":["low_gi","high_fiber","plant_protein"],"diet_types":["veg","vegan"],"meal_types":["snack"],"cuisines":["indian"],"allergens":[]},
    {"name":"Hummus with carrot sticks","calories":150,"protein_g":5,"carbs_g":15,"fat_g":8,"fiber_g":4,"sodium_mg":180,"gi":"low","tags":["low_gi","high_fiber","plant_protein"],"diet_types":["veg","vegan"],"meal_types":["snack"],"cuisines":["mediterranean"],"allergens":["sesame"]},
    {"name":"Green tea (unsweetened)","calories":2,"protein_g":0,"carbs_g":0,"fat_g":0,"fiber_g":0,"sodium_mg":0,"gi":"low","tags":["anti_inflammatory"],"diet_types":["veg","vegan","non-veg"],"meal_types":["breakfast","snack","dinner"],"cuisines":["global"],"allergens":[]},
    {"name":"Lemon water (unsweetened)","calories":4,"protein_g":0,"carbs_g":1,"fat_g":0,"fiber_g":0,"sodium_mg":0,"gi":"low","tags":["hydration"],"diet_types":["veg","vegan","non-veg"],"meal_types":["breakfast","snack","dinner"],"cuisines":["global"],"allergens":[]},
]

FACTORS = [0.6, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0]


def _scale(v: float, f: float, as_int: bool = False):
    x = v * f
    return int(round(x)) if as_int else round(x, 1)


def generate_rows(size: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    i = 0
    while len(rows) < size:
        seed = SEEDS[i % len(SEEDS)]
        factor = FACTORS[(i // len(SEEDS)) % len(FACTORS)]
        row = {
            "name": f"{seed['name']} | portion_x{factor}",
            "calories": _scale(seed["calories"], factor, as_int=True),
            "protein_g": _scale(seed["protein_g"], factor),
            "carbs_g": _scale(seed["carbs_g"], factor),
            "fat_g": _scale(seed["fat_g"], factor),
            "fiber_g": _scale(seed.get("fiber_g", 0), factor),
            "sodium_mg": _scale(seed.get("sodium_mg", 0), factor, as_int=True),
            "gi": seed.get("gi", ""),
            "tags": ",".join(seed.get("tags", [])),
            "diet_types": ",".join(seed.get("diet_types", [])),
            "meal_types": ",".join(seed.get("meal_types", [])),
            "cuisines": ",".join(seed.get("cuisines", [])),
            "allergens": ",".join(seed.get("allergens", [])),
        }
        rows.append(row)
        i += 1
    return rows[:size]


def write_csv(out_path: Path, rows: List[Dict[str, Any]]):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "name","calories","protein_g","carbs_g","fat_g","fiber_g","sodium_mg","gi",
        "tags","diet_types","meal_types","cuisines","allergens",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--size", type=int, default=600)
    p.add_argument("--out", type=str, default="datasets/foods_600.csv")
    args = p.parse_args()

    rows = generate_rows(args.size)
    write_csv(Path(args.out), rows)
    print(f"Wrote {args.size} rows to {args.out}")


if __name__ == "__main__":
    main()
