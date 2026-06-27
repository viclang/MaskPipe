"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_vat_code.ItVatCodeRecognizer."""

# BEGIN GENERATED: imports
from typing import List, Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b([0-9][ _]?){11}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["piva", "pi"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "partita"}, {"LEMMA": "iva"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
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
# END GENERATED: validator

IT_VAT_CODE = Entity(
    label="IT_VAT_CODE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
