"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.aba_routing_recognizer.AbaRoutingRecognizer."""
from spacy.tokens import Span
from typing import List
from typing import Tuple
from maskpipe.entities.entity import Entity

def _checksum(sanitized_value: str) -> bool:
    s = 0
    for idx, m in enumerate([3, 7, 1, 3, 7, 1, 3, 7, 1]):
        s += int(sanitized_value[idx]) * m
    return s % 10 == 0

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', '')])
    return bool(_checksum(sanitized_value))

ABA_ROUTING_NUMBER = Entity(
    label="ABA_ROUTING_NUMBER",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b[0123678]\d{8}\b"}}]},
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b[0123678]\d{3}-\d{4}-\d\b"}}]},
        {"score": 0.3, "pattern": [
            {"TEXT": {"REGEX": r"\b[0123678]\d{3}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b\d{4}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b\d\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["aba", "routing", "abarouting", "association", "bankrouting"]}}], "score": 0.35},
    ],
)
