"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_fin_recognizer.SgFinRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"(?i)(\b[A-Z][0-9]{7}[A-Z]\b)"}}]},
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"(?i)(\b[STFGM][0-9]{7}[A-Z]\b)"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["fin", "fin#", "nric", "nric#"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

SG_NRIC_FIN = Entity(
    label="SG_NRIC_FIN",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
