"""Extract Presidio validate/invalidate methods as a standalone _validator(span) -> bool function.

Change this file when presidio renames or restructures validate_result / invalidate_result.
"""
import ast

from presidio_analyzer import PatternRecognizer

from .ast_utils import deduplicate
from .extraction import extract_instance_method
from .source_cleanup import fix_blank_lines

def _adapt_first_param_to_span(src: str, func_name: str) -> str:
    """Change func_name(original_param: str, ...) to func_name(span: Span, ...) and prepend original_param = span.text."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name and node.args.args:
            orig_param = node.args.args[0].arg
            node.args.args[0].arg = "span"
            node.args.args[0].annotation = ast.parse("Span", mode="eval").body
            node.returns = ast.parse("bool", mode="eval").body
            assign = ast.parse(f"{orig_param} = span.text").body[0]
            node.body.insert(0, assign)
            break
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def extract_validator(recognizer) -> tuple[str, list[str]] | tuple[None, None]:
    has_validate = type(recognizer).validate_result is not PatternRecognizer.validate_result
    has_invalidate = type(recognizer).invalidate_result is not PatternRecognizer.invalidate_result

    if not has_validate and not has_invalidate:
        return None, None

    all_imports: list[str] = ["from spacy.tokens import Span"]
    helper_srcs: list[str] = []

    try:
        if has_invalidate:
            src, imports = extract_instance_method(recognizer, "invalidate_result", "_invalidate")
            helper_srcs.append(src)
            all_imports.extend(imports)

        if has_validate:
            src, imports = extract_instance_method(recognizer, "validate_result", "_validator")
            src = _adapt_first_param_to_span(src, "_validator")
            if has_invalidate:
                src = _inject_invalidate_check(src)
            helper_srcs.append(src)
            all_imports.extend(imports)
        else:
            wrapper = (
                "def _validator(span: Span) -> bool:\n"
                "    if _invalidate(span.text):\n"
                "        return False\n"
                "    return True"
            )
            helper_srcs.append(wrapper)
    except Exception:
        return None, None

    return fix_blank_lines("\n\n".join(helper_srcs)), deduplicate(all_imports)

def _inject_invalidate_check(src: str) -> str:
    """Insert 'if _invalidate(text): return False' into _validator after the span.text assignment."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_validator":
            # body[0] is `orig_param = span.text` — read its target name
            first = node.body[0]
            orig_param = first.targets[0].id if isinstance(first, ast.Assign) else "pattern_text"
            check = ast.parse(f"if _invalidate({orig_param}):\n    return False").body[0]
            node.body.insert(1, check)
            break
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
