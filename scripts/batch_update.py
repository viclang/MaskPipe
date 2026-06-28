"""Bulk regeneration of entity files from Presidio recognizers.

Change this file when the update strategy or init-refresh logic needs to change.
"""
import sys
from pathlib import Path

from codegen import generate, GENERATED_MARKER
from paths import derive_output_path, write_entity_file
from presidio_analyzer import EntityRecognizer
from presidio_converter import PresidioConverter
from resolve_recognizer import collect_recognizer_subclasses, resolve_recognizer
from update_init import refresh_country_init, refresh_root_init, update_gen_blocks


def update_all(entities_root: Path, context_boost: float, *, add_new: bool = False) -> None:
    """Re-generate existing generated entity files, optionally adding new ones from presidio_analyzer."""
    converter = PresidioConverter(context_boost=context_boost)
    errors: list[str] = []

    # Phase 1: re-generate existing generated files; track covered recognizer classes
    covered: set[str] = set()
    for path in sorted(entities_root.rglob("*.py")):
        first_line = path.read_text(encoding="utf-8").split("\n", 1)[0]
        if not first_line.startswith(GENERATED_MARKER):
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
        write_entity_file(source, path, force=True)
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
                cls.__module__,
                entities_root,
            )
            if out.exists():
                continue  # hand-written file takes precedence — skip
            source = generate(recognizer, converter)
            write_entity_file(source, out, force=True)
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
