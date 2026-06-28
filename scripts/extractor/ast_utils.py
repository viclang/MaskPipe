"""Generic AST transformers and import resolution. No presidio dependencies."""
import ast
import builtins
import copy
import inspect
import logging
import sys

_BUILTINS = frozenset(dir(builtins))
logger = logging.getLogger(__name__)

def is_presidio(obj) -> bool:
    mod = inspect.getmodule(obj)
    return mod is not None and mod.__name__.startswith("presidio_analyzer")

class SelfAttrInliner(ast.NodeTransformer):
    """Replace self.attr (non-callable) with its live value from the recognizer."""

    def __init__(self, recognizer):
        self._recognizer = recognizer

    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            try:
                value = getattr(self._recognizer, node.attr)
                if not callable(value):
                    return ast.parse(repr(value), mode="eval").body
            except (AttributeError, SyntaxError):
                pass
        return node

class LiteralParamInliner(ast.NodeTransformer):
    """Replace named parameters with their inlined literal values."""

    def __init__(self, param_values: dict):
        self._param_values = param_values

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self._param_values:
            try:
                return ast.parse(repr(self._param_values[node.id]), mode="eval").body
            except SyntaxError:
                pass
        return node

class GlobalConstantInliner(ast.NodeTransformer):
    """Inline module-level constants (plain values with no importable origin) as literals."""

    def __init__(self, globals_: dict, local_names: set[str]):
        self._globals = globals_
        self._local = local_names

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load) or node.id in self._local:
            return node
        obj = self._globals.get(node.id)
        if obj is None or is_presidio(obj) or callable(obj) or inspect.ismodule(obj) or isinstance(obj, type):
            return node
        if inspect.getmodule(obj) is not None:
            return node
        try:
            return ast.copy_location(ast.parse(repr(obj), mode="eval").body, node)
        except (SyntaxError, ValueError):
            return node

class ArgumentSubstitutor(ast.NodeTransformer):
    """Substitute named parameters with given argument AST nodes."""

    def __init__(self, substitutions: dict[str, ast.expr]):
        self._substitutions = substitutions

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self._substitutions:
            return ast.copy_location(copy.deepcopy(self._substitutions[node.id]), node)
        return node

def local_names(func_def: ast.FunctionDef) -> set[str]:
    names = {a.arg for a in func_def.args.args}
    for node in ast.walk(func_def):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    return names

def free_names(func_def: ast.FunctionDef) -> set[str]:
    local = local_names(func_def)
    used = {
        n.id
        for n in ast.walk(func_def)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    return used - local - _BUILTINS

def resolve_imports(names: set[str], globals_: dict) -> list[str]:
    imports = []
    for name in sorted(names):
        obj = globals_.get(name)
        if obj is None or is_presidio(obj):
            continue
        if inspect.ismodule(obj):
            module_name = obj.__name__
            if name != module_name:
                imports.append(f"import {module_name} as {name}")
            else:
                imports.append(f"import {module_name}")
            continue
        if isinstance(obj, logging.Logger):
            imports.append(f"import logging\n{name} = logging.getLogger(__name__)")
            continue
        mod = inspect.getmodule(obj)
        if mod is None:
            continue
        own_mod = getattr(obj, "__module__", None) or mod.__name__
        if own_mod.startswith("_"):
            public = own_mod.lstrip("_")
            pub_mod = sys.modules.get(public)
            if pub_mod is not None and getattr(pub_mod, name, None) is obj:
                own_mod = public
        if getattr(sys.modules.get(own_mod), name, None) is not obj:
            continue
        imports.append(f"from {own_mod} import {name}")
    return imports

def drop_presidio_return_type(func_def: ast.FunctionDef, globals_: dict) -> None:
    if func_def.returns is None:
        return
    for node in ast.walk(func_def.returns):
        if isinstance(node, ast.Name) and is_presidio(globals_.get(node.id)):
            func_def.returns = None
            return

def remove_docstring(func_def: ast.FunctionDef) -> None:
    if (
        func_def.body
        and isinstance(func_def.body[0], ast.Expr)
        and isinstance(func_def.body[0].value, ast.Constant)
        and isinstance(func_def.body[0].value.value, str)
    ):
        func_def.body = func_def.body[1:]

def deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    return [i for i in items if not (i in seen or seen.add(i))]  # type: ignore[func-returns-value]
