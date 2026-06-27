"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.australia.au_medicare_recognizer.AuMedicareRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[2-6]\d{3}\s\d{5}\s\d\b"}}]},
    {"score": 0.1, "pattern": [
        {"TEXT": {"REGEX": r"\b[2-6]\d{3}\b"}},
        {"TEXT": {"REGEX": r"\b\d{5}\b"}},
        {"TEXT": {"REGEX": r"\b\d\b"}},
    ]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b[2-6]\d{9}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": "medicare"}], "score": 0.35},
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
    medicare_list = [int(digit) for digit in text if not digit.isspace()]
    weight = [1, 3, 7, 9, 1, 3, 7, 9]
    sum_product = 0
    for i in range(8):
        sum_product += medicare_list[i] * weight[i]
    remainder = sum_product % 10
    return remainder == medicare_list[8]
# END GENERATED: validator

AU_MEDICARE = Entity(
    label="AU_MEDICARE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
