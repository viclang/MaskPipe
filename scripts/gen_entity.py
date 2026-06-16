"""Generate a native maskpipe Entity from a Presidio PatternRecognizer.

Usage:
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass>
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass> --out src/maskpipe/entities/us/generated.py
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass> --context-boost 0.4

Example:
    python scripts/gen_entity.py \\
        presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer.UsSsnRecognizer
"""
import argparse
import importlib
import sys
from pathlib import Path

from maskpipe.presidio import PresidioConverter

try:
    from presidio_analyzer import EntityRecognizer, PatternRecognizer
    import presidio_analyzer.predefined_recognizers  # noqa: F401 — registers all subclasses
except ImportError:
    print("error: presidio-analyzer is required. Install with: pip install maskpipe[presidio]", file=sys.stderr)
    sys.exit(1)

# scripts/ is not a package, so add it to sys.path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from codegen import generate  # noqa: E402

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _all_recognizer_subclasses(cls=None):
    if cls is None:
        cls = EntityRecognizer
    return set(cls.__subclasses__()).union(
        s for c in cls.__subclasses__() for s in _all_recognizer_subclasses(c)
    )

def _find_recognizer_class(name: str):
    for cls in _all_recognizer_subclasses():
        if cls.__name__ == name:
            return cls
    raise SystemExit(f"error: '{name}' not found among EntityRecognizer subclasses")

def _load_recognizer(dotted_path: str):
    if "." not in dotted_path:
        return _find_recognizer_class(dotted_path)()
    module_path, _, class_name = dotted_path.rpartition(".")
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise SystemExit(f"error: cannot import module '{module_path}': {e}")
    try:
        cls = getattr(module, class_name)
    except AttributeError:
        raise SystemExit(f"error: '{class_name}' not found in '{module_path}'")
    return cls()

# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------

_COUNTRY_PREFIXES: dict[str, str] = {
    "us": "us_", "australia": "au_", "uk": "uk_", "india": "in_",
    "singapore": "sg_", "italy": "it_", "spain": "es_", "poland": "pl_",
    "netherlands": "nl_",
}

_REPO_ROOT = Path(__file__).parent.parent

def _default_out_path(recognizer) -> Path:
    module = type(recognizer).__module__
    label = recognizer.supported_entities[0]

    parts = module.split(".")
    subdir = "generated"
    if "country_specific" in parts:
        idx = parts.index("country_specific")
        if idx + 1 < len(parts):
            subdir = parts[idx + 1]

    name = label.lower()
    prefix = _COUNTRY_PREFIXES.get(subdir, "")
    if prefix and name.startswith(prefix):
        name = name[len(prefix):]

    return _REPO_ROOT / "src" / "maskpipe" / "entities" / subdir / (name + ".py")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a native maskpipe Entity from a Presidio PatternRecognizer or EntityRecognizer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("recognizer", help="Dotted path to the recognizer class")
    parser.add_argument(
        "--out", metavar="FILE",
        help="Output path (default: src/maskpipe/entities/<country>/<name>.py)",
    )
    parser.add_argument(
        "--stdout", action="store_true",
        help="Print to stdout instead of writing a file",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite the output file if it already exists",
    )
    parser.add_argument(
        "--context-boost", type=float, default=0.35, metavar="SCORE",
        help="Score added to context patterns (default: 0.35)",
    )
    args = parser.parse_args()

    recognizer = _load_recognizer(args.recognizer)
    converter = PresidioConverter(context_boost=args.context_boost)
    source = generate(recognizer, converter)

    if args.stdout:
        print(source)
        return

    out = Path(args.out) if args.out else _default_out_path(recognizer)
    if out.exists() and not args.force:
        print(f"error: {out} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"written to {out}", file=sys.stderr)

if __name__ == "__main__":
    main()
