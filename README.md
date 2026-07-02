# Matousek Partition Tree Demo

Verified proof-skeleton implementation of the two-dimensional Matousek partition-tree construction, plus a practical kd-style baseline.

This project is for computational-geometry study and demonstration. It is not a production spatial index and not a certified implementation of Matousek's theorem.

## What This Implements

The main script follows the 2D proof skeleton:

1. Dualize the input point set into lines.
2. Build a finite test set from vertices of a fixed-scale cutting.
3. Construct groups round by round using exponential weights.
4. Build weighted cuttings and verify their preconditions.
5. Double weights for crossed test lines.
6. Recurse into a partition tree.
7. Answer halfplane counting queries by prune/take/recurse.

The implementation uses exact rational arithmetic with `fractions.Fraction`.

## What This Does Not Claim

- It is not an industrial R-tree/kd-tree replacement.
- It is not a certified formal implementation of the theorem.
- It uses a bounded box model for cuttings instead of the full projective plane.
- Constants are large; the verified proof-skeleton is intentionally slow.

For practical spatial indexing, see `src/practical_partition_tree_2d.py`.

## Files

- `src/matousek_partition_tree.py` - verified proof-skeleton implementation.
- `src/practical_partition_tree_2d.py` - fast kd-style exact halfplane counter.
- `src/visualize_partition_tree_2d.py` - simple visualization helper for the practical tree.
- `docs/two_dimensional_partition_theorem_math_only.md` - math-only derivation.
- `docs/efficient_partition_trees_calculation_notes.md` - calculation notes from Matousek's paper.
- `docs/slides_lecture06_matousek_correspondence.md` - mapping from COMP5045 slides to paper content.
- `examples/points_example.csv` - small point-set input.
- `assets/partition_tree_example.png` - example visualization.

## Quick Start

Use Python 3.11+.

Run the proof-skeleton demo. This uses only the Python standard library:

```bash
python3 src/matousek_partition_tree.py 200 42
```

Expected behavior:

- builds a recursive tree,
- prints root group sizes,
- checks 60 random halfplane queries against brute force,
- prints empirical root-level crossing counts.

Run the practical kd-style baseline:

```bash
python3 src/practical_partition_tree_2d.py examples/points_example.csv --r 4 --leaf-size 2 --groups-out groups_example.json --halfplane 1 0 -5
```

Install plotting dependency only if you want visualization:

```bash
python3 -m pip install -r requirements.txt
```

Generate a visualization:

```bash
python3 src/visualize_partition_tree_2d.py examples/points_example.csv groups_example.json --out partition_tree_example.png --halfplane 1 0 -5
```

## Theory Summary

For a finite planar point set:

$$
P\subset\mathbb R^2
$$

and group-size parameter:

$$
s
$$

set:

$$
r=\frac ns
$$

The 2D partition theorem constructs a simplicial partition whose line-crossing number is:

$$
O(\sqrt r)
$$

The implementation exposes the proof mechanics behind that statement, especially:

- point-line duality,
- cuttings,
- finite test set,
- exponential reweighting,
- weighted-cutting recurrence.

## Why It Is Slow

The proof-skeleton implementation is slow because it repeatedly:

- constructs line arrangements,
- clips exact rational polygons,
- verifies weighted cutting constraints,
- refines heavy cells,
- rebuilds cuttings round by round.

This is expected. The purpose is transparency and proof correspondence, not throughput.

## Project Positioning

Use this wording in a resume or report:

> Implemented a verified proof-skeleton of the 2D Matousek partition-tree construction for halfplane range counting, including dual test-set construction, weighted cuttings, exponential reweighting, and exact query verification against brute force.

Avoid claiming:

> Production implementation of Matousek's theorem.

## Citation

Jiří Matoušek, **Efficient Partition Trees**, *Discrete & Computational Geometry* 8, 315-334, 1992.
