"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.india.in_gstin_recognizer.InGstinRecognizer."""
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _sanitize_value(text: str) -> str:
    import re
    gstin_pattern = '\\b((?:0[1-9]|[1-3][0-7])[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}[0-9A-Za-z]{1}Z[0-9A-Za-z]{1})\\b'
    match = re.search(gstin_pattern, text.upper())
    if match:
        return match.group(1)
    sanitized = text.upper()
    for old, new in [('-', ''), (' ', '')]:
        sanitized = sanitized.replace(old, new)
    return sanitized

def _validate_pan_format(pan: str) -> bool:
    if len(pan) != 10:
        return False
    first_five = pan[:5]
    letter_count = sum((1 for c in first_five if c.isalpha()))
    if letter_count < 3:
        return False
    if not pan[5:9].isdigit():
        return False
    if not pan[9].isalpha():
        return False
    return True

def _validate_gstin(gstin: str) -> bool:
    if len(gstin) != 15:
        return False
    state_code = gstin[:2]
    if not state_code.isdigit() or not 1 <= int(state_code) <= 37:
        return False
    pan_part = gstin[2:12]
    if not _validate_pan_format(pan_part):
        return False
    reg_number = gstin[12]
    if not reg_number.isalnum():
        return False
    if gstin[13] != 'Z':
        return False
    checksum = gstin[14]
    if not checksum.isalnum():
        return False
    return True

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text)
    return bool(_validate_gstin(sanitized_value))

IN_GSTIN = Entity(
    label="IN_GSTIN",
    patterns=[
        {"score": 0.8, "pattern": [{"TEXT": {"REGEX": r"\b((?:0[1-9]|[1-3][0-7])[A-Za-z0-9]{10}[A-Za-z0-9]{1}Z[A-Za-z0-9]{1})\b"}}]},
        {"score": 0.4, "pattern": [{"TEXT": {"REGEX": r"\b((?:0[1-9]|[1-3][0-7])[A-Za-z0-9]{11}Z[A-Za-z0-9]{1})\b"}}]},
        {"score": 0.1, "pattern": [{"TEXT": {"REGEX": r"\b([0-9]{2}[A-Za-z0-9]{11}Z[A-Za-z0-9]{1})\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["gstin", "gst", "goods and services tax", "tax identification", "gst number", "gst registration"]}}], "score": 0.35},
    ],
)
