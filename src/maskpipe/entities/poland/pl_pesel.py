"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.poland.pl_pesel_recognizer.PlPeselRecognizer."""

# BEGIN GENERATED: imports
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.4, "pattern": [{"TEXT": {"REGEX": "[0-9]{2}([02468][1-9]|[13579][012])(0[1-9]|1[0-9]|2[0-9]|3[01])[0-9]{5}"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["pesel"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    digits = [int(digit) for digit in pattern_text]
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum((digit * weight for digit, weight in zip(digits[:10], weights)))
    checksum %= 10
    return checksum == digits[10]
# END GENERATED: validator

PL_PESEL = Entity(
    label="PL_PESEL",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
