# ECS pattern for the codegen pipeline

The `scripts/` codegen pipeline is organised as an Entity Component System: `RecognizerEntity` is a typed component container, each component (`IdentityComponent`, `PatternsComponent`, `ContextComponent`, `ValidatorComponent`, `AnalyzeComponent`, …) is a pure `@dataclass`, and each `_attach_*` function in `codegen.py` is a system that adds exactly one component. Rendering is fully decoupled into a Jinja2 template (`templates/entity.j2`) that receives components as template variables and never calls Python logic.

This is the organizing metaphor, not a performance optimisation. The goal is future-proofing: when Presidio restructures a recognizer type, the change is isolated to the one system and the one template block that handles it. Adding a new recognizer kind requires a new component, a new system, and a new template block — no existing code changes.

## Considered Options

- **Monolithic generator function**: simpler initially, but every new recognizer variant requires branching inside a growing function.
- **ECS** (chosen): each variation is an independent, addable unit. The cost is more files and the indirection of component lookup.
