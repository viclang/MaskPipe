# Raw entity list in ColumnAnalysis is opt-in

`ColumnAnalysis` could always include the full list of detected `EntityResult` objects from sampled cells, or only when explicitly requested. For large `n`, the list grows linearly with sample size and is rarely needed in production — most callers only need the column label, coverage, and score.

`entities` is a `NotRequired` field, populated only when `include_entities=True` is passed to `analyze()`. It defaults to absent.

To keep the summary useful without the raw list, `entity_distribution` was enriched from a plain `Dict[str, int]` (counts only) to `Dict[str, LabelStats]`, where `LabelStats` carries both `coverage` and average `score` per label — the two components that compose the column-level `score` (see ADR-0007). Callers who only need aggregate statistics never pay the memory cost of materialising the full entity list.
