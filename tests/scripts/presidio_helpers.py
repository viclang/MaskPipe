"""Shared fixtures and helpers for scripts/ tests (require presidio-analyzer)."""
import sys
from pathlib import Path

import pytest
from spacy.tokens import Span

from maskpipe.entities.entity import Entity

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

try:
    from presidio_analyzer import PatternRecognizer
    from presidio_converter import PresidioConverter
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False

skip_no_presidio = pytest.mark.skipif(not HAS_PRESIDIO, reason="presidio-analyzer not installed")


def _convert_recognizer(converter: "PresidioConverter", recognizer: "PatternRecognizer") -> Entity:
    """Convert a Presidio PatternRecognizer to a maskpipe Entity using translation primitives."""
    patterns = []
    for p in recognizer.patterns:
        patterns.extend(converter.translate_pattern(p.regex, p.score))

    has_validate = type(recognizer).validate_result is not PatternRecognizer.validate_result
    has_invalidate = type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result
    validator = None
    if has_validate or has_invalidate:
        _r = recognizer
        def validator(span: Span, _r=_r) -> bool:
            if _r.invalidate_result(span.text):
                return False
            result = _r.validate_result(span.text)
            return result if result is not None else True

    return Entity(
        label=recognizer.supported_entities[0],
        patterns=patterns or None,
        validator=validator,
        context_patterns=converter.translate_context(recognizer.context),
    )
