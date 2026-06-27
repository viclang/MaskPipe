# Module-filename-based output path derivation for codegen

Entity files are named after the recognizer's Python module filename — stripping only the `_recognizer` suffix — rather than the entity label or the recognizer class name. For example, `us_ssn_recognizer.py` → `us_ssn.py`, not `ssn.py` (label-stripped) or `us_ssn_recognizer.py` (class-name). This makes the mapping reversible: given a generated file, `--update-all` can reconstruct the original Presidio dotted path from the first-line marker without any lookup table.

## Considered Options

- **Label-based** (`US_SSN` → `ssn.py`): requires a per-country prefix strip table; breaks when Presidio renames a label.
- **Class-name-based** (`UsSsnRecognizer` → `us_ssn_recognizer.py`): verbose; redundant with module filename.
- **Module-filename-based** (chosen): no table needed; stable as long as Presidio keeps its file naming convention.
