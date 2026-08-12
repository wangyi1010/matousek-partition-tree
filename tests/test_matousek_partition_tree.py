"""Property tests for the verified proof-skeleton implementation.

The construction verifies its own preconditions internally (and raises on
failure); these tests assert the theorem's *postconditions* independently:
partition validity, group sizes, simplex containment, cutting conditions,
and exact query equivalence against brute force.

Kept small (n=400, r=25) so CI stays under a few minutes despite exact
rational arithmetic. beta*sqrt(r) = 0.25*5 = 1.25 > 1, so the test-set
cutting is nontrivial and the full mechanism is exercised.
"""

import random
from fractions import Fraction as F

import pytest

from matousek_partition_tree import (
    CuttingError,
    build_tree,
    dual_of_line,
    dual_of_point,
    halfplane_side,
    line_crosses_tri,
    point_in_tri,
    query_count,
    simplicial_partition,
    weighted_cutting,
)

N, SEED, S = 400, 42, 16  # r = 25


def make_points(n=N, seed=SEED):
    rng = random.Random(seed)
    D = 10**4
    return [(F(rng.randint(0, D), D), F(rng.randint(0, D), D)) for _ in range(n)]


@pytest.fixture(scope="module")
def partition():
    pts = make_points()
    part, stats = simplicial_partition(pts, S, random.Random(SEED))
    return pts, part, stats


@pytest.fixture(scope="module")
def tree():
    pts = make_points()
    return pts, build_tree(pts, r=N // S, leaf_size=S, rng=random.Random(SEED))


def test_groups_partition_the_point_set(partition):
    pts, part, _stats = partition
    seen = []
    for group, _ in part:
        seen.extend(group)
    assert len(seen) == len(pts)
    assert sorted(seen) == sorted(pts)  # disjoint + covering


def test_group_sizes_in_s_2s(partition):
    _, part, _stats = partition
    for group, _ in part:
        assert S <= len(group) < 2 * S


def test_groups_contained_in_their_simplices(partition):
    _, part, _stats = partition
    for group, tri in part:
        assert all(point_in_tri(p, tri) for p in group)


def test_query_matches_brute_force(tree):
    pts, root = tree
    rng = random.Random(7)
    D = 10**4
    checked = 0
    while checked < 25:
        h = (F(rng.randint(-D, D), D), F(rng.randint(-D, D), D), F(rng.randint(-D, D), D))
        if h[0] == 0 and h[1] == 0:
            continue
        exact = sum(halfplane_side(h, p) >= 0 for p in pts)
        assert query_count(root, h) == exact
        checked += 1


def test_test_set_crossings_are_tracked(partition):
    """kappa bookkeeping must equal recounting crossings from scratch."""
    _, part, stats = partition
    assert stats.Q, "test set should be nonempty at r=25"
    tris = [tri for _, tri in part]
    for q, kappa in zip(stats.Q, stats.kappa, strict=True):
        # kappa excludes the terminal simplex (weights stop updating there)
        recount = sum(line_crosses_tri(q, t) for t in tris[:-1])
        assert kappa == recount


def test_weighted_cutting_postconditions():
    """Independently re-verify both cutting conditions on returned output."""
    rng = random.Random(3)
    lines = [(F(rng.randint(-100, 100), 100), F(rng.randint(-100, 100), 100)) for _ in range(30)]
    weights = [F(2) ** rng.randint(0, 5) for _ in lines]
    box = [(F(-4), F(-4)), (F(4), F(-4)), (F(4), F(4)), (F(-4), F(4))]
    t = 3.0
    budget = 40
    tris = weighted_cutting(lines, weights, t, box, rng, max_faces=budget)
    assert len(tris) <= budget
    W = sum(weights)
    t_frac = F(t)
    for tr in tris:
        crossing = sum(w for l, w in zip(lines, weights, strict=True) if line_crosses_tri(l, tr))
        assert crossing * t_frac <= W


def test_duality_is_an_exact_involution():
    points = [(F(2, 3), F(-5, 7)), (F(-11, 13), F(17, 19)), (F(0), F(0))]
    lines = [(F(3, 5), F(-7, 11)), (F(-2), F(9, 4)), (F(0), F(0))]
    assert all(dual_of_line(dual_of_point(point)) == point for point in points)
    assert all(dual_of_point(dual_of_line(line)) == line for line in lines)


def test_axis_aligned_and_boundary_queries_match_brute_force():
    points = [
        (F(-2), F(0)),
        (F(-1), F(1)),
        (F(0), F(0)),
        (F(1), F(-1)),
        (F(2), F(0)),
    ]
    tree = build_tree(points, r=4, leaf_size=2, rng=random.Random(11))
    queries = [
        (F(1), F(0), F(0)),
        (F(0), F(1), F(0)),
        (F(-1), F(0), F(1)),
        (F(1), F(1), F(0)),
    ]
    for query in queries:
        expected = sum(halfplane_side(query, point) >= 0 for point in points)
        assert query_count(tree, query) == expected


@pytest.mark.parametrize("seed", [0, 7, 19])
def test_tree_queries_match_brute_force_across_seeds(seed):
    points = make_points(n=120, seed=seed)
    tree = build_tree(points, r=25, leaf_size=16, rng=random.Random(seed))
    rng = random.Random(seed + 100)
    for _ in range(8):
        query = (F(rng.randint(-20, 20)), F(rng.randint(-20, 20)), F(rng.randint(-20, 20)))
        if query[0] == 0 and query[1] == 0:
            query = (F(1), query[1], query[2])
        expected = sum(halfplane_side(query, point) >= 0 for point in points)
        assert query_count(tree, query) == expected


def test_cutting_rejects_an_impossible_face_budget():
    box = [(F(-1), F(-1)), (F(1), F(-1)), (F(1), F(1)), (F(-1), F(1))]
    with pytest.raises(CuttingError):
        weighted_cutting([], [], 1.0, box, random.Random(0), max_faces=1)
