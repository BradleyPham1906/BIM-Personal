"""access_reference.py -- the V161 walk times, worked out again here, another way, from the fixture.

The app cuts the edges beside the lot every 5 m and walks from there with a binary heap. Here the
same model is worked out with a finer net (every half metre), Python's heapq, numpy for the nearest
edge, and parks' edges sampled every metre, so the two must agree to a fraction of a minute:
- a way's class for walking, by OpenStreetMap's conventions (motorways, foot=no and private ways out,
  unless foot=yes; sidewalks and crossings walked);
- the walk leaves the lot anywhere: every point of the ground network within 30 m of the lot is a
  start, its time the straight step from the lot line at 80 m a minute; steps at half speed;
- a place's time: the network's time where it meets it, plus the straight step to it;
- the intersections, as LEED ND counts them: dead ends taken off until none is left, corners within
  12 m merged, those within 400 m of the lot."""
import heapq, math
import numpy as np
import access_fixture as FX

V, F, MAXT, STEPS, CUT = 80.0, 30.0, 20.0, 2.0, 0.5
CLS = {'trunk': 'a', 'trunk_link': 'a', 'primary': 'a', 'primary_link': 'a', 'secondary': 'c', 'secondary_link': 'c', 'tertiary': 'c', 'tertiary_link': 'c',
       'residential': 'l', 'unclassified': 'l', 'living_street': 'l', 'road': 'l', 'service': 's',
       'pedestrian': 'p', 'footway': 'p', 'path': 'p', 'cycleway': 'p', 'steps': 'p', 'bridleway': 'p', 'track': 'p', 'corridor': 'p', 'platform': 'p'}


def walk_class(tg, honour_foot=True):
    c = CLS.get(tg.get('highway'))
    if not c:
        return ''
    foot = tg.get('foot', '') if honour_foot else ''
    if foot in ('no', 'private', 'use_sidepath'):
        return ''
    if tg.get('access') in ('no', 'private') and foot not in ('yes', 'designated', 'permissive', 'destination'):
        return ''
    if tg.get('motorroad') == 'yes' and foot not in ('yes', 'designated', 'permissive'):
        return ''
    if c == 'p' and (tg.get('footway') or tg.get('path') or tg.get('cycleway') or '') in ('sidewalk', 'crossing', 'traffic_island'):
        return 'w'
    return c


def seg_dist(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    l2 = dx * dx + dz * dz
    t = 0 if l2 < 1e-12 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / l2))
    return math.hypot(px - ax - t * dx, pz - az - t * dz)


def pip(x, z, poly):
    inside, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi:
            inside = not inside
        j = i
    return inside


class Lot:
    def __init__(self, ring=None, pt=(0.0, 0.0)):
        self.ring, self.pt = ring, pt

    def dist(self, x, z):
        if not self.ring:
            return math.hypot(x - self.pt[0], z - self.pt[1])
        if pip(x, z, self.ring):
            return 0.0
        n = len(self.ring)
        return min(seg_dist(x, z, *self.ring[i], *self.ring[(i + 1) % n]) for i in range(n))

    def seg(self, ax, az, bx, bz):
        """the least distance from segment ab to the lot (0 where it touches); sampled finely"""
        L = math.hypot(bx - ax, bz - az)
        k = max(1, int(math.ceil(L / 0.25)))
        return min(self.dist(ax + (bx - ax) * i / k, az + (bz - az) * i / k) for i in range(k + 1))

    def area(self):
        r = self.ring
        return abs(sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))) / 2

    def perim(self):
        r = self.ring
        return sum(math.hypot(r[(i + 1) % len(r)][0] - r[i][0], r[(i + 1) % len(r)][1] - r[i][1]) for i in range(len(r)))


class Ref:
    """the network and its walk times, for a lot; opts break one rule, to show the suite would see it"""
    def __init__(self, lot, walk_motorways=False, private_walkable=False, steps_slow=True, seed_bridges=False, honour_foot=True):
        self.lot = lot
        X = dict(FX.NET.xy)
        nxt = max(X) + 1
        E = []          # (a, b, length, factor, class, lev, way id, tags)
        ground = set()
        for w in FX.NET.ways:
            tg = w['tags']
            c = walk_class(tg, honour_foot)
            if walk_motorways and tg.get('highway') == 'motorway':
                c = 'a'
            if private_walkable and tg.get('access') == 'private':
                c = CLS[tg['highway']]
            if not c:
                continue
            lev = tg.get('bridge', 'no') != 'no' or tg.get('tunnel', 'no') != 'no'
            m = STEPS if (tg.get('highway') == 'steps' and steps_slow) else 1.0
            ids = w['ids']
            if not lev or seed_bridges:
                ground.update(ids)
            for a, b in zip(ids, ids[1:]):
                (ax, az), (bx, bz) = X[a], X[b]
                L = math.hypot(bx - ax, bz - az)
                if (not lev or seed_bridges) and lot.seg(ax, az, bx, bz) <= F:
                    k = max(1, int(math.ceil(L / CUT)))
                    chain = [a]
                    for i in range(1, k):
                        X[nxt] = (ax + (bx - ax) * i / k, az + (bz - az) * i / k)
                        ground.add(nxt)
                        chain.append(nxt)
                        nxt += 1
                    chain.append(b)
                    for p, q in zip(chain, chain[1:]):
                        E.append((p, q, math.hypot(X[q][0] - X[p][0], X[q][1] - X[p][1]), m, c, lev and not seed_bridges, w['id'], tg))
                else:
                    E.append((a, b, L, m, c, lev, w['id'], tg))
        self.X, self.E = X, E
        adj = {}
        for a, b, L, m, c, lev, wid, tg in E:
            cost = L * m / V
            adj.setdefault(a, []).append((b, cost))
            adj.setdefault(b, []).append((a, cost))
        D = {}
        hp = []
        for n in ground:
            d = lot.dist(*X[n])
            if d <= F:
                t = d / V
                if t < D.get(n, 1e18):
                    D[n] = t
                    heapq.heappush(hp, (t, n))
        if not D:   # no street within 30 m: from where the nearest comes nearest
            best = None
            for a, b, L, m, c, lev, wid, tg in E:
                if lev:
                    continue
                k = max(1, int(math.ceil(L / 0.25)))
                for i in range(k + 1):
                    x = X[a][0] + (X[b][0] - X[a][0]) * i / k
                    z = X[a][1] + (X[b][1] - X[a][1]) * i / k
                    d = lot.dist(x, z)
                    if best is None or d < best[0]:
                        best = (d, a, b, i / k, L, m)
            d, a, b, f, L, m = best
            for n, s in ((a, f * L), (b, (1 - f) * L)):
                t = d / V + s * m / V
                if t < D.get(n, 1e18):
                    D[n] = t
                    heapq.heappush(hp, (t, n))
            self.far = d
        else:
            self.far = None
        done = set()
        while hp:
            t, u = heapq.heappop(hp)
            if u in done:
                continue
            done.add(u)
            for v, c in adj.get(u, []):
                if t + c < D.get(v, 1e18):
                    D[v] = t + c
                    heapq.heappush(hp, (t + c, v))
        self.D = D
        A = np.array([X[e[0]] for e in E])
        B = np.array([X[e[1]] for e in E])
        self.A, self.B = A, B
        self.Lm = np.array([e[2] for e in E])
        self.Ta = np.array([D.get(e[0], 1e18) for e in E])
        self.Tb = np.array([D.get(e[1], 1e18) for e in E])
        self.M = np.array([e[3] for e in E])
        self.lev = np.array([e[5] for e in E])

    def point(self, x, z, maxR=300.0, exclude=None):
        """the walk time to a point: the network's where it meets the nearest edge, plus the step"""
        d = self.B - self.A
        l2 = (d * d).sum(1)
        t = np.clip(((x - self.A[:, 0]) * d[:, 0] + (z - self.A[:, 1]) * d[:, 1]) / np.maximum(l2, 1e-12), 0, 1)
        px = self.A[:, 0] + t * d[:, 0]
        pz = self.A[:, 1] + t * d[:, 1]
        dist = np.hypot(px - x, pz - z)
        i = int(np.argmin(dist))
        if dist[i] > maxR:
            return None
        s = t[i] * self.Lm[i]
        tt = min(self.Ta[i] + s * self.M[i] / V, self.Tb[i] + (self.Lm[i] - s) * self.M[i] / V)
        if not self.lev[i]:
            dl = self.lot.dist(px[i], pz[i])
            if dl <= F:
                tt = min(tt, dl / V)
        order = np.argsort(dist)
        return {'t': tt + dist[i] / V, 'd': float(dist[i]), 'gap': float(dist[order[1]] - dist[i])}

    def ring_time(self, ring, step=1.0, maxR=60.0):
        """a park's: to the nearest point of its edge"""
        best = None
        for (ax, az), (bx, bz) in zip(ring, ring[1:] + ring[:1]):
            L = math.hypot(bx - ax, bz - az)
            k = max(1, int(math.ceil(L / step)))
            for i in range(k):
                r = self.point(ax + (bx - ax) * i / k, az + (bz - az) * i / k, maxR)
                if r and (best is None or r['t'] < best):
                    best = r['t']
        return best

    def band_lengths(self):
        """metres of streets and paths (not sidewalks or crossings) within 5, 10, 15 and 20 minutes"""
        out = [0.0, 0.0, 0.0, 0.0]
        for (a, b, L, m, c, lev, wid, tg), ta, tb in zip(self.E, self.Ta, self.Tb):
            if c == 'w':
                continue
            prev = 0.0
            for k, T in enumerate((5, 10, 15, 20)):
                cc = L * m / V
                la = min(L, (T - ta) / cc * L) if ta <= T else 0.0
                lb = min(L, (T - tb) / cc * L) if tb <= T else 0.0
                l = min(L, la + lb)
                out[k] += l - prev
                prev = l
        return out

    def intersections(self, R=400.0, merge=12.0):
        """LEED ND's count: streets and paths, not sidewalks, crossings or service roads, nor areas"""
        adj = {}
        for a, b, L, m, c, lev, wid, tg in self.E:
            if c in ('a', 'c', 'l', 'p') and tg.get('area') != 'yes' and a != b:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
        deg = {n: len(v) for n, v in adj.items()}
        alive = {n: list(v) for n, v in adj.items()}
        Q = [n for n, d in deg.items() if d == 1]
        while Q:
            u = Q.pop()
            if deg.get(u) != 1:
                continue
            v = alive[u][0]
            alive[u] = []
            deg[u] = 0
            alive[v].remove(u)
            deg[v] -= 1
            if deg[v] == 1:
                Q.append(v)
        C = [n for n, d in deg.items() if d >= 3 and self.lot.dist(*self.X[n]) <= R + merge]
        seen, pts = set(), []
        for n in C:
            if n in seen:
                continue
            grp, i = [n], 0
            seen.add(n)
            while i < len(grp):
                a = grp[i]
                i += 1
                for b in C:
                    if b not in seen and math.hypot(self.X[b][0] - self.X[a][0], self.X[b][1] - self.X[a][1]) <= merge:
                        seen.add(b)
                        grp.append(b)
            cx = sum(self.X[g][0] for g in grp) / len(grp)
            cz = sum(self.X[g][1] for g in grp) / len(grp)
            if self.lot.dist(cx, cz) <= R:
                pts.append((cx, cz, len(grp)))
        return pts


# ---------------- the census, worked out here ----------------
def share(X, Y):
    """the Census Bureau's derived proportion, and its ratio formula where the root goes negative"""
    p = X[0] / Y[0]
    r = X[1] ** 2 - p * p * Y[1] ** 2
    if r < 0:
        r = X[1] ** 2 + p * p * Y[1] ** 2
    return p, math.sqrt(r) / Y[0]


def summ(L):
    return sum(x[0] for x in L), math.sqrt(sum(x[1] ** 2 for x in L))


def facts(geo):
    out = {}
    for k, (e, m) in FX.FACTS[geo].items():
        out[k] = [None if e < 0 else e, 0 if m == -555555555 else (None if m < 0 else m)]
    return out


BANDS = [[3], [4], [5], [6, 7], [8, 9, 10], [11], [12], [13], [14], [15], [16], [17], [18, 19], [20, 21], [22], [23], [24], [25]]


def pyramid(geo):
    c = FX.pyramid_cells(geo)
    return {'m': [sum(c['B01001_%03dE' % i] for i in b) for b in BANDS], 'f': [sum(c['B01001_%03dE' % (i + 24)] for i in b) for b in BANDS]}
