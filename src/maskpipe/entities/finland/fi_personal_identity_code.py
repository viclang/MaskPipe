"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.finland.fi_personal_identity_code_recognizer.FiPersonalIdentityCodeRecognizer."""
from datetime import datetime
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

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

FI_PERSONAL_IDENTITY_CODE = Entity(
    label="FI_PERSONAL_IDENTITY_CODE",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"\b(\d{6})([+-ABCDEFYXWVU])(\d{3})([0123456789ABCDEFHJKLMNPRSTUVWXY])\b"}}]},
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"(\d{6})([+-ABCDEFYXWVU])(\d{3})([0123456789ABCDEFHJKLMNPRSTUVWXY])"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["hetu", "henkilötunnus", "personbeteckningen", "personal identity code"]}}], "score": 0.35},
    ],
)
