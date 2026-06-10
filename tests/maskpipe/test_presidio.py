"""Tests for PresidioConverter (maskpipe[presidio-analyzer]).

Integration tests that require presidio-analyzer are skipped when
the package is not installed.
"""
import pytest
from unittest.mock import MagicMock
from spacy.lang.en import English

from maskpipe.presidio import PresidioConverter

try:
    from presidio_analyzer import Pattern, PatternRecognizer, EntityRecognizer
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False

skip_no_presidio = pytest.mark.skipif(not HAS_PRESIDIO, reason="presidio-analyzer not installed")


# --- Unit tests (no presidio required) ---

def test_translate_pattern_wraps_regex():
    converter = PresidioConverter()
    patterns = converter._translate_pattern(r"\b\d{9}\b", 0.5)
    assert len(patterns) == 1
    assert patterns[0]["score"] == 0.5
    assert patterns[0]["pattern"] == [{"TEXT": {"REGEX": r"\b\d{9}\b"}}]


def test_translate_context_returns_none_when_empty():
    converter = PresidioConverter()
    assert converter._translate_context([]) is None
    assert converter._translate_context(None) is None


def test_translate_context_uses_context_boost():
    converter = PresidioConverter(context_boost=0.4)
    result = converter._translate_context(["ssn", "social security"])
    assert result is not None
    assert len(result) == 1
    assert result[0]["score"] == 0.4
    assert result[0]["pattern"] == [{"LEMMA": {"IN": ["ssn", "social security"]}}]


# --- Integration tests (require presidio-analyzer) ---

@skip_no_presidio
def test_convert_pattern_recognizer_produces_entity():
    class SimpleRecognizer(PatternRecognizer):
        PATTERNS = [Pattern("test", r"\b\d{9}\b", 0.5)]
        CONTEXT = ["test", "number"]

        def __init__(self):
            super().__init__(supported_entity="TEST_NUM", patterns=self.PATTERNS, context=self.CONTEXT)

    entity = PresidioConverter().convert(SimpleRecognizer())

    assert entity.label == "TEST_NUM"
    assert entity.patterns is not None
    assert len(entity.patterns) == 1
    assert entity.patterns[0]["score"] == 0.5
    assert entity.context_patterns is not None
    assert entity.validator is None  # no validate_result override


@skip_no_presidio
def test_convert_pattern_recognizer_with_validator():
    class ValidatedRecognizer(PatternRecognizer):
        PATTERNS = [Pattern("test", r"\b\d{9}\b", 0.5)]
        CONTEXT = []

        def __init__(self):
            super().__init__(supported_entity="VALIDATED", patterns=self.PATTERNS, context=self.CONTEXT)

        def validate_result(self, pattern_text: str):
            return pattern_text.isdigit()

    entity = PresidioConverter().convert(ValidatedRecognizer())
    assert entity.validator is not None

    nlp = English()
    doc = nlp("123456789")
    span = doc[0:1]
    assert entity.validator(span) is True


@skip_no_presidio
def test_convert_all_returns_list():
    class R1(PatternRecognizer):
        def __init__(self):
            super().__init__(supported_entity="E1", patterns=[Pattern("p", r"\d+", 0.5)])

    class R2(PatternRecognizer):
        def __init__(self):
            super().__init__(supported_entity="E2", patterns=[Pattern("p", r"[A-Z]+", 0.3)])

    entities = PresidioConverter().convert_all([R1(), R2()])
    assert len(entities) == 2
    assert entities[0].label == "E1"
    assert entities[1].label == "E2"


@skip_no_presidio
def test_convert_au_abn_recognizer():
    from presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer import AuAbnRecognizer

    entity = PresidioConverter().convert(AuAbnRecognizer())

    assert entity.label == "AU_ABN"
    assert entity.patterns is not None
    assert entity.validator is not None
    assert entity.context_patterns is not None


@skip_no_presidio
def test_au_abn_validator_rejects_invalid():
    from presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer import AuAbnRecognizer

    entity = PresidioConverter().convert(AuAbnRecognizer())

    nlp = English()
    doc = nlp("00000000000")
    span = doc[0:1]
    assert entity.validator(span) is False


@skip_no_presidio
def test_convert_uk_nhs_recognizer():
    from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nhs_recognizer import NhsRecognizer

    entity = PresidioConverter().convert(NhsRecognizer())

    assert entity.label == "UK_NHS"
    assert entity.validator is not None


@skip_no_presidio
def test_custom_context_boost():
    class SimpleRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="CUSTOM",
                patterns=[Pattern("p", r"\d+", 0.5)],
                context=["custom", "id"],
            )

    entity = PresidioConverter(context_boost=0.5).convert(SimpleRecognizer())
    assert entity.context_patterns[0]["score"] == 0.5
