"""US ITIN (Individual Taxpayer Identification Number) entity.

Recognizes ITINs issued by the IRS for individuals who are not
eligible for SSNs. Format: 9XX-XX-XXXX where 9XX starts with 9
and the second group starts with 5-9 (excluding 93).
"""
from spacy.tokens import Span

from ..entity import Entity


def _valid_itin(span: Span) -> bool:
    """
    Validate US ITIN format.

    ITIN format: 9XX-XX-XXXX
    - Always starts with 9
    - Second group (positions 4-5) starts with 5, 6, 7, 8, or 9 (not 93)
    """
    text = span.text.strip()
    only_digits = "".join(c for c in text if c.isdigit())

    if len(only_digits) != 9:
        return False

    # Must start with 9
    if only_digits[0] != "9":
        return False

    # Second group must be 50-92 (not 93-99)
    second_group = int(only_digits[3:5])
    if second_group < 50 or second_group > 92:
        return False

    return True


US_ITIN = Entity(
    label="US_ITIN",
    patterns=[
        # Medium: 9XX-XX-XXXX with consistent delimiters
        {
            "score": 0.5,
            "pattern": [
                {"TEXT": {"REGEX": r"\b9\d{2}[- .](5\d|6[0-5]|7\d|8[0-8]|9[0-24-9])[- .]\d{4}\b"}},
            ],
        },
        # Weak: 9XX-XXXX (hyphen only)
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b9\d{2}[- ](5\d|6[0-5]|7\d|8[0-8]|9[0-24-9])\d{4}\b"}},
            ],
        },
        # Very weak: 9 digits starting with 9
        {
            "score": 0.15,
            "pattern": [
                {"TEXT": {"REGEX": r"\b9\d{8}\b"}},
            ],
        },
    ],
    validator=_valid_itin,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "itin"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "tax"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "taxpayer"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "taxid"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "tin"}}]},
    ],
)
