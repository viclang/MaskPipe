"""File routing: map Presidio recognizer metadata to output paths and write entity files.

Change this file when the output directory layout or file naming conventions change.
"""
from pathlib import Path


def derive_output_path(module: str, entities_root: Path) -> Path:
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
