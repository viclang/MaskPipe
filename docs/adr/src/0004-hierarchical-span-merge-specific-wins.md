# Hierarchical span merge: more specific label wins within a group

When overlapping spans belong to the same hierarchy group (e.g. `date` and `date_of_birth` are in the `date` group), the more specific label wins — `date_of_birth` beats `date`. Ties in specificity are broken by score. Overlapping spans from different groups are resolved by score alone (highest score claims the tokens first).

The hierarchy is a configurable dict (`parent → [children]`) with a sensible default covering common PII groupings. The winner's label and score are kept; the merged span covers the full token range of both.

This is the opposite of what a reader might expect: in most systems a broader category wins over a sub-category. Here the sub-category is preferred because `date_of_birth` carries more information than `date` — precision is more useful downstream for redaction and structured analysis.

## Considered Options

- **Score-only resolution**: simpler, but a generic `date` pattern with a high score would silently beat a specific `date_of_birth` pattern with a slightly lower score, losing the semantic distinction.
- **Parent wins**: consistent with a "safe default" philosophy, but discards specificity that the recognizer worked to establish.
- **Child wins** (chosen): preserves the most informative label; score breaks ties within the same specificity level.
