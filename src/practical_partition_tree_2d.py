from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, field
from typing import Iterable, Literal


Point = tuple[float, float]
Halfplane = tuple[float, float, float]
CellStatus = Literal["inside", "outside", "crossing"]


@dataclass
class Box:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def corners(self) -> list[Point]:
        return [
            (self.min_x, self.min_y),
            (self.min_x, self.max_y),
            (self.max_x, self.min_y),
            (self.max_x, self.max_y),
        ]

    def to_dict(self) -> dict[str, float]:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }


@dataclass
class Node:
    cell: Box
    count: int
    points: list[Point] | None = None
    children: list["Node"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return self.points is not None


def bounding_box(points: list[Point]) -> Box:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


def point_in_halfplane(point: Point, halfplane: Halfplane) -> bool:
    a, b, c = halfplane
    x, y = point
    return a * x + b * y + c >= 0


def classify_box(box: Box, halfplane: Halfplane) -> CellStatus:
    values = []
    a, b, c = halfplane
    for x, y in box.corners:
        values.append(a * x + b * y + c)

    if all(v >= 0 for v in values):
        return "inside"
    if all(v < 0 for v in values):
        return "outside"
    return "crossing"


def split_once(points: list[Point]) -> tuple[list[Point], list[Point]]:
    box = bounding_box(points)
    spread_x = box.max_x - box.min_x
    spread_y = box.max_y - box.min_y
    axis = 0 if spread_x >= spread_y else 1
    ordered = sorted(points, key=lambda p: (p[axis], p[1 - axis]))
    mid = len(ordered) // 2
    return ordered[:mid], ordered[mid:]


def partition_points(points: list[Point], r: int) -> list[list[Point]]:
    if r <= 0:
        raise ValueError("r must be positive")
    if not points:
        return []

    groups = [points]
    while len(groups) < r:
        idx = max(range(len(groups)), key=lambda i: len(groups[i]))
        group = groups.pop(idx)
        if len(group) <= 1:
            groups.append(group)
            break

        left, right = split_once(group)
        if left:
            groups.append(left)
        if right:
            groups.append(right)

    return groups


def build_tree(points: list[Point], *, r: int = 8, leaf_size: int = 16) -> Node:
    if not points:
        raise ValueError("cannot build a partition tree from an empty point set")
    if r < 2:
        raise ValueError("r must be at least 2")
    if leaf_size < 1:
        raise ValueError("leaf_size must be positive")

    cell = bounding_box(points)
    if len(points) <= leaf_size:
        return Node(cell=cell, count=len(points), points=list(points))

    node = Node(cell=cell, count=len(points))
    groups = partition_points(points, min(r, len(points)))
    node.children = [build_tree(group, r=r, leaf_size=leaf_size) for group in groups]
    return node


def query_halfplane_count(node: Node, halfplane: Halfplane) -> int:
    status = classify_box(node.cell, halfplane)

    if status == "inside":
        return node.count
    if status == "outside":
        return 0
    if node.is_leaf:
        assert node.points is not None
        return sum(1 for p in node.points if point_in_halfplane(p, halfplane))

    return sum(query_halfplane_count(child, halfplane) for child in node.children)


def collect_groups(node: Node) -> list[dict]:
    if node.is_leaf:
        assert node.points is not None
        return [
            {
                "count": node.count,
                "cell": node.cell.to_dict(),
                "points": [{"x": x, "y": y} for x, y in node.points],
            }
        ]

    groups: list[dict] = []
    for child in node.children:
        groups.extend(collect_groups(child))
    return groups


def load_points_csv(path: str) -> list[Point]:
    points: list[Point] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if "x" not in reader.fieldnames or "y" not in reader.fieldnames:
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
