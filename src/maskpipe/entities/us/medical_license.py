"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.medical_license_recognizer.MedicalLicenseRecognizer."""

# BEGIN GENERATED: imports
from typing import List
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX]{1}[a-zA-Z]{1}\d{7}|[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX]{1}9\d{7}"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["medical", "certificate", "dea"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _luhn_checksum(sanitized_value: str) -> bool:

    def digits_of(n: str) -> List[int]:
        return [int(dig) for dig in str(n)]
    digits = digits_of(sanitized_value[2:])
    checksum = digits.pop()
    even_digits = digits[-1::-2]
    odd_digits = digits[-2::-2]
    checksum *= -1
    checksum += 2 * sum(even_digits) + sum(odd_digits)
    return checksum % 10 == 0

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    checksum = _luhn_checksum(sanitized_value)
    return checksum
# END GENERATED: validator

MEDICAL_LICENSE = Entity(
    label="MEDICAL_LICENSE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
