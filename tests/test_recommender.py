from app.data.schema import from_dict
from app.services.recommender import recommend


def test_recommendation_structure():
    profile = from_dict({
        "personal": {"age": 45, "gender": "male", "height": 172, "weight": 80},
        "medical": {"conditions": ["diabetes", "hypertension"]},
        "dietary": {"diet_type": "veg", "preferred_cuisine": ["indian"], "dislikes": ["spicy"]},
        "lifestyle": {"activity_level": "moderate", "sleep_hours": 6.5, "stress_level": "high"},
        "nutrition": {"daily_calories": 1800},
        "special": {"low_gi": True, "low_sodium": True, "weight_loss": True},
    })

    result = recommend(profile)
    for key in [
        "personalized_meal_plan",
        "snacks_recommendation",
        "foods_to_include",
        "foods_to_avoid",
        "calorie_breakdown",
        "weekly_diet_plan",
        "hydration_and_lifestyle_tips",
        "preparation_tips",
        "nutrition_targets",
        "explanations",
    ]:
        assert key in result
