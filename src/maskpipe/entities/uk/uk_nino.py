"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nino_recognizer.UkNinoRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b(?!bg|gb|nk|kn|nt|tn|zz|BG|GB|NK|KN|NT|TN|ZZ) ?([a-ceghj-pr-tw-zA-CEGHJ-PR-TW-Z]{1}[a-ceghj-npr-tw-zA-CEGHJ-NPR-TW-Z]{1}) ?([0-9]{2}) ?([0-9]{2}) ?([0-9]{2}) ?([a-dA-D{1}])\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["nino"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "national"}, {"LEMMA": "insurance"}], "score": 0.35},
    {"pattern": [{"LEMMA": "ni"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

UK_NINO = Entity(
    label="UK_NINO",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
