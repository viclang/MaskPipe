"""Parity tests: native maskpipe entities vs Presidio-converted equivalents.

These tests compare detection results between the native maskpipe implementation
and the Presidio recognizer converted via PresidioConverter. They document both
where the two agree and where they intentionally diverge (e.g. the native entity
has stricter validation than Presidio's regex-only approach).
"""
import pytest
from spacy.lang.en import English

from maskpipe import PipelineBuilder
from maskpipe.presidio import PresidioConverter

try:
    from presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer import UsSsnRecognizer
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False

skip_no_presidio = pytest.mark.skipif(not HAS_PRESIDIO, reason="presidio-analyzer not installed")


def _build(entity):
    nlp = English()
    builder = PipelineBuilder(nlp, disable=["context_enhancer", "anonymizer"])
    builder.add_entities([entity])
    return nlp


def _detect(nlp, text):
    doc = nlp(text)
    return {s.text for s in doc.spans["sc"]}


# Valid SSNs — both implementations should detect these.
# Note: hyphenated ("123-45-6789") and space-separated ("123 45 6789") formats
# are NOT included — spaCy's English tokenizer splits on hyphens and spaces,
# so neither implementation detects them via single-token patterns.
# Dot-separated ("401.22.3456") works because spaCy keeps it as one token.
VALID_SSNS = [
    "532431234",    # 9-digit, no separator
    "401223456",    # 9-digit, no separator
    "401.22.3456",  # dot-separated — single token in spaCy
    "532.43.1234",  # dot-separated — single token in spaCy
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

# Numbers that native maskpipe rejects but Presidio does not.
# Presidio's invalidate_result doesn't check area codes 900-999.
NATIVE_STRICTER = [
    "912345678",    # area 900+ — invalid per SSA; maskpipe rejects, Presidio doesn't
]

CLEARLY_NOT_SSN = [
    "Call me at 12-34-567",
    "No numbers here",
]


@pytest.fixture
def native_nlp():
    from maskpipe.entities.us.ssn import SSN
    return _build(SSN)


@pytest.fixture
def presidio_nlp():
    entity = PresidioConverter().convert(UsSsnRecognizer())
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
@pytest.mark.parametrize("text", NATIVE_STRICTER)
def test_native_stricter_than_presidio(native_nlp, presidio_nlp, text):
    """Native maskpipe is stricter: rejects area codes 900-999 (Presidio does not)."""
    assert not _detect(native_nlp, text), f"native should reject: {text!r}"
    assert _detect(presidio_nlp, text), f"presidio should accept: {text!r}"
