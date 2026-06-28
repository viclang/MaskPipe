"""Integration tests for DocBuilder adapter methods using real model packages.

Each test is skipped when the required package is not installed.
Install all with: uv sync --group dev
"""
import pytest
from spacy.lang.en import English

from maskpipe.doc_builder import DocBuilder

TEXT = "John Smith works at Google in New York."


def _nlp():
    return English()


# --- GLiNER ---

try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

skip_no_gliner = pytest.mark.skipif(not HAS_GLINER, reason="gliner not installed")


@skip_no_gliner
def test_with_gliner_integration():
    model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
    entities = model.predict_entities(TEXT, ["person", "organization", "location"])
    doc = DocBuilder(_nlp(), TEXT).with_gliner(entities).build()
    spans = doc.spans["sc"]
    assert len(spans) > 0
    assert all(isinstance(s.label_, str) and s.label_ for s in spans)
    assert all(0.0 <= s._.score <= 1.0 for s in spans)


# --- HuggingFace Transformers ---

try:
    from transformers import pipeline as hf_pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

skip_no_transformers = pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")


@skip_no_transformers
def test_with_transformers_integration():
    ner = hf_pipeline("ner", model="dslim/distilbert-NER", aggregation_strategy="simple")
    entities = ner(TEXT)
    doc = DocBuilder(_nlp(), TEXT).with_transformers(entities).build()
    spans = doc.spans["sc"]
    assert len(spans) > 0
    assert all(isinstance(s.label_, str) and s.label_ for s in spans)
    assert all(0.0 <= s._.score <= 1.0 for s in spans)


# --- GLiNER2 ---

try:
    from gliner2 import GLiNER2
    HAS_GLINER2 = True
except ImportError:
    HAS_GLINER2 = False

skip_no_gliner2 = pytest.mark.skipif(not HAS_GLINER2, reason="gliner2 not installed")


@skip_no_gliner2
def test_with_gliner2_integration():
    model = GLiNER2.from_pretrained("fastino/gliner2-base-v1")
    result = model.extract_entities(
        TEXT,
        ["person", "organization", "location"],
        include_confidence=True,
        include_spans=True,
    )
    doc = DocBuilder(_nlp(), TEXT).with_gliner2(result).build()
    spans = doc.spans["sc"]
    assert len(spans) > 0
    assert all(isinstance(s.label_, str) and s.label_ for s in spans)
    assert all(0.0 <= s._.score <= 1.0 for s in spans)


# --- OpenMed ---

try:
    from openmed import extract_pii
    HAS_OPENMED = True
except ImportError:
    HAS_OPENMED = False

skip_no_openmed = pytest.mark.skipif(not HAS_OPENMED, reason="openmed not installed")


@skip_no_openmed
def test_with_openmed_integration():
    result = extract_pii(TEXT, "OpenMed/OpenMed-PII-ClinicalE5-Small-33M-v1")
    doc = DocBuilder(_nlp(), TEXT).with_openmed(result).build()
    spans = doc.spans["sc"]
    assert len(spans) > 0
    assert all(isinstance(s.label_, str) and s.label_ for s in spans)
    assert all(0.0 <= s._.score <= 1.0 for s in spans)
