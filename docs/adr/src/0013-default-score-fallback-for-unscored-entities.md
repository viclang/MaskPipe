# Entities without a score extension fall back to default_score

When extracting entities in `_process_doc`, the score for each entity is read from `ent._.score` if the spaCy `score` extension is registered. If the extension is absent, `self.default_score` is used instead.

Not all spaCy pipelines register a `score` extension. Rule-based recognisers (e.g. the built-in `Recognizer` component) attach scores via the extension; plain NER models from spaCy or HuggingFace do not. Without a fallback, unscored entities would require special-casing at every call site or a mandatory pre-processing step.

`default_score` is configurable on `StructuredAnalyzer` (default `0.6`) so that callers can tune the assumed confidence for their pipeline. A hardcoded fallback (e.g. `1.0`) would overstate confidence for rule-based matches that were never validated; `0.0` would suppress those entities from the `coverage × average_score` ranking entirely.

## Considered Options

- **Require a score extension**: breaks any pipeline that does not register one.
- **Default to `1.0`**: overstates confidence for unverified matches.
- **Default to `0.0`**: effectively removes unscored entities from ranking.
- **Configurable `default_score`** (chosen): callers set a prior that reflects how much they trust their pipeline's unscored output.
