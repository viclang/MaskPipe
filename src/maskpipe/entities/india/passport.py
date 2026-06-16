"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_passport_recognizer.InPassportRecognizer."""
from maskpipe.entities.entity import Entity

IN_PASSPORT = Entity(
    label="IN_PASSPORT",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b[A-Z][1-9]\d\s?\d{4}[1-9]\b"}}]},
        {"score": 0.1, "pattern": [
            {"TEXT": {"REGEX": r"\b[A-Z][1-9]\d\b"}},
            {"TEXT": {"REGEX": r"\b\d{4}[1-9]\b"}},
        ]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["passport", "indian passport", "passport number"]}}], "score": 0.35},
    ],
)
