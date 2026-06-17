"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.spain.es_nif_recognizer.EsNifRecognizer."""
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
    pattern_text = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    letter = pattern_text[-1]
    number = int(''.join(filter(str.isdigit, pattern_text)))
    letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
    return letter == letters[number % 23]

ES_NIF = Entity(
    label="ES_NIF",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]?[0-9]{7}[-]?[A-Z]\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b[0-9]?[0-9]{7}\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b[A-Z]\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["documento nacional de identidad", "dni", "nif", "identificación"]}}], "score": 0.35},
    ],
)
