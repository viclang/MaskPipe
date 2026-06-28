"""Output normalization passes — exist because we care how generated code looks.

Change this file when adjusting formatting, sorting, or whitespace rules in generated entity files.
"""
import ast
import re


def fix_blank_lines(src: str) -> str:
    src = re.sub(r'\n+(def |class )', r'\n\n\1', src)
    return src.lstrip('\n')


def _natural_sort_key(node: ast.expr) -> tuple:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return (0, node.value, "")
        if isinstance(node.value, str):
            parts = re.split(r'(\d+)', node.value)
            return (1,) + tuple(int(p) if p.isdigit() else p.lower() for p in parts)
    return (2, 0, ast.unparse(node))


class _SetLiteralSorter(ast.NodeTransformer):
    def visit_Set(self, node: ast.Set) -> ast.Set:
        self.generic_visit(node)
        try:
            node.elts = sorted(node.elts, key=_natural_sort_key)
        except Exception:
            pass
        return node


def sort_set_literals(src: str) -> str:
    """Sort set literal elements in natural order (numeric chunks sorted as ints) for deterministic output."""
    tree = ast.parse(src)
    _SetLiteralSorter().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
