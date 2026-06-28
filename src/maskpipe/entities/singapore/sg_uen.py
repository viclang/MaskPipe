"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_uen_recognizer.SgUenRecognizer."""

# BEGIN GENERATED: imports
from datetime import date
from spacy.tokens import Span
from maskpipe.entities.entity import ContextPattern, Entity, Pattern
# END GENERATED: imports

# BEGIN GENERATED: patterns
_PATTERNS: list[Pattern] = [
    {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b\d{8}[A-Z]\b|\b\d{9}[A-Z]\b|\b(T|S)\d{2}[A-Z]{2}\d{4}[A-Z]\b"}}]},
]
# END GENERATED: patterns

# BEGIN GENERATED: context_patterns
_CONTEXT_PATTERNS: list[ContextPattern] = [
    {"pattern": [{"LEMMA": {"IN": ["uen", "acra"]}}], "score": 0.35},
    {"pattern": [{"LEMMA": "unique"}, {"LEMMA": "entity"}, {"LEMMA": "number"}], "score": 0.35},
    {"pattern": [{"LEMMA": "business"}, {"LEMMA": "registration"}], "score": 0.35},
]
# END GENERATED: context_patterns

# BEGIN GENERATED: validator
def _validate_uen_format_a(uen: str) -> bool:
    check_digit = uen[-1]
    weighted_sum = sum((int(n) * w for n, w in zip(uen[:-1], (10, 4, 9, 3, 8, 2, 7, 1))))
    checksum = 'XMKECAWLJDB'[weighted_sum % 11]
    return check_digit == checksum

def _validate_uen_format_c(uen: str) -> bool:
    check_digit = uen[-1]
    if uen[0] not in {'R', 'S', 'T'}:
        return False
    entity_type = uen[3:5]
    if entity_type not in {'CC', 'CD', 'CH', 'CL', 'CM', 'CP', 'CS', 'CX', 'DP', 'FB', 'FC', 'FM', 'FN', 'GA', 'GB', 'GS', 'HC', 'HS', 'LL', 'LP', 'MB', 'MC', 'MD', 'MH', 'MM', 'MQ', 'NB', 'NR', 'PA', 'PB', 'PF', 'RF', 'RP', 'SM', 'SS', 'TC', 'TU', 'VH', 'XL'}:
        return False
    weighted_sum = sum(('ABCDEFGHJKLMNPQRSTUVWX0123456789'.index(n) * w for n, w in zip(uen[:-1], (4, 3, 5, 3, 10, 2, 2, 5, 7))))
    checksum = 'ABCDEFGHJKLMNPQRSTUVWX0123456789'[(weighted_sum - 5) % 11]
    return check_digit == checksum

def _validate_uen_format_b(uen: str) -> bool:
    check_digit = uen[-1]
    year_of_registration = int(uen[0:4])
    if year_of_registration > date.today().year:
        return False
    weighted_sum = sum((int(n) * w for n, w in zip(uen[:-1], (10, 8, 6, 4, 9, 7, 5, 3, 1))))
    checksum = 'ZKCMDNERGWH'[weighted_sum % 11]
    return check_digit == checksum

def _validator(span: Span) -> bool:
    pattern_text = span.text
    if len(pattern_text) == 9:
        return _validate_uen_format_a(pattern_text)
    elif len(pattern_text) == 10 and pattern_text[0].isalpha():
        return _validate_uen_format_c(pattern_text)
    elif len(pattern_text) == 10:
        return _validate_uen_format_b(pattern_text)
    return False
# END GENERATED: validator

SG_UEN = Entity(
    label="SG_UEN",
    patterns=_PATTERNS,
    validator=_validator,
    context_patterns=_CONTEXT_PATTERNS,
)
