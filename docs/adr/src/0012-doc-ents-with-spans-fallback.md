# Downstream consumers read doc.ents with fallback to doc.spans

`Anonymizer` and `StructuredAnalyzer` read entities from `doc.ents` first. If `doc.ents` is empty they fall back to `doc.spans[spans_key]`, passing the spans through `HierarchicalMergeFilter` to enforce the non-overlap invariant before use.

In the standard pipeline, `ConflictResolver` populates `doc.ents` (see ADR-0014). The fallback exists so that both components remain functional in pipelines that omit `ConflictResolver` — for example, a span-categorizer pipeline or a lightweight setup without conflict resolution. Without the fallback, omitting `ConflictResolver` would silently produce empty output.

`doc.ents` is preferred when populated because `ConflictResolver` has already enforced non-overlap and applied the score threshold. The fallback applies `HierarchicalMergeFilter` to ensure the same invariant holds on the spans path.

## Considered Options

- **`doc.ents` only**: any pipeline without `ConflictResolver` silently produces no output.
- **`doc.spans` only**: ignores the resolved, threshold-filtered result from `ConflictResolver`.
- **Configurable via a flag**: adds API surface and requires callers to know which pipeline shape they are using.
- **`doc.ents` with `doc.spans` fallback** (chosen): transparent to callers, no extra configuration, correct for both pipeline shapes.
