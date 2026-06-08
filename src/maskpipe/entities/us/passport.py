"""US Passport Number entity.

Recognizes US passport numbers in both legacy (9 digits) and
Next Generation (letter + 8 digits) formats.
"""
from spacy.tokens import Span

from ..entity import Entity

# US Passport numbers are inherently weak matches (9 digits could be anything)
# Validation helps reduce false positives


def _valid_passport(span: Span) -> bool:
    """Basic validation for US passport numbers."""
    text = span.text.strip()
    only_digits = "".join(c for c in text if c.isdigit())

    # Legacy format: 9 digits
    if len(only_digits) == 9 and len(text) == 9:
        return True

    # Next Generation: 1 letter + 8 digits
    if len(text) == 9 and text[0].isalpha() and only_digits.isdigit():
        return True

    return False


US_PASSPORT = Entity(
    label="US_PASSPORT",
    patterns=[
        # Next Generation: letter + 8 digits (medium)
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[A-Z]\d{8}\b"}},
            ],
        },
        # Legacy: 9 digits (weak)
        {
            "score": 0.15,
            "pattern": [
                {"TEXT": {"REGEX": r"\b\d{9}\b"}},
            ],
        },
    ],
    validator=_valid_passport,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "passport"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "travel"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "document"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "identity"}}]},
    ],
)
