"""Generate a native maskpipe Entity from a Presidio PatternRecognizer.

Usage:
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass>
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass> --out src/maskpipe/entities/us/ssn.py
    python scripts/gen_entity.py <dotted.path.to.RecognizerClass> --context-boost 0.4
    python scripts/gen_entity.py --update-all   # re-generate all previously generated entities

Example:
    python scripts/gen_entity.py \\
        presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer.UsSsnRecognizer
"""
import argparse
import importlib
import re
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

_REPO_ROOT = Path(__file__).parent.parent

def derive_output_path(label: str, module: str, entities_root: Path) -> Path:
    parts = module.split(".")
    subdir = ""
    if "country_specific" in parts:
        idx = parts.index("country_specific")
        if idx + 1 < len(parts):
            subdir = parts[idx + 1]

    # Derive filename from the recognizer module file, stripping only the _recognizer suffix.
    # e.g. us_bank_recognizer → us_bank, aba_routing_recognizer → aba_routing
    name = parts[-1].removesuffix("_recognizer")

    return entities_root / subdir / (name + ".py")

def write_entity_file(source: str, path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

_GENERATED_MARKER = '"""Entity generated from presidio_analyzer.'

# ---------------------------------------------------------------------------
# __init__.py maintenance
# ---------------------------------------------------------------------------

_ENTITY_VAR_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=\s*Entity\(', re.MULTILINE)
_GEN_BLOCK_RE = re.compile(r'([ \t]*)# BEGIN GENERATED: (\w+)\n(.*?)\n\1# END GENERATED: \2', re.DOTALL)

def update_gen_blocks(old_source: str, new_source: str) -> str:
    """Splice GEN blocks from new_source into old_source, leaving everything else untouched.

    Falls back to full replacement when no old block names match the new source
    (e.g. after a block rename), so migration is automatic.
    """
    new_blocks = {m.group(2): m.group(0) for m in _GEN_BLOCK_RE.finditer(new_source)}
    old_names = {m.group(2) for m in _GEN_BLOCK_RE.finditer(old_source)}
    if old_names - new_blocks.keys():  # stale block names → migrate via full replacement
        return new_source
    return _GEN_BLOCK_RE.sub(
        lambda m: new_blocks.get(m.group(2), m.group(0)),
        old_source,
    )

def _find_entity_exports(path: Path) -> list[str]:
    return _ENTITY_VAR_RE.findall(path.read_text(encoding="utf-8"))

def refresh_country_init(directory: Path) -> bool:
    """Generate or overwrite __init__.py for a country entity subdirectory.

    Scans all .py files in the directory, collects Entity variable names, and
    writes a clean __init__.py with imports and __all__.  Returns True when the
    file is newly created (so the caller can register the new subpackage).
    """
    exports: list[tuple[str, str]] = []
    for py_file in sorted(directory.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        for var in _find_entity_exports(py_file):
            exports.append((py_file.stem, var))

    if not exports:
        return False

    init_path = directory / "__init__.py"
    was_new = not init_path.exists()

    lines = ["# auto-generated by gen_entity.py — do not edit by hand"]
    for module, var in exports:
        lines.append(f"from .{module} import {var}")
    lines.append("")
    lines.append("__all__ = [")
    for _, var in exports:
        lines.append(f'    "{var}",')
    lines.append("]")

    init_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return was_new

def refresh_root_init(entities_root: Path, new_packages: set[str]) -> None:
    """Add missing country subpackage imports to the root entities __init__.py."""
    if not new_packages:
        return
    init_path = entities_root / "__init__.py"
    if not init_path.exists():
        return
    content = init_path.read_text(encoding="utf-8")
    already = set(re.findall(r'from \. import (\w+)', content))
    missing = sorted(new_packages - already)
    if not missing:
        return

    lines = content.splitlines()
    # Insert after the last "from . import" line
    last_import_idx = max(
        (i for i, ln in enumerate(lines) if ln.startswith("from . import ")),
        default=-1,
    )
    lines[last_import_idx + 1:last_import_idx + 1] = [f"from . import {pkg}" for pkg in missing]

    # Add to __all__
    all_start = next((i for i, ln in enumerate(lines) if ln.strip() == "__all__ = ["), None)
    if all_start is not None:
        close = next(i for i in range(all_start, len(lines)) if lines[i].strip() == "]")
        lines[close:close] = [f'    "{pkg}",' for pkg in missing]

    init_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"updated entities/__init__.py with: {', '.join(missing)}", file=sys.stderr)


def update_all(entities_root: Path, context_boost: float, *, add_new: bool = False) -> None:
    """Re-generate existing generated entity files, optionally adding new ones from presidio_analyzer."""
    converter = PresidioConverter(context_boost=context_boost)
    errors: list[str] = []

    # Phase 1: re-generate existing generated files; track covered recognizer classes
    covered: set[str] = set()
    for path in sorted(entities_root.rglob("*.py")):
        first_line = path.read_text(encoding="utf-8").split("\n", 1)[0]
        if not first_line.startswith(_GENERATED_MARKER):
            continue
        dotted_path = first_line[len('"""Entity generated from '):].rstrip('."')
        covered.add(dotted_path)
        try:
            recognizer = resolve_recognizer(dotted_path)
        except ValueError as e:
            errors.append(f"  {path.relative_to(entities_root)}: {e}")
            continue
        old_source = path.read_text(encoding="utf-8")
        source = generate(recognizer, converter)
        if "# BEGIN GENERATED:" in old_source:
            source = update_gen_blocks(old_source, source)
        path.write_text(source, encoding="utf-8")
        print(f"updated {path.relative_to(entities_root)}", file=sys.stderr)

    # Phase 2 (opt-in): generate files for Presidio recognizers not yet present
    if add_new:
        for cls in sorted(collect_recognizer_subclasses(EntityRecognizer), key=lambda c: c.__name__):
            if "generic" not in cls.__module__ and "country_specific" not in cls.__module__:
                continue
            dotted_path = f"{cls.__module__}.{cls.__name__}"
            if dotted_path in covered:
                continue  # already handled in phase 1
            try:
                recognizer = cls()
                if not recognizer.supported_entities:
                    continue
            except Exception:
                continue
            out = derive_output_path(
                recognizer.supported_entities[0],
                cls.__module__,
                entities_root,
            )
            if out.exists():
                continue  # hand-written file takes precedence — skip
            source = generate(recognizer, converter)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(source, encoding="utf-8")
            print(f"added {out.relative_to(entities_root)}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for msg in errors:
            print(msg, file=sys.stderr)
        sys.exit(1)

    # Refresh __init__.py for every country subdirectory that has entity files.
    new_packages: set[str] = set()
    for subdir in sorted(entities_root.iterdir()):
        if subdir.is_dir() and any(p for p in subdir.glob("*.py") if p.name != "__init__.py"):
            was_new = refresh_country_init(subdir)
            if was_new:
                new_packages.add(subdir.name)
            print(f"refreshed {subdir.name}/__init__.py", file=sys.stderr)
    refresh_root_init(entities_root, new_packages)

# ---------------------------------------------------------------------------
# Orchestrator (CLI)
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a native maskpipe Entity from a Presidio PatternRecognizer or EntityRecognizer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("recognizer", nargs="?", help="Dotted path to the recognizer class")
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
    parser.add_argument(
        "--entities-root", metavar="DIR",
        default=str(_REPO_ROOT / "src" / "maskpipe" / "entities"),
        help="Root directory for entity files (default: src/maskpipe/entities)",
    )
    parser.add_argument(
        "--update-all", action="store_true",
        help="Re-generate all entity files originally produced by this script.",
    )
    parser.add_argument(
        "--add-new", action="store_true",
        help="Used with --update-all: also generate files for Presidio recognizers not yet present.",
    )
    args = parser.parse_args()
    entities_root = Path(args.entities_root)

    if args.update_all:
        update_all(entities_root, args.context_boost, add_new=args.add_new)
        return

    if not args.recognizer:
        parser.error("recognizer is required unless --update-all is specified")

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
            entities_root,
        )
    )

    try:
        write_entity_file(source, out, force=args.force)
    except FileExistsError:
        print(f"error: {out} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    print(f"written to {out}", file=sys.stderr)

    # Update __init__.py for the target directory (country subdirs only).
    if out.parent != entities_root:
        was_new = refresh_country_init(out.parent)
        if was_new:
            refresh_root_init(entities_root, {out.parent.name})

if __name__ == "__main__":
    main()
