# Column label selected by coverage × average score

When classifying a column, we need a single strategy to rank candidate entity labels. Three approaches were considered: most common (frequency only), highest confidence (score only), and a composite metric.

We rank labels by `coverage × average_score` and pick the highest. `coverage` is the fraction of sampled cells containing that label; `average_score` is the mean entity confidence for that label. The winner becomes the column label, with its coverage and score reported directly.

Pure frequency ignores confidence: a noisy label with marginally more hits wins over a rare but high-confidence one. Pure confidence ignores prevalence: a single high-confidence outlier can dominate a column where a different label appears in every cell. The product rewards labels that are both common and confident, without requiring a threshold parameter. Exact ties are practically impossible with a continuous product, so no tie-breaker is needed.

The `PII` column label is removed: mixed columns are characterised by their `entity_distribution`, which callers can inspect to determine multi-type presence themselves.

## Considered Options

- **Most common, tie-break by average score** (previous approach): tie-breaker only fires on exact count ties; confidence is otherwise ignored.
- **Highest confidence**: sensitive to outliers; a single strong detection overrides a label present in every cell.
- **Presidio `mixed` strategy**: uses highest confidence above a threshold, most common below — introduces an arbitrary threshold and two separate code paths.
- **`coverage × average_score`** (chosen): single continuous metric, no threshold, naturally balances frequency and confidence.
