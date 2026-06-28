"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_passport_recognizer.ItPassportRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\d{7}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["passaporto", "elettronico", "italiano", "viaggio", "viaggiare", "estero", "documento", "dogana"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

IT_PASSPORT = Entity(
    label="IT_PASSPORT",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
