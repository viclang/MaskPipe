"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_voter_recognizer.InVoterRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]{1}[ABCDGHJKMNPRSYabcdghjkmnprsy]{1}[A-Za-z]{1}([0-9]){7})\b"}}]},
    {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b([A-Za-z]){3}([0-9]){7}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["voter", "epic"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "elector"}, {"LEMMA": "photo"}, {"LEMMA": "identity"}, {"LEMMA": "card"}], "score": 0.35},
]
# END GENERATED: context_patterns

IN_VOTER = Entity(
    label="IN_VOTER",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
