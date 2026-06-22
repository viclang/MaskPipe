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
# Capabilities
# ---------------------------------------------------------------------------

def collect_recognizer_subclasses(root: type) -> set[type]:
    return set(root.__subclasses__()).union(
        s for c in root.__subclasses__() for s in collect_recognizer_subclasses(c)
    )

def find_recognizer_class(name: str, candidates: set[type]) -> type:
    for cls in candidates:
        if cls.__name__ == name:
            return cls
    raise ValueError(f"'{name}' not found among EntityRecognizer subclasses")

def import_recognizer_class(dotted_path: str) -> type:
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
        cls = import_recognizer_class(spec)
    else:
        cls = find_recognizer_class(spec, collect_recognizer_subclasses(EntityRecognizer))
    return cls()

_COUNTRY_LABEL_PREFIXES: dict[str, str] = {
    "us": "us_", "australia": "au_", "uk": "uk_", "india": "in_",
    "singapore": "sg_", "italy": "it_", "spain": "es_", "poland": "pl_",
    "netherlands": "nl_",
}

_REPO_ROOT = Path(__file__).parent.parent

def derive_output_path(label: str, module: str, repo_root: Path) -> Path:
    parts = module.split(".")
    subdir = ""
    if "country_specific" in parts:
        idx = parts.index("country_specific")
        if idx + 1 < len(parts):
            subdir = parts[idx + 1]

    name = label.lower()
    prefix = _COUNTRY_LABEL_PREFIXES.get(subdir, "")
    if prefix and name.startswith(prefix):
        name = name[len(prefix):]

    return repo_root / "src" / "maskpipe" / "entities" / subdir / (name + ".py")

def write_entity_file(source: str, path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

# ---------------------------------------------------------------------------
# Orchestrator (CLI)
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

    try:
        recognizer = resolve_recognizer(args.recognizer)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    converter = PresidioConverter(context_boost=args.context_boost)
    source = generate(recognizer, converter)

    if args.stdout:
        sys.stdout.buffer.write(source.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        return

    out = (
        Path(args.out) if args.out
        else derive_output_path(
            recognizer.supported_entities[0],
            type(recognizer).__module__,
            _REPO_ROOT,
        )
    )

    try:
        write_entity_file(source, out, force=args.force)
    except FileExistsError:
        print(f"error: {out} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    print(f"written to {out}", file=sys.stderr)

if __name__ == "__main__":
    main()
