# None and whitespace-only values are filtered before sampling

Before sampling cell values for analysis, `None` and whitespace-only values are removed from the candidate pool. When `None` values are excluded, the sampler draws a replacement from the remaining non-null pool rather than reducing the sample size.

Remaining values are coerced to `str` before being passed to `DocBuilder`.

Including nulls would silently inflate apparent non-PII coverage: a column with 40 % null values would produce 40 % `NON_PII` results not because the model failed to detect PII but because there was nothing to detect. Filtering before sampling keeps coverage a meaningful signal of model output rather than a measure of data completeness. Callers who need null statistics should compute them separately from the raw data.

Whitespace-only strings (e.g. `" "`, `"\t"`) are treated the same as `None` because they produce empty spaCy `Doc` objects with no tokens, contributing no entity signal while artificially reducing the effective sample.
