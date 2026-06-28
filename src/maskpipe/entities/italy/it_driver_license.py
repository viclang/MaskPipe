"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_driver_license_recognizer.ItDriverLicenseRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.2, "pattern": [{"TEXT": {"REGEX": r"\b(?i)(([A-Z]{2}\d{7}[A-Z])|(U1[BCDEFGHLJKMNPRSTUWYXZ0-9]{7}[A-Z]))\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["patente", "licenza"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "patente"}, {"LEMMA": "di"}, {"LEMMA": "guida"}], "score": 0.35},
    {"pattern": [{"LEMMA": "licenza"}, {"LEMMA": "di"}, {"LEMMA": "guida"}], "score": 0.35},
]
# END GENERATED: context_patterns

IT_DRIVER_LICENSE = Entity(
    label="IT_DRIVER_LICENSE",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
