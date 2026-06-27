"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_npi_recognizer.UsNpiRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[12]\d{9}\b"}}]},
    {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"\b[12]\d{3}[ -]\d{3}[ -]\d{3}\b"}}]},
    {"score": 0.4, "pattern": [
        {"TEXT": {"REGEX": r"\b[12]\d{3}\b"}},
        {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        {"TEXT": {"REGEX": r"\b\d{3}\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["npi", "provider", "taxonomy"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "provider"}], "score": 0.35},
    {"pattern": [{"LEMMA": "npi"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "provider"}, {"LEMMA": "id"}], "score": 0.35},
    {"pattern": [{"LEMMA": "provider"}, {"LEMMA": "identifier"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _invalidate(pattern_text: str) -> bool:
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    if sanitized_value:
        body = sanitized_value[:-1] if len(sanitized_value) > 1 else sanitized_value
        if body and len(set(body)) == 1:
            return True
    return False

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
    if _invalidate(pattern_text):
        return False
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    return bool(_npi_luhn_checksum(sanitized_value))
# END GENERATED: validator

US_NPI = Entity(
    label="US_NPI",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
