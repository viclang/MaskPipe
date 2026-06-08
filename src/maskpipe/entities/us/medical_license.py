"""US Medical License / DEA Number entity.

Recognizes DEA certificate numbers for US healthcare providers.
Format: 2 letters + 7 digits, or 1 letter + 9 digits.
First letter is A-G, H, J-K, L, M, P, R, S, T, U, or X.
Second letter is always A-Z.
Includes Luhn checksum validation.
"""
from typing import List

from spacy.tokens import Span

from ..entity import Entity


def _valid_medical_license(span: Span) -> bool:
    """
    Validate DEA/Medical License number using Luhn checksum.

    The checksum is applied to digits 3-9 (skipping the first 2 letters).
    """
    text = span.text.strip()

    if len(text) != 9:
        return False

    # First char must be a valid DEA prefix letter
    valid_prefix = "abcdefghjklmprstuxABCDEFGHJKLMPRSTUX"
    if text[0] not in valid_prefix:
        return False

    # Second char must be a letter
    if not text[1].isalpha():
        return False

    # Remaining 7 chars must be digits
    if not text[2:].isdigit():
        return False

    # Luhn checksum on last 7 digits
    digits = text[2:]
    checksum = int(digits[-1]) * -1
    even_digits = [int(d) for d in digits[-2::-2]]
    odd_digits = [int(d) for d in digits[-3::-2]]
    checksum += 2 * sum(even_digits) + sum(odd_digits)

    return checksum % 10 == 0


US_MEDICAL_LICENSE = Entity(
    label="US_MEDICAL_LICENSE",
    patterns=[
        # Medium: AAX-XXXXXXX (first letter + letter + 7 digits)
        {
            "score": 0.5,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX][a-zA-Z]\d{7}\b"}},
            ],
        },
        # Weak: A9-XXXXXXXX (first letter + 9)
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX]9\d{7}\b"}},
            ],
        },
    ],
    validator=_valid_medical_license,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "dea"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "medical"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "certificate"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "license"}}]},
    ],
)
