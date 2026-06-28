"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_passport_recognizer.InPassportRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z][1-9]\d\s?\d{4}[1-9]\b"}}]},
    {"score": 0.1, "pattern": [
        {"TEXT": {"REGEX": r"\b[A-Z][1-9]\d\b"}},
        {"TEXT": {"REGEX": r"\b\d{4}[1-9]\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": "passport"}], "score": 0.35},
    {"pattern": [{"LEMMA": "indian"}, {"LEMMA": "passport"}], "score": 0.35},
    {"pattern": [{"LEMMA": "passport"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

IN_PASSPORT = Entity(
    label="IN_PASSPORT",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
