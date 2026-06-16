"""Post-processing passes that clean up extracted source code.

Change this file when RecognizerResult's structure changes in presidio.
Everything else here is presidio-agnostic.
"""
import ast
import copy
import re

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

def inline_single_return_functions(src: str) -> str:
    """Inline top-level functions whose entire body is a single return expression."""
    try:
        tree = ast.parse(src)
        inlineable: dict[str, tuple[list[str], ast.expr]] = {}

        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
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
        return remove_uncalled_functions(ast.unparse(new_tree), keep={"_analyze"})
    except Exception:
        return src

def remove_unused_imports(src: str, imports: list[str]) -> list[str]:
    result = []
    for imp in imports:
        if "\n" in imp:
            result.append(imp)
            continue
        name = imp.split(" import ", 1)[-1].strip() if imp.startswith("from ") else imp[len("import "):].strip()
        if name in src:
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
        return src
