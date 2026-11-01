"""ladybug_reference.py -- V172b's analyses worked out again, apart from the app and from Ladybug.

- The EPW and the DDY read as text: the EPW data dictionary (EnergyPlus 24.1, Auxiliary Programs) and the
  SizingPeriod:DesignDay fields as a station's DDY lays them out.
- UTCI by the official program's 6th-order polynomial: its 210 terms below were read out of UTCI_a002.f90 by a script
  (utci.org, 'UTCI Program Code.zip', SHA-256 83ea34dc2428093c8b0f4e299bfb0a24752ff49ec1e11741927a75dafae283f1, read
  2026-11-01; the program's text is not copied here, only its coefficients and their powers), with its saturation
  vapour pressure (Hardy 1998, as the program has it) and the ten categories of UTCI's scale: cold below a bound,
  heat above one, so 9.0 and 26.0 exactly are no thermal stress.
- PMV and PPD by Fanger's model as ISO 7730:2005 gives it (its program in Annex D), held here to the standard's 12 cases
  as Tartarini's validation tables v1.1.0 give them (MIT; ts_pmv_ppd.json, SHA-256
  182f8f8c6c6f9798424e6a95a1373b37bce70367e56aa24fb46215aff84a1025), and UTCI to its 8 in-range values (ts_utci.json,
  SHA-256 671094bb22fb69b4be71f060719c6ac1a40d25ff2f40dd09db4015ca73dac03d).
- The wind's 16 sectors centred on the compass points, lower edge in and upper out, calm a speed of exactly 0.
- The hours as Ladybug holds an EPW's (ladybug/epw.py, read in the wheel): its fields at an instant (temperature, dew
  point, humidity, wind, sky cover, the sky's infrared) have the file's last row moved to the front, so its 00:00 is
  the value at 00:00; its fields over an hour (pressure, radiation) are the rows as they are, its 00:00 the hour to
  01:00. Open-Meteo's hours the same way: an instant's variable its own hour, pressure and radiation the hour after
  (radiation being the mean of the hour before); a gap filled along the line between its neighbours.
- A board's figures in bands (figures whose rows overlap) and in reading order (row by row, left to right).
"""
import math

# the polynomial's terms: (coefficient, the powers of Ta, va, Tmrt - Ta, Pa in kPa), in the program's order
UTCI_TERMS = [
    (0.607562052, 0, 0, 0, 0),
    (-0.0227712343, 1, 0, 0, 0),
    (0.000806470249, 2, 0, 0, 0),
    (-0.000154271372, 3, 0, 0, 0),
    (-3.24651735e-06, 4, 0, 0, 0),
    (7.32602852e-08, 5, 0, 0, 0),
    (1.35959073e-09, 6, 0, 0, 0),
    (-2.2583652, 0, 1, 0, 0),
    (0.0880326035, 1, 1, 0, 0),
    (0.00216844454, 2, 1, 0, 0),
    (-1.53347087e-05, 3, 1, 0, 0),
    (-5.72983704e-07, 4, 1, 0, 0),
    (-2.55090145e-09, 5, 1, 0, 0),
    (-0.751269505, 0, 2, 0, 0),
    (-0.00408350271, 1, 2, 0, 0),
    (-5.21670675e-05, 2, 2, 0, 0),
    (1.94544667e-06, 3, 2, 0, 0),
    (1.14099531e-08, 4, 2, 0, 0),
    (0.158137256, 0, 3, 0, 0),
    (-6.57263143e-05, 1, 3, 0, 0),
    (2.22697524e-07, 2, 3, 0, 0),
    (-4.16117031e-08, 3, 3, 0, 0),
    (-0.0127762753, 0, 4, 0, 0),
    (9.66891875e-06, 1, 4, 0, 0),
    (2.52785852e-09, 2, 4, 0, 0),
    (0.000456306672, 0, 5, 0, 0),
    (-1.74202546e-07, 1, 5, 0, 0),
    (-5.91491269e-06, 0, 6, 0, 0),
    (0.398374029, 0, 0, 1, 0),
    (0.000183945314, 1, 0, 1, 0),
    (-0.00017375451, 2, 0, 1, 0),
    (-7.60781159e-07, 3, 0, 1, 0),
    (3.77830287e-08, 4, 0, 1, 0),
    (5.43079673e-10, 5, 0, 1, 0),
    (-0.0200518269, 0, 1, 1, 0),
    (0.000892859837, 1, 1, 1, 0),
    (3.45433048e-06, 2, 1, 1, 0),
    (-3.77925774e-07, 3, 1, 1, 0),
    (-1.69699377e-09, 4, 1, 1, 0),
    (0.000169992415, 0, 2, 1, 0),
    (-4.99204314e-05, 1, 2, 1, 0),
    (2.47417178e-07, 2, 2, 1, 0),
    (1.07596466e-08, 3, 2, 1, 0),
    (8.49242932e-05, 0, 3, 1, 0),
    (1.35191328e-06, 1, 3, 1, 0),
    (-6.21531254e-09, 2, 3, 1, 0),
    (-4.99410301e-06, 0, 4, 1, 0),
    (-1.89489258e-08, 1, 4, 1, 0),
    (8.15300114e-08, 0, 5, 1, 0),
    (0.00075504309, 0, 0, 2, 0),
    (-5.65095215e-05, 1, 0, 2, 0),
    (-4.52166564e-07, 2, 0, 2, 0),
    (2.46688878e-08, 3, 0, 2, 0),
    (2.42674348e-10, 4, 0, 2, 0),
    (0.00015454725, 0, 1, 2, 0),
    (5.2411097e-06, 1, 1, 2, 0),
    (-8.75874982e-08, 2, 1, 2, 0),
    (-1.50743064e-09, 3, 1, 2, 0),
    (-1.56236307e-05, 0, 2, 2, 0),
    (-1.33895614e-07, 1, 2, 2, 0),
    (2.49709824e-09, 2, 2, 2, 0),
    (6.51711721e-07, 0, 3, 2, 0),
    (1.94960053e-09, 1, 3, 2, 0),
    (-1.00361113e-08, 0, 4, 2, 0),
    (-1.21206673e-05, 0, 0, 3, 0),
    (-2.1820366e-07, 1, 0, 3, 0),
    (7.51269482e-09, 2, 0, 3, 0),
    (9.79063848e-11, 3, 0, 3, 0),
    (1.25006734e-06, 0, 1, 3, 0),
    (-1.81584736e-09, 1, 1, 3, 0),
    (-3.52197671e-10, 2, 1, 3, 0),
    (-3.3651463e-08, 0, 2, 3, 0),
    (1.35908359e-10, 1, 2, 3, 0),
    (4.1703262e-10, 0, 3, 3, 0),
    (-1.30369025e-09, 0, 0, 4, 0),
    (4.13908461e-10, 1, 0, 4, 0),
    (9.22652254e-12, 2, 0, 4, 0),
    (-5.08220384e-09, 0, 1, 4, 0),
    (-2.24730961e-11, 1, 1, 4, 0),
    (1.17139133e-10, 0, 2, 4, 0),
    (6.62154879e-10, 0, 0, 5, 0),
    (4.0386326e-13, 1, 0, 5, 0),
    (1.95087203e-12, 0, 1, 5, 0),
    (-4.73602469e-12, 0, 0, 6, 0),
    (5.12733497, 0, 0, 0, 1),
    (-0.312788561, 1, 0, 0, 1),
    (-0.0196701861, 2, 0, 0, 1),
    (0.00099969087, 3, 0, 0, 1),
    (9.51738512e-06, 4, 0, 0, 1),
    (-4.66426341e-07, 5, 0, 0, 1),
    (0.548050612, 0, 1, 0, 1),
    (-0.00330552823, 1, 1, 0, 1),
    (-0.0016411944, 2, 1, 0, 1),
    (-5.16670694e-06, 3, 1, 0, 1),
    (9.52692432e-07, 4, 1, 0, 1),
    (-0.0429223622, 0, 2, 0, 1),
    (0.00500845667, 1, 2, 0, 1),
    (1.00601257e-06, 2, 2, 0, 1),
    (-1.81748644e-06, 3, 2, 0, 1),
    (-0.00125813502, 0, 3, 0, 1),
    (-0.000179330391, 1, 3, 0, 1),
    (2.34994441e-06, 2, 3, 0, 1),
    (0.000129735808, 0, 4, 0, 1),
    (1.2906487e-06, 1, 4, 0, 1),
    (-2.28558686e-06, 0, 5, 0, 1),
    (-0.0369476348, 0, 0, 1, 1),
    (0.00162325322, 1, 0, 1, 1),
    (-3.1427968e-05, 2, 0, 1, 1),
    (2.59835559e-06, 3, 0, 1, 1),
    (-4.77136523e-08, 4, 0, 1, 1),
    (0.0086420339, 0, 1, 1, 1),
    (-0.000687405181, 1, 1, 1, 1),
    (-9.13863872e-06, 2, 1, 1, 1),
    (5.15916806e-07, 3, 1, 1, 1),
    (-3.59217476e-05, 0, 2, 1, 1),
    (3.28696511e-05, 1, 2, 1, 1),
    (-7.10542454e-07, 2, 2, 1, 1),
    (-1.243823e-05, 0, 3, 1, 1),
    (-7.385844e-09, 1, 3, 1, 1),
    (2.20609296e-07, 0, 4, 1, 1),
    (-0.00073246918, 0, 0, 2, 1),
    (-1.87381964e-05, 1, 0, 2, 1),
    (4.80925239e-06, 2, 0, 2, 1),
    (-8.7549204e-08, 3, 0, 2, 1),
    (2.7786293e-05, 0, 1, 2, 1),
    (-5.06004592e-06, 1, 1, 2, 1),
    (1.14325367e-07, 2, 1, 2, 1),
    (2.53016723e-06, 0, 2, 2, 1),
    (-1.72857035e-08, 1, 2, 2, 1),
    (-3.95079398e-08, 0, 3, 2, 1),
    (-3.59413173e-07, 0, 0, 3, 1),
    (7.04388046e-07, 1, 0, 3, 1),
    (-1.89309167e-08, 2, 0, 3, 1),
    (-4.79768731e-07, 0, 1, 3, 1),
    (7.96079978e-09, 1, 1, 3, 1),
    (1.62897058e-09, 0, 2, 3, 1),
    (3.94367674e-08, 0, 0, 4, 1),
    (-1.18566247e-09, 1, 0, 4, 1),
    (3.34678041e-10, 0, 1, 4, 1),
    (-1.15606447e-10, 0, 0, 5, 1),
    (-2.80626406, 0, 0, 0, 2),
    (0.548712484, 1, 0, 0, 2),
    (-0.0039942841, 2, 0, 0, 2),
    (-0.000954009191, 3, 0, 0, 2),
    (1.93090978e-05, 4, 0, 0, 2),
    (-0.308806365, 0, 1, 0, 2),
    (0.0116952364, 1, 1, 0, 2),
    (0.000495271903, 2, 1, 0, 2),
    (-1.90710882e-05, 3, 1, 0, 2),
    (0.00210787756, 0, 2, 0, 2),
    (-0.000698445738, 1, 2, 0, 2),
    (2.30109073e-05, 2, 2, 0, 2),
    (0.00041785659, 0, 3, 0, 2),
    (-1.27043871e-05, 1, 3, 0, 2),
    (-3.04620472e-06, 0, 4, 0, 2),
    (0.0514507424, 0, 0, 1, 2),
    (-0.00432510997, 1, 0, 1, 2),
    (8.99281156e-05, 2, 0, 1, 2),
    (-7.14663943e-07, 3, 0, 1, 2),
    (-0.000266016305, 0, 1, 1, 2),
    (0.000263789586, 1, 1, 1, 2),
    (-7.01199003e-06, 2, 1, 1, 2),
    (-0.000106823306, 0, 2, 1, 2),
    (3.61341136e-06, 1, 2, 1, 2),
    (2.29748967e-07, 0, 3, 1, 2),
    (0.000304788893, 0, 0, 2, 2),
    (-6.42070836e-05, 1, 0, 2, 2),
    (1.16257971e-06, 2, 0, 2, 2),
    (7.68023384e-06, 0, 1, 2, 2),
    (-5.47446896e-07, 1, 1, 2, 2),
    (-3.5993791e-08, 0, 2, 2, 2),
    (-4.36497725e-06, 0, 0, 3, 2),
    (1.68737969e-07, 1, 0, 3, 2),
    (2.67489271e-08, 0, 1, 3, 2),
    (3.23926897e-09, 0, 0, 4, 2),
    (-0.0353874123, 0, 0, 0, 3),
    (-0.22120119, 1, 0, 0, 3),
    (0.0155126038, 2, 0, 0, 3),
    (-0.000263917279, 3, 0, 0, 3),
    (0.0453433455, 0, 1, 0, 3),
    (-0.00432943862, 1, 1, 0, 3),
    (0.000145389826, 2, 1, 0, 3),
    (0.00021750861, 0, 2, 0, 3),
    (-6.66724702e-05, 1, 2, 0, 3),
    (3.3321714e-05, 0, 3, 0, 3),
    (-0.00226921615, 0, 0, 1, 3),
    (0.000380261982, 1, 0, 1, 3),
    (-5.45314314e-09, 2, 0, 1, 3),
    (-0.000796355448, 0, 1, 1, 3),
    (2.53458034e-05, 1, 1, 1, 3),
    (-6.31223658e-06, 0, 2, 1, 3),
    (0.000302122035, 0, 0, 2, 3),
    (-4.77403547e-06, 1, 0, 2, 3),
    (1.73825715e-06, 0, 1, 2, 3),
    (-4.09087898e-07, 0, 0, 3, 3),
    (0.614155345, 0, 0, 0, 4),
    (-0.0616755931, 1, 0, 0, 4),
    (0.00133374846, 2, 0, 0, 4),
    (0.00355375387, 0, 1, 0, 4),
    (-0.000513027851, 1, 1, 0, 4),
    (0.000102449757, 0, 2, 0, 4),
    (-0.00148526421, 0, 0, 1, 4),
    (-4.11469183e-05, 1, 0, 1, 4),
    (-6.80434415e-06, 0, 1, 1, 4),
    (-9.77675906e-06, 0, 0, 2, 4),
    (0.0882773108, 0, 0, 0, 5),
    (-0.00301859306, 1, 0, 0, 5),
    (0.00104452989, 0, 1, 0, 5),
    (0.000247090539, 0, 0, 1, 5),
    (0.00148348065, 0, 0, 0, 6),
]


def utci(ta, tr, va, rh):
    """UTCI in C: air temperature, mean radiant temperature, wind at 10 m (held to 0.5..17 m/s as Ladybug holds it), RH %"""
    va = min(17.0, max(0.5, va))
    pa = es(ta) * rh / 100.0 / 10.0   # kPa
    d = tr - ta
    s = ta
    for c, a, b, e, f in UTCI_TERMS:
        s += c * ta ** a * va ** b * d ** e * pa ** f
    return s


def es(t):
    """saturation vapour pressure over water, hPa: Hardy (1998), as UTCI_a002 computes it"""
    g = (-2.8365744e3, -6.028076559e3, 1.954263612e1, -2.737830188e-2, 1.6261698e-5, 7.0229056e-10, -1.8680009e-13)
    tk = t + 273.15
    v = 2.7150305 * math.log(tk)
    for i, x in enumerate(g):
        v += x * tk ** (i - 2)
    return math.exp(v) * 0.01


def utci_class(v, bands):
    """the category, 0 (extreme cold stress) to 9 (extreme heat stress); bands the nine bounds"""
    for k in range(5):
        if v < bands[k]:
            return k
    for k in range(5, 9):
        if v <= bands[k]:
            return 5 if k == 5 else k
    return 9


# ISO 7730:2005's cases (Tartarini's tables, v1.1.0): air, radiant, relative air speed, RH, met, clo -> PMV, PPD
ISO_7730 = [(22, 22, 0.1, 60, 1.2, 0.5, -0.8, 16.9), (27, 27, 0.1, 60, 1.2, 0.5, 0.8, 17.3), (27, 27, 0.3, 60, 1.2, 0.5, 0.4, 8.9),
            (23.5, 25.5, 0.1, 60, 1.2, 0.5, -0.0, 5.0), (23.5, 25.5, 0.3, 60, 1.2, 0.5, -0.6, 11.4), (19, 19, 0.1, 40, 1.2, 1.0, -0.6, 12.5),
            (23.5, 23.5, 0.3, 40, 1.2, 1.0, 0.1, 5.3), (23.0, 21.0, 0.1, 40, 1.2, 1.0, 0.1, 5.1), (23.0, 21.0, 0.3, 40, 1.2, 1.0, -0.2, 5.6),
            (22.0, 22.0, 0.1, 60, 1.6, 0.5, 0.1, 5.0), (27.0, 27.0, 0.1, 60, 1.6, 0.5, 1.2, 33.9), (27.0, 27.0, 0.3, 60, 1.6, 0.5, 0.9, 24.1)]
# UTCI's in-range cases (the same tables): air, radiant, RH, wind -> UTCI
UTCI_CASES = [(25, 27, 50, 1, 25.2), (19, 24, 50, 1, 20.0), (19, 14, 50, 1, 16.8), (27, 22, 50, 1, 25.5), (27, 22, 50, 10, 20.0),
              (27, 22, 50, 16, 15.8), (30, 27, 50, 1, 29.6), (9, 9, 50, 1, 8.7)]


def pmv_ppd(ta, tr, vel, rh, met, clo, wme=0.0):
    """Fanger's PMV and PPD (ISO 7730:2005, Annex D)"""
    pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))
    icl = 0.155 * clo
    m = met * 58.15
    w = wme * 58.15
    mw = m - w
    fcl = 1 + 1.29 * icl if icl <= 0.078 else 1.05 + 0.645 * icl
    hcf = 12.1 * math.sqrt(vel)
    taa, tra = ta + 273, tr + 273
    tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)
    p1 = icl * fcl
    p2, p3, p4 = p1 * 3.96, p1 * 100, p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * (tra / 100.0) ** 4
    xn, xf, n = tcla / 100.0, tcla / 50.0, 0
    hc = hcf
    while abs(xn - xf) > 0.00015:
        xf = (xf + xn) / 2
        hcn = 2.38 * abs(100.0 * xf - taa) ** 0.25
        hc = hcf if hcf > hcn else hcn
        xn = (p5 + p4 * hc - p2 * xf ** 4) / (100 + p3 * hc)
        n += 1
        if n > 150:
            raise ValueError('PMV did not converge')
    tcl = 100 * xn - 273
    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa)
    hl2 = 0.42 * (mw - 58.15) if mw > 58.15 else 0.0
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    hl4 = 0.0014 * m * (34 - ta)
    hl5 = 3.96 * fcl * (xn ** 4 - (tra / 100.0) ** 4)
    hl6 = fcl * hc * (tcl - ta)
    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100.0 - 95.0 * math.exp(-0.03353 * pmv ** 4 - 0.2179 * pmv ** 2)
    return pmv, ppd


def pmv_from_ppd(ppd):
    """the PMV at the edge of a PPD limit: PPD rises with |PMV|, so a bisection"""
    lo, hi = 0.0, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if pmv_ppd_value(mid) < ppd:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pmv_ppd_value(pmv):
    return 100.0 - 95.0 * math.exp(-0.03353 * pmv ** 4 - 0.2179 * pmv ** 2)


# ---- the EPW and the DDY ----
EPW_FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'flags', 'db', 'dp', 'rh', 'p', 'eh', 'ed', 'ir', 'gh', 'dn', 'df', 'gi', 'di', 'fi', 'zl',
              'wd', 'ws', 'tc', 'oc', 'vis', 'ceil', 'pwo', 'pwc', 'pw', 'aod', 'snow', 'dss', 'alb', 'rain', 'rainq']


def read_epw(text):
    """its location and its hours, as columns"""
    lines = [ln for ln in text.replace('\r', '').split('\n') if ln.strip()]
    loc = lines[0].split(',')
    rows = [ln.split(',') for ln in lines[8:]]
    cols = {f: [] for f in EPW_FIELDS}
    for r in rows:
        for i, f in enumerate(EPW_FIELDS):
            v = r[i]
            cols[f].append(v if f == 'flags' else float(v))
    return {'city': loc[1], 'state': loc[2], 'country': loc[3], 'source': loc[4], 'station': loc[5], 'lat': float(loc[6]), 'lon': float(loc[7]),
            'tz': float(loc[8]), 'elev': float(loc[9]), 'n': len(rows), 'cols': cols}


def read_ddy(text):
    """the SizingPeriod:DesignDay objects: name, month, day, type, dry bulb, range, humidity type and value, pressure, wind"""
    out, cur = [], None
    for ln in text.replace('\r', '').split('\n'):
        s = ln.split('!-')[0].strip()
        if s.startswith('SizingPeriod:DesignDay'):
            cur = []
            continue
        if cur is None or not s:
            continue
        end = s.endswith(';')
        cur.append(s.rstrip(',;').strip())
        if end:
            out.append({'name': cur[0], 'month': int(cur[1]), 'day': int(cur[2]), 'type': cur[3], 'db': float(cur[4]), 'range': float(cur[5]),
                        'hum_type': cur[8], 'hum': float(cur[9]), 'p': float(cur[14]), 'wind': float(cur[15]), 'dir': float(cur[16])})
            cur = None
    return out


# ---- the wind ----
def wind_rose(wd, ws, bins, sectors=16):
    """each sector's hours by speed band; calm (a speed of 0) apart. A sector is centred on its compass point, its lower
    edge in and its upper edge out; a speed falls in the last band whose lower bound it reaches."""
    w = 360.0 / sectors
    S = [[0] * len(bins) for _ in range(sectors)]
    calm = 0
    for d, v in zip(wd, ws):
        if v == 0:
            calm += 1
            continue
        k = int(math.floor(((d + w / 2) % 360.0) / w)) % sectors
        j = 0
        for i, b in enumerate(bins):
            if v >= b:
                j = i
        S[k][j] += 1
    return S, calm


# ---- Open-Meteo's hours, as the app reads them ----
def fill(vals):
    """gaps (None) along the line between their neighbours, the ends held"""
    out = list(vals)
    good = [i for i, v in enumerate(out) if v is not None]
    for i in range(len(out)):
        if out[i] is None:
            lo = [g for g in good if g < i]
            hi = [g for g in good if g > i]
            if not lo:
                out[i] = out[hi[0]]
            elif not hi:
                out[i] = out[lo[-1]]
            else:
                a, b = lo[-1], hi[0]
                out[i] = out[a] + (out[b] - out[a]) * (i - a) / float(b - a)
    return out


def instant(col):
    """an EPW's column at an instant, as Ladybug holds it: the last row first"""
    return [col[-1]] + list(col[:-1])


def om_hours(body, n):
    """the year's n hours from Open-Meteo's answer, as Ladybug holds an EPW's: an instant's variable at its own hour,
    pressure and radiation the hour after"""
    h = body['hourly']
    return {'db': fill(h['temperature_2m'][0:n]), 'rh': [min(100.0, max(0.0, v)) for v in fill(h['relative_humidity_2m'][0:n])],
            'ws': [max(0.0, v) for v in fill(h['wind_speed_10m'][0:n])], 'wd': [v % 360.0 for v in fill(h['wind_direction_10m'][0:n])],
            'p': [v * 100.0 for v in fill(h['surface_pressure'][1:n + 1])], 'tenths': [min(10.0, max(0.0, v * 0.1)) for v in fill(h['cloud_cover'][0:n])],
            'gh': fill(h['shortwave_radiation'][1:n + 1]), 'filled': sum(1 for v in h['temperature_2m'][0:n] if v is None)}


# ---- a board's figures in bands, and in reading order ----
def bands(figs):
    """bands of figures whose rows overlap, top to bottom; in each, rows (tops within a quarter step) left to right"""
    L = sorted(figs, key=lambda f: (f['y'], f['x']))
    out = []
    for f in L:
        if out and f['y'] < out[-1]['b'] - 1e-6:
            out[-1]['f'].append(f)
            out[-1]['b'] = max(out[-1]['b'], f['y'] + f['h'])
        else:
            out.append({'t': f['y'], 'b': f['y'] + f['h'], 'f': [f]})
    for B in out:
        row, ry, keyed = 0, None, []
        for g in B['f']:
            if ry is None or g['y'] - ry >= 0.25:
                if ry is not None:
                    row += 1
                ry = g['y']
            keyed.append((row, g['x'], g))
        B['f'] = [g for _, _, g in sorted(keyed, key=lambda t: (t[0], t[1]))]
    return [{'t': B['t'], 'b': B['b'], 'k': [g['k'] for g in B['f']]} for B in out]
