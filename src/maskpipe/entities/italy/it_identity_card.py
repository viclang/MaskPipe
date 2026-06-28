"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_identity_card_recognizer.ItIdentityCardRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\s?\d{7}\b"}}]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b\d{7}[A-Z]{2}\b"}}]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\d{5}[A-Z]{2}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["carta", "identità", "elettronica", "cie", "documento", "riconoscimento", "espatrio"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

IT_IDENTITY_CARD = Entity(
    label="IT_IDENTITY_CARD",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
