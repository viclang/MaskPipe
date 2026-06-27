"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_passport_recognizer.UkPassportRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z]{2}\d{7}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["passport", "hmpo"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "passport"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "travel"}, {"LEMMA": "document"}], "score": 0.35},
    {"pattern": [{"LEMMA": "uk"}, {"LEMMA": "passport"}], "score": 0.35},
    {"pattern": [{"LEMMA": "british"}, {"LEMMA": "passport"}], "score": 0.35},
    {"pattern": [{"LEMMA": "her"}, {"LEMMA": "majesty"}], "score": 0.35},
    {"pattern": [{"LEMMA": "his"}, {"LEMMA": "majesty"}], "score": 0.35},
    {"pattern": [{"LEMMA": "hm"}, {"LEMMA": "passport"}], "score": 0.35},
]
# END GENERATED: context_patterns

UK_PASSPORT = Entity(
    label="UK_PASSPORT",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
