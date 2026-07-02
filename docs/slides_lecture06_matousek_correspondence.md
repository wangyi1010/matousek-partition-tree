# Lecture 06 Slides 85-95: Matousek Paper Calculation Extraction

Source paper: Jiri Matousek, "Efficient Partition Trees", Discrete & Computational Geometry 8:315-334, 1992.

Scope: only the paper content corresponding to the lecture slides on partition trees and simplicial partitions.

## 1. Background Warmup: Four-Way Partition

This part is not the main Matousek theorem. It is the older/simple partition-tree idea used in the slides before introducing simplicial partitions.

The plane is recursively divided into four regions, each containing:

$$
\frac n4
$$

points.

For a halfplane query, the query boundary is a line. In the worst case, this line intersects three of the four regions, so the query recurses into three children.

Thus the query recurrence is:

$$
T(n)=3T(n/4)+O(1)
$$

Solving:

$$
T(n)=O(n^{\log_4 3})
$$

Since:

$$
\log_4 3\approx 0.792
$$

we get:

$$
T(n)=O(n^{0.792})
$$

This is the bound shown on slide 89.

## 2. Paper Definition: Simplicial Partition

The paper defines a simplicial partition of P as:

$$
\Pi=\{(P_1,\Delta_1),\ldots,(P_m,\Delta_m)\}
$$

where:

- the sets \(P_i\) are pairwise disjoint,
- together they form a partition of P,
- each \(\Delta_i\) is a relatively open simplex containing \(P_i\).

In dimension 2, a simplex is a triangle, so the slide writes:

$$
F(P)=\{(P_1,t_1),\ldots,(P_r,t_r)\}
$$

where each \(t_i\) is a triangle containing \(P_i\).

The paper allows lower-dimensional simplices for degenerate point sets, but the slides only use the planar triangle picture.

## 3. Paper Definition: Crossing Number

The paper says a hyperplane h crosses a simplex \(\Delta\) if:

$$
h\cap\Delta\ne\emptyset
$$

and:

$$
\Delta\not\subset h
$$

In the plane, hyperplanes are lines.

So the crossing number of a line h relative to \(\Pi\) is:

$$
\#\{\Delta_i:h\text{ crosses }\Delta_i\}
$$

The crossing number of the whole partition is:

$$
\max_h \#\{\Delta_i:h\text{ crosses }\Delta_i\}
$$

This is exactly slide 91:

$$
\text{crossing number}=\text{maximal number of triangles intersected by a line}
$$

## 4. Paper Class-Size Condition and Slide "Fine" Condition

The paper uses parameter s and requires:

$$
s\le |P_i|<2s
$$

It also sets:

$$
r=\frac ns
$$

Therefore:

$$
2s=\frac{2n}{r}
$$

So the paper condition implies:

$$
|P_i|<\frac{2n}{r}
$$

The slide calls a simplicial r-partition fine if:

$$
|P_i|\le \frac{2n}{r}
$$

So the slide's fine condition is the upper-bound part of the paper's stronger condition.

## 5. Paper Theorem 3.1: Partition Theorem

The paper states in fixed dimension d:

Given P, n, and s with:

$$
2\le s<n
$$

set:

$$
r=\frac ns
$$

Then there exists a simplicial partition \(\Pi\) such that:

$$
s\le |P_i|<2s
$$

and the crossing number is:

$$
O(r^{1-1/d})
$$

For the lecture slides, d equals 2. Therefore:

$$
r^{1-1/d}=r^{1-1/2}=r^{1/2}=\sqrt r
$$

So in the plane:

$$
\text{crossing number}=O(\sqrt r)
$$

This is the theorem stated on slide 92:

$$
\text{fine simplicial partition of size }r
\text{ and crossing number }O(\sqrt r)
$$

## 6. Paper Construction Time Used by Slides

The paper's exact algorithmic statement is in Theorem 4.7.

The slide uses the clean version:

$$
O(n^{1+\varepsilon})
$$

construction time for a planar fine simplicial partition with optimal crossing number:

$$
O(\sqrt r)
$$

This corresponds to Theorem 4.7(iii), which says for any s, a simplicial partition with crossing number:

$$
O(r^{1-1/d})
$$

can be constructed in:

$$
O(n^{1+\delta})
$$

Renaming the paper's fixed positive constant \(\delta\) as the lecture's \(\varepsilon\), in 2D this becomes:

$$
O(n^{1+\varepsilon})
$$

preprocessing/construction time.

## 7. Building the Partition Tree from the Theorem

At a node containing n points:

- build a fine simplicial r-partition,
- create r children,
- each child contains at most:

$$
\frac{2n}{r}
$$

points,
- store the triangle/simplex for each child.

For a halfplane query, the boundary is a line.

At the current node:

1. Check all r child triangles.
2. If a child triangle is fully inside the query halfplane, add its stored aggregate answer.
3. If it is disjoint, ignore it.
4. If it is crossed by the query boundary line, recurse into that child.

Because the crossing number is:

$$
O(\sqrt r)
$$

the query recurses into only:

$$
O(\sqrt r)
$$

children.

This gives the slide recurrence:

$$
T(n)=r+\sqrt r\cdot T(2n/r)
$$

The first term r is the cost of scanning all r children at the current node.

The recursive term appears because:

- at most \(\sqrt r\) children are crossed,
- each crossed child has at most \(2n/r\) points.

## 8. Solving the Slide Query Recurrence

The recurrence is:

$$
T(n)=r+\sqrt r\cdot T(2n/r)
$$

The slides choose r as a sufficiently large constant depending only on \(\varepsilon\). Therefore r does not grow with n.

We prove:

$$
T(n)=O(n^{1/2+\varepsilon})
$$

Assume inductively:

$$
T(m)\le C m^{1/2+\varepsilon}
$$

Then:

$$
T(n)\le r+\sqrt r\cdot C(2n/r)^{1/2+\varepsilon}
$$

Simplify the recursive term:

$$
\sqrt r\cdot (2n/r)^{1/2+\varepsilon}
=
r^{1/2}\cdot 2^{1/2+\varepsilon}n^{1/2+\varepsilon}r^{-1/2-\varepsilon}
$$

Cancel the powers of r:

$$
r^{1/2}r^{-1/2-\varepsilon}=r^{-\varepsilon}
$$

So:

$$
\sqrt r\cdot (2n/r)^{1/2+\varepsilon}
=
2^{1/2+\varepsilon}r^{-\varepsilon}n^{1/2+\varepsilon}
$$

Thus:

$$
T(n)\le r+C2^{1/2+\varepsilon}r^{-\varepsilon}n^{1/2+\varepsilon}
$$

To make the induction close, choose r so large that:

$$
2^{1/2+\varepsilon}r^{-\varepsilon}<1
$$

Equivalently:

$$
r>2^{(1/2+\varepsilon)/\varepsilon}
$$

The slide gives one convenient constant choice of this type:

$$
r=2\cdot 2^{1/(2\varepsilon)}
$$

Up to constant-factor slack, this is just saying:

$$
r=\Theta(2^{1/(2\varepsilon)})
$$

With such a constant r:

$$
T(n)=O(n^{1/2+\varepsilon})
$$

This is slide 95.

## 9. Space Bound in the Slides

At a node with m points, the partition creates r children.

Because r is chosen as a constant depending only on \(\varepsilon\), each node has constant branching factor.

Each point belongs to exactly one child at each level.

The partition tree stores:

- one aggregate value per child,
- one simplex/triangle per child,
- leaves for constant-size point sets.

The total number of tree nodes is linear in the number of leaves, and the leaves partition the original point set.

Therefore total space is:

$$
O(n)
$$

This is slide 93.

## 10. Preprocessing Bound in the Slides

At each node, the expensive step is constructing the simplicial partition.

The lecture uses Matousek's construction-time guarantee:

$$
O(m^{1+\varepsilon})
$$

for a node with m points, with r treated as a constant depending on \(\varepsilon\).

Since the children form a partition of the node's points and each child has at most a constant fraction of the parent points, the total over the recursive tree remains:

$$
O(n^{1+\varepsilon})
$$

Intuition:

At one level with subproblem sizes \(m_1,\ldots,m_k\), where:

$$
\sum_j m_j=n
$$

and each \(m_j\) is a constant fraction of its parent, the superlinear exponent makes the geometric decay dominate across levels.

Hence total preprocessing:

$$
O(n^{1+\varepsilon})
$$

This is slide 94.

## 11. Final Slide Theorem

Combining:

- Matousek 2D simplicial partition theorem:

$$
O(\sqrt r)
$$

crossing number,

- constant-r recursive partition tree,
- recurrence:

$$
T(n)=r+\sqrt r\cdot T(2n/r)
$$

- sufficiently large constant r depending on \(\varepsilon\),

gives:

$$
T(n)=O(n^{1/2+\varepsilon})
$$

The resulting planar halfplane range searching structure has:

$$
O(n)
$$

space,

$$
O(n^{1+\varepsilon})
$$

construction time,

and:

$$
O(n^{1/2+\varepsilon})
$$

query time.

This is exactly slide 96.

