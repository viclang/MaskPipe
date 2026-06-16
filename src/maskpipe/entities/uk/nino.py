"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nino_recognizer.UkNinoRecognizer."""
from maskpipe.entities.entity import Entity

UK_NINO = Entity(
    label="UK_NINO",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b(?!bg|gb|nk|kn|nt|tn|zz|BG|GB|NK|KN|NT|TN|ZZ) ?([a-ceghj-pr-tw-zA-CEGHJ-PR-TW-Z]{1}[a-ceghj-npr-tw-zA-CEGHJ-NPR-TW-Z]{1}) ?([0-9]{2}) ?([0-9]{2}) ?([0-9]{2}) ?([a-dA-D{1}])\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["national insurance", "ni number", "nino"]}}], "score": 0.35},
    ],
)
