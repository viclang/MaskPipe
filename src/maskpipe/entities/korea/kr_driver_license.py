"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_driver_license_recognizer.KrDriverLicenseRecognizer."""

from spacy.tokens import Span
from maskpipe.entities.entity import Entity
from maskpipe.entities.util import sanitize_value

def sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', ''), (' ', '')])
    if len(sanitized_value) != 12:
        return False
    if not sanitized_value.isdigit():
        return False
    region_code = sanitized_value[:2]
    if region_code not in {'20', '14', '19', '11', '26', '15', '23', '25', '28', '18', '21', '17', '12', '13', '24', '16', '22'}:
        return False
    return True

KR_DRIVER_LICENSE = Entity(
    label="KR_DRIVER_LICENSE",
    patterns=[
        {"score": 0.05, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)(\d{2})[- ]?(\d{2})[- ]?(\d{6})[- ]?(\d{2})(?!\d)"}}]},
        {"score": 0.05, "pattern": [
            {"TEXT": {"REGEX": r"\b(?<!\d)(\d{2})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{2})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{6})\b"}},
            {"TEXT": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"\b(\d{2})(?!\d)\b"}},
        ]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["운전면허", "운전면허번호", "면허번호", "korean driver license", "korean driver's license"]}}], "score": 0.35},
    ],
)
