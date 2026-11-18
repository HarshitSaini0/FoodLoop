"""Fixed routing rules. A plain rule engine decides; no language model is involved.

Rules mirror Table 1 of the FoodLoop concept paper. They are a design proposal,
not validated food-safety limits.
"""
from dataclasses import dataclass

CONFIDENCE_MIN = 0.80

ROUTES = ("people", "animals", "energy_or_compost", "hold")

ROUTE_LABELS = {
    "people": "Feed people (shelter or food bank)",
    "animals": "Feed animals",
    "energy_or_compost": "Energy (digester) or compost",
    "hold": "Hold for a person to decide",
}


@dataclass(frozen=True)
class Decision:
    route: str
    reason: str


def propose_route(label: str, confidence: float, higher_risk: bool) -> Decision:
    """Return the suggested route. A person must still confirm it."""
    if higher_risk:
        return Decision("hold", "Higher-risk food (for example meat, dairy, ready-to-eat) needs a stricter check.")
    if confidence < CONFIDENCE_MIN:
        return Decision("hold", f"Model confidence {confidence:.0%} is below the {CONFIDENCE_MIN:.0%} minimum.")
    if label == "fresh":
        return Decision("people", "Model reads the food as fresh with enough confidence.")
    if label == "rotten":
        return Decision("energy_or_compost", "Model reads the food as spoiled with enough confidence.")
    return Decision("hold", f"Unknown label '{label}'.")
