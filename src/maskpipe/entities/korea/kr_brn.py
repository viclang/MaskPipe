"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_brn_recognizer.KrBrnRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{3}-\d{2}-\d{5}(?!\d)"}}]},
    {"score": 0.1, "pattern": [
        {"TEXT": {"REGEX": r"\b(?<!\d)\d{3}\b"}},
        {"TEXT": "-"},
        {"TEXT": {"REGEX": r"\b\d{2}\b"}},
        {"TEXT": "-"},
        {"TEXT": {"REGEX": r"\b\d{5}(?!\d)\b"}},
    ]},
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{10}(?!\d)"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["사업자등록번호", "사업자번호", "사업자", "brn"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "business"}, {"LEMMA": "registration"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "brn"}], "score": 0.35},
    {"pattern": [{"LEMMA": "business"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "tax"}, {"LEMMA": "registration"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validate_checksum(brn: str) -> bool:
    digits = [int(d) for d in brn]
    magic_keys = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    total_sum = 0
    for i in range(8):
        total_sum += digits[i] * magic_keys[i]
    last_key_mul = digits[8] * magic_keys[8]
    total_sum += last_key_mul // 10 + last_key_mul
    remainder = total_sum % 10
    check_digit = (10 - remainder) % 10
    return check_digit == digits[9]

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', '')])
    if len(sanitized_value) != 10:
        return False
    if not sanitized_value.isdigit():
        return False
    return _validate_checksum(sanitized_value)
# END GENERATED: validator

KR_BRN = Entity(
    label="KR_BRN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
