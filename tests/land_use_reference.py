"""land_use_reference.py -- V168's methods worked out again in Python, from their sources and from the
fixture's own coordinates, for the suite to hold the app to.

- The crosswalk: OpenStreetMap's tags to LBCS's activities, as the research checked it against LBCS's
  descriptions (reference/plan-v167-v170.md, "V168's second round at the source"), and the order in
  which a feature's tags are read.
- The land use mix: a 5 m grid over the 400 m square, each cell a building's own use, else the smallest
  area over it, else grass's; the shares of 1000 to 8000; Shannon's H over them divided by ln N (Cervero,
  as Chen and Song quote it).
- Spacematrix (Buildings and Cities' box): GSI the ground floors over the land, FSI the floor area,
  OSR (1 - GSI) / FSI (papers citing the book), L FSI / GSI; the footprints cut to the box
  (Sutherland and Hodgman); the storeys from building:levels (less building:min_level), else the height
  over 3 m, at least one (momepy's floor area, with V168's floor of one).
- 3-30-300 (Browning et al., 2024): the trees seen from the site's centre by 180 sight lines at eye
  height (V164's), within 100 m; the canopy on a 2 m grid of the 500 m circle, cut to the context's
  square; the walk to a public green space of 0.5 ha or more along V161's walk times.
- The zoning: each district's share of the zoned ground in the square.
Point in polygon is the even-odd crossing rule the app uses (access_reference.pip)."""
import math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import land_use_fixture as FX     # noqa: E402
import site_analysis_fixture as SFX   # noqa: E402
from access_reference import pip   # noqa: E402

# ---- LBCS (APA's workbook and activity page, read 2026-10-18) ----
FAMILIES = [(1000, 'Residential activities', 'FFFF00'), (2000, 'Shopping, business, or trade', 'FF0000'),
            (3000, 'Industrial, manufacturing, and waste-related', 'A020F0'), (4000, 'Social, institutional, or infrastructure-related', '0000FF'),
            (5000, 'Travel or movement', 'BEBEBE'), (6000, 'Mass assembly of people', '2F4F4F'), (7000, 'Leisure', '90EE90'),
            (8000, 'Natural resources-related', '228B22'), (9000, 'No human activity or unclassifiable', 'FFFFFF')]

# ---- the crosswalk, family by family, with the description that puts each tag there ----
XW = {}
for c, tags in (
    (1000, 'landuse=residential building=house building=apartments building=residential building=detached building=semidetached_house building=terrace '
           'building=bungalow building=dormitory building=hotel tourism=hotel tourism=motel tourism=guest_house tourism=hostel amenity=nursing_home '
           'social_facility=group_home'),                      # 1100 household living, 1200 transient living, 1300 institutional living
    (2000, 'landuse=commercial landuse=retail shop=* office=* building=commercial building=retail building=office building=supermarket building=kiosk '
           'amenity=restaurant amenity=cafe amenity=fast_food amenity=pub amenity=bar amenity=bank amenity=marketplace'),
    (3000, 'landuse=industrial landuse=construction landuse=landfill building=industrial building=warehouse building=factory man_made=works '
           'man_made=wastewater_plant amenity=recycling'),     # 3200 waste, 3300 construction
    (4000, 'landuse=education landuse=institutional landuse=civic_admin landuse=cemetery landuse=military landuse=school amenity=school '
           'amenity=university amenity=college amenity=kindergarten amenity=hospital amenity=clinic amenity=doctors amenity=library amenity=police '
           'amenity=fire_station amenity=courthouse amenity=post_office amenity=prison amenity=grave_yard building=school building=university '
           'building=college building=kindergarten building=hospital building=civic building=government building=public power=substation'),   # 4600 interment, 4700 military
    (5000, 'landuse=railway landuse=garages amenity=parking building=garage building=garages building=parking industrial=port landuse=port '
           'aeroway=aerodrome aeroway=apron'),                 # 5210 parking, 5400 rail, 5520 ports
    (6000, 'amenity=bus_station building=train_station building=transportation aeroway=terminal leisure=stadium building=stadium amenity=theatre '
           'amenity=cinema amenity=arts_centre amenity=community_centre amenity=place_of_worship amenity=townhall landuse=religious landuse=churchyard '
           'building=church building=cathedral building=chapel building=mosque building=synagogue building=temple tourism=museum tourism=gallery '
           'tourism=zoo tourism=aquarium'),                    # 6100 terminals, 6200 stadiums, 6300 theatres, 6600 assembly, 6700 museums
    (7000, 'leisure=park leisure=playground leisure=pitch leisure=sports_centre leisure=golf_course leisure=garden leisure=track leisure=marina '
           'landuse=recreation_ground landuse=village_green tourism=theme_park tourism=camp_site'),
    (8000, 'landuse=farmland landuse=field landuse=farmyard landuse=orchard landuse=vineyard landuse=allotments landuse=plant_nursery '
           'landuse=greenhouse_horticulture landuse=aquaculture landuse=meadow landuse=forest landuse=quarry'),   # 8100 farming, 8300 pasture, 8400 logging, 8500 quarrying
    (9000, 'natural=wood natural=scrub natural=grassland landuse=brownfield landuse=greenfield landuse=grass landuse=flowerbed')):
    for t in tags.split():
        XW[t] = c
WEAK = ['landuse=grass', 'landuse=flowerbed']
BKEYS = ['amenity', 'shop', 'office', 'tourism', 'leisure', 'social_facility', 'building', 'landuse', 'man_made', 'power', 'aeroway', 'industrial']
AKEYS = ['industrial', 'amenity', 'leisure', 'tourism', 'aeroway', 'landuse', 'natural', 'man_made', 'power', 'railway']


def classify(tags, building):
    for k in (BKEYS if building else AKEYS):
        v = tags.get(k)
        if v in (None, '', 'no'):
            continue
        v = str(v)
        if k + '=' + v in XW:
            return {'c': XW[k + '=' + v], 'tag': k + '=' + v, 'weak': (k + '=' + v) in WEAK}
        if k + '=*' in XW:
            return {'c': XW[k + '=*'], 'tag': k + '=' + v, 'weak': False}
    return None


# ---- geometry ----
def area(P):
    a = 0.0
    for i in range(len(P)):
        j = (i + 1) % len(P)
        a += P[i][0] * P[j][1] - P[j][0] * P[i][1]
    return abs(a) / 2


def clip(P, x0, z0, x1, z1):
    def cut(L, inside, isect):
        out = []
        for i in range(len(L)):
            a, b = L[i], L[(i + 1) % len(L)]
            ia, ib = inside(a), inside(b)
            if ia:
                out.append(a)
            if ia != ib:
                out.append(isect(a, b))
        return out
    R = cut(P, lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (x0 - a[0]) / (b[0] - a[0]) * (b[1] - a[1])))
    if R:
        R = cut(R, lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (x1 - a[0]) / (b[0] - a[0]) * (b[1] - a[1])))
    if R:
        R = cut(R, lambda p: p[1] >= z0, lambda a, b: (a[0] + (z0 - a[1]) / (b[1] - a[1]) * (b[0] - a[0]), z0))
    if R:
        R = cut(R, lambda p: p[1] <= z1, lambda a, b: (a[0] + (z1 - a[1]) / (b[1] - a[1]) * (b[0] - a[0]), z1))
    return R


def bbox(rings):
    xs = [p[0] for r in rings for p in r]
    zs = [p[1] for r in rings for p in r]
    return min(xs), min(zs), max(xs), max(zs)


# ---- the fixture's land, as the app reads it from OpenStreetMap ----
def _ring(pts):
    return [(float(p[0]), float(p[1])) for p in pts]


def areas():
    """[(key, tags, outer, holes, area, cls)] in the app's order: Mill Park and the meadow first (V164's), then the land"""
    A = []
    for i, t, pts in [(5001, {'leisure': 'park', 'name': 'Mill Park'}, SFX.PARK), (6001, {'landuse': 'meadow'}, SFX.MEADOW)] + FX.AREAS:
        kind = 'green' if (t.get('leisure') == 'park' or t.get('landuse') in ('grass', 'forest', 'meadow', 'recreation_ground', 'village_green') or
                           t.get('natural') in ('wood', 'scrub', 'grassland')) else 'landuse'
        o = _ring(pts)
        A.append({'key': kind + ':way:' + str(i), 'tags': t, 'outer': [o], 'holes': [], 'area': area(o), 'cls': classify(t, False), 'name': t.get('name', '')})
    for i, t, outer, inner in FX.MP_AREAS:
        o, H = _ring(outer), [_ring(r) for r in inner]
        A.append({'key': 'landuse:relation:' + str(i), 'tags': t, 'outer': [o], 'holes': H, 'area': area(o) - sum(area(h) for h in H), 'cls': classify(t, False), 'name': t.get('name', '')})
    return A


def storeys(t, h, mn):
    lv = _num(t.get('building:levels'))
    if lv is not None and 0 < lv < 300:
        ml = _num(t.get('building:min_level'))
        return max(0.0, lv - (ml if ml is not None and ml > 0 else 0)), 'levels'
    return max(1, math.floor((h - mn) / 3.0 + 1e-9)), 'height'


def _num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def buildings():
    """[(fp, holes, tags, h, min, storeys, from, ground, area, cls, whole)]: V164's five, the forty sheds, then V168's"""
    B = []

    def add(i, t, pts, inner=(), h=None, mn=0.0, whole=None):
        fp = _ring(pts)
        H = _num(t.get('height')) if h is None else h
        s, fr = storeys(t, H, mn)
        holes = [_ring(r) for r in inner]
        a = area(fp) - sum(area(r) for r in holes)
        B.append({'fp': fp, 'holes': holes, 'tags': t, 'h': H, 'min': mn, 's': s, 'from': fr, 'ground': not (mn > 0), 'area': a,
                  'cls': classify(t, True), 'whole': whole or ('way:' + str(i))})
    for i, nm, x0, z0, x1, z1, h, extra in SFX.BUILDINGS:
        t = {'building': 'yes', 'name': nm, 'height': str(h)}
        t.update(extra)
        add(i, t, SFX.box(x0, z0, x1, z1))
    for k, (x, z) in enumerate(SFX.FAR):
        add(300 + k, {'building': 'shed', 'height': '4'}, SFX.box(x, z, x + 6, z + 6))
    for i, t, pts, inner in FX.BUILDINGS:
        add(i, t, pts, inner)
    for i, t, pts in FX.PARTS:   # the outline's parts stand for it
        add(i, t, pts, mn=_num(t.get('min_height')) or 0.0, whole='way:' + str(FX.PART_HOUSE[0]))
    i, t, outer, inner = FX.COURT
    add(i, t, outer, inner, whole='relation:' + str(i))
    return B


def trees():
    """[(x, z, crown radius, height)]: V164's three, then V168's"""
    T = [(x, z, 4.8 / 2, 8.0) for x, z in SFX.TREES]
    for i, t, x, z in FX.TREES:
        h = float(t['height'])
        cd = float(t['diameter_crown']) if 'diameter_crown' in t else round(h * 0.6 * 100) / 100
        T.append((float(x), float(z), max(0.5, cd / 2), h))
    return T


# ---- the square, the grid, the mix ----
def window(c=FX.SITE, w=400.0):
    h = w / 2
    return c[0] - h, c[1] - h, c[0] + h, c[1] + h


def raster(A, B, c=FX.SITE, w=400.0, rc=5.0):
    x0, z0, x1, z1 = window(c, w)
    nx = int(round(w / rc))
    R = [0] * (nx * nx)
    rank = [math.inf] * (nx * nx)

    def lay(cls, tier, ar, inside, bb):
        i0, i1 = max(0, math.floor((bb[0] - x0) / rc)), min(nx - 1, math.floor((bb[2] - x0) / rc))
        j0, j1 = max(0, math.floor((bb[1] - z0) / rc)), min(nx - 1, math.floor((bb[3] - z0) / rc))
        r = tier * 1e12 + ar
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                x, z, k = x0 + (i + 0.5) * rc, z0 + (j + 0.5) * rc, j * nx + i
                if r < rank[k] and inside(x, z):
                    rank[k], R[k] = r, cls
    for b in B:
        if b['cls'] and b['ground']:
            lay(b['cls']['c'], 0, b['area'], lambda x, z, b=b: pip(x, z, b['fp']) and not any(pip(x, z, h) for h in b['holes']), bbox([b['fp']]))
    for a in A:
        if a['cls']:
            lay(a['cls']['c'], 2 if a['cls']['weak'] else 1, a['area'],
                lambda x, z, a=a: any(pip(x, z, o) for o in a['outer']) and not any(pip(x, z, h) for h in a['holes']), bbox(a['outer']))
    return R


def mix(A, B, N=8, **kw):
    R = raster(A, B, **kw)
    cnt, none, un = {}, 0, 0
    for c in R:
        if not c:
            un += 1
        elif c == 9000:
            none += 1
        else:
            cnt[c] = cnt.get(c, 0) + 1
    n = sum(cnt.values())
    sh = [(c, cnt[c], cnt[c] / n) for c in sorted(cnt)]
    H = -sum(p * math.log(p) for _, _, p in sh)
    return {'cnt': cnt, 'n': n, 'none': none, 'un': un, 'tot': len(R), 'H': H, 'ix': H / math.log(N) if N >= 2 and n else None, 'sh': sh}


# ---- Spacematrix ----
def area_in(b, x0, z0, x1, z1):
    R = clip(b['fp'], x0, z0, x1, z1)
    a = area(R) if len(R) >= 3 else 0.0
    for h in b['holes']:
        Q = clip(h, x0, z0, x1, z1)
        if len(Q) >= 3:
            a -= area(Q)
    return max(0.0, a)


def form(B, x0, z0, x1, z1):
    A = (x1 - x0) * (z1 - z0)
    gf = fa = 0.0
    n = 0
    for b in B:
        a = area_in(b, x0, z0, x1, z1)
        if not a > 0:
            continue
        n += 1
        if b['ground']:
            gf += a
        fa += a * b['s']
    gsi, fsi = gf / A, fa / A
    return {'gsi': gsi, 'fsi': fsi, 'osr': (1 - gsi) / fsi if fsi > 0 else None, 'l': fa / gf if gf > 0 else None, 'n': n, 'gf': gf, 'fa': fa}


def grain(B, c=FX.SITE, w=400.0):
    x0, z0, x1, z1 = window(c, w)
    seen, n, ar, lev, hgt = set(), 0, 0.0, 0, 0
    for b in B:
        cx = sum(p[0] for p in b['fp']) / len(b['fp'])
        cz = sum(p[1] for p in b['fp']) / len(b['fp'])
        if cx < x0 or cx > x1 or cz < z0 or cz > z1:
            continue
        if b['from'] == 'levels':
            lev += 1
        else:
            hgt += 1
        if b['ground']:
            ar += b['area']
        if b['whole'] not in seen:
            seen.add(b['whole'])
            n += 1
    return {'n': n, 'ha': n / (w * w / 10000), 'mean': ar / n if n else 0, 'lev': lev, 'hgt': hgt}


# ---- 3-30-300 ----
def reach(lot=((10, -40), (50, -40), (50, -10), (10, -10)), radius=300.0):
    xs, zs = [p[0] for p in lot], [p[1] for p in lot]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
    h = max(max(xs) - min(xs), max(zs) - min(zs)) / 2 + radius
    return cx - h, cz - h, cx + h, cz + h


def canopy(T, A, c=FX.SITE, R=500.0, rc=2.0, re=None):
    cx, cz = c
    n = math.ceil(R / rc)
    N2, gx0, gz0 = 2 * n, cx - n * rc, cz - n * rc
    mark = bytearray(N2 * N2)

    def span(a, b, g0):
        return max(0, math.floor((a - g0) / rc)), min(N2 - 1, math.floor((b - g0) / rc))
    for x, z, r, _ in T:
        I, J = span(x - r, x + r, gx0), span(z - r, z + r, gz0)
        for i in range(I[0], I[1] + 1):
            for j in range(J[0], J[1] + 1):
                X, Z = gx0 + (i + 0.5) * rc, gz0 + (j + 0.5) * rc
                if (X - x) ** 2 + (Z - z) ** 2 <= r * r:
                    mark[j * N2 + i] = 1
    for a in A:
        t = a['tags']
        if not (t.get('natural') == 'wood' or t.get('landuse') == 'forest'):
            continue
        b = bbox(a['outer'])
        I, J = span(b[0], b[2], gx0), span(b[1], b[3], gz0)
        for i in range(I[0], I[1] + 1):
            for j in range(J[0], J[1] + 1):
                k = j * N2 + i
                if not mark[k] and any(pip(gx0 + (i + 0.5) * rc, gz0 + (j + 0.5) * rc, o) for o in a['outer']):
                    mark[k] = 1
    cnt = can = 0
    for i in range(N2):
        X = gx0 + (i + 0.5) * rc
        for j in range(N2):
            Z = gz0 + (j + 0.5) * rc
            if (X - cx) ** 2 + (Z - cz) ** 2 > R * R:
                continue
            if re and (X < re[0] or X > re[2] or Z < re[1] or Z > re[3]):
                continue
            cnt += 1
            can += mark[j * N2 + i]
    full = max(0.0, min(cx - re[0], re[2] - cx, cz - re[1], re[3] - cz)) if re else R
    return {'share': can / cnt if cnt else None, 'cells': cnt, 'can': can, 'full': min(R, full), 'clipped': bool(re) and full < R}


def ray_hit(ox, oz, dx, dz, P, mx):
    best = mx
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        ex, ez = b[0] - a[0], b[1] - a[1]
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = ((a[0] - ox) * ez - (a[1] - oz) * ex) / den
        s = ((a[0] - ox) * dz - (a[1] - oz) * dx) / den
        if t > 0.01 and 0 <= s <= 1 and t < best:
            best = t
    return best


def seen(B, T, c=FX.SITE, see=100.0, eye=1.6):
    """the trees met first by 180 sight lines at eye height: the trees' crowns as V164's octagons"""
    obs = [('b', b['fp'], b['h'], None) for b in B if b['h'] > 0]
    for k, (x, z, r, h) in enumerate(T):
        rr = max(1.0, r)
        obs.append(('t', [(x + rr * math.cos(q * math.pi / 4), z + rr * math.sin(q * math.pi / 4)) for q in range(8)], h, k))
    use = [o for o in obs if o[2] > eye and not pip(c[0], c[1], o[1])]
    got = []
    for k in range(180):
        a = math.radians(2 * k)
        dx, dz, d, hit = math.sin(a), -math.cos(a), see, None
        for o in use:
            t = ray_hit(c[0], c[1], dx, dz, o[1], d)
            if t < d:
                d, hit = t, o
        if hit and hit[0] == 't' and hit[3] not in got:
            got.append(hit[3])
    return got


def greens(A, m2=5000.0):
    G = []
    for a in A:
        t = a['tags']
        if (t.get('leisure') in ('park', 'garden') or t.get('landuse') in ('recreation_ground', 'village_green')) and t.get('access') not in ('private', 'no'):
            G.append(dict(a, big=a['area'] >= m2 - 0.001))
    return G


def walk_to(segs, v, g):
    """to a point of the network inside it, or to its edge every 15 m from the nearest piece within 60 m"""
    pcs = []
    for s in segs:
        for i in range(4, len(s) - 2, 3):
            pcs.append((s[i - 3], s[i - 2], s[i - 1], s[i], s[i + 1], s[i + 2]))
    best = None
    for p in pcs:
        for q in ((p[0], p[1], p[2]), (p[3], p[4], p[5])):
            if any(pip(q[0], q[1], o) for o in g['outer']) and not any(pip(q[0], q[1], h) for h in g['holes']):
                if best is None or q[2] * v < best:
                    best = q[2] * v

    def near(x, z):
        bd, bt = math.inf, None
        for p in pcs:
            dx, dz = p[3] - p[0], p[4] - p[1]
            l2 = dx * dx + dz * dz
            u = max(0.0, min(1.0, ((x - p[0]) * dx + (z - p[1]) * dz) / l2)) if l2 > 1e-12 else 0.0
            px, pz = p[0] + u * dx, p[1] + u * dz
            d = math.hypot(x - px, z - pz)
            if d <= 60 and d < bd:
                bd, bt = d, p[2] + u * (p[5] - p[2])
        return None if bt is None else bt * v + bd
    for r in g['outer']:
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            n = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / 15))
            for k in range(n):
                w = near(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                if w is not None and (best is None or w < best):
                    best = w
    return best


# ---- the zoning around ----
def zoning(c=FX.SITE, w=400.0):
    x0, z0, x1, z1 = window(c, w)
    by, lot = {}, None
    for zn, pts, far in FX.DISTRICTS:
        P = _ring(pts)
        if pip(c[0], c[1], P) and lot is None:
            lot = zn
        Q = clip(P, x0, z0, x1, z1)
        a = area(Q) if len(Q) >= 3 else 0.0
        if a > 0:
            by[zn] = by.get(zn, 0.0) + a
    tot = sum(by.values())
    return {'lot': lot, 'share': {k: v / tot for k, v in by.items()}, 'order': sorted(by, key=lambda k: -by[k])}


def rgba(c, tr):
    a = (c[3] if len(c) > 3 else 255) / 255 * (1 - tr / 100)
    a = max(0, min(1, round(a * 1000) / 1000))
    return 'rgba(%d,%d,%d,%s)' % (round(c[0]), round(c[1]), round(c[2]), ('%g' % a))
