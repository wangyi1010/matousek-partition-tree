# Two-Dimensional Partition Theorem: Math Derivation

Source: planar specialization of Matousek's Partition Theorem from *Efficient Partition Trees*. The cutting theorem used as a black box is the Chazelle-Friedman cutting machinery.

## Goal

Input:

$$
P=\lbrace p_1,\ldots,p_n \rbrace\subset\mathbb R^2
$$

Choose:

$$
2\le s< n
$$

Set:

$$
r=\frac ns
$$

Construct:

$$
\Pi=\lbrace (P_1,\Delta_1),\ldots,(P_m,\Delta_m) \rbrace
$$

such that:

$$
P_i\cap P_j=\varnothing\quad(i\ne j)
$$

$$
\bigcup_iP_i=P
$$

$$
P_i\subseteq\Delta_i
$$

$$
s\le |P_i|<2s
$$

and:

$$
\mathrm{cr}(\Pi)=O(\sqrt r)
$$

For a line h:

$$
\mathrm{cr}_\Pi(h) = |\lbrace i:h\text{ crosses }\Delta_i \rbrace|
$$

and:

$$
\mathrm{cr}(\Pi)=\max_h\mathrm{cr}_\Pi(h)
$$

## Cutting Inputs

For n lines in the plane, a $`(1/t)`$-cutting has:

$$
O(t^2)
$$

cells, and each cell is crossed by:

$$
O\left(\frac nt\right)
$$

lines.

Weighted version:

For weighted lines $`(Q,w)`$, define:

$$
W=\sum_{q\in Q}w(q)
$$

A weighted $`(1/t)`$-cutting satisfies for every cell C:

$$
\sum_{q\in Q(C)}w(q)\le \frac Wt
$$

where:

$$
Q(C)=\lbrace q\in Q:q\text{ crosses }C \rbrace
$$

In 2D, for some absolute constant A:

$$
\\#\text{faces}\le At^2
$$

## Step 1: Build the Finite Test Set Q

Use duality:

$$
p=(a,b)\longleftrightarrow p^\ast :y=ax-b
$$

$$
\ell:y=ax-b\longleftrightarrow \ell^\ast =(a,b)
$$

Incidence:

$$
p\in\ell\Longleftrightarrow \ell^\ast \in p^\ast 
$$

Above-below:

$$
p\text{ above }\ell \Longleftrightarrow \ell^\ast \text{ above }p^\ast 
$$

Verification:

Let:

$$
p=(u,v)
$$

and:

$$
\ell:y=ax-b
$$

Then:

$$
p\text{ above }\ell \Longleftrightarrow v>au-b
$$

Also:

$$
p^\ast :y=ux-v
$$

and:

$$
\ell^\ast =(a,b)
$$

The dual point $`\ell^*`$ is above the dual line $`p^*`$ iff:

$$
b>ua-v
$$

which is equivalent to:

$$
v>au-b
$$

Dualize P:

$$
P^\ast =\lbrace p_1^\ast ,\ldots,p_n^\ast  \rbrace
$$

Choose:

$$
t=\beta\sqrt r
$$

with beta small enough that the cutting has at most r vertices.

Since:

$$
O(t^2)=O(\beta^2r)\le r
$$

the vertex set:

$$
V=\lbrace v_1,\ldots,v_N \rbrace
$$

satisfies:

$$
N\le r
$$

Dualize vertices back:

$$
q_j=v_j^\ast 
$$

Define:

$$
Q=\lbrace q_1,\ldots,q_N \rbrace
$$

Thus:

$$
|Q|=N\le r
$$

Important object distinction:

$$
R\subseteq P^\ast 
$$

is the sampled set of about t dual lines used to build the cutting.

$$
V
$$

is the set of cutting vertices, which are points in the dual plane.

$$
Q=V^\ast 
$$

is a new set of primal lines.

Thus:

$$
Q\not\subseteq P^\ast 
$$

The cutting parameter is:

$$
t=\Theta(\sqrt r)
$$

so every dual cutting cell A is crossed by at most:

$$
O\left(\frac n{\sqrt r}\right)
$$

dual lines from $`P^*`$.

## Step 2: Test Set Lemma

Assume $`\Pi`$ is any simplicial partition with:

$$
|P_i|\ge s
$$

Define:

$$
K_Q=\max_{q\in Q}\mathrm{cr}_\Pi(q)
$$

Claim:

$$
\forall h,\quad \mathrm{cr}_\Pi(h) \le 3K_Q + O\left(\frac{n}{s\sqrt r}\right)
$$

Proof skeleton:

Take any nonvertical line h. Its dual point is:

$$
h^\ast 
$$

Let A be the triangular dual cutting cell with:

$$
h^\ast \in\mathrm{int}(A)
$$

Let:

$$
A=\mathrm{conv}\lbrace v_1,v_2,v_3 \rbrace
$$

Define:

$$
q_j=v_j^\ast 
$$

Then:

$$
q_1,q_2,q_3\in Q
$$

Cells crossed by at least one of $`q_1,q_2,q_3`$ are at most:

$$
3K_Q
$$

Detailed count:

$$
\mathrm{cr}_\Pi(q_1)\le K_Q
$$

$$
\mathrm{cr}_\Pi(q_2)\le K_Q
$$

$$
\mathrm{cr}_\Pi(q_3)\le K_Q
$$

Therefore:

$$
|\lbrace \Delta_i:\Delta_i\text{ crossed by at least one of }q_1,q_2,q_3 \rbrace| \le K_Q+K_Q+K_Q = 3K_Q
$$

Call $`\Delta_i`$ bad if:

$$
h\text{ crosses }\Delta_i
$$

but:

$$
q_1,q_2,q_3\text{ do not cross }\Delta_i
$$

Key geometric implication:

$$
\Delta_i\text{ bad and }p\in P_i \Longrightarrow p^\ast \cap A\ne\varnothing
$$

Reason in sign language:

The three primal lines $`q_1,q_2,q_3`$ decompose the primal plane into sign cells.

The all-above cell is:

$$
\lbrace x:x\text{ is above }q_1,q_2,q_3 \rbrace
$$

The all-below cell is:

$$
\lbrace x:x\text{ is below }q_1,q_2,q_3 \rbrace
$$

If h crossed the all-above cell, there would be:

$$
x\in h
$$

with:

$$
x\text{ above }q_1,q_2,q_3
$$

By duality:

$$
q_1^\ast =v_1,\quad q_2^\ast =v_2,\quad q_3^\ast =v_3
$$

all lie on the same side of $`x^*`$.

Since:

$$
x\in h
$$

we have:

$$
h^\ast \in x^\ast 
$$

So $`x^*`$ is a line through an interior point of triangle A.

But a line through an interior point of a triangle cannot put all three triangle vertices on the same side. Contradiction.

The same applies to the all-below cell.

Therefore every sign cell crossed by h is mixed-sign.

Now let:

$$
p\in P_i\subseteq\Delta_i
$$

where $`\Delta_i`$ is bad.

Because $`q_1,q_2,q_3`$ do not cross $`\Delta_i`$, the simplex $`\Delta_i`$ lies inside one sign cell of their arrangement.

Since h crosses $`\Delta_i`$, that sign cell is crossed by h, hence is mixed-sign.

So p has mixed signs relative to:

$$
q_1,q_2,q_3
$$

By above-below duality, the vertices:

$$
v_1,v_2,v_3
$$

are not all on the same side of $`p^*`$.

If $`p^*`$ did not cross A, then the convex triangle:

$$
A=\mathrm{conv}\lbrace v_1,v_2,v_3 \rbrace
$$

would lie entirely on one side of $`p^*`$, so all three vertices would be on the same side.

Contradiction. Thus:

$$
p^\ast \cap A\ne\varnothing
$$

Equivalently:

$$
\text{bad primal simplex} \Longrightarrow \text{dual conflict with }A
$$

Since A is a $`(1/\sqrt r)`$-cutting cell:

$$
|\lbrace p\in P:p^\ast \cap A\ne\varnothing \rbrace| = O\left(\frac n{\sqrt r}\right)
$$

Bad groups are disjoint and each has at least s points, so:

$$
\\#\text{bad simplices} \le O\left(\frac{n/\sqrt r}{s}\right)
$$

Detailed division:

Let B be the number of bad simplices.

Each bad simplex contributes at least s original points:

$$
|P_i|\ge s
$$

The bad groups are disjoint, so total bad points are at least:

$$
Bs
$$

But the dual conflict bound gives total bad points at most:

$$
O\left(\frac n{\sqrt r}\right)
$$

Thus:

$$
Bs\le O\left(\frac n{\sqrt r}\right)
$$

and:

$$
B\le O\left(\frac n{s\sqrt r}\right)
$$

Thus:

$$
\\#\text{bad simplices} = O\left(\frac{n}{s\sqrt r}\right)
$$

Therefore:

$$
\mathrm{cr}_\Pi(h) \le 3K_Q + O\left(\frac{n}{s\sqrt r}\right)
$$

Since:

$$
r=\frac ns
$$

we have:

$$
\frac{n}{s\sqrt r} = \frac r{\sqrt r} = \sqrt r
$$

So:

$$
K_Q=O(\sqrt r) \Longrightarrow \mathrm{cr}_\Pi(h)=O(\sqrt r)
$$

## Step 3: Construct $`\Pi`$ for Fixed Q

At round i:

$$
P^{(i)}=P\setminus(P_1\cup\cdots\cup P_i)
$$

$$
n_i=|P^{(i)}|
$$

For test line q:

$$
\kappa_i(q)=|\lbrace j\le i:q\text{ crosses }\Delta_j \rbrace|
$$

Define exponential weight:

$$
w_i(q)=2^{\kappa_i(q)}
$$

Total weight:

$$
W_i=\sum_{q\in Q}w_i(q)
$$

Initially:

$$
\kappa_0(q)=0
$$

$$
w_0(q)=1
$$

$$
W_0=|Q|
$$

If:

$$
n_i<2s
$$

make the terminal group:

$$
P_{i+1}=P^{(i)}
$$

and stop.

Otherwise choose:

$$
t_i=\alpha\sqrt{\frac{n_i}{s}}
$$

where alpha is small enough that:

$$
A\alpha^2\le 1
$$

Then:

$$
At_i^2 = A\alpha^2\frac{n_i}{s} \le \frac{n_i}{s}
$$

Known and chosen quantities in this formula:

$$
n_i=|P^{(i)}|
$$

is known at the start of round i.

$$
s
$$

is the fixed group-size parameter.

$$
A
$$

is the absolute constant from the weighted cutting theorem.

$$
t_i
$$

is chosen from these quantities.

The reason is the pigeonhole constraint:

$$
\\#\text{faces}\le At_i^2\le \frac{n_i}{s}
$$

so the average number of remaining points per face is at least:

$$
\frac{n_i}{n_i/s}=s
$$

Build a weighted $`(1/t_i)`$-cutting for $`(Q,w_i)`$.

For every face C:

$$
w_i(Q(C))\le \frac{W_i}{t_i}
$$

Number of faces:

$$
\le \frac{n_i}{s}
$$

Pigeonhole:

$$
\exists F_{i+1} \quad |P^{(i)}\cap F_{i+1}|\ge s
$$

Set:

$$
\Delta_{i+1}=F_{i+1}
$$

Choose:

$$
P_{i+1}\subseteq P^{(i)}\cap\Delta_{i+1}
$$

with:

$$
|P_{i+1}|=s
$$

Remove:

$$
P^{(i+1)}=P^{(i)}\setminus P_{i+1}
$$

## Step 4: Weight Recurrence

Let:

$$
Q_{i+1}=\lbrace q\in Q:q\text{ crosses }\Delta_{i+1} \rbrace
$$

For $`q\in Q_{i+1}`$:

$$
w_{i+1}(q)=2w_i(q)
$$

For $`q\notin Q_{i+1}`$:

$$
w_{i+1}(q)=w_i(q)
$$

Therefore:

$$
W_{i+1} = W_i+w_i(Q_{i+1})
$$

No-step derivation:

Split Q into crossing and noncrossing test lines:

$$
Q=Q_{i+1}\cup(Q\setminus Q_{i+1})
$$

Then:

$$
W_{i+1} = \sum_{q\notin Q_{i+1}}w_{i+1}(q) + \sum_{q\in Q_{i+1}}w_{i+1}(q)
$$

For noncrossing lines:

$$
w_{i+1}(q)=w_i(q)
$$

For crossing lines:

$$
w_{i+1}(q)=2w_i(q)
$$

So:

$$
W_{i+1} = \sum_{q\notin Q_{i+1}}w_i(q) + \sum_{q\in Q_{i+1}}2w_i(q)
$$

Rewrite:

$$
W_{i+1} = \sum_{q\in Q}w_i(q) + \sum_{q\in Q_{i+1}}w_i(q)
$$

Therefore:

$$
W_{i+1}=W_i+w_i(Q_{i+1})
$$

Since $`\Delta_{i+1}`$ is a cutting face:

$$
w_i(Q_{i+1})\le \frac{W_i}{t_i}
$$

Hence:

$$
W_{i+1} \le W_i\left(1+\frac1{t_i}\right)
$$

In nonterminal rounds:

$$
n_i=n-is
$$

and:

$$
\frac{n_i}{s}=r-i
$$

Thus:

$$
t_i=\Theta(\sqrt{r-i})
$$

so for a constant C:

$$
\frac1{t_i}\le \frac{C}{\sqrt{r-i}}
$$

Therefore:

$$
W_{i+1} \le W_i\left(1+\frac{C}{\sqrt{r-i}}\right)
$$

The terminal round can at most double every weight:

$$
W_m\le 2W_L
$$

where L is the number of nonterminal rounds.

## Step 5: Product Estimate

Since:

$$
L\le r
$$

we get:

$$
W_m \le 2|Q| \prod_{i=0}^{L-1} \left(1+\frac{C}{\sqrt{r-i}}\right)
$$

Taking logs:

$$
\log W_m \le O(1)+\log |Q| + \sum_{i=0}^{L-1} \log\left(1+\frac{C}{\sqrt{r-i}}\right)
$$

Using:

$$
\log(1+x)\le x
$$

gives:

$$
\log W_m \le O(1)+\log |Q| + C\sum_{i=0}^{L-1}\frac1{\sqrt{r-i}}
$$

Since:

$$
\sum_{i=0}^{L-1}\frac1{\sqrt{r-i}} \le \sum_{j=1}^{r}\frac1{\sqrt j}
$$

and:

$$
\sum_{j=1}^{r}j^{-1/2} \le 1+\int_1^r x^{-1/2}\,dx
$$

with:

$$
\int_1^r x^{-1/2}\,dx = 2(\sqrt r-1)
$$

we obtain:

$$
\sum_{j=1}^{r}j^{-1/2}=O(\sqrt r)
$$

Therefore:

$$
\log W_m = O(\log |Q|+\sqrt r)
$$

## Step 6: Bound $`K_Q`$

For any $`q\in Q`$:

$$
w_m(q)=2^{\kappa_m(q)}
$$

and:

$$
w_m(q)\le W_m
$$

Thus:

$$
2^{\kappa_m(q)}\le W_m
$$

Taking logs:

$$
\kappa_m(q)\le \log_2 W_m
$$

Hence:

$$
\kappa_m(q)=O(\log |Q|+\sqrt r)
$$

Therefore:

$$
K_Q = \max_{q\in Q}\kappa_m(q) = O(\log |Q|+\sqrt r)
$$

Since:

$$
|Q|\le r
$$

we have:

$$
\log |Q|\le \log r
$$

and:

$$
\log r=O(\sqrt r)
$$

Thus:

$$
K_Q=O(\sqrt r)
$$

Here:

$$
\kappa_i(q)
$$

is cumulative for one q up to round i.

$$
K_Q
$$

is the final maximum over all q in Q.

At the end:

$$
K_Q=\max_{q\in Q}\kappa_m(q)
$$

## Step 7: Extend from Q to All Lines

From the Test Set Lemma:

$$
\mathrm{cr}_\Pi(h) \le 3K_Q + O\left(\frac{n}{s\sqrt r}\right)
$$

Substitute:

$$
K_Q=O(\sqrt r)
$$

and:

$$
\frac{n}{s\sqrt r} = \sqrt r
$$

Then:

$$
\mathrm{cr}_\Pi(h) \le 3O(\sqrt r)+O(\sqrt r)
$$

so:

$$
\mathrm{cr}_\Pi(h)=O(\sqrt r)
$$

for every line h.

Therefore:

$$
\mathrm{cr}(\Pi)=O(\sqrt r)
$$

## Appendix: Proof of the 2D Cutting Lemma

Statement:

Given n lines H in the plane and a parameter t, there exists a cutting with:

$$
O(t^2)
$$

cells, such that every cell is crossed by at most:

$$
O\left(\frac nt\right)
$$

lines of H.

The weighted version replaces counts by total weights.

Proof skeleton:

Choose a random sample R from H of size:

$$
O(t)
$$

Build the arrangement of R and triangulate its cells. The arrangement of O(t) lines has:

$$
O(t^2)
$$

faces.

For a triangle $`\Delta`$, define its conflict list:

$$
H_\Delta=\{h\in H:h\text{ crosses }\Delta\}
$$

and its excess:

$$
e(\Delta)=\frac{|H_\Delta|}{n/t}=\frac{|H_\Delta|t}{n}
$$

If:

$$
e(\Delta)\le C
$$

for a sufficiently large constant C, then $`\Delta`$ is already good, because:

$$
|H_\Delta|\le C\frac nt
$$

If:

$$
e(\Delta)>C
$$

then refine $`\Delta`$ locally. Let:

$$
n_\Delta=|H_\Delta|
$$

To make each refined cell crossed by at most $`O(n/t)`$ original lines, use a local cutting for $`H_\Delta`$ with parameter:

$$
u_\Delta=\frac{n_\Delta}{n/t}=\frac{n_\Delta t}{n}=e(\Delta)
$$

This local refinement has:

$$
O(u_\Delta^2)=O(e(\Delta)^2)
$$

subcells, and each subcell is crossed by at most:

$$
O\left(\frac{n_\Delta}{u_\Delta}\right)=O\left(\frac nt\right)
$$

lines.

Thus the final cutting size is bounded by:

$$
\sum_{\Delta}O\left(\max\{1,e(\Delta)^2\}\right)
$$

The key random-sampling estimate is:

$$
\mathbb E\left[|\{\Delta:e(\Delta)\ge u\}|\right]\le C_1t^2e^{-C_2u}
$$

for constants $`C_1,C_2>0`$.

Using dyadic levels:

$$
\sum_{\Delta}\max\{1,e(\Delta)^2\}\le O(t^2)+\sum_{j\ge 0}O(2^{2j})\cdot|\{\Delta:2^j\le e(\Delta)<2^{j+1}\}|
$$

Taking expectations and applying the exponential tail bound:

$$
\mathbb E\left[\sum_{\Delta}\max\{1,e(\Delta)^2\}\right]\le O(t^2)+\sum_{j\ge 0}O(2^{2j})\cdot C_1t^2e^{-C_2 2^j}
$$

The series:

$$
\sum_{j\ge 0}2^{2j}e^{-C_2 2^j}
$$

converges, so:

$$
\mathbb E\left[\sum_{\Delta}\max\{1,e(\Delta)^2\}\right]=O(t^2)
$$

Therefore some random sample produces a cutting of size:

$$
O(t^2)
$$

with every final cell crossed by at most:

$$
O\left(\frac nt\right)
$$

lines.

Weighted form:

For weighted lines $`(H,w)`$, let:

$$
W=w(H)
$$

Sample lines with probability proportional to weight, or equivalently replace each line h by $`w(h)`$ copies after scaling rational weights to integers. The same argument gives cells C satisfying:

$$
w(H_C)\le O\left(\frac Wt\right)
$$

After absorbing constants into the cutting parameter, this is the weighted cutting form used in the partition proof:

$$
w(H_C)\le \frac Wt
$$

Scope of this appendix:

This appendix explains why the cutting tool is valid and why the two-dimensional complexity is $`O(t^2)`$. The sharp optimal version relies on the exponential decay estimate above, which is the Chazelle-Friedman sampling argument cited in the references.

## Final Statement

For every finite point set:

$$
P\subset\mathbb R^2
$$

and every:

$$
2\le s< n
$$

with:

$$
r=\frac ns
$$

there exists a simplicial partition:

$$
\Pi=\lbrace (P_1,\Delta_1),\ldots,(P_m,\Delta_m) \rbrace
$$

such that:

$$
s\le |P_i|<2s
$$

and:

$$
\mathrm{cr}(\Pi)=O(\sqrt r)
$$

## Preprocessing Time: Building the Partition Tree

This is a theorem-level bound for the *construction* of the whole tree,
separate from the query recurrence. It is the theorem's guarantee, **not** a
proved wall-clock bound for this Python implementation (which uses exact
`Fraction` arithmetic and randomized cutting retries — see the caveat at the
end).

Let $`B(m)`$ be the time to build a partition tree on $`m`$ points. For any
fixed $`\delta>0`$, one simplicial partition at a node is constructed in
$`O(m^{1+\delta})`$ time, so:

$$
B(m)=O\left(m^{1+\delta}\right)+\sum_i B(m_i),
$$

where the child classes are disjoint and each is a constant factor smaller:

$$
\sum_i m_i=m,\qquad m_i\le\frac{2m}{r}.
$$

**Cost at a single depth.** Fix a depth $`j`$ of the recursion tree, and let
$`V_j`$ be the nodes at that depth. Their point sets are disjoint, so their
sizes sum to at most $`m`$, and by applying the size shrinkage $`j`$ times the
largest one is bounded:

$$
\sum_{v\in V_j}m_v\le m,\qquad \max_{v\in V_j}m_v\le m\left(\frac{2}{r}\right)^j.
$$

Split each per-node cost as $`m_v^{1+\delta}=m_v\,m_v^{\delta}`$ and pull out
the max on the $`\delta`$ factor:

$$
\begin{aligned}
C_j
&=\sum_{v\in V_j}O\left(m_v^{1+\delta}\right)
 =O\left(\sum_{v\in V_j}m_v\,m_v^{\delta}\right)\\
&\le O\left(\left(\max_{v\in V_j}m_v\right)^{\delta}\sum_{v\in V_j}m_v\right)
 \le O\left(m^{1+\delta}\left(\frac{2}{r}\right)^{j\delta}\right).
\end{aligned}
$$

**Sum over all depths.** For fixed $`r>2`$ the per-level factor is below one,
so the level costs form a convergent geometric series:

$$
\left(\frac{2}{r}\right)^{\delta}<1
\quad\Longrightarrow\quad
\sum_{j\ge0}\left(\frac{2}{r}\right)^{j\delta}=\frac{1}{1-\left(\frac{2}{r}\right)^{\delta}}=O(1).
$$

Therefore:

$$
B(m)=O\left(m^{1+\delta}\sum_{j\ge0}\left(\frac{2}{r}\right)^{j\delta}\right)=O\left(m^{1+\delta}\right).
$$

**Matching the stated bound.** Taking $`\delta=\varepsilon/2`$ gives the
stronger intermediate bound $`O(n^{1+\varepsilon/2})`$, and hence the standard
stated preprocessing bound:

$$
B(n)=O\left(n^{1+\varepsilon}\right).
$$

Note that $`O(n\log n)\subsetneq O(n^{1+\varepsilon})`$ strictly: for every
fixed $`\varepsilon>0`$ we have $`\log n=O(n^{\varepsilon})`$ but not the
reverse. Matoušek's tighter $`O(n\log n)`$ preprocessing is a separate result
that charges construction against the partition structure rather than this
level-by-level geometric series.

**Caveat for this implementation.** The bound above is the theoretical
guarantee. It does **not** claim this Python code runs in $`O(n^{1+\varepsilon})`$
wall-clock time: that would additionally require a bit-complexity analysis of
exact `Fraction` arithmetic and a runtime analysis of the randomized cutting
retries and runtime verification. This code trades all of that away for exact
arithmetic and verifiable preconditions, and is correspondingly slow.

## References

- Jiri Matousek, **Efficient Partition Trees**, *Discrete & Computational Geometry* 8, 315-334, 1992.
- Bernard Chazelle and Joel Friedman, **A deterministic view of random sampling and its use in geometry**, *Combinatorica* 10, 229-249, 1990.
