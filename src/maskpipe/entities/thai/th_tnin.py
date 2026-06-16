"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.thai.th_tnin_recognizer.ThTninRecognizer."""
from spacy.tokens import Span
from typing import List
from typing import Tuple
from typing import Union
from maskpipe.entities.entity import Entity

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

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> Union[bool, None]:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [])
    if len(sanitized_value) != 13:
        return False
    if not sanitized_value.isdigit():
        return False
    return _validate_checksum(sanitized_value)

TH_TNIN = Entity(
    label="TH_TNIN",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[1-9](?:[134][0-9]|[25][0134567]|[67][01234567]|[89][0123456])\d{10}\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["thai national id", "thai id number", "tnin", "เลขประจำตัวประชาชน", "เลขบัตรประชาชน", "รหัสปชช"]}}], "score": 0.35},
    ],
)
