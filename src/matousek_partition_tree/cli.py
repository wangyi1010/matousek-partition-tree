"""Demo CLI for the verified construction (console script: matousek-demo).

Builds a tree at r = 64 (beta*sqrt(r) > 1, so the test-set cutting is
nontrivial and the full mechanism is exercised), verifies 60 random
halfplane queries against brute force, and prints measured root-level
crossing numbers against the nominal O(sqrt r) bound.
"""

from __future__ import annotations

import math
import random
import sys
from fractions import Fraction as F

from matousek_partition_tree.core import (
    build_tree,
    crossing_number,
    halfplane_side,
    query_count,
)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    rng = random.Random(seed)
    D = 10**4
    pts = [(F(rng.randint(0, D), D), F(rng.randint(0, D), D)) for _ in range(n)]

    R = 64
    tree = build_tree(pts, r=R, leaf_size=32, rng=random.Random(seed))
    print(f"built: n={n}, r={R}, root children={len(tree.children)}")
    sizes = sorted(ch.count for ch in tree.children)
    print(f"root group sizes: {sizes}  (target [s,2s) = [{n // R},{2 * (n // R)}))")

    bad = 0
    for _ in range(60):
        a = F(rng.randint(-D, D), D)
        b = F(rng.randint(-D, D), D)
        c = F(rng.randint(-D, D), D)
        if a == 0 and b == 0:
            continue
        h = (a, b, c)
        exact = sum(halfplane_side(h, p) >= 0 for p in pts)
        got = query_count(tree, h)
        bad += got != exact
    print(f"query check vs brute force: {60 - bad}/60 exact matches")

    crossings = []
    for _ in range(300):
        m = F(rng.randint(-2 * D, 2 * D), D)
        c0 = F(rng.randint(-2 * D, 2 * D), D)
        crossings.append(crossing_number(tree, (m, c0)))
    mx, avg = max(crossings), sum(crossings) / len(crossings)
    print(
        f"root-level crossings over 300 random lines: max={mx}, "
        f"avg={avg:.2f}, bound O(sqrt r)=O({math.sqrt(R):.2f}) "
        f"(out of {len(tree.children)} simplices)"
    )


if __name__ == "__main__":
    main()
