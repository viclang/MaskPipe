"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_aadhaar_recognizer.InAadhaarRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _is_verhoeff_number(input_number: int) -> bool:
    __d__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1], [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
    __p__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1], [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]
    __inv__ = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    c = 0
    inverted_number = list(map(int, reversed(str(input_number))))
    for i in range(len(inverted_number)):
        c = __d__[c][__p__[i % 8][inverted_number[i]]]
    return __inv__[c] == 0

def _is_palindrome(text: str, case_insensitive: bool=False) -> bool:
    palindrome_text = text
    if case_insensitive:
        palindrome_text = palindrome_text.replace(' ', '').lower()
    return palindrome_text == palindrome_text[::-1]

def _check_aadhaar(sanitized_value: str) -> bool:
    is_valid_aadhaar: bool = False
    if len(sanitized_value) == 12 and sanitized_value.isnumeric() is True and (int(sanitized_value[0]) >= 2) and (_is_verhoeff_number(int(sanitized_value)) is True) and (_is_palindrome(sanitized_value) is False):
        is_valid_aadhaar = True
    return is_valid_aadhaar

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', ''), (':', '')])
    return bool(_check_aadhaar(sanitized_value))

IN_AADHAAR = Entity(
    label="IN_AADHAAR",
    patterns=[
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{12}\b"}}]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{4}[- :][0-9]{4}[- :][0-9]{4}\b"}}]},
        {"score": 0.01, "pattern": [
            {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["aadhaar", "uidai"]}}], "score": 0.35},
    ],
)
