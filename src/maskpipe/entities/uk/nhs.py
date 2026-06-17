"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nhs_recognizer.NhsRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:

    def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
    pattern_text = span.text
    text = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    total = sum([int(c) * multiplier for c, multiplier in zip(text, reversed(range(11)))])
    remainder = total % 11
    check_remainder = remainder == 0
    return check_remainder

UK_NHS = Entity(
    label="UK_NHS",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b([0-9]{4})\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["national health service", "nhs", "health services authority", "health authority"]}}], "score": 0.35},
    ],
)
