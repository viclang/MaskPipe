"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_passport_recognizer.UkPassportRecognizer."""
from maskpipe.entities.entity import Entity

UK_PASSPORT = Entity(
    label="UK_PASSPORT",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z]{2}\d{7}\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["passport", "passport number", "travel document", "uk passport", "british passport", "her majesty", "his majesty", "hm passport", "hmpo"]}}], "score": 0.35},
    ],
)
