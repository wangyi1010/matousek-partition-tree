# Contributing

## Setup

```bash
git clone https://github.com/wangyi1010/matousek-partition-tree
cd matousek-partition-tree
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,viz]"
```

## Workflow

Before pushing:

```bash
ruff check src/ tests/ benchmarks/
ruff format src/ tests/ benchmarks/
pytest tests/ --cov --cov-report=term-missing
```

CI runs the same three steps plus both CLI demos; the coverage gate in
`pyproject.toml` is a measured baseline — if you add code, add tests that
keep it honest rather than lowering the gate.

## Conventions

- Exact rational arithmetic (`fractions.Fraction`) in all geometry — no
  floats in predicates. Floats are allowed only for extent estimation
  (`combinatorial_box`) and plotting.
- The verified construction fails loudly: precondition violations raise
  `CuttingError` / `TestSetError`, never degrade silently. Keep it that
  way — a "fix" that weakens a runtime check needs a proof-side argument.
- `zip(..., strict=True)` when equal lengths are an invariant.
- Library modules log via `logging`; only CLI modules print.
- No module-level mutable state.
- Docstrings tie code to the proof (Step 1 / Step 3+4 / lemma names);
  when you change behavior, update the corresponding docstring claim.

## Docs

`docs/*.md` are GitHub-armored (see the math-rendering commit messages
for the full list of GitHub quirks). The typeset PDFs are built with
pandoc + XeLaTeX from de-armored Markdown; rebuild commands are in the
git history of `docs/`.
