"""Entity generated from presidio_analyzer.predefined_recognizers.generic.mac_recognizer.MacAddressRecognizer."""
from spacy.tokens import Span
import re
from maskpipe.entities.entity import Entity

def _invalidate(pattern_text: str) -> bool:
    cleaned = re.sub('[:\\-.]', '', pattern_text)
    if re.fullmatch('[0-9A-Fa-f]{12}', cleaned) is None:
        return True
    if cleaned.upper() == 'FFFFFFFFFFFF' or cleaned.upper() == '000000000000':
        return True
    return False

def _validator(span: Span) -> bool:
    if _invalidate(span.text):
        return False
    return True

MAC_ADDRESS = Entity(
    label="MAC_ADDRESS",
    patterns=[
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}\b"}}]},
        {"score": 0.6, "pattern": [{"TEXT": {"REGEX": r"\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["mac", "mac address", "hardware address", "physical address", "ethernet"]}}], "score": 0.35},
    ],
)
