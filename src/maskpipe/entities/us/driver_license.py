"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_driver_license_recognizer.UsLicenseRecognizer."""
from maskpipe.entities.entity import Entity

US_DRIVER_LICENSE = Entity(
    label="US_DRIVER_LICENSE",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\b"}}]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{6,14}|[0-9]{16})\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["driver", "license", "permit", "lic", "identification", "dls", "cdls", "lic#", "driving"]}}], "score": 0.35},
    ],
)
