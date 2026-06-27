"""Entity generated from presidio_analyzer.predefined_recognizers.generic.mac_recognizer.MacAddressRecognizer."""

# BEGIN GENERATED: imports
import re
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}\b"}}]},
    {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["mac", "ethernet"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "mac"}, {"LEMMA": "address"}], "score": 0.35},
    {"pattern": [{"LEMMA": "hardware"}, {"LEMMA": "address"}], "score": 0.35},
    {"pattern": [{"LEMMA": "physical"}, {"LEMMA": "address"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    cleaned = re.sub('[:\\-.]', '', pattern_text)
    if re.fullmatch('[0-9A-Fa-f]{12}', cleaned) is None:
        return False
    if cleaned.upper() == 'FFFFFFFFFFFF' or cleaned.upper() == '000000000000':
        return False
    return True
# END GENERATED: validator

MAC_ADDRESS = Entity(
    label="MAC_ADDRESS",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
