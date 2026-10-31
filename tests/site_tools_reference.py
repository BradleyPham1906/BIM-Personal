"""site_tools_reference.py -- V172's site analysis tools worked out again in Python, from the sources, not from the app.

Each function follows what reference/research-site-analysis-tools.md read at the source:
- the grid: the lot's extent and 100 m beyond it, 1 m cells, doubled while over 250,000 cells (the app's own rule,
  stated in its note); a cell belongs to an area when its centre is inside (even-odd), to a line or a point when its
  centre is within half a cell of it;
- distance: brute force, every cell centre to every source cell centre (Esri's Euclidean Distance measures centre
  to centre); Felzenszwalb and Huttenlocher's one-dimensional transform checked against brute force on samples;
- the ground's slope between the 5 m grid's points: the four nearest points' bilinear weights, those with no value
  left out and the rest renormalised; outside the points' span, no value;
- slope classes: a slope at a bound is in the class above it (V165's rule);
- the transforms: QGIS's fuzzy membership formulas (qgsalgorithmfuzzifyraster.cpp, read as text) -- Small
  1/(1+(x/f2)^f1), Large 1/(1+(x/f2)^-f1), Near 1/(1+f1(x-f2)^2), Linear between the thresholds -- each rescaled so
  its least and greatest values between the thresholds are the scale's ends (Esri, "How Rescale by Function works");
  the thresholds the data's least and greatest by default; Range of Classes and Unique Categories one to one;
- weighting: Multiplier, the transformed values times their weights added; Percent, added at their share, the result
  rescaled to the scale (Esri, "Implement the suitability modeling workflow", step 3);
- Locate: the documented simplification -- the 24 best cells at least half the region's side apart, each grown by
  its best neighbour sharing a side, the highest mean kept;
- the site capacity calculation: Chalfont Borough Zoning, section 440-17, as read (Zoneomics' copy)."""
import heapq, math
import numpy as np

MARGIN, MAXCELLS = 100, 250000
ACRE = 4046.8564224   # the international acre, m2
# Chalfont Borough Zoning, section 440-17 B, the open space ratios as read on 2026-10-27
CHALFONT = {'floodplain': 1.00, 'slope_lo': 15, 'slope_hi': 25, 'slope_a': 0.70, 'slope_b': 0.85, 'forest': 0.50,
            'forest_with': 0.80, 'pond': 1.00, 'waters': 1.00, 'wetland': 1.00}
# the app's working set for constraints and opportunities (V172), the registry's record app.synthesis
SYNTH = {'near_art': 30, 'front': 10, 'sunny': 6, 'shade': 2, 'green': 15}
LEVELS = 91


# ---------------------------------------------------------------- the grid
def grid(ring, margin=MARGIN):
    xs, zs = [p[0] for p in ring], [p[1] for p in ring]
    x0, x1, z0, z1 = min(xs) - margin, max(xs) + margin, min(zs) - margin, max(zs) + margin
    cell = 1
    while math.ceil((x1 - x0) / cell) * math.ceil((z1 - z0) / cell) > MAXCELLS:
        cell *= 2
    x0, z0 = math.floor(x0 / cell) * cell, math.floor(z0 / cell) * cell
    return {'x0': x0, 'z0': z0, 'cell': cell, 'nx': math.ceil((x1 - x0) / cell), 'nz': math.ceil((z1 - z0) / cell)}


def centres(G):
    cx = G['x0'] + (np.arange(G['nx']) + 0.5) * G['cell']
    cz = G['z0'] + (np.arange(G['nz']) + 0.5) * G['cell']
    return np.meshgrid(cx, cz)   # (nz, nx) each


def inside(G, ring):
    """even-odd: a centre is in when an odd number of the ring's crossings of its row lie strictly left of it, or it lies on one"""
    X, Z = centres(G)
    left = np.zeros(X.shape, dtype=int)
    on = np.zeros(X.shape, dtype=bool)
    n = len(ring)
    for k in range(n):
        a, b = ring[k], ring[(k + 1) % n]
        cross = (a[1] <= Z) != (b[1] <= Z)
        if not cross.any():
            continue
        with np.errstate(divide='ignore', invalid='ignore'):
            xc = a[0] + (Z - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
        left += (cross & (xc < X)).astype(int)
        on |= cross & (xc == X)
    return ((left % 2) == 1) | on


def near_edge(G, ring, eps=1e-6):
    """centres within eps of the ring's edges: where two correct rules may disagree"""
    X, Z = centres(G)
    m = np.zeros(X.shape, dtype=bool)
    for k in range(len(ring)):
        m |= seg_dist(X, Z, ring[k], ring[(k + 1) % len(ring)]) < eps
    return m


def seg_dist(X, Z, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dz * dz
    t = np.clip(((X - a[0]) * dx + (Z - a[1]) * dz) / L, 0, 1) if L > 0 else np.zeros(X.shape)
    return np.hypot(a[0] + t * dx - X, a[1] + t * dz - Z)


def stroke(G, segs):
    X, Z = centres(G)
    m = np.zeros(X.shape, dtype=bool)
    h = G['cell'] / 2
    for a, b in segs:
        m |= seg_dist(X, Z, a, b) <= h + 1e-9
    return m


def disc(G, p, r):
    X, Z = centres(G)
    return np.hypot(X - p[0], Z - p[1]) <= max(r, G['cell'] / 2) + 1e-9


# ---------------------------------------------------------------- distance
def dt1_brute(f):
    n = len(f)
    return [min((q - p) ** 2 + f[p] for p in range(n)) for q in range(n)]


def edt(G, src, where=None):
    """metres from each cell centre to the nearest source cell centre, brute force; None with no source.
    where: only those cells are measured (nan elsewhere), for a check that needs no more"""
    X, Z = centres(G)
    S = np.argwhere(src)
    if not len(S):
        return None
    sx, sz = X[S[:, 0], S[:, 1]], Z[S[:, 0], S[:, 1]]
    sel = np.flatnonzero(where.ravel()) if where is not None else np.arange(X.size)
    px, pz = X.ravel()[sel], Z.ravel()[sel]
    out = np.full(X.size, np.nan)
    step = max(1, 4000000 // max(1, len(sx)))
    for i in range(0, len(px), step):
        d2 = (px[i:i + step, None] - sx[None, :]) ** 2 + (pz[i:i + step, None] - sz[None, :]) ** 2
        out[sel[i:i + step]] = np.sqrt(d2.min(axis=1))
    return out.reshape(X.shape)


# ---------------------------------------------------------------- the ground's slope on the grid
def resample(G, D, slope):
    """D: the 5 m grid (x0, z0, cell, nx, nz); slope: its values (None where none), row by row"""
    X, Z = centres(G)
    S = np.array([np.nan if v is None else v for v in slope], dtype=float).reshape(D['nz'], D['nx'])
    gx, gz = (X - D['x0']) / D['cell'], (Z - D['z0']) / D['cell']
    out = np.full(X.shape, np.nan)
    ok = (gx >= 0) & (gz >= 0) & (gx <= D['nx'] - 1) & (gz <= D['nz'] - 1)
    i0 = np.minimum(D['nx'] - 2, np.floor(gx)).astype(int)
    j0 = np.minimum(D['nz'] - 2, np.floor(gz)).astype(int)
    fx, fz = gx - i0, gz - j0
    num, den = np.zeros(X.shape), np.zeros(X.shape)
    for dj, di, w in ((0, 0, (1 - fx) * (1 - fz)), (0, 1, fx * (1 - fz)), (1, 0, (1 - fx) * fz), (1, 1, fx * fz)):
        jj, ii = np.clip(j0 + dj, 0, D['nz'] - 1), np.clip(i0 + di, 0, D['nx'] - 1)
        v = S[jj, ii]
        good = np.isfinite(v)
        num += np.where(good, w * np.nan_to_num(v), 0)
        den += np.where(good, w, 0)
    with np.errstate(invalid='ignore', divide='ignore'):
        r = np.where(den > 1e-9, num / den, np.nan)
    out[ok] = r[ok]
    return out


def classes(v, uppers):
    """the class of each slope: the first whose upper bound is above it; a slope at a bound is in the class above"""
    out = np.full(v.shape, -1, dtype=int)
    good = np.isfinite(v)
    c = np.zeros(v.shape, dtype=int)
    for i, u in enumerate(uppers[:-1]):
        c += (v >= u).astype(int)
    out[good] = c[good]
    return out


# ---------------------------------------------------------------- the transforms
def fz_small(x, mid, sp):
    return 1 / (1 + (max(0.0, x) / mid) ** sp)


def fz_large(x, mid, sp):
    return 0.0 if x <= 0 else 1 / (1 + (x / mid) ** (-sp))


def fz_near(x, mid, sp):
    return 1 / (1 + sp * (x - mid) ** 2)


def transform(o, xs, sc=(1, 10)):
    """o: how, dir, lo, hi, mid, spread, breaks, vals; xs the criterion's values (nan none). Returns the values on the scale."""
    xs = np.asarray(xs, dtype=float)
    s0, s1 = sc
    how = o['how']
    if how == 'cats':
        vals = o['vals']
        return np.array([vals[int(round(x))] if np.isfinite(x) else np.nan for x in xs])
    if how == 'classes':
        br, vals = o['breaks'], o['vals']
        return np.array([vals[sum(1 for b in br if x >= b)] if np.isfinite(x) else np.nan for x in xs])
    fin = xs[np.isfinite(xs)]
    lo = o.get('lo') if o.get('lo') is not None else (fin.min() if len(fin) else 0.0)
    hi = o.get('hi') if o.get('hi') is not None else (fin.max() if len(fin) else 0.0)
    if not hi > lo:
        return np.where(np.isfinite(xs), (s0 + s1) / 2, np.nan)
    mid = o.get('mid') if o.get('mid') is not None else (lo + hi) / 2
    sp = o.get('spread') if o.get('spread') is not None else (4 / (hi - lo) ** 2 if how == 'near' else 5)
    f = {'small': lambda x: fz_small(x, mid, sp), 'large': lambda x: fz_large(x, mid, sp), 'near': lambda x: fz_near(x, mid, sp), 'linear': lambda x: x}[how]
    f0, f1 = f(lo), f(hi)
    fmin, fmax = min(f0, f1), max(f0, f1)
    if how == 'near' and lo <= mid <= hi:
        fmax = f(mid)
    out = []
    for x in xs:
        if not np.isfinite(x):
            out.append(np.nan)
            continue
        t = (f(min(hi, max(lo, x))) - fmin) / (fmax - fmin) if fmax > fmin else 0.5
        out.append(s1 - t * (s1 - s0) if (how == 'linear' and o.get('dir') == 'down') else s0 + t * (s1 - s0))
    return np.array(out)


def weigh(T, W, by, sc=(1, 10)):
    """T: transformed criteria (arrays), W: their weights; nan anywhere is nan in the result"""
    S = np.zeros(T[0].shape)
    for t, w in zip(T, W):
        S = S + (w / 100.0 if by == 'pct' else w) * t
    if by == 'pct':
        fin = S[np.isfinite(S)]
        if len(fin) and fin.max() > fin.min():
            S = sc[0] + (S - fin.min()) / (fin.max() - fin.min()) * (sc[1] - sc[0])
    return S


def quantised(S):
    """the value each cell keeps: its level between the least and greatest, of 91"""
    fin = S[np.isfinite(S)]
    lo, hi = fin.min(), fin.max()
    q = np.clip(np.round((S - lo) / (hi - lo) * (LEVELS - 1)) if hi > lo else 0 * S, 0, LEVELS - 1)
    return lo + (hi - lo) * q / (LEVELS - 1), lo, hi


# ---------------------------------------------------------------- Locate
def locate(V, ok, nx, nz, need):
    """V, ok: flat lists; the region's cells (sorted), its mean, the seeds' number"""
    C = sorted([k for k in range(nx * nz) if ok[k]], key=lambda k: (-V[k], k))
    sp = max(1.0, math.sqrt(need) / 2)
    seeds = []
    for a in C:
        if len(seeds) >= 24:
            break
        ai, aj = a % nx, a // nx
        if all((ai - s % nx) ** 2 + (aj - s // nx) ** 2 >= sp * sp for s in seeds):
            seeds.append(a)
    best = None
    for s in seeds:
        q, H, got, tot = {s}, [(-V[s], s)], [], 0.0
        while H and len(got) < need:
            _, k = heapq.heappop(H)
            got.append(k)
            tot += V[k]
            i, j = k % nx, k // nx
            for nb in ((k - 1) if i > 0 else -1, (k + 1) if i < nx - 1 else -1, (k - nx) if j > 0 else -1, (k + nx) if j < nz - 1 else -1):
                if nb >= 0 and nb not in q and ok[nb]:
                    q.add(nb)
                    heapq.heappush(H, (-V[nb], nb))
        if len(got) >= need:
            m = tot / len(got)
            if best is None or m > best[1] + 1e-12:
                best = (sorted(got), m)
    return (best[0], best[1], len(seeds)) if best else (None, None, len(seeds))


def connected(cells, nx):
    """whether cells (flat indices) are one region by sides"""
    S = set(cells)
    if not S:
        return False
    seen, st = set(), [next(iter(S))]
    while st:
        k = st.pop()
        if k in seen:
            continue
        seen.add(k)
        i = k % nx
        for nb in ((k - 1) if i > 0 else None, (k + 1) if i < nx - 1 else None, k - nx, k + nx):
            if nb is not None and nb in S and nb not in seen:
                st.append(nb)
    return len(seen) == len(S)


# ---------------------------------------------------------------- the site capacity calculation
def capacity(lot, flood, wetland, water, slope, forest, cell, R=CHALFONT):
    """each lot cell's resource by the highest ratio (the list's order among equals); forest with another resource takes
    forest_with. Returns (category index per cell, -1 none; the ratios in the app's order) -- the order: floodplain,
    wetland, pond or water, the upper slope class, the lower, forest with another, forest"""
    r = [R['floodplain'], R['wetland'], max(R['pond'], R['waters']), R['slope_b'], R['slope_a'], R['forest_with'], R['forest']]
    nz, nx = lot.shape
    cat = np.full(lot.shape, -1, dtype=int)
    for j in range(nz):
        for i in range(nx):
            if not lot[j, i]:
                continue
            s = slope[j, i]
            has = [flood[j, i], wetland[j, i], water[j, i], np.isfinite(s) and s >= R['slope_hi'] - 1e-9,
                   np.isfinite(s) and R['slope_lo'] - 1e-9 <= s < R['slope_hi'] - 1e-9, False, forest[j, i]]
            if has[6] and any(has[:5]):
                has[5], has[6] = True, False
            best, bv = -1, -1.0
            for k in range(7):
                if has[k] and r[k] > bv + 1e-12:
                    best, bv = k, r[k]
            cat[j, i] = best
    return cat, r


def capacity_numbers(cat, r, total, less, cell, density=None, imperv=None):
    a2 = cell * cell
    land = sum(int((cat == k).sum()) * a2 for k in range(7))
    prot = sum(int((cat == k).sum()) * a2 * r[k] for k in range(7))
    base = max(0.0, total - less)
    net = max(0.0, base - prot)
    out = {'base': base, 'land': land, 'prot': prot, 'net': net}
    if density is not None:
        out['units'] = int(math.floor(net / ACRE * density + 1e-9))   # "do not round up"
    if imperv is not None:
        out['imperv'] = net * imperv / 100
    return out
