"""Entity generated from presidio_analyzer.predefined_recognizers.generic.mac_recognizer.MacAddressRecognizer."""
import re
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:
    pattern_text = span.text
    cleaned = re.sub('[:\\-.]', '', pattern_text)
    if re.fullmatch('[0-9A-Fa-f]{12}', cleaned) is None:
        return False
    if cleaned.upper() == 'FFFFFFFFFFFF' or cleaned.upper() == '000000000000':
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
