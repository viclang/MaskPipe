"""Entity generated from presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_uen_recognizer.SgUenRecognizer."""
from spacy.tokens import Span
from datetime import date
from typing import Optional
from maskpipe.entities.entity import Entity

def _validate_uen_format_a(uen: str) -> bool:
    check_digit = uen[-1]
    weighted_sum = sum((int(n) * w for n, w in zip(uen[:-1], (10, 4, 9, 3, 8, 2, 7, 1))))
    checksum = 'XMKECAWLJDB'[weighted_sum % 11]
    return check_digit == checksum

def _validate_uen_format_c(uen: str) -> bool:
    check_digit = uen[-1]
    if uen[0] not in {'T', 'R', 'S'}:
        return False
    entity_type = uen[3:5]
    if entity_type not in {'HS', 'FN', 'CH', 'DP', 'XL', 'PB', 'PF', 'CL', 'GB', 'CC', 'CS', 'SM', 'CX', 'MQ', 'LP', 'RF', 'GS', 'VH', 'FM', 'CD', 'PA', 'CM', 'MM', 'CP', 'MC', 'GA', 'MH', 'MB', 'LL', 'MD', 'NB', 'FB', 'TU', 'NR', 'SS', 'TC', 'RP', 'FC', 'HC'}:
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

SG_UEN = Entity(
    label="SG_UEN",
    patterns=[
        {"score": 0.3, "pattern": [{"TEXT": {"REGEX": r"\b\d{8}[A-Z]\b|\b\d{9}[A-Z]\b|\b(T|S)\d{2}[A-Z]{2}\d{4}[A-Z]\b"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["uen", "unique entity number", "business registration", "acra"]}}], "score": 0.35},
    ],
)
