"""Form-finding worked examples: the force density method (FDM) and dynamic relaxation (DR).

Research note: docs/research/research-physical-world/formfinding-runoff.md (topic A).
Data only, never part of a suite. Run: python3 -I formfinding.py  (numpy 2.x; the pure-Python
solvers below do not need it and are what an ES5 port would follow).

Sign convention (as compas_fd's fd_numpy and jax_fdm, read 2026-11-21):
    (Ci^T Q Ci) x_free = p_free - Ci^T Q Cf x_fixed,   per axis x, y, z
with C the edge-node connectivity matrix (+1 at the edge's start, -1 at its end), Q = diag(q),
p the nodal loads, and q > 0 meaning tension.
"""
import math
import time

try:
    import numpy as np
except ImportError:  # the pure-Python parts still run
    np = None


# ------------------------------------------------------------------ nets
def grid_net(n, spacing=1.0):
    """An n x n node grid in plan, z = 0, edges along rows and columns; boundary nodes fixed."""
    xyz, idx = [], {}
    for j in range(n):
        for i in range(n):
            idx[(i, j)] = len(xyz)
            xyz.append([i * spacing, j * spacing, 0.0])
    edges = []
    for j in range(n):
        for i in range(n):
            if i + 1 < n:
                edges.append((idx[(i, j)], idx[(i + 1, j)]))
            if j + 1 < n:
                edges.append((idx[(i, j)], idx[(i, j + 1)]))
    fixed = [idx[(i, j)] for j in range(n) for i in range(n) if i in (0, n - 1) or j in (0, n - 1)]
    return xyz, edges, fixed, idx


def star_net():
    """Example (a): one free node joined to the four corners of a 2 x 2 square at z = 0."""
    xyz = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0], [0.7, 1.6, 3.0]]
    edges = [(4, 0), (4, 1), (4, 2), (4, 3)]
    fixed = [0, 1, 2, 3]
    return xyz, edges, fixed


# ------------------------------------------------------------------ FDM, pure Python
def fdm_pure(xyz, edges, fixed, q, loads):
    """Assemble D = Ci^T Q Ci and the right-hand side directly from the edges (no C matrix),
    then solve by Gaussian elimination with partial pivoting. This is what an ES5 port does."""
    n = len(xyz)
    fixed_set = set(fixed)
    free = [i for i in range(n) if i not in fixed_set]
    pos = {v: k for k, v in enumerate(free)}
    m = len(free)
    D = [[0.0] * m for _ in range(m)]
    B = [[loads[v][a] for a in range(3)] for v in free]
    for e, (i, j) in enumerate(edges):
        qe = q[e]
        for a_, b_ in ((i, j), (j, i)):
            if a_ in pos:
                ra = pos[a_]
                D[ra][ra] += qe
                if b_ in pos:
                    D[ra][pos[b_]] -= qe
                else:  # the fixed end moves to the right-hand side
                    for ax in range(3):
                        B[ra][ax] += qe * xyz[b_][ax]
    X = gauss_solve(D, B)
    out = [list(p) for p in xyz]
    for k, v in enumerate(free):
        out[v] = X[k]
    return out


def gauss_solve(A, B):
    m = len(A)
    A = [row[:] for row in A]
    B = [row[:] for row in B]
    for c in range(m):
        p = max(range(c, m), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-12:
            raise ValueError("singular: a free node has no path to a support, or q sums to zero")
        A[c], A[p] = A[p], A[c]
        B[c], B[p] = B[p], B[c]
        for r in range(c + 1, m):
            f = A[r][c] / A[c][c]
            if f:
                for k in range(c, m):
                    A[r][k] -= f * A[c][k]
                for k in range(3):
                    B[r][k] -= f * B[c][k]
    X = [[0.0] * 3 for _ in range(m)]
    for r in range(m - 1, -1, -1):
        for k in range(3):
            s = B[r][k] - sum(A[r][j] * X[j][k] for j in range(r + 1, m))
            X[r][k] = s / A[r][r]
    return X


# ------------------------------------------------------------------ FDM, numpy (the matrix form)
def fdm_numpy(xyz, edges, fixed, q, loads):
    n = len(xyz)
    free = [i for i in range(n) if i not in set(fixed)]
    C = np.zeros((len(edges), n))
    for e, (i, j) in enumerate(edges):
        C[e, i] = 1.0
        C[e, j] = -1.0
    Ci, Cf = C[:, free], C[:, fixed]
    Q = np.diag(q)
    X = np.array(xyz, float)
    P = np.array(loads, float)
    D = Ci.T @ Q @ Ci
    rhs = P[free] - Ci.T @ Q @ Cf @ X[fixed]
    X[free] = np.linalg.solve(D, rhs)
    residual = P - C.T @ Q @ C @ X  # zero at free nodes; reactions (negated) at fixed nodes
    return X, residual, D


# ------------------------------------------------------------------ DR
def dr(xyz, edges, fixed, loads, k, rest, dt=1.0, lam=1.0, damping="kinetic", c=0.1,
       tol=1e-9, kmax=200000, correct=True):
    """Dynamic relaxation with linear springs (stiffness k, rest length rest).
    Residual R_i = p_i + sum_j T_ij/L_ij (x_j - x_i), T = k (L - rest).
    Leapfrog (Day 1965; Barnes): v(t+dt/2) = A v(t-dt/2) + B dt R(t)/M ; x(t+dt) = x(t) + dt v(t+dt/2).
    Fictitious masses M_i = lam * dt^2/2 * S_i, S_i the sum of the axial stiffnesses at node i
    (k for a zero-rest-length spring; Barnes's bound, lam >= 1).
    kinetic: A = B = 1, and at a kinetic-energy peak the nodes are moved back to
      x* = x(t+dt) - 1.5 dt v(t+dt/2) + dt^2/2 R(t)/M   (the position at t - dt/2, see the note)
      and every velocity is reset; the restart uses v(dt/2) = dt/2 R/M.
    viscous: A = (1 - c/2)/(1 + c/2), B = (1 + A)/2 (compas 1.x's Coeff class)."""
    n = len(xyz)
    fixed_set = set(fixed)
    free = [i for i in range(n) if i not in fixed_set]
    X = [list(p) for p in xyz]
    nbr = [[] for _ in range(n)]
    for e, (i, j) in enumerate(edges):
        nbr[i].append((j, e))
        nbr[j].append((i, e))
    S = [sum(k[e] for _, e in nbr[i]) for i in range(n)]
    M = [lam * dt * dt / 2.0 * s if s else 1.0 for s in S]

    def resid(X):
        R = [[loads[i][a] for a in range(3)] for i in range(n)]
        for e, (i, j) in enumerate(edges):
            d = [X[j][a] - X[i][a] for a in range(3)]
            L = math.sqrt(sum(t * t for t in d))
            fd = k[e] * (L - rest[e]) / L if L > 0 else k[e]  # force density T/L
            for a in range(3):
                R[i][a] += fd * d[a]
                R[j][a] -= fd * d[a]
        return R

    if damping == "viscous":
        A = (1 - c * 0.5) / (1 + c * 0.5)
        Bc = 0.5 * (1 + A)
    else:
        A, Bc = 1.0, 1.0
    V = [[0.0] * 3 for _ in range(n)]
    R = resid(X)
    ke_prev = 0.0
    peaks = 0
    for it in range(1, kmax + 1):
        Rt = R
        first = all(V[i][0] == 0 and V[i][1] == 0 and V[i][2] == 0 for i in free)
        for i in free:
            for a in range(3):
                if damping == "kinetic" and first:
                    V[i][a] = 0.5 * dt * Rt[i][a] / M[i]
                else:
                    V[i][a] = A * V[i][a] + Bc * dt * Rt[i][a] / M[i]
                X[i][a] += dt * V[i][a]
        ke = sum(0.5 * M[i] * sum(v * v for v in V[i]) for i in free)
        if damping == "kinetic" and ke < ke_prev:
            peaks += 1
            for i in free:
                if correct:
                    for a in range(3):
                        X[i][a] = X[i][a] - 1.5 * dt * V[i][a] + dt * dt / 2.0 * Rt[i][a] / M[i]
                V[i] = [0.0, 0.0, 0.0]
            ke = 0.0
        ke_prev = ke
        R = resid(X)
        rmax = max(math.sqrt(sum(r * r for r in R[i])) for i in free)
        if rmax < tol:
            return X, it, peaks, rmax
    return X, kmax, peaks, rmax


def maxdiff(A, B):
    return max(abs(A[i][a] - B[i][a]) for i in range(len(A)) for a in range(3))


def main():
    print("=== (a) one free node, four corners of a 2 x 2 square, q = 1, p = (0, 0, -1)")
    xyz, edges, fixed = star_net()
    loads = [[0, 0, 0]] * 4 + [[0.0, 0.0, -1.0]]
    for q in (1.0, 2.0, -1.0):
        out = fdm_pure(xyz, edges, fixed, [q] * 4, loads)
        closed = [1.0, 1.0, -1.0 / (4 * q)]  # x = mean of the corners + p / sum(q)
        print("q = %5.2f  FDM %s   closed form %s" % (q, [round(v, 12) for v in out[4]], closed))
        assert maxdiff([out[4]], [closed]) < 1e-12
    L = math.sqrt(1 + 1 + 0.0625)
    print("edge length %.6f, force q*L %.6f; vertical equilibrium 4*q*L*(0.25/L) = %.6f" % (L, L, 4 * 0.25))
    print("initial position (0.7, 1.6, 3.0) is irrelevant: the system is linear (checked).")

    print("\n=== (b) 5 x 5 net, spacing 1 m, boundary fixed at z = 0, 9 free nodes, q = 1, p = -1 kN each")
    xyz, edges, fixed, idx = grid_net(5)
    loads = [[0.0, 0.0, -1.0 if i not in set(fixed) else 0.0] for i in range(len(xyz))]
    q = [1.0] * len(edges)
    out = fdm_pure(xyz, edges, fixed, q, loads)
    if np is not None:
        X, res, D = fdm_numpy(xyz, edges, fixed, q, loads)
        print("numpy vs pure Python max |diff| = %.3e" % maxdiff(out, X.tolist()))
        free = [i for i in range(len(xyz)) if i not in set(fixed)]
        print("max |residual| at free nodes = %.3e" % np.abs(res[free]).max())
        print("sum of the vertical reactions = %.6f (load total 9)" % (-res[fixed, 2].sum()))
        ev = np.linalg.eigvalsh(D)
        print("D eigenvalues min %.4f max %.4f (positive definite for q > 0)" % (ev.min(), ev.max()))
    for name, (i, j) in (("centre (2,2)", (2, 2)), ("edge-mid (2,1)", (2, 1)), ("corner (1,1)", (1, 1))):
        print("%-15s xyz = (%.6f, %.6f, %.9f)" % (name, *out[idx[(i, j)]]))
    # exact fractions: z_c = -11/16? derive check by symmetry solve below
    zc, ze, zk = out[idx[(2, 2)]][2], out[idx[(2, 1)]][2], out[idx[(1, 1)]][2]
    # symmetry: 3 unknowns. corner: 4zk - 2ze = -1 ; edge: 4ze - 2zk - zc = -1 ; centre: 4zc - 4ze = -1
    import fractions as F
    A3 = [[F.Fraction(4), F.Fraction(-2), F.Fraction(0)], [F.Fraction(-2), F.Fraction(4), F.Fraction(-1)],
          [F.Fraction(0), F.Fraction(-4), F.Fraction(4)]]
    b3 = [F.Fraction(-1)] * 3
    # tiny exact elimination
    for c_ in range(3):
        for r in range(c_ + 1, 3):
            f = A3[r][c_] / A3[c_][c_]
            A3[r] = [A3[r][k_] - f * A3[c_][k_] for k_ in range(3)]
            b3[r] -= f * b3[c_]
    s = [F.Fraction(0)] * 3
    for r in (2, 1, 0):
        s[r] = (b3[r] - sum(A3[r][k_] * s[k_] for k_ in range(r + 1, 3))) / A3[r][r]
    print("exact by symmetry: corner %s, edge-mid %s, centre %s" % (s[0], s[1], s[2]))
    assert abs(float(s[0]) - zk) < 1e-12 and abs(float(s[1]) - ze) < 1e-12 and abs(float(s[2]) - zc) < 1e-12
    # q scaling: z scales by 1/q
    out2 = fdm_pure(xyz, edges, fixed, [4.0] * len(edges), loads)
    print("q = 4: centre z = %.9f (= z(q=1)/4: %s)" % (out2[idx[(2, 2)]][2], abs(out2[idx[(2, 2)]][2] - zc / 4) < 1e-12))
    # compression: q = -1 with the same downward load gives the mirror image (a funicular vault)
    out3 = fdm_pure(xyz, edges, fixed, [-1.0] * len(edges), loads)
    print("q = -1: centre z = %+.9f (mirror of the hanging net)" % out3[idx[(2, 2)]][2])
    # member forces for the frame solver hand-over
    f = []
    for e, (i, j) in enumerate(edges):
        L = math.dist(out[i], out[j])
        f.append(q[e] * L)
    print("edge forces q*L: min %.6f kN, max %.6f kN (all tension)" % (min(f), max(f)))
    # singular edge case
    try:
        fdm_pure([[0, 0, 0], [1, 0, 0], [2, 0, 0]], [(1, 2)], [0], [1.0], [[0, 0, 0], [0, 0, -1], [0, 0, -1]])
        print("disconnected: solved (unexpected)")
    except ValueError as ex:
        print("disconnected free nodes -> %s" % ex)

    print("\n=== (c) DR on the same net: zero rest length springs, k = q = 1, from the flat start")
    rest0 = [0.0] * len(edges)
    for damping, lam in (("kinetic", 1.0), ("kinetic", 1.5), ("viscous", 1.0), ("viscous", 1.5)):
        t0 = time.perf_counter()
        Xd, its, peaks, rmax = dr(xyz, edges, fixed, loads, q, rest0, lam=lam, damping=damping, c=0.1)
        ms = (time.perf_counter() - t0) * 1000
        print("%-8s lam %.1f: %6d iterations, %4d KE peaks, |R|max %.1e, max |x_DR - x_FDM| = %.2e (%.0f ms)"
              % (damping, lam, its, peaks, rmax, maxdiff(Xd, out), ms))
    Xd, its, peaks, rmax = dr(xyz, edges, fixed, loads, q, rest0, lam=1.0, damping="kinetic", correct=False)
    print("kinetic lam 1.0 without the peak correction: %d iterations, %d peaks" % (its, peaks))
    # DR at the stability bound with lam < 1 diverges
    Xd, its, peaks, rmax = dr(xyz, edges, fixed, loads, q, rest0, lam=0.45, damping="kinetic", kmax=2000)
    print("kinetic lam 0.45: after %d iterations |R|max = %.3e (unstable below the bound)" % (its, rmax))
    # where the true bound is: undamped leapfrog is stable while dt^2 * eig_max(M^-1 K) <= 4,
    # i.e. lam >= eig_max(D) / (2 * S) = 6.8284 / 8 = 0.8536 here; Barnes's lam = 1 is the Gershgorin bound
    for lam in (0.86, 0.85):
        Xd, its, peaks, rmax = dr(xyz, edges, fixed, loads, q, rest0, lam=lam, damping="viscous", c=0.0, kmax=5000)
        print("undamped lam %.2f: after %d iterations |R|max = %.3e" % (lam, its, rmax))
    # counter-check: a positive rest length breaks the equivalence
    Xd, its, peaks, rmax = dr(xyz, edges, fixed, loads, q, [0.5] * len(edges), lam=1.5, damping="kinetic")
    print("rest length 0.5: centre z = %.6f vs FDM %.6f (differs: q_eff = k(1 - L0/L) varies by edge)"
          % (Xd[idx[(2, 2)]][2], zc))
    if np is not None:
        # the converged DR net is an FDM equilibrium with its own q_eff: check it
        qeff = []
        for e, (i, j) in enumerate(edges):
            L = math.dist(Xd[i], Xd[j])
            qeff.append(1.0 * (L - 0.5) / L)
        Xq, _, _ = fdm_numpy(xyz, edges, fixed, qeff, loads)
        print("FDM with those q_eff reproduces the DR net: max |diff| = %.2e" % maxdiff(Xq.tolist(), Xd))


if __name__ == "__main__":
    main()
