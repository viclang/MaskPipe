"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_vat_code.ItVatCodeRecognizer."""
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
    text = _sanitize_value(pattern_text, [('-', ''), (' ', ''), ('_', '')])
    if text == '00000000000':
        return False
    x = 0
    y = 0
    for i in range(0, 5):
        x += int(text[2 * i])
        tmp_y = int(text[2 * i + 1]) * 2
        if tmp_y > 9:
            tmp_y = tmp_y - 9
        y += tmp_y
    t = (x + y) % 10
    c = (10 - t) % 10
    if c == int(text[10]):
        result = True
    else:
        result = False
    return result

IT_VAT_CODE = Entity(
    label="IT_VAT_CODE",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b([0-9][ _]?){11}\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["piva", "partita iva", "pi"]}}], "score": 0.35},
    ],
)
