"""Measure the crossing-number constants of the verified construction.

For growing r, one application of the Partition Theorem is built on the
same point set, and three quantities are measured:

  K_Q        max crossings over the test set Q — what the exponential
             weights directly control; theory says O(log|Q| + sqrt r);
  random max max crossings over random query lines — controlled only
             indirectly, via the Test Set Lemma  cr(h) <= 3*K_Q + sqrt(r);
  the lemma bound itself, flagged when it exceeds the number of groups
             (vacuous: the theorem promises nothing at that scale).

This reproduces the headline empirical result: the mechanism works
(K_Q grows like sqrt r, times a measured constant of about 3-5), but with
these constants the all-lines guarantee is vacuous until r is in the
hundreds — which is precisely why no production library implements this
construction.

Usage:  python3 benchmarks/measure_crossings.py [n] [seed] [--plot out.png]
        (defaults n=1200 seed=7; full run takes a few minutes: exact
         rational arithmetic)
"""

from __future__ import annotations

import math
import random
import sys
from fractions import Fraction as F

import matousek_partition_tree as mpt

R_VALUES = (25, 36, 64)
N_QUERY_LINES = 200


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(args[0]) if args else 1200
    seed = int(args[1]) if len(args) > 1 else 7
    plot_out = None
    if "--plot" in sys.argv:
        i = sys.argv.index("--plot")
        plot_out = sys.argv[i + 1] if i + 1 < len(sys.argv) else "assets/crossing_scaling.png"

    rng = random.Random(seed)
    D = 10**4
    pts = [(F(rng.randint(0, D), D), F(rng.randint(0, D), D)) for _ in range(n)]

    rows = []
    print(f"n={n}, seed={seed}, {N_QUERY_LINES} random query lines per r\n")
    print("| r | groups | |Q| | K_Q | K_Q/sqrt(r) | random max | lemma 3K_Q+sqrt(r) |")
    print("|---|---|---|---|---|---|---|")
    for R in R_VALUES:
        s = n // R
        part, stats = mpt.simplicial_partition(pts, s, random.Random(seed))
        tris = [tri for _, tri in part]
        rand_cr = []
        for _ in range(N_QUERY_LINES):
            line = (F(rng.randint(-2 * D, 2 * D), D), F(rng.randint(-2 * D, 2 * D), D))
            rand_cr.append(sum(mpt.line_crosses_tri(line, t) for t in tris))
        kq = stats.K_Q
        lemma = 3 * kq + math.sqrt(R)
        vac = " (vacuous)" if lemma >= len(part) else ""
        rows.append((R, len(part), len(stats.Q), kq, max(rand_cr), lemma))
        print(
            f"| {R} | {len(part)} | {len(stats.Q)} | {kq} | "
            f"{kq / math.sqrt(R):.2f} | {max(rand_cr)} | "
            f"{lemma:.0f}{vac} |"
        )

    if plot_out:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        rs = [row[0] for row in rows]
        kqs = [row[3] for row in rows]
        rmaxs = [row[4] for row in rows]
        groups = [row[1] for row in rows]
        sq = [math.sqrt(R) for R in rs]
        fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
        ax.plot(rs, kqs, "o-", label="K_Q (test lines, weight-controlled)")
        ax.plot(rs, rmaxs, "s-", label="max crossings, random lines")
        ax.plot(rs, groups, ":", color="0.5", label="total groups (= r)")
        ax.plot(rs, [4 * v for v in sq], "--", label="4*sqrt(r) reference")
        ax.set_xlabel("r")
        ax.set_ylabel("simplices crossed")
        ax.set_title(f"Crossing numbers versus r (n = {n})")
        ax.legend(fontsize=9)
        fig.tight_layout()
        fig.savefig(plot_out, bbox_inches="tight")
        print(f"\nplot written: {plot_out}")


if __name__ == "__main__":
    main()
