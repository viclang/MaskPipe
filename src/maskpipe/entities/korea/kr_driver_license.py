"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_driver_license_recognizer.KrDriverLicenseRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)(\d{2})[- ]?(\d{2})[- ]?(\d{6})[- ]?(\d{2})(?!\d)"}}]},
    {"score": 0.05, "pattern": [
        {"TEXT": {"REGEX": r"\b(?<!\d)(\d{2})\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b(\d{2})\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b(\d{6})\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b(\d{2})(?!\d)\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["운전면허", "운전면허번호", "면허번호"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "driver"}, {"LEMMA": "license"}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "driver's"}, {"LEMMA": "license"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    if len(sanitized_value) != 12:
        return False
    if not sanitized_value.isdigit():
        return False
    region_code = sanitized_value[:2]
    if region_code not in {'11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '28'}:
        return False
    return True
# END GENERATED: validator

KR_DRIVER_LICENSE = Entity(
    label="KR_DRIVER_LICENSE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
