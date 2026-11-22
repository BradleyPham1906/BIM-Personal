"""Stormwater worked examples: D8 flow direction and accumulation with Priority-Flood filling,
and the rational method.

Research note: docs/research/research-physical-world/formfinding-runoff.md (topic B).
Data only, never part of a suite. Run: python3 -I runoff.py  (standard library only).

Sources the code follows (read 2026-11-21):
- D8 as WhiteboxTools d8_pointer.rs (MIT): steepest drop / distance over 8 neighbours, the
  diagonal distance sqrt(dx^2 + dy^2), the first neighbour wins a tie, no positive drop -> 0 (pit/flat).
- Priority-Flood and Priority-Flood+epsilon: Barnes, Lehman, Mulla 2014, Algorithms 1 and 3 (arXiv 1511.04463).
- Accumulation as WhiteboxTools d8_flow_accum.rs: every cell starts at 1 (itself), passed downstream
  in topological order (cells with no inflow first).
- Rational method: HEC-22 4th ed. (FHWA-HIF-24-006, 2024) eq. 4.1 Q = C I A / Ku, Ku = 360 in SI;
  weighted C eq. 4.2; Table 4.1 ranges.
"""
import heapq
import math
import random
import time

DR = [-1, -1, 0, 1, 1, 1, 0, -1]   # neighbour order: N, NE, E, SE, S, SW, W, NW (row grows south)
DC = [0, 1, 1, 1, 0, -1, -1, -1]
NAMES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def d8(z, cell=1.0):
    rows, cols = len(z), len(z[0])
    out = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            best, bdir = 0.0, None
            for k in range(8):
                rr, cc = r + DR[k], c + DC[k]
                if 0 <= rr < rows and 0 <= cc < cols:
                    dist = cell * (math.sqrt(2.0) if DR[k] and DC[k] else 1.0)
                    s = (z[r][c] - z[rr][cc]) / dist
                    if s > best:          # strict: the first steepest wins a tie
                        best, bdir = s, k
            out[r][c] = bdir             # None = no lower neighbour: a pit, a flat or an outlet
    return out


def priority_flood(z, eps=0.0):
    """Algorithm 1 (eps = 0) or a plain-epsilon form of Algorithm 3: each cell reached from c is
    raised to at least z(c) + eps, so filled depressions drain. Edge cells are the outlets."""
    rows, cols = len(z), len(z[0])
    w = [row[:] for row in z]
    closed = [[False] * cols for _ in range(rows)]
    pq, n = [], 0
    for r in range(rows):
        for c in range(cols):
            if r in (0, rows - 1) or c in (0, cols - 1):
                heapq.heappush(pq, (w[r][c], n, r, c)); n += 1
                closed[r][c] = True
    while pq:
        h, _, r, c = heapq.heappop(pq)
        for k in range(8):
            rr, cc = r + DR[k], c + DC[k]
            if 0 <= rr < rows and 0 <= cc < cols and not closed[rr][cc]:
                closed[rr][cc] = True
                if w[rr][cc] <= w[r][c]:
                    w[rr][cc] = w[r][c] + eps
                heapq.heappush(pq, (w[rr][cc], n, rr, cc)); n += 1
    return w


def accumulate(fd):
    rows, cols = len(fd), len(fd[0])
    acc = [[1] * cols for _ in range(rows)]
    inflow = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            k = fd[r][c]
            if k is not None:
                inflow[r + DR[k]][c + DC[k]] += 1
    stack = [(r, c) for r in range(rows) for c in range(cols) if inflow[r][c] == 0]
    seen = 0
    while stack:
        r, c = stack.pop(); seen += 1
        k = fd[r][c]
        if k is not None:
            rr, cc = r + DR[k], c + DC[k]
            acc[rr][cc] += acc[r][c]
            inflow[rr][cc] -= 1
            if inflow[rr][cc] == 0:
                stack.append((rr, cc))
    assert seen == rows * cols, "a cycle in the flow directions"
    return acc


def show(title, grid, fmt):
    print(title)
    for row in grid:
        print("   " + " ".join(fmt(v) for v in row))


def rational_si(C, i_mm_h, A_ha):
    return C * i_mm_h * A_ha / 360.0


def main():
    print("=== B4(a) D8 on a 4 x 4 tilted plane, 1 m cells, with one pit")
    z = [[10.0 - r - 0.5 * c for c in range(4)] for r in range(4)]
    z[1][1] = 6.0   # the plane gives 8.5 there; 6.0 is below all eight neighbours (lowest 7.0)
    show("elevation (m), row 0 north:", z, lambda v: "%5.2f" % v)
    fd0 = d8(z)
    show("D8 before filling ('.' = no lower neighbour):", fd0, lambda k: "%2s" % (NAMES[k] if k is not None else "."))
    acc0 = accumulate(fd0)
    show("accumulation before filling (cells, itself included):", acc0, lambda v: "%2d" % v)

    w = priority_flood(z)
    show("Priority-Flood (eps = 0):", w, lambda v: "%5.2f" % v)
    fd1 = d8(w)
    show("D8 after eps = 0 fill (the filled pit is a flat):", fd1, lambda k: "%2s" % (NAMES[k] if k is not None else "."))
    we = priority_flood(z, eps=1e-3)
    fde = d8(we)
    show("D8 after eps = 0.001 fill:", fde, lambda k: "%2s" % (NAMES[k] if k is not None else "."))
    acc = accumulate(fde)
    show("accumulation (cells):", acc, lambda v: "%2d" % v)
    print("pit raised from 6.000 to %.3f m; outlet cell (3,3) collects %d of 16 cells" % (we[1][1], acc[3][3]))
    print("total of outlet (edge, no lower neighbour) cells' accumulation = %d"
          % sum(acc[r][c] for r in range(4) for c in range(4) if fde[r][c] is None))

    print("\n=== timing proxy: 200 x 200 random-relief grid, Priority-Flood+eps, D8, accumulation (CPython)")
    random.seed(1)
    n = 200
    zz = [[0.02 * (r + c) + random.random() for c in range(n)] for r in range(n)]
    t0 = time.perf_counter(); wf = priority_flood(zz, eps=1e-6); t1 = time.perf_counter()
    f = d8(wf); t2 = time.perf_counter(); a = accumulate(f); t3 = time.perf_counter()
    raised = sum(1 for r in range(n) for c in range(n) if wf[r][c] > zz[r][c])
    print("fill %.0f ms (%d of %d cells raised), D8 %.0f ms, accumulation %.0f ms; max accumulation %d"
          % ((t1 - t0) * 1e3, raised, n * n, (t2 - t1) * 1e3, (t3 - t2) * 1e3, max(max(r) for r in a)))

    print("\n=== B4(b) rational method, 2 ha site: 1 ha roofs C = 0.9, 1 ha lawn C = 0.3, i = 100 mm/h")
    C = (0.9 * 1.0 + 0.3 * 1.0) / 2.0
    Q = rational_si(C, 100.0, 2.0)
    print("composite C = %.3f (HEC-22 eq. 4.2)" % C)
    print("Q = C i A / 360 = %.6f m3/s = %.1f L/s" % (Q, Q * 1000))
    print("Q = 0.00278 C i A = %.6f m3/s (rounded constant, +%.2f%%)" % (0.00278 * C * 100 * 2, (0.00278 * 360 - 1) * 100))
    # customary units, Ku = 1: Q (ft3/s) = C I(in/h) A(ac); 1 ac-in/h = 1.0083 ft3/s
    A_ac = 2.0 * 10000 / 4046.8564224
    I_in = 100.0 / 25.4
    Qcfs = C * I_in * A_ac
    print("customary: A = %.4f ac, I = %.4f in/h, Q = %.4f ft3/s = %.6f m3/s (%.2f%% below SI: Ku = 1 drops 1.0083)"
          % (A_ac, I_in, Qcfs, Qcfs * 0.3048 ** 3, (1 - Qcfs * 0.3048 ** 3 / Q) * 100))
    # HEC-22 Example 4.3 check
    print("HEC-22 Ex. 4.3: 0.235*1.9*43.3 = %.1f ft3/s, 0.315*2.3*43.3 = %.1f ft3/s" % (0.235 * 1.9 * 43.3, 0.315 * 2.3 * 43.3))
    print("   in m3/s: %.3f and %.3f (the manual prints 0.55 and '89 m3/s', a typo for 0.89)"
          % (0.235 * 1.9 * 43.3 * 0.3048 ** 3, 0.315 * 2.3 * 43.3 * 0.3048 ** 3))

    print("\n=== time of concentration and a NOAA Atlas 14 intensity")
    L, S = 200.0, 0.02
    t = 0.0195 * L ** 0.770 * S ** -0.385
    print("Kirpich (TxDOT eq. 4-15, SI K = 0.0195): L = %.0f m, S = %.3f -> tc = %.2f min" % (L, S, t))
    V = 1.0 * 0.619 * (S * 100) ** 0.5
    print("HEC-22 eq. 4.4, paved shallow concentrated flow k = 0.619, Sp = 2%%: V = %.3f m/s, 200 m in %.2f min" % (V, 200 / V / 60))
    # Philadelphia (39.9526, -75.1652), PFDS english PDS, read 2026-11-21: 10-yr 5-min 6.47 in/h, 10-min 5.17 in/h
    for d, inch in (("5-min", 6.47), ("10-min", 5.17)):
        i = inch * 25.4
        print("PFDS 10-yr %s: %.2f in/h = %.1f mm/h -> Q(2 ha, C = 0.6) = %.4f m3/s" % (d, inch, i, rational_si(C, i, 2.0)))
    print("metric CSV gives 164 and 131 mm/h (rounded to whole mm/h)")


if __name__ == "__main__":
    main()
