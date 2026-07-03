"""Property tests for the practical kd-style baseline: exact queries and
structural invariants, at a size the float implementation handles instantly.
"""

import random

import pytest

from matousek_partition_tree.practical import (
    build_tree,
    collect_groups,
    point_in_halfplane,
    query_halfplane_count,
)


@pytest.fixture(scope="module")
def data():
    rng = random.Random(11)
    pts = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(3000)]
    return pts, build_tree(pts, r=8, leaf_size=16)


def test_query_matches_brute_force(data):
    pts, tree = data
    rng = random.Random(5)
    for _ in range(100):
        h = (rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-60, 60))
        if h[0] == 0 and h[1] == 0:
            continue
        exact = sum(point_in_halfplane(p, h) for p in pts)
        assert query_halfplane_count(tree, h) == exact


def test_leaves_partition_the_point_set(data):
    pts, tree = data
    leaf_points = []
    for g in collect_groups(tree):
        leaf_points.extend((p["x"], p["y"]) for p in g["points"])
    assert len(leaf_points) == len(pts)
    assert sorted(leaf_points) == sorted(pts)


def test_leaf_size_respected(data):
    _, tree = data
    for g in collect_groups(tree):
        assert 1 <= g["count"] <= 16


def test_duplicate_points_do_not_hang():
    pts = [(1.0, 1.0)] * 50
    tree = build_tree(pts, r=4, leaf_size=8)
    assert query_halfplane_count(tree, (1.0, 0.0, 0.0)) == 50
