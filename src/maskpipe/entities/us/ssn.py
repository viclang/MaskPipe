"""US Social Security Number (SSN) entity.

Recognizes SSN in formats: XXX-XX-XXXX, XXX XX XXXX, XXX.XX.XXXX
Includes validation to reject invalid SSN ranges.
"""
from collections import defaultdict
from typing import List

from spacy.tokens import Span

from ..entity import Entity


def _valid_ssn(span: Span) -> bool:
    """
    Validate a US Social Security Number.

    Rules (per SSA):
    - Cannot be all zeros in any group
    - Area (first 3 digits) cannot be 000, 666, or 900-999
    - Cannot be 078-05-1120 (the test SSN)
    - Cannot be 123-45-6789
    - All digits cannot be the same
    - Delimiters must be consistent (all same or all none)
    """
    text = span.text.strip()
    only_digits = "".join(c for c in text if c.isdigit())

    # Must be exactly 9 digits
    if len(only_digits) != 9:
        return False

    # All same digit rejected
    if len(set(only_digits)) == 1:
        return False

    # Groups cannot be all zeros
    area = only_digits[:3]
    group = only_digits[3:5]
    serial = only_digits[5:]
    if group == "00" or serial == "0000":
        return False

    # Invalid area codes
    if area in ("000", "666"):
        return False
    if int(area) >= 900:
        return False

    # Known test/reserved SSNs
    if only_digits in ("078051120", "123456789", "987654321"):
        return False

    # Delimiters must all be the same character (no mixing "-" and ".")
    non_digit_chars = [c for c in text if c not in "0123456789"]
    if non_digit_chars:
        if len(set(non_digit_chars)) > 1:
            return False

    return True


SSN = Entity(
    label="US_SSN",
    patterns=[
        # Medium confidence: XXX-XX-XXXX with consistent delimiters
        {
            "score": 0.6,
            "pattern": [
                {"TEXT": {"REGEX": r"\b\d{3}[- .]\d{2}[- .]\d{4}\b"}},
            ],
        },
        # Weak confidence: 9 consecutive digits
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b\d{9}\b"}},
            ],
        },
    ],
    validator=_valid_ssn,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "social"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "security"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "ssn"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "ssid"}}]},
    ],
)
