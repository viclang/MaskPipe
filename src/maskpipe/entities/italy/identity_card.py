"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_identity_card_recognizer.ItIdentityCardRecognizer."""
from maskpipe.entities.entity import Entity

IT_IDENTITY_CARD = Entity(
    label="IT_IDENTITY_CARD",
    patterns=[
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\s?\d{7}\b"}}]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b\d{7}[A-Z]{2}\b"}}]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\d{5}[A-Z]{2}\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["carta", "identità", "elettronica", "cie", "documento", "riconoscimento", "espatrio"]}}], "score": 0.35},
    ],
)
