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
    free_names,
    resolve_imports,
    drop_presidio_return_type,
    remove_docstring,
    deduplicate,
)
from .extraction import SelfMethodInliner, PresidioReferenceInliner
from .source_cleanup import (
    RECOGNIZER_RESULT_FALLBACK,
    replace_result_objects_with_tuples,
    remove_uncalled_functions,
    inline_single_return_functions,
    remove_unused_imports,
    fix_blank_lines,
)

def extract_analyze(recognizer) -> tuple[str, list[str]]:
    method = getattr(type(recognizer), "analyze")
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)

    func_def = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    # Inline all params except `text`, which becomes the sole argument of _analyze
    params_to_inline: dict = {
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
    drop_presidio_return_type(func_def, method.__globals__)

    tree = SelfAttrInliner(recognizer).visit(tree)
    ast.fix_missing_locations(tree)

    if params_to_inline:
        tree = LiteralParamInliner(params_to_inline).visit(tree)
        ast.fix_missing_locations(tree)

    extracted_names: set[str] = {"_analyze"}
    self_method_inliner = SelfMethodInliner(recognizer, extracted_names)
    tree = self_method_inliner.visit(tree)
    ast.fix_missing_locations(tree)

    presidio_inliner = PresidioReferenceInliner(method.__globals__, extracted_names)
    tree = presidio_inliner.visit(tree)
    ast.fix_missing_locations(tree)

    imports = resolve_imports(free_names(func_def), method.__globals__)
    helper_srcs = list(self_method_inliner.helper_srcs.values()) + list(presidio_inliner.helper_srcs.values())
    src = "\n\n".join(helper_srcs + [ast.unparse(tree)])
    all_imports = deduplicate(self_method_inliner.imports + presidio_inliner.imports + imports)

    src = replace_result_objects_with_tuples(src)
    src = remove_uncalled_functions(src, keep={"_analyze"})
    src = inline_single_return_functions(src)

    if "_RecognizerResult(" in src:
        all_imports = [RECOGNIZER_RESULT_FALLBACK] + all_imports

    all_imports = remove_unused_imports(src, all_imports)
    src = fix_blank_lines(src)
    return src, all_imports
