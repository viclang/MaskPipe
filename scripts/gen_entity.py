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
import sys
from pathlib import Path

# scripts/ is not a package, so add it to sys.path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from codegen import generate  # noqa: E402
from paths import derive_output_path, write_entity_file  # noqa: E402
from update_init import refresh_country_init, refresh_root_init  # noqa: E402

try:
    from presidio_converter import PresidioConverter
    from resolve_recognizer import resolve_recognizer
    from batch_update import update_all
    import presidio_analyzer.predefined_recognizers  # noqa: F401 — registers all subclasses
except ImportError:
    print("error: presidio-analyzer is required. Install with: uv sync --group codegen", file=sys.stderr)
    sys.exit(1)

_REPO_ROOT = Path(__file__).parent.parent


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
