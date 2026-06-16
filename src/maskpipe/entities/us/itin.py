"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_itin_recognizer.UsItinRecognizer."""
from maskpipe.entities.entity import Entity

US_ITIN = Entity(
    label="US_ITIN",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b9\d{2}[- ](5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))\d{4}\b|\b9\d{2}(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))[- ]\d{4}\b"}}]},
        {"score": 0.05, "pattern": [
            {"TEXT": {"REGEX": r"\b9\d{2}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))\d{4}\b|\b9\d{2}(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b\d{4}\b"}},
        ]},
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b9\d{2}(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))\d{4}\b"}}]},
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b9\d{2}[- ](5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))[- ]\d{4}\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b9\d{2}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b\d{4}\b"}},
        ]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"]}}], "score": 0.35},
    ],
)
