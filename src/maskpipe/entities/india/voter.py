"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_voter_recognizer.InVoterRecognizer."""
from maskpipe.entities.entity import Entity

IN_VOTER = Entity(
    label="IN_VOTER",
    patterns=[
        {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{1}[ABCDGHJKMNPRSYabcdghjkmnprsy]{1}[A-Za-z]{1}([0-9]){7})\b"}}]},
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]){3}([0-9]){7}\b"}}]},
    ],
    validator=None,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["voter", "epic", "elector photo identity card"]}}], "score": 0.35},
    ],
)
