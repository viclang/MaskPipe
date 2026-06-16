"""Assemble native maskpipe Entity source files from Presidio recognizers."""
from maskpipe.presidio import PresidioConverter
from presidio_analyzer import EntityRecognizer, PatternRecognizer

from porter import extract_analyze, extract_validator

def _format_str_literal(s: str) -> str:
    if "\\" in s:
        if '"' not in s:
            return f'r"{s}"'
        if '"""' not in s:
            return 'r"""' + s + '"""'
        escaped = s.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    escaped = s.replace('"', '\\"')
    return f'"{escaped}"'

def _format_literal(v) -> str:
    if isinstance(v, str):
        return _format_str_literal(v)
    if isinstance(v, dict):
        pairs = ", ".join(f'"{k}": {_format_literal(val)}' for k, val in v.items())
        return "{" + pairs + "}"
    if isinstance(v, (list, tuple)):
        items = ", ".join(_format_literal(item) for item in v)
        return "[" + items + "]"
    return repr(v)

def _format_pattern(p: dict, indent: str = "        ") -> str:
    score = p.get("score", 0.5)
    tokens = p["pattern"]
    if len(tokens) == 1:
        return f'{indent}{{"score": {score}, "pattern": [{_format_literal(tokens[0])}]}}'
    token_lines = "\n".join(f"{indent}    {_format_literal(t)}," for t in tokens)
    return f'{indent}{{"score": {score}, "pattern": [\n{token_lines}\n{indent}]}}'

def _format_context_pattern(cp: dict, indent: str = "        ") -> str:
    parts = [f'"pattern": {_format_literal(cp["pattern"])}']
    if "score" in cp:
        parts.append(f'"score": {cp["score"]}')
    return f'{indent}{{{", ".join(parts)}}}'

def _emit_imports(imports: list[str], lines: list[str]) -> None:
    seen: set[str] = set()
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            if "\n" in imp:
                lines.append("")
                lines.append(imp)
                lines.append("")
            else:
                lines.append(imp)

def _generate_pattern_entity(recognizer: PatternRecognizer, converter: PresidioConverter) -> str:
    label = recognizer.supported_entities[0]
    var_name = label.replace("-", "_")
    class_name = type(recognizer).__name__
    module_name = type(recognizer).__module__

    patterns = []
    for p in recognizer.patterns:
        patterns.extend(converter._translate_pattern(p.regex, p.score))

    context_patterns = converter._translate_context(getattr(recognizer, "context", None))
    validator_src, validator_imports = extract_validator(recognizer)
    has_validator = validator_src is not None

    validator_port_failed = not has_validator and (
        type(recognizer).validate_result is not PatternRecognizer.validate_result
        or type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result
    )

    lines: list[str] = []
    lines.append(f'"""Entity generated from {module_name}.{class_name}."""')

    if validator_imports:
        _emit_imports(validator_imports, lines)
    lines.append("from maskpipe.entities.entity import Entity")

    if has_validator:
        lines.append("")
        lines.append(validator_src)
    elif validator_port_failed:
        lines.append("")
        lines.append("# TODO: port validator logic from:")
        if type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result:
            lines.append(f"#   {module_name}.{class_name}.invalidate_result")
        if type(recognizer).validate_result is not PatternRecognizer.validate_result:
            lines.append(f"#   {module_name}.{class_name}.validate_result")
        lines.append("_validator = None")

    lines.append("")
    lines.append(f"{var_name} = Entity(")
    lines.append(f'    label="{label}",')

    if patterns:
        lines.append("    patterns=[")
        for p in patterns:
            lines.append(_format_pattern(p) + ",")
        lines.append("    ],")

    lines.append(f"    validator={'_validator' if (has_validator or validator_port_failed) else 'None'},")

    if context_patterns:
        lines.append("    context_patterns=[")
        for cp in context_patterns:
            lines.append(_format_context_pattern(cp) + ",")
        lines.append("    ],")

    lines.append(")")
    lines.append("")

    return "\n".join(lines)

def _generate_entity_recognizer_entity(recognizer: EntityRecognizer, converter: PresidioConverter) -> str:
    label = recognizer.supported_entities[0]
    var_name = label.replace("-", "_")
    class_name = type(recognizer).__name__
    module_name = type(recognizer).__module__

    analyze_src, analyze_imports = extract_analyze(recognizer)
    context_patterns = converter._translate_context(getattr(recognizer, "context", None))

    custom_matcher_src = (
        f"def _custom_matcher(doc: Doc) -> list[tuple[int, int, float]]:\n"
        f"    spans = []\n"
        f"    for char_start, char_end, score in _analyze(doc.text):\n"
        f'        span = doc.char_span(char_start, char_end, alignment_mode="{converter.alignment_mode}")\n'
        f"        if span:\n"
        f"            spans.append((span.start, span.end, score))\n"
        f"    return spans"
    )

    lines: list[str] = []
    lines.append(f'"""Entity generated from {module_name}.{class_name}."""')
    lines.append("from spacy.tokens import Doc")
    _emit_imports(analyze_imports, lines)
    lines.append("from maskpipe.entities.entity import Entity")

    lines.append("")
    lines.append(analyze_src)
    lines.append("")
    lines.append(custom_matcher_src)
    lines.append("")
    lines.append(f"{var_name} = Entity(")
    lines.append(f'    label="{label}",')
    lines.append("    custom_matcher=_custom_matcher,")

    if context_patterns:
        lines.append("    context_patterns=[")
        for cp in context_patterns:
            lines.append(_format_context_pattern(cp) + ",")
        lines.append("    ],")

    lines.append(")")
    lines.append("")

    return "\n".join(lines)

def generate(recognizer: EntityRecognizer, converter: PresidioConverter) -> str:
    if isinstance(recognizer, PatternRecognizer):
        return _generate_pattern_entity(recognizer, converter)
    return _generate_entity_recognizer_entity(recognizer, converter)
