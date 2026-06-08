"""US Medicare Beneficiary Identifier (MBI) entity.

Recognizes Medicare MBI numbers in format: C A AN N A AN N A A N N
where:
- C = numeric character (0-9)
- A = alphabetic (excluding S, L, O, I, B, Z)
- AN = alphanumeric (excluding S, L, O, I, B, Z)

Examples: 1EG4-TE5-MK73 (with dashes) or 1EG4TE5MK737 (without)
"""
from spacy.tokens import Span

from ..entity import Entity

# Valid letters: A-Z excluding S, L, O, I, B, Z
_VALID_LETTERS = "ACDEFGHJKMNPQRTUVWXY"
_VALID_ALPHANUM = "0-9ACDEFGHJKMNPQRTUVWXY"

# Regex patterns
_MBI_NO_DASH = (
    rf"[0-9][{_VALID_LETTERS}][{_VALID_ALPHANUM}][0-9]"
    rf"[{_VALID_LETTERS}][{_VALID_ALPHANUM}][0-9]"
    rf"[{_VALID_LETTERS}][{_VALID_LETTERS}][0-9][0-9]"
)
_MBI_WITH_DASH = (
    rf"[0-9][{_VALID_LETTERS}][{_VALID_ALPHANUM}][0-9]-"
    rf"[{_VALID_LETTERS}][{_VALID_ALPHANUM}][0-9]-"
    rf"[{_VALID_LETTERS}][{_VALID_LETTERS}][0-9][0-9]"
)


def _valid_mbi(span: Span) -> bool:
    """Validate MBI format (11 chars, correct positions)."""
    text = span.text.strip()
    # Remove dashes for validation
    clean = text.replace("-", "")
    if len(clean) != 11:
        return False

    # Check each position
    for i, (char, expected) in enumerate(zip(clean, "NLNLNLNNNN")):
        if expected == "N":
            if not char.isdigit():
                return False
        elif expected == "L":
            if char not in _VALID_LETTERS:
                return False
        elif expected == "A":
            if char not in _VALID_ALPHANUM:
                return False
    return True


US_MBI = Entity(
    label="US_MBI",
    patterns=[
        # Medium: with dashes XXXX-XXX-XXXX
        {
            "score": 0.5,
            "pattern": [
                {"TEXT": {"REGEX": rf"\b{_MBI_WITH_DASH}\b"}},
            ],
        },
        # Weak: without dashes
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": rf"\b{_MBI_NO_DASH}\b"}},
            ],
        },
    ],
    validator=_valid_mbi,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "medicare"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "mbi"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "beneficiary"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "cms"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "medicaid"}}]},
    ],
)
