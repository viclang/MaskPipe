# Auto-generated __init__.py for country entity subdirectories

`--update-all` regenerates `__init__.py` for every country subdirectory under `entities/` by scanning for `Entity(` assignments in each `.py` file. The root `entities/__init__.py` is updated surgically — only missing `from . import <country>` lines are inserted; existing hand-curated content is preserved. Country-level `__init__.py` files are always fully overwritten by the script.

This means country-level `__init__.py` files must not be edited by hand — any customisation (aliases, re-exports) will be lost on the next `--update-all` run. Custom imports belong in the root `entities/__init__.py` or a wrapper module.

## Considered Options

- **Manual maintenance**: full control, but country init files drift out of sync as new entities are added.
- **Auto-generated** (chosen): always in sync; no manual step needed after `--add-new`. Trade-off is that hand-written aliases in country inits are not supported.
