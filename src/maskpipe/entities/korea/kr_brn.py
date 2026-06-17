"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_brn_recognizer.KrBrnRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:

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
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', '')])
    if len(sanitized_value) != 10:
        return False
    if not sanitized_value.isdigit():
        return False
    return _validate_checksum(sanitized_value)

KR_BRN = Entity(
    label="KR_BRN",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{3}-\d{2}-\d{5}(?!\d)"}}]},
        {"score": 0.1, "pattern": [
            {"TEXT": {"REGEX": r"\b(?<!\d)\d{3}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b\d{2}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b\d{5}(?!\d)\b"}},
        ]},
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{10}(?!\d)"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["사업자등록번호", "사업자번호", "사업자", "brn", "business registration number", "korean brn", "business number", "tax registration number"]}}], "score": 0.35},
    ],
)
