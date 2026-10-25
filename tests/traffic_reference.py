"""traffic_reference.py -- V171's numbers worked out again in Python from their sources (reference/research-traffic.md,
section 7), not from the app's code: the car following, the signal plans, the turns, the site's trips and the streets'
traffic. The suite compares the app's results with these.

  IDM        Kesting, Treiber and Helbing (2010), equations 2.1 and 2.2, Table 1: a car
  MOBIL      Kesting, Treiber and Helbing (2007), Table 1
  Signals    FHWA Traffic Signal Timing Manual (2008): 3.3 (saturation flow, lost time), 5.3 (Kell and Fullerton,
             Table 5-3), 6.4 (Webster, the least and the preferred most cycle); MUTCD 11th Edition, 4F.17 and 4I.06
  K          FDOT Project Traffic Forecasting Handbook (2014), Figure 2.4: 9% on urban arterials
  Turns      NCHRP Report 255 (1982), chapter 8: the matrix balanced to the streets' volumes
  Trips      City of San Diego, Trip Generation Manual (May 2003), Table 1
  Walkers    Helbing and Molnar (1995), section III
"""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from standards_reference import FHWA, OSM_FC   # noqa: E402

FT = 0.3048
MPH = 1.609344

# ---- the IDM's car (Table 1) and the step ----
IDM = {'T': 1.5, 's0': 2.0, 'a': 1.4, 'b': 2.0, 'delta': 4}
FREE = 1000.0          # Treiber: a free road is a gap of 1000 m
STEP = 0.2             # the app's step, under Treiber's 0.5 s
CAR_L = 5.79           # AASHTO's passenger car, 19 ft (V169)


def idm(v, v0, s, dv, P=IDM):
    """the IDM's acceleration: a [1 - (v/v0)^delta - (s*/s)^2], s* = s0 + max(0, vT + v dv / (2 sqrt(ab)))"""
    ss = P['s0'] + max(0.0, v * P['T'] + v * dv / (2 * math.sqrt(P['a'] * P['b'])))
    return P['a'] * (1 - (max(0.0, v) / v0) ** P['delta'] - (ss / s) ** 2)


def gap_eq(v, v0, P=IDM):
    """the steady gap behind a car at v: s_e = (s0 + vT) / sqrt(1 - (v/v0)^delta)"""
    return (P['s0'] + v * P['T']) / math.sqrt(1 - (v / v0) ** P['delta'])


MOBIL = {'p': 1.0, 'thr': 0.1, 'bsafe': 4.0}

# ---- signals ----
SAT = 1900             # passenger cars an hour a lane (3.3.2)
LOST = 4               # seconds a phase (3.3.3)
WEBSTER = (1.5, 5)     # (1.5 L + 5) / (1 - Y), Equation 6-1
CYCLE = (60, 120)      # the least suggested; the preferred most for four legs (6.4)
Y_MAX = 0.95           # the app's: at or above, the longest cycle
KF_T, KF_A, KF_LV = 1.0, 10 * FT, 20 * FT   # Equation 5-2: t 1 s, a 10 ft/s2, a vehicle 20 ft
YELLOW = (3, 6)        # MUTCD 4F.17
RED_MAX = 6            # MUTCD 4F.17
WALK = 7               # MUTCD 4I.06
CLEAR = 3.5 * FT       # MUTCD 4I.06, 3.5 ft/s
MIN_GREEN = {'fast': 10, 'major': 7, 'minor': 4, 'local': 2}   # Table 5-3's lower values
FAST = 40 * MPH        # km/h: a major arterial over 40 mph


def green_class(base, v0):
    """an approach's class for its least green: FHWA's class of its street (the app's reading of OpenStreetMap's)"""
    fc = OSM_FC.get(base)
    if fc in ('interstate', 'freeway', 'opa'):
        return 'fast' if v0 * 3.6 > FAST else 'major'
    return 'minor' if fc == 'minor_art' else 'local'


def _along(b, axis):
    d = ((b - axis) % 180 + 180) % 180
    return d < 45 or d > 135


def plan(ap, arms):
    """a two-phase plan. ap: the approaches [{'bear', 'q', 'lanes', 'v', 'cls'}]; arms: the car arms [{'k', 'bear', 'w'}].
    The approach with the most traffic a lane sets the first phase's axis; within 45 degrees of it, either way, is that
    phase. Returns {'C', 'C0', 'Y', 'L', 'grown', 'ph': [{'arms', 'y', 'Y', 'AR', 'G', 'gmin', 't0'}]}"""
    crit = ap[0]
    for a in ap[1:]:
        if a['q'] / a['lanes'] > crit['q'] / crit['lanes']:
            crit = a
    axis = crit['bear'] % 180
    ph = [{'arms': [], 'ap': []}, {'arms': [], 'ap': []}]
    for a in arms:
        ph[0 if _along(a['bear'], axis) else 1]['arms'].append(a['k'])
    for a in ap:
        ph[0 if _along(a['bear'], axis) else 1]['ap'].append(a)
    width = [max([a['w'] for a in arms if a['k'] in ph[k]['arms']] or [0]) for k in (0, 1)]
    out, Y, change = [], 0.0, 0.0
    for k in (0, 1):
        A = ph[k]['ap']
        y = max([a['q'] / a['lanes'] for a in A] or [0]) / SAT
        v = max([a['v'] for a in A] or [0])
        o = {'arms': ph[k]['arms'], 'y': y, 'Y': 0.0, 'AR': 0.0}
        if A:
            o['Y'] = min(YELLOW[1], max(YELLOW[0], KF_T + v / (2 * KF_A)))
            o['AR'] = min(RED_MAX, (width[1 - k] + KF_LV) / max(v, 0.1))
        o['gdrv'] = max([MIN_GREEN[a['cls']] for a in A] or [0])
        o['gped'] = WALK + width[1 - k] / CLEAR
        o['gmin'] = max(o['gdrv'], o['gped'])
        Y += y
        change += o['Y'] + o['AR']
        out.append(o)
    L = 2 * LOST
    C0 = (WEBSTER[0] * L + WEBSTER[1]) / (1 - Y) if Y < Y_MAX else math.inf
    C = min(CYCLE[1], max(CYCLE[0], C0))
    G = greens(C - change, [o['y'] for o in out], [o['gmin'] for o in out])
    grown = False
    if sum(G) + change > C + 1e-9:
        C, grown = sum(G) + change, True
    t = 0.0
    for o, g in zip(out, G):
        o['G'], o['t0'] = g, t
        t += g + o['Y'] + o['AR']
    return {'C': C, 'C0': C0, 'Y': Y, 'L': L, 'grown': grown, 'ph': out, 'axis': axis}


def greens(avail, y, gmin):
    """the time the change intervals leave, shared by y; a green under its least is held at it and the rest shared"""
    fixed = [False] * len(y)
    while True:
        rest = avail - sum(g for g, f in zip(gmin, fixed) if f)
        yf = sum(v for v, f in zip(y, fixed) if not f)
        free = [i for i in range(len(y)) if not fixed[i]]
        G = [gmin[i] if fixed[i] else (rest * y[i] / yf if yf > 0 else rest / len(free)) for i in range(len(y))]
        low = [i for i in free if G[i] < gmin[i] - 1e-9]
        if not low:
            return G
        for i in low:
            fixed[i] = True
        if all(fixed):
            return list(gmin)


def signal(P, k, t):
    """phase k's light at time t: ('g', the green left), ('y', the yellow left) or ('r', 0)"""
    tc = t % P['C']
    o = P['ph'][k]
    x = (tc - o['t0']) % P['C']
    if x < o['G']:
        return 'g', o['G'] - x
    if x < o['G'] + o['Y']:
        return 'y', o['G'] + o['Y'] - x
    return 'r', 0.0


# ---- demand ----
K = 9                  # percent (FDOT, Figure 2.4)
ITER = 10              # NCHRP 255: six to ten rounds


def fc_mid(r):
    """the middle of an AADT range, to the nearest 10, as the noise analysis takes it"""
    return round((r[0] + r[1]) / 20) * 10


def link_volume(base):
    """a direction's volume in the peak hour: its class's urban AADT's middle times K, half of it each way"""
    fc = OSM_FC.get(base)
    if not fc:
        return 0.0
    return fc_mid(FHWA[fc][2]) * K / 100 * 0.5


def furness(qi, qo, ok, n=ITER):
    """NCHRP 255's balancing: each approach's turns first in proportion to the exits' volumes, then the matrix scaled to
    the exits' volumes (their total made the approaches') and to the approaches', in turn, n times. Returns each
    approach's shares (an approach with nothing to share by: its allowed exits evenly)"""
    I, J = len(qi), len(qo)
    ti, to = sum(qi), sum(qo)
    target = [v * ti / to for v in qo] if to > 0 else [0.0] * J
    T = []
    for i in range(I):
        row = [qo[j] if ok[i][j] and qo[j] > 0 else 0.0 for j in range(J)]
        s = sum(row)
        T.append([x / s * qi[i] if s > 0 else 0.0 for x in row])
    if ti > 0 and to > 0:
        for _ in range(n):
            for j in range(J):
                cs = sum(T[i][j] for i in range(I))
                if cs > 0:
                    for i in range(I):
                        T[i][j] *= target[j] / cs
            for i in range(I):
                rs = sum(T[i])
                if rs > 0:
                    T[i] = [x * qi[i] / rs for x in T[i]]
    out = []
    for i in range(I):
        s = sum(T[i])
        if s > 0:
            out.append([x / s for x in T[i]])
        else:
            m = sum(1 for j in range(J) if ok[i][j])
            out.append([(1 / m if ok[i][j] else 0.0) if m else 0.0 for j in range(J)])
    return out


# ---- the site's trips: San Diego's Table 1 ----
SD = {'mdu_lo': {'rate': 8, 'am': (8, 2, 8), 'pm': (10, 7, 3)},
      'mdu_hi': {'rate': 6, 'am': (8, 2, 8), 'pm': (9, 7, 3)},
      'office': {'ln': (0.756, 3.95), 'am': (13, 9, 1), 'pm': (14, 2, 8)},
      'retail': {'rate': 40, 'am': (3, 6, 4), 'pm': (9, 5, 5)},
      'hotel': {'rate': 10, 'am': (6, 6, 4), 'pm': (8, 6, 4)}}
DENSE = 20             # dwelling units an acre
ACRE = 4046.8564224    # m2, the international acre
KSF = 1000 * FT * FT   # m2 in a thousand square feet


def trips(rows, acres, peak):
    """rows [(use, n)]: dwelling units, thousand sq ft or rooms; returns (in, out, [(key, day, in, out)])"""
    du = sum(n for u, n in rows if u == 'mdu')
    tin = tout = 0.0
    per = []
    for u, n in rows:
        key = ('mdu_hi' if acres and du / acres > DENSE else 'mdu_lo') if u == 'mdu' else u
        R = SD.get(key)
        if not R or not n > 0:
            per.append((key, 0.0, 0.0, 0.0))
            continue
        day = math.exp(R['ln'][0] * math.log(n) + R['ln'][1]) if 'ln' in R else R['rate'] * n
        share, a, b = R[peak]
        ph = day * share / 100
        per.append((key, day, ph * a / (a + b), ph * b / (a + b)))
        tin += ph * a / (a + b)
        tout += ph * b / (a + b)
    return tin, tout, per


# ---- walkers ----
WALK_MEAN, WALK_SD, WALK_CAP = 1.34, 0.26, 1.3
