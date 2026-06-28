"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.spain.es_nie_recognizer.EsNieRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[X-Z]?[0-9]?[0-9]{7}[-]?[A-Z]\b"}}]},
    {"score": 0.5, "pattern": [
        {"TEXT": {"REGEX": r"\b[X-Z]?[0-9]?[0-9]{7}\b"}},
        {"TEXT": "-"},
        {"TEXT": {"REGEX": r"\b[A-Z]\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": "nie"}], "score": 0.35},
    {"pattern": [{"LEMMA": "número"}, {"LEMMA": "de"}, {"LEMMA": "identificación"}, {"LEMMA": "de"}, {"LEMMA": "extranjero"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    pattern_text = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
    letter = pattern_text[-1]
    if not pattern_text[1:-1].isdigit or pattern_text[:1] not in 'XYZ':
        return False
    if len(pattern_text) < 8 or len(pattern_text) > 9:
        return False
    number = int(str('XYZ'.index(pattern_text[0])) + pattern_text[1:-1])
    return letter == letters[number % 23]
# END GENERATED: validator

ES_NIE = Entity(
    label="ES_NIE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
