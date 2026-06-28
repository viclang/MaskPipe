# spaCy as the pipeline foundation instead of Presidio

The entire detection and anonymization pipeline is built as native spaCy components (`Pipe` subclasses registered via `Language.factory`). Presidio is the obvious choice for PII detection — it ships a large library of recognizers out of the box and has an `AnonymizerEngine`. We chose spaCy instead.

spaCy gives composable, serializable pipeline components that integrate directly with language models, the spaCy matcher, and the broader spaCy ecosystem. The Presidio recognizer library is still available via `gen_entity.py`, which extracts Presidio recognizer logic into standalone spaCy-native `Entity` files — so Presidio remains a code-generation source, not a runtime dependency.

## Considered Options

- **Presidio as runtime engine**: less code to write, but Presidio's pipeline is not composable with spaCy components, requires `presidio-analyzer` in production, and its anonymization model is separate from its detection model.
- **spaCy** (chosen): more code upfront, but the pipeline is fully serializable, composable with any spaCy component, and `presidio-analyzer` is only needed at codegen time.
