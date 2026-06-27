"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.nigeria.ng_nin_recognizer.NgNinRecognizer."""

# BEGIN GENERATED: imports
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b\d{11}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["nin", "nimc"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "identification"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "identity"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "identity"}], "score": 0.35},
    {"pattern": [{"LEMMA": "nigeria"}, {"LEMMA": "id"}], "score": 0.35},
    {"pattern": [{"LEMMA": "nigerian"}, {"LEMMA": "identification"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _is_verhoeff_number(input_number: int) -> bool:
    __d__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1], [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
    __p__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1], [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]
    __inv__ = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    c = 0
    inverted_number = list(map(int, reversed(str(input_number))))
    for i in range(len(inverted_number)):
        c = __d__[c][__p__[i % 8][inverted_number[i]]]
    return __inv__[c] == 0

def _check_nin(value: str) -> bool:
    return bool(len(value) == 11 and value.isnumeric() and _is_verhoeff_number(int(value)))

def _validator(span: Span) -> bool:
    pattern_text = span.text
    return bool(_check_nin(pattern_text))
# END GENERATED: validator

NG_NIN = Entity(
    label="NG_NIN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
