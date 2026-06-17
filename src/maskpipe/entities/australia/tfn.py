"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.australia.au_tfn_recognizer.AuTfnRecognizer."""
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
    tfn_list = [int(digit) for digit in text if not digit.isspace()]
    weight = [1, 4, 3, 7, 5, 8, 6, 9, 10]
    sum_product = 0
    for i in range(9):
        sum_product += tfn_list[i] * weight[i]
    remainder = sum_product % 11
    return remainder == 0

AU_TFN = Entity(
    label="AU_TFN",
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
        {"pattern": [{"LEMMA": {"IN": ["tax file number", "tfn"]}}], "score": 0.35},
    ],
)
