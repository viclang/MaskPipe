from __future__ import annotations

import re
from typing import Callable, List, Optional, Tuple

from spacy.tokens import Doc, Span

from maskpipe.entities.entity import ContextPattern, Entity, Pattern

try:
    from presidio_analyzer import EntityRecognizer, PatternRecognizer
except ImportError:
    raise ImportError(
        "presidio-analyzer is required to use presidio_converter. "
        "Install with: uv sync --group codegen"
    )


class PresidioConverter:
    """Convert Presidio recognizers to maskpipe Entity objects.

    Supports both PatternRecognizer (translated to spaCy token patterns)
    and EntityRecognizer (bridged via custom_matcher using analyze()).

    Requires: uv sync --group codegen

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

    def convert(self, recognizer: EntityRecognizer) -> Entity:
        """Convert a Presidio recognizer to a maskpipe Entity."""
        if isinstance(recognizer, PatternRecognizer):
            return self._convert_pattern_recognizer(recognizer)
        return self._convert_entity_recognizer(recognizer)

    def convert_all(self, recognizers: List[EntityRecognizer]) -> List[Entity]:
        """Convert a list of Presidio recognizers to maskpipe Entity objects."""
        return [self.convert(r) for r in recognizers]

    def _convert_pattern_recognizer(self, recognizer: PatternRecognizer) -> Entity:
        patterns: List[Pattern] = []
        for p in recognizer.patterns:
            patterns.extend(self.translate_pattern(p.regex, p.score))

        context_patterns = self.translate_context(recognizer.context)
        validator = self._wrap_validator(recognizer)

        return Entity(
            label=recognizer.supported_entities[0],
            patterns=patterns or None,
            validator=validator,
            context_patterns=context_patterns,
        )

    # Matches separator char classes that cause spaCy's tokenizer to split:
    #   Group 1: char class with leading hyphen [- .], space [a b], or slash [/.]
    #            (leading hyphen = literal, not a range like [0-9] or [a-z])
    #   Group 2: \s whitespace escape
    # The trailing \?? in each alternative consumes an optional ? quantifier
    # (e.g. [- ]? or \s?) so it doesn't end up dangling in the regex parts.
    _SEP_CLASS = re.compile(
        r"(\[(?:-[^\]]*|[^\]]* [^\]]*|[^\]]*/[^\]]*)\])\??"  # char class with -, space, or /
        r"|(\\s)\??"                                            # \s whitespace escape
    )
    # Used to mask char classes when scanning for bare literal separators.
    _CC_MASK = re.compile(r"\[[^\]]*\]")
    _MARKER = "\x00"

    def translate_pattern(self, regex: str, score: float) -> List[Pattern]:
        """Translate a Presidio regex to one or two maskpipe Pattern dicts.

        Always produces the original as a single-token pattern (covers tokenizers
        that keep the string together, e.g. nl/es/pt for hyphens).

        When separators are detected, also produces one multi-token pattern:
        each segment is a separate token and the separator is an optional token
        (``OP: "?"`` when space is in the separator class, required otherwise).
        This single multi-token pattern covers all split-tokenizer cases.

        If the split produces unbalanced regex fragments (e.g. from an outer
        capturing group), the multi-token variant is silently skipped.
        """
        single = Pattern(pattern=[{"TEXT": {"REGEX": regex}}], score=score)
        sep_matches = list(self._SEP_CLASS.finditer(regex))

        if sep_matches:
            parts, has_hyphen, has_space, has_dot, has_slash = self._split_at_matches(regex, sep_matches)
        else:
            # Fallback: scan for literal - or / outside character classes.
            # Masking replaces [...] with \x00 of the same length so positions
            # stay stable; any - or / found afterwards is outside a char class.
            masked = self._CC_MASK.sub(lambda m: self._MARKER * len(m.group()), regex)
            lit = [(m.start(), m.group()) for m in re.finditer(r"(?<!\\)[-/]", masked)]
            if not lit:
                return [single]
            positions = [pos for pos, _ in lit]
            first_sep = lit[0][1]
            has_hyphen, has_space, has_dot, has_slash = first_sep == "-", False, False, first_sep == "/"
            parts = self._split_at_positions(regex, positions)

        bounded = [self._word_bounded(p) for p in parts]
        if not self._all_valid(*bounded):
            return [single]

        # Build the optional separator token.
        # Space is implicit (no token between adjacent space-separated words),
        # so only -, . and / need an explicit separator token.
        sep_chars = [c for c, flag in [("-", has_hyphen), (".", has_dot), ("/", has_slash)] if flag]
        opt = {"OP": "?"} if has_space else {}
        if len(sep_chars) == 1:
            sep_token: dict = {"TEXT": sep_chars[0], **opt}
        elif sep_chars:
            sep_token = {"TEXT": {"IN": sep_chars}, **opt}
        else:
            sep_token = {}

        tokens: List[dict] = []
        for part in bounded[:-1]:
            tokens.append({"TEXT": {"REGEX": part}})
            if sep_token:
                tokens.append(sep_token)
        tokens.append({"TEXT": {"REGEX": bounded[-1]}})

        return [single, Pattern(pattern=tokens, score=score)]

    @staticmethod
    def _split_at_matches(regex: str, matches: list) -> tuple:
        """Split regex at separator match positions; return (parts, has_hyphen, has_space, has_dot, has_slash)."""
        has_hyphen = has_space = has_dot = has_slash = False
        parts: List[str] = []
        prev = 0
        for m in matches:
            parts.append(regex[prev:m.start()])
            prev = m.end()
            cc = m.group(1)  # char class e.g. "[- ./]", or None for \s
            if cc:
                inner = cc[1:-1]
                has_hyphen |= inner.startswith("-")
                has_space |= " " in inner
                has_dot |= "." in inner
                has_slash |= "/" in inner
            else:
                has_space = True  # \s
        parts.append(regex[prev:])
        return parts, has_hyphen, has_space, has_dot, has_slash

    @staticmethod
    def _split_at_positions(regex: str, positions: list) -> list:
        """Split regex at specific character positions (width 1)."""
        parts: List[str] = []
        prev = 0
        for pos in positions:
            parts.append(regex[prev:pos])
            prev = pos + 1
        parts.append(regex[prev:])
        return parts

    @staticmethod
    def _word_bounded(s: str) -> str:
        if not s.startswith(r"\b"):
            s = r"\b" + s
        if not s.endswith(r"\b"):
            s = s + r"\b"
        return s

    @staticmethod
    def _all_valid(*regexes: str) -> bool:
        for r in regexes:
            try:
                re.compile(r)
            except re.error:
                return False
        return True

    def _wrap_validator(self, recognizer: PatternRecognizer) -> Optional[Callable[[Span], bool]]:
        # Presidio has two separate validation hooks that are both called in analyze():
        # - validate_result: positive validation (returns True/False/None)
        # - invalidate_result: negative validation (returns True to discard)
        # They don't chain through each other, so we must call both.
        has_validate = type(recognizer).validate_result is not PatternRecognizer.validate_result
        has_invalidate = type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result
        if not has_validate and not has_invalidate:
            return None

        def _validator(span: Span, _r: PatternRecognizer = recognizer) -> bool:
            if _r.invalidate_result(span.text):
                return False
            result = _r.validate_result(span.text)
            return result if result is not None else True

        return _validator

    def translate_context(
        self, context: Optional[List[str]]
    ) -> Optional[List[ContextPattern]]:
        if not context:
            return None
        single_words: List[str] = []
        patterns: List[ContextPattern] = []
        for phrase in context:
            tokens = phrase.lower().split()
            if len(tokens) == 1:
                single_words.append(tokens[0])
            else:
                # Multi-word phrase: one token dict per word so spaCy matches across tokens
                patterns.append({"pattern": [{"LEMMA": t} for t in tokens], "score": self.context_boost})
        if len(single_words) == 1:
            patterns.insert(0, {"pattern": [{"LEMMA": single_words[0]}], "score": self.context_boost})
        elif single_words:
            patterns.insert(0, {"pattern": [{"LEMMA": {"IN": single_words}}], "score": self.context_boost})
        return patterns or None

    def _convert_entity_recognizer(self, recognizer: EntityRecognizer) -> Entity:
        entities = recognizer.supported_entities
        alignment_mode = self.alignment_mode
        min_score = self.min_score

        def _matcher(doc: Doc) -> List[Tuple[int, int, float]]:
            results = recognizer.analyze(doc.text, entities=entities, nlp_artifacts=None)  # ty:ignore[invalid-argument-type]
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
