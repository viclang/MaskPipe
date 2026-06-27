"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.australia.au_acn_recognizer.AuAcnRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b\d{3}\s\d{3}\s\d{3}\b"}}]},
    {"score": 0.1, "pattern": [
        {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        {"TEXT": {"REGEX": r"\b\d{3}\b"}},
    ]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b\d{9}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": "acn"}], "score": 0.35},
    {"pattern": [{"LEMMA": "australian"}, {"LEMMA": "company"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    text = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    acn_list = [int(digit) for digit in text if not digit.isspace()]
    weight = [8, 7, 6, 5, 4, 3, 2, 1]
    sum_product = 0
    for i in range(8):
        sum_product += acn_list[i] * weight[i]
    remainder = sum_product % 10
    complement = 10 - remainder
    return complement == acn_list[-1]
# END GENERATED: validator

AU_ACN = Entity(
    label="AU_ACN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
