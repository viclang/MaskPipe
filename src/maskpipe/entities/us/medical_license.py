"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.medical_license_recognizer.MedicalLicenseRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

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

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    checksum = _luhn_checksum(sanitized_value)
    return checksum

MEDICAL_LICENSE = Entity(
    label="MEDICAL_LICENSE",
    patterns=[
        {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX]{1}[a-zA-Z]{1}\d{7}|[abcdefghjklmprstuxABCDEFGHJKLMPRSTUX]{1}9\d{7}"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["medical", "certificate", "dea"]}}], "score": 0.35},
    ],
)
