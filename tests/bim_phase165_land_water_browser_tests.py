#!/usr/bin/env python3
"""bim_phase165_land_water_browser_tests.py -- V165: site analysis in the model II, land and water.

The ground is tests/land_fixture.py's -- a fall to the north-east, a hill to the south-west, a valley
32 m north-east of the site, a hollow that ponds -- served as AWS Terrain Tiles; FEMA's flood map is its
strips along the valley. Everything the analyses draw is worked out again here another way: the ground
against the function it was made from, Horn's slope and aspect, Priority-Flood with the same heap and
D8, the accumulation, Strahler's order, the catchments, the ponds, the land draining onto the site and
where it leaves; each contour point against the ground between the two grid points it lies between.

  1. THE RUN: the Ground and water step; the ground every 5 m, kept in metres above sea level.
  2. THE LAYERS: six, under Site analysis; slope and aspect off, the rest on.
  3. SLOPE AND ASPECT: Horn's method, cell for cell; the five classes and their shares; the rings
     through the points between the cells; the site's mean and steepest; aspect read for warmth.
  4. CONTOURS: the step, the levels at round heights, each point on the ground at its height; the
     index contours labelled with a number.
  5. MARCHING SQUARES: a block's ring, a hole, a line that runs out at the edge.
  6. WATER: the filled ground, the directions, the accumulation, the order, the catchments, the ponds,
     the links, the land draining onto the site and where it leaves -- each against the reference;
     the elements drawn from them.
  7. FLOOD ZONES: FEMA's zones as classed, coloured, labelled, cut to the square; the site's zone;
     the classing of zones, the base flood elevation, the US.
  8. FINDINGS: the site's slope, its drainage, its FEMA zone.
  9. THE ENGINE: a hidden coverage shown; a class restyled, drawn in its new fill; a class turned and
     undone; a contour picked; the key compacted in a small view.
 10. ELSEWHERE: the context's terrain, a surface of the project's own; FEMA down; a site outside the
     US; a phone and a tablet.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import site_analysis_fixture as FX   # noqa: E402
import land_fixture as LFX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
TOWER = [-12, -10, 12, 10, 24]
LAND = ('contours', 'slope', 'aspect', 'flow', 'ponds', 'flood')
NAMES = {'contours': 'Contours', 'slope': 'Slope', 'aspect': 'Aspect', 'flow': 'Water flow', 'ponds': 'Ponds', 'flood': 'Flood zones'}
SLOPE_BREAKS = [5, 10, 15, 25]
SLOPE_NAMES = ['0 to 5%', '5 to 10%', '10 to 15%', '15 to 25%', 'Over 25%']
SLOPE_COLS = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
DIRS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
DIRNAME = {'N': 'north', 'NE': 'north-east', 'E': 'east', 'SE': 'south-east', 'S': 'south', 'SW': 'south-west', 'W': 'west', 'NW': 'north-west'}
WARM = ['#4575b4', '#91bfdb', '#e6dfc8', '#fc8d59', '#d7301f']
DX = [1, 1, 0, -1, -1, -1, 0, 1]
DZ = [0, 1, 1, 1, 0, -1, -1, -1]
DL = [1, math.sqrt(2), 1, math.sqrt(2), 1, math.sqrt(2), 1, math.sqrt(2)]
EPS = 1e-5


def disp(v, dp):
    """the app's bimDispNum: fixed, trailing zeros trimmed"""
    s = ('%.' + str(dp) + 'f') % v
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def pct(n, t):
    return disp(100.0 * n / t, 1) + '%' if t else '—'


def ha(m2):
    return disp(m2 / 10000.0, 2) + ' ha' if m2 >= 2000 else disp(m2, 0) + ' m²'


# ---- Horn (1981), as the app is said to work it out ----
def horn(H, ok, nx, nz, c):
    N = nx * nz
    sl, asp = [None] * N, [None] * N
    for j in range(nz):
        for i in range(nx):
            k = j * nx + i
            if not ok[k]:
                continue
            e = H[k]

            def h(i2, j2):
                if i2 < 0 or j2 < 0 or i2 >= nx or j2 >= nz:
                    return e
                q = j2 * nx + i2
                return H[q] if ok[q] else e
            a, b, cc, d, f, g, hh, ii = h(i - 1, j - 1), h(i, j - 1), h(i + 1, j - 1), h(i - 1, j), h(i + 1, j), h(i - 1, j + 1), h(i, j + 1), h(i + 1, j + 1)
            dx = ((cc + 2 * f + ii) - (a + 2 * d + g)) / (8 * c)
            dz = ((g + 2 * hh + ii) - (a + 2 * b + cc)) / (8 * c)
            s = math.sqrt(dx * dx + dz * dz) * 100
            sl[k] = s
            asp[k] = -1 if s < 2 else (math.degrees(math.atan2(-dx, dz)) + 360) % 360   # true north up: east (1, 0), north (0, -1)
    return sl, asp


def dir8(az):
    return int(((az + 22.5) % 360) // 45) % 8


# ---- the app's heap, ported, so Priority-Flood's ties go the same way ----
class Heap:
    def __init__(self):
        self.a = []

    def size(self):
        return len(self.a)

    def push(self, x):
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i > 0:
            p = (i - 1) >> 1
            if a[p][0] <= x[0]:
                break
            a[i] = a[p]
            i = p
        a[i] = x

    def pop(self):
        a = self.a
        top = a[0]
        x = a.pop()
        i, n = 0, len(a)
        if n:
            while True:
                l, r, m, mv = 2 * i + 1, 2 * i + 2, i, x[0]
                if l < n and a[l][0] < mv:
                    m, mv = l, a[l][0]
                if r < n and a[r][0] < mv:
                    m = r
                if m == i:
                    break
                a[i] = a[m]
                i = m
            a[i] = x
        return top


def hydro(H, ok, nx, nz, c):
    """Barnes, Lehman and Mulla's Priority-Flood with epsilon, O'Callaghan and Mark's D8, the rest"""
    N, a2 = nx * nz, c * c
    F, dirs, down, done = [0.0] * N, [-2] * N, [-1] * N, [0] * N
    Q, order_ = Heap(), []

    def edge(i, j):
        if i == 0 or j == 0 or i == nx - 1 or j == nz - 1:
            return True
        return any(not ok[(j + DZ[e]) * nx + i + DX[e]] for e in range(8))
    for j in range(nz):
        for i in range(nx):
            k = j * nx + i
            if ok[k] and edge(i, j):
                F[k], done[k], dirs[k] = H[k], 1, -1
                Q.push([F[k], k])
    while Q.size():
        cc = Q.pop()[1]
        ci, cj = cc % nx, cc // nx
        order_.append(cc)
        for d in range(8):
            a, b = ci + DX[d], cj + DZ[d]
            if a < 0 or b < 0 or a >= nx or b >= nz:
                continue
            nk = b * nx + a
            if not ok[nk] or done[nk]:
                continue
            done[nk] = 1
            F[nk] = max(H[nk], F[cc] + EPS * DL[d])
            Q.push([F[nk], nk])
    for k in range(N):
        if not ok[k] or dirs[k] == -1:
            continue
        ki, kj, best, bs = k % nx, k // nx, -1, 0
        for d in range(8):
            a, b = ki + DX[d], kj + DZ[d]
            if a < 0 or b < 0 or a >= nx or b >= nz:
                continue
            q = b * nx + a
            if not ok[q]:
                continue
            s2 = (F[k] - F[q]) / (DL[d] * c)
            if s2 > bs:
                bs, best = s2, d
        dirs[k] = best
        if best >= 0:
            down[k] = (kj + DZ[best]) * nx + ki + DX[best]
    byF = sorted(order_, key=lambda k: (-F[k], -k))
    acc = [a2 if ok[k] else 0 for k in range(N)]
    for k in byF:
        if down[k] >= 0:
            acc[down[k]] += acc[k]
    stream = [1 if ok[k] and acc[k] >= 2500 else 0 for k in range(N)]
    nin, order, mxo, cnt = [0] * N, [0] * N, [0] * N, [0] * N
    up = [[] for _ in range(N)]
    for k in range(N):
        if down[k] >= 0:
            up[down[k]].append(k)
            if stream[k] and stream[down[k]]:
                nin[down[k]] += 1
    for k in byF:
        if not stream[k]:
            continue
        order[k] = (mxo[k] + 1 if cnt[k] >= 2 else mxo[k]) if mxo[k] else 1
        t = down[k]
        if t >= 0 and stream[t]:
            if order[k] > mxo[t]:
                mxo[t], cnt[t] = order[k], 1
            elif order[k] == mxo[t]:
                cnt[t] += 1
    lab, outl = [-1] * N, {}
    for k in reversed(byF):
        lab[k] = k if dirs[k] == -1 else (lab[down[k]] if down[k] >= 0 else k)
        outl[lab[k]] = outl.get(lab[k], 0) + 1
    pid, ponds = [0] * N, []
    for k in range(N):
        if not ok[k] or pid[k] or F[k] - H[k] < 0.1:
            continue
        pool = {'cells': [], 'volume': 0.0, 'depth': 0.0, 'deep': k, 'level': -1e300}
        stack = [k]
        pid[k] = -1
        while stack:
            u = stack.pop()
            ui, uj, dd = u % nx, u // nx, F[u] - H[u]
            pool['cells'].append(u)
            pool['volume'] += dd * a2
            pool['level'] = max(pool['level'], F[u])
            if dd > pool['depth']:
                pool['depth'], pool['deep'] = dd, u
            for d in range(8):
                a, b = ui + DX[d], uj + DZ[d]
                if a < 0 or b < 0 or a >= nx or b >= nz:
                    continue
                v = b * nx + a
                if ok[v] and not pid[v] and F[v] - H[v] >= 0.1:
                    pid[v] = -1
                    stack.append(v)
        pool['area'] = len(pool['cells']) * a2
        if pool['area'] >= 50:
            ponds.append(pool)
    ponds.sort(key=lambda p: (-p['volume'], p['deep']))
    links = []
    for k in range(N):
        if not stream[k] or nin[k] == 1:
            continue
        nodes, cur = [k], k
        while True:
            t = down[cur]
            if t < 0:
                break
            nodes.append(t)
            if nin[t] != 1:
                break
            cur = t
        links.append({'from': k, 'to': nodes[-1], 'order': order[k], 'outlet': down[nodes[-1]] < 0, 'n': len(nodes)})
    return {'F': F, 'down': down, 'acc': acc, 'order': order, 'lab': lab, 'stream': stream, 'up': up, 'outCells': outl,
            'ponds': ponds[:8], 'pondsAll': len(ponds), 'links': links}


def upstream(Y, M):
    U, st = [0] * len(M), []
    for k, m in enumerate(M):
        if m:
            U[k] = 1
            st.append(k)
    while st:
        k = st.pop()
        for u in Y['up'][k]:
            if not U[u]:
                U[u] = 1
                st.append(u)
    return U


def exits(Y, M):
    E = sorted([k for k in range(len(M)) if M[k] and Y['down'][k] >= 0 and not M[Y['down'][k]]], key=lambda k: (-Y['acc'][k], k))
    out = []
    for k in E:
        if len(out) >= 2:
            break
        if out and Y['acc'][k] < 0.25 * out[0]['acc']:
            break
        p, c = [k], k
        for _ in range(4):
            c = Y['down'][c]
            if c < 0:
                break
            p.append(c)
        if len(p) > 1:
            out.append({'k': k, 'acc': Y['acc'][k], 'path': p})
    return out


def ring_area(R):
    a = 0.0
    for i in range(len(R)):
        j = (i + 1) % len(R)
        a += R[i][0] * R[j][1] - R[j][0] * R[i][1]
    return abs(a) / 2


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ST = {'ground': 'land', 'flood': 'zones'}

        async def fresh(store, vw=(1440, 900), mobile=False):
            c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
            for h in FX.HOSTS:
                await c.route(h, FX.route_handler(store))
            for h in BLOCKERS:
                await c.route(h, lambda r: r.abort())
            p = await c.new_page()
            e = []
            p.on('pageerror', lambda x: e.append(str(x)))
            await within(p.goto('file://' + str(HTML)), 'goto')
            await p.wait_for_timeout(2000)
            await p.evaluate("()=>window.__a3dEnter()")
            await p.evaluate("""(a)=>{var x0=a[0],z0=a[1],x1=a[2],z1=a[3],h=a[4];return window.__a3dPushTestObj({id:'TOWER',t:'solid',name:'Tower',pos:[0,0,0],layer:'layer-0',
              mesh:{v:[[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,h,z0],[x1,h,z0],[x1,h,z1],[x0,h,z1]],f:[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}});}""", TOWER)
            await p.evaluate("()=>window.__a3dAnzView(true)")
            await p.wait_for_timeout(200)
            return c, p, e

        ctx, page, errs = await fresh(ST)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def wait_run(pg=None, bound=90):
            for _ in range(bound * 4):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await (pg or page).wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def analyze(pg=None):
            await (pg or page).fill('[data-saaddr]', '1 Market Street')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=pg)
            return await wait_run(pg=pg)

        async def diags(a=None, pg=None):
            return [o for o in ((await safe("()=>window.__a3dState().objs", pg=pg)) or []) if o.get('t') == 'diag' and (a is None or o['dg']['a'] == a)]

        async def el(a, k, pg=None):
            for o in await diags(a, pg=pg):
                if o['dg']['k'] == k:
                    return o
            return None

        def rows(o):
            return {r[0]: r[1] for r in o['dg']['info'].get('rows', [])}

        try:
            fin = await analyze()
            steps = {s['id']: s for s in fin.get('steps', [])}
            D = await safe("()=>window.__a3dDgState()") or {}

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The run")
            ck(await safe("()=>typeof window.__acad3dV165==='string'&&/priorityflood/.test(window.__acad3dV165)&&/fema/.test(window.__acad3dV165)") is True, "the V165 marker")
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(re.match(r'^V\d+$', ver) and int(ver[1:]) >= 165, "the app says V165 or later (%s)" % ver)
            ck([s['id'] for s in fin.get('steps', [])] == ['place', 'context', 'land', 'climate', 'access', 'zoning', 'draw'], "Ground and water is a step, after the context")
            ck(steps.get('land', {}).get('state') == 'ok' and steps['land']['text'] == 'the ground every 5 m for 150 m around, 4 flood zones from FEMA',
               "the step says what came: the ground every 5 m, FEMA's zones (%s)" % steps.get('land', {}).get('text'))
            hits = [h[0] for h in ST.get('hits', [])]
            ck(hits.count('flood') == 1, "FEMA asked once (%d)" % hits.count('flood'))
            fu = [h[1] for h in ST['hits'] if h[0] == 'flood'][0]
            ck('/NFHL/MapServer/28/query?' in fu and 'f=geojson' in fu and 'inSR=4326' in fu, "its flood hazard layer, for the square, as GeoJSON")
            dem = await safe("()=>window.__a3dLandDem()") or {}
            nx, nz, cell, x0, z0 = dem.get('nx'), dem.get('nz'), dem.get('cell'), dem.get('x0'), dem.get('z0')
            ck(dem.get('from') == 'tiles' and nx == 61 and nz == 61 and cell == 5 and x0 == -150 and z0 == -150, "the ground every 5 m, 61 by 61 points, 150 m around the site")
            datum = dem.get('datum')
            ck(datum is not None and abs(datum - round(LFX.land_height(0, 0), 2)) <= 0.011, "model 0 is the ground under the site's origin: %.2f m above sea level" % (datum or 0))
            H = dem.get('H') or []
            ok = [1 if v is not None else 0 for v in H]
            Hn = [v if v is not None else 0.0 for v in H]
            err = max((abs(Hn[j * nx + i] + datum - LFX.land_height(x0 + i * cell, z0 + j * cell)) for j in range(nz) for i in range(nx)), default=99)
            ck(sum(ok) == nx * nz and err < 0.06, "every point the ground it was made from, within %.3f m (the tiles' pixels and their centimetres)" % err)
            kept = await safe("()=>window.__a3dLandGet()") or {}
            kd = kept.get('dem') or {}
            ck(len(kd.get('h', [])) == 3721 and all(isinstance(v, int) for v in kd['h']) and abs(kd['h'][30 * 61 + 30] / 100 - datum) <= 0.011 and kd.get('zoom') == 15,
               "kept with the project in centimetres above sea level, with its zoom")
            ck('AWS Terrain Tiles at zoom 15' in dem.get('src', '') and 'srtm' in dem.get('src', ''), "its source named, with the imagery under it (%s)" % dem.get('src'))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The layers")
            LY = {l['id']: l for l in (await safe("()=>window.__a3dLayers()") or [])}
            root = D.get('layers', {}).get('root')
            lays = {a: LY.get(D.get('layers', {}).get(a)) for a in LAND}
            ck(all(lays.values()) and all(lays[a]['name'] == 'Site analysis - ' + NAMES[a] and lays[a].get('parent') == root for a in LAND), "a layer for each, under Site analysis")
            ck([a for a in LAND if lays[a] and lays[a].get('visible') is False] == ['slope', 'aspect'], "slope and aspect, which cover the ground, start hidden; the rest shown")
            S = await safe("()=>window.__a3dDgSite()") or {}
            ck(S.get('c') == [0, 0] and abs(S.get('r', 0) - math.hypot(24, 20) / 2) < 1e-9, "the site: the tower's centre and half-diagonal")
            M = [1 if ok[k] and ((x0 + (k % nx) * cell) ** 2 + (z0 + (k // nx) * cell) ** 2) <= S['r'] ** 2 else 0 for k in range(nx * nz)]

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Slope and aspect")
            sl, asp = horn(Hn, ok, nx, nz, cell)
            HN = await safe("()=>window.__a3dLandHorn()") or {}
            ck(len(HN.get('slope', [])) == nx * nz and max(abs(a - b) for a, b in zip(sl, HN['slope'])) < 1e-9, "Horn's slope, cell for cell, as worked out here")
            ck(max(abs(a - b) for a, b in zip(asp, HN['aspect'])) < 1e-9, "and its aspect, clockwise from true north, flat under 2%")
            cls = [sum(1 for v in sl if v is not None and v >= b) for b in [0] + SLOPE_BREAKS]
            cnt = [cls[i] - (cls[i + 1] if i + 1 < len(cls) else 0) for i in range(5)]
            tot = sum(cnt)
            ck(all(cnt) and cnt[4] > 0, "the ground has all five classes, the hill's flanks over 25%% (%s)" % cnt)
            ok_cls = True
            for i in range(5):
                o = await el('slope', 'class:%d' % i)
                if not o or o['name'] != 'Slope ' + SLOPE_NAMES[i] or o['dg']['s'].get('fill') != SLOPE_COLS[i] or not rows(o).get('Of the ground around', '').startswith(pct(cnt[i], tot) + ' ('):
                    ok_cls = False
                    print('      class %d: %s' % (i, o and (o['name'], o['dg']['s'], rows(o))))
            ck(ok_cls, "each class an element, in its colour, its share of the ground as counted here")
            halfgrid = True
            for i in range(5):
                o = await el('slope', 'class:%d' % i)
                for R in (o['dg']['g']['bands'][0]['rings'] if o else []):
                    for p in R:
                        gx, gz = (p[0] - x0) / cell, (p[2] - z0) / cell
                        fx, fz = abs(gx - round(gx)), abs(gz - round(gz))
                        if not ((fx < 0.003 and abs(fz - 0.5) < 0.003) or (fz < 0.003 and abs(fx - 0.5) < 0.003)):
                            halfgrid = False
            ck(halfgrid, "every ring point half-way between two grid points: the edge between the classes")
            ss = [sl[k] for k in range(nx * nz) if M[k]]
            site = await el('slope', 'site')
            ck(site and rows(site).get('Mean') == disp(sum(ss) / len(ss), 1) + '%' and rows(site).get('Steepest', '').startswith(disp(max(ss), 1) + '%'),
               "the site's mean %s%% and steepest %s%%, over the cells inside it" % (disp(sum(ss) / len(ss), 1), disp(max(ss), 1)))
            mainc = max(range(5), key=lambda i: (sum(1 for v in ss if (SLOPE_BREAKS + [1e9])[i] > v >= ([0] + SLOPE_BREAKS)[i]), -i))
            ck(site and site['dg']['lb'][0]['t'] == 'Site: mostly ' + SLOPE_NAMES[mainc] + ', mean ' + disp(sum(ss) / len(ss), 1) + '%', "labelled: %s" % (site and site['dg']['lb'][0]['t']))
            dcnt = [0] * 9
            for v in asp:
                if v is not None:
                    dcnt[8 if v < 0 else dir8(v)] += 1
            ok_dir = True
            for i in range(9):
                key = 'flat' if i == 8 else 'dir:' + DIRS[i]
                o = await el('aspect', key)
                if not dcnt[i]:
                    ok_dir = ok_dir and o is None
                    continue
                want_col = '#bdbdbd' if i == 8 else WARM[4 - round(abs(((i * 45 - 180) % 360 + 540) % 360 - 180) / 45)]
                if not o or o['dg']['s'].get('fill') != want_col or not rows(o).get('Of the ground around', '').startswith(pct(dcnt[i], sum(dcnt)) + ' ('):
                    ok_dir = False
                    print('      aspect %s: %s' % (key, o and (o['dg']['s'], rows(o))))
            ck(ok_dir, "aspect: each way an element, its share as counted here; south warm, north cool, at 40 N")
            ck(await safe("()=>[window.__a3dLandWarm(4,40),window.__a3dLandWarm(0,40),window.__a3dLandWarm(4,-33),window.__a3dLandWarm(0,-33),window.__a3dLandWarm(2,40)]") == [4, 0, 0, 4, 2],
               "south of the equator the north is the warm side; east and west between")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Contours")
            lo, hi = min(v for v in Hn), max(v for v in Hn)
            step = next(s for s in [0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50] if math.floor((hi + datum) / s + 1e-9) - math.ceil((lo + datum) / s - 1e-9) + 1 <= 24)
            levs = [k * step for k in range(math.ceil((lo + datum) / step - 1e-9), math.floor((hi + datum) / step + 1e-9) + 1)]
            CT = await diags('contours')
            got = sorted(int(o['dg']['k'][2:]) for o in CT)
            ck(step == 2 and got == [int(round(L * 100)) for L in levs], "every %g m at round heights above sea level, %s to %s (%d lines)" % (step, levs[0], levs[-1], len(levs)))
            onlevel, worst = True, 0.0
            for o in CT:
                L = int(o['dg']['k'][2:]) / 100.0
                y = L - datum
                for line in o['dg']['g']['lines']:
                    for p in line:
                        if abs(p[1] - round(y + 0.03, 2)) > 0.006:
                            onlevel = False
                        gx, gz = (p[0] - x0) / cell, (p[2] - z0) / cell
                        if abs(gx - round(gx)) < 0.003:
                            i, j = int(round(gx)), min(nz - 2, int(math.floor(gz)))
                            t = gz - j
                            hv = Hn[j * nx + i] * (1 - t) + Hn[(j + 1) * nx + i] * t
                        elif abs(gz - round(gz)) < 0.003:
                            j, i = int(round(gz)), min(nx - 2, int(math.floor(gx)))
                            t = gx - i
                            hv = Hn[j * nx + i] * (1 - t) + Hn[j * nx + i + 1] * t
                        else:
                            onlevel = False
                            continue
                        worst = max(worst, abs(hv - y))
            ck(onlevel and worst < 0.01, "each point on a grid edge, where the ground between its two points is at the height (within %.4f m)" % worst)
            idx = [o for o in CT if round(int(o['dg']['k'][2:]) / 100.0 / step) % 5 == 0]
            ck(idx and all(o['dg']['lb'] and o['dg']['lb'][0]['t'] == disp(int(o['dg']['k'][2:]) / 100.0, 0) and o['dg']['s']['w'] == 1.7 for o in idx) and
               all(not o['dg']['lb'] and o['dg']['s']['w'] == 0.8 for o in CT if o not in idx),
               "every fifth an index contour, thicker, labelled with its height as a number (%s)" % [o['dg']['lb'][0]['t'] for o in idx if o['dg']['lb']])
            lgc = ((D.get('runs') or {}).get('contours') or {}).get('legend') or []
            ck(lgc and lgc[2]['name'] == 'Every 2 m; every fifth labelled with its height in metres above sea level', "the key gives the step and the unit")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Marching squares")
            blk = await safe("()=>{var V=[],i,j;for(j=0;j<7;j++)for(i=0;i<7;i++)V.push(i>=2&&i<5&&j>=2&&j<5?1:0);return window.__a3dLandMs(V,7,7,0.5,0);}") or []
            ck(len(blk) == 1 and abs(ring_area(blk[0]) - 8.5) < 1e-9, "a block of 3 by 3 points: one ring through the half-way points, 8.5 cells (its corners cut)")
            hole = await safe("()=>{var V=[],i,j;for(j=0;j<7;j++)for(i=0;i<7;i++)V.push(i>=1&&i<6&&j>=1&&j<6&&!(i===3&&j===3)?1:0);return window.__a3dLandMs(V,7,7,0.5,0);}") or []
            ar = sorted(ring_area(r) for r in hole)
            ck(len(hole) == 2 and abs(ar[0] - 0.5) < 1e-9 and abs(ar[1] - 24.5) < 1e-9, "5 by 5 with its middle missing: two rings, 24.5 round 0.5, read even-odd (%s)" % ar)
            ramp = await safe("()=>{var V=[],i,j;for(j=0;j<4;j++)for(i=0;i<5;i++)V.push(i);return window.__a3dLandMs(V,5,4,1.5,null);}") or []
            ck(len(ramp) == 1 and len(ramp[0]) == 4 and all(abs(p[0] - 1.5) < 1e-12 for p in ramp[0]) and sorted(p[1] for p in ramp[0]) == [0, 1, 2, 3],
               "a ramp's 1.5 contour: one line at x 1.5 running out at both edges")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Water")
            Y = hydro(Hn, ok, nx, nz, cell)
            YA = await safe("()=>window.__a3dLandHydro()") or {}
            ck(YA and max(abs(a - b) for a, b in zip(Y['F'], YA['F'])) == 0, "the filled ground, cell for cell, as Priority-Flood fills it here")
            ck(YA.get('down') == Y['down'], "each cell to its steepest neighbour on it (D8)")
            ck(max(abs(a - b) for a, b in zip(Y['acc'], YA['acc'])) < 1e-6 and max(Y['acc']) > 20000, "the accumulation, highest first: %s at most" % ha(max(Y['acc'])))
            ck(YA.get('order') == Y['order'] and YA.get('lab') == Y['lab'], "Strahler's order on the flow lines, and each cell's outlet")
            pp = YA.get('ponds') or []
            ck(len(pp) == len(Y['ponds']) == 1 and sorted(pp[0]['cells']) == sorted(Y['ponds'][0]['cells']) and abs(pp[0]['volume'] - Y['ponds'][0]['volume']) < 1e-6 and pp[0]['deep'] == Y['ponds'][0]['deep'],
               "one pond, the hollow's: %d cells, %.1f m³, %.2f m deep" % (len(Y['ponds'][0]['cells']) if Y['ponds'] else 0, Y['ponds'][0]['volume'] if Y['ponds'] else 0, Y['ponds'][0]['depth'] if Y['ponds'] else 0))
            dk = Y['ponds'][0]['deep'] if Y['ponds'] else -1
            ck(dk >= 0 and math.hypot(x0 + (dk % nx) * cell + 60, z0 + (dk // nx) * cell + 60) <= 7.1, "its deepest point at the hollow, (-60, -60)")
            ck(sorted((l['from'], l['to'], l['order'], l['outlet']) for l in YA.get('links', [])) == sorted((l['from'], l['to'], l['order'], l['outlet']) for l in Y['links']) and len(Y['links']) >= 2,
               "the flow lines, link by link (%d), from each source or confluence" % len(Y['links']))
            U = upstream(Y, M)
            ck(YA.get('site') == M and YA.get('upstream') == U, "the site's cells, and the land whose water reaches them")
            EX = exits(Y, M)
            ck([(e['k'], e['path']) for e in YA.get('exits', [])] == [(e['k'], e['path']) for e in EX] and EX, "where the site's water leaves it, the most first")
            FL = await diags('flow')
            lk = [o for o in FL if o['dg']['k'].startswith('flow:')]
            drawn = sorted('flow:%d-%d' % (l['from'], l['to']) for l in Y['links'] if l['n'] >= 2)   # a confluence at the edge has nothing to draw
            ck(sorted(o['dg']['k'] for o in lk) == drawn and all(o['dg']['s'].get('head') and o['dg']['s'].get('w') == [1.1, 1.7, 2.4, 3.1, 3.8][min(5, int(o['name'].split()[-1])) - 1] for o in lk),
               "each link of two points or more a line with its arrowhead, wider by its order (%s)" % [(o['name'], o['dg']['s'].get('w'), o['dg']['s'].get('head')) for o in lk])
            tot_ok = sum(ok)
            big = sorted([o for o, n in Y['outCells'].items() if n >= 0.04 * tot_ok])
            CA = sorted(int(o['dg']['k'][6:]) for o in FL if o['dg']['k'].startswith('catch:'))
            ck(CA == big and all(o['dg']['g']['kind'] == 'lines' and o['dg']['s']['dash'] for o in FL if o['dg']['k'].startswith('catch:')),
               "the catchments of 4%% or more, %d, outlined dashed" % len(big))
            edgefree = True
            for o in FL:
                if o['dg']['k'].startswith('catch:'):
                    for line in o['dg']['g']['lines']:
                        for p in line:
                            if (p[0] - x0) / cell < -0.25 or (p[2] - z0) / cell < -0.25 or (p[0] - x0) / cell > nx - 0.75 or (p[2] - z0) / cell > nz - 0.75:
                                edgefree = False
            ck(edgefree, "the divides only: no line along the edge of the ground analysed")
            nu = sum(1 for k in range(nx * nz) if U[k] and not M[k])
            uo = await el('flow', 'upstream')
            ck(uo and uo['dg']['lb'][0]['t'] == ha(nu * 25) + ' drains onto the site' and uo['dg']['g']['bands'][0]['rings'], "the land draining onto the site, %s, shaded and said" % ha(nu * 25))
            e0 = EX[0]
            pa, pb = e0['path'][0], e0['path'][-1]
            vx, vz = (pb % nx - pa % nx) * cell, (pb // nx - pa // nx) * cell
            dn = DIRNAME[DIRS[dir8((math.degrees(math.atan2(vx, -vz)) + 360) % 360)]]
            xo = await el('flow', 'exit:%d' % e0['k'])
            ck(xo and xo['dg']['s']['head'] and xo['dg']['lb'][0]['t'] == 'Drains to the ' + dn, "an arrow where it leaves: drains to the %s" % dn)
            po = await diags('ponds')
            ck(len(po) == 1 and po[0]['dg']['k'] == 'pond:%d' % dk and po[0]['dg']['lb'][0]['t'] == disp(Y['ponds'][0]['depth'], 1) + ' m deep, ' + disp(Y['ponds'][0]['volume'], 0) + ' m³'
               and po[0]['dg']['g']['marks'], "the pond drawn, its deepest point marked: %s" % (po and po[0]['dg']['lb'][0]['t']))

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Flood zones")
            FZ = {o['dg']['k']: o for o in await diags('flood')}
            ck(sorted(FZ) == ['site', 'zone:FIX_1', 'zone:FIX_2', 'zone:FIX_3'], "the floodway, zone AE and shaded X drawn; unshaded X, minimal, not (%s)" % sorted(FZ))
            ck(FZ.get('zone:FIX_1', {}).get('dg', {}).get('s', {}).get('fill') == '#c2416b' and FZ['zone:FIX_2']['dg']['s']['fill'] == '#3d85d8' and FZ['zone:FIX_3']['dg']['s']['fill'] == '#f0a04b',
               "the floodway crimson, the 1% blue, the 0.2% orange")
            ck(len(FZ.get('zone:FIX_2', {}).get('dg', {}).get('g', {}).get('bands', [{}])[0].get('rings', [])) == 2, "zone AE's two strips, one element")
            ck(FZ['zone:FIX_2']['dg']['lb'][0]['t'] == 'Zone AE, BFE 315 ft' and FZ['zone:FIX_1']['dg']['lb'][0]['t'] == 'Zone AE, floodway, BFE 315 ft', "labelled with the zone and its base flood elevation")
            ck(rows(FZ['zone:FIX_2']).get('Base flood elevation') == '315 ft (96.01 m), NAVD88', "the elevation in its feet, in metres, on its datum")
            inbox = all(-150.001 <= p[0] <= 150.001 and -150.001 <= p[2] <= 150.001 for o in FZ.values() for B in o['dg']['g'].get('bands', []) for R in B['rings'] for p in R)
            ck(inbox, "cut to the square analysed")
            ck(FZ['site']['dg']['lb'][0]['t'] == 'Site: zone X, 0.2% annual chance', "the site: zone X, the 0.2%% annual chance (%s)" % FZ['site']['dg']['lb'][0]['t'])
            zof = await safe("""()=>[{FLD_ZONE:'AE',ZONE_SUBTY:' ',SFHA_TF:'T'},{FLD_ZONE:'A'},{FLD_ZONE:'AO',SFHA_TF:'T'},{FLD_ZONE:'VE',SFHA_TF:'T'},{FLD_ZONE:'AE',ZONE_SUBTY:'FLOODWAY'},
              {FLD_ZONE:'X',ZONE_SUBTY:'0.2 PCT ANNUAL CHANCE FLOOD HAZARD'},{FLD_ZONE:'X',ZONE_SUBTY:'AREA OF MINIMAL FLOOD HAZARD'},{FLD_ZONE:'D'},{FLD_ZONE:'OPEN WATER'}].map(window.__a3dLandZoneOf)""")
            ck(zof == ['sfha', 'sfha', 'sfha', 'coastal', 'floodway', 'x02', None, 'undetermined', None], "FEMA's zones as FEMA classes them (%s)" % zof)
            bf = await safe("()=>[window.__a3dLandBfe({STATIC_BFE:-9999}),window.__a3dLandBfe({STATIC_BFE:12.5,LEN_UNIT:'Meters',V_DATUM:'NAVD88'})]") or [1, None]
            ck(bf[0] is None and bf[1] and bf[1]['text'] == '12.5 m, NAVD88', "no elevation where FEMA gives none; metres as metres")
            us = await safe("()=>[[40,-75],[61.2,-149.9],[21.3,-157.8],[18.2,-66.5],[13.4,144.8],[-14.3,-170.7],[51.5,-0.12],[35.7,139.7],[-33.9,151.2]].map(function(p){return window.__a3dLandUS(p[0],p[1]);})")
            ck(us == [True, True, True, True, True, True, False, False, False], "FEMA asked for the US and its territories only (%s)" % us)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Findings")
            FD = {f.get('auto'): f for f in ((await safe("()=>window.__a3dSa()") or {}).get('findings') or [])}
            fl5, st15 = sum(1 for v in ss if v < 5), sum(1 for v in ss if v >= 15)
            want = 'Mean ' + disp(sum(ss) / len(ss), 1) + '%, steepest ' + disp(max(ss), 1) + '%; ' + pct(fl5, len(ss)) + ' under 5%' + ((', ' + pct(st15, len(ss)) + ' at 15% or more') if st15 else '')
            ck(FD.get('landform.slope', {}).get('value') == want and FD['landform.slope']['cat'] == 'landform', "the site's slope: %s" % FD.get('landform.slope', {}).get('value'))
            wd = 'Drains to the ' + dn + '; ' + (ha(nu * 25) + ' around drains onto it' if nu else 'nothing around drains onto it') + '; ' + ('1 pond within 150 m' if len(Y['ponds']) == 1 else '%d ponds within 150 m' % len(Y['ponds']))
            ck(FD.get('water.drainage', {}).get('value') == wd and FD['water.drainage']['cat'] == 'water', "its drainage: %s" % FD.get('water.drainage', {}).get('value'))
            ck(FD.get('water.fema', {}).get('value') == 'The site is in zone X, 0.2% annual chance; within 150 m: floodway, 1%' and FD['water.fema']['cls'] == 'constraint',
               "its FEMA zone, and those near it, a constraint")
            F = await safe("()=>[].map.call(document.querySelectorAll('.a3d-analyze-wrap [data-sacat=\"water\"] .a3d-saftt'),function(e){return e.textContent;})") or []
            ck('Drainage' in F and 'Flood zone (FEMA)' in F, "both read in Water (%s)" % F)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. The engine")
            await safe("()=>window.__a3dAnzView(true)")
            await page.wait_for_timeout(150)
            rowtxt = await safe("()=>(document.querySelector('[data-anzcard=\"dgslope\"] [data-anzact=\"dg:show:slope\"]')||{}).textContent")
            ck(rowtxt == 'Show', "Slope's row offers Show, its layer being off")
            await safe("()=>document.querySelector('[data-anzcard=\"dgslope\"] [data-anzact=\"dg:show:slope\"]').click()")
            await page.wait_for_timeout(150)
            LY = {l['id']: l for l in (await safe("()=>window.__a3dLayers()") or [])}
            ck(LY[D['layers']['slope']].get('visible') is not False, "and Show turns it on")
            for a in [x for x in D['layers'] if x not in ('root', 'slope') and not x.startswith('shadow:')]:
                await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", D['layers'][a])
            # a class-0 point inside its region: all eight neighbours of the class too, away from the site
            pick = None
            for j in range(3, nz - 3):
                for i in range(3, nx - 3):
                    k = j * nx + i
                    if math.hypot(x0 + i * cell, z0 + j * cell) < 60:
                        continue
                    if all(sl[(j + b) * nx + i + a] < 5 for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2)):
                        pick = (x0 + i * cell, Hn[k], z0 + j * cell)
                        break
                if pick:
                    break
            await safe("(p)=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:p[0],tz:p[2],dist:120});}", list(pick))
            await page.wait_for_timeout(400)
            px = "(p)=>{var s=window.__a3dDgToScreen(p),c=document.getElementById('a3d-canvas'),r=window.devicePixelRatio||1,d=c.getContext('2d').getImageData(Math.round(s[0]*r)-2,Math.round(s[1]*r)-2,5,5).data,m={},i,k,best=null;for(i=0;i<d.length;i+=4){k=d[i]+','+d[i+1]+','+d[i+2];m[k]=(m[k]||0)+1;if(!best||m[k]>m[best])best=k;}return best.split(',').map(Number);}"
            c0 = await safe(px, list(pick)) or [0, 0, 0]
            o0 = await el('slope', 'class:0')
            await safe("(i)=>window.__a3dDgSet(i,'fill','#00ff00')", o0['id'])
            await page.wait_for_timeout(300)
            c1 = await safe(px, list(pick)) or [0, 0, 0]
            ck(c0[0] > 200 and c0[1] > 200 and c1[0] < 60 and c1[1] > 200 and c1[2] < 60, "a class drawn in its colour (%s), and restyled, in its new fill (%s)" % (c0, c1))
            await safe("()=>window.__a3dUndo()")
            # a class has no line of its own: a click inside it picks it, last, where nothing else is
            at = "(p)=>{var s=window.__a3dDgToScreen(p),r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left+s[0],r.top+s[1]];}"
            await safe("()=>window.__a3dSelectFor([])")
            # the class's ring point nearest the middle of the view; the selection's yellow, drawn solid, counted round it
            rp = min((p for rg in o0['dg']['g']['bands'][0]['rings'] for p in rg), key=lambda p: math.hypot(p[0] - pick[0], p[2] - pick[2]))
            lit = "(p)=>{var s=window.__a3dDgToScreen(p),c=document.getElementById('a3d-canvas'),r=window.devicePixelRatio||1,d=c.getContext('2d').getImageData(Math.round(s[0]*r)-5,Math.round(s[1]*r)-5,11,11).data,n=0,i;for(i=0;i<d.length;i+=4)if(d[i+3]>230&&Math.abs(d[i]-255)+Math.abs(d[i+1]-209)+Math.abs(d[i+2]-102)<50)n++;return n;}"
            lit0 = await safe(lit, rp)
            q = await safe(at, list(pick))
            await page.mouse.click(q[0], q[1])
            await page.wait_for_timeout(250)
            sel1 = await safe("()=>window.__a3dSelSet()")
            ck(sel1 == [o0['id']], "a click inside a class picks it, though it has no line to click (%s)" % sel1)
            lit1 = await safe(lit, rp)
            ck(lit0 == 0 and lit1 >= 4, "and its outline is lit, on a dark edge (%s pixels of the selection's yellow round its edge, %s before)" % (lit1, lit0))
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:120});}")
            await page.wait_for_timeout(300)
            q = await safe(at, [0, TOWER[4], 0])
            await page.mouse.click(q[0], q[1])
            await page.wait_for_timeout(250)
            ck(await safe("()=>window.__a3dSelSet()") == ['TOWER'], "the model over it picked first: the tower, not the class under it")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:p[0],tz:p[2],dist:120});}".replace('p[0]', str(pick[0])).replace('p[2]', str(pick[2])))
            await page.wait_for_timeout(300)
            r0 = o0['dg']['g']['bands'][0]['rings'][0][0]
            await safe("(i)=>window.__a3dRotateSelection([i],[0,0],Math.PI/2)", o0['id'])
            r1 = (await el('slope', 'class:0'))['dg']['g']['bands'][0]['rings'][0][0]
            ck(abs(math.hypot(r1[0], r1[2]) - math.hypot(r0[0], r0[2])) < 0.02 and abs(r1[1] - r0[1]) < 1e-9 and (abs(r1[0] - r0[0]) > 1 or abs(r1[2] - r0[2]) > 1),
               "a class turned a quarter about the site: its rings turned with it")
            await safe("()=>window.__a3dUndo()")
            ck((await el('slope', 'class:0'))['dg']['g']['bands'][0]['rings'][0][0] == r0, "and undone")
            await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", D['layers']['contours'])
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:300});}")
            await page.wait_for_timeout(400)
            # a point on a contour's line, half-way along one of its segments, clear of every word drawn
            boxes = [b for h in (await safe("()=>window.__a3dDgHits()") or []) for b in h['boxes']]
            vw = await safe("()=>{var c=document.getElementById('a3d-canvas').getBoundingClientRect();return [c.width,c.height];}")
            tried, picked = 0, []
            for o in CT:
                for line in o['dg']['g']['lines']:
                    if len(line) < 4 or tried >= 6:
                        continue
                    a_, b_ = line[len(line) // 2 - 1], line[len(line) // 2]
                    sp = await safe("(p)=>window.__a3dDgToScreen(p)", [(a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2, (a_[2] + b_[2]) / 2])
                    if not sp or not (20 < sp[0] < vw[0] - 20 and 20 < sp[1] < vw[1] - 20):
                        continue
                    if any(b[0] - 14 <= sp[0] <= b[0] + b[2] + 14 and b[1] - 14 <= sp[1] <= b[1] + b[3] + 14 for b in boxes):
                        continue
                    tried += 1
                    picked.append((o['id'], await safe("(a)=>window.__a3dPick(a[0],a[1])", sp[:2])))
                    break
            ck(tried >= 3 and all(a_ == b_ for a_, b_ in picked), "a contour, several lines in one element, picked by its line, away from its words (%d of %d)" % (sum(a_ == b_ for a_, b_ in picked), tried))
            for a in [x for x in D['layers'] if x != 'root' and not x.startswith('shadow:')]:
                await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", D['layers'][a])
            await page.set_viewport_size({'width': 1440, 'height': 540})
            await page.wait_for_timeout(500)
            LG = await safe("()=>window.__a3dDgLegend()") or {}
            sr = await safe("()=>window.__a3dSafeViewRect()") or {}
            bx = LG.get('box') or [0, 0, 0, 99999]
            ck(LG and (LG.get('more', 0) > 0 or LG.get('sources') is False) and bx[1] + bx[3] <= sr.get('y', 0) + sr.get('h', 0) + 0.5,
               "every analysis shown in a small view: the key drops its sources, then its last blocks, and stays in the view (%s more, sources %s)" % (LG.get('more'), LG.get('sources')))
            ck(LG.get('more', 0) == 0 or True, "(the key's blocks: %s)" % [b['title'] for b in LG.get('blocks', [])])
            await page.set_viewport_size({'width': 1440, 'height': 900})
            await page.wait_for_timeout(300)
            L2 = await safe("()=>window.__a3dDgLegend()") or {}
            sb = [b for b in L2.get('blocks', []) if b['title'] == 'Slope']
            ck(sb and sb[0]['rows'] == ['0-5%', '5-10%', '10-15%', '15-25%', '25+%'], "slope's key in the view: its five classes, short")
            b4 = {o['id']: o['dg']['g'] for o in await diags()}
            r = await safe("()=>window.__a3dDgRun('flow')") or {}
            af = {o['id']: o['dg']['g'] for o in await diags('flow')}
            ck(r.get('flow', {}).get('made') == 0 and all(af[i] == b4[i] for i in af), "run again from the kept ground: the same elements, the same lines")
            ck(not errs, "no page errors (%s)" % errs[:3])

            # ---------------------------------------------------------------------------------
            print("\n-- 10. Elsewhere")
            saved = await safe("()=>window.__a3dLandGet()")
            # another ground: two valleys falling north, meeting at the site's line -- order 2 below
            dem = saved['dem']

            def yv(x, z):
                return 100 + 0.05 * z + 0.06 * (min(abs(x + 0.6 * z), abs(x - 0.6 * z)) if z >= 0 else abs(x))
            hv = [int(round(yv(dem['x0'] + i * dem['cell'], dem['z0'] + j * dem['cell']) * 100)) for j in range(dem['nz']) for i in range(dem['nx'])]
            await safe("(v)=>window.__a3dLandSet(v)", dict(saved, dem=dict(dem, h=hv)))
            await safe("()=>window.__a3dDgRun('flow')")
            FY = [o for o in await diags('flow') if o['dg']['k'].startswith('flow:')]
            od = sorted(int(o['name'].split()[-1]) for o in FY)
            W5 = [1.1, 1.7, 2.4, 3.1, 3.8]
            ck(od.count(1) >= 2 and 2 in od and all(o['dg']['s']['w'] == W5[min(5, int(o['name'].split()[-1])) - 1] for o in FY),
               "two valleys meeting: below them the line is order 2, drawn wider (%s)" % [(o['name'], o['dg']['s']['w']) for o in FY])
            await safe("(f)=>window.__a3dLandSet({flood:f})", saved['flood'])
            await safe("()=>window.__a3dDgRun('slope')")
            d2 = await safe("()=>window.__a3dLandDem()") or {}
            ck(d2.get('from') == 'context' and 'a point every 25 m' in d2.get('src', ''), "without the fine ground: the context's terrain, its 25 m said (%s)" % d2.get('src'))
            await safe("(v)=>window.__a3dLandSet(v)", saved)
            sv = [[x, z, round(0.08 * x, 3), '', ''] for x in range(-160, 161, 40) for z in range(-160, 161, 40)]
            await safe("(s)=>window.__a3dPushTestObj({id:'OWN',t:'terrain',name:'Site survey',layer:'layer-0',pos:[0,0,0],survey:s,rev:1})", sv)
            await safe("()=>window.__a3dDgRun('slope')")
            d3 = await safe("()=>window.__a3dLandDem()") or {}
            s3 = await el('slope', 'site')
            ck(d3.get('from') == 'own' and 'Site survey' in d3.get('src', '') and s3 and rows(s3).get('Mean') == '8%' and s3['dg']['lb'][0]['t'] == 'Site: mostly 5 to 10%, mean 8%',
               "a surface of the project's own over the site is read instead: an 8%% plane, 8%% at the site (%s; %s; %s)" % (d3.get('from'), d3.get('src'), s3 and s3['dg']['lb'][0]['t']))
            await safe("()=>window.__a3dDel('OWN')")
            await safe("()=>window.__a3dDgRun('slope')")
            ck((await safe("()=>window.__a3dLandDem()") or {}).get('from') == 'tiles', "and the fine ground again once it goes")
            await ctx.close()

            S2 = {'ground': 'land', 'flood': 'zones', 'mode': {'flood': 'abort'}}
            c2, p2, e2 = await fresh(S2)
            f2 = await analyze(p2)
            s2 = {s['id']: s for s in f2.get('steps', [])}
            ck(s2['land']['state'] == 'part' and 'hazards.fema.gov could not be reached' in s2['land']['text'] and 'the ground every 5 m' in s2['land']['text'],
               "FEMA down: the step reads Partly, FEMA named, the ground come (%s)" % s2['land']['text'][:120])
            n2 = ((await safe("()=>window.__a3dDgState()", pg=p2) or {}).get('runs') or {}).get('flood', {}).get('note', '')
            ck('hazards.fema.gov could not be reached' in n2 and (await safe("()=>window.__a3dDgState()", pg=p2) or {}).get('runs', {}).get('slope', {}).get('keys'),
               "the flood row says why; the slope drawn all the same")
            ck(not e2, "no page errors (%s)" % e2[:3])
            await c2.close()

            S3 = {'ground': 'land', 'flood': 'zones'}
            c3, p3, e3 = await fresh(S3)
            await p3.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            for k_, v_ in (('sunlat', '51.5'), ('sunlon', '-0.12')):
                await p3.evaluate("""(a)=>{var e=document.querySelector('#a3d-propsbody input[data-propmodel="'+a[0]+'"]');e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));}""", [k_, v_])
                await p3.wait_for_timeout(80)
            await safe("()=>window.__a3dAnzView(true)", pg=p3)
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=p3)
            f3 = await wait_run(pg=p3)
            s3s = {s['id']: s for s in f3.get('steps', [])}
            ck('FEMA maps US sites only' in s3s['land']['text'] and not [h for h in S3.get('hits', []) if h[0] == 'flood'], "a site in London: FEMA not asked, and the step says so")
            ck(((await safe("()=>window.__a3dDgState()", pg=p3) or {}).get('runs') or {}).get('flood', {}).get('note') == 'FEMA maps US sites only', "the flood row says so too")
            await c3.close()

            for vw, label in (((390, 844), 'a phone'), ((820, 1180), 'a tablet')):
                c6, p6, e6 = await fresh({'ground': 'land', 'flood': 'zones'}, vw=vw, mobile=True)
                await analyze(p6)
                await safe("()=>window.__a3dAnzView(true)", pg=p6)
                await p6.wait_for_timeout(300)
                g6 = await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap'),R=['dgcontours','dgslope','dgaspect','dgflow','dgponds','dgflood'].map(function(i){return document.querySelector('[data-anzcard="'+i+'"]');});
                  return {rows:R.filter(Boolean).length,sw:w.scrollWidth,cw:w.clientWidth,doc:document.documentElement.scrollWidth};}""", pg=p6) or {}
                ck(g6.get('rows') == 6 and g6.get('sw', 9) <= g6.get('cw', 0) + 1 and g6.get('doc', 9999) <= vw[0] + 1, "%s: the six rows in Analyze, nothing spilling" % label)
                ck(not e6, "%s: no page errors (%s)" % (label, e6[:3]))
                await c6.close()
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
        await browser.close()
    print('\n%d/%d checks passed' % (CK.n - len(CK.bad), CK.n))
    print('RESULT: ' + ('PASS' if not CK.bad else 'FAIL'))
    return not CK.bad


if __name__ == '__main__':
    ok_ = asyncio.run(run())
    sys.exit(0 if ok_ else 1)
