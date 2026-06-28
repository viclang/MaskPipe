# MaskPipe

A spaCy-native library for detecting and transforming sensitive entities (PII, financial data, and other confidential information) in free text and structured data.

## Capabilities

- **Detect sensitive spans in free text**: given a spaCy `Doc`, identify token spans matching known entity types using pattern rules, validators, and/or an external NLP model; produce scored `Span` objects.
- **Boost span confidence from context**: given a `Doc` with detected spans, raise their scores when configured context words appear nearby within a token window or via dependency link.
- **Merge overlapping spans**: given a set of candidate spans, apply a hierarchical filter to resolve conflicts and return a non-overlapping, highest-priority subset.
- **Transform detected spans in text**: given a `Doc` with spans, replace each span with the output of its redactor — a fixed placeholder, generated fake value, encrypted form, or any callable.
- **Classify columns in structured data**: given a dict of column → values, run detection across sampled cell values and infer the dominant entity type for each column.
- **Bridge external model output**: given raw output from an external NLP model (e.g. GLiNER), map it into spaCy `Span` annotations so the rest of the pipeline can process it uniformly.

## Language

### Detection

**Entity**:
A configuration object that fully describes how to recognize and transform one type of sensitive data — its label, token patterns, validator, context patterns, and optional default redactor. Not a detected instance; detected instances are spaCy `Span` objects.
_Avoid_: EntityType, RecognizerConfig, EntityDefinition

**Pattern**:
A spaCy token match rule paired with a confidence `score`. The `score` is the detection confidence when this pattern fires.
_Avoid_: Rule, TokenPattern

**Validator**:
A `(Span) -> bool` function attached to an `Entity` that accepts or rejects a candidate span after pattern matching. Runs after the pattern fires; `False` discards the span.
_Avoid_: Filter, Checker

### Context

**ContextPattern**:
A spaCy token match rule that, when found near a span, raises that span's score by the pattern's `score` (boost delta). When no `score` is set on the pattern, `ContextEnhancer.default_score` is used as the fallback.
_Avoid_: ContextRule, ContextBoost

**default_score** *(on `ContextEnhancer`)*:
The fallback boost delta applied when a matching `ContextPattern` carries no `score` of its own. Mirrors the `score` field name on `ContextPattern`.
_Avoid_: confidence_boost

### Redaction

**Redactor**:
A rule for transforming a detected span's text into its replacement. Three forms are accepted and normalized internally to `(str) -> str`:
- **Fixed string** — same replacement every time (e.g. `"[SSN]"`).
- **Generator** — zero-arg callable; called once per span, producing a different value each time (e.g. a fake-data factory).
- **Transform** — one-arg callable receiving the original text (e.g. encryption, hashing).
_Avoid_: Replacement, Mask, Anonymizer (for the rule — `Anonymizer` is the pipeline component)

**Masked text**:
The result of applying all redactors to a `Doc`; stored on `doc._.masked` as a plain string. The original `Doc` is left unchanged.
_Avoid_: Anonymized text, redacted text

### Pipeline

**PipelineBuilder**:
Assembles a spaCy `Language` pipeline from a list of `Entity` configs, wiring `Recognizer`, `ContextEnhancer`, `ConflictResolver`, and `Anonymizer` components in order. `Entity.redactor` values are seeded into the `Anonymizer` as defaults; `Anonymizer.add_redactors()` overrides them at runtime.

**DocBuilder**:
A fluent factory for constructing spaCy `Doc` objects seeded with pre-mapped entity annotations and/or context words before the pipeline runs. Used when detection comes from an external model rather than the `Recognizer` component; `StructuredAnalyzer` uses it internally for every cell value it processes.
_Avoid_: DocFactory, DocAnnotator

**EntityMapper**:
An adapter that converts raw output from an external NLP model into `EntityResult` objects so they can be loaded into a spaCy `Doc` by `DocBuilder`.
_Provisional_: may be renamed as external model integrations expand

### Structured Analysis

**StructuredAnalyzer**:
The component that classifies columns in tabular data. For each column it samples cell values, runs them through the spaCy pipeline via `DocBuilder`, and returns a `ColumnAnalysis` per column. The column name is passed as a context word to `DocBuilder` so that `ContextEnhancer` can boost entity scores when the column name appears near a detected span — e.g. a column named `"geboortedatum"` boosts birth-date entity confidence. Does not mutate input data.
_Avoid_: ColumnClassifier, TableAnalyzer

**ColumnAnalysis**:
The result of classifying one column. Carries a `label` (the dominant entity type or `NON_PII`), a `score` (`coverage × average entity confidence` for the winning label — the same metric used to select it), an `entity_distribution` (per-label `LabelStats`), and an optional `entities` list when `include_entities=True`. See ADR-0007.

**LabelStats**:
Per-label summary within `entity_distribution`. Carries `coverage` (fraction of sampled cells containing that label) and `score` (average detection confidence). Mirrors the top-level `ColumnAnalysis` fields for easy comparison.

**coverage** *(on `ColumnAnalysis` and `LabelStats`)*:
Fraction of sampled cells that contain at least one entity of the relevant label. A cell contributes to a label's coverage even if it also contains entities of other labels. For `NON_PII` columns, coverage is `0.0`. See ADR-0008.
_Avoid_: frequency, prevalence
