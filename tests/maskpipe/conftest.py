"""Shared test fixtures and helpers for maskpipe tests."""
import copy
from dataclasses import dataclass

import pytest
from spacy.language import Language

from maskpipe import PipelineBuilder
from maskpipe.entities.entity import Entity

try:
    from presidio_analyzer import EntityRecognizer as _PresidioRecognizer
    from maskpipe.presidio import PresidioConverter
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False

skip_no_presidio = pytest.mark.skipif(not HAS_PRESIDIO, reason="presidio-analyzer not installed")


def _build_pipeline(entity: Entity, nlp: Language, disable=("context_enhancer", "anonymizer")):
    PipelineBuilder(nlp, disable=list(disable)).add_entities([entity])
    return nlp


def _detect(nlp, text: str) -> set[str]:
    return {s.text for s in nlp(text).spans["sc"]}


@dataclass
class ParityResult:
    """Detection result comparing a native entity against a Presidio recognizer."""
    native: set[str]
    presidio: set[str]

    @property
    def matches(self) -> bool:
        return self.native == self.presidio

    @property
    def only_native(self) -> set[str]:
        return self.native - self.presidio

    @property
    def only_presidio(self) -> set[str]:
        return self.presidio - self.native


class PresidioParityHelper:
    """Test helper that compares a native maskpipe Entity against a Presidio recognizer.

    Pass a Presidio recognizer instance and a native Entity; call ``compare(text)``
    to get a ``ParityResult`` showing what each side detected.

    Usage::

        helper = PresidioParityHelper(UsSsnRecognizer(), SSN)
        result = helper.compare("532-43-1234")
        assert result.matches

        result = helper.compare("912-34-5678")
        assert result.only_native == set()     # native rejects it
        assert result.only_presidio == {"912-34-5678"}  # presidio accepts it

    Requires presidio-analyzer to be installed; guard tests with ``skip_no_presidio``.
    """

    def __init__(self, presidio_recognizer, native_entity: Entity, nlp: Language):
        if not HAS_PRESIDIO:
            raise RuntimeError("presidio-analyzer is not installed")
        converted = PresidioConverter().convert(presidio_recognizer)
        self._presidio_nlp = _build_pipeline(converted, copy.deepcopy(nlp))
        self._native_nlp = _build_pipeline(native_entity, nlp)

    def compare(self, text: str) -> ParityResult:
        return ParityResult(
            native=_detect(self._native_nlp, text),
            presidio=_detect(self._presidio_nlp, text),
        )
