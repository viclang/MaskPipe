# doc.spans[spans_key] is the working location; doc.ents is the final output

All mid-pipeline components (`DocBuilder`, `Recognizer`, `ContextEnhancer`) read and write entities exclusively to `doc.spans[spans_key]`. `ConflictResolver` is the single gate that reads `doc.spans[spans_key]`, resolves overlaps, and writes the non-overlapping result to `doc.ents`. Downstream consumers (`Anonymizer`, `StructuredAnalyzer`) read from `doc.ents`.

`doc.spans` permits overlapping spans; `doc.ents` does not. Keeping the working copy in `doc.spans` means upstream components can produce overlapping candidates freely — pattern matching, external model output, and context enhancement all operate without needing to enforce non-overlap. `ConflictResolver` enforces the invariant exactly once at the boundary.

The alternative — using `doc.ents` as the working location throughout — would require every upstream component to run conflict resolution before writing, coupling detection logic to resolution logic and preventing any component from seeing the full overlapping candidate set.

`annotate_ents` flags on `DocBuilder` and `Recognizer`, and `style` flags on `ContextEnhancer`, `ConflictResolver`, and `Anonymizer`, were removed as a direct consequence: each component now has exactly one location to read from and one to write to, determined by its position in the pipeline.

## Consequences

A pipeline that omits `ConflictResolver` leaves `doc.ents` empty. `Anonymizer` and `StructuredAnalyzer` handle this via a `doc.spans` fallback (see ADR-0012), so they remain functional without the resolver — but the non-overlap guarantee is not enforced until `ConflictResolver` is present.
