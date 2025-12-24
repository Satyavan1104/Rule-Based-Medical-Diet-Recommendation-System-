from app.data.schema import from_dict
from app.rules.engine import build_constraints


def test_diabetes_rules_low_gi_required():
    profile = from_dict({
        "personal": {"age": 40, "gender": "male", "height": 175, "weight": 80},
        "medical": {"conditions": ["diabetes"]},
        "dietary": {"diet_type": "veg"},
        "lifestyle": {},
        "nutrition": {},
        "special": {},
    })
    c, _ = build_constraints(profile)
    assert "low_gi" in c.required_tags
    assert "refined_sugar" in c.avoid_tags


def test_hypertension_sodium_limit():
    profile = from_dict({
        "personal": {"age": 40, "gender": "male", "height": 175, "weight": 80},
        "medical": {"conditions": ["hypertension"]},
        "dietary": {"diet_type": "veg"},
        "lifestyle": {},
        "nutrition": {},
        "special": {},
    })
    c, _ = build_constraints(profile)
    assert c.max_sodium_mg is not None
    assert c.max_sodium_mg <= 1500


def test_renal_avoids_banana_and_rajma():
    profile = from_dict({
        "personal": {"age": 40, "gender": "male", "height": 175, "weight": 80},
        "medical": {"conditions": ["kidney disease"]},
        "dietary": {"diet_type": "veg"},
        "lifestyle": {},
        "nutrition": {},
        "special": {},
    })
    c, _ = build_constraints(profile)
    # Avoid names are matched as substrings
    assert any(name in c.avoid_names for name in {"banana", "rajma"})


def test_thyroid_caution_soy():
    profile = from_dict({
        "personal": {"age": 40, "gender": "female", "height": 165, "weight": 60},
        "medical": {"conditions": ["thyroid"]},
        "dietary": {"diet_type": "veg"},
        "lifestyle": {},
        "nutrition": {},
        "special": {},
    })
    c, _ = build_constraints(profile)
    assert any("tofu" in n for n in c.avoid_names)
