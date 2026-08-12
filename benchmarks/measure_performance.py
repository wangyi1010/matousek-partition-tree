"""Measure construction cost and exact halfplane-query performance.

This benchmark complements ``measure_crossings.py``.  It validates every
generated query against brute force, then reports wall-clock construction
time and median per-query latency for the partition tree and brute force.

Examples:

    python benchmarks/measure_performance.py
    python benchmarks/measure_performance.py --sizes 200 400 --queries 50
    python benchmarks/measure_performance.py --smoke --json /tmp/perf.json

Results are machine-dependent.  They are evidence about this Python proof
skeleton, not an empirical proof of the theorem's asymptotic bounds.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import matousek_partition_tree as mpt


def make_points(n: int, seed: int) -> list[mpt.Point]:
    rng = random.Random(seed)
    denominator = 10**4
    return [
        (
            F(rng.randint(0, denominator), denominator),
            F(rng.randint(0, denominator), denominator),
        )
        for _ in range(n)
    ]


def make_queries(count: int, seed: int) -> list[mpt.Halfplane]:
    rng = random.Random(seed)
    denominator = 10**4
    queries: list[mpt.Halfplane] = []
    while len(queries) < count:
        query = (
            F(rng.randint(-denominator, denominator), denominator),
            F(rng.randint(-denominator, denominator), denominator),
            F(rng.randint(-denominator, denominator), denominator),
        )
        if query[0] != 0 or query[1] != 0:
            queries.append(query)
    return queries


def brute_count(points: list[mpt.Point], query: mpt.Halfplane) -> int:
    return sum(mpt.halfplane_side(query, point) >= 0 for point in points)


def node_count(root: mpt.PNode) -> int:
    return 1 + sum(node_count(child) for child in root.children)


def median_batch_seconds(call, repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def measure(
    n: int,
    *,
    seed: int,
    r: int,
    leaf_size: int,
    query_count: int,
    repeats: int,
) -> dict[str, Any]:
    points = make_points(n, seed)
    queries = make_queries(query_count, seed + 1)

    start = time.perf_counter()
    tree = mpt.build_tree(points, r=r, leaf_size=leaf_size, rng=random.Random(seed))
    build_seconds = time.perf_counter() - start

    expected = [brute_count(points, query) for query in queries]
    actual = [mpt.query_count(tree, query) for query in queries]
    if actual != expected:
        mismatch = next(
            i for i, pair in enumerate(zip(actual, expected, strict=True)) if pair[0] != pair[1]
        )
        raise AssertionError(
            f"query {mismatch} disagrees: tree={actual[mismatch]}, brute={expected[mismatch]}"
        )

    tree_seconds = median_batch_seconds(
        lambda: [mpt.query_count(tree, query) for query in queries], repeats
    )
    brute_seconds = median_batch_seconds(
        lambda: [brute_count(points, query) for query in queries], repeats
    )
    tree_us = tree_seconds * 1_000_000 / query_count
    brute_us = brute_seconds * 1_000_000 / query_count

    return {
        "n": n,
        "r": r,
        "leaf_size": leaf_size,
        "queries": query_count,
        "tree_nodes": node_count(tree),
        "build_seconds": build_seconds,
        "tree_query_us": tree_us,
        "brute_query_us": brute_us,
        "query_speedup": brute_us / tree_us,
        "exact_matches": query_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[200, 400, 800])
    parser.add_argument("--queries", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--r", type=int, default=25)
    parser.add_argument("--leaf-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--json", type=Path, help="optional path for machine-readable results")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="small deterministic run intended for CI",
    )
    args = parser.parse_args()
    if args.smoke:
        args.sizes = [120]
        args.queries = 8
        args.repeats = 1
        args.leaf_size = 16
    if any(size <= args.leaf_size for size in args.sizes):
        parser.error("every size must be larger than --leaf-size")
    if args.queries < 1 or args.repeats < 1 or args.r < 2:
        parser.error("--queries and --repeats must be positive; --r must be at least 2")
    return args


def main() -> None:
    args = parse_args()
    rows = [
        measure(
            n,
            seed=args.seed,
            r=args.r,
            leaf_size=args.leaf_size,
            query_count=args.queries,
            repeats=args.repeats,
        )
        for n in args.sizes
    ]

    print("| n | nodes | build (s) | tree query (us) | brute query (us) | speedup | exact |")
    print("|---:|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['n']} | {row['tree_nodes']} | {row['build_seconds']:.3f} | "
            f"{row['tree_query_us']:.1f} | {row['brute_query_us']:.1f} | "
            f"{row['query_speedup']:.2f}x | {row['exact_matches']}/{row['queries']} |"
        )

    if args.json:
        payload = {
            "seed": args.seed,
            "repeats": args.repeats,
            "results": rows,
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nJSON written: {args.json}")


if __name__ == "__main__":
    main()
