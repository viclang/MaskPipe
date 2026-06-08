"""US Driver License Number entity.

Recognizes US driver license numbers in various state formats.
Note: formats vary by state, so this uses broad patterns with
low confidence. Context patterns are important for accuracy.
"""
from spacy.tokens import Span

from ..entity import Entity

# Pattern components from NTSI (National Traffic and Motor Vehicle Safety Act)
# States have different formats, so we use a broad approach


def _valid_driver_license(span: Span) -> bool:
    """Basic validation for driver license numbers."""
    text = span.text.strip()
    # Must be at least 6 characters, at most 17
    if len(text) < 6 or len(text) > 17:
        return False
    # Must contain at least one letter or digit
    if not any(c.isalnum() for c in text):
        return False
    return True


US_DRIVER_LICENSE = Entity(
    label="US_DRIVER_LICENSE",
    patterns=[
        # Alphanumeric: starts with letter(s), followed by digits (medium)
        {
            "score": 0.4,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[A-Z][A-Z0-9*]{5,11}\b"}},
            ],
        },
        # Alphanumeric: starts with digits, contains a letter (weak)
        {
            "score": 0.25,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[0-9]{3,8}[A-Z][0-9A-Z*]{3,8}\b"}},
            ],
        },
        # Pure digits (very weak - many false positives)
        {
            "score": 0.1,
            "pattern": [
                {"TEXT": {"REGEX": r"\b\d{6,17}\b"}},
            ],
        },
    ],
    validator=_valid_driver_license,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "driver"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "license"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "permit"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "lic"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "identification"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "dls"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "cdls"}}]},
    ],
)
