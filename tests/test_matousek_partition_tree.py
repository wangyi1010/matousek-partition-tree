"""Property tests for the verified proof-skeleton implementation.

The construction verifies its own preconditions internally (and raises on
failure); these tests assert the theorem's *postconditions* independently:
partition validity, group sizes, simplex containment, cutting conditions,
and exact query equivalence against brute force.

Kept small (n=400, r=25) so CI stays under a few minutes despite exact
rational arithmetic. beta*sqrt(r) = 0.25*5 = 1.25 > 1, so the test-set
cutting is nontrivial and the full mechanism is exercised.
"""

import math
import random
from fractions import Fraction as F

import pytest

import matousek_partition_tree as mpt
from matousek_partition_tree import (
    build_tree,
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
    D = 10 ** 4
    return [(F(rng.randint(0, D), D), F(rng.randint(0, D), D))
            for _ in range(n)]


@pytest.fixture(scope="module")
def partition():
    pts = make_points()
    part = simplicial_partition(pts, S, random.Random(SEED))
    return pts, part


@pytest.fixture(scope="module")
def tree():
    pts = make_points()
    return pts, build_tree(pts, r=N // S, leaf_size=S,
                           rng=random.Random(SEED))


def test_groups_partition_the_point_set(partition):
    pts, part = partition
    seen = []
    for group, _ in part:
        seen.extend(group)
    assert len(seen) == len(pts)
    assert sorted(seen) == sorted(pts)  # disjoint + covering


def test_group_sizes_in_s_2s(partition):
    _, part = partition
    for group, _ in part:
        assert S <= len(group) < 2 * S


def test_groups_contained_in_their_simplices(partition):
    _, part = partition
    for group, tri in part:
        assert all(point_in_tri(p, tri) for p in group)


def test_query_matches_brute_force(tree):
    pts, root = tree
    rng = random.Random(7)
    D = 10 ** 4
    checked = 0
    while checked < 25:
        h = (F(rng.randint(-D, D), D), F(rng.randint(-D, D), D),
             F(rng.randint(-D, D), D))
        if h[0] == 0 and h[1] == 0:
            continue
        exact = sum(halfplane_side(h, p) >= 0 for p in pts)
        assert query_count(root, h) == exact
        checked += 1


def test_test_set_crossings_are_tracked():
    """kappa bookkeeping must equal recounting crossings from scratch.

    Runs its own partition (not the fixture): LAST_STATS is module-global
    and reflects the most recent simplicial_partition call, so the stats
    must be read immediately after the call they belong to."""
    pts = make_points(300, 9)
    part = mpt.simplicial_partition(pts, 12, random.Random(9))  # r = 25
    stats = mpt.LAST_STATS
    assert stats["Q"], "test set should be nonempty at r=25"
    tris = [tri for _, tri in part]
    for q, kappa in zip(stats["Q"], stats["kappa"]):
        # kappa excludes the terminal simplex (weights stop updating there)
        recount = sum(line_crosses_tri(q, t) for t in tris[:-1])
        assert kappa == recount


def test_weighted_cutting_postconditions():
    """Independently re-verify both cutting conditions on returned output."""
    rng = random.Random(3)
    lines = [(F(rng.randint(-100, 100), 100), F(rng.randint(-100, 100), 100))
             for _ in range(30)]
    weights = [F(2) ** rng.randint(0, 5) for _ in lines]
    box = [(F(-4), F(-4)), (F(4), F(-4)), (F(4), F(4)), (F(-4), F(4))]
    t = 3.0
    budget = 40
    tris = weighted_cutting(lines, weights, t, box, rng, max_faces=budget)
    assert len(tris) <= budget
    W = sum(weights)
    t_frac = F(t)
    for tr in tris:
        crossing = sum(w for l, w in zip(lines, weights)
                       if line_crosses_tri(l, tr))
        assert crossing * t_frac <= W
