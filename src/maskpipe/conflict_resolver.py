from collections.abc import Iterable
from typing import Callable, Optional

from spacy.language import Language
from spacy.pipeline import Pipe
from spacy.tokens import Doc, Span

from .constants import SPANS_KEY
from .span_filter import DEFAULT_HIERARCHY, hierarchical_merge_filter

SpansFilterFunc = Callable[[Iterable[Span]], Iterable[Span]]

DEFAULT_RESOLVER_CONFIG = {
    "spans_key": SPANS_KEY,
    "spans_filter": {
        "@misc": "maskpipe.hierarchical_merge_filter.v1",
        "hierarchy": DEFAULT_HIERARCHY
    },
    "threshold": 0.5
}

@Language.factory("conflict_resolver", assigns=["doc.ents"], default_config=DEFAULT_RESOLVER_CONFIG)
class ConflictResolver(Pipe):
    """Reads doc.spans[spans_key], resolves overlaps, and writes the result to doc.ents."""

    def __init__(
        self,
        nlp: Optional[Language] = None,
        name: str = "conflict_resolver",
        spans_key: str = SPANS_KEY,
        spans_filter: SpansFilterFunc = hierarchical_merge_filter,
        threshold: float = 0.5
    ):
        """
        Args:
            nlp: The spaCy Language object (optional; not used at runtime).
            name: Component name registered in the pipeline.
            spans_key: Key under ``doc.spans`` to read candidate spans from.
            spans_filter: Callable that resolves overlapping spans. Defaults to
                :func:`hierarchical_merge_filter`, which keeps the longest span
                per overlap group.
            threshold: Minimum ``span._.score`` a span must have to survive
                into ``doc.ents``. Spans below this value are dropped.
        """
        self.nlp = nlp
        self.name = name
        self.spans_key = spans_key
        self.spans_filter = spans_filter
        self.threshold = threshold

    def __call__(self, doc: Doc) -> Doc:
        """Process document and resolve span conflicts (pipeline method)."""
        spans = list(doc.spans.get(self.spans_key, []))
        if not spans:
            return doc

        resolved_spans = self.spans_filter(spans) if self.spans_filter is not None else spans

        if self.threshold > 0.0:
            resolved_spans = [
                span for span in resolved_spans
                if getattr(span._, "score", 0.0) >= self.threshold
            ]

        doc.set_ents(list(resolved_spans))
        return doc