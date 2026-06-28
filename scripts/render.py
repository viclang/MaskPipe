"""Jinja2-based rendering: RecognizerEntity → Python source file."""
from __future__ import annotations
import re
import sys
from pathlib import Path

_STDLIB = getattr(sys, "stdlib_module_names", frozenset())

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from codegen import (
    RecognizerEntity,
    AnalyzeComponent,
    ContextComponent,
    IdentityComponent,
    PatternsComponent,
    ValidatorComponent,
    ValidatorTodoComponent,
)


# ---------------------------------------------------------------------------
# Format filters — registered on the Jinja2 environment
# ---------------------------------------------------------------------------

def _str_literal(s: str) -> str:
    """Format a string as a Python literal, using raw strings when backslashes are present."""
    if "\\" in s:
        if '"' not in s:
            return f'r"{s}"'
        if '"""' not in s:
            return 'r"""' + s + '"""'
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    escaped = s.replace('"', '\\"')
    return f'"{escaped}"'


def _literal(v) -> str:
    if isinstance(v, str):
        return _str_literal(v)
    if isinstance(v, dict):
        pairs = ", ".join(f'"{k}": {_literal(val)}' for k, val in v.items())
        return "{" + pairs + "}"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_literal(item) for item in v) + "]"
    return repr(v)


def _format_pattern(p: dict) -> str:
    indent = "    "
    score = p.get("score", 0.5)
    tokens = p["pattern"]
    if len(tokens) == 1:
        return f'{indent}{{"score": {score}, "pattern": [{_literal(tokens[0])}]}}'
    token_lines = "\n".join(f"{indent}    {_literal(t)}," for t in tokens)
    return f'{indent}{{"score": {score}, "pattern": [\n{token_lines}\n{indent}]}}'


def _format_context_pattern(cp: dict) -> str:
    indent = "    "
    parts = [f'"pattern": {_literal(cp["pattern"])}']
    if "score" in cp:
        parts.append(f'"score": {cp["score"]}')
    return f'{indent}{{{", ".join(parts)}}}'


# ---------------------------------------------------------------------------
# Jinja2 environment
# ---------------------------------------------------------------------------

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)
_env.filters["format_pattern"] = _format_pattern
_env.filters["format_context_pattern"] = _format_context_pattern


# ---------------------------------------------------------------------------
# Import assembly
# ---------------------------------------------------------------------------

def _import_sort_key(imp: str) -> tuple[int, str]:
    mod = imp.split()[1].split(".")[0]
    return (0 if mod in _STDLIB else 1, imp)


def _build_imports_block(validator: ValidatorComponent | None, analyze: AnalyzeComponent | None) -> str:
    """Collect imports from validator and analyze components, deduped, stdlib-first, multi-line blocks last.

    Same-module `from X import a` / `from X import b` lines are merged into
    `from X import a, b` to comply with PEP 8.
    """
    raw: list[str] = []
    if analyze:
        raw.append("from spacy.tokens import Doc")
    if validator:
        raw.extend(validator.imports)
    if analyze:
        raw.extend(analyze.imports)

    from_imports: dict[str, set[str]] = {}
    bare: list[str] = []
    multi: list[str] = []
    seen: set[str] = set()

    for imp in raw:
        if imp in seen:
            continue
        seen.add(imp)
        if "\n" in imp:
            multi.append(imp)
        elif imp.startswith("from ") and " import " in imp:
            module, _, names_str = imp[5:].partition(" import ")
            from_imports.setdefault(module, set()).update(
                n.strip() for n in names_str.split(",")
            )
        else:
            bare.append(imp)

    merged = [f"from {mod} import {', '.join(sorted(names))}" for mod, names in from_imports.items()]
    single = sorted(bare + merged, key=_import_sort_key)

    lines: list[str] = list(single)
    for imp in multi:
        lines.extend(["", imp, ""])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(entity: RecognizerEntity) -> str:
    validator = entity.get(ValidatorComponent)
    analyze = entity.get(AnalyzeComponent)
    patterns = entity.get(PatternsComponent)
    context = entity.get(ContextComponent)
    imports_block = _build_imports_block(validator, analyze)
    entity_import_names = ["Entity"]
    if patterns:
        entity_import_names.append("Pattern")
    if context:
        entity_import_names.append("ContextPattern")
    entity_import = f"from maskpipe.entities.entity import {', '.join(sorted(entity_import_names))}"
    src = _env.get_template("entity.j2").render(
        identity=entity.get(IdentityComponent),
        patterns=patterns,
        context=context,
        validator=validator,
        validator_todo=entity.get(ValidatorTodoComponent),
        analyze=analyze,
        imports_block=imports_block,
        entity_import=entity_import,
    )
    return re.sub(r"\n{3,}", "\n\n", src)
