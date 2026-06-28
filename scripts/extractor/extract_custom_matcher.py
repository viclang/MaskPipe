"""Extract the Presidio analyze method as a standalone _analyze(text: str) function.

Change this file when presidio changes the analyze method signature (e.g. new params,
renamed NlpArtifacts, changed entities param behaviour).
"""
import ast
import inspect
import textwrap

from .ast_utils import (
    SelfAttrInliner,
    LiteralParamInliner,
    GlobalConstantInliner,
    free_names,
    local_names,
    resolve_imports,
    drop_presidio_return_type,
    remove_docstring,
    deduplicate,
)
from .extraction import SelfMethodInliner, PresidioReferenceInliner
from .presidio_fixes import (
    RECOGNIZER_RESULT_FALLBACK,
    replace_result_objects_with_tuples,
    remove_uncalled_functions,
    inline_single_return_functions,
    remove_unused_imports,
    fix_blank_lines,
)

def _parse_analyze_method(recognizer) -> tuple[ast.Module, ast.FunctionDef, dict]:
    """Get the analyze method's AST, the top-level FunctionDef, and its globals."""
    method = getattr(type(recognizer), "analyze")
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)
    func_def = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
    if func_def is None:
        raise ValueError(f"No FunctionDef found in source of {type(recognizer).__name__}.analyze")
    return tree, func_def, method.__globals__

def _prepare_func_def(func_def: ast.FunctionDef, recognizer, globals_: dict) -> dict:
    """Strip non-text params, rename to _analyze, drop docstring and presidio return type. Returns params_to_inline."""
    params_to_inline = {
        arg.arg: (recognizer.supported_entities if arg.arg == "entities" else None)
        for arg in func_def.args.args
        if arg.arg not in ("self", "text")
    }
    func_def.args.args = [a for a in func_def.args.args if a.arg == "text"]
    func_def.args.defaults = []
    func_def.args.kwonlyargs = []
    func_def.args.kw_defaults = []
    remove_docstring(func_def)
    func_def.name = "_analyze"
    drop_presidio_return_type(func_def, globals_)
    return params_to_inline

def _apply_self_transforms(
    tree: ast.Module,
    recognizer,
    params_to_inline: dict,
    extracted_names: set[str],
) -> tuple[ast.Module, list[str], list[str]]:
    """Apply SelfAttrInliner, LiteralParamInliner, SelfMethodInliner. Returns (tree, helper_srcs, imports)."""
    tree = SelfAttrInliner(recognizer).visit(tree)
    ast.fix_missing_locations(tree)
    if params_to_inline:
        tree = LiteralParamInliner(params_to_inline).visit(tree)
        ast.fix_missing_locations(tree)
    self_inliner = SelfMethodInliner(recognizer, extracted_names)
    tree = self_inliner.visit(tree)
    ast.fix_missing_locations(tree)
    return tree, list(self_inliner.helper_srcs.values()), self_inliner.imports

def _apply_presidio_transforms(
    tree: ast.Module,
    func_def: ast.FunctionDef,
    globals_: dict,
    extracted_names: set[str],
) -> tuple[ast.Module, list[str], list[str]]:
    """Apply PresidioReferenceInliner and GlobalConstantInliner. Returns (tree, helper_srcs, imports)."""
    presidio_inliner = PresidioReferenceInliner(globals_, extracted_names)
    tree = presidio_inliner.visit(tree)
    ast.fix_missing_locations(tree)
    tree = GlobalConstantInliner(globals_, local_names(func_def)).visit(tree)
    ast.fix_missing_locations(tree)
    return tree, list(presidio_inliner.helper_srcs.values()), presidio_inliner.imports

def _assemble_source(
    tree: ast.Module,
    func_def: ast.FunctionDef,
    globals_: dict,
    helper_srcs: list[str],
    raw_imports: list[str],
) -> tuple[str, list[str]]:
    """Resolve remaining imports, join source, and run post-processing passes."""
    imports = resolve_imports(free_names(func_def), globals_)
    src = "\n\n".join(helper_srcs + [ast.unparse(tree)])
    all_imports = deduplicate(raw_imports + imports)
    src = replace_result_objects_with_tuples(src)
    src = remove_uncalled_functions(src, keep={"_analyze"})
    src = inline_single_return_functions(src, keep={"_analyze"})
    if "_RecognizerResult(" in src:
        all_imports = [RECOGNIZER_RESULT_FALLBACK] + all_imports
    all_imports = remove_unused_imports(src, all_imports)
    src = fix_blank_lines(src)
    return src, all_imports

def extract_custom_matcher(recognizer) -> tuple[str, list[str]]:
    tree, func_def, globals_ = _parse_analyze_method(recognizer)
    params_to_inline = _prepare_func_def(func_def, recognizer, globals_)
    extracted_names: set[str] = {"_analyze"}

    tree, self_helpers, self_imports = _apply_self_transforms(tree, recognizer, params_to_inline, extracted_names)
    tree, presidio_helpers, presidio_imports = _apply_presidio_transforms(tree, func_def, globals_, extracted_names)

    return _assemble_source(
        tree, func_def, globals_,
        helper_srcs=self_helpers + presidio_helpers,
        raw_imports=self_imports + presidio_imports,
    )
