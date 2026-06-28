"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_passport_recognizer.UsPassportRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(\b[0-9]{9}\b)"}}]},
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(\b[A-Z][0-9]{8}\b)"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["us", "united", "states", "passport", "passport#", "travel", "document"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

US_PASSPORT = Entity(
    label="US_PASSPORT",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
