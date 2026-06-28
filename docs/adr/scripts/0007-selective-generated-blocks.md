# Selective BEGIN GENERATED / END GENERATED blocks with named variables

Generated entity files use named section markers (`# BEGIN GENERATED: <name>` / `# END GENERATED: <name>`) instead of whole-file regeneration. Each logical section — `imports`, `patterns`, `context_patterns`, `validator`, `custom_matcher` — is an independently replaceable block. Patterns and context patterns are assigned to named module-level variables (`_PATTERNS: list[Pattern]`, `_CONTEXT_PATTERNS: list[ContextPattern]`) so each block can be removed without breaking the `Entity(...)` call at the bottom.

Removing a block's markers permanently opts that section out of future regeneration. `--update-all` detects stale block names (e.g. after a rename) and falls back to full-file replacement automatically.

## Considered Options

- **Whole-file regeneration**: simpler script, but any hand-edit is silently overwritten on the next `--update-all` run.
- **Selective blocks** (chosen): hand-edited sections survive regeneration; the generated parts stay up to date with Presidio changes. The cost is a slightly more complex update loop in `gen_entity.py`.
