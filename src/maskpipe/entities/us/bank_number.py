"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_bank_recognizer.UsBankRecognizer."""
from maskpipe.entities.entity import Entity

US_BANK_NUMBER = Entity(
    label="US_BANK_NUMBER",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{8,17}\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["check", "account", "account#", "acct", "bank", "save", "debit"]}}], "score": 0.35},
    ],
)
