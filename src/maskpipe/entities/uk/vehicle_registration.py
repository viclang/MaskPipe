"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_vehicle_registration_recognizer.UkVehicleRegistrationRecognizer."""
from typing import List
from typing import Tuple
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _validator(span: Span) -> bool:

    def _sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
    pattern_text = span.text
    sanitized_value = _sanitize_value(pattern_text, [('-', ''), (' ', '')])
    if len(sanitized_value) == 7 and sanitized_value[:2].isalpha():
        age_id_str = sanitized_value[2:4]
        if age_id_str.isdigit():
            age_id = int(age_id_str)
            return 2 <= age_id <= 29 or 51 <= age_id <= 79
    return None

UK_VEHICLE_REGISTRATION = Entity(
    label="UK_VEHICLE_REGISTRATION",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b[A-HJ-PR-Y][A-HJ-PR-Y](?:0[1-9]|[1-7][0-9])[- ]?[A-HJ-PR-Z]{3}\b"}}]},
        {"score": 0.3, "pattern": [
            {"TEXT": {"REGEX": r"\b[A-HJ-PR-Y][A-HJ-PR-Y](?:0[1-9]|[1-7][0-9])\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b[A-HJ-PR-Z]{3}\b"}},
        ]},
        {"score": 0.2, "pattern": [{"TEXT": {"REGEX": r"\b[A-HJ-NPR-TV-Y]\d{1,3}[- ]?[A-HJ-PR-Y][A-HJ-PR-Z]{2}\b"}}]},
        {"score": 0.2, "pattern": [
            {"TEXT": {"REGEX": r"\b[A-HJ-NPR-TV-Y]\d{1,3}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b[A-HJ-PR-Y][A-HJ-PR-Z]{2}\b"}},
        ]},
        {"score": 0.15, "pattern": [{"TEXT": {"REGEX": r"\b[A-HJ-PR-Z]{3}[- ]?\d{1,3}[- ]?[A-HJ-NPR-TV-Y]\b"}}]},
        {"score": 0.15, "pattern": [
            {"TEXT": {"REGEX": r"\b[A-HJ-PR-Z]{3}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b\d{1,3}\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b[A-HJ-NPR-TV-Y]\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["vehicle", "registration", "number plate", "licence plate", "license plate", "reg", "vrn", "dvla", "v5c", "logbook", "mot", "car", "insured vehicle"]}}], "score": 0.35},
    ],
)
