"""Core extraction machinery: turn Presidio recognizer methods into standalone functions.

SelfMethodInliner and PresidioReferenceInliner live here together because they are
mutually recursive — each calls the extraction functions defined below them.
"""
import ast
import inspect
import logging
import textwrap

from presidio_analyzer import RecognizerResult as _RC

logger = logging.getLogger(__name__)

from .ast_utils import (
    _is_presidio,
    SelfAttrInliner,
    GlobalConstantInliner,
    local_names,
    free_names,
    resolve_imports,
    drop_presidio_return_type,
    remove_docstring,
    deduplicate,
)
from .source_cleanup import wrap_bool_returns, remove_unused_imports

class SelfMethodInliner(ast.NodeTransformer):
    """Replace self.method(args) with extracted helper _method(args)."""

    def __init__(self, recognizer, extracted_names: set[str]):
        self._recognizer = recognizer
        self._extracted_names = extracted_names
        self.helper_srcs: dict[str, str] = {}
        self.imports: list[str] = []

    def visit_Call(self, node):
        self.generic_visit(node)
        if not (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            return node

        attr_name = node.func.attr
        # Python name mangling: `__foo` in a class body is stored as `_ClassName__foo`
        real_attr = (
            f"_{type(self._recognizer).__name__}{attr_name}"
            if attr_name.startswith("__") and not attr_name.endswith("__")
            else attr_name
        )
        helper_name = "_" + attr_name.lstrip("_")

        try:
            value = getattr(self._recognizer, real_attr)
            if not callable(value):
                return node
            if helper_name not in self._extracted_names:
                src, imports = extract_instance_method(self._recognizer, real_attr, helper_name, self._extracted_names)
                self.helper_srcs[helper_name] = src
                self.imports.extend(imports)
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id=helper_name, ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                ),
                node,
            )
        except Exception:
            logger.exception("SelfMethodInliner: failed to extract %s.%s", type(self._recognizer).__name__, attr_name)
            return node

class PresidioReferenceInliner(ast.NodeTransformer):
    """Remove all presidio dependencies from extracted code:
    - PresidioClass.method(args)                → extracted helper _method(args)
    - PresidioClass.CONSTANT                    → inlined literal value
    - RecognizerResult(start=X, end=Y, score=Z) → _RecognizerResult(start=X, end=Y, score=Z)
    - OtherPresidioClass(args)                  → SimpleNamespace(args)
    - EntityRecognizer.remove_duplicates(x)     → x
    """

    def __init__(self, globals_: dict, extracted_names: set[str]):
        self._globals = globals_
        self._extracted_names = extracted_names
        self.helper_srcs: dict[str, str] = {}
        self.imports: list[str] = []

    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name):
            cls_obj = self._globals.get(node.value.id)
            if cls_obj is not None and _is_presidio(cls_obj) and isinstance(cls_obj, type):
                try:
                    value = getattr(cls_obj, node.attr)
                    if not callable(value):
                        return ast.parse(repr(value), mode="eval").body
                except AttributeError:
                    pass
        return node

    def visit_Call(self, node):
        self.generic_visit(node)

        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            cls_obj = self._globals.get(node.func.value.id)
            if cls_obj is not None and _is_presidio(cls_obj):
                method_name = node.func.attr
                if method_name == "remove_duplicates" and node.args:
                    return node.args[0]
                real_method = (
                    f"_{cls_obj.__name__}{method_name}"
                    if method_name.startswith("__") and not method_name.endswith("__")
                    else method_name
                )
                helper_name = f"_{method_name.lstrip('_')}"
                if helper_name not in self._extracted_names:
                    self._extracted_names.add(helper_name)
                    try:
                        func = getattr(cls_obj, real_method)
                        src, imports = extract_static_method(func, helper_name, self._extracted_names)
                        self.helper_srcs[helper_name] = src
                        self.imports.extend(imports)
                    except Exception:
                        logger.exception("PresidioReferenceInliner: failed to extract %s.%s", cls_obj.__name__, real_method)
                        return node
                return ast.copy_location(
                    ast.Call(
                        func=ast.Name(id=helper_name, ctx=ast.Load()),
                        args=node.args,
                        keywords=node.keywords,
                    ),
                    node,
                )

        if isinstance(node.func, ast.Name):
            cls_obj = self._globals.get(node.func.id)
            if cls_obj is not None and _is_presidio(cls_obj) and isinstance(cls_obj, type):
                if cls_obj is _RC:
                    replacement_name = "_RecognizerResult"
                else:
                    self.imports.append("from types import SimpleNamespace")
                    replacement_name = "SimpleNamespace"
                return ast.copy_location(
                    ast.Call(
                        func=ast.Name(id=replacement_name, ctx=ast.Load()),
                        args=node.args,
                        keywords=node.keywords,
                    ),
                    node,
                )

        return node

def _finalize_extracted_function(
    tree: ast.Module,
    func_def: ast.FunctionDef,
    globals_: dict,
    extracted_names: set[str],
    prior_helper_srcs: list[str],
    prior_imports: list[str],
) -> tuple[str, list[str]]:
    """Apply Presidio + GlobalConstant inlining, resolve imports, and assemble source."""
    presidio_inliner = PresidioReferenceInliner(globals_, extracted_names)
    tree = presidio_inliner.visit(tree)
    ast.fix_missing_locations(tree)
    tree = GlobalConstantInliner(globals_, local_names(func_def)).visit(tree)
    ast.fix_missing_locations(tree)
    imports = resolve_imports(free_names(func_def), globals_)
    helper_srcs = prior_helper_srcs + list(presidio_inliner.helper_srcs.values())
    src = wrap_bool_returns("\n\n".join(helper_srcs + [ast.unparse(tree)]))
    all_imports = remove_unused_imports(src, deduplicate(prior_imports + presidio_inliner.imports + imports))
    return src, all_imports

def extract_static_method(func, func_name: str, extracted_names: set[str]) -> tuple[str, list[str]]:
    """Extract a plain function or staticmethod as a self-contained helper."""
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    func_def = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
    if func_def is None:
        raise ValueError(f"No FunctionDef found in source of {func.__qualname__}")
    func_def.decorator_list = []
    remove_docstring(func_def)
    func_def.name = func_name
    drop_presidio_return_type(func_def, func.__globals__)
    return _finalize_extracted_function(tree, func_def, func.__globals__, extracted_names, [], [])

def extract_instance_method(
    recognizer,
    method_name: str,
    func_name: str,
    extracted_names: set[str] | None = None,
) -> tuple[str, list[str]]:
    """Extract a recognizer instance method as a self-contained standalone function."""
    if extracted_names is None:
        extracted_names = set()
    extracted_names.add(func_name)

    method = getattr(type(recognizer), method_name)
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)
    func_def = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
    if func_def is None:
        raise ValueError(f"No FunctionDef found in source of {type(recognizer).__name__}.{method_name}")
    func_def.args.args = [a for a in func_def.args.args if a.arg != "self"]
    func_def.decorator_list = []
    remove_docstring(func_def)
    func_def.name = func_name
    drop_presidio_return_type(func_def, method.__globals__)

    tree = SelfAttrInliner(recognizer).visit(tree)
    ast.fix_missing_locations(tree)
    self_inliner = SelfMethodInliner(recognizer, extracted_names)
    tree = self_inliner.visit(tree)
    ast.fix_missing_locations(tree)

    return _finalize_extracted_function(
        tree, func_def, method.__globals__, extracted_names,
        prior_helper_srcs=list(self_inliner.helper_srcs.values()),
        prior_imports=self_inliner.imports,
    )
