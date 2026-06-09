from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

from spacy.tokens import Doc, Span

from maskpipe.entities.entity import ContextPattern, Entity, Pattern

if TYPE_CHECKING:
    from presidio_analyzer import EntityRecognizer, PatternRecognizer


class PresidioConverter:
    """Convert Presidio recognizers to maskpipe Entity objects.

    Supports both PatternRecognizer (translated to spaCy token patterns)
    and EntityRecognizer (bridged via custom_matcher using analyze()).

    Requires: pip install maskpipe[presidio]

    Args:
        context_boost: Score added to context_patterns. Default 0.35.
        alignment_mode: char_span alignment for EntityRecognizer bridge.
            One of "strict", "contract", "expand". Default "expand".
        min_score: Minimum score to include results from EntityRecognizer.
    """

    def __init__(
        self,
        context_boost: float = 0.35,
        alignment_mode: str = "expand",
        min_score: float = 0.0,
    ) -> None:
        self.context_boost = context_boost
        self.alignment_mode = alignment_mode
        self.min_score = min_score

    def convert(self, recognizer: "EntityRecognizer") -> Entity:
        """Convert a Presidio recognizer to a maskpipe Entity."""
        try:
            from presidio_analyzer import PatternRecognizer
        except ImportError:
            raise ImportError(
                "presidio-analyzer is required. "
                "Install with: pip install maskpipe[presidio]"
            )

        if isinstance(recognizer, PatternRecognizer):
            return self._convert_pattern_recognizer(recognizer)
        return self._convert_entity_recognizer(recognizer)

    def convert_all(self, recognizers: List["EntityRecognizer"]) -> List[Entity]:
        """Convert a list of Presidio recognizers to maskpipe Entity objects."""
        return [self.convert(r) for r in recognizers]

    def _convert_pattern_recognizer(self, recognizer: "PatternRecognizer") -> Entity:
        patterns: List[Pattern] = []
        for p in recognizer.patterns:
            patterns.extend(self._translate_pattern(p.regex, p.score))

        context_patterns = self._translate_context(recognizer.context)
        validator = self._wrap_validator(recognizer)

        return Entity(
            label=recognizer.supported_entities[0],
            patterns=patterns or None,
            validator=validator,
            context_patterns=context_patterns,
        )

    def _translate_pattern(self, regex: str, score: float) -> List[Pattern]:
        """Translate a Presidio regex string to maskpipe Pattern dicts.

        Override this method to customise translation for specific patterns.
        """
        return [{"pattern": [{"TEXT": {"REGEX": regex}}], "score": score}]

    def _wrap_validator(self, recognizer: "PatternRecognizer") -> Optional[Callable[[Span], bool]]:
        from presidio_analyzer import PatternRecognizer as PR

        # Presidio has two separate validation hooks that are both called in analyze():
        # - validate_result: positive validation (returns True/False/None)
        # - invalidate_result: negative validation (returns True to discard)
        # They don't chain through each other, so we must call both.
        has_validate = type(recognizer).validate_result is not PR.validate_result
        has_invalidate = type(recognizer).invalidate_result is not PR.invalidate_result
        if not has_validate and not has_invalidate:
            return None

        def _validator(span: Span, _r: "PatternRecognizer" = recognizer) -> bool:
            if _r.invalidate_result(span.text):
                return False
            result = _r.validate_result(span.text)
            return result if result is not None else True

        return _validator

    def _translate_context(
        self, context: Optional[List[str]]
    ) -> Optional[List[ContextPattern]]:
        if not context:
            return None
        return [{"pattern": [{"LOWER": {"IN": list(context)}}], "score": self.context_boost}]

    def _convert_entity_recognizer(self, recognizer: "EntityRecognizer") -> Entity:
        entities = recognizer.supported_entities
        alignment_mode = self.alignment_mode
        min_score = self.min_score

        def _matcher(doc: Doc) -> List[Tuple[int, int, float]]:
            results = recognizer.analyze(doc.text, entities=entities, nlp_artifacts=None)
            spans = []
            for r in results:
                if r.score < min_score:
                    continue
                span = doc.char_span(r.start, r.end, alignment_mode=alignment_mode)
                if span:
                    spans.append((span.start, span.end, r.score))
            return spans

        return Entity(
            label=recognizer.supported_entities[0],
            custom_matcher=_matcher,
        )
