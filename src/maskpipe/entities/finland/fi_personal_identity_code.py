"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.finland.fi_personal_identity_code_recognizer.FiPersonalIdentityCodeRecognizer."""

# BEGIN GENERATED: imports
from datetime import datetime
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b(\d{6})([+-ABCDEFYXWVU])(\d{3})([0123456789ABCDEFHJKLMNPRSTUVWXY])\b"}}]},
    {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(\d{6})([+-ABCDEFYXWVU])(\d{3})([0123456789ABCDEFHJKLMNPRSTUVWXY])"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["hetu", "henkilötunnus", "personbeteckningen"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "personal"}, {"LEMMA": "identity"}, {"LEMMA": "code"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validator(span: Span) -> bool:
    pattern_text = span.text
    if len(pattern_text) != 11:
        return False
    date_part = pattern_text[0:6]
    try:
        datetime.strptime(date_part, '%d%m%y')
    except ValueError:
        return False
    individual_number = pattern_text[7:10]
    control_character = pattern_text[-1]
    valid_control_characters = '0123456789ABCDEFHJKLMNPRSTUVWXY'
    number_to_check = int(date_part + individual_number)
    return valid_control_characters[number_to_check % 31] == control_character
# END GENERATED: validator

FI_PERSONAL_IDENTITY_CODE = Entity(
    label="FI_PERSONAL_IDENTITY_CODE",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
