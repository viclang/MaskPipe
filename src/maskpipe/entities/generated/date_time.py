"""Entity generated from presidio_analyzer.predefined_recognizers.generic.date_recognizer.DateRecognizer."""
from maskpipe.entities.entity import Entity

DATE_TIME = Entity(
    label="DATE_TIME",
    patterns=[
        {"score": 0.8, "pattern": [{"TEXT": {"REGEX": r"\b(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|1[0-2])/([1-9]|0[1-9]|[1-2][0-9]|3[0-1])/(\d{4}|\d{2}))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])/([1-9]|0[1-9]|1[0-2])/(\d{4}|\d{2}))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(\d{4}/([1-9]|0[1-9]|1[0-2])/([1-9]|0[1-9]|[1-2][0-9]|3[0-1]))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-\d{4})\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-([1-9]|0[1-9]|1[0-2])-\d{4})\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(\d{4}-([1-9]|0[1-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1]))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])\.([1-9]|0[1-9]|1[0-2])\.(\d{4}|\d{2}))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-(\d{4}|\d{2}))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b((JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-(\d{4}|\d{2}))\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))\b"}}]},
        {"score": 0.2, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|1[0-2])/\d{4})\b"}}]},
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b(([1-9]|0[1-9]|1[0-2])/\d{2})\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["date", "birthday"]}}], "score": 0.35},
    ],
)
