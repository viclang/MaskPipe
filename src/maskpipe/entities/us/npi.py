"""US NPI (National Provider Identifier) entity.

Recognizes NPI numbers assigned to healthcare providers by CMS.
Format: 10 digits starting with 1 (individual) or 2 (organization).
Includes Luhn checksum validation with "80840" prefix per CMS spec.
"""
from typing import List

from spacy.tokens import Span

from ..entity import Entity


def _valid_npi(span: Span) -> bool:
    """
    Validate NPI using Luhn algorithm with "80840" prefix (CMS spec).

    Steps:
    1. Take the 10-digit NPI
    2. Prepend "80840" to get a 15-digit number
    3. Apply standard Luhn algorithm: result mod 10 should equal 0
    """
    text = span.text.strip()
    digits = [c for c in text if c.isdigit()]

    if len(digits) != 10:
        return False

    # Must start with 1 or 2
    if digits[0] not in ("1", "2"):
        return False

    # Reject if all body digits are identical (e.g., 1111111111)
    body = digits[:-1]
    if len(set(body)) == 1:
        return False

    # Luhn checksum with "80840" prefix
    prefixed = "80840" + "".join(digits)
    nums = [int(d) for d in prefixed]

    checksum = 0
    for i, digit in enumerate(reversed(nums)):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit

    return checksum % 10 == 0


US_NPI = Entity(
    label="US_NPI",
    patterns=[
        # Medium: XXX-XXX-XXX format
        {
            "score": 0.5,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[12]\d{3}[- ]\d{3}[- ]\d{3}\b"}},
            ],
        },
        # Weak: 10 consecutive digits starting with 1 or 2
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[12]\d{9}\b"}},
            ],
        },
    ],
    validator=_valid_npi,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "npi"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "provider"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "national"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "taxonomy"}}]},
    ],
)
