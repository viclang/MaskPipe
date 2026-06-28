"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_itin_recognizer.UsItinRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
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
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

US_ITIN = Entity(
    label="US_ITIN",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
