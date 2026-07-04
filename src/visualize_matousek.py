"""Render the root-level simplicial partition of the verified Matousek
construction (matousek_partition_tree.py) as a figure for the README.

Reproduces the demo setting: n = 1200 uniform points, r = 64, s = 18
-> 66 groups with sizes in [18, 36).

Panels:
  1. a labeled subset of groups, with all other points muted;
  2. the same labeled groups with their simplices (drawing all 66 is unreadable
     because the construction's triangles legitimately extend far beyond
     the data and overlap — only the point groups are disjoint);
  3. a query line: points whose simplex the line crosses (must recurse)
     vs points resolved wholesale (their simplex is entirely on one side).

Usage:  python3 src/visualize_matousek.py [n] [seed] [out.png]
"""

from __future__ import annotations

import random
import sys
from fractions import Fraction as F

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon

from matousek_partition_tree.core import line_crosses_tri, simplicial_partition


def centroid(group):
    return (
        sum(float(p[0]) for p in group) / len(group),
        sum(float(p[1]) for p in group) / len(group),
    )


def choose_visible_groups(part, count=8):
    """Pick groups spread across the x-order so the labels are readable."""
    ordered = sorted(range(len(part)), key=lambda k: centroid(part[k][0])[0])
    if count >= len(ordered):
        return ordered
    return [ordered[round(i * (len(ordered) - 1) / (count - 1))] for i in range(count)]


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    out = sys.argv[3] if len(sys.argv) > 3 else "assets/partition_tree_example.png"

    rng = random.Random(seed)
    D = 10**4
    pts = [(F(rng.randint(0, D), D), F(rng.randint(0, D), D)) for _ in range(n)]
    R = 64
    s = n // R
    part, stats = simplicial_partition(pts, s, random.Random(seed))
    sizes = sorted(len(g) for g, _ in part)
    print(
        f"n={n}, r={R}, s={s}: {len(part)} groups, sizes {sizes[0]}..{sizes[-1]}, K_Q={stats.K_Q}"
    )

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17.8, 5.9), dpi=150)
    for ax in (ax1, ax2, ax3):
        ax.set_xlim(-0.06, 1.06)
        ax.set_ylim(-0.06, 1.06)
        ax.set_aspect("equal")
        ax.tick_params(labelsize=8)

    # panel 1: selected labeled groups, not 66 indistinguishable colors
    show = choose_visible_groups(part, 8)
    sample_cmap = plt.get_cmap("tab10")
    ax1.scatter(
        [float(p[0]) for p in pts], [float(p[1]) for p in pts], s=4, color="0.82", linewidths=0
    )
    for j, k in enumerate(show):
        group, _tri = part[k]
        col = sample_cmap(j)
        cx, cy = centroid(group)
        ax1.scatter(
            [float(p[0]) for p in group],
            [float(p[1]) for p in group],
            s=18,
            color=col,
            edgecolors="white",
            linewidths=0.35,
            label=f"G{k} ({len(group)})",
        )
        ax1.text(
            cx,
            cy,
            f"G{k}",
            fontsize=8,
            weight="bold",
            color="black",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "alpha": 0.82, "lw": 0},
        )
    ax1.set_title(
        f"8 labeled groups out of {len(part)} total\n"
        f"label format: group id, legend shows group size; all groups are disjoint",
        fontsize=11,
    )
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, fontsize=7, frameon=False)

    # panel 2: the same sample groups with their simplices
    ax2.scatter(
        [float(p[0]) for p in pts], [float(p[1]) for p in pts], s=4, color="0.84", linewidths=0
    )
    for j, k in enumerate(show):
        group, tri = part[k]
        col = sample_cmap(j)
        tri_f = [(float(v[0]), float(v[1])) for v in tri]
        ax2.add_patch(
            MplPolygon(tri_f, closed=True, facecolor=col, alpha=0.12, edgecolor=col, linewidth=1.6)
        )
        ax2.scatter(
            [float(p[0]) for p in group],
            [float(p[1]) for p in group],
            s=16,
            linewidths=0,
            color=col,
        )
        cx, cy = centroid(group)
        ax2.text(
            cx,
            cy,
            f"G{k}",
            fontsize=8,
            weight="bold",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "alpha": 0.82, "lw": 0},
        )
    ax2.set_title(
        "same 8 groups with their containing simplices\n"
        "triangles may overlap or extend outside view; point groups do not overlap",
        fontsize=11,
    )

    # panel 3: query line, crossed vs wholesale-resolved simplices
    h = (F(3, 10), F(35, 100))  # y = 0.3 x + 0.35
    crossed = [line_crosses_tri(h, tri) for _, tri in part]
    n_crossed = sum(crossed)
    for (group, _), cr in zip(part, crossed, strict=True):
        col, size = ("#d85a30", 8) if cr else ("0.78", 4)
        ax3.scatter(
            [float(p[0]) for p in group],
            [float(p[1]) for p in group],
            s=size,
            color=col,
            linewidths=0,
        )
    xs = [-0.06, 1.06]
    ax3.plot(xs, [float(h[0]) * x + float(h[1]) for x in xs], "k-", linewidth=1.6)
    ax3.set_title(
        f"query line crosses {n_crossed}/{len(part)} simplices\n"
        "orange points: must recurse — gray: counted wholesale",
        fontsize=11,
    )
    ax3.legend(
        handles=[
            Line2D([], [], color="k", linewidth=1.6, label="query line h"),
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                color="#d85a30",
                markersize=5,
                label="in crossed simplex",
            ),
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                color="0.78",
                markersize=5,
                label="resolved in O(1)",
            ),
        ],
        loc="lower right",
        fontsize=8,
    )

    fig.suptitle(
        "Verified Matousek simplicial partition — one application of the "
        f"Partition Theorem (n={n}, r={R})",
        fontsize=12.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, bbox_inches="tight")
    print(f"crossed: {n_crossed}/{len(part)}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
