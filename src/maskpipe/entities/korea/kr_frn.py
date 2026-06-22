"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_frn_recognizer.KrFrnRecognizer."""

from spacy.tokens import Span
from maskpipe.entities.entity import Entity
from maskpipe.entities.util import sanitize_value

def _validate_region_code(region_code: int) -> bool:
    return bool(True if 0 <= region_code <= 95 else False)

def _validate_checksum(frn: str) -> bool:
    digit_sum = super()._compute_checksum(frn)
    checksum = (13 - digit_sum % 11) % 10
    return checksum == int(frn[12])

def sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def _validator(span: Span) -> bool:
    pattern_text = span.text
    sanitized_value = sanitize_value(pattern_text, [('-', '')])
    if len(sanitized_value) != 13:
        return False
    if not sanitized_value.isdigit():
        return False
    region_code = int(sanitized_value[7:9])
    if _validate_region_code(region_code) and _validate_checksum(sanitized_value):
        return True
    return None

KR_FRN = Entity(
    label="KR_FRN",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": r"(?<!\d)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(-?)[5-8]\d{6}(?!\d)"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["외국인등록번호", "korean frn", "frn", "foreigner registration number", "korean foreigner registration number", "외국인번호"]}}], "score": 0.35},
    ],
)
