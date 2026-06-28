# AST source extraction for Presidio validator logic

Validator logic is extracted from Presidio recognizer source code via AST manipulation (`extractor/`) rather than wrapped at runtime. The extraction pipeline uses `inspect.getsource()`, strips Presidio-specific references (self-attributes, self-method calls, Presidio class references, module-level constants), resolves free names to importable statements, and emits a standalone `_validator(span: Span) -> bool` function with no Presidio dependency.

The generated entity files import no Presidio types at all. This means the maskpipe pipeline can run without `presidio-analyzer` installed; Presidio is only needed at code-generation time.

## Considered Options

- **Runtime wrapping**: call `recognizer.validate_result(span.text)` inside a lambda at import time. Simple, but requires `presidio-analyzer` as a production dependency and couples the entity type to a live Presidio instance.
- **AST extraction** (chosen): the generated file is fully self-contained. The cost is a complex extraction pipeline that can fail for unusual validator implementations (falls back to a `# TODO` comment in that case).
