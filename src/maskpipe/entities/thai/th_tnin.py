"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.thai.th_tnin_recognizer.ThTninRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[1-9](?:[134][0-9]|[25][0134567]|[67][01234567]|[89][0123456])\d{10}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["tnin", "เลขประจำตัวประชาชน", "เลขบัตรประชาชน", "รหัสปชช"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "thai"}, {"LEMMA": "national"}, {"LEMMA": "id"}], "score": 0.35},
    {"pattern": [{"LEMMA": "thai"}, {"LEMMA": "id"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validate_checksum(tnin: str) -> bool:
    weights = list(range(13, 1, -1))
    total_sum = 0
    for i in range(12):
        total_sum += weights[i] * int(tnin[i])
    x = total_sum % 11
    if x <= 1:
        expected_check_digit = 1 - x
    else:
        expected_check_digit = 11 - x
    actual_check_digit = int(tnin[12])
    return expected_check_digit == actual_check_digit

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [])
    if len(sanitized_value) != 13:
        return False
    if not sanitized_value.isdigit():
        return False
    return _validate_checksum(sanitized_value)
# END GENERATED: validator

TH_TNIN = Entity(
    label="TH_TNIN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
