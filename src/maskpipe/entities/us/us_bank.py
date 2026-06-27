"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.us.us_bank_recognizer.UsBankRecognizer."""

# BEGIN GENERATED: imports
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"\b[0-9]{8,17}\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["check", "account", "account#", "acct", "bank", "save", "debit"]}}], "score": 0.35},
]
# END GENERATED: context_patterns

US_BANK_NUMBER = Entity(
    label="US_BANK_NUMBER",
    patterns=_PATTERNS,
    validator=None,
    context_patterns=_CONTEXT_PATTERNS,
)
