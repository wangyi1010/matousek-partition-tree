"""CLI for the practical kd-style tree (console script: practical-tree)."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable

from matousek_partition_tree.practical import (
    Point,
    build_tree,
    collect_groups,
    query_halfplane_count,
)


def load_points_csv(path: str) -> list[Point]:
    points: list[Point] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "x" not in reader.fieldnames or "y" not in reader.fieldnames:
            raise ValueError("CSV must have columns named x and y")
        for row in reader:
            points.append((float(row["x"]), float(row["y"])))
    return points


def save_groups_json(path: str, groups: Iterable[dict]) -> None:
    with open(path, "w") as f:
        json.dump(list(groups), f, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a practical 2D partition tree.")
    parser.add_argument("csv", help="Input CSV with columns x,y")
    parser.add_argument("--r", type=int, default=8, help="branching/group parameter")
    parser.add_argument("--leaf-size", type=int, default=16, help="maximum points per leaf")
    parser.add_argument("--groups-out", help="write final leaf groups to JSON")
    parser.add_argument(
        "--halfplane",
        nargs=3,
        type=float,
        metavar=("A", "B", "C"),
        help="count points satisfying A*x + B*y + C >= 0",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    points = load_points_csv(args.csv)
    tree = build_tree(points, r=args.r, leaf_size=args.leaf_size)

    print(f"points: {len(points)}")
    print(f"leaf groups: {len(collect_groups(tree))}")

    if args.groups_out:
        save_groups_json(args.groups_out, collect_groups(tree))
        print(f"groups written: {args.groups_out}")

    if args.halfplane:
        count = query_halfplane_count(tree, tuple(args.halfplane))
        print(f"halfplane count: {count}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
