"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.italy.it_passport_recognizer.ItPassportRecognizer."""
from maskpipe.entities.entity import Entity

IT_PASSPORT = Entity(
    label="IT_PASSPORT",
    patterns=[
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"(?i)\b[A-Z]{2}\d{7}\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["passaporto", "elettronico", "italiano", "viaggio", "viaggiare", "estero", "documento", "dogana"]}}], "score": 0.35},
    ],
)
