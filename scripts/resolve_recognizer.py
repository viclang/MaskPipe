"""Locate and instantiate Presidio EntityRecognizer subclasses by name or dotted path.

Change this file when Presidio restructures its module hierarchy or subclass registration.
"""
import importlib

from presidio_analyzer import EntityRecognizer


def collect_recognizer_subclasses(root: type) -> set[type]:
    return set(root.__subclasses__()).union(
        s for c in root.__subclasses__() for s in collect_recognizer_subclasses(c)
    )


def _find_recognizer_class(name: str, candidates: set[type]) -> type:
    for cls in candidates:
        if cls.__name__ == name:
            return cls
    raise ValueError(f"'{name}' not found among EntityRecognizer subclasses")


def _import_recognizer_class(dotted_path: str) -> type:
    module_path, _, class_name = dotted_path.rpartition(".")
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise ValueError(f"cannot import module '{module_path}': {e}") from e
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ValueError(f"'{class_name}' not found in '{module_path}'")


def resolve_recognizer(spec: str) -> EntityRecognizer:
    if "." in spec:
        cls = _import_recognizer_class(spec)
    else:
        cls = _find_recognizer_class(spec, collect_recognizer_subclasses(EntityRecognizer))
    return cls()
