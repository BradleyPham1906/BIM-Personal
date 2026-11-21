"""Seismic and structural-dynamics worked examples for the research note
docs/research/research-physical-world/seismic-dynamics.md (2026-11-21).

Data, not a test suite. Run from the repository root:
    python3 docs/research/experiments/physical-world/seismic.py
Needs numpy only. Reads the saved USGS response usgs-asce7-22-la-siteC-rcII.json beside it.

(a) ASCE/SEI 7-22 ELF for a 4-storey steel special moment frame at lat 34, lon -118,
    Site Class C, Risk Category II (USGS values), Method 2 and Method 1.
(b) A 2-dof shear building: closed-form periods, mode shapes, participation factors,
    effective modal masses; a plain Jacobi generalized eigensolver (Bathe) checked against
    numpy; SRSS and CQC; Rayleigh damping.
(c) Newmark average acceleration (gamma 1/2, beta 1/4) for an SDOF: forced half-sine
    (Chopra's example parameters) and free vibration, against the exact solutions; and MDOF
    Newmark with Rayleigh damping against modal superposition.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FT = 0.3048  # m per ft, exact
G = 9.80665


def line(t=''):
    print(t)


# ------------------------------------------------------------------ (a) ELF
def interp_spectrum(periods, ords, T):
    """ASCE 7-22 11.4.5.1: linear interpolation below 10 s; beyond 10 s, Sa(10)*10/T up to TL,
    Sa(10)*10*TL/T^2 beyond TL (TL passed separately)."""
    if T <= periods[0]:
        return ords[0]
    for i in range(1, len(periods)):
        if T <= periods[i]:
            t0, t1 = periods[i - 1], periods[i]
            return ords[i - 1] + (ords[i] - ords[i - 1]) * (T - t0) / (t1 - t0)
    raise ValueError('T beyond 10 s: use the 10/T or 10TL/T^2 tail')


def sds_sd1_from_multiperiod(periods, sa, vs_gt_442):
    """ASCE 7-22 21.4 (as NEHRP 2020 Part 1 gives it): SDS = 0.9 max Sa over 0.2..5 s;
    SD1 = 0.9 max T*Sa over 1..2 s (vs > 442 m/s) or 1..5 s (vs <= 442 m/s), not less than Sa(1)."""
    sds = 0.9 * max(s for t, s in zip(periods, sa) if 0.2 - 1e-9 <= t <= 5 + 1e-9)
    hi = 2.0 if vs_gt_442 else 5.0
    tsa = max(t * s for t, s in zip(periods, sa) if 1 - 1e-9 <= t <= hi + 1e-9)
    sa1 = interp_spectrum(periods, sa, 1.0)
    sd1 = max(0.9 * tsa, sa1)
    return sds, sd1


def cu_of_sd1(sd1):
    """Table 12.8-1 (unchanged 7-16 to 7-22 per the sources in the note); linear between rows."""
    rows = [(0.1, 1.7), (0.15, 1.6), (0.2, 1.5), (0.3, 1.4), (0.4, 1.4)]
    if sd1 >= 0.4:
        return 1.4
    if sd1 <= 0.1:
        return 1.7
    for (a, ca), (b, cb) in zip(rows, rows[1:]):
        if a <= sd1 <= b:
            return ca + (cb - ca) * (sd1 - a) / (b - a)


def k_exp(T):
    """12.8.3: k = 1 for T <= 0.5, 2 for T >= 2.5, linear between."""
    if T <= 0.5:
        return 1.0
    if T >= 2.5:
        return 2.0
    return 1.0 + (T - 0.5) / 2.0


def cs_method2(sds, sd1, s1, T, TL, R, Ie):
    base = sds / (R / Ie)
    upper = sd1 / (T * (R / Ie)) if T <= TL else sd1 * TL / (T * T * (R / Ie))
    cs = min(base, upper)
    low1 = max(0.044 * sds * Ie, 0.01)
    low2 = 0.5 * s1 / (R / Ie) if s1 >= 0.6 else 0.0
    return max(cs, low1, low2), dict(base=base, upper=upper, low1=low1, low2=low2)


def example_a():
    line('=' * 72)
    line('(a) ELF, 4-storey steel SMF, lat 34 lon -118, Site Class C, Risk Category II')
    d = json.load(open(os.path.join(HERE, 'usgs-asce7-22-la-siteC-rcII.json')))['response']['data']
    sds, sd1, s1, ss, TL = d['sds'], d['sd1'], d['s1'], d['ss'], d['tl']
    line(f"USGS: SS={ss} S1={s1} SDS={sds} SD1={sd1} TL={TL} TS={d['ts']} T0={d['t0']} SDC={d['sdc']}")
    mp = d['multiPeriodDesignSpectrum']
    sds_c, sd1_c = sds_sd1_from_multiperiod(mp['periods'], mp['ordinates'], vs_gt_442=True)
    line(f'21.4 recomputed from the multi-period design spectrum: SDS={sds_c:.3f} (USGS {sds}), '
         f'SD1={sd1_c:.3f} (USGS {sd1})')
    assert abs(sds_c - sds) < 0.006 and abs(sd1_c - sd1) < 0.006
    assert abs(d['ts'] - sd1 / sds) < 0.001 and abs(d['t0'] - 0.2 * sd1 / sds) < 0.001
    # two-period spectrum ordinate at T=0 is 0.4 SDS
    tp = d['twoPeriodDesignSpectrum']
    line(f"two-period spectrum Sa(0)={tp['ordinates'][0]} vs 0.4*SDS={0.4 * sds:.3f}")

    R, Cd, Om, Ie = 8.0, 5.5, 3.0, 1.0
    n, hs, w = 4, 3.5, 2000.0
    hx = [hs * (i + 1) for i in range(n)]
    hn = hx[-1]
    Ct_ft, x = 0.028, 0.8
    Ct_si = Ct_ft * (1 / FT) ** x
    Ta = Ct_ft * (hn / FT) ** x
    Ta_si = Ct_si * hn ** x
    assert abs(Ta - Ta_si) < 1e-12
    Cu = cu_of_sd1(sd1)
    line(f'hn={hn} m = {hn / FT:.3f} ft; Ct={Ct_ft} (ft) = {Ct_si:.4f} (m); Ta={Ta:.4f} s; '
         f'Cu={Cu}; CuTa={Cu * Ta:.4f} s')
    for name, ctf, xx in [('steel MRF', 0.028, 0.8), ('concrete MRF', 0.016, 0.9),
                          ('steel EBF/BRBF', 0.030, 0.75), ('all other', 0.020, 0.75)]:
        line(f'   SI Ct {name}: {ctf} * 3.28084^{xx} = {ctf * (1 / FT) ** xx:.4f}')
    T = Ta  # no computed period: T = Ta (12.8.2)
    cs, parts = cs_method2(sds, sd1, s1, T, TL, R, Ie)
    line('Method 2: SDS/(R/Ie)={base:.4f}; SD1/(T R/Ie)={upper:.4f}; 0.044SDS Ie>=0.01 -> {low1:.4f}; '
         '0.5S1/(R/Ie) (S1>=0.6) -> {low2:.4f}'.format(**parts))
    W = n * w
    V = cs * W
    line(f'Cs={cs:.4f}  W={W:.0f} kN  V={V:.1f} kN')
    sa_T = interp_spectrum(mp['periods'], mp['ordinates'], T)
    t_peak = mp['periods'][int(np.argmax(mp['ordinates']))]
    sa_m1 = max(mp['ordinates']) if T < t_peak else sa_T
    cs1 = max(sa_m1 / (R / Ie), parts['low1'], parts['low2'])
    line(f'Method 1: Sa(T={T:.3f})={sa_T:.4f} g (peak at {t_peak} s), Cs={cs1:.4f}, V={cs1 * W:.1f} kN')
    k = k_exp(T)
    wh = [w * h ** k for h in hx]
    sw = sum(wh)
    F = [V * a / sw for a in wh]
    line(f'k={k:.4f}')
    Vx = 0.0
    for i in reversed(range(n)):
        Vx += F[i]
        line(f'  level {i + 1}: hx={hx[i]:.1f} m  wx h^k={wh[i]:.1f}  Cvx={wh[i] / sw:.4f}  '
             f'Fx={F[i]:.1f} kN  storey shear={Vx:.1f} kN')
    assert abs(sum(F) - V) < 1e-9

    # drift with an assumed storey stiffness (a shear building), computed period uncapped (12.8.6.2)
    kst = 200000.0  # kN/m per storey, ASSUMED for the example
    m = w / G      # t per level
    K = np.zeros((n, n))
    for i in range(n):
        K[i, i] += kst
        if i + 1 < n:
            K[i, i] += kst
            K[i, i + 1] -= kst
            K[i + 1, i] -= kst
    M = np.eye(n) * m
    lam, phi = np.linalg.eigh(np.linalg.solve(np.sqrt(M), np.linalg.solve(np.sqrt(M), K).T).T)
    T1 = 2 * math.pi / math.sqrt(lam[0])
    line(f'drift model: storey k={kst:.0f} kN/m (assumed), m={m:.2f} t/level, computed T1={T1:.4f} s '
         f'(below CuTa={Cu * Ta:.3f} s; V above used T=Ta; 12.8.6.2 lets drift use the computed T uncapped)')
    # elastic displacements under the ELF forces (strength level), then Cd/Ie
    de = np.linalg.solve(K, np.array(F))
    rho = 1.3  # redundancy factor assumed 1.3 in SDC D for the moment-frame limit
    lim = 0.020
    prev = 0.0
    for i in range(n):
        dxe = de[i] - prev
        prev = de[i]
        D = Cd * dxe / Ie
        line(f'  storey {i + 1}: delta_xe={dxe * 1000:.3f} mm  Delta=Cd*dxe/Ie={D * 1000:.2f} mm  '
             f'ratio={D / hs:.5f}  limit 0.020hsx={lim * hs * 1000:.0f} mm, /rho(1.3)={lim * hs / rho * 1000:.1f} mm')
    return dict(Ta=Ta, Cs=cs, V=V, k=k, F=F)


# ------------------------------------------------------------------ (b) eigen
def jacobi_general(K, M, sweeps=50, tol=1e-12):
    """Generalized Jacobi (Bathe, FEP 1982 / 2014, section 11.3.3), as Frame3DD's eig.c does:
    rotate pairs until K and M are both diagonal. Returns eigenvalues ascending and
    M-orthonormal vectors. Plain loops: what a small ES5 port would do."""
    n = K.shape[0]
    A, B = K.astype(float).copy(), M.astype(float).copy()
    V = np.eye(n)
    for sweep in range(sweeps):
        off = 0.0
        for i in range(n - 1):
            for j in range(i + 1, n):
                ck = A[i, j] ** 2 / (A[i, i] * A[j, j])
                cm = B[i, j] ** 2 / (B[i, i] * B[j, j])
                off = max(off, ck, cm)
                if ck < tol and cm < tol:
                    continue
                kbi = A[i, i] * B[i, j] - B[i, i] * A[i, j]
                kbj = A[j, j] * B[i, j] - B[j, j] * A[i, j]
                kb = A[i, i] * B[j, j] - A[j, j] * B[i, i]
                det = kb * kb / 4 + kbi * kbj
                s = math.sqrt(max(det, 0.0))
                d1 = kb / 2 + (s if kb >= 0 else -s)
                if d1 == 0:
                    alpha, gamma = 0.0, -A[i, j] / A[j, j]
                else:
                    alpha, gamma = kbj / d1, -kbi / d1
                P = np.eye(n)
                P[i, j] = alpha
                P[j, i] = gamma
                A = P.T @ A @ P
                B = P.T @ B @ P
                V = V @ P
        if off < tol:
            break
    lam = np.diag(A) / np.diag(B)
    V = V / np.sqrt(np.diag(B))
    idx = np.argsort(lam)
    return lam[idx], V[:, idx], sweep + 1


def cqc_rho(zi, zj, r):
    """Der Kiureghian (1981) cross-modal coefficient, r = wj/wi (frequency ratio, not w^2)."""
    num = 8 * math.sqrt(zi * zj) * (zi + r * zj) * r ** 1.5
    den = (1 - r * r) ** 2 + 4 * zi * zj * r * (1 + r * r) + 4 * (zi * zi + zj * zj) * r * r
    return num / den


def example_b():
    line('=' * 72)
    line('(b) 2-dof shear building: m1=m2=m, k1=k2=k')
    m, k = 100.0, 40000.0  # t, kN/m
    M = np.diag([m, m])
    K = np.array([[2 * k, -k], [-k, k]])
    w2_exact = [(3 - math.sqrt(5)) / 2 * k / m, (3 + math.sqrt(5)) / 2 * k / m]
    T_exact = [2 * math.pi / math.sqrt(v) for v in w2_exact]
    phi_exact = [np.array([1.0, (1 + math.sqrt(5)) / 2]), np.array([1.0, (1 - math.sqrt(5)) / 2])]
    lam, V, sweeps = jacobi_general(K, M)
    line(f'closed form w^2 = (3 -/+ sqrt5)/2 k/m = {w2_exact[0]:.4f}, {w2_exact[1]:.4f} rad^2/s^2; '
         f'T = {T_exact[0]:.5f}, {T_exact[1]:.5f} s')
    line(f'Jacobi ({sweeps} sweeps): {lam[0]:.4f}, {lam[1]:.4f}')
    assert np.allclose(lam, w2_exact, rtol=1e-10)
    iota = np.ones(2)
    Mt = iota @ M @ iota
    cum = 0.0
    for nmode in range(2):
        ph = phi_exact[nmode]
        Ln = ph @ M @ iota
        Mn = ph @ M @ ph
        G_ = Ln / Mn
        Meff = Ln * Ln / Mn
        cum += Meff / Mt
        v = V[:, nmode] / V[0, nmode]
        assert np.allclose(v, ph, rtol=1e-9)
        line(f'mode {nmode + 1}: phi={ph.round(5)}  Gamma={G_:.5f}  M*={Meff:.4f} t = {Meff / Mt * 100:.3f}%  '
             f'cumulative {cum * 100:.3f}%')
    line(f'closed form: M1*/M = 1/2 + 1/sqrt5 = {0.5 + 1 / math.sqrt(5):.6f}; '
         f'M2*/M = 1/2 - 1/sqrt5 = {0.5 - 1 / math.sqrt(5):.6f}')

    # bigger check: 10-storey shear building, Jacobi vs numpy
    n = 10
    Kb = np.zeros((n, n))
    for i in range(n):
        Kb[i, i] = 2 * k if i < n - 1 else k
        if i + 1 < n:
            Kb[i, i + 1] = Kb[i + 1, i] = -k
    Mb = np.diag(np.linspace(120, 80, n))
    lj, Vj, sw = jacobi_general(Kb, Mb)
    ln = np.sort(np.linalg.eigvals(np.linalg.solve(Mb, Kb)).real)
    line(f'10-dof: Jacobi {sw} sweeps, max rel. eigenvalue error vs numpy {np.max(np.abs(lj - ln) / ln):.2e}; '
         f'M-orthonormal check {np.max(np.abs(Vj.T @ Mb @ Vj - np.eye(n))):.1e}')

    # CQC coefficient checks
    z = 0.05
    line(f'CQC rho(r=1)={cqc_rho(z, z, 1.0):.6f}; rho(r=0.9)={cqc_rho(z, z, 0.9):.4f}; '
         f'rho(r=0.5)={cqc_rho(z, z, 0.5):.5f}; rho(r=T2/T1=0.382, this 2-dof)={cqc_rho(z, z, T_exact[1] / T_exact[0]):.5f}')
    eq = lambda r: 8 * z * z * (1 + r) * r ** 1.5 / ((1 - r * r) ** 2 + 4 * z * z * r * (1 + r) ** 2)
    for r in (0.3, 0.7, 0.95, 1.2):
        assert abs(cqc_rho(z, z, r) - eq(r)) < 1e-12
        assert abs(cqc_rho(0.03, 0.07, r) - cqc_rho(0.07, 0.03, 1 / r)) < 1e-12
    # the OpenSeesPy example passes eigenvalues (w^2) as "lambdas": the ratio is then r^2
    r = math.sqrt(w2_exact[0] / w2_exact[1])
    line(f'rho with r=w1/w2={r:.4f}: {cqc_rho(z, z, r):.5f}; with r=w1^2/w2^2={r * r:.4f}: {cqc_rho(z, z, r * r):.6f}')

    # Rayleigh damping, 5% in modes 1 and 2
    w1, w2 = math.sqrt(w2_exact[0]), math.sqrt(w2_exact[1])
    a0 = z * 2 * w1 * w2 / (w1 + w2)
    a1 = z * 2 / (w1 + w2)
    for wv in (w1, w2):
        assert abs(a0 / (2 * wv) + a1 * wv / 2 - z) < 1e-12
    line(f'Rayleigh: a0={a0:.5f} 1/s, a1={a1:.6f} s (zeta=5% at w1={w1:.4f}, w2={w2:.4f} rad/s)')
    return dict(M=M, K=K, a0=a0, a1=a1, w=(w1, w2), phi=phi_exact)


# ------------------------------------------------------------------ (c) Newmark
def newmark_sdof(m, c, k, p, dt, u0=0.0, v0=0.0, gamma=0.5, beta=0.25):
    """Chopra, Dynamics of Structures, Table 5.4.2 (linear systems), incremental form."""
    a0 = (p[0] - c * v0 - k * u0) / m
    a1 = m / (beta * dt) + gamma / beta * c
    a2 = m / (2 * beta) + dt * (gamma / (2 * beta) - 1) * c
    kh = k + gamma / (beta * dt) * c + m / (beta * dt * dt)
    u, v, a = [u0], [v0], [a0]
    for i in range(len(p) - 1):
        dp = p[i + 1] - p[i] + a1 * v[i] + a2 * a[i]
        du = dp / kh
        dv = gamma / (beta * dt) * du - gamma / beta * v[i] + dt * (1 - gamma / (2 * beta)) * a[i]
        da = du / (beta * dt * dt) - v[i] / (beta * dt) - a[i] / (2 * beta)
        u.append(u[i] + du)
        v.append(v[i] + dv)
        a.append(a[i] + da)
    return np.array(u), np.array(v), np.array(a)


def exact_halfsine(m, k, z, p0, Om, td, t):
    wn = math.sqrt(k / m)
    wd = wn * math.sqrt(1 - z * z)
    r = Om / wn
    den = (1 - r * r) ** 2 + (2 * z * r) ** 2
    C = p0 / k * (1 - r * r) / den
    D = p0 / k * (-2 * z * r) / den
    A = -D
    B = (z * wn * A - C * Om) / wd

    def forced(tt):
        e = math.exp(-z * wn * tt)
        u = e * (A * math.cos(wd * tt) + B * math.sin(wd * tt)) + C * math.sin(Om * tt) + D * math.cos(Om * tt)
        du = (-z * wn * e * (A * math.cos(wd * tt) + B * math.sin(wd * tt))
              + e * (-A * wd * math.sin(wd * tt) + B * wd * math.cos(wd * tt))
              + C * Om * math.cos(Om * tt) - D * Om * math.sin(Om * tt))
        return u, du
    u1, v1 = forced(td)
    out = []
    for tt in t:
        if tt <= td + 1e-12:
            out.append(forced(tt)[0])
        else:
            s = tt - td
            out.append(math.exp(-z * wn * s) * (u1 * math.cos(wd * s) + (v1 + z * wn * u1) / wd * math.sin(wd * s)))
    return np.array(out)


def example_c(bres):
    line('=' * 72)
    line('(c) Newmark average acceleration, SDOF: m=0.2533 kip-s2/in, k=10 kip/in, zeta=0.05 (Tn=1.0 s)')
    m, k, z = 0.2533, 10.0, 0.05
    wn = math.sqrt(k / m)
    c = 2 * z * m * wn
    dt, td, p0 = 0.1, 0.6, 10.0
    t = np.arange(0, 1.0 + 1e-9, dt)
    p = np.where(t <= td + 1e-9, p0 * np.sin(math.pi * t / td), 0.0)
    u, v, a = newmark_sdof(m, c, k, p, dt)
    ue = exact_halfsine(m, k, z, p0, math.pi / td, td, t)
    line(' t     Newmark u (in)   exact u (in)')
    for ti, ui, uei in zip(t, u, ue):
        line(f' {ti:.1f}   {ui:9.4f}        {uei:9.4f}')
    # free vibration, undamped: period elongation of average acceleration
    for ratio in (0.05, 0.1):
        T = 1.0
        dtf = ratio * T
        nstep = int(round(20 * T / dtf))
        uf, _, _ = newmark_sdof(1.0, 0.0, (2 * math.pi) ** 2, np.zeros(nstep + 1), dtf, u0=1.0)
        amp = np.max(np.abs(uf[-int(2 / ratio):]))
        # period from zero crossings
        zc = [i for i in range(1, len(uf)) if uf[i - 1] > 0 >= uf[i]]
        tz = [((i - 1) + uf[i - 1] / (uf[i - 1] - uf[i])) * dtf for i in zc]
        Tnum = (tz[-1] - tz[0]) / (len(tz) - 1)
        wdt = 2 * math.pi * ratio
        Tth = 2 * math.pi * dtf / (2 * math.atan(wdt / 2))  # exact for average acceleration, undamped
        line(f'free vibration dt/T={ratio}: amplitude after 20 T = {amp:.6f} (no decay); '
             f'period {Tnum:.5f} s, theory {Tth:.5f} s, elongation {(Tnum - 1) * 100:.3f}% '
             f'(approx (w dt)^2/12 = pi^2/3 (dt/T)^2 = {math.pi ** 2 / 3 * ratio ** 2 * 100:.3f}%)')

    line('MDOF Newmark (2-dof of (b), Rayleigh 5%) vs modal superposition, ground pulse')
    M, K = bres['M'], bres['K']
    a0r, a1r = bres['a0'], bres['a1']
    C = a0r * M + a1r * K
    dt2 = 0.005
    tt = np.arange(0, 3.0 + 1e-9, dt2)
    ag = np.where(tt <= 0.5, 0.3 * G * np.sin(math.pi * tt / 0.5), 0.0)
    iota = np.ones(2)
    P = -np.outer(ag, M @ iota)
    # MDOF Newmark (matrix form of Table 5.4.2, Chopra Table 16.3.3)
    gm, bt = 0.5, 0.25
    U = np.zeros((len(tt), 2))
    Vv = np.zeros_like(U)
    A = np.zeros_like(U)
    A[0] = np.linalg.solve(M, P[0] - C @ Vv[0] - K @ U[0])
    Kh = K + gm / (bt * dt2) * C + M / (bt * dt2 ** 2)
    A1 = M / (bt * dt2) + gm / bt * C
    A2 = M / (2 * bt) + dt2 * (gm / (2 * bt) - 1) * C
    for i in range(len(tt) - 1):
        dp = P[i + 1] - P[i] + A1 @ Vv[i] + A2 @ A[i]
        du = np.linalg.solve(Kh, dp)
        dv = gm / (bt * dt2) * du - gm / bt * Vv[i] + dt2 * (1 - gm / (2 * bt)) * A[i]
        da = du / (bt * dt2 ** 2) - Vv[i] / (bt * dt2) - A[i] / (2 * bt)
        U[i + 1], Vv[i + 1], A[i + 1] = U[i] + du, Vv[i] + dv, A[i] + da
    # modal superposition with the same Newmark per mode (Rayleigh is classical damping)
    Um = np.zeros_like(U)
    for nm, (wv, ph) in enumerate(zip(bres['w'], bres['phi'])):
        Mn = ph @ M @ ph
        Gm = ph @ M @ iota / Mn
        zn = a0r / (2 * wv) + a1r * wv / 2
        q, _, _ = newmark_sdof(1.0, 2 * zn * wv, wv * wv, -Gm * ag, dt2)
        Um += np.outer(q, ph)
    err = np.max(np.abs(U - Um)) / np.max(np.abs(U))
    line(f'  peak roof displacement {np.max(np.abs(U[:, 1])) * 1000:.3f} mm; max difference vs modal '
         f'superposition {err:.2e} (relative)')
    assert err < 1e-9


if __name__ == '__main__':
    example_a()
    b = example_b()
    example_c(b)
