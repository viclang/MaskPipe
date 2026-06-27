"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.aba_routing_recognizer.AbaRoutingRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b[0123678]\d{8}\b"}}]},
    {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b[0123678]\d{3}-\d{4}-\d\b"}}]},
    {"score": 0.3, "pattern": [
        {"TEXT": {"REGEX": r"\b[0123678]\d{3}\b"}},
        {"TEXT": "-"},
        {"TEXT": {"REGEX": r"\b\d{4}\b"}},
        {"TEXT": "-"},
        {"TEXT": {"REGEX": r"\b\d\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["aba", "routing", "abarouting", "association", "bankrouting"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _checksum(sanitized_value: str) -> bool:
    s = 0
    for idx, m in enumerate([3, 7, 1, 3, 7, 1, 3, 7, 1]):
        s += int(sanitized_value[idx]) * m
    return s % 10 == 0

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', '')])
    return bool(_checksum(sanitized_value))
# END GENERATED: validator

ABA_ROUTING_NUMBER = Entity(
    label="ABA_ROUTING_NUMBER",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
