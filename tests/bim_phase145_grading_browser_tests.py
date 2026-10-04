#!/usr/bin/env python3
"""bim_phase145_grading_browser_tests.py -- V145: grading -- daylight slopes, a proposed surface,
cut and fill between surfaces, spot elevations and slope arrows.

Every number is held to a second calculation here in Python:

  1. A RECTANGULAR PAD on flat ground, in fill and in cut: the volume in closed form -- the pad's
     prism, a wedge along every edge, and a cone at each corner over the fan of slope lines the
     app draws there (15 degrees apart) -- and every daylight point at the slope's reach.
  2. AN L-SHAPED PAD (an inside corner): on flat ground, in closed form (the slopes meet in a valley
     on the corner's bisector); on sloping ground, against the defining surface -- the ground held
     between Z - d/fill and Z + d/cut, d the distance to the pad -- integrated on a 5 cm grid.
  3. CUT AND FILL BETWEEN SURFACES: two planes, a tent, and surfaces that half overlap, each
     against the integral worked by hand.
  4. GRADING AGAIN: out of date when a pad changes, updated in place, pads graded together, slopes
     that overlap, a pad off the surface, slopes that run off it.
  5. THE MAP, SPOTS AND ARROWS: cut and fill bands recomputed from the triangles; spot heights; arrows
     down a plane of known gradient.
  6. THE APP: Properties, the Analyze card, the commands, the plan and 3D, undo, LandXML, reload.

The harness never waits without a bound (V123).
"""
import asyncio, math, pathlib, re, sys, traceback
import numpy as np
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 120


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


S15 = math.sin(math.radians(15))


def rect_volume(A, P, H, r, corners=4):
    """prism + edge wedges + a cone over each corner's 6-ray fan (each H w^2 sin15)"""
    w = r * H
    return A * H + P * w * H / 2 + corners * H * w * w * S15


def l_flat_volume(A, P, H, r):
    """the L: five outside corners (fans), one inside corner (the offset lines meet; -2s of length)"""
    w = r * H
    return A * H + P * r * H * H / 2 - r * r * H ** 3 / 3 + 5 * H * w * w * S15


def poly_area(P):
    return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2


def dist_rect(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2])
    dz = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dz)


def grid_truth(L, Z, rc, rf, ground, ext, h=0.05):
    """cut and fill of the defining surface, on a grid of h"""
    xs = np.arange(ext[0] + h / 2, ext[2], h)
    zs = np.arange(ext[1] + h / 2, ext[3], h)
    X, Zg = np.meshgrid(xs, zs)
    D = np.full(X.shape, np.inf)
    n = len(L)
    for k in range(n):
        a, b = np.array(L[k], float), np.array(L[(k + 1) % n], float)
        d = b - a
        u = np.clip(((X - a[0]) * d[0] + (Zg - a[1]) * d[1]) / (d @ d), 0, 1)
        D = np.minimum(D, np.hypot(a[0] + d[0] * u - X, a[1] + d[1] * u - Zg))
    inside = np.zeros(X.shape, bool)
    j = n - 1
    for i in range(n):
        xi, zi = L[i]
        xj, zj = L[j]
        cond = ((zi > Zg) != (zj > Zg)) & (X < (xj - xi) * (Zg - zi) / ((zj - zi) if zj != zi else 1e-30) + xi)
        inside ^= cond
        j = i
    D[inside] = 0
    G = ground(X, Zg)
    Pr = np.minimum(np.maximum(G, Z - D / rf), Z + D / rc)
    dd = Pr - G
    return float(-dd[dd < 0].sum() * h * h), float(dd[dd > 0].sum() * h * h)


def tri_area(P, t):
    a, b, c = P[t[0]], P[t[1]], P[t[2]]
    return ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2


CF = [-2, -1, -0.5, -0.1, 0.1, 0.5, 1, 2]


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV145")
        ck(bool(has) and 'daylight' in has and 'tinvolume' in has, "__acad3dV145 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
        ck(mv and int(mv.group(1)) >= 145, "the app says V145 or later (%s)" % (mv and mv.group(1)))

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def flat(x0, n=12, step=5, f=None):
            pts = [[x0 + i * step, j * step, (f(i * step, j * step) if f else 0.0), '', ''] for i in range(n + 1) for j in range(n + 1)]
            return await safe("(p)=>window.__a3dMakeTerrain(p)", pts)

        async def pad(pts):
            return await safe("(p)=>window.__a3dSketch('poly',p)", pts)

        async def setp(pid, f, v):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}", pid)
            await page.fill('#a3d-propsbody [data-propf="%s"]' % f, str(v))
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(60)

        async def grade(pads, ter):
            return await safe("(a)=>window.__a3dGrade(a[0],a[1])", [pads, ter]) or {}

        async def height(i, x, z):
            return await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [i, x, z])

        async def info(i):
            return await safe("(i)=>window.__a3dGradeInfo(i)", i) or {}

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. a rectangular pad on flat ground")
            F1 = await flat(0)
            R1 = await pad([[20, 20], [40, 20], [40, 30], [20, 30]])
            await setp(R1, 'gradeelev', 1)
            await setp(R1, 'fillslope', 3)
            r = await grade([R1], F1)
            P1 = r.get('id')
            v = r.get('volume', {})
            want = rect_volume(200, 60, 1, 3)
            ck(r.get('created') and abs(v.get('fill', 0) - want) < 1e-6 and v.get('cut') == 0,
               "fill 1 m at 3:1: %.6f m3 = prism 200 + wedges 90 + corner fans %.4f (a true cone would be %.4f)" % (v.get('fill', 0), want - 290, math.pi * 3))
            ck(abs(v.get('fillArea', 0) - (200 + 60 * 3 + 4 * 6 * 0.5 * 9 * S15)) < 1e-6 and abs(v.get('area', 0) - 3600) < 1e-6,
               "over the pad, its slopes and their corner fans (%.4f m2), measured where both surfaces are (3600 m2)" % v.get('fillArea', 0))
            sp = await safe("(a)=>window.__a3dGradeSpokes(a[0],a[1])", [R1, F1]) or {}
            S = sp.get('spokes', [])
            ck(len(S) == 9 * 2 + 4 * 2 + 4 * 7 and all(s['r']['kind'] == 'daylight' and s['r']['dir'] == -1 for s in S),
               "%d slope lines (9 and 4 along the edges, 7 in each corner's fan), all in fill to daylight" % len(S))
            ck(all(abs(dist_rect(s['r']['end'], (20, 20, 40, 30)) - 3) < 1e-6 and abs(s['r']['h']) < 1e-9 for s in S),
               "every daylight point 3 m from the pad, on the ground")
            hs = [await height(P1, 30, 25), await height(P1, 30, 18.5), await height(P1, 30, 17.5), await height(P1, 30, 10)]
            ck(abs(hs[0] - 1) < 1e-9 and abs(hs[1] - 0.5) < 1e-9 and abs(hs[2] - 1 / 6) < 1e-9 and abs(hs[3]) < 1e-9,
               "the proposed ground: the pad at 1, 1.5 m out 0.5, 2.5 m out 0.1667, beyond the daylight the ground (%s)" % hs)
            T1 = await safe("(i)=>window.__a3dTerrainTin(i)", P1)
            ck(abs(sum(abs(tri_area(T1['P'], t)) for t in T1['tris']) - 3600) < 1e-6 and all(tri_area(T1['P'], t) > 0 for t in T1['tris']),
               "the proposed surface tiles the whole site, every triangle counter-clockwise")
            pc = [p for p in T1['P'] if 20 < p[0] < 40 and 20 < p[1] < 30]
            ck(not pc, "no existing point is left under the pad")
            # cut
            F2 = await flat(200)
            R2 = await pad([[220, 20], [240, 20], [240, 30], [220, 30]])
            await setp(R2, 'gradeelev', -1)
            await setp(R2, 'cutslope', 2)
            r = await grade([R2], F2)
            v = r.get('volume', {})
            ck(abs(v.get('cut', 0) - rect_volume(200, 60, 1, 2)) < 1e-6 and v.get('fill') == 0 and abs(v.get('net', 0) - v.get('cut', 0)) < 1e-12,
               "cut 1 m at 2:1: %.6f m3 (prism, wedges, fans), all of it to take away" % v.get('cut', 0))
            sp = await safe("(a)=>window.__a3dGradeSpokes(a[0],a[1])", [R2, F2]) or {}
            ck(all(s['r']['dir'] == 1 and abs((s['r']['h'] - (-1)) / s['r']['t'] - s['k'] / 2) < 1e-9 for s in sp['spokes']),
               "every slope line rises at 1 in 2 (its cut slope, not its fill slope)")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. an L-shaped pad")
            F3 = await flat(400, 16)
            L3 = [[425, 25], [455, 25], [455, 40], [440, 40], [440, 55], [425, 55]]
            R3 = await pad(L3)
            await setp(R3, 'gradeelev', 1.5)
            await setp(R3, 'fillslope', 2)
            r = await grade([R3], F3)
            v = r.get('volume', {})
            want = l_flat_volume(675, 120, 1.5, 2)
            ck(abs(v.get('fill', 0) - want) < 1e-6, "fill 1.5 m at 2:1 round an L: %.6f m3, in closed form %.6f" % (v.get('fill', 0), want))
            sp = await safe("(a)=>window.__a3dGradeSpokes(a[0],a[1])", [R3, F3]) or {}
            val = [s for s in sp['spokes'] if s['valley']]
            ck(len(val) == 1 and abs(val[0]['k'] - math.cos(math.pi / 4)) < 1e-12 and val[0]['p'] == [440, 40],
               "one valley line, on the inside corner's bisector, falling at cos 45 of the rate")
            ck(abs(math.hypot(val[0]['r']['end'][0] - 440, val[0]['r']['end'][1] - 40) - 3 * math.sqrt(2)) < 1e-6,
               "the valley daylights where the two offset lines meet (3 sqrt 2 out)")
            tr = [s for s in sp['spokes'] if s['r']['kind'] == 'valley']
            ck(tr and all(abs(abs(s['r']['end'][0] - 440) - abs(s['r']['end'][1] - 40)) < 1e-6 for s in tr),
               "the slope lines near the corner stop on the bisector (%d)" % len(tr))
            # sloping ground, against the defining surface
            F4 = await flat(600, 16, 5, lambda x, z: 0.06 * x + 0.02 * z)
            L4 = [[625, 25], [655, 25], [655, 40], [640, 40], [640, 55], [625, 55]]
            R4 = await pad(L4)
            Z4, rc4, rf4 = 2.6, 1.5, 2.5
            await setp(R4, 'gradeelev', Z4)
            await setp(R4, 'cutslope', rc4)
            await setp(R4, 'fillslope', rf4)
            r = await grade([R4], F4)
            P4 = r.get('id')
            v = r.get('volume', {})
            tc, tf = grid_truth([[x - 600, z] for x, z in L4], Z4, rc4, rf4, lambda X, Zg: 0.06 * X + 0.02 * Zg, (0, 0, 80, 80))
            ck(v and abs(v['cut'] - tc) / tc < 1e-3 and abs(v['fill'] - tf) / tf < 1e-3,
               "on a 6%% and 2%% slope, cut %.3f and fill %.3f against the defining surface's %.3f and %.3f (5 cm grid)" % (v.get('cut', 0), v.get('fill', 0), tc, tf))
            sp = await safe("(a)=>window.__a3dGradeSpokes(a[0],a[1])", [R4, F4]) or {}
            S = sp['spokes']
            ok_rate = all(s['r']['t'] < 1e-9 or abs((s['r']['h'] - Z4) / s['r']['t'] - s['r']['dir'] * s['k'] / (rc4 if s['r']['dir'] > 0 else rf4)) < 1e-9 for s in S)
            ok_day = all(abs(s['r']['h'] - (0.06 * (s['r']['end'][0] - 600) + 0.02 * s['r']['end'][1])) < 1e-6 for s in S if s['r']['kind'] == 'daylight')
            ck(ok_rate and ok_day and {-1, 1} <= {s['r']['dir'] for s in S},
               "every slope line rises at its cut slope or falls at its fill slope, and daylights on the ground")
            h = await height(P4, 640.3, 40.3)
            ck(abs(h - (Z4 + 0.3 / rc4)) < 1e-9, "in the inside corner's valley, 0.3 m from both edges, the slope stands %.4f (Z + d/cut)" % h)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. cut and fill between surfaces")
            A = await flat(1000, 10, 4)
            B = await flat(1000, 8, 5, lambda x, z: 0.1 * x - 1)
            V = await safe("(a)=>window.__a3dTinVolume(a[0],a[1])", [A, B]) or {}
            ck(abs(V['cut'] - 200) < 1e-9 and abs(V['fill'] - 1800) < 1e-9 and abs(V['area'] - 1600) < 1e-9 and abs(V['cutArea'] - 400) < 1e-9 and abs(V['fillArea'] - 1200) < 1e-9,
               "a plane crossing a plane at x=10: cut 200, fill 1800 m3, over 400 and 1200 m2, triangles of 4 m against 5 m (%s)" % V)
            Tn = await flat(1000, 8, 5, lambda x, z: 0.5 - abs(x - 20) / 20)
            V = await safe("(a)=>window.__a3dTinVolume(a[0],a[1])", [A, Tn]) or {}
            ck(abs(V['cut'] - 200) < 1e-9 and abs(V['fill'] - 200) < 1e-9 and abs(V['cutArea'] - 800) < 1e-9, "a tent: 200 m3 each way, by hand")
            Hf = await flat(1020, 8, 5, lambda x, z: 1.0)
            V = await safe("(a)=>window.__a3dTinVolume(a[0],a[1])", [A, Hf]) or {}
            ck(abs(V['fill'] - 800) < 1e-9 and abs(V['area'] - 800) < 1e-9 and V['cut'] == 0, "half overlapping: only where both are (800 m2, 800 m3)")
            V2 = await safe("(a)=>window.__a3dTinVolume(a[0],a[1])", [B, A]) or {}
            ck(abs(V2['cut'] - 1800) < 1e-9 and abs(V2['fill'] - 200) < 1e-9, "the other way round, cut and fill swap")
            await safe("(a)=>window.__a3dSelectFor(a)", [A, B])
            await safe("()=>window.__a3dRunCmd('cutfill')")
            ck('cut 200 m' in await toast() and 'fill 1800 m' in await toast(), "CUTFILL with two surfaces selected says so (%s)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 4. grading again")
            F6 = await flat(1200)
            R6 = await pad([[1220, 20], [1240, 20], [1240, 30], [1220, 30]])
            await setp(R6, 'gradeelev', 1)
            await setp(R6, 'fillslope', 3)
            n0 = len(await safe("()=>window.__a3dState().objs"))
            r = await grade([R6], F6)
            P6 = r['id']
            await safe("()=>window.__a3dUndo()")
            ck(len(await safe("()=>window.__a3dState().objs")) == n0 and not await info(P6), "undo takes the new proposed surface away")
            r = await grade([R6], F6)
            P6 = r['id']
            await setp(R6, 'gradeelev', 1.2)
            ck((await info(P6)).get('stale'), "changing the pad's elevation leaves the proposed surface out of date")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", P6)
            await page.wait_for_timeout(80)
            await page.click('#a3d-propsbody [data-propf="regrade"]')
            await page.wait_for_timeout(150)
            g = await info(P6)
            ck(not g['stale'] and abs(g['grading']['volume']['fill'] - rect_volume(200, 60, 1.2, 3)) < 1e-6 and
               len([x for x in await safe("()=>window.__a3dState().objs") if x.get('grading')]) == 5,
               "Grade Again updates it in place: 1.2 m, %.4f m3" % g['grading']['volume']['fill'])
            R6b = await pad([[1245, 45], [1255, 45], [1255, 55], [1245, 55]])
            await setp(R6b, 'gradeelev', 0.5)
            await setp(R6b, 'fillslope', 3)
            r = await grade([R6b], F6)
            ck(r['id'] == P6 and len(r['pads']) == 2 and abs(r['volume']['fill'] - rect_volume(200, 60, 1.2, 3) - rect_volume(100, 40, 0.5, 3)) < 1e-6,
               "grading a second pad keeps the first: the two volumes add (%.4f)" % r['volume']['fill'])
            R6c = await pad([[1244, 20], [1250, 20], [1250, 30], [1244, 30]])
            await setp(R6c, 'gradeelev', 1)
            r = await grade([R6c], F6)
            n6c = [x['name'] for x in await safe("()=>window.__a3dState().objs") if x['id'] == R6c][0]
            ck(r['overlaps'] and n6c in r['overlaps'][0], "slopes that overlap are named (%s)" % r['overlaps'])
            sp6 = await safe("(a)=>window.__a3dGradeSpokes(a[0],a[1])", [R6c, F6]) or {}
            ck(sp6.get('slopes') == {'cut': 2, 'fill': 2} and all(abs((s['r']['h'] - 1) / s['r']['t'] + s['k'] / 2) < 1e-9 for s in sp6['spokes'] if s['r']['t'] > 1e-9),
               "a pad with no slopes given falls at the default 2:1")
            await setp(R6c, 'gradeelev', '')
            r = await grade([R6b], F6)
            ck(not r['overlaps'] and len(r['pads']) == 2, "a pad with no elevation leaves the grading when it is graded again")
            Roff = await pad([[1255, 10], [1270, 10], [1270, 20], [1255, 20]])
            await setp(Roff, 'gradeelev', 1)
            r = await grade([Roff], F6)
            ck(any('not wholly on the existing surface' in e for e in r.get('errors', [])), "a pad off the surface is refused, by name (%s)" % r.get('errors'))
            await setp(Roff, 'gradeelev', '')
            Redge = await pad([[1202, 50], [1208, 50], [1208, 58], [1202, 58]])
            await setp(Redge, 'gradeelev', 1)
            await setp(Redge, 'fillslope', 3)
            r = await grade([Redge], F6)
            pe = [p for p in r['pads'] if p['id'] == Redge]
            ck(pe and pe[0]['offSurface'] > 0, "slopes that run off the surface are counted (%s)" % (pe and pe[0]['offSurface']))
            await setp(Redge, 'gradeelev', '')
            await grade([R6], F6)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the cut and fill map, spots and arrows")
            B1 = await safe("(i)=>window.__a3dTerrainBands(i,'cutfill')", P1) or {}
            T1 = await safe("(i)=>window.__a3dTerrainTin(i)", P1)
            want = [0.0] * 9
            for t_ in T1['tris']:
                d = sum(T1['H'][q] for q in t_) / 3
                k = next((i for i, th in enumerate(CF) if d < th), 8)
                want[k] += abs(tri_area(T1['P'], t_))
            ck(B1 and all(abs(want[i] - B1['bands'][i]['area']) < 1e-6 for i in range(9)) and abs(B1['bands'][7]['area'] - 200) < 1e-6,
               "the cut and fill bands: each triangle's depth at its centroid, the pad (200 m2) all 'Fill 1 to 2 m'")
            ck(await safe("(i)=>window.__a3dTerrainBands(i,'cutfill')", F1) is None, "an existing surface has no cut and fill of its own")
            sA = await safe("()=>window.__a3dAddPoint(30,25)")
            sB = await safe("()=>window.__a3dAddPoint(30,18.5)")
            sC = await safe("()=>window.__a3dAddPoint(-50,-50)")
            await safe("(a)=>window.__a3dSelectFor(a)", [sA, sB, sC])
            await safe("()=>window.__a3dRunCmd('spotelev')")
            e = [await safe("(i)=>window.__a3dSpotElev(i)", i) for i in (sA, sB, sC)]
            ck(abs(e[0]['h'] - 1) < 1e-9 and e[0]['surface'] == P1 and abs(e[1]['h'] - 0.5) < 1e-9 and e[2]['h'] is None,
               "SPOTELEV: on the proposed surface first -- the pad 1.00, the slope 0.50 -- and none off every surface")
            sD = await safe("()=>window.__a3dAddPoint(30,25)")
            await safe("(a)=>window.__a3dSelectFor(a)", [sD, F1])
            await safe("()=>window.__a3dRunCmd('spotelev')")
            e = await safe("(i)=>window.__a3dSpotElev(i)", sD)
            ck(abs(e['h']) < 1e-9 and e['surface'] == F1, "with the existing surface selected too, the spot reads it")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", P1)
            await page.wait_for_timeout(80)
            n0 = len(await safe("()=>window.__a3dState().objs"))
            await page.click('#a3d-propsbody [data-propf="gradespots"]')
            await page.wait_for_timeout(150)
            new = (await safe("()=>window.__a3dState().objs"))[n0:]
            hv = [await safe("(i)=>window.__a3dSpotElev(i)", x['id']) for x in new]
            ck(len(new) == 4 and all(abs(x['h'] - 1) < 1e-9 for x in hv) and sorted((x['x'], x['z']) for x in hv) == [(20, 20), (20, 30), (40, 20), (40, 30)],
               "Spot the Pad Corners: four spots, each 1.00")
            await safe("()=>window.__a3dSetPlanView&&window.__a3dSetPlanView()")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dZoomToSelection();}", P1)
            await page.wait_for_timeout(250)
            sh = await safe("()=>window.__a3dSpotsShown()") or []
            mine = {x['id']: x for x in sh}
            ck(sA in mine and mine[sA]['text'] == '1.00' and mine[sC]['text'] == 'no surface', "the plan labels them (%s, %s)" % (mine.get(sA, {}).get('text'), mine.get(sC, {}).get('text')))
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", F4)
            await page.wait_for_timeout(60)
            await page.check('#a3d-propsbody [data-propf="terrarrows"]')
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dZoomToSelection();}", F4)
            await page.wait_for_timeout(250)
            d4 = [d for d in (await safe("()=>window.__a3dTerrainShown()") or []) if d['id'] == F4]
            ar = (d4[0]['arrows'] or {}) if d4 else {}
            g0 = math.hypot(0.06, 0.02)
            ck(ar.get('count', 0) > 20 and all(abs(a['dx'] + 0.06 / g0) < 1e-9 and abs(a['dz'] + 0.02 / g0) < 1e-9 and abs(a['slope'] - 100 * g0) < 1e-9 for a in ar['list']),
               "Slope Arrows on a 6%%/2%% plane: %d arrows, every one straight down it at %.3f%%" % (ar.get('count', 0), 100 * g0))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the app")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", R4)
            await page.wait_for_timeout(60)
            hb = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('data-propf="cutslope"' in hb and 'data-propf="fillslope"' in hb and 'Proposed' in hb, "a pad's Properties: its cut and fill slopes, and the surface it is graded into")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", P4)
            await page.wait_for_timeout(60)
            hb = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('data-graderow="cut"' in hb and 'data-graderow="net"' in hb and 'Up to date' in hb and 'Survey Check' not in hb,
               "a proposed surface's Grading group: cut, fill, net, up to date; and no survey check -- it was not surveyed")
            ck('value="cutfill"' in hb, "its Colour By offers cut and fill")
            await page.select_option('#a3d-propsbody [data-propf="terrview"]', 'cutfill')
            await page.wait_for_timeout(200)
            lg = await safe("()=>window.__a3dTerrainLegend()")
            ck(lg and 'cut and fill' in (await safe("()=>JSON.stringify(window.__a3dTerrainLegend())")) or (lg and lg['rows'] and lg['rows'][0].startswith('Cut')),
               "choosing it colours the plan, with a cut and fill legend (%s)" % (lg and lg['rows']))
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", F4)
            hb = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('value="cutfill"' not in hb and 'Survey Check' in hb, "an existing surface offers no cut and fill, and keeps its survey check")
            sh = {d['id']: d for d in (await safe("()=>window.__a3dTerrainShown()") or [])}
            ck(sh.get(F4, {}).get('dashed') and sh.get(P4, {}).get('grading') and not sh.get(A, {}).get('dashed'),
               "in plan the existing ground under a proposed surface is dashed; one with none is not")
            await safe("()=>window.__a3dSetView('iso')")
            await page.wait_for_timeout(350)
            ids3 = [x['id'] for x in (await safe("()=>window.__a3dTerrain3d()") or [])]
            ck(P4 in ids3 and F4 not in ids3 and A in ids3, "in 3D the proposed surface stands in for the existing one")
            await safe("()=>window.__a3dSetPlanView&&window.__a3dSetPlanView()")
            await page.click('#a3d-rail [data-tab="analyze"]')
            await page.wait_for_timeout(250)
            C = {c['id']: c for c in (await safe("()=>window.__a3dAnalyzeCards()") or [])}
            ck('grading' in C and C['grading']['state'] == 'on' and 'cut' in C['grading']['status'] and 'm³' in C['grading']['status'],
               "a Grading card in Analyze (%s)" % C.get('grading', {}).get('status'))
            ids = [c for c in C]
            ck(ids.index('grading') == ids.index('terrain') + 1, "after the terrain card")
            await setp(R1, 'gradeelev', 1.1)
            C = {c['id']: c for c in (await safe("()=>window.__a3dAnalyzeCards()") or [])}
            ck(C['grading']['state'] == 'stale' and 'changed since' in C['grading']['status'], "the card says when the pads have changed (%s)" % C['grading']['status'])
            await grade([R1], F1)
            await setp(R6, 'gradeelev', 1.3)
            v1 = (await info(P1))['grading']['volume']['fill']
            await safe("(i)=>window.__a3dSelectFor([i])", P6)
            await safe("()=>window.__a3dRunCmd('grade')")
            g = await info(P6)
            ck(not g['stale'] and abs(g['grading']['volume']['fill'] - rect_volume(200, 60, 1.3, 3) - rect_volume(100, 40, 0.5, 3)) < 1e-6 and
               (await info(P1))['grading']['volume']['fill'] == v1,
               "GRADE with a proposed surface selected grades its own pads again, on its own ground (%s)" % await toast())
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return /^(GRADE|CUTFILL|CUTFILLMAP|SPOTELEV|SLOPEARROWS)$/.test(c.name);}).map(function(c){return c.name;})") or []
            ck(len(cat) == 5, "the five commands are in the catalogue (%s)" % sorted(cat))
            for q_, n_ in (('daylight', 'GRADE'), ('earthwork volume', 'CUTFILL'), ('spot elevation', 'SPOTELEV'), ('slope arrows', 'SLOPEARROWS'), ('cut fill map', 'CUTFILLMAP')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dRunCmd('cutfillmap')")
            G = [x for x in (await safe("()=>window.__a3dState().objs")) if x.get('grading')]
            ck(G and all(x.get('tview') == 'cutfill' for x in G), "CUTFILLMAP colours every proposed surface")
            await safe("()=>window.__a3dRunCmd('cutfillmap')")
            ck(not any(x.get('tview') for x in (await safe("()=>window.__a3dState().objs")) if x.get('grading')), "and again takes the colours off")
            sk0 = await pad([[1300, 0], [1310, 0], [1310, 10]])
            await safe("(i)=>window.__a3dSelectFor([i])", sk0)
            await safe("()=>window.__a3dRunCmd('grade')")
            ck('Pad Elevation' in await toast(), "GRADE on an outline with no elevation says what to give it (%s)" % await toast())
            doc = await safe("(i)=>window.__a3dLandXmlDoc([i])", P1) or {}
            T1 = await safe("(i)=>window.__a3dTerrainTin(i)", P1)
            ck(doc.get('surfaces') == 1 and doc.get('faces') == len(T1['tris']), "the proposed surface goes out as LandXML, like any other")
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            g = await info(P4)
            o = [x for x in (await safe("()=>window.__a3dState().objs")) if x['id'] == R4][0]
            e = await safe("(i)=>window.__a3dSpotElev(i)", sA)
            ck(g and not g['stale'] and abs(g['grading']['volume']['cut'] - v['cut']) < 1e-9 and o.get('cutSlope') == 1.5 and o.get('fillSlope') == 2.5 and abs(e['h'] - 1.1) < 1e-9,
               "after a reload: the grading, its volumes, the slopes and the spots are all there")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled at: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
