"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_aadhaar_recognizer.InAadhaarRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.util import is_verhoeff_number, sanitize_value
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{12}\b"}}]},
    {"score": 0.01, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{4}[- :][0-9]{4}[- :][0-9]{4}\b"}}]},
    {"score": 0.01, "pattern": [
        {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
        {"TEXT": "-", "OP": "?"},
        {"TEXT": {"REGEX": r"\b[0-9]{4}\b"}},
    ]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["aadhaar", "uidai"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _is_palindrome(text: str, case_insensitive: bool=False) -> bool:
    palindrome_text = text
    if case_insensitive:
        palindrome_text = palindrome_text.replace(' ', '').lower()
    return palindrome_text == palindrome_text[::-1]

def _check_aadhaar(sanitized_value: str) -> bool:
    is_valid_aadhaar: bool = False
    if len(sanitized_value) == 12 and sanitized_value.isnumeric() is True and (int(sanitized_value[0]) >= 2) and (is_verhoeff_number(int(sanitized_value)) is True) and (_is_palindrome(sanitized_value) is False):
        is_valid_aadhaar = True
    return is_valid_aadhaar

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', ''), (':', '')])
    return bool(_check_aadhaar(sanitized_value))
# END GENERATED: validator

IN_AADHAAR = Entity(
    label="IN_AADHAAR",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
