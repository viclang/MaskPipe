"""Post-processing passes that clean up extracted source code.

Change this file when RecognizerResult's structure changes in presidio.
Everything else here is presidio-agnostic.
"""
import ast
import copy
import logging
import re

logger = logging.getLogger(__name__)

from .ast_utils import ArgumentSubstitutor

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
    """Replace _RecognizerResult(start=X, end=Y, score=Z, ...) with (X, Y, Z)."""

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

def fix_blank_lines(src: str) -> str:
    src = re.sub(r'\n+(def |class )', r'\n\n\1', src)
    return src.lstrip('\n')

def _is_clearly_bool(expr: ast.expr) -> bool:
    if isinstance(expr, ast.Constant) and isinstance(expr.value, bool):
        return True
    if isinstance(expr, ast.Compare):
        return True
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
        return True
    if isinstance(expr, ast.Name):
        return True  # variable — assumed correctly typed at assignment site
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
        return node  # don't recurse into nested functions

def wrap_bool_returns(src: str) -> str:
    """Wrap return values in bool() for top-level functions annotated -> bool."""
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

class _CallSiteReplacer(ast.NodeTransformer):
    """Replace calls to known single-return functions with the inlined return expression."""

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

def inline_single_return_functions(src: str, keep: set[str] = frozenset()) -> str:
    """Inline top-level functions whose entire body is a single return expression."""
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

class _ReturnFlipper(ast.NodeTransformer):
    """Flip return True ↔ return False, not recursing into nested function defs."""

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
    """True when _validator is just: [optional assign,] if _invalidate(...): return False; return True."""
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


def _build_invalidate_inline(inv_node: ast.FunctionDef) -> list[ast.stmt]:
    """Body of _invalidate prepared for inlining at an `if _invalidate(...): return False` site.

    - Terminal `return False` (valid path) is dropped so execution falls through to the caller.
    - All remaining `return True` (invalid path) are changed to `return False`.
    """
    body = list(inv_node.body)
    if (body
            and isinstance(body[-1], ast.Return)
            and isinstance(body[-1].value, ast.Constant)
            and body[-1].value.value is False):
        body = body[:-1]

    class _TrueToFalse(ast.NodeTransformer):
        def visit_Return(self, node):
            if isinstance(node.value, ast.Constant) and node.value.value is True:
                node.value = ast.Constant(value=False)
            return node
        def visit_FunctionDef(self, node):
            return node
        def visit_AsyncFunctionDef(self, node):
            return node

    return [_TrueToFalse().visit(copy.deepcopy(s)) for s in body]


def fold_helpers_into_validator(src: str) -> str:
    """Inline _invalidate body into _validator and remove _invalidate.

    - Deduplicates top-level function definitions by name (keeps first).
    - Normalises _invalidate to end with an explicit return before transforming.
    - Thin wrapper (`if _invalidate(...): return False; return True`):
        replaces the whole _validator body with _invalidate's body, full True↔False flip.
    - Complex body (has_validate + has_invalidate):
        inlines _invalidate at the `if _invalidate(...): return False` call site —
        `return True` → `return False`, terminal `return False` dropped (fall-through).
    - All other helpers stay top-level.
    """
    try:
        tree = ast.parse(src)

        # Dedup top-level functions: keep first definition for each name
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

        # Normalize: ensure _invalidate ends with an explicit return so transforms are lossless
        if not isinstance(inv_node.body[-1], ast.Return):
            inv_node.body.append(ast.Return(value=ast.Constant(value=False)))

        validator = next(
            (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_validator"),
            None,
        )

        if validator is not None:
            if _is_thin_invalidate_wrapper(validator):
                # Replace entire thin-wrapper body with _invalidate body, full True↔False flip
                body = validator.body
                orig_param = inv_node.args.args[0].arg if inv_node.args.args else "pattern_text"
                flipped = [_ReturnFlipper().visit(copy.deepcopy(s)) for s in inv_node.body]
                assign = ast.parse(f"{orig_param} = span.text").body[0]
                validator.body = [assign] + flipped
            else:
                # Inline at the injected `if _invalidate(arg): return False` site
                inline_stmts = _build_invalidate_inline(inv_node)

                class _InlineAtCallSite(ast.NodeTransformer):
                    def visit_FunctionDef(self, node):
                        new_body: list[ast.stmt] = []
                        for stmt in node.body:
                            if (
                                isinstance(stmt, ast.If)
                                and isinstance(stmt.test, ast.Call)
                                and isinstance(stmt.test.func, ast.Name)
                                and stmt.test.func.id == "_invalidate"
                                and not stmt.orelse
                                and len(stmt.body) == 1
                                and isinstance(stmt.body[0], ast.Return)
                                and isinstance(stmt.body[0].value, ast.Constant)
                                and stmt.body[0].value.value is False
                            ):
                                new_body.extend(copy.deepcopy(inline_stmts))
                            else:
                                new_body.append(stmt)
                        node.body = new_body
                        return node

                _InlineAtCallSite().visit(validator)

        # Remove _invalidate definition
        tree.body = [
            n for n in tree.body
            if not (isinstance(n, ast.FunctionDef) and n.name == "_invalidate")
        ]

        ast.fix_missing_locations(tree)
        return fix_blank_lines(ast.unparse(tree))
    except Exception:
        logger.exception("fold_helpers_into_validator failed")
        return src


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
