# Two-tier redactor precedence: Entity default vs Anonymizer runtime override

Redactors can be declared in two places. `Entity.redactor` is a default strategy co-located with the type definition; `PipelineBuilder` seeds it into the `Anonymizer` when assembling the pipeline. `Anonymizer.add_redactors()` is a runtime override that updates the same internal dict after the pipeline is built, and therefore always wins.

This layering lets entity definitions ship with sensible defaults (e.g. `"[SSN]"`) while allowing callers to substitute a different strategy at runtime (e.g. format-preserving encryption) without touching the entity definition.

## Redactor forms

A redactor is one of three forms, all normalized internally to `(str) -> str`:

- **Fixed string** — `"[REDACTED]"`: the same replacement for every occurrence.
- **Generator** — `Callable[[], str]`: called once per span with no arguments; used for fake-data generators where each occurrence gets a different value.
- **Transform** — `Callable[[str], str]`: called with the original span text; used for encryption, hashing, or format-preserving substitution.

## Considered Options

- **Single declaration point** (Entity only): cleaner, but forces the entity definition to know about runtime deployment concerns like encryption keys.
- **Single declaration point** (Anonymizer only): flexible at runtime, but no way to ship a sensible default with the entity type.
- **Two-tier** (chosen): defaults travel with the type; deployment-specific overrides stay at the call site.
