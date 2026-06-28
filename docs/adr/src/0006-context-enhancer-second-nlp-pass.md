# ContextEnhancer re-parses extended text in a second NLP pass

`ContextEnhancer.__call__` does not work solely with the `Doc` it receives. It concatenates `doc.text` with any `doc._.context_words`, passes the result through `self.nlp(...)` with most pipes disabled (producing `extended_doc`), normalises lemmas to lowercase on that copy, then runs a `Matcher` against `extended_doc` to find context patterns near the original spans.

This is surprising: a spaCy pipeline component is expected to operate only on the doc passed to it, not to invoke the pipeline again internally.

The re-parse is required because context words arrive as plain strings at call time (they may come from metadata, a database record, or a request header — not from the document text). LEMMA patterns must match against tokenised, lemmatised text. There is no spaCy API to inject pre-tokenised tokens into an existing `Doc` after construction, so the only way to lemmatise the context words using the same vocabulary and model is to run them through the pipeline. The second pass uses `select_pipes(disable=[...])` to skip all analysis components; only the tokeniser and lemmatiser run, keeping the cost proportional to the number of context words rather than the full pipeline.

The `extended_doc` is a scratch object and is discarded after the enhancer returns. The original `doc` is the only doc that is mutated.

## Considered Options

- **Require callers to pre-tokenise context words**: pushes the tokenisation burden to every call site and couples callers to the pipeline's vocabulary.
- **Match context words as plain strings (no lemmatisation)**: simpler, but breaks case-insensitive and inflection-insensitive matching — `"geboortedatum"` would not match a pattern written for `"geboorte"`.
- **Second NLP pass on extended text** (chosen): context words are lemmatised consistently with the main doc; the cost is bounded by disabling all analysis pipes; the original doc is untouched.
