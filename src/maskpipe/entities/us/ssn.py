"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer.UsSsnRecognizer."""
from collections import defaultdict
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:
    pattern_text = span.text
    delimiter_counts = defaultdict(int)
    for c in pattern_text:
        if c in ('.', '-', ' '):
            delimiter_counts[c] += 1
    if len(delimiter_counts.keys()) > 1:
        return False
    only_digits = ''.join((c for c in pattern_text if c.isdigit()))
    if all((only_digits[0] == c for c in only_digits)):
        return False
    if only_digits[3:5] == '00' or only_digits[5:] == '0000':
        return False
    for sample_ssn in ('000', '666', '123456789', '98765432', '078051120'):
        if only_digits.startswith(sample_ssn):
            return False
    return True

US_SSN = Entity(
    label="US_SSN",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{5})-([0-9]{4})\b"}}]},
        {"score": 0.05, "pattern": [
            {"TEXT": {"REGEX": r"\b([0-9]{5})\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b([0-9]{4})\b"}},
        ]},
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{3})-([0-9]{6})\b"}}]},
        {"score": 0.05, "pattern": [
            {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
            {"TEXT": "-"},
            {"TEXT": {"REGEX": r"\b([0-9]{6})\b"}},
        ]},
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b(([0-9]{3})-([0-9]{2})-([0-9]{4}))\b"}}]},
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{9}\b"}}]},
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{3})[- .]([0-9]{2})[- .]([0-9]{4})\b"}}]},
        {"score": 0.5, "pattern": [
            {"TEXT": {"REGEX": r"\b([0-9]{3})\b"}},
            {"TEXT": {"IN": ["-", "."]}, "OP": "?"},
            {"TEXT": {"REGEX": r"\b([0-9]{2})\b"}},
            {"TEXT": {"IN": ["-", "."]}, "OP": "?"},
            {"TEXT": {"REGEX": r"\b([0-9]{4})\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["social", "security", "ssn", "ssns", "ssid"]}}], "score": 0.35},
    ],
)
