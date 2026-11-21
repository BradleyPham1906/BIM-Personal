"""Member design checks and cracking: worked examples for the research note
docs/research/research-physical-world/member-checks-cracking.md (2026-11-21).

Data, not a suite. Pure Python 3, no dependencies. Run:  python3 -I member_checks.py
Every number the note quotes is printed here and checked by an assert, so the note and the
script cannot drift apart. Units: N, mm, MPa inside; kN and kN m printed.

Sources (levels as in the note): ACI 318-19 provisions read through secondary copies (S):
fr 19.2.3.1, Ec 19.2.2.1(b), Mcr 24.2.3.5, Ie Table 24.2.3.5 (Bischoff form, 2/3 Mcr), beta1
Table 22.2.2.4.3, phi Table 21.2.2, As,min 9.6.1.2, Vc Table 22.5.5.1 with lambda_s 22.5.5.1.3.
AISC 360-22 read through open implementations and secondary copies (S): E3, F2, G2.1, H1.1,
Table B4.1b. W10x49 properties: AISC Shapes Database v15/v16 values as copied in several
independent repositories (S, aisc.org refused).
"""
import math

IN = 25.4          # mm per inch
KSI = 6.894757     # MPa per ksi
PSI = KSI / 1000.0


def close(a, b, tol):
    assert abs(a - b) <= tol, (a, b, tol)


# --------------------------------------------------------------------------------------------
# (a) RC beam, ACI 318-19
# --------------------------------------------------------------------------------------------
def aci_beam(b=300.0, h=500.0, d=450.0, fc=30.0, As=942.0, fy=420.0, Es=200000.0, lam=1.0):
    r = {}
    r['Ec'] = 4700.0 * math.sqrt(fc)                 # 19.2.2.1(b), normal weight, MPa
    r['fr'] = 0.62 * lam * math.sqrt(fc)             # 19.2.3.1, MPa
    r['Ig'] = b * h ** 3 / 12.0                      # gross concrete, steel neglected
    r['yt'] = h / 2.0
    r['Mcr'] = r['fr'] * r['Ig'] / r['yt']           # 24.2.3.5, N mm
    n = Es / r['Ec']
    r['n'] = n
    # cracked, singly reinforced: b x^2 / 2 = n As (d - x)
    A, B, C = b / 2.0, n * As, -n * As * d
    x = (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)
    r['kd'] = x
    r['k'] = x / d
    r['Icr'] = b * x ** 3 / 3.0 + n * As * (d - x) ** 2
    # flexural strength
    if fc <= 28.0:
        beta1 = 0.85
    elif fc < 55.0:
        beta1 = 0.85 - 0.05 * (fc - 28.0) / 7.0
    else:
        beta1 = 0.65
    r['beta1'] = beta1
    a = As * fy / (0.85 * fc * b)
    c = a / beta1
    eps_t = 0.003 * (d - c) / c
    eps_ty = fy / Es
    if eps_t >= eps_ty + 0.003:
        phi = 0.90
    elif eps_t <= eps_ty:
        phi = 0.65
    else:
        phi = 0.65 + 0.25 * (eps_t - eps_ty) / 0.003
    r.update(a=a, c=c, eps_t=eps_t, phi=phi)
    r['Mn'] = As * fy * (d - a / 2.0)
    r['phiMn'] = phi * r['Mn']
    # minimum flexural steel, 9.6.1.2 (SI form)
    r['As_min'] = max(0.25 * math.sqrt(fc) / fy * b * d, 1.4 / fy * b * d)
    # one-way shear, Table 22.5.5.1 (SI coefficients; Nu = 0)
    rho_w = As / (b * d)
    lam_s = min(1.0, math.sqrt(2.0 / (1.0 + d / 250.0)))   # SI form, d in mm (d/10 in is d/254)
    r['rho_w'] = rho_w
    r['lam_s'] = lam_s
    vmax = 0.42 * lam * math.sqrt(fc) * b * d
    r['Vc_a'] = min(0.17 * lam * math.sqrt(fc) * b * d, vmax)
    r['Vc_b'] = min(0.66 * lam * rho_w ** (1.0 / 3.0) * math.sqrt(fc) * b * d, vmax)
    r['Vc_c'] = min(0.66 * lam_s * lam * rho_w ** (1.0 / 3.0) * math.sqrt(fc) * b * d, vmax)
    return r


def ie_bischoff(Ma, Mcr, Ig, Icr):
    """ACI 318-19 Table 24.2.3.5, nonprestressed."""
    if Ma <= 2.0 / 3.0 * Mcr:
        return Ig
    return Icr / (1.0 - (2.0 / 3.0 * Mcr / Ma) ** 2 * (1.0 - Icr / Ig))


def ie_branson(Ma, Mcr, Ig, Icr):
    """ACI 318-14 24.2.3.5a, for comparison only."""
    if Ma <= Mcr:
        return Ig
    q = (Mcr / Ma) ** 3
    return min(Ig, q * Ig + (1 - q) * Icr)


R = aci_beam()
print('(a) RC beam 300 x 500, d 450, fc 30, 3 bars 20 mm (942 mm2), fy 420')
print('  Ec   = %.1f MPa' % R['Ec'])
print('  fr   = %.4f MPa' % R['fr'])
print('  Ig   = %.4e mm4, yt = %.0f mm' % (R['Ig'], R['yt']))
print('  Mcr  = %.2f kN m' % (R['Mcr'] / 1e6))
print('  n    = %.4f' % R['n'])
print('  kd   = %.2f mm (k = %.4f)' % (R['kd'], R['k']))
print('  Icr  = %.4e mm4 (Icr/Ig = %.4f)' % (R['Icr'], R['Icr'] / R['Ig']))
print('  beta1= %.4f, a = %.2f mm, c = %.2f mm, eps_t = %.5f, phi = %.2f'
      % (R['beta1'], R['a'], R['c'], R['eps_t'], R['phi']))
print('  Mn   = %.2f kN m, phi Mn = %.2f kN m' % (R['Mn'] / 1e6, R['phiMn'] / 1e6))
print('  As,min = %.1f mm2' % R['As_min'])
print('  rho_w = %.5f, lambda_s = %.4f' % (R['rho_w'], R['lam_s']))
print('  Vc (a) = %.1f kN, (b) = %.1f kN, (c) = %.1f kN; phi 0.75 -> phi Vc(c) = %.1f kN'
      % (R['Vc_a'] / 1e3, R['Vc_b'] / 1e3, R['Vc_c'] / 1e3, 0.75 * R['Vc_c'] / 1e3))
for Ma_kNm in (20.0, 60.0, 120.0):
    Ma = Ma_kNm * 1e6
    ie = ie_bischoff(Ma, R['Mcr'], R['Ig'], R['Icr'])
    ib = ie_branson(Ma, R['Mcr'], R['Ig'], R['Icr'])
    print('  Ma = %5.1f kN m: Ie(318-19) = %.4e mm4 (Ie/Ig %.4f); Branson (318-14) %.4e (%.4f)'
          % (Ma_kNm, ie, ie / R['Ig'], ib, ib / R['Ig']))

close(R['Ec'], 25742.96, 0.1)
close(R['fr'], 3.3959, 1e-4)
close(R['Ig'], 3.125e9, 1)
close(R['Mcr'] / 1e6, 42.45, 0.01)
close(R['n'], 7.7692, 1e-3)
close(R['kd'], 125.77, 0.01)
close(R['Icr'] / 1e9, 0.9683, 1e-4)
close(R['phiMn'] / 1e6, 151.03, 0.01)
close(R['phi'], 0.90, 0)
close(R['As_min'], 450.0, 0.1)
close(ie_bischoff(60e6, R['Mcr'], R['Ig'], R['Icr']) / 1e9, 1.1439, 1e-4)
close(ie_bischoff(120e6, R['Mcr'], R['Ig'], R['Icr']) / 1e9, 1.0070, 1e-4)
close(R['Vc_c'] / 1e3, 78.8, 0.1)
assert ie_bischoff(20e6, R['Mcr'], R['Ig'], R['Icr']) == R['Ig']   # 20 < 2/3 Mcr = 28.3

# The same Mcr in inch-pound units (7.5 sqrt(psi)) to show the SI rounding is small
fc_psi = 30.0 / PSI
fr_us = 7.5 * math.sqrt(fc_psi) * PSI
print('  fr from 7.5 sqrt(psi) = %.4f MPa (vs 0.62 sqrt(MPa) %.4f): %.2f %% apart'
      % (fr_us, R['fr'], 100 * (fr_us / R['fr'] - 1)))
close(fr_us, 3.4108, 1e-3)
# Vc(c) in psi units with lambda_s = sqrt(2/(1+d/10)), d in inches
d_in = 450.0 / IN
vc_us = 8 * math.sqrt(2 / (1 + d_in / 10)) * R['rho_w'] ** (1 / 3.) * math.sqrt(fc_psi) * PSI * 300 * 450
print('  Vc(c) from the psi form = %.1f kN' % (vc_us / 1e3))

# What the app's Concrete card (E = 32 GPa) implies for fc if Ec = 4700 sqrt(fc)
print('  app Concrete E 32 GPa -> fc = %.1f MPa by 19.2.2.1(b)' % ((32000 / 4700.0) ** 2))
# Stiffness modifiers, Table 6.6.3.1.1(a)
print('  0.35 Ig (beam) = %.4e mm4; Icr/Ig here = %.3f' % (0.35 * R['Ig'], R['Icr'] / R['Ig']))

# --------------------------------------------------------------------------------------------
# (b) W10x49 (W250x73) column, AISC 360-22, L = 4 m, K = 1, Fy = 345 MPa, E = 200 000 MPa
# --------------------------------------------------------------------------------------------
W = dict(A=14.4, d=10.0, bf=10.0, tw=0.340, tf=0.560, Ix=272.0, Zx=60.4, Sx=54.6, rx=4.35,
         Iy=93.4, Zy=28.3, Sy=18.7, ry=2.54, J=1.39, Cw=2070.0, rts=2.84, ho=9.44,
         bf2tf=8.93, htw=23.1)  # AISC Shapes Database, inches


def mm(v, p):
    return v * IN ** p


E, Fy, L = 200000.0, 345.0, 4000.0
A = mm(W['A'], 2); rx = mm(W['rx'], 1); ry = mm(W['ry'], 1)
Zx = mm(W['Zx'], 3); Sx = mm(W['Sx'], 3); Zy = mm(W['Zy'], 3); Sy = mm(W['Sy'], 3)
J = mm(W['J'], 4); rts = mm(W['rts'], 1); ho = mm(W['ho'], 1)
dd = mm(W['d'], 1); tw = mm(W['tw'], 1)
print()
print('(b) W10x49 (W250x73), L = 4 m, K = 1, Fy 345 MPa, E 200 000 MPa')
print('  A = %.0f mm2, rx = %.1f mm, ry = %.1f mm, Zx = %.4e mm3, Sx = %.4e mm3'
      % (A, rx, ry, Zx, Sx))
# Table B4.1b compactness (flexure), Table B4.1a (compression)
lp_f = 0.38 * math.sqrt(E / Fy); lr_f = 1.0 * math.sqrt(E / Fy)
lp_w = 3.76 * math.sqrt(E / Fy); lr_w = 5.70 * math.sqrt(E / Fy)
lc_f = 0.56 * math.sqrt(E / Fy); lc_w = 1.49 * math.sqrt(E / Fy)
print('  flange bf/2tf = %.2f: compact <= %.2f, noncompact <= %.2f; compression nonslender <= %.2f'
      % (W['bf2tf'], lp_f, lr_f, lc_f))
print('  web h/tw = %.1f: compact <= %.1f, noncompact <= %.1f; compression nonslender <= %.1f'
      % (W['htw'], lp_w, lr_w, lc_w))
assert W['bf2tf'] <= lp_f and W['htw'] <= lp_w and W['bf2tf'] <= lc_f and W['htw'] <= lc_w
# E3, flexural buckling about the weak axis governs (rx > ry, same Lc)
slx, sly = L / rx, L / ry
sl = max(slx, sly)
Fe = math.pi ** 2 * E / sl ** 2
lim = 4.71 * math.sqrt(E / Fy)
Fn = (0.658 ** (Fy / Fe)) * Fy if sl <= lim else 0.877 * Fe
Pn = Fn * A
phiPn = 0.90 * Pn
print('  Lc/rx = %.1f, Lc/ry = %.1f; limit 4.71 sqrt(E/Fy) = %.1f' % (slx, sly, lim))
print('  Fe = %.1f MPa, Fy/Fe = %.4f, Fn = %.1f MPa, Pn = %.0f kN, phi Pn = %.0f kN'
      % (Fe, Fy / Fe, Fn, Pn / 1e3, phiPn / 1e3))
close(Fe, 513.5, 0.5)
close(Fn, 260.4, 0.3)
close(phiPn / 1e3, 2178, 1)
# F2, Lb = 4 m, Cb = 1.0 (conservative, uniform moment)
Lp = 1.76 * ry * math.sqrt(E / Fy)
c = 1.0
jc = J * c / (Sx * ho)
Lr = 1.95 * rts * E / (0.7 * Fy) * math.sqrt(jc + math.sqrt(jc ** 2 + 6.76 * (0.7 * Fy / E) ** 2))
Mp = Fy * Zx


def f2_mn(Lb, Cb):
    if Lb <= Lp:
        return Mp
    if Lb <= Lr:
        return min(Mp, Cb * (Mp - (Mp - 0.7 * Fy * Sx) * (Lb - Lp) / (Lr - Lp)))
    Fcr = Cb * math.pi ** 2 * E / (Lb / rts) ** 2 * math.sqrt(1 + 0.078 * jc * (Lb / rts) ** 2)
    return min(Mp, Fcr * Sx)


Mn1 = f2_mn(L, 1.0)
print('  Mp = %.1f kN m, Lp = %.0f mm, Lr = %.0f mm' % (Mp / 1e6, Lp, Lr))
print('  Lb = 4 m, Cb = 1.0: Mn = %.1f kN m, phi Mn = %.1f kN m' % (Mn1 / 1e6, 0.9 * Mn1 / 1e6))
print('  Lb = 4 m, Cb = 1.67 (linear, one end zero): Mn = %.1f kN m' % (f2_mn(L, 1.67) / 1e6))
print('  Lb = 8 m, Cb = 1.0 (elastic LTB): Mn = %.1f kN m' % (f2_mn(8000.0, 1.0) / 1e6))
close(Mp / 1e6, 341.5, 0.3)
close(Lp, 2734, 2)
close(Lr, 9631, 2)
close(0.9 * Mn1 / 1e6, 286.6, 0.1)
# Cb, F1-1, from quarter-point moments
def cb(mmax, ma, mb, mc):
    return 12.5 * mmax / (2.5 * mmax + 3 * ma + 4 * mb + 3 * mc)
print('  Cb uniform = %.3f; linear 0 to M = %.3f; simple span uniform load = %.3f'
      % (cb(1, 1, 1, 1), cb(1, .25, .5, .75), cb(1, .75, 1, .75)))
close(cb(1, .75, 1, .75), 1.136, 1e-3)
# G2.1, rolled I with h/tw <= 2.24 sqrt(E/Fy): Cv1 = 1, phi_v = 1.0
Aw = dd * tw
Vn = 0.6 * Fy * Aw * 1.0
print('  h/tw %.1f <= 2.24 sqrt(E/Fy) = %.1f: Vn = phi Vn = %.0f kN (Aw = d tw = %.0f mm2)'
      % (W['htw'], 2.24 * math.sqrt(E / Fy), Vn / 1e3, Aw))
close(Vn / 1e3, 454.0, 1.0)
# H1-1 combined, Pr = 1000 kN, Mrx = 100 kN m, Mry = 0
Mpy = min(Fy * Zy, 1.6 * Fy * Sy)
phiMcy = 0.9 * Mpy
def h1(Pr, Mrx, Mry, Pc, Mcx, Mcy):
    p = Pr / Pc
    if p >= 0.2:
        return p + 8.0 / 9.0 * (Mrx / Mcx + Mry / Mcy), 'H1-1a'
    return p / 2.0 + (Mrx / Mcx + Mry / Mcy), 'H1-1b'
for Pr, Mrx, Mry in ((1000e3, 100e6, 0.0), (200e3, 150e6, 20e6), (1800e3, 60e6, 10e6)):
    u, eq = h1(Pr, Mrx, Mry, phiPn, 0.9 * Mn1, phiMcy)
    print('  Pr %4.0f kN, Mrx %3.0f, Mry %2.0f kN m -> %s ratio %.3f'
          % (Pr / 1e3, Mrx / 1e6, Mry / 1e6, eq, u))
u1, _ = h1(1000e3, 100e6, 0.0, phiPn, 0.9 * Mn1, phiMcy)
close(u1, 0.7694, 1e-3)

# The app's own sharp-corner I section from the catalogue's nominal sizes (no fillets)
d0, bf0, tf0, tw0 = 10.0 * IN, 10.0 * IN, 0.560 * IN, 0.340 * IN
hw = d0 - 2 * tf0
A0 = 2 * bf0 * tf0 + hw * tw0
Iz0 = (bf0 * d0 ** 3 - (bf0 - tw0) * hw ** 3) / 12.0
Iy0 = (2 * tf0 * bf0 ** 3 + hw * tw0 ** 3) / 12.0
print('  app section (section-profiles.js, no fillets): A = %.0f mm2 (%.1f%% of table), '
      'Iz = %.4e (%.1f%%), ry = %.1f mm (%.1f%%)'
      % (A0, 100 * A0 / A, Iz0, 100 * Iz0 / mm(W['Ix'], 4), math.sqrt(Iy0 / A0),
         100 * math.sqrt(Iy0 / A0) / ry))
print('\nall asserts passed')
