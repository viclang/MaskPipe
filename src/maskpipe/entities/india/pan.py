"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_pan_recognizer.InPanRecognizer."""
from maskpipe.entities.entity import Entity

IN_PAN = Entity(
    label="IN_PAN",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{3}[AaBbCcFfGgHhJjLlPpTt]{1}[A-Za-z]{1}[0-9]{4}[A-Za-z]{1})\b"}}]},
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{5}[0-9]{4}[A-Za-z]{1})\b"}}]},
        {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b((?=.*?[a-zA-Z])(?=.*?[0-9]{4})[\w@#$%^?~-]{10})\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["permanent account number", "pan"]}}], "score": 0.35},
    ],
)
