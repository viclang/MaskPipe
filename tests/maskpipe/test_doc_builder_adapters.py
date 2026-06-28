"""Tests for DocBuilder model-specific adapter methods."""
import maskpipe  # registers spaCy extensions
from spacy.lang.en import English

from maskpipe.doc_builder import DocBuilder

TEXT = "John lives in Amsterdam"


def _nlp():
    return English()


def test_with_transformers_creates_span():
    entities = [{"start": 0, "end": 4, "entity_group": "PERSON", "score": 0.85}]
    doc = DocBuilder(_nlp(), TEXT).with_transformers(entities).build()
    assert len(doc.spans["sc"]) == 1
    span = doc.spans["sc"][0]
    assert span.text == "John"
    assert span.label_ == "PERSON"
    assert span._.score == 0.85


def test_with_gliner2_uses_confidence_as_score():
    result = {"PERSON": {"start": 0, "end": 4, "text": "John", "confidence": 0.88}}
    doc = DocBuilder(_nlp(), TEXT).with_gliner2(result).build()
    assert len(doc.spans["sc"]) == 1
    span = doc.spans["sc"][0]
    assert span.text == "John"
    assert span.label_ == "PERSON"
    assert span._.score == 0.88


def test_with_openmed_calls_to_dict_and_maps_confidence():
    class FakePredictionResult:
        def to_dict(self):
            return {"entities": [{"start": 0, "end": 4, "label": "PERSON", "confidence": 0.75}]}

    doc = DocBuilder(_nlp(), TEXT).with_openmed(FakePredictionResult()).build()
    assert len(doc.spans["sc"]) == 1
    span = doc.spans["sc"][0]
    assert span.text == "John"
    assert span.label_ == "PERSON"
    assert span._.score == 0.75


def test_build_batch_transformers_maps_entity_group():
    texts = ["John lives here", "Amsterdam is nice"]
    entities_list = [
        [{"start": 0, "end": 4, "entity_group": "PERSON", "score": 0.9}],
        [{"start": 0, "end": 9, "entity_group": "GPE", "score": 0.8}],
    ]
    docs = list(DocBuilder.build_batch_transformers(_nlp(), texts, entities_list))
    assert docs[0].spans["sc"][0].label_ == "PERSON"
    assert docs[1].spans["sc"][0].label_ == "GPE"


def test_build_batch_gliner2_maps_per_item():
    texts = ["John lives here", "Amsterdam is nice"]
    entities_list = [
        {"PERSON": {"start": 0, "end": 4, "text": "John", "confidence": 0.9}},
        {"GPE": {"start": 0, "end": 9, "text": "Amsterdam", "confidence": 0.8}},
    ]
    docs = list(DocBuilder.build_batch_gliner2(_nlp(), texts, entities_list))
    assert docs[0].spans["sc"][0].label_ == "PERSON"
    assert docs[1].spans["sc"][0].label_ == "GPE"


def test_with_gliner_creates_span():
    entities = [{"start": 0, "end": 4, "text": "John", "label": "PERSON", "score": 0.9}]
    doc = DocBuilder(_nlp(), TEXT).with_gliner(entities).build()
    assert len(doc.spans["sc"]) == 1
    span = doc.spans["sc"][0]
    assert span.text == "John"
    assert span.label_ == "PERSON"
    assert span._.score == 0.9
