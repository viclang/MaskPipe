"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer.AuAbnRecognizer."""
from spacy.tokens import Span
from maskpipe.entities.entity import Entity
from maskpipe.entities.util import sanitize_value

def _validator(span: Span) -> bool:
    pattern_text = span.text
    text = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    abn_list = [int(digit) for digit in text if not digit.isspace()]
    weight = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    abn_list[0] = 9 if abn_list[0] == 0 else abn_list[0] - 1
    sum_product = 0
    for i in range(11):
        sum_product += abn_list[i] * weight[i]
    remainder = sum_product % 89
    return remainder == 0

AU_ABN = Entity(
    label="AU_ABN",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b\d{2}\s\d{3}\s\d{3}\s\d{3}\b"}}]},
        {"score": 0.1, "pattern": [
            {"TEXT": {"REGEX": r"\b\d{2}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
            {"TEXT": {"REGEX": r"\b\d{3}\b"}},
        ]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b\d{11}\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["australian business number", "abn"]}}], "score": 0.35},
    ],
)
