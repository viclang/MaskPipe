"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_passport_recognizer.UsPassportRecognizer."""
from maskpipe.entities.entity import Entity

US_PASSPORT = Entity(
    label="US_PASSPORT",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(\b[0-9]{9}\b)"}}]},
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(\b[A-Z][0-9]{8}\b)"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["us", "united", "states", "passport", "passport#", "travel", "document"]}}], "score": 0.35},
    ],
)
