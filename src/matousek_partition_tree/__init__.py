"""Verified proof-skeleton implementation of the 2D Matoušek Partition
Theorem for halfplane range counting."""

from matousek_partition_tree.core import (
    CuttingError,
    Halfplane,
    Line,
    PartitionStats,
    PNode,
    Point,
    TestSetError,
    build_test_set,
    build_tree,
    crossing_number,
    halfplane_side,
    line_crosses_tri,
    point_in_tri,
    query_count,
    simplicial_partition,
    weighted_cutting,
)

__version__ = "0.4.0"

__all__ = [
    "CuttingError",
    "Halfplane",
    "Line",
    "PNode",
    "PartitionStats",
    "Point",
    "TestSetError",
    "__version__",
    "build_test_set",
    "build_tree",
    "crossing_number",
    "halfplane_side",
    "line_crosses_tri",
    "point_in_tri",
    "query_count",
    "simplicial_partition",
    "weighted_cutting",
]
