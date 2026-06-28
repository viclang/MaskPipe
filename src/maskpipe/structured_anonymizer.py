import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

from .structured_analyzer import ColumnAnalysis, NON_PII_LABEL

NoArgReplacement = Callable[[], str]
TextReplacement = Callable[[str], str]


class StructuredAnonymizer:
    """Replace PII column values with label-specific surrogates.

    Works on pre-computed :class:`ColumnAnalysis` results from
    :class:`StructuredAnalyzer`. Each cell in a PII-labeled column is replaced
    whole; the original data is never mutated.
    """

    def __init__(
        self,
        min_score: float = 0.0,
    ):
        """
        Args:
            min_score: Minimum ``ColumnAnalysis.score`` (coverage × avg confidence)
                a column must reach to be anonymized. Columns below this threshold
                are left unchanged even if labeled PII. Defaults to ``0.0``
                (anonymize all non-NON_PII columns regardless of score).
        """
        self.min_score = min_score
        self._redactors: Dict[str, TextReplacement] = {}

    def add_redactors(
        self,
        redactors: Dict[str, Union[str, NoArgReplacement, TextReplacement]],
    ) -> None:
        """Register or update replacement rules for entity labels.

        Args:
            redactors: Maps entity labels to a fixed string, a zero-argument
                callable returning a string, or a one-argument callable
                receiving the original cell value and returning its replacement.
                If no rule is registered for a label the default replacement
                ``[LABEL]`` is used.
        """
        self._redactors.update(
            {k: self._normalize_redactor(v) for k, v in redactors.items()}
        )

    def anonymize(
        self,
        data: Dict[str, List[Any]],
        analysis: Dict[str, ColumnAnalysis],
    ) -> Dict[str, List[Any]]:
        """Return a copy of *data* with PII columns redacted.

        Columns are redacted when their ``ColumnAnalysis.label`` is not
        ``NON_PII`` and their ``score`` meets the ``min_score`` threshold.
        All other columns are copied unchanged. ``None`` values are preserved
        as-is regardless of column label.

        Args:
            data: Column-oriented data (``{column: [values...]}``) to anonymize.
            analysis: Per-column analysis produced by
                :meth:`StructuredAnalyzer.analyze`.

        Returns:
            New dict with the same columns; PII column values are replaced,
            all other values are shallow-copied.
        """
        result: Dict[str, List[Any]] = {}
        for col, values in data.items():
            col_analysis = analysis.get(col)
            if (
                col_analysis is None
                or col_analysis["label"] == NON_PII_LABEL
                or col_analysis["score"] < self.min_score
            ):
                result[col] = list(values)
            else:
                label = col_analysis["label"]
                redactor = self._get_redactor(label)
                result[col] = [
                    redactor(str(v)) if v is not None else None
                    for v in values
                ]
        return result

    def _get_redactor(self, label: str) -> TextReplacement:
        return self._redactors.get(label, lambda _: f"[{label.upper()}]")

    @staticmethod
    def _normalize_redactor(
        redactor: Union[str, NoArgReplacement, TextReplacement],
    ) -> TextReplacement:
        if isinstance(redactor, str):
            fixed = redactor
            return lambda _: fixed
        sig = inspect.signature(redactor)
        params = [p for p in sig.parameters.values() if p.name != "self"]
        if not params:
            generator = cast(NoArgReplacement, redactor)
            return lambda _: generator()
        if len(params) == 1:
            return cast(TextReplacement, redactor)
        raise TypeError(
            f"Redactor must be a str or callable taking zero or one positional "
            f"argument, got {len(params)} parameters"
        )
