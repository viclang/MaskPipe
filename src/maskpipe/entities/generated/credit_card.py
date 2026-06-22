"""Entity generated from presidio_analyzer.predefined_recognizers.generic.credit_card_recognizer.CreditCardRecognizer."""
from spacy.tokens import Span
from maskpipe.entities.entity import Entity
from maskpipe.entities.util import sanitize_value, luhn_checksum

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    return luhn_checksum(sanitized_value)

CREDIT_CARD = Entity(
    label="CREDIT_CARD",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b(?!1\d{12}(?!\d))((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b"}}]},
        {"score": 0.3, "pattern": [
            {"TEXT": {"REGEX": r"\b(?!1\d{12}(?!\d))((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{3,4})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{3,4})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{3,5})\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["credit", "card", "visa", "mastercard", "cc ", "amex", "discover", "jcb", "diners", "maestro", "instapayment"]}}], "score": 0.35},
    ],
)
