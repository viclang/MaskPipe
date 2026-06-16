"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_driver_license_recognizer.ItDriverLicenseRecognizer."""
from maskpipe.entities.entity import Entity

IT_DRIVER_LICENSE = Entity(
    label="IT_DRIVER_LICENSE",
    patterns=[
        {"score": 0.2, "pattern": [{"TEXT": {"REGEX": r"\b(?i)(([A-Z]{2}\d{7}[A-Z])|(U1[BCDEFGHLJKMNPRSTUWYXZ0-9]{7}[A-Z]))\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["patente", "patente di guida", "licenza", "licenza di guida"]}}], "score": 0.35},
    ],
)
