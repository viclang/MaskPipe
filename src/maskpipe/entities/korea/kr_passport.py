"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_passport_recognizer.KrPassportRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(?<![A-Z0-9a-z])[MmSsRrOoDd]\d{3}[A-Za-z]\d{4}(?![0-9])"}}]},
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<![A-Z0-9a-z])[MmSsRrOoDd]\d{8}(?![0-9])"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["여권", "passport"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "passport"}], "score": 0.35},
    {"pattern": [{"LEMMA": "korean"}, {"LEMMA": "passport"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "대한민국"}, {"LEMMA": "여권"}], "score": 0.35},
    {"pattern": [{"LEMMA": "passport"}, {"LEMMA": "number"}], "score": 0.35},
]
# END GENERATED: context_patterns

KR_PASSPORT = Entity(
    label="KR_PASSPORT",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
