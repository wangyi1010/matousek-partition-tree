// Crossover benchmark: native C++ partition tree vs native C++ brute force,
// for 2D halfplane range counting on a fixed point set queried many times.
//
// This is the native counterpart of benchmarks/measure_crossings.py's
// practical baseline: it isolates "does the tree structure help?" from
// "is C faster than Python?" by putting both methods in the same language,
// same compiler, same -O3. Mirrors src/matousek_partition_tree/practical.py:
// wider-axis median split into r groups, leaves scanned directly, queries
// prune whole cells that fall entirely inside/outside the halfplane.
//
// Build:  c++ -O3 -march=native -std=c++17 cpp/bench.cpp -o cpp/bench
// Run:    ./cpp/bench

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <random>
#include <vector>

struct Point { double x, y; };
struct Halfplane { double a, b, c; };
struct Box { double min_x, min_y, max_x, max_y; };

enum Status { INSIDE, OUTSIDE, CROSSING };

static Box bounding_box(const std::vector<Point>& pts) {
    double mnx = pts[0].x, mny = pts[0].y, mxx = pts[0].x, mxy = pts[0].y;
    for (const auto& p : pts) {
        mnx = std::min(mnx, p.x); mny = std::min(mny, p.y);
        mxx = std::max(mxx, p.x); mxy = std::max(mxy, p.y);
    }
    return {mnx, mny, mxx, mxy};
}

static inline bool in_halfplane(const Point& p, const Halfplane& h) {
    return h.a * p.x + h.b * p.y + h.c >= 0.0;
}

static Status classify(const Box& b, const Halfplane& h) {
    double v[4] = {
        h.a * b.min_x + h.b * b.min_y + h.c,
        h.a * b.min_x + h.b * b.max_y + h.c,
        h.a * b.max_x + h.b * b.min_y + h.c,
        h.a * b.max_x + h.b * b.max_y + h.c,
    };
    bool all_in = true, all_out = true;
    for (double x : v) { if (x >= 0.0) all_out = false; else all_in = false; }
    if (all_in) return INSIDE;
    if (all_out) return OUTSIDE;
    return CROSSING;
}

struct Node {
    Box cell;
    int count;
    std::vector<Point> points;          // non-empty only for leaves
    std::vector<std::unique_ptr<Node>> children;
    bool is_leaf() const { return children.empty(); }
};

// wider-axis median split (mirrors practical.py split_once)
static void split_once(const std::vector<Point>& pts,
                       std::vector<Point>& left, std::vector<Point>& right) {
    Box b = bounding_box(pts);
    int axis = (b.max_x - b.min_x) >= (b.max_y - b.min_y) ? 0 : 1;
    std::vector<Point> ordered = pts;
    std::sort(ordered.begin(), ordered.end(), [axis](const Point& p, const Point& q) {
        double pa = axis == 0 ? p.x : p.y, qa = axis == 0 ? q.x : q.y;
        double pb = axis == 0 ? p.y : p.x, qb = axis == 0 ? q.y : q.x;
        return pa != qa ? pa < qa : pb < qb;
    });
    size_t mid = ordered.size() / 2;
    left.assign(ordered.begin(), ordered.begin() + mid);
    right.assign(ordered.begin() + mid, ordered.end());
}

// partition into r groups by repeatedly splitting the largest (mirrors practical.py)
static std::vector<std::vector<Point>> partition_points(const std::vector<Point>& pts, int r) {
    std::vector<std::vector<Point>> groups;
    groups.push_back(pts);
    while ((int)groups.size() < r) {
        size_t idx = 0;
        for (size_t i = 1; i < groups.size(); i++)
            if (groups[i].size() > groups[idx].size()) idx = i;
        if (groups[idx].size() <= 1) break;
        std::vector<Point> g = std::move(groups[idx]);
        groups.erase(groups.begin() + idx);
        std::vector<Point> l, rr;
        split_once(g, l, rr);
        if (!l.empty()) groups.push_back(std::move(l));
        if (!rr.empty()) groups.push_back(std::move(rr));
    }
    return groups;
}

static std::unique_ptr<Node> build_tree(const std::vector<Point>& pts, int r, int leaf_size) {
    auto node = std::make_unique<Node>();
    node->cell = bounding_box(pts);
    node->count = (int)pts.size();
    if ((int)pts.size() <= leaf_size) {
        node->points = pts;
        return node;
    }
    auto groups = partition_points(pts, std::min(r, (int)pts.size()));
    for (auto& g : groups)
        node->children.push_back(build_tree(g, r, leaf_size));
    return node;
}

static int query_count(const Node* node, const Halfplane& h) {
    Status s = classify(node->cell, h);
    if (s == INSIDE) return node->count;
    if (s == OUTSIDE) return 0;
    if (node->is_leaf()) {
        int c = 0;
        for (const auto& p : node->points) c += in_halfplane(p, h);
        return c;
    }
    int c = 0;
    for (const auto& ch : node->children) c += query_count(ch.get(), h);
    return c;
}

// brute force over struct-of-arrays (autovectorizes under -O3)
static int brute_count(const std::vector<double>& xs, const std::vector<double>& ys,
                       const Halfplane& h) {
    int c = 0;
    size_t n = xs.size();
    for (size_t i = 0; i < n; i++) c += (h.a * xs[i] + h.b * ys[i] + h.c >= 0.0);
    return c;
}

using clk = std::chrono::steady_clock;
static double secs(clk::time_point a, clk::time_point b) {
    return std::chrono::duration<double>(b - a).count();
}

int main() {
    const int Q = 200, R = 8, LEAF = 16;
    const std::vector<int> Ns = {1000, 10000, 100000, 500000, 1000000};
    std::mt19937_64 rng(42);
    std::uniform_real_distribution<double> u01(0.0, 1.0), um11(-1.0, 1.0);

    std::printf("Q = %d queries over a fixed set, tree r=%d leaf=%d\n\n", Q, R, LEAF);
    std::printf("%9s | %11s | %11s %11s %10s | %11s %11s %8s\n",
                "N", "build tree", "tree/q", "brute/q", "speedup",
                "tree tot", "brute tot", "winner");
    std::printf("--------------------------------------------------------------------------------------------\n");

    for (int n : Ns) {
        std::vector<Point> pts(n);
        std::vector<double> xs(n), ys(n);
        for (int i = 0; i < n; i++) { pts[i] = {u01(rng), u01(rng)}; xs[i] = pts[i].x; ys[i] = pts[i].y; }
        std::vector<Halfplane> qs(Q);
        for (int i = 0; i < Q; i++) qs[i] = {um11(rng), um11(rng), um11(rng)};

        auto t0 = clk::now();
        auto tree = build_tree(pts, R, LEAF);
        double build = secs(t0, clk::now());

        volatile long sink = 0;
        t0 = clk::now();
        for (const auto& h : qs) sink += query_count(tree.get(), h);
        double tree_q_tot = secs(t0, clk::now());

        t0 = clk::now();
        for (const auto& h : qs) sink += brute_count(xs, ys, h);
        double brute_q_tot = secs(t0, clk::now());

        // correctness check
        for (const auto& h : qs)
            if (query_count(tree.get(), h) != brute_count(xs, ys, h)) {
                std::printf("MISMATCH at n=%d\n", n); return 1;
            }

        double tq = tree_q_tot / Q, bq = brute_q_tot / Q;
        double tree_total = build + tree_q_tot, brute_total = brute_q_tot;  // brute has ~0 build
        const char* winner = tree_total < brute_total ? "tree" : "brute";
        std::printf("%9d | %9.1fms | %8.1fus %8.1fus %9.2fx | %8.1fms %8.1fms %8s\n",
                    n, build * 1e3, tq * 1e6, bq * 1e6, bq / tq,
                    tree_total * 1e3, brute_total * 1e3, winner);
    }

    // --- query-volume sweep: where does total time (build + Q queries) cross? ---
    std::printf("\nTotal-time crossover (build amortized over query volume):\n");
    std::printf("%9s %8s | %11s %11s %8s | %s\n",
                "N", "Q", "tree tot", "brute tot", "winner", "break-even Q");
    std::printf("------------------------------------------------------------------------\n");
    for (int n : {100000, 1000000}) {
        std::vector<Point> pts(n);
        std::vector<double> xs(n), ys(n);
        std::mt19937_64 r2(7);
        std::uniform_real_distribution<double> u01(0.0, 1.0), um11(-1.0, 1.0);
        for (int i = 0; i < n; i++) { pts[i] = {u01(r2), u01(r2)}; xs[i] = pts[i].x; ys[i] = pts[i].y; }

        auto t0 = clk::now();
        auto tree = build_tree(pts, R, LEAF);
        double build = secs(t0, clk::now());

        // per-query timings from a 200-query probe
        std::vector<Halfplane> probe(200);
        for (auto& h : probe) h = {um11(r2), um11(r2), um11(r2)};
        volatile long sink = 0;
        t0 = clk::now();
        for (const auto& h : probe) sink += query_count(tree.get(), h);
        double tq = secs(t0, clk::now()) / probe.size();
        t0 = clk::now();
        for (const auto& h : probe) sink += brute_count(xs, ys, h);
        double bq = secs(t0, clk::now()) / probe.size();

        double breakeven = (bq > tq) ? build / (bq - tq) : 1e18;
        for (int qv : {200, 2000, 20000}) {
            double tt = build + tq * qv, bt = bq * qv;
            std::printf("%9d %8d | %9.1fms %9.1fms %8s | ~%.0f queries\n",
                        n, qv, tt * 1e3, bt * 1e3, tt < bt ? "tree" : "brute", breakeven);
        }
    }
    return 0;
}
