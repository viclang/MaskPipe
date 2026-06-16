"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_fin_recognizer.SgFinRecognizer."""
from maskpipe.entities.entity import Entity

SG_NRIC_FIN = Entity(
    label="SG_NRIC_FIN",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"(?i)(\b[A-Z][0-9]{7}[A-Z]\b)"}}]},
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"(?i)(\b[STFGM][0-9]{7}[A-Z]\b)"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["fin", "fin#", "nric", "nric#"]}}], "score": 0.35},
    ],
)
