#!/usr/bin/env python3
"""bim_phase108_terrain_browser_tests.py -- V108: survey points, TIN surface, contours, earthwork.

Asserted on the model against invariants and hand values, not against the build's own output:
  1. DELAUNAY: on 40 scattered points every circumcircle is empty of other points, the triangle
     count is 2n - h - 2 (h hull points), and the triangles tile the convex hull exactly. A 5 x 5
     grid, where every square's corners are cocircular, still gives 32 triangles tiling 64 m2;
     points on one line give none.
  2. CONTOURS on a planar surface y = 100 + 0.1x - 0.05z lie exactly on the plane, every fifth is
     an index contour, and the 101 m contour is 22.3607 m long -- the length of the line
     0.1x - 0.05z = 1 across the 30 x 20 m surface.
  3. SURVEY, driven through its dialog: PNEZD in US survey feet with a header line, True North at
     30 deg, base elevation 340. Point 2 (100 usft north of the base, 5 usft up) lands at
     x = 30.480061 sin 30, z = -30.480061 cos 30, y = 1.524003; the header is reported, the base
     is kept on the site and offered back.
  4. EARTHWORK by the TIN prism method, pads given their elevation in Properties -- driven:
     a 4 m pyramid over a 10 x 10 m pad is 133.333 m3 of cut; a pad across a 0.2 slope whose
     elevation line falls INSIDE triangles (x = 27.5, not on a TIN edge) is 0.125 m3 cut and
     15.125 m3 fill; 2 m of flat ground over 20 m2 is 40 m3; a pad half
     off the surface reports the 10 m2 it could not measure. The Earthwork schedule and
     Properties say the same, and name the method.
  5. KEPT: pad elevation is one undo step; interval, pads and surfaces survive a reload; zoom
     extents includes a surface; contours draw in plan only.
"""
import asyncio, math, pathlib, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
USFT = 1200 / 3937


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


def near(a, b, tol=1e-6):
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(a - b) <= tol


def area2(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def hull(pts):
    s = sorted(set(map(tuple, pts)))
    lo, up = [], []
    for p in s:
        while len(lo) >= 2 and area2(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(s):
        while len(up) >= 2 and area2(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def poly_area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def circum(a, b, c):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    ux = ((a[0]**2 + a[1]**2) * (b[1] - c[1]) + (b[0]**2 + b[1]**2) * (c[1] - a[1]) + (c[0]**2 + c[1]**2) * (a[1] - b[1])) / d
    uz = ((a[0]**2 + a[1]**2) * (c[0] - b[0]) + (b[0]**2 + b[1]**2) * (a[0] - c[0]) + (c[0]**2 + c[1]**2) * (b[0] - a[0])) / d
    return ux, uz, (a[0] - ux)**2 + (a[1] - uz)**2


def rect(i, x0, z0, x1, z1):
    return {'id': 'P%d' % i, 't': 'sketch', 'name': 'Pad_%d' % i, 'col': '#5ec4b8', 'pos': [0, 0, 0],
            'pts': [[x0, z0], [x1, z0], [x1, z1], [x0, z1]], 'y': 0, 'closed': True}


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(260)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        async def safe(js, arg=None):
            try:
                return await (page.evaluate(js, arg) if arg is not None else page.evaluate(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def prop_set(obj_id, key, v):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", obj_id)
            await page.wait_for_timeout(80)
            try:
                loc = page.locator('input[data-propf="%s"]' % key)
                await loc.fill(v, timeout=3000)
                await loc.press('Enter', timeout=3000)
                await page.wait_for_timeout(150)
            except Exception as e:
                print('      (driving %s failed: %s)' % (key, str(e)[:120]))
            await blur()

        print('\n-- 1. Delaunay')
        seed, P = 12345, []
        for _ in range(40):
            seed = (seed * 1103515245 + 12345) % 2**31
            x = (seed % 50000) / 1000.0
            seed = (seed * 1103515245 + 12345) % 2**31
            P.append([x, (seed % 30000) / 1000.0])
        T = (await safe("(p)=>window.__a3dDelaunay(p)", P)) or []
        empty = all(all((P[k][0] - cx)**2 + (P[k][1] - cz)**2 >= r2 * (1 - 1e-9) for k in range(len(P)) if k not in t)
                    for t in T for (cx, cz, r2) in [circum(P[t[0]], P[t[1]], P[t[2]])])
        H = hull(P)
        ck(len(T) > 0 and empty and all(area2(P[t[0]], P[t[1]], P[t[2]]) > 0 for t in T), 'every circumcircle is empty and every triangle counter-clockwise (%d)' % len(T))
        ck(len(T) == 2 * len(P) - len(H) - 2, 'triangles = 2n - h - 2 = %d (got %d)' % (2 * len(P) - len(H) - 2, len(T)))
        ck(abs(sum(abs(area2(P[t[0]], P[t[1]], P[t[2]])) / 2 for t in T) - poly_area(H)) < 1e-6, 'they tile the convex hull exactly')
        G = [[2 * i, 2 * j] for i in range(5) for j in range(5)]
        TG = (await safe("(p)=>window.__a3dDelaunay(p)", G)) or []
        ck(len(TG) == 32 and abs(sum(abs(area2(G[t[0]], G[t[1]], G[t[2]])) / 2 for t in TG) - 64) < 1e-9, 'a 5 x 5 grid of cocircular squares: 32 triangles tiling 64 m2 (%d)' % len(TG))
        ck((await safe("()=>window.__a3dDelaunay([[0,0],[1,1],[2,2],[3,3]])")) == [], 'points on one line make no triangles')

        print('\n-- 2. contours on a plane')
        plane = lambda x, z: 100 + 0.1 * x - 0.05 * z
        mdl = [[x, z, plane(x, z), '', ''] for x in range(0, 31, 5) for z in range(0, 21, 5)] + [[x, z, plane(x, z), '', ''] for x, z in ((7.3, 3.1), (12.9, 17.2), (21.4, 9.8), (26.6, 14.1))]
        TP = await safe("(m)=>window.__a3dMakeTerrain(m)", mdl)
        cs = (await safe("(i)=>window.__a3dContours(i,0.5)", TP)) or []
        on = all(abs(plane(p[0], p[1]) - c['level']) < 1e-9 for c in cs for s in c['segs'] for p in s)
        levels = [round(c['level'], 6) for c in cs if any(math.dist(s[0], s[1]) > 1e-9 for s in c['segs'])]
        ck(on and levels == [99.5 + 0.5 * k for k in range(7)], 'every contour point is on the plane; levels 99.5 to 102.5 (%s)' % levels)
        idx = {round(c['level'], 6): c['index'] for c in cs}
        ck(idx.get(100.0) is True and idx.get(102.5) is True and idx.get(101.0) is False, 'every fifth is an index contour: 100.0 and 102.5')
        c101 = [c for c in cs if abs(c['level'] - 101) < 1e-9]
        L = sum(math.dist(s[0], s[1]) for s in c101[0]['segs']) if c101 else 0
        ck(abs(L - math.hypot(10, 20)) < 1e-9, 'the 101 m contour is %.4f m long, as the line 0.1x - 0.05z = 1 across the surface (%.4f)' % (math.hypot(10, 20), L))

        print('\n-- 3. SURVEY, through its dialog')
        await safe("()=>window.__a3dSetTrueNorth(30)")
        await blur()
        await palette_run(page, 'SURVEY')
        rows = 'Point,Northing,Easting,Elevation,Description\n1,5000.000,2000.000,340.000,BASE\n2,5100.000,2000.000,345.000,N100\n3,5000.000,2100.000,342.000,E100\n4,5100.000,2100.000,350.000,NE CORNER\n5,5050.000,2050.000,346.000,MID'
        before = set(o['id'] for o in ((await safe("()=>window.__a3dState()")) or {}).get('objs', []))
        try:
            await page.locator('.a3d-dlg textarea[data-a3dp="pts"]').fill(rows, timeout=3000)
            await page.select_option('.a3d-dlg select[data-a3dp="units"]', 'usft', timeout=3000)
            await page.locator('.a3d-dlg input[data-a3dp="bz"]').fill('340', timeout=3000)
            await page.locator('.a3d-dlg [data-a3dlg="ok"]').click(timeout=3000)
            await page.wait_for_timeout(300)
        except Exception as e:
            print('      (driving the dialog failed: %s)' % str(e)[:140])
        objs = ((await safe("()=>window.__a3dState()")) or {}).get('objs', [])
        new = [o for o in objs if o['id'] not in before and o.get('t') == 'terrain']
        TS = new[0]['id'] if new else None
        tin = (await safe("(i)=>window.__a3dTerrainTin(i)", TS)) or {'P': [], 'H': []}
        u, s30, c30 = USFT, 0.5, math.cos(math.radians(30))
        want2 = (100 * u * s30, -100 * u * c30, 5 * u)
        want3 = (100 * u * c30, 100 * u * s30, 2 * u)
        ok = len(tin['P']) == 5 and all(abs(a - b) < 1e-6 for a, b in zip((tin['P'][1][0], tin['P'][1][1], tin['H'][1]), want2)) \
            and all(abs(a - b) < 1e-6 for a, b in zip((tin['P'][2][0], tin['P'][2][1], tin['H'][2]), want3))
        ck(ok, 'US survey feet, True North 30, base 340: point 2 at (%.6f, %.6f, %.6f), point 3 at (%.6f, %.6f, %.6f)' % (want2 + want3))
        sv = new[0].get('survey', []) if new else []
        ck(len(sv) == 5 and sv[3][3] == '4' and sv[3][4] == 'NE CORNER' and (new[0].get('source') or {}).get('skipped') == [1],
           'point numbers and descriptions kept; the header line is reported as not read')
        await blur()
        await palette_run(page, 'SURVEY')
        pre = await safe("()=>['bn','be','bz'].map(function(k){var e=document.querySelector('.a3d-dlg [data-a3dp=\"'+k+'\"]');return e?e.value:null;})")
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"cancel\"]');if(b)b.click();}")
        ck(pre == ['5000', '2000', '340'], 'the base point is kept on the site and offered back (%s)' % pre)
        await safe("()=>window.__a3dSetTrueNorth(0)")

        print('\n-- 4. earthwork')
        await safe("(o)=>window.__a3dTestSetObjs(o)", [rect(1, -5, -5, 5, 5), rect(2, 22, 0, 28, 5), rect(3, 41, 1, 46, 5), rect(4, 48, 0, 52, 5)])
        T1 = await safe("(m)=>window.__a3dMakeTerrain(m)", [[-5, -5, 100, '', ''], [5, -5, 100, '', ''], [5, 5, 100, '', ''], [-5, 5, 100, '', ''], [0, 0, 104, '', '']])
        T2 = await safe("(m)=>window.__a3dMakeTerrain(m)", [[x, z, 100 + 0.2 * (x - 20), '', ''] for x in (20, 25, 30) for z in (0, 5, 10)])
        T3 = await safe("(m)=>window.__a3dMakeTerrain(m)", [[x, z, 102, '', ''] for x in (40, 45, 50) for z in (0, 5, 10)])
        for pid, v in (('P1', '100'), ('P2', '101.5'), ('P3', '100'), ('P4', '100')):
            await prop_set(pid, 'gradeelev', v)
        ew = {r['pad']: r for r in ((await safe("()=>window.__a3dScheduleRows('earthwork')")) or {}).get('rows', [])}
        p1, p2, p3, p4 = (ew.get('Pad_%d' % k, {}) for k in (1, 2, 3, 4))
        ck(near(p1.get('cut'), 400 / 3) and near(p1.get('fill'), 0) and p1.get('method') == 'TIN prism', 'a 4 m pyramid over a 10 x 10 m pad: %.4f m3 cut (%s)' % (400 / 3, p1.get('cut')))
        ck(near(p2.get('cut'), 0.125) and near(p2.get('fill'), 15.125) and near(p2.get('net'), -15), 'across a 0.2 slope, the line inside triangles: 0.125 m3 cut, 15.125 m3 fill, net -15 = -0.5 m x 30 m2 (%s, %s)' % (p2.get('cut'), p2.get('fill')))
        ck(near(p3.get('cut'), 40) and near(p3.get('fill'), 0), '2 m of flat ground over 20 m2: 40 m3 (%s)' % p3.get('cut'))
        ck(near(p4.get('onSurface'), 10) and near(p4.get('cut'), 20) and '10.00 m² off the surface' in p4.get('note', ''), 'half off the surface: 10 m2 measured, 20 m3, and the 10 m2 off it is said (%r)' % p4.get('note'))
        await safe("()=>{window.__a3dSelectFor(['P1']);window.__a3dRefreshProps();}")
        txt = (await safe("()=>document.body.innerText")) or ''
        ck('cut 133.33 m³, fill 0.00 m³ against Surface_' in txt and '(TIN prism)' in txt, 'Properties shows the same volumes and names the method')
        await blur()
        await safe("()=>window.__a3dUndo()")
        ew2 = {r['pad'] for r in ((await safe("()=>window.__a3dScheduleRows('earthwork')")) or {}).get('rows', [])}
        ck('Pad_4' not in ew2 and 'Pad_1' in ew2, 'a pad elevation is one undo step')
        await prop_set('P4', 'gradeelev', '100')

        print('\n-- 5. interval, drawing, extents, reload')
        await prop_set(T3, 'terrint', '0.25')
        await safe("()=>{window.__a3dFlat(true);window.__a3dSelectFor([]);window.__a3dTestPaint();}")
        shown = {d['id']: d for d in ((await safe("()=>window.__a3dTerrainShown()")) or [])}
        ck(near(shown.get(T3, {}).get('step'), 0.25) and shown.get(T1, {}).get('segments', 0) > 0 and len(shown) == 3,
           'the owner interval is used, and all three surfaces draw contours in plan')
        await safe("()=>{window.__a3dFlat(false);window.__a3dTestPaint();}")
        ck(not (await safe("()=>window.__a3dTerrainShown()")), 'not in 3D')
        await safe("()=>window.__a3dFlat(true)")
        bb = await safe("(i)=>window.__a3dWorldBounds([i])", T1)
        ck(isinstance(bb, dict) and bb.get('mn') == [-5, 100, -5] and bb.get('mx') == [5, 104, 5], 'zoom extents sees a surface: x, y, z from (-5, 100, -5) to (5, 104, 5) (%s)' % bb)
        await page.wait_for_timeout(1500)
        await page.reload()
        await page.wait_for_timeout(2300)
        ew3 = {r['pad']: r for r in ((await safe("()=>window.__a3dScheduleRows('earthwork')")) or {}).get('rows', [])}
        t3 = (await safe("(i)=>window.__a3dObjSnapshot(i)", T3)) or {}
        ck(near(ew3.get('Pad_1', {}).get('cut'), 400 / 3) and near(ew3.get('Pad_4', {}).get('cut'), 20) and t3.get('interval') == 0.25,
           'surfaces, pads and the interval survive a reload')
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
