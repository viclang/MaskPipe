"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nhs_recognizer.NhsRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b"}}]},
    {"score": 0.5, "pattern": [
        {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b([0-9]{4})\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": "nhs"}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "health"}, {"LEMMA": "service"}], "score": 0.35},
    {"pattern": [{"LEMMA": "health"}, {"LEMMA": "services"}, {"LEMMA": "authority"}], "score": 0.35},
    {"pattern": [{"LEMMA": "health"}, {"LEMMA": "authority"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    text = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    total = sum([int(c) * multiplier for c, multiplier in zip(text, reversed(range(11)))])
    remainder = total % 11
    check_remainder = remainder == 0
    return check_remainder
# END GENERATED: validator

UK_NHS = Entity(
    label="UK_NHS",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
