from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Dict, Any


# NOTE: This schema captures all input features requested in the task
# and offers basic helpers for validation/normalization.


@dataclass
class PersonalDetails:
    age: int
    gender: str  # "male" | "female" | "other"
    height_cm: float
    weight_kg: float
    bmi: Optional[float] = None
    body_type: Optional[str] = None  # e.g., "ectomorph", "mesomorph", "endomorph"


@dataclass
class MedicalParameters:
    conditions: List[str] = field(default_factory=list)  # e.g., ["diabetes", "hypertension"]
    allergies: List[str] = field(default_factory=list)   # e.g., ["lactose", "gluten", "nuts", "seafood"]
    medications: List[str] = field(default_factory=list)
    blood_sugar_mgdl: Optional[float] = None
    blood_pressure: Optional[Tuple[int, int]] = None     # (systolic, diastolic)
    cholesterol_mgdl: Optional[float] = None
    hemoglobin_gdl: Optional[float] = None


@dataclass
class DietaryPreferences:
    diet_type: str = "veg"  # "veg" | "non-veg" | "vegan"
    likes: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    preferred_cuisine: List[str] = field(default_factory=list)
    meal_frequency: int = 3
    snacking_preference: str = "moderate"  # "low" | "moderate" | "high"


@dataclass
class LifestyleParameters:
    activity_level: str = "sedentary"  # keys of ACTIVITY_FACTORS
    exercise_routine: str = "none"
    sleep_hours: float = 7.0
    stress_level: str = "moderate"  # "low" | "moderate" | "high"


@dataclass
class NutritionalRequirements:
    daily_calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None
    salt_limit_g: Optional[float] = None
    sugar_limit_g: Optional[float] = None
    water_liters: Optional[float] = None


@dataclass
class SpecialDietRules:
    low_gi: bool = False
    low_sodium: bool = False
    high_fiber: bool = False
    renal: bool = False
    high_protein: bool = False
    anti_inflammatory: bool = False
    weight_gain: bool = False
    weight_loss: bool = False
    gluten_free: bool = False
    lactose_free: bool = False


@dataclass
class UserProfile:
    personal: PersonalDetails
    medical: MedicalParameters
    dietary: DietaryPreferences
    lifestyle: LifestyleParameters
    nutrition: NutritionalRequirements
    special: SpecialDietRules

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------- Helpers ---------------------------

def compute_bmi(height_cm: float, weight_kg: float) -> float:
    """Compute BMI given height in cm and weight in kg."""
    h_m = height_cm / 100.0
    if h_m <= 0:
        return 0.0
    return round(weight_kg / (h_m ** 2), 2)


def normalize_gender(g: str) -> str:
    g = (g or "").strip().lower()
    if g in {"m", "male"}:
        return "male"
    if g in {"f", "female"}:
        return "female"
    return "other"


def normalize_list(xs: Optional[List[str]]) -> List[str]:
    return [x.strip().lower() for x in (xs or []) if isinstance(x, str) and x.strip()]


def from_dict(data: Dict[str, Any]) -> UserProfile:
    """Create a UserProfile from a nested dict. Attempts to compute BMI if missing."""
    p = data.get("personal", {})
    m = data.get("medical", {})
    d = data.get("dietary", {})
    l = data.get("lifestyle", {})
    n = data.get("nutrition", {})
    s = data.get("special", {})

    personal = PersonalDetails(
        age=int(p.get("age", 30)),
        gender=normalize_gender(p.get("gender", "other")),
        height_cm=float(p.get("height", p.get("height_cm", 170))),
        weight_kg=float(p.get("weight", p.get("weight_kg", 70))),
        bmi=p.get("bmi"),
        body_type=p.get("body_type"),
    )
    if personal.bmi is None:
        personal.bmi = compute_bmi(personal.height_cm, personal.weight_kg)

    medical = MedicalParameters(
        conditions=normalize_list(m.get("conditions")),
        allergies=normalize_list(m.get("allergies")),
        medications=m.get("medications", []) or [],
        blood_sugar_mgdl=(
            float(m.get("blood_sugar_mgdl")) if m.get("blood_sugar_mgdl") is not None else None
        ),
        blood_pressure=tuple(m.get("blood_pressure")) if m.get("blood_pressure") else None,
        cholesterol_mgdl=(
            float(m.get("cholesterol_mgdl")) if m.get("cholesterol_mgdl") is not None else None
        ),
        hemoglobin_gdl=(
            float(m.get("hemoglobin_gdl")) if m.get("hemoglobin_gdl") is not None else None
        ),
    )

    dietary = DietaryPreferences(
        diet_type=(d.get("diet_type") or "veg").strip().lower(),
        likes=normalize_list(d.get("likes")),
        dislikes=normalize_list(d.get("dislikes")),
        preferred_cuisine=normalize_list(d.get("preferred_cuisine")),
        meal_frequency=int(d.get("meal_frequency", 3)),
        snacking_preference=(d.get("snacking_preference") or "moderate").strip().lower(),
    )

    lifestyle = LifestyleParameters(
        activity_level=(l.get("activity_level") or "sedentary").strip().lower(),
        exercise_routine=l.get("exercise_routine", "none"),
        sleep_hours=float(l.get("sleep_hours", 7.0)),
        stress_level=(l.get("stress_level") or "moderate").strip().lower(),
    )

    nutrition = NutritionalRequirements(
        daily_calories=(int(n.get("daily_calories")) if n.get("daily_calories") is not None else None),
        protein_g=(float(n.get("protein_g")) if n.get("protein_g") is not None else None),
        carbs_g=(float(n.get("carbs_g")) if n.get("carbs_g") is not None else None),
        fats_g=(float(n.get("fats_g")) if n.get("fats_g") is not None else None),
        salt_limit_g=(float(n.get("salt_limit_g")) if n.get("salt_limit_g") is not None else None),
        sugar_limit_g=(float(n.get("sugar_limit_g")) if n.get("sugar_limit_g") is not None else None),
        water_liters=(float(n.get("water_liters")) if n.get("water_liters") is not None else None),
    )

    special = SpecialDietRules(
        low_gi=bool(s.get("low_gi", False)),
        low_sodium=bool(s.get("low_sodium", False)),
        high_fiber=bool(s.get("high_fiber", False)),
        renal=bool(s.get("renal", False)),
        high_protein=bool(s.get("high_protein", False)),
        anti_inflammatory=bool(s.get("anti_inflammatory", False)),
        weight_gain=bool(s.get("weight_gain", False)),
        weight_loss=bool(s.get("weight_loss", False)),
        gluten_free=bool(s.get("gluten_free", False)),
        lactose_free=bool(s.get("lactose_free", False)),
    )

    return UserProfile(
        personal=personal,
        medical=medical,
        dietary=dietary,
        lifestyle=lifestyle,
        nutrition=nutrition,
        special=special,
    )


def load_profile_json(path: str) -> UserProfile:
    import json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return from_dict(data)
