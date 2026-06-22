"""US ABA Routing Number entity.

Recognizes ABA (American Banking Association) routing numbers
also known as routing transit numbers (RTN).
Includes Luhn-like checksum validation.
"""
from spacy.tokens import Span

from ..entity import Entity

def _valid_aba_routing(span: Span) -> bool:
    """
    Validate ABA routing number using checksum algorithm.

    The checksum multiplies digits by [3, 7, 1, 3, 7, 1, 3, 7, 1]
    and checks if the sum mod 10 equals 0.
    """
    text = span.text.strip()
    digits = [c for c in text if c.isdigit()]
    if len(digits) != 9:
        return False

    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    checksum = sum(int(d) * w for d, w in zip(digits, weights))
    return checksum % 10 == 0

ABA_ROUTING_NUMBER = Entity(
    label="ABA_ROUTING_NUMBER",
    patterns=[
        # Medium confidence: XXX-XXX-XX format
        {
            "score": 0.5,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[0123678]\d{3}-\d{4}-\d\b"}},
            ],
        },
        # Weak confidence: 9 consecutive digits starting with 0-3 or 6-8
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[0123678]\d{8}\b"}},
            ],
        },
    ],
    validator=_valid_aba_routing,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "routing"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "aba"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "bank"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "transit"}}]},
    ],
)
