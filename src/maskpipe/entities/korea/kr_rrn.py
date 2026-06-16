"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_rrn_recognizer.KrRrnRecognizer."""
from spacy.tokens import Span
from typing import List
from typing import Tuple
from typing import Optional
from maskpipe.entities.entity import Entity

def _validate_region_code(region_code: int) -> bool:
    return bool(True if 0 <= region_code <= 95 else False)

def _compute_checksum(rn: str) -> int:
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    return sum((int(rn[i]) * weights[i] for i in range(12)))

def _validate_checksum(rrn: str) -> bool:
    digit_sum = _compute_checksum(rrn)
    checksum = (11 - digit_sum % 11) % 10
    return checksum == int(rrn[12])

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

KR_RRN = Entity(
    label="KR_RRN",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(-?)[1-4]\d{6}(?!\d)"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["korean rrn", "korean resident registration number", "resident registration number", "rrn", "rrn", "rrn#"]}}], "score": 0.35},
    ],
)
