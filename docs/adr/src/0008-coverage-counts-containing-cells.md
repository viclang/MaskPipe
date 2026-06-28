# Coverage counts cells containing a label, not cells dominated by it

`ColumnAnalysis.coverage` could be defined as (a) the fraction of cells whose sole detected label matched the column winner, or (b) the fraction of cells that contain any entity of the winning label, including mixed cells.

We use definition (b): a cell contributes to a label's coverage if it contains any entity with that label, regardless of whether the cell also contains other labels.

Definition (a) underreports in the common case where a column has a dominant type but some cells contain additional PII alongside it. A column where 80 % of cells have only `NAME` and 20 % have both `NAME` and `SSN` would show 0.8 NAME coverage under (a) even though NAME appears in every cell. Definition (b) gives 1.0, which is the more accurate signal for downstream decisions about masking.

## Consequences

Per-label coverage in `entity_distribution` will be high for multiple labels in mixed columns. Callers who need to detect mixed columns should inspect `entity_distribution` rather than relying on the top-level `label` alone.
