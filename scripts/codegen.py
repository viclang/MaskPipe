"""ECS pipeline: Presidio recognizer → RecognizerEntity → Python source.

Each component is a pure-data dataclass. Each system attaches one component.
render.py consumes the entity; this file knows nothing about formatting.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TypeVar

from presidio_converter import PresidioConverter
from presidio_analyzer import EntityRecognizer, PatternRecognizer

from extractor import extract_custom_matcher, extract_validator
from maskpipe.entities.entity import ContextPattern, Pattern

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Components — one dataclass per concern, pure data
# ---------------------------------------------------------------------------

@dataclass
class IdentityComponent:
    label: str
    var_name: str
    module: str
    class_name: str


@dataclass
class PatternsComponent:
    patterns: list[Pattern]


@dataclass
class ContextComponent:
    context_patterns: list[ContextPattern]


@dataclass
class ValidatorComponent:
    src: str
    imports: list[str]


@dataclass
class ValidatorTodoComponent:
    """Attached when validator logic exists in Presidio but could not be extracted."""
    methods: list[str]


@dataclass
class AnalyzeComponent:
    src: str
    imports: list[str]
    alignment_mode: str


# ---------------------------------------------------------------------------
# Entity — typed component container
# ---------------------------------------------------------------------------

class RecognizerEntity:
    def __init__(self) -> None:
        self._components: dict[type, Any] = {}

    def attach(self, component: Any) -> "RecognizerEntity":
        self._components[type(component)] = component
        return self

    def get(self, component_type: type[T]) -> T | None:
        return self._components.get(component_type)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Systems — each attaches one component
# ---------------------------------------------------------------------------

def _attach_identity(recognizer: EntityRecognizer, entity: RecognizerEntity) -> None:
    label = recognizer.supported_entities[0]
    entity.attach(IdentityComponent(
        label=label,
        var_name=label.replace("-", "_"),
        module=type(recognizer).__module__,
        class_name=type(recognizer).__name__,
    ))


def _attach_context(recognizer: EntityRecognizer, converter: PresidioConverter, entity: RecognizerEntity) -> None:
    cp = converter.translate_context(getattr(recognizer, "context", None))
    if cp:
        entity.attach(ContextComponent(context_patterns=cp))


def _attach_patterns(recognizer: PatternRecognizer, converter: PresidioConverter, entity: RecognizerEntity) -> None:
    patterns = []
    for p in recognizer.patterns:
        patterns.extend(converter.translate_pattern(p.regex, p.score))
    entity.attach(PatternsComponent(patterns=patterns))


def _attach_validator(recognizer: PatternRecognizer, entity: RecognizerEntity) -> None:
    result = extract_validator(recognizer)
    if result is not None:
        src, imports = result
        entity.attach(ValidatorComponent(src=src, imports=imports))
        return
    methods = []
    if type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result:
        methods.append("invalidate_result")
    if type(recognizer).validate_result is not PatternRecognizer.validate_result:
        methods.append("validate_result")
    if methods:
        entity.attach(ValidatorTodoComponent(methods=methods))


def _attach_analyze(recognizer: EntityRecognizer, converter: PresidioConverter, entity: RecognizerEntity) -> None:
    src, imports = extract_custom_matcher(recognizer)
    entity.attach(AnalyzeComponent(src=src, imports=imports, alignment_mode=converter.alignment_mode))


GENERATED_MARKER = '"""Entity generated from presidio_analyzer.'


# ---------------------------------------------------------------------------
# Build — run applicable systems over a recognizer
# ---------------------------------------------------------------------------

def _build(recognizer: EntityRecognizer, converter: PresidioConverter) -> RecognizerEntity:
    entity = RecognizerEntity()
    _attach_identity(recognizer, entity)
    _attach_context(recognizer, converter, entity)
    if isinstance(recognizer, PatternRecognizer):
        _attach_patterns(recognizer, converter, entity)
        _attach_validator(recognizer, entity)
    else:
        _attach_analyze(recognizer, converter, entity)
    return entity


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(recognizer: EntityRecognizer, converter: PresidioConverter) -> str:
    from render import render
    return render(_build(recognizer, converter))
