"""movement_reference.py -- V166's methods worked out again in Python, apart from the app, for the suite.

From the published methods, not from the app's code:
- level of traffic stress, Mekuria, Furth and Nixon (MTI report 11-19, 2012): separated paths 1; a bike
  lane beside parking by the lanes each way (one 1, more 3) and the speed (25 mph 1, 30 2, 35 3, 40 4); a
  bike lane with no parking by the lanes each way (one 1, two on a divided road's carriageway 2, more 3),
  its width (6 ft or more 1, less 2, unmapped not counted) and the speed (30 mph or less 1, 35 3, 40 4);
  mixed traffic by the speed and the lanes (up to 25 mph: 2-3 lanes 1 on a residential street of under 3
  lanes or one without a centre line, else 2; 4-5 lanes 3; 6 or more 4. 30 mph: 2 or 3, then 4. 35 mph and
  over: 4). Rows in km/h end at 41, 51 and 61;
- the 2016 table for an unsignalized crossing with no refuge, where a way at LTS 2 or less (of any class)
  meets a main street of another name;
- the low-stress reach: Dijkstra by distance over every way a bicycle may use and over those at LTS 2 or
  less, a piece reached when both ends are within 1.25 times the shortest;
- PTAL, TfL: the walk, half the headway and the reliability allowance (bus 2, rail 0.75); 30 over that;
  per mode the best in full, the rest at half; the bands of the index.
The defaults where a street maps no speed or lanes are V164's road classes, as the app's noise uses them."""
import heapq, math, re
import access_reference as AR

ROADS = {'motorway': (100, 4), 'trunk': (90, 4), 'primary': (60, 2), 'secondary': (50, 2), 'tertiary': (50, 2),
         'unclassified': (40, 2), 'residential': (40, 2), 'living_street': (20, 1)}
XTAB = [[1, 2, 4], [1, 2, 4], [2, 3, 4], [3, 4, 4]]
PTAL_WALK = {'bus': 8, 'tram': 12, 'metro': 12, 'rail': 12, 'light': 12}
PTAL_K = {'bus': 2.0, 'tram': 0.75, 'metro': 0.75, 'rail': 0.75, 'light': 0.75}


def kmh(s):
    s = str(s or '').strip()
    if not s:
        return None
    m = re.match(r'^(\d+(?:\.\d+)?)\s*(mph|km/h|kmh|kph)?$', s, re.I)
    if m:
        v = float(m.group(1))
        return (v * 1.609344 if m.group(2) and m.group(2).lower() == 'mph' else v) if v > 0 else None
    low = s.lower()
    if low == 'walk':
        return 7.0
    if low == 'none':
        return 130.0
    if low == 'gb:nsl_single':
        return 96.6
    if low in ('gb:nsl_dual', 'gb:motorway'):
        return 112.7
    for suf, v in ((':living_street', 20.0), (':urban', 50.0), (':rural', 90.0), (':motorway', 120.0)):
        if low.endswith(suf):
            return v
    m = re.search(r':zone:?(\d+)$', s, re.I)
    return float(m.group(1)) if m else None


def oneway(t):
    return str(t.get('oneway', '')) in ('yes', '1', 'true', '-1') or t.get('junction') == 'roundabout'


def speed(t, base):
    v = kmh(t.get('maxspeed'))
    if v:
        return v, 'mapped'
    m = re.search(r':(\d+)$', str(t.get('zone:maxspeed', '')))
    if m:
        return float(m.group(1)), 'mapped as a zone'
    if base in ROADS:
        return float(ROADS[base][0]), 'assumed'
    return (20.0 if base == 'service' else (30.0 if base == 'track' else 40.0)), 'assumed'


def _int(v):
    try:
        return int(str(v).strip().split('.')[0]) if re.match(r'^\s*\d', str(v)) else None
    except ValueError:
        return None


def lanes(t, base):
    n, f, b = _int(t.get('lanes')), _int(t.get('lanes:forward')), _int(t.get('lanes:backward'))
    if n and 0 < n < 20:
        return n, 'mapped'
    if (f and f > 0) or (b and b > 0):
        return (f or 0) + (b or 0), 'mapped'
    if base in ROADS:
        L = ROADS[base][1]
        return (max(1, math.ceil(L / 2)) if oneway(t) else L), 'assumed'
    return (1 if oneway(t) else 2), 'assumed'


def facility(t):
    lane = False
    for k in ('cycleway', 'cycleway:both', 'cycleway:left', 'cycleway:right'):
        v = str(t.get(k, ''))
        if v in ('track', 'opposite_track'):
            return 'track'
        if v in ('lane', 'opposite_lane'):
            lane = True
    if t.get('shoulder:access:bicycle') == 'yes':
        lane = True
    return 'lane' if lane else ''


def lane_width(t):
    for k in ('cycleway:width', 'cycleway:both:width', 'cycleway:right:width', 'cycleway:left:width'):
        try:
            v = float(t.get(k))
        except (TypeError, ValueError):
            continue
        if 0 < v < 10:
            return v
    return None


def parking(t):
    def side(s):
        v = t.get('parking:' + s, t.get('parking:both'))
        if v is not None:
            if v in ('lane', 'street_side', 'on_kerb', 'half_on_kerb', 'shoulder', 'yes', 'parallel', 'diagonal', 'perpendicular'):
                return True
            if v in ('no', 'separate'):
                return False
        o = t.get('parking:lane:' + s, t.get('parking:lane:both'))
        if o is not None:
            if o in ('parallel', 'diagonal', 'perpendicular', 'marked', 'yes', 'inline', 'orthogonal'):
                return True
            if o in ('no', 'no_parking', 'no_stopping', 'fire_lane', 'separate'):
                return False
        return None
    return side('left'), side('right')


def row(v):
    return 0 if v <= 41 else (1 if v <= 51 else (2 if v <= 61 else 3))


def lts(t):
    """the level, 0 where a bicycle may not ride"""
    hw = str(t.get('highway', ''))
    base = re.sub(r'_link$', '', hw)
    bi = str(t.get('bicycle', ''))
    if bi in ('no', 'use_sidepath', 'dismount'):
        return 0
    if base == 'motorway' and bi not in ('yes', 'designated', 'permissive'):
        return 0
    if str(t.get('access', '')) in ('no', 'private') and bi not in ('yes', 'designated', 'permissive', 'destination'):
        return 0
    if hw == 'steps':
        return 0
    if hw in ('cycleway', 'path'):
        return 1
    if hw in ('footway', 'pedestrian', 'bridleway'):
        return 1 if bi in ('yes', 'designated', 'permissive') else 0
    if hw == 'track':
        return 2
    if t.get('motor_vehicle') == 'no' or t.get('motorcar') == 'no':
        return 1
    if hw == 'living_street' or t.get('bicycle_road') == 'yes' or t.get('cyclestreet') == 'yes':
        return 1
    fac = facility(t)
    if fac == 'track':
        return 1
    v, _ = speed(t, base)
    n, _ = lanes(t, base)
    ow = oneway(t)
    pd = n if ow else math.ceil(n / 2)
    if base == 'service' and row(v) == 0:
        return 2
    if fac == 'lane':
        pl, pr = parking(t)
        if pl is True or pr is True:
            return max(1 if pd <= 1 else 3, [1, 2, 3, 4][row(v)])
        w = lane_width(t)
        return max(1 if pd <= 1 else (2 if (pd == 2 and ow) else 3), [1, 1, 3, 4][row(v)], 1 if w is None else (1 if w >= 1.8 else 2))
    res = (base in ('residential', 'unclassified') or t.get('lane_markings') == 'no') and n <= 2
    r = row(v)
    if r == 0:
        return (1 if res else 2) if n <= 3 else (3 if n <= 5 else 4)
    if r == 1:
        return (2 if res else 3) if n <= 3 else 4
    return 4


def crossings(mv, W):
    """each junction where a way at LTS 2 or less meets a main street of another name: its level by the 2016
    table, controlled where a signal or an all-way stop is within 20 m"""
    inc = {}
    for wi, rec in enumerate(mv['w']):
        for nd in rec[1:]:
            inc.setdefault(nd, []).append(wi)
    sig = [c for c in mv.get('xs', []) if 's' in c[2] or 'a' in c[2]]
    out = []
    for nd, L in inc.items():
        if len(L) < 2:
            continue
        mains, minors = [], []
        for wi in dict.fromkeys(L):
            tg = mv['t'][mv['w'][wi][0]]
            if tg.get('highway') in ('trunk', 'primary', 'secondary', 'tertiary'):
                mains.append(wi)
            if 1 <= W[wi] <= 2:
                minors.append(wi)
        if not mains or not minors:
            continue
        x, z = mv['x'][nd], mv['z'][nd]
        ctl = any((c[0] - x) ** 2 + (c[1] - z) ** 2 <= 400 for c in sig)

        def nm(wi):
            return str(mv['t'][mv['w'][wi][0]].get('name', ''))
        lvs = {}
        for m in minors:
            best = 0
            crossed = False
            for wi in mains:
                if wi == m or (nm(wi) and nm(wi) == nm(m)):
                    continue
                tg = mv['t'][mv['w'][wi][0]]
                v, _ = speed(tg, tg['highway'])
                n, _ = lanes(tg, tg['highway'])
                best = max(best, XTAB[row(v)][0 if n <= 3 else (1 if n <= 5 else 2)])
                crossed = True
            if crossed:
                lvs[m] = best
        if not lvs:
            continue
        lv = max(lvs.values())
        out.append({'n': nd, 'lts': 1 if ctl else lv, 'ctl': ctl, 'minors': sorted(lvs), 'pen': (not ctl and lv > 2), 'lv': lv, 'lvs': lvs})
    return out


def _dij(n, adj, maxlv, seeds):
    D = [math.inf] * n
    h = []
    for i, d in seeds:
        if d < D[i]:
            D[i] = d
            heapq.heappush(h, (d, i))
    while h:
        d, u = heapq.heappop(h)
        if d > D[u]:
            continue
        for v, l, lv in adj[u]:
            if lv > maxlv:
                continue
            nd = d + l
            if nd < D[v]:
                D[v] = nd
                heapq.heappush(h, (nd, v))
    return D


def reach(mv, W, X, lot_ring):
    """the pieces (way, k) reached at low stress, with the two distances"""
    L = AR.Lot(ring=lot_ring) if lot_ring else AR.Lot()
    n = len(mv['x'])
    pen = {c['n']: c for c in X if c['pen']}
    adj = [[] for _ in range(n)]
    lvE = {}
    for wi, rec in enumerate(mv['w']):
        if W[wi] < 1:
            continue
        for k in range(2, len(rec)):
            a, b = rec[k - 1], rec[k]
            l = math.hypot(mv['x'][b] - mv['x'][a], mv['z'][b] - mv['z'][a])
            v = W[wi]
            for nd in (a, b):
                if nd in pen and wi in pen[nd]['lvs'] and pen[nd]['lvs'][wi] > 2:
                    v = max(v, pen[nd]['lvs'][wi])
            lvE[(wi, k)] = v
            adj[a].append((b, l, v))
            adj[b].append((a, l, v))
    seeds = [(i, L.dist(mv['x'][i], mv['z'][i])) for i in range(n) if L.dist(mv['x'][i], mv['z'][i]) <= 30]
    if not seeds:
        best = min((L.dist(mv['x'][i], mv['z'][i]), i) for i in range(n) if adj[i])
        seeds = [(best[1], best[0])]
    Da = _dij(n, adj, 4, seeds)
    Dl = _dij(n, adj, 2, seeds)

    def fine(x):
        return Dl[x] < math.inf and Dl[x] <= 1.25 * Da[x] + 0.5
    ok = set()
    for wi, rec in enumerate(mv['w']):
        for k in range(2, len(rec)):
            v = lvE.get((wi, k))
            if v is not None and 1 <= v <= 2 and fine(rec[k - 1]) and fine(rec[k]):
                ok.add((wi, k))
    return ok, Da, Dl


def band(ai):
    if not ai > 0:
        return '0'
    for t, b in ((2.5, '1a'), (5, '1b'), (10, '2'), (15, '3'), (20, '4'), (25, '5'), (40, '6a')):
        if ai <= t:
            return b
    return '6b'


def ptal(stops, iv):
    best = {}
    for s in stops:
        for md, lab in s['l']:
            lim = PTAL_WALK.get(md)
            if not lim or not s['t'] <= lim:
                continue
            k = md + '|' + lab
            if k not in best or s['t'] < best[k]['t']:
                best[k] = {'m': md, 'l': lab, 't': s['t'], 'stop': s['n']}
    modes = {}
    for k, b in best.items():
        h = iv.get(k)
        b['iv'] = h if h and h > 0 else None
        if b['iv']:
            b['edf'] = 30.0 / (b['t'] + 0.5 * b['iv'] + PTAL_K[b['m']])
            modes.setdefault(b['m'], []).append(b['edf'])
    ai = 0.0
    for E in modes.values():
        E = sorted(E, reverse=True)
        ai += E[0] + 0.5 * sum(E[1:])
    have = sum(1 for b in best.values() if b['iv'])
    return {'lines': best, 'have': have, 'ai': ai, 'band': band(ai), 'floor': 0 < have < len(best)}
