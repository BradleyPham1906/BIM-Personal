"""Wind (ASCE/SEI 7-22, ch. 26-27, directional procedure) and floor live load (ASCE 7-22 4.7, 4.8)
arithmetic, as data and checks only: the numbers behind
docs/research/research-physical-world/loads-wind-gravity.md (2026-11-21).

Run: python3 -I docs/research/experiments/physical-world/wind_loads.py
It prints every table and asserts every check; it fetches nothing and writes nothing.

Sources of the constants (levels as in the note):
  Table 26.11-1 (7-22) alpha, zg: B 7.5/3280 ft, C 9.8/2460 ft, D 11.5/1935 ft; 7-16 B 7.0/1200,
      C 9.5/900, D 11.5/700 (S: S.K. Ghosh, ICC 2023 deck, slide 142; Oasis Engineering's MIT code).
  Kz = 2.41 (z/zg)^(2/alpha) for 15 ft <= z <= zg; z < 15 ft uses 15 ft; Kz = 2.41 for zg <= z <= 3280 ft
      (7-22; 7-16 used 2.01) (S: Ghosh slide 141; Oasis code).
  q = 0.00256 Kz Kzt Ke V^2 (psf, mph) = 0.613 Kz Kzt Ke V^2 (Pa, m/s), Eq. 26.10-1, Kd NOT in q (S: ICC
      Demystifying Loads Part 2; 0.613 derivation P in ASCE 7-02 C6.5.10).
  p = q Kd G Cp - qi Kd (GCpi), Eq. 27.3-1 (S: ICC Demystifying Loads Part 2).
  Kd 0.85 buildings (Table 26.6-1), G 0.85 rigid, Cp walls 0.8 / -0.5,-0.3,-0.2 / -0.7 (P in 7-02 Fig. 6-6;
      S for 7-22), GCpi +/-0.18 enclosed.
  Live load reduction L = Lo (0.25 + 4.57/sqrt(KLL AT)) (P in IBC 2021 1607.12.1 via Seattle's adopted copy;
      S for ASCE 7-22 4.7.2 via ENERCALC's 7-22 verification example).
"""

import math

FT = 0.3048                 # m per ft, exact
MPH = 0.44704               # m/s per mph, exact (also the ASCE Hazard Tool's own factor)
PSF = 0.047880258980        # kPa per psf (= 0.45359237 kg * 9.80665 / 0.09290304 m2 / 1000)

# Table 26.11-1 terrain exposure constants: alpha, zg (ft)
EXPOSURE_722 = {'B': (7.5, 3280.0), 'C': (9.8, 2460.0), 'D': (11.5, 1935.0)}
EXPOSURE_716 = {'B': (7.0, 1200.0), 'C': (9.5, 900.0), 'D': (11.5, 700.0)}


def kz(z_ft, exposure, edition='7-22'):
    """Velocity pressure exposure coefficient Kz (Table 26.10-1 note formula)."""
    alpha, zg = (EXPOSURE_722 if edition == '7-22' else EXPOSURE_716)[exposure]
    c = 2.41 if edition == '7-22' else 2.01
    z = max(z_ft, 15.0)
    if z >= zg:
        return c
    return c * (z / zg) ** (2.0 / alpha)


def kz_si(z_m, exposure, edition='7-22'):
    return kz(z_m / FT, exposure, edition)


def ke_si(elev_m):
    """Ground elevation factor, exponential form e^(-0.0000362 zg_ft) (S, see note)."""
    return math.exp(-0.0000362 * elev_m / FT)


def q_si(z_m, V, exposure, Kzt=1.0, Ke=1.0):
    """Velocity pressure, Pa, V in m/s, Eq. 26.10-1 (7-22: no Kd)."""
    return 0.613 * kz_si(z_m, exposure) * Kzt * Ke * V * V


def cp_leeward(L_over_B):
    """Leeward wall Cp, Fig. 27.3-1: -0.5 (0-1), -0.3 (2), -0.2 (>=4), linear between."""
    r = L_over_B
    if r <= 1.0:
        return -0.5
    if r <= 2.0:
        return -0.5 + (r - 1.0) * 0.2
    if r <= 4.0:
        return -0.3 + (r - 2.0) * 0.05
    return -0.2


def approx_close(a, b, tol):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- check 1: Kz against tabulated values
# Ghosh (ICC 2023), slides 143-144: Kz for Exposures B and C, 7-16 and 7-22 columns.
GHOSH_B = {15: (0.57, 0.57), 20: (0.62, 0.62), 25: (0.67, 0.66), 30: (0.70, 0.69), 40: (0.76, 0.74),
           50: (0.81, 0.79), 60: (0.85, 0.83), 70: (0.89, 0.86), 80: (0.93, 0.90), 90: (0.96, 0.92),
           100: (0.99, 0.95), 120: (1.04, 1.00), 140: (1.09, 1.04), 160: (1.13, 1.08), 180: (1.17, 1.11),
           200: (1.20, 1.14), 250: (1.28, 1.21), 300: (1.35, 1.27), 350: (1.41, 1.33), 400: (1.47, 1.38),
           450: (1.52, 1.42), 500: (1.57, 1.46)}
GHOSH_C = {15: (0.85, 0.85), 20: (0.90, 0.90), 25: (0.95, 0.94), 30: (0.98, 0.98), 40: (1.04, 1.04),
           50: (1.09, 1.09), 60: (1.14, 1.13), 70: (1.17, 1.17), 80: (1.21, 1.20), 90: (1.24, 1.23),
           100: (1.27, 1.25), 120: (1.32, 1.30), 140: (1.36, 1.34), 160: (1.40, 1.38), 180: (1.43, 1.41),
           200: (1.46, 1.44), 250: (1.53, 1.51), 300: (1.59, 1.57), 350: (1.65, 1.62), 400: (1.69, 1.66),
           450: (1.74, 1.70), 500: (1.78, 1.74)}
# ICC Demystifying Loads Part 2, slide 41: 7-22 Exposure D column.
ICC_D = {15: 1.03, 20: 1.08, 25: 1.12, 30: 1.16, 40: 1.22, 50: 1.27, 60: 1.31, 70: 1.34, 80: 1.38,
         90: 1.40, 100: 1.43, 120: 1.48, 140: 1.52, 160: 1.55, 180: 1.58, 200: 1.61, 250: 1.68,
         300: 1.73, 350: 1.78, 400: 1.82, 450: 1.86, 500: 1.89}

print('Check 1: Kz formula against tabulated Kz (2 decimals)')
mism = []
for exp, tab in (('B', GHOSH_B), ('C', GHOSH_C)):
    for z, (k16, k22) in tab.items():
        for ed, kt in (('7-16', k16), ('7-22', k22)):
            k = kz(z, exp, ed)
            if not approx_close(k, kt, 0.0051):
                mism.append((exp, ed, z, round(k, 4), kt))
print('  B and C rows compared:', 4 * len(GHOSH_B), 'mismatches > 0.005:', mism)
# Known: Ghosh's 7-16 B at 500 ft prints 1.57 where the formula gives 1.564 (ICC's deck prints 1.56).
assert all(m[:3] == ('B', '7-16', 500) for m in mism), mism
# Exposure D: the ICC deck's 7-22 D column (no change marked) follows the 7-16 constants
# (2.01, 700 ft); the 7-22 formula (2.41, 1935 ft) gives values up to about 0.015 higher.
d16 = max(abs(kz(z, 'D', '7-16') - kt) for z, kt in ICC_D.items())
d22 = max(abs(kz(z, 'D', '7-22') - kt) for z, kt in ICC_D.items())
d22_signed = min(kz(z, 'D', '7-22') - kt for z, kt in ICC_D.items())
print('  Exposure D, ICC column: max |diff| vs 7-16 formula %.4f, vs 7-22 formula %.4f (7-22 formula never lower: %s)'
      % (d16, d22, d22_signed > -0.0051))
assert d16 < 0.0075 and d22 < 0.016 and d22_signed > -0.0051

# ---------------------------------------------------------------- check 2: ICC Example 5.12 (7-22, Exp B, V 105 mph)
print('Check 2: ICC Example 5.12, Exposure B, V = 105 mph, Kzt = Ke = 1')
for z, kt, qt in ((142.5, 1.04, 29.4), (104.5, 0.96, 27.1), (47.5, 0.78, 22.0)):
    k = kz(z, 'B')
    q = 0.00256 * k * 105 ** 2
    q_tab = 0.00256 * kt * 105 ** 2          # the example rounds Kz to 2 places before q
    print('  z %.1f ft  Kz %.4f (table %.2f)  qz %.2f psf, with rounded Kz %.2f (table %.1f)'
          % (z, k, kt, q, q_tab, qt))
    assert approx_close(k, kt, 0.0051) and approx_close(q_tab, qt, 0.06) and approx_close(q, qt, 0.15)

# ---------------------------------------------------------------- check 3: Ke table against the exponential
print('Check 3: Ke table (7-16 Table 26.9-1 per Ghosh slide 114) against e^(-0.0000362 zg)')
for elev_ft, kt in ((0, 1.00), (1000, 0.96), (2000, 0.93), (3000, 0.90), (4000, 0.86), (5000, 0.83), (6000, 0.80)):
    k = math.exp(-0.0000362 * elev_ft)
    print('  %5d ft  %.4f (table %.2f)' % (elev_ft, k, kt))
    assert approx_close(k, kt, 0.006)  # the table looks rounded down at 4000 ft (0.8652 -> 0.86)

# ---------------------------------------------------------------- check 4: constants
print('Check 4: constants')
c_si = 0.5 * 1.225          # 1/2 rho, rho = 1.225 kg/m3 standard atmosphere -> Pa per (m/s)^2
c_us = 0.5 * 0.0765 / 32.174 * (5280.0 / 3600.0) ** 2   # psf per mph^2 (7-02 C6.5.10 derivation)
print('  0.5*rho SI %.4f (ASCE 0.613); US %.6f (ASCE 0.00256)' % (c_si, c_us))
assert approx_close(c_si, 0.613, 0.0005) and approx_close(c_us, 0.00256, 0.000005)
print('  15*sqrt(ft2->m2) = %.4f (ASCE 4.57); 400 ft2 = %.2f m2 (37.16); 100 psf = %.3f kPa (4.79)'
      % (15 * math.sqrt(FT * FT), 400 * FT * FT, 100 * PSF))
assert approx_close(15 * FT, 4.57, 0.003) and approx_close(400 * FT * FT, 37.16, 0.005)
print('  zg SI: B %.1f m, C %.1f m, D %.1f m; z min 15 ft = %.3f m' %
      (3280 * FT, 2460 * FT, 1935 * FT, 15 * FT))

# ---------------------------------------------------------------- worked example (a)
print('\nWorked example (a): 30 m x 20 m enclosed, 3 storeys of 3.5 m, V 50 m/s, Exposure C,')
print('Kzt = Ke = 1, Kd 0.85, G 0.85, wind normal to the 30 m face (B = 30 m, L = 20 m)')
V, B, L, Kd, G, Kzt, Ke = 50.0, 30.0, 20.0, 0.85, 0.85, 1.0, 1.0
levels = [3.5, 7.0, 10.5]
h = levels[-1]
cpw, cpl = 0.8, cp_leeward(L / B)
assert cpl == -0.5
qh = q_si(h, V, 'C')
p_lee = qh * Kd * G * cpl                         # Pa, negative = away from the leeward face
print('  L/B = %.3f -> leeward Cp %.1f; qh = q(10.5 m) = %.1f Pa; leeward p = %.1f Pa' % (L / B, cpl, qh, p_lee))
trib = []
for i, z in enumerate(levels):
    lo = (z + (levels[i - 1] if i else 0.0)) / 2.0
    hi = z if i == len(levels) - 1 else (z + levels[i + 1]) / 2.0
    trib.append((lo, hi))
rows = []
total = 0.0
for z, (lo, hi) in zip(levels, trib):
    k = kz_si(z, 'C')
    qz = q_si(z, V, 'C')
    p_wind = qz * Kd * G * cpw
    net = p_wind - p_lee                        # GCpi cancels on the two opposite walls
    F = net * B * (hi - lo) / 1000.0            # kN
    total += F
    rows.append((z, k, qz, p_wind, net, lo, hi, F))
    print('  z %4.1f m  Kz %.4f  qz %7.1f Pa  windward p %6.1f Pa  net %6.1f Pa  band %.2f-%.2f m  F %.2f kN'
          % (z, k, qz, p_wind, net, lo, hi, F))
base_band = trib[0][0]
print('  bottom band 0-%.2f m goes straight to the base (not a storey force)' % base_band)
print('  sum of storey forces, Case 1: %.2f kN' % total)
# Fixed expectations for a test (rounded):
exp_kz = [0.8512, 0.9285, 1.0086]
exp_F = [137.79, 144.98, 76.21]
for (z, k, *rest), ke, fe in zip(rows, exp_kz, exp_F):
    assert approx_close(k, ke, 0.0001) and approx_close(rest[-1], fe, 0.01), (z, k, rest[-1])
assert approx_close(total, 358.99, 0.02)
# Case 2: 0.75 of Case 1 with MT = 0.75 (PW + PL) B ex, ex = +/-0.15 B, per unit height; per storey:
print('  Case 2 per storey: 0.75 F and torsion 0.75 F x 0.15 B:')
for z, k, qz, pw, net, lo, hi, F in rows:
    print('    z %4.1f m  F %.2f kN  MT +/- %.2f kN m' % (z, 0.75 * F, 0.75 * F * 0.15 * B))
print('  Case 3: 0.75 of Case 1 in both directions at once; Case 4: 0.563 of Case 1 in both, with')
print('  MT = 0.563 (Fx Bx ex + Fy By ey), e = +/-0.15 B (Fig. 27.3-8; 7-02 Fig. 6-9 text, P)')

# ---------------------------------------------------------------- worked example (b): live load reduction
print('\nWorked example (b): office, Lo = 2.40 kPa (50 psf; Table 4.3-1 prints 2.40), 8 m x 8 m bays')


def llr(Lo, KLL, AT, floors, Lo_limit_kpa=4.79, reducible=True):
    """ASCE 7-22 4.7.2 basic reduction (SI). Returns (L, why)."""
    if not reducible:
        return Lo, 'not reducible (assembly, Table footnote)'
    if Lo > Lo_limit_kpa:
        if floors >= 2:
            return Lo * 0.8, 'heavy live load: 20 % for 2+ floors only'
        return Lo, 'heavy live load: not reduced'
    if KLL * AT < 37.16:
        return Lo, 'KLL AT < 37.16 m2'
    f = 0.25 + 4.57 / math.sqrt(KLL * AT)
    lim = 0.5 if floors == 1 else 0.4
    return Lo * max(min(f, 1.0), lim), 'factor %.5f, floor %.2f' % (f, lim)


cases = [
    ('interior column, 2 floors above (AT 128 m2)', 2.40, 4, 128.0, 2),
    ('interior column, 1 floor (AT 64 m2)', 2.40, 4, 64.0, 1),
    ('interior beam 8 m span at 4 m (AT 32 m2)', 2.40, 2, 32.0, 1),
    ('interior beam 4 m span at 4 m (AT 16 m2)', 2.40, 2, 16.0, 1),
    ('interior column, 5 floors (AT 320 m2)', 2.40, 4, 320.0, 5),
    ('storage 7.18 kPa column, 2 floors (AT 128 m2)', 7.18, 4, 128.0, 2),
]
expect = [1.0847, 1.2855, 1.9710, 2.40, 0.96, 5.744]
for (name, Lo, K, A, n), e in zip(cases, expect):
    Lr, why = llr(Lo, K, A, n)
    print('  %-48s L = %.4f kPa (%s); L x AT %.1f kN' % (name, Lr, why, Lr * A))
    assert approx_close(Lr, e, 0.0006), (name, Lr)
Lr, why = llr(4.79, 4, 128.0, 2, reducible=False)
print('  %-48s L = %.4f kPa (%s)' % ('assembly lobby 4.79 kPa column', Lr, why))

# ENERCALC 7-22 verification example (imperial): Lo 80 psf, KLL 4, AT 570 ft2, one floor -> 45.131 psf
L80 = 80 * (0.25 + 15 / math.sqrt(4 * 570))
print('  ENERCALC column check: %.3f psf (published 45.131)' % L80)
assert approx_close(L80, 45.131, 0.001)
# Roof (4.8): Lo 20 psf, At 570 ft2, F = 5 -> R1 0.63, R2 0.95, 11.97 -> 12 psf minimum
R1 = 1.2 - 0.001 * 570
R2 = 1.2 - 0.05 * 5
Lr_roof = max(12.0, min(20.0, 20 * R1 * R2))
print('  ENERCALC roof check: R1 %.2f R2 %.2f Lo R1 R2 %.2f psf -> %.0f psf' % (R1, R2, 20 * R1 * R2, Lr_roof))
assert approx_close(20 * R1 * R2, 11.97, 0.001) and Lr_roof == 12.0

# ---------------------------------------------------------------- data: ASCE geodatabase answers (2026-11-21)
print('\nData recorded from gis.asce.org ASCE722/w2022_mri{300,700,1700,3000} identify (mph, raw grid):')
SAMPLES = {'Denver -105.0,40.0': (100.875, 106.977, 113.418, 117.381),
           'Chicago -87.63,41.88': (100.0, 107.061, 114.252, 119.214),
           'Miami -80.19,25.77': (157.024, 169.202, 181.417, 189.231),
           'San Francisco -122.42,37.77': (86.4817, 91.8424, 98.563, 102.782),
           'New York -74.0,40.71': (107.826, 115.698, 125.506, 129.743),
           'Houston -95.37,29.76': (125.597, 133.376, 139.772, 145.167)}
for k, v in SAMPLES.items():
    print('  %-28s RC I-IV %s mph -> RC II %d mph = %d m/s (tool rounds after converting)'
          % (k, v, round(v[1]), round(v[1] * MPH)))
print('\nAll checks passed.')
