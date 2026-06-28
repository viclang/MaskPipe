"""Parity tests: native maskpipe entities vs Presidio-converted equivalents.

These tests compare detection results between the native maskpipe implementation
and the Presidio recognizer converted via PresidioConverter. They document both
where the two agree and where they intentionally diverge (e.g. the native entity
has stricter validation than Presidio's regex-only approach).
"""
import pytest
from spacy.lang.en import English

from maskpipe import PipelineBuilder
from presidio_helpers import _convert_recognizer, skip_no_presidio
from presidio_converter import PresidioConverter

try:
    from presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer import UsSsnRecognizer
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False


def _build(entity):
    nlp = English()
    builder = PipelineBuilder(nlp, disable=["context_enhancer", "anonymizer"])
    builder.add_entities([entity])
    return nlp


def _detect(nlp, text):
    doc = nlp(text)
    return {s.text for s in doc.spans["sc"]}


# Valid SSNs — both implementations should detect these.
# Dot-separated ("401.22.3456") is a single token in spaCy, so both detect it.
# 9-digit no-separator is also a single token, so both detect it.
VALID_SSNS = [
    "532431234",    # 9-digit, no separator
    "401223456",    # 9-digit, no separator
    "401.22.3456",  # dot-separated — single token in spaCy
    "532.43.1234",  # dot-separated — single token in spaCy
]


# Valid SSNs that both implementations detect via multi-token patterns.
# PresidioConverter._translate_pattern expands [- .] separator classes into
# explicit hyphen-token and adjacent-token alternatives.
VALID_SSNS_MULTITOKEN = [
    "532-43-1234",  # hyphen-separated
    "401 22 3456",  # space-separated
]

# Numbers that pass the regex but are rejected by BOTH validators.
# Both native maskpipe and Presidio's invalidate_result reject these.
BOTH_REJECT = [
    "078051120",    # reserved test SSN
    "123456789",    # well-known test SSN
    "987654321",    # reserved (Presidio rejects; added to native after audit)
    "000123456",    # area code 000 invalid
    "666123456",    # area code 666 invalid
]

CLEARLY_NOT_SSN = [
    "Call me at 12-34-567",
    "No numbers here",
]


@pytest.fixture
def native_nlp():
    from maskpipe.entities.us.us_ssn import US_SSN
    return _build(US_SSN)


@pytest.fixture
def presidio_nlp():
    entity = _convert_recognizer(PresidioConverter(), UsSsnRecognizer())
    return _build(entity)


@skip_no_presidio
@pytest.mark.parametrize("text", VALID_SSNS)
def test_both_detect_valid_ssn(native_nlp, presidio_nlp, text):
    assert _detect(native_nlp, text), f"native missed: {text!r}"
    assert _detect(presidio_nlp, text), f"presidio missed: {text!r}"


@skip_no_presidio
@pytest.mark.parametrize("text", CLEARLY_NOT_SSN)
def test_neither_detects_non_ssn(native_nlp, presidio_nlp, text):
    assert not _detect(native_nlp, text), f"native false positive: {text!r}"
    assert not _detect(presidio_nlp, text), f"presidio false positive: {text!r}"


@skip_no_presidio
@pytest.mark.parametrize("text", BOTH_REJECT)
def test_both_reject_invalid_ssn(native_nlp, presidio_nlp, text):
    """Both implementations agree: these pass the regex but fail validation."""
    assert not _detect(native_nlp, text), f"native should reject: {text!r}"
    assert not _detect(presidio_nlp, text), f"presidio should reject: {text!r}"


@skip_no_presidio
@pytest.mark.parametrize("text", VALID_SSNS_MULTITOKEN)
def test_both_detect_multitoken_formats(native_nlp, presidio_nlp, text):
    """Both detect hyphen/space-separated SSNs via multi-token patterns.
    PresidioConverter expands [- .] separator classes into explicit token sequences."""
    assert _detect(native_nlp, text), f"native missed: {text!r}"
    assert _detect(presidio_nlp, text), f"presidio missed: {text!r}"
