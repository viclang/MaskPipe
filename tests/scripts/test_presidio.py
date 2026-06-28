"""Tests for PresidioConverter (maskpipe[presidio-analyzer]).

Integration tests that require presidio-analyzer are skipped when
the package is not installed.
"""
import pytest
from spacy.lang.en import English

from presidio_helpers import _convert_recognizer, skip_no_presidio
from presidio_converter import PresidioConverter

try:
    from presidio_analyzer import Pattern, PatternRecognizer
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False


# --- Unit tests (no presidio required) ---

def test_translate_pattern_wraps_regex():
    converter = PresidioConverter()
    patterns = converter.translate_pattern(r"\b\d{9}\b", 0.5)
    assert len(patterns) == 1
    assert patterns[0]["score"] == 0.5
    assert patterns[0]["pattern"] == [{"TEXT": {"REGEX": r"\b\d{9}\b"}}]


def test_translate_context_returns_none_when_empty():
    converter = PresidioConverter()
    assert converter.translate_context([]) is None
    assert converter.translate_context(None) is None


def test_translate_context_uses_context_boost():
    converter = PresidioConverter(context_boost=0.4)
    result = converter.translate_context(["ssn", "social security"])
    assert result is not None
    assert len(result) == 2
    # single word → LEMMA pattern
    assert result[0]["score"] == 0.4
    assert result[0]["pattern"] == [{"LEMMA": "ssn"}]
    # multi-word phrase → per-token LEMMA pattern
    assert result[1]["score"] == 0.4
    assert result[1]["pattern"] == [{"LEMMA": "social"}, {"LEMMA": "security"}]


# --- Integration tests (require presidio-analyzer) ---

@skip_no_presidio
def test_convert_pattern_recognizer_produces_entity():
    class SimpleRecognizer(PatternRecognizer):
        PATTERNS = [Pattern("test", r"\b\d{9}\b", 0.5)]
        CONTEXT = ["test", "number"]

        def __init__(self):
            super().__init__(supported_entity="TEST_NUM", patterns=self.PATTERNS, context=self.CONTEXT)

    entity = _convert_recognizer(PresidioConverter(), SimpleRecognizer())

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

    entity = _convert_recognizer(PresidioConverter(), ValidatedRecognizer())
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

    entities = [_convert_recognizer(PresidioConverter(), r) for r in [R1(), R2()]]
    assert len(entities) == 2
    assert entities[0].label == "E1"
    assert entities[1].label == "E2"


@skip_no_presidio
def test_convert_au_abn_recognizer():
    from presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer import AuAbnRecognizer

    entity = _convert_recognizer(PresidioConverter(), AuAbnRecognizer())

    assert entity.label == "AU_ABN"
    assert entity.patterns is not None
    assert entity.validator is not None
    assert entity.context_patterns is not None


@skip_no_presidio
def test_au_abn_validator_rejects_invalid():
    from presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer import AuAbnRecognizer

    entity = _convert_recognizer(PresidioConverter(), AuAbnRecognizer())

    nlp = English()
    doc = nlp("00000000000")
    span = doc[0:1]
    assert entity.validator(span) is False


@skip_no_presidio
def test_convert_uk_nhs_recognizer():
    from presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nhs_recognizer import NhsRecognizer

    entity = _convert_recognizer(PresidioConverter(), NhsRecognizer())

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

    entity = _convert_recognizer(PresidioConverter(context_boost=0.5), SimpleRecognizer())
    assert entity.context_patterns[0]["score"] == 0.5
