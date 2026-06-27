"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_pan_recognizer.InPanRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{3}[AaBbCcFfGgHhJjLlPpTt]{1}[A-Za-z]{1}[0-9]{4}[A-Za-z]{1})\b"}}]},
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{5}[0-9]{4}[A-Za-z]{1})\b"}}]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b((?=.*?[a-zA-Z])(?=.*?[0-9]{4})[\w@#$%^?~-]{10})\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["pan"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "permanent"}, {"LEMMA": "account"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

IN_PAN = Entity(
    label="IN_PAN",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
