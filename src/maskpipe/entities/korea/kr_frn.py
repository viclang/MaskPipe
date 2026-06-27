"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_frn_recognizer.KrFrnRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(-?)[5-8]\d{6}(?!\d)"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["외국인등록번호", "frn", "외국인번호"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "frn"}], "score": 0.35},
    {"pattern": [{"LEMMA": "foreigner"}, {"LEMMA": "registration"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "foreigner"}, {"LEMMA": "registration"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validate_region_code(region_code: int) -> bool:
    return bool(True if 0 <= region_code <= 95 else False)

def _validate_checksum(frn: str) -> bool:
    digit_sum = super()._compute_checksum(frn)
    checksum = (13 - digit_sum % 11) % 10
    return checksum == int(frn[12])

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', '')])
    if len(sanitized_value) != 13:
        return False
    if not sanitized_value.isdigit():
        return False
    region_code = int(sanitized_value[7:9])
    if _validate_region_code(region_code) and _validate_checksum(sanitized_value):
        return True
    return None
# END GENERATED: validator

KR_FRN = Entity(
    label="KR_FRN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
