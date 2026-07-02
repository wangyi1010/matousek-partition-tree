from __future__ import annotations

import argparse
import csv
import json
from itertools import cycle

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def load_points_csv(path: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            points.append((float(row["x"]), float(row["y"])))
    return points


def load_groups_json(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def add_halfplane_line(ax, halfplane: tuple[float, float, float], xs: list[float], ys: list[float]) -> None:
    a, b, c = halfplane
    pad_x = max(1.0, (max(xs) - min(xs)) * 0.15)
    pad_y = max(1.0, (max(ys) - min(ys)) * 0.15)
    x0, x1 = min(xs) - pad_x, max(xs) + pad_x
    y0, y1 = min(ys) - pad_y, max(ys) + pad_y

    if abs(b) > 1e-12:
        line_xs = [x0, x1]
        line_ys = [-(a * x + c) / b for x in line_xs]
        ax.plot(line_xs, line_ys, color="black", linewidth=2, linestyle="--", label="halfplane boundary")
    elif abs(a) > 1e-12:
        x = -c / a
        ax.axvline(x, color="black", linewidth=2, linestyle="--", label="halfplane boundary")

    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)


def visualize(
    points_path: str,
    groups_path: str,
    output_path: str,
    halfplane: tuple[float, float, float] | None = None,
) -> None:
    points = load_points_csv(points_path)
    groups = load_groups_json(groups_path)

    colors = cycle(
        [
            "#2E86AB",
            "#F18F01",
            "#C73E1D",
            "#6A994E",
            "#7B2CBF",
            "#008B8B",
            "#D45087",
            "#4D908E",
        ]
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    for idx, group in enumerate(groups):
        color = next(colors)
        cell = group["cell"]
        width = cell["max_x"] - cell["min_x"]
        height = cell["max_y"] - cell["min_y"]

        if width == 0:
            width = 0.18
            x = cell["min_x"] - width / 2
        else:
            x = cell["min_x"]

        if height == 0:
            height = 0.18
            y = cell["min_y"] - height / 2
        else:
            y = cell["min_y"]

        rect = Rectangle(
            (x, y),
            width,
            height,
            linewidth=1.8,
            edgecolor=color,
            facecolor=color,
            alpha=0.13,
        )
        ax.add_patch(rect)

        gx = [p["x"] for p in group["points"]]
        gy = [p["y"] for p in group["points"]]
        ax.scatter(gx, gy, color=color, s=55, zorder=3)

        cx = x + width / 2
        cy = y + height / 2
        ax.text(cx, cy, f"G{idx}", color=color, fontsize=9, ha="center", va="center")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    if halfplane is not None:
        add_halfplane_line(ax, halfplane, xs, ys)
    else:
        pad_x = max(1.0, (max(xs) - min(xs)) * 0.15)
        pad_y = max(1.0, (max(ys) - min(ys)) * 0.15)
        ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("2D Partition Tree Leaf Groups")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize 2D partition tree groups.")
    parser.add_argument("points_csv")
    parser.add_argument("groups_json")
    parser.add_argument("--out", default="partition_tree_visualization.png")
    parser.add_argument(
        "--halfplane",
        nargs=3,
        type=float,
        metavar=("A", "B", "C"),
        help="draw boundary of A*x + B*y + C >= 0",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    visualize(
        args.points_csv,
        args.groups_json,
        args.out,
        tuple(args.halfplane) if args.halfplane else None,
    )
    print(f"visualization written: {args.out}")


if __name__ == "__main__":
    main()
