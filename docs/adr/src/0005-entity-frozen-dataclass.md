# Entity is a frozen dataclass

`Entity` is declared `@dataclass(frozen=True)`. Its `__post_init__` converts any mutable `Sequence` passed for `patterns` or `context_patterns` into a `tuple` using `object.__setattr__` to bypass the frozen guard. Callers that need a modified copy use the generated `.replace()` wrapper around `dataclasses.replace`.

This is not the obvious choice. A plain mutable dataclass or a `TypedDict` would be simpler and require no `object.__setattr__` workaround. The frozen form is deliberately chosen because `Entity` instances are shared across pipeline components — the `PipelineBuilder` hands the same object to the `Recognizer`, the `ContextEnhancer`, and the `Anonymizer`. A mutable config object would allow one component (or user code) to silently mutate shared state, causing the other components to see a different configuration than what was registered.

## Considered Options

- **Mutable dataclass**: simplest, but shared instances can be accidentally mutated between construction and use, or between two pipeline runs that share a config.
- **TypedDict / plain dict**: no mutation guard at all; no `.replace()` ergonomics.
- **Frozen dataclass** (chosen): immutability is enforced by the runtime; `object.__setattr__` is confined to `__post_init__` and is a well-known pattern for this exact case. `.replace()` gives a clean copy-with-overrides API.
