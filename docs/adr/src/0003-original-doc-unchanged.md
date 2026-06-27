# Anonymizer leaves the original Doc unchanged; masked text stored in doc._.masked

The `Anonymizer` pipeline component does not modify the spaCy `Doc` it receives. Instead it writes the masked plain text to a custom extension `doc._.masked` and returns the original `Doc` untouched — with all spans, entities, and token annotations intact.

This means callers can access both the original annotated `Doc` (with detected spans and their scores) and the masked output string from a single pipeline run. The alternative — returning a new masked doc or replacing the text in place — would discard the span annotations that downstream code may need.

## Considered Options

- **Return masked text directly**: simplest API, but loses all span annotations.
- **Mutate doc.text in place**: not possible in spaCy — `Doc.text` is immutable.
- **Return a new masked Doc**: preserves the pipeline pattern but forces callers to choose which doc to keep.
- **`doc._.masked` extension** (chosen): both the annotated original and the masked string are available from one doc; no pipeline branching needed.
