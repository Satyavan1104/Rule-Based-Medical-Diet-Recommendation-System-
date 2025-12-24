from __future__ import annotations
from typing import Dict, Any

from app.data.schema import from_dict, UserProfile
from app.services.recommender import recommend as _recommend


def get_recommendations(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Programmatic API entrypoint.
    Pass a nested dict matching the UserProfile schema, returns recommendations dict.
    """
    profile: UserProfile = from_dict(input_payload)
    return _recommend(profile)
