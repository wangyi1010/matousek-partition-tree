# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and this project
follows semantic versioning.

## [0.4.0] — 2026-07-10

Narrowed to the faithful theorem only.

### Removed
- The practical kd-style baseline (`practical.py`, `practical_cli.py`, the
  `practical-tree` console script, and their test) and the `examples/`
  directory that only served it. This repository is now exclusively the
  exact-arithmetic, verified proof-faithful construction. The fast,
  no-guarantee counterpart is out of scope here.

## [0.3.0] — 2026-07-03

Production restructure: flat scripts become an installable package.

### Changed
- **Package layout**: `src/matousek_partition_tree/` with `core.py`
  (verified construction), `practical.py` (kd-style baseline, previously
  `practical_partition_tree_2d.py`), and CLI modules. One top-level
  package, one wheel — the baseline is a submodule, not a second package.
- **`simplicial_partition()` returns `(groups, PartitionStats)`** instead
  of setting the module-level `LAST_STATS` global. `PartitionStats` is a
  frozen dataclass with tuple fields (deeply immutable). This is the
  breaking API change of this release.
- Library code logs via `logging.getLogger(__name__)`; `print()` remains
  only in the CLI modules.
- `zip(..., strict=True)` wherever equal lengths are an invariant — a
  mismatch is a bug and should raise, not be silenced.
- Type aliases (`Point`, `Line`, `Halfplane`) via `TypeAlias`.
  NamedTuple was evaluated and rejected with measurement: attribute
  access is cost-free here (exact-rational arithmetic dominates), but
  construction is ~1.25x slower and the innermost loops construct points.
- Build system: hatchling; console scripts `matousek-demo` and
  `practical-tree`; project renamed `matousek-partition-tree-demo` →
  `matousek-partition-tree`.
- CI: separate lint job (ruff check + format), tests run against the
  installed package (`pip install -e ".[dev]"`), coverage gate enforced
  (threshold set from a measured baseline, not aspiration), demos run
  via the console scripts.
- Classifier is `Development Status :: 3 - Alpha` — consistent with the
  README's own "not production" disclaimers.

### Removed
- `LAST_STATS` module global (see above).
- `tests/conftest.py` sys.path hack: tests now import the installed
  package, so a broken wheel configuration fails CI instead of being
  masked.
- `src/visualize_partition_tree_2d.py`: visualizer for the old
  flat-script CSV/JSON workflow, superseded by `visualize_matousek.py`.
- mypy configuration: it was not enforced in CI, and unenforced strict
  config rots. Type hints remain best-effort; a checked mypy job can be
  added later together with the work to make it pass.

### Fixed
- `practical` CSV loader no longer crashes on an empty file
  (`reader.fieldnames` is `None`).

## [0.2.0] — 2026-07-02

- Practical kd-style baseline, three-panel partition figure generated
  from the verified code, crossing-number benchmark and scaling plot,
  postcondition property tests, CI, story-first README, GitHub math
  rendering fixes across all docs, typeset PDF versions of the docs.

## [0.1.0] — 2026-07-02

- Initial verified proof-skeleton implementation of the 2D Matoušek
  Partition Theorem: exact rational arithmetic, two-level
  Chazelle–Friedman weighted cuttings with runtime verification, fixed-β
  test sets, exponential reweighting, partition tree, exact halfplane
  counting queries.
