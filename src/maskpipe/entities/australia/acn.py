"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.australia.au_acn_recognizer.AuAcnRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    text = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    acn_list = [int(digit) for digit in text if not digit.isspace()]
    weight = [8, 7, 6, 5, 4, 3, 2, 1]
    sum_product = 0
    for i in range(8):
        sum_product += acn_list[i] * weight[i]
    remainder = sum_product % 10
    complement = 10 - remainder
    return complement == acn_list[-1]

AU_ACN = Entity(
    label="AU_ACN",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b\d{3}\s\d{3}\s\d{3}\b"}}]},
        {"score": 0.1, "pattern": [
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        ]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b\d{9}\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["australian company number", "acn"]}}], "score": 0.35},
    ],
)
