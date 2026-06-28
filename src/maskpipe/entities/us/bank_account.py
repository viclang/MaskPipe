"""US Bank Account Number entity.

Recognizes US bank account numbers (8-17 digits).
Note: Bank account numbers are inherently weak matches as they
overlap with other numeric patterns. Context patterns are essential.
"""
from spacy.tokens import Span

from ..entity import Entity

def _valid_bank_account(span: Span) -> bool:
    """Basic validation for bank account numbers."""
    text = span.text.strip()
    only_digits = "".join(c for c in text if c.isdigit())
    # Must be 8-17 digits
    return 8 <= len(only_digits) <= 17

US_BANK_ACCOUNT = Entity(
    label="US_BANK_ACCOUNT",
    patterns=[
        # Weak: 8-17 consecutive digits
        {
            "score": 0.3,
            "pattern": [
                {"TEXT": {"REGEX": r"\b\d{8,17}\b"}},
            ],
        },
    ],
    validator=_valid_bank_account,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "bank"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "account"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "acct"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "checking"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "debit"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "savings"}}]},
    ],
)
