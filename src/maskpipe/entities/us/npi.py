"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_npi_recognizer.UsNpiRecognizer."""
from spacy.tokens import Span
from maskpipe.entities.entity import Entity
from maskpipe.entities.util import sanitize_value

def _npi_luhn_checksum(sanitized_value: str) -> bool:
    prefixed = '80840' + sanitized_value
    digits = [int(d) for d in prefixed]
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    if sanitized_value:
        body = sanitized_value[:-1] if len(sanitized_value) > 1 else sanitized_value
        if body and len(set(body)) == 1:
            return False
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    return bool(_npi_luhn_checksum(sanitized_value))

US_NPI = Entity(
    label="US_NPI",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[12]\d{9}\b"}}]},
        {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"\b[12]\d{3}[ -]\d{3}[ -]\d{3}\b"}}]},
        {"score": 0.4, "pattern": [
            {"TEXT": {"REGEX": r"\b[12]\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["npi", "national provider", "provider", "npi number", "provider id", "provider identifier", "taxonomy"]}}], "score": 0.35},
    ],
)
