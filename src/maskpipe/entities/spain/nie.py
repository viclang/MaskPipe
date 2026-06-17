"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.spain.es_nie_recognizer.EsNieRecognizer."""
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
    pattern_text = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
    letter = pattern_text[-1]
    if not pattern_text[1:-1].isdigit or pattern_text[:1] not in 'XYZ':
        return False
    if len(pattern_text) < 8 or len(pattern_text) > 9:
        return False
    number = int(str('XYZ'.index(pattern_text[0])) + pattern_text[1:-1])
    return letter == letters[number % 23]

ES_NIE = Entity(
    label="ES_NIE",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[X-Z]?[0-9]?[0-9]{7}[-]?[A-Z]\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b[X-Z]?[0-9]?[0-9]{7}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b[A-Z]\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["número de identificación de extranjero", "nie"]}}], "score": 0.35},
    ],
)
