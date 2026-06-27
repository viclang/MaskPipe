"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.nigeria.ng_vehicle_registration_recognizer.NgVehicleRegistrationRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z]{3}[- ]?\d{3}[A-Z]{2}\b"}}]},
    {"score": 0.5, "pattern": [
        {"TEXT": {"REGEX": r"\b[A-Z]{3}\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b\d{3}[A-Z]{2}\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["plate", "vehicle", "registration"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "plate"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "vehicle"}, {"LEMMA": "registration"}], "score": 0.35},
    {"pattern": [{"LEMMA": "license"}, {"LEMMA": "plate"}], "score": 0.35},
    {"pattern": [{"LEMMA": "number"}, {"LEMMA": "plate"}], "score": 0.35},
]
# END GENERATED: context_patterns

NG_VEHICLE_REGISTRATION = Entity(
    label="NG_VEHICLE_REGISTRATION",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
