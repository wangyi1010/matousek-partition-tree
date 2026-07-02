"""2D Matousek partition tree (COMP5045) — VERIFIED PROOF-SKELETON
implementation (not a certified implementation of the theorem): every
enforceable precondition is checked at runtime and violations raise;
the two remaining modeling gaps are documented below.

Construction, mapped to the proof:

  Step 1  point-line duality + (1/(beta*sqrt r))-cutting of P* -> test set
          Q, with a FIXED beta chosen so the cutting should have <= r
          vertices; if the verified cutting exceeds r vertices, raise
          instead of shrinking beta (no truncation either, so the Test
          Set Lemma's sandwich always exists when construction succeeds).
  Step 3  round-by-round: exponential weights w_i(q) = 2^kappa_i(q),
          weighted (1/t_i)-cutting of Q whose face count is VERIFIED to be
          <= n_i / s, so the pigeonhole face with >= s points provably
          exists (asserted, not searched for).
  Step 4  weights of crossed test lines are doubled after each round.
  Tree    recurse the theorem inside every group.

Cutting construction is the random-sampling proof of the cutting theorem
turned into a Las Vegas procedure: sample lines with probability
proportional to weight, build the exact arrangement of the sample, fan-
triangulate, then VERIFY both cutting conditions

    (a) every triangle is crossed by total weight <= W / t,
    (b) number of triangles <= the caller's face budget,

adapting the sample size and resampling until both hold (raises after a
bounded number of failures instead of ever returning an unverified
cutting).

All geometry is exact rational arithmetic (fractions.Fraction): no
floating-point robustness issues. Boundary-only line/simplex contacts
are treated by a general-position convention and are NOT counted as
crossings; the same convention is used consistently in construction and
verification.

Remaining gap vs the literal theorem (documented, not hidden): cuttings
are built inside a combinatorially complete bounding box — a box that
contains all pairwise intersections of the lines being cut, so the
arrangement inside the box has the full combinatorial structure. The
paper works over the whole (projective) plane; unbounded cells are here
represented by their clipped versions. Query correctness is unaffected.

Usage:  python3 matousek_partition_tree.py [n_points] [seed]
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from fractions import Fraction as F

# ---------------------------------------------------------------- primitives
# A nonvertical line is (m, c) meaning y = m*x + c, with Fraction coords.
# A point is (x, y) with Fraction coords.

Line = tuple
Point = tuple


def dual_of_point(p: Point) -> Line:
    """p = (a, b)  ->  p* : y = a*x - b."""
    return (p[0], -p[1])


def dual_of_line(l: Line) -> Point:
    """l : y = m*x + c = m*x - (-c)  ->  l* = (m, -c). Involution with above."""
    return (l[0], -l[1])


def side(l: Line, p: Point) -> F:
    """> 0 if p is above l, < 0 below, 0 on."""
    m, c = l
    x, y = p
    return y - (m * x + c)


def seg_line_point(a: Point, b: Point, l: Line) -> Point:
    """Intersection of segment ab's supporting line with l (caller guarantees
    a and b are on strictly opposite sides of l)."""
    sa, sb = side(l, a), side(l, b)
    t = sa / (sa - sb)
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


# ------------------------------------------------------ convex-polygon tools
def clip(poly: list[Point], l: Line, keep_above: bool) -> list[Point]:
    """Sutherland-Hodgman clip of a convex polygon against one side of l."""
    if not poly:
        return []
    out: list[Point] = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        sa, sb = side(l, a), side(l, b)
        ina = sa >= 0 if keep_above else sa <= 0
        inb = sb >= 0 if keep_above else sb <= 0
        if ina:
            out.append(a)
        if ina != inb and sa != sb:
            out.append(seg_line_point(a, b, l))
    dedup = [q for i, q in enumerate(out) if q != out[(i - 1) % len(out)]]
    return dedup if len(dedup) >= 3 else []


def poly_area2(poly: list[Point]) -> F:
    s = F(0)
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return abs(s)


def arrangement_cells(lines: list[Line], box: list[Point]) -> list[list[Point]]:
    """Cells of the arrangement of `lines`, restricted to convex region `box`."""
    cells = [box]
    for l in lines:
        nxt: list[list[Point]] = []
        for cell in cells:
            up, dn = clip(cell, l, True), clip(cell, l, False)
            for c in (up, dn):
                if c and poly_area2(c) > 0:
                    nxt.append(c)
        cells = nxt
    return cells


def fan_triangles(poly: list[Point]) -> list[list[Point]]:
    tris = []
    for i in range(1, len(poly) - 1):
        t = [poly[0], poly[i], poly[i + 1]]
        if poly_area2(t) > 0:
            tris.append(t)
    return tris


def line_crosses_tri(l: Line, tri: list[Point]) -> bool:
    """h crosses simplex: h meets the simplex's interior, i.e. strictly mixed
    vertex signs (the paper's general-position crossing; boundary-only
    contact is not a crossing — cutting lines pass through their own cells'
    vertices, and counting that would make condition (a) unsatisfiable)."""
    ss = [side(l, v) for v in tri]
    return min(ss) < 0 < max(ss)


def point_in_tri(p: Point, tri: list[Point]) -> bool:
    a, b, c = tri
    d1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    d2 = (c[0] - b[0]) * (p[1] - b[1]) - (c[1] - b[1]) * (p[0] - b[0])
    d3 = (a[0] - c[0]) * (p[1] - c[1]) - (a[1] - c[1]) * (p[0] - c[0])
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def combinatorial_box(lines: list[Line], pts: list[Point] = ()) -> list[Point]:
    """Axis-aligned box containing all pairwise intersections of `lines` and
    all of `pts`, inflated 2x. Inside it, the arrangement of any subset of
    `lines` has its complete combinatorial structure (all vertices), so
    clipped cells only lose unbounded ends, never vertices.

    The extent scan uses floats (exact values are only needed for the
    geometry inside, and the box is inflated well past float error)."""
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    fl = [(float(m), float(c)) for m, c in lines]
    for i in range(len(fl)):
        m1, c1 = fl[i]
        for j in range(i + 1, len(fl)):
            m2, c2 = fl[j]
            if m1 != m2:
                x = (c2 - c1) / (m1 - m2)
                xs.append(x)
                ys.append(m1 * x + c1)
    if not xs:
        xs, ys = [0.0], [0.0]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys), 1.0) * 2
    lo_x = F(cx - half).limit_denominator(10 ** 6)
    hi_x = F(cx + half).limit_denominator(10 ** 6)
    lo_y = F(cy - half).limit_denominator(10 ** 6)
    hi_y = F(cy + half).limit_denominator(10 ** 6)
    return [(lo_x, lo_y), (hi_x, lo_y), (hi_x, hi_y), (lo_x, hi_y)]


# ----------------------------------------------------------------- cuttings
class CuttingError(RuntimeError):
    pass


def poly_crossed(l: Line, poly: list[Point]) -> bool:
    """Line meets the polygon's interior (strictly mixed vertex signs)."""
    ss = [side(l, v) for v in poly]
    return min(ss) < 0 < max(ss)


def weighted_cutting(lines: list[Line], weights: list[F], t: float,
                     box: list[Point], rng: random.Random,
                     max_faces: int | None = None,
                     max_tries: int = 60) -> list[list[Point]]:
    """VERIFIED weighted (1/t)-cutting for (lines, weights) inside `box`,
    via the Chazelle-Friedman two-level construction the cutting theorem's
    O(t^2)-face bound actually comes from:

      level 1: sample ~t lines with probability proportional to weight and
               build their arrangement (coarse: O(t^2) cells, some heavy);
      level 2: any cell still crossed by weight > W/t is refined in place,
               repeatedly split by a weighted-random line crossing it,
               until every piece is light.

    (A naive single sample needs ~t*log t lines for lightness, which has
    O(t^2 log^2 t) cells and busts the O(t^2) face budget.)

    Then verify exactly: (a) every cell's crossing weight <= W/t — fan
    triangles inherit lightness from their cell — and (b) triangle count
    within `max_faces` (the caller's pigeonhole budget). Resamples on
    failure; raises CuttingError rather than return an unverified cutting."""
    W = sum(weights)
    t_frac = F(t).limit_denominator(10 ** 9)
    if not lines or t <= 1:
        tris = fan_triangles(box)
        if max_faces is not None and len(tris) > max_faces:
            raise CuttingError("trivial cutting exceeds face budget")
        return tris
    fweights = [float(w) for w in weights]

    def cell_weight_heavy(cell: list[Point]) -> tuple[bool, list[int]]:
        idx = [i for i, l in enumerate(lines) if poly_crossed(l, cell)]
        heavy = sum(weights[i] for i in idx) * t_frac > W
        return heavy, idx

    k0 = max(1, min(len(lines), math.ceil(t)))
    for _ in range(max_tries):
        # level 1: coarse sample of ~t distinct lines (k0 adapts downward if
        # the face budget binds; k0 = 0 degenerates to pure level-2
        # refinement starting from the whole box)
        if k0 > 0:
            picks = rng.choices(lines, weights=fweights, k=4 * k0)
            sample = list(dict.fromkeys(picks))[:k0]
        else:
            sample = []
        cells = arrangement_cells(sample, box)

        # level 2: refine heavy cells by weighted-random splitting
        final: list[list[Point]] = []
        stack = cells
        failed = False
        guard = 0
        while stack:
            guard += 1
            if guard > 4000:
                failed = True
                break
            cell = stack.pop()
            heavy, idx = cell_weight_heavy(cell)
            if not heavy:
                final.append(cell)
                continue
            splitter = rng.choices(idx,
                                   weights=[fweights[i] for i in idx], k=1)[0]
            up = clip(cell, lines[splitter], True)
            dn = clip(cell, lines[splitter], False)
            pieces = [c for c in (up, dn) if c and poly_area2(c) > 0]
            if len(pieces) < 2:  # numerically degenerate split; give up cell
                failed = True
                break
            stack.extend(pieces)
        if failed:
            continue

        tris = [tr for cell in final for tr in fan_triangles(cell)]
        if max_faces is not None and len(tris) > max_faces:
            k0 = max(0, k0 - max(1, k0 // 3))  # coarser level 1 next try
            continue
        return tris
    raise CuttingError(f"no verified (1/{t:.2f})-cutting in {max_tries} tries")


# ------------------------------------------------------- Step 1: test set Q
class TestSetError(RuntimeError):
    pass


def build_test_set(points: list[Point], r: float,
                   rng: random.Random) -> list[Line]:
    """Q = duals of ALL vertices of a fixed-scale (1/t)-cutting of P*, with
    t = beta * sqrt(r). If the cutting has more than r vertices, raise
    TestSetError instead of shrinking beta or truncating vertices.

    Faithfulness constraint: the Test Set Lemma's bad-simplex bound
    O(n/(s*sqrt r)) requires the dual cutting to stay at Theta(sqrt r)
    scale, so beta is a FIXED constant (chosen once as ~1/sqrt(A') from
    this implementation's empirical cutting-vertex constant A' ~ 16), not
    an adaptive knob. If the cutting still has more than r vertices at
    that fixed scale, the constants are too large for this r and we raise
    rather than shrink t further (which would keep |Q| <= r but inflate
    the conflict bound toward O(n)). For beta*sqrt(r) <= 1 (r < 16) the
    cutting is trivially the bounding box — the small-r regime where the
    theorem's bound is vacuous regardless."""
    duals = [dual_of_point(p) for p in points]
    box = combinatorial_box(duals)
    budget = max(4, math.ceil(r))
    beta = 0.25
    t = beta * math.sqrt(r)
    tris = weighted_cutting(duals, [F(1)] * len(duals), t, box, rng)
    verts = list(dict.fromkeys(v for tr in tris for v in tr))
    if len(verts) > budget:
        raise TestSetError(
            f"(1/{t:.2f})-cutting of P* has {len(verts)} > r={budget} "
            f"vertices: cutting constants too large for this r")
    return [dual_of_point(v) for v in verts]  # Q = V*, ALL vertices


# --------------------------------------- Step 3+4: rounds with exp. weights
def simplicial_partition(points: list[Point], s: int, rng: random.Random,
                         ) -> list[tuple[list[Point], list[Point]]]:
    """One application of the Partition Theorem: groups of size in [s, 2s)."""
    n = len(points)
    Q = build_test_set(points, n / s, rng)
    kappa = [0] * len(Q)
    remaining = list(points)
    box = combinatorial_box(Q, points)
    out: list[tuple[list[Point], list[Point]]] = []

    while len(remaining) >= 2 * s:
        n_i = len(remaining)
        face_budget = n_i // s  # pigeonhole: #faces <= n_i/s
        # alpha trades the two cutting conditions off: smaller alpha loosens
        # the per-cell weight bound (fewer refinement splits) while the face
        # budget n_i/s is fixed by pigeonhole. Our constructive cutting
        # constant A (sampling + fan triangulation) is larger than the
        # optimal one the paper assumes, so alpha must be smaller than the
        # paper's 1/2 for both conditions to be satisfiable together.
        t_i = 0.35 * math.sqrt(n_i / s)
        w = [F(2) ** kp for kp in kappa]
        tris = weighted_cutting(Q, w, t_i, box, rng, max_faces=face_budget)

        counts = [sum(point_in_tri(p, tr) for p in remaining) for tr in tris]
        best = max(range(len(tris)), key=counts.__getitem__)
        # closed triangles cover the box, so sum(counts) >= n_i and
        # max >= n_i / #faces >= s: existence is guaranteed, not searched.
        assert counts[best] >= s, "pigeonhole violated (should be impossible)"

        tri = tris[best]
        inside = [p for p in remaining if point_in_tri(p, tri)]
        group, rest_in = inside[:s], inside[s:]
        remaining = [p for p in remaining
                     if not point_in_tri(p, tri)] + rest_in
        out.append((group, tri))
        for j, q in enumerate(Q):  # Step 4: double crossed test lines
            if line_crosses_tri(q, tri):
                kappa[j] += 1

    if remaining:  # terminal round: any simplex containing the rest is legal
        out.append((remaining, bounding_triangle(remaining)))
    global LAST_STATS  # diagnostics: K_Q = max kappa over the test set
    LAST_STATS = {"Q": Q, "kappa": kappa,
                  "K_Q": max(kappa) if kappa else 0}
    return out


LAST_STATS: dict = {}


def bounding_triangle(points: list[Point]) -> list[Point]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    lo_x, hi_x, lo_y, hi_y = min(xs), max(xs), min(ys), max(ys)
    w = (hi_x - lo_x) + 1
    h = (hi_y - lo_y) + 1
    return [(lo_x - w, lo_y - 1), (hi_x + w, lo_y - 1),
            ((lo_x + hi_x) / 2, hi_y + 2 * h)]


# -------------------------------------------------------------------- tree
@dataclass
class PNode:
    count: int
    tri: list[Point] | None = None  # simplex of this node within its parent
    children: list["PNode"] = field(default_factory=list)
    points: list[Point] | None = None  # leaves only


def build_tree(points: list[Point], r: int = 8, leaf_size: int = 32,
               rng: random.Random | None = None,
               tri: list[Point] | None = None) -> PNode:
    rng = rng or random.Random(0)
    if len(points) <= leaf_size:
        return PNode(count=len(points), tri=tri, points=points)
    s = max(1, len(points) // r)
    node = PNode(count=len(points), tri=tri)
    for group, gtri in simplicial_partition(points, s, rng):
        node.children.append(build_tree(group, r, leaf_size, rng, gtri))
    return node


# ------------------------------------------------------------------- query
def halfplane_side(h: tuple, p: Point) -> F:
    a, b, c = h
    return a * p[0] + b * p[1] + c


def query_count(node: PNode, h: tuple) -> int:
    """Count points with a*x + b*y + c >= 0."""
    if node.tri is not None:
        vals = [halfplane_side(h, v) for v in node.tri]
        if all(v >= 0 for v in vals):
            return node.count
        if all(v < 0 for v in vals):
            return 0
    if node.points is not None:
        return sum(halfplane_side(h, p) >= 0 for p in node.points)
    return sum(query_count(ch, h) for ch in node.children)


def crossing_number(node: PNode, line: Line) -> int:
    """Simplices of node's own partition crossed by `line` (one level)."""
    return sum(line_crosses_tri(line, ch.tri) for ch in node.children)


# -------------------------------------------------------------------- demo
def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    rng = random.Random(seed)
    D = 10 ** 4
    pts = [(F(rng.randint(0, D), D), F(rng.randint(0, D), D))
           for _ in range(n)]

    # r must satisfy beta*sqrt(r) > 1 (i.e. r > 16 at beta = 0.25) for the
    # test-set cutting to be nontrivial and actually exercise the mechanism.
    R = 64
    tree = build_tree(pts, r=R, leaf_size=32, rng=random.Random(seed))
    print(f"built: n={n}, r={R}, root children={len(tree.children)}")
    sizes = sorted(ch.count for ch in tree.children)
    print(f"root group sizes: {sizes}  (target [s,2s) = [{n // R},{2 * (n // R)}))")

    bad = 0
    for _ in range(60):
        a = F(rng.randint(-D, D), D)
        b = F(rng.randint(-D, D), D)
        c = F(rng.randint(-D, D), D)
        if a == 0 and b == 0:
            continue
        h = (a, b, c)
        exact = sum(halfplane_side(h, p) >= 0 for p in pts)
        got = query_count(tree, h)
        bad += got != exact
    print(f"query check vs brute force: {60 - bad}/60 exact matches")

    crossings = []
    for _ in range(300):
        m = F(rng.randint(-2 * D, 2 * D), D)
        c0 = F(rng.randint(-2 * D, 2 * D), D)
        crossings.append(crossing_number(tree, (m, c0)))
    mx, avg = max(crossings), sum(crossings) / len(crossings)
    print(f"root-level crossings over 300 random lines: max={mx}, "
          f"avg={avg:.2f}, bound O(sqrt r)=O({math.sqrt(R):.2f}) "
          f"(out of {len(tree.children)} simplices)")


if __name__ == "__main__":
    main()
