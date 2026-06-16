"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_passport_recognizer.KrPassportRecognizer."""
from maskpipe.entities.entity import Entity

KR_PASSPORT = Entity(
    label="KR_PASSPORT",
    patterns=[
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(?<![A-Z0-9a-z])[MmSsRrOoDd]\d{3}[A-Za-z]\d{4}(?![0-9])"}}]},
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<![A-Z0-9a-z])[MmSsRrOoDd]\d{8}(?![0-9])"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["korean passport", "korean passport number", "대한민국 여권", "여권", "passport", "passport number"]}}], "score": 0.35},
    ],
)
