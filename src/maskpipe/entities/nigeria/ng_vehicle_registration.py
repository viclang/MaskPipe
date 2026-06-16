"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.nigeria.ng_vehicle_registration_recognizer.NgVehicleRegistrationRecognizer."""
from maskpipe.entities.entity import Entity

NG_VEHICLE_REGISTRATION = Entity(
    label="NG_VEHICLE_REGISTRATION",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z]{3}[- ]?\d{3}[A-Z]{2}\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b[A-Z]{3}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b\d{3}[A-Z]{2}\b"}},
        ]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["plate number", "vehicle registration", "license plate", "number plate", "plate", "vehicle", "registration"]}}], "score": 0.35},
    ],
)
