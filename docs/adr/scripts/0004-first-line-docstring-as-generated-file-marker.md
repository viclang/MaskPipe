# First-line docstring as generated file identity marker

Generated entity files begin with a docstring of the form:

```python
"""Entity generated from presidio_analyzer.<module>.<ClassName>."""
```

This first line serves as both a human-readable marker and a machine-parseable pointer: `--update-all` scans `entities/` for files whose first line starts with this prefix, extracts the dotted path, and uses it to re-instantiate the original Presidio recognizer for regeneration. No separate manifest or database is needed.

## Considered Options

- **Separate manifest file** (e.g. `generated.json`): explicit, but a second source of truth that can drift from the actual files.
- **Comment marker** (`# generated from ...`): invisible to `help()` and IDEs; harder to grep for the class path.
- **First-line docstring** (chosen): visible in the file, readable by humans and tools, self-contained. The constraint is that the format must not change without running `--update-all` to migrate all files.
