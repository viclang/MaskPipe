"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.nigeria.ng_nin_recognizer.NgNinRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import is_verhoeff_number
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
def _check_nin(value: str) -> bool:
    return bool(len(value) == 11 and value.isnumeric() and is_verhoeff_number(int(value)))

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
