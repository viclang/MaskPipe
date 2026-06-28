"""Presidio-specific AST rewrites applied to extracted validator and matcher source.

Change this file when Presidio changes its internal structure (RecognizerResult shape,
validate_result tri-state semantics, super() usage, utility function signatures).
"""
import ast
import copy
import logging
import re

from .ast_utils import ArgumentSubstitutor
from .normalize import fix_blank_lines

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Utility-function deduplication
# ---------------------------------------------------------------------------

_UTIL_FINGERPRINTS: dict[str, tuple[str, str]] = {}

def _build_util_fingerprints() -> None:
    _CANONICAL = {
        "_sanitize_value": (
            "sanitize_value",
            "def _sanitize_value(text, replacement_pairs):\n"
            "    for search_string, replacement_string in replacement_pairs:\n"
            "        text = text.replace(search_string, replacement_string)\n"
            "    return text",
        ),
        "_luhn_checksum": (
            "luhn_checksum",
            "def _luhn_checksum(digits):\n"
            "    nums = [int(d) for d in digits]\n"
            "    odd_digits = nums[-1::-2]\n"
            "    even_digits = nums[-2::-2]\n"
            "    checksum = sum(odd_digits)\n"
            "    for d in even_digits:\n"
            "        checksum += sum(int(dig) for dig in str(d * 2))\n"
            "    return checksum % 10 == 0",
        ),
        "_is_verhoeff_number": (
            "is_verhoeff_number",
            "def _is_verhoeff_number(input_number):\n"
            "    __d__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1], [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]\n"
            "    __p__ = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1], [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]\n"
            "    __inv__ = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]\n"
            "    c = 0\n"
            "    inverted_number = list(map(int, reversed(str(input_number))))\n"
            "    for i in range(len(inverted_number)):\n"
            "        c = __d__[c][__p__[i % 8][inverted_number[i]]]\n"
            "    return __inv__[c] == 0",
        ),
    }
    for extracted_name, (util_name, src) in _CANONICAL.items():
        try:
            tree = ast.parse(src)
            func = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
            fingerprint = "; ".join(ast.unparse(stmt) for stmt in func.body)
            _UTIL_FINGERPRINTS[extracted_name] = (util_name, fingerprint)
        except Exception:
            logger.exception("_build_util_fingerprints: failed to parse canonical for %s", extracted_name)

_build_util_fingerprints()


def replace_util_functions(src: str) -> tuple[str, list[str]]:
    """Remove inlined utility functions whose bodies match a canonical util implementation.

    Returns the cleaned source and a list of import strings to add.
    Call sites are renamed from the extracted name to the util name.
    """
    if not _UTIL_FINGERPRINTS:
        return src, []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src, []

    to_replace: dict[str, str] = {}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name not in _UTIL_FINGERPRINTS:
            continue
        util_name, expected_fp = _UTIL_FINGERPRINTS[node.name]
        actual_fp = "; ".join(ast.unparse(stmt) for stmt in node.body)
        if actual_fp == expected_fp:
            to_replace[node.name] = util_name

    if not to_replace:
        return src, []

    tree.body = [
        node for node in tree.body
        if not (isinstance(node, ast.FunctionDef) and node.name in to_replace)
    ]

    class _Renamer(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in to_replace:
                node.id = to_replace[node.id]
            return node

    tree = _Renamer().visit(tree)
    ast.fix_missing_locations(tree)

    imports = [
        f"from maskpipe.entities.util import {util_name}"
        for util_name in dict.fromkeys(to_replace.values())
    ]
    return fix_blank_lines(ast.unparse(tree)), imports

# ---------------------------------------------------------------------------
# RecognizerResult → tuple
# ---------------------------------------------------------------------------

RECOGNIZER_RESULT_FALLBACK = """\
class _RecognizerResult:
    def __init__(self, entity_type, start, end, score, **_):
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score

    def contained_in(self, other) -> bool:
        return self.start >= other.start and self.end <= other.end

    def __hash__(self):
        return hash(f"{self.start} {self.end} {self.score} {self.entity_type}")

    def __eq__(self, other) -> bool:
        return (self.entity_type == other.entity_type
                and self.score == other.score
                and self.start == other.start
                and self.end == other.end)"""

class _RecognizerResultCallToTuple(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "_RecognizerResult":
            kwargs = {kw.arg: kw.value for kw in node.keywords}
            start, end, score = kwargs.get("start"), kwargs.get("end"), kwargs.get("score")
            if start is not None and end is not None and score is not None:
                return ast.copy_location(
                    ast.Tuple(elts=[start, end, score], ctx=ast.Load()), node
                )
        return node

def replace_result_objects_with_tuples(src: str) -> str:
    try:
        tree = ast.parse(src)
        tree = _RecognizerResultCallToTuple().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        logger.exception("replace_result_objects_with_tuples failed")
        return src

# ---------------------------------------------------------------------------
# Boolean normalization
# ---------------------------------------------------------------------------

def _is_clearly_bool(expr: ast.expr) -> bool:
    if isinstance(expr, ast.Constant) and isinstance(expr.value, bool):
        return True
    if isinstance(expr, ast.Compare):
        return True
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
        return True
    if isinstance(expr, ast.Name):
        return True
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
        return expr.func.id in ('bool', 'isinstance')
    return False

class _BoolReturnWrapper(ast.NodeTransformer):
    def visit_Return(self, node):
        if node.value is None or _is_clearly_bool(node.value):
            return node
        node.value = ast.Call(func=ast.Name(id='bool', ctx=ast.Load()), args=[node.value], keywords=[])
        return node

    def visit_FunctionDef(self, node):
        return node

def wrap_bool_returns(src: str) -> str:
    try:
        tree = ast.parse(src)
        wrapper = _BoolReturnWrapper()
        for node in tree.body:
            if (isinstance(node, ast.FunctionDef)
                    and isinstance(node.returns, ast.Name)
                    and node.returns.id == 'bool'):
                node.body = [wrapper.visit(stmt) for stmt in node.body]
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        logger.exception("wrap_bool_returns failed")
        return src

def normalize_bool_tristate(src: str) -> str:
    """Replace `= None` with `= True` in top-level -> bool functions.

    Presidio's validate_result uses None as a tri-state "uncertain" value.
    In a bool validator, uncertain means the match passes, so None maps to True.
    """
    try:
        tree = ast.parse(src)
        changed = False
        for node in tree.body:
            if not (isinstance(node, ast.FunctionDef)
                    and isinstance(node.returns, ast.Name)
                    and node.returns.id == 'bool'):
                continue
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Assign)
                        and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is None):
                    stmt.value = ast.Constant(value=True)
                    changed = True
        if not changed:
            return src
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        logger.exception("normalize_bool_tristate failed")
        return src

# ---------------------------------------------------------------------------
# Helper inlining and dead-code removal
# ---------------------------------------------------------------------------

class _CallSiteReplacer(ast.NodeTransformer):
    def __init__(self, inlineable: dict[str, tuple[list[str], ast.expr]]):
        self._inlineable = inlineable

    def visit_Call(self, node):
        self.generic_visit(node)
        if (isinstance(node.func, ast.Name)
                and node.func.id in self._inlineable
                and len(node.args) == len(self._inlineable[node.func.id][0])):
            params, return_expr = self._inlineable[node.func.id]
            substitutions = dict(zip(params, node.args))
            inlined = ArgumentSubstitutor(substitutions).visit(copy.deepcopy(return_expr))
            return ast.copy_location(inlined, node)
        return node

def inline_single_return_functions(src: str, keep: set[str] = frozenset()) -> str:  # ty:ignore[invalid-parameter-default]
    try:
        tree = ast.parse(src)
        inlineable: dict[str, tuple[list[str], ast.expr]] = {}

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or node.name in keep:
                continue
            body = node.body
            if (len(body) == 2
                    and isinstance(body[0], ast.Assign)
                    and isinstance(body[1], ast.Return)
                    and isinstance(body[1].value, ast.Name)
                    and len(body[0].targets) == 1
                    and isinstance(body[0].targets[0], ast.Name)
                    and body[0].targets[0].id == body[1].value.id):
                inlineable[node.name] = ([a.arg for a in node.args.args], body[0].value)
            elif len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None:
                inlineable[node.name] = ([a.arg for a in node.args.args], body[0].value)

        if not inlineable:
            return src

        new_tree = _CallSiteReplacer(inlineable).visit(tree)
        ast.fix_missing_locations(new_tree)
        return remove_uncalled_functions(ast.unparse(new_tree), keep=keep)
    except Exception:
        logger.exception("inline_single_return_functions failed")
        return src

def remove_unused_imports(src: str, imports: list[str]) -> list[str]:
    result = []
    for imp in imports:
        if "\n" in imp:
            result.append(imp)
            continue
        name = imp.split(" import ", 1)[-1].strip() if imp.startswith("from ") else imp[len("import "):].strip()
        if " as " in name:
            name = name.split(" as ", 1)[1].strip()
        if re.search(r"\b" + re.escape(name) + r"\b", src):
            result.append(imp)
    return result

def remove_uncalled_functions(src: str, keep: set[str]) -> str:
    try:
        tree = ast.parse(src)
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        tree.body = [
            node for node in tree.body
            if not (
                isinstance(node, ast.FunctionDef)
                and node.name not in keep
                and node.name not in called
            )
        ]
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        logger.exception("remove_uncalled_functions failed")
        return src

def has_super_calls(src: str) -> bool:
    """Return True if the source contains any super() call — indicates unresolvable inheritance."""
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "super"
            ):
                return True
    except SyntaxError:
        pass
    return False

# ---------------------------------------------------------------------------
# Invalidate/validator merging
# ---------------------------------------------------------------------------

class _ReturnFlipper(ast.NodeTransformer):
    def visit_Return(self, node):
        if isinstance(node.value, ast.Constant):
            if node.value.value is True:
                node.value = ast.Constant(value=False)
            elif node.value.value is False:
                node.value = ast.Constant(value=True)
        return node

    def visit_FunctionDef(self, node):
        return node

    def visit_AsyncFunctionDef(self, node):
        return node

def _is_thin_invalidate_wrapper(validator_def: ast.FunctionDef) -> bool:
    body = validator_def.body
    start = 1 if body and isinstance(body[0], ast.Assign) else 0
    if len(body) - start != 2:
        return False
    check, ret = body[start], body[start + 1]
    return (
        isinstance(check, ast.If)
        and isinstance(check.test, ast.Call)
        and isinstance(check.test.func, ast.Name)
        and check.test.func.id == "_invalidate"
        and len(check.body) == 1
        and isinstance(check.body[0], ast.Return)
        and isinstance(check.body[0].value, ast.Constant)
        and check.body[0].value.value is False
        and not check.orelse
        and isinstance(ret, ast.Return)
        and isinstance(ret.value, ast.Constant)
        and ret.value.value is True
    )

def fold_helpers_into_validator(src: str) -> str:
    """Inline _invalidate body into _validator and remove _invalidate."""
    try:
        tree = ast.parse(src)

        seen_names: set[str] = set()
        tree.body = [
            n for n in tree.body
            if not isinstance(n, ast.FunctionDef)
            or (n.name not in seen_names and not seen_names.add(n.name))  # type: ignore[func-returns-value]
        ]

        inv_node = next(
            (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_invalidate"),
            None,
        )
        if inv_node is None:
            ast.fix_missing_locations(tree)
            return fix_blank_lines(ast.unparse(tree))

        if not isinstance(inv_node.body[-1], ast.Return):
            inv_node.body.append(ast.Return(value=ast.Constant(value=False)))

        validator = next(
            (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_validator"),
            None,
        )

        inlined = False
        if validator is not None and _is_thin_invalidate_wrapper(validator):
            orig_param = inv_node.args.args[0].arg if inv_node.args.args else "pattern_text"
            flipped = [_ReturnFlipper().visit(copy.deepcopy(s)) for s in inv_node.body]
            assign = ast.parse(f"{orig_param} = span.text").body[0]
            validator.body = [assign] + flipped
            inlined = True

        if inlined:
            tree.body = [
                n for n in tree.body
                if not (isinstance(n, ast.FunctionDef) and n.name == "_invalidate")
            ]

        ast.fix_missing_locations(tree)
        return fix_blank_lines(ast.unparse(tree))
    except Exception:
        logger.exception("fold_helpers_into_validator failed")
        return src
