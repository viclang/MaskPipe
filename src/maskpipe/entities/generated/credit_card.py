"""Entity generated from presidio_analyzer.predefined_recognizers.generic.credit_card_recognizer.CreditCardRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:

    def _luhn_checksum(sanitized_value: str) -> bool:

        def digits_of(n: str) -> List[int]:
            return [int(dig) for dig in str(n)]
        digits = digits_of(sanitized_value)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10 == 0

    def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    checksum = _luhn_checksum(sanitized_value)
    return checksum

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
