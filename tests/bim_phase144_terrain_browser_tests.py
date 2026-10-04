#!/usr/bin/env python3
"""bim_phase144_terrain_browser_tests.py -- V144: terrain -- breaklines, a boundary, LandXML, analysis.

Every result is held to a second calculation here in Python:

  1. LANDXML IN: a hand-written file in feet, one face clockwise and one marked invisible -- the
     surface keeps the file's own triangles, each turned counter-clockwise, the invisible one left
     out, every point placed in metres by the first point; refusals for what is not LandXML.
  2. SLOPE, ASPECT, ELEVATION: planes of known gradient fall in the band their slope (%) names; a
     plane faces where it falls, turned by True North; elevation bands recomputed from the triangles.
  3. BREAKLINES: each drawn segment is covered by TIN edges end to end; crossing lines meet at a
     shared vertex; a ridge coded BL1 in the survey is held, where without the code it is cut.
  4. THE BOUNDARY: the triangles fill exactly the boundary's area and nothing outside it; the points
     outside are left out, counted, and the survey check still passes.
  5. LANDXML OUT: a survey in US survey feet, turned 30 degrees, comes back out with its own
     northings, eastings and elevations; read back in, it is the same surface.
  6. THE APP: the Properties group, the plan's colours and legend, the Analyze card, the commands,
     IMPORTCAD, Remove, undo, and the reload.

The harness never waits without a bound (V123).
"""
import asyncio, math, pathlib, re, sys, tempfile, traceback, xml.etree.ElementTree as ET
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
STALL = 90


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


def tri_area(P, t):
    a, b, c = P[t[0]], P[t[1]], P[t[2]]
    return ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2


def covered(tin, A, B, tol=1e-6):
    """the length of segment AB that the TIN's edges lie along"""
    P = tin['P']
    dx, dz = B[0] - A[0], B[1] - A[1]
    L2 = dx * dx + dz * dz
    seen, tot = set(), 0.0

    def on(p):
        t = ((p[0] - A[0]) * dx + (p[1] - A[1]) * dz) / L2
        ex, ez = A[0] + dx * t - p[0], A[1] + dz * t - p[1]
        return -tol <= t <= 1 + tol and ex * ex + ez * ez < tol

    for tr in tin['tris']:
        for k in range(3):
            u, v = tr[k], tr[(k + 1) % 3]
            key = (min(u, v), max(u, v))
            if key in seen:
                continue
            if on(P[u]) and on(P[v]):
                seen.add(key)
                tot += math.hypot(P[u][0] - P[v][0], P[u][1] - P[v][1])
    return tot


def in_rect(p, r, tol=1e-9):
    return r[0] - tol <= p[0] <= r[2] + tol and r[1] - tol <= p[1] <= r[3] + tol


ASPECT_NAMES = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']


async def run():
    ck = CK
    TMP = pathlib.Path(tempfile.mkdtemp(prefix='v144_'))   # outside the repo
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

        has = await safe("()=>window.__acad3dV144")
        ck(bool(has) and 'breaklines' in has and 'landxmlin' in has, "__acad3dV144 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def tin(i):
            return await safe("(i)=>window.__a3dTerrainTin(i)", i)

        async def height(i, x, z):
            return await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [i, x, z])

        async def obj(i):
            return await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]||null", i)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 0. the version")
            ver = await safe("()=>window.__a3dAppVersion?window.__a3dAppVersion():null")
            src = HTML.read_text(encoding='utf-8')
            # AMENDED FOR V145: the version moves on with each phase; V144 or later
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", src)
            vn = int(mv.group(1)) if mv else 0
            ck(vn >= 144, "the app says V144 or later (V%d)" % vn)

            # ---------------------------------------------------------------------------------
            print("\n-- 1. LandXML in")
            FT = 0.3048
            pts = {1: (1000.0, 2000.0, 100.0), 2: (1000.0, 2100.0, 110.0), 3: (1100.0, 2100.0, 120.0),
                   4: (1100.0, 2000.0, 105.0), 5: (1050.0, 2200.0, 130.0)}
            xmlin = ('<?xml version="1.0"?><LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" version="1.2">'
                     '<Units><Imperial linearUnit="foot" areaUnit="squareFoot" volumeUnit="cubicYard" angularUnit="decimal degrees" directionUnit="decimal degrees"/></Units>'
                     '<Surfaces><Surface name="Existing Ground"><Definition surfType="TIN"><Pnts>' +
                     ''.join('<P id="%d">%r %r %r</P>' % (k, v[0], v[1], v[2]) for k, v in pts.items()) +
                     '</Pnts><Faces><F>1 2 3</F><F>1 4 3</F><F i="1">2 5 3</F></Faces></Definition></Surface></Surfaces></LandXML>')
            r = await safe("(t)=>window.__a3dLandXmlImport(t,'eg.xml')", xmlin) or {}
            ck(r.get('ids') and r.get('units') == 'ft' and r['surfaces'][0]['name'] == 'Existing Ground' and r['surfaces'][0]['faces'] == 2,
               "one surface, in feet, named from the file, with 2 faces (the invisible one left out) (%s)" % r)
            lid = (r.get('ids') or [None])[0]
            T = await tin(lid) or {'P': [], 'H': [], 'tris': []}
            ck(T.get('ownFaces') and len(T['tris']) == 2 and len(T['P']) == 5, "it keeps the file's own triangles, not a new triangulation")
            exp = [((v[1] - 2000.0) * FT, -(v[0] - 1000.0) * FT, v[2] * FT) for k, v in sorted(pts.items())]
            ck(all(abs(T['P'][i][0] - exp[i][0]) < 1e-6 and abs(T['P'][i][1] - exp[i][1]) < 1e-6 and abs(T['H'][i] - exp[i][2]) < 1e-6 for i in range(5)),
               "every point in metres: east to x, north to -z, from the first point; elevations kept")
            ck(all(tri_area(T['P'], t) > 0 for t in T['tris']), "each face counter-clockwise in plan, the clockwise one turned")
            c = [(exp[0][k] + exp[1][k] + exp[2][k]) / 3 for k in range(3)]
            h = await height(lid, c[0], c[1])
            ck(h is not None and abs(h - c[2]) < 1e-9, "the surface at a face's centroid is the face's own plane (%s vs %.6f)" % (h, c[2]))
            c5 = [(exp[1][k] + exp[4][k] + exp[2][k]) / 3 for k in range(3)]
            ck(await height(lid, c5[0], c5[1]) is None, "the invisible face is not surface")
            st = await safe("()=>{var s=window.__a3dSite();return s&&s.surveyBase;}")
            ck(st and abs(st['n'] - 1000) < 1e-9 and abs(st['e'] - 2000) < 1e-9 and st['units'] == 'ft', "with no survey base yet, the first point becomes it (%s)" % st)
            for bad_, want in (('not xml <', 'is not XML'), ('<?xml version="1.0"?><Foo/>', 'is not a LandXML file'),
                               ('<?xml version="1.0"?><LandXML><Surfaces/></LandXML>', 'No TIN surface'),
                               ('<?xml version="1.0"?><LandXML><Units><Metric linearUnit="millimeter"/></Units><Surfaces><Surface><Definition><Pnts><P id="1">0 0 0</P></Pnts></Definition></Surface></Surfaces></LandXML>', 'Millimetre')):
                rr = await safe("(t)=>window.__a3dLandXmlImport(t,'x.xml')", bad_) or {}
                ck(want in (rr.get('error') or ''), "refused: %s (%s)" % (want, rr.get('error')))
            rr = await safe("(i)=>window.__a3dTerrainEdit(i,'faces')", lid)
            T2 = await tin(lid)
            ck(rr and not T2['ownFaces'] and len(T2['tris']) == 3, "Re-triangulate drops the file's faces for Delaunay's (%d triangles)" % len(T2['tris']))
            await safe("()=>window.__a3dUndo()")
            T3 = await tin(lid)
            ck(T3 and T3['ownFaces'] and len(T3['tris']) == 2, "and undo brings them back")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. slope, aspect, elevation")

            async def plane(a, b, off=0.0, step=4):
                pts_ = [[off + i * step, j * step, a * (off + i * step) + b * j * step, '', ''] for i in range(11) for j in range(11)]
                return await safe("(p)=>window.__a3dMakeTerrain(p)", pts_)

            bands_s = [0, 2, 5, 8.33, 15, 25, 50, float('inf')]
            for a, b in ((0.01, 0.0), (0.05, 0.02), (0.1, 0.03), (0.2, 0.2), (0.6, 0.0)):
                pid = await plane(a, b, 200)
                sl = 100 * math.hypot(a, b)
                k = next(i for i in range(7) if sl < bands_s[i + 1])
                B = await safe("(i)=>window.__a3dTerrainBands(i,'slope')", pid) or {}
                ck(abs(B['total'] - 1600) < 1e-6 and abs(B['bands'][k]['area'] - 1600) < 1e-6 and set(B['tri']) == {k},
                   "a plane of %.2f%% falls wholly in %s (%s m2)" % (sl, B['bands'][k]['label'], B['bands'][k]['area']))
                await safe("()=>window.__a3dUndo()")
            for a, b, want in ((0.1, 0, 'W'), (-0.1, 0, 'E'), (0, -0.1, 'S'), (0, 0.1, 'N'), (0.1, 0.1, 'NW'), (-0.1, 0.1, 'NE')):
                pid = await plane(a, b, 200)
                B = await safe("(i)=>window.__a3dTerrainBands(i,'aspect')", pid) or {}
                got = [x['label'] for x in B['bands'] if x['area'] > 0]
                ck(got == ['Facing ' + want], "rising %s, a plane faces %s (%s)" % ('east' if a > 0 else 'west' if a < 0 else 'north' if b < 0 else 'south', want, got))
                await safe("()=>window.__a3dUndo()")
            pid = await plane(0.01, 0, 200)
            B = await safe("(i)=>window.__a3dTerrainBands(i,'aspect')", pid)
            ck([x['label'] for x in B['bands'] if x['area'] > 0] == ['Flat (under 2%)'], "a 1% plane is flat, facing nowhere")
            await safe("()=>window.__a3dUndo()")
            # True North 90: project east is north, so ground rising to +x falls to the south
            await safe("()=>window.__a3dSetTrueNorth(90)")
            pid = await plane(0.1, 0, 200)
            B = await safe("(i)=>window.__a3dTerrainBands(i,'aspect')", pid)
            ck([x['label'] for x in B['bands'] if x['area'] > 0] == ['Facing S'], "turned by True North 90: the same plane faces S")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSetTrueNorth(0)")
            # elevation: a bowl, recomputed band by band from its own triangles
            bowl = [[300 + i * 3, j * 3, ((i - 6) ** 2 + (j - 6) ** 2) * 0.05, '', ''] for i in range(13) for j in range(13)]
            bid = await safe("(p)=>window.__a3dMakeTerrain(p)", bowl)
            T = await tin(bid)
            B = await safe("(i)=>window.__a3dTerrainBands(i,'elevation')", bid)
            lo, hi = min(T['H']), max(T['H'])
            n = len(B['bands'])
            want = [0.0] * n
            for tr in T['tris']:
                hm = sum(T['H'][q] for q in tr) / 3
                want[min(n - 1, max(0, int((hm - lo) // ((hi - lo) / n))))] += abs(tri_area(T['P'], tr))
            ck(n == 7 and all(abs(want[i] - B['bands'][i]['area']) < 1e-6 for i in range(n)) and abs(sum(want) - 36 * 36) < 1e-6,
               "a bowl's seven elevation bands hold the area of the triangles whose mean height is in each (%s)" % [round(x, 1) for x in want])
            ck(B['bands'][0]['label'].startswith('0 to') and B['bands'][6]['label'].endswith('m'), "labelled from the lowest to the highest (%s ... %s)" % (B['bands'][0]['label'], B['bands'][6]['label']))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. breaklines")
            gid = await plane(0.05, 0.02, 0)
            T0 = await tin(gid)
            tri_pts = [[1, 1], [37, 22], [30, 38]]
            sid = await safe("(p)=>window.__a3dSketch('poly',p)", tri_pts)
            await safe("(a)=>window.__a3dSelectFor(a)", [sid, gid])
            br = await safe("()=>window.__a3dBreakline()") or {}
            T1 = await tin(gid)
            segs = [(tri_pts[i], tri_pts[(i + 1) % 3]) for i in range(3)]
            cov = [covered(T1, A, Bp) for A, Bp in segs]
            ck(br.get('constraints') == 3 and not br.get('unforced'), "BREAKLINE: three segments held, none refused (%s)" % br)
            ck(all(abs(cv - math.hypot(Bp[0] - A[0], Bp[1] - A[1])) < 1e-6 for cv, (A, Bp) in zip(cov, segs)),
               "each segment is covered end to end by TIN edges (%s)" % [round(x, 3) for x in cov])
            ck(sum(covered(T0, A, Bp) for A, Bp in segs) < 1, "and was not before (the test is not trivially true)")
            ck(abs(sum(abs(tri_area(T1['P'], t)) for t in T1['tris']) - 1600) < 1e-6 and all(tri_area(T1['P'], t) > 0 for t in T1['tris']),
               "the triangles still tile the surface exactly, all counter-clockwise")
            newv = [(T1['P'][i], T1['H'][i]) for i in range(len(T0['P']), len(T1['P']))]
            ck(len(newv) == 3 and all(abs(hh - (0.05 * p[0] + 0.02 * p[1])) < 1e-9 for p, hh in newv), "its new vertices sit on the ground at the height it has there")
            o = await obj(gid)
            ck(o and len(o['breaklines']) == 1 and o['breaklines'][0]['pts'][0][2] is None and o['breaklines'][0].get('from') == sid, "kept on the surface, with no height of its own, naming its polyline")
            # a second line crossing the first: one shared vertex at the crossing
            s2 = await safe("(p)=>window.__a3dSketch('poly',p)", [[2, 30], [38, 6], [39, 30]])
            await safe("(a)=>window.__a3dSelectFor(a)", [s2, gid])
            br2 = await safe("()=>window.__a3dBreakline()") or {}
            T2 = await tin(gid)
            # where 2,30 -> 38,6 crosses 1,1 -> 37,22 (in Python)
            def xing(a, b, c, d):
                den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
                t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
                return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
            X = xing([1, 1], [37, 22], [2, 30], [38, 6])
            ck(not br2.get('unforced') and any(math.hypot(p[0] - X[0], p[1] - X[1]) < 1e-6 for p in T2['P']),
               "a crossing breakline: both held, with a vertex where they cross (%.3f, %.3f)" % tuple(X))
            ck(all(abs(covered(T2, A, Bp) - math.hypot(Bp[0] - A[0], Bp[1] - A[1])) < 1e-6 for A, Bp in
                   segs + [([2, 30], [38, 6]), ([38, 6], [39, 30]), ([39, 30], [2, 30])]), "every segment of both, covered")
            # a breakline straight through survey points: held through them, no new vertex
            did = await plane(0.05, 0.02, 600)
            Td0 = await tin(did)
            dsk = await safe("(p)=>window.__a3dSketch('poly',p)", [[600, 0], [640, 40], [640, 0]])
            await safe("(a)=>window.__a3dSelectFor(a)", [dsk, did])
            brd = await safe("()=>window.__a3dBreakline()") or {}
            Td = await tin(did)
            ck(not brd.get('unforced') and len(Td['P']) == len(Td0['P']) and abs(covered(Td, [600, 0], [640, 40]) - 40 * math.sqrt(2)) < 1e-6,
               "a breakline through survey points is held through them, with no new point (%s)" % brd)
            # the survey's own coded ridge
            ridge = [(k * 10.0, k * 6.0) for k in range(5)]
            nrm = math.hypot(0.6, -1)

            def ridge_h(x, z):
                return 5 - 0.4 * abs(0.6 * x - z) / nrm
            pts_ = []
            for i in range(-1, 8):
                for j in range(-3, 7):
                    x, z = i * 7 - 2.0, j * 7 - 1.0
                    if abs(0.6 * x - z) / nrm < 1.5:
                        continue
                    pts_.append([500 + x, z, ridge_h(x, z), '', ''])
            plain = pts_ + [[500 + x, z, 5.0, 'R%d' % k, ''] for k, (x, z) in enumerate(ridge)]
            coded = pts_ + [[500 + x, z, 5.0, 'R%d' % k, 'BL1 ridge'] for k, (x, z) in enumerate(ridge)]

            async def ridge_err(i):
                worst = 0
                for k in range(4):
                    for s in range(1, 10):
                        u = s / 10
                        x = 500 + ridge[k][0] + (ridge[k + 1][0] - ridge[k][0]) * u
                        z = ridge[k][1] + (ridge[k + 1][1] - ridge[k][1]) * u
                        hh = await height(i, x, z)
                        worst = max(worst, abs(5 - hh) if hh is not None else 99)
                return worst
            pl = await safe("(p)=>window.__a3dMakeTerrain(p)", plain)
            e0 = await ridge_err(pl)
            await safe("()=>window.__a3dUndo()")
            cd = await safe("(p)=>window.__a3dMakeTerrain(p)", coded)
            e1 = await ridge_err(cd)
            Tc = await tin(cd)
            ck(e0 > 0.05, "without codes, Delaunay cuts the ridge (%.3f m low at worst)" % e0)
            ck(e1 < 1e-9 and len(Tc['constraints']) == 4, "coded BL1, the ridge is held along its whole length (%.2g m)" % e1)
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the boundary")
            rect = [5, 5, 35, 30]
            bsk = await safe("(p)=>window.__a3dSketch('poly',p)", [[5, 5], [35, 5], [35, 30], [5, 30]])
            await safe("(a)=>window.__a3dSelectFor(a)", [bsk, gid])
            bo = await safe("()=>window.__a3dTerrainBoundary()") or {}
            T3 = await tin(gid)
            area = sum(abs(tri_area(T3['P'], t)) for t in T3['tris'])
            ck(abs(area - 750) < 1e-6, "the triangles fill exactly the boundary's 750 m2 (%.6f)" % area)
            ck(all(in_rect(T3['P'][q], rect) for t in T3['tris'] for q in t), "and no triangle reaches outside it")
            grid = [(i * 4, j * 4) for i in range(11) for j in range(11)]
            nout = sum(1 for p in grid if not (5 < p[0] < 35 and 5 < p[1] < 30))
            ck(bo.get('outside') == nout and len(T3['outside']) == nout, "the %d survey points outside are left out and counted (%s)" % (nout, bo))
            hs = [await height(gid, x, z) for x, z in ((6, 6), (20, 17.5), (34.9, 29.9), (12.3, 27.1))]
            ck(all(hh is not None and abs(hh - (0.05 * x + 0.02 * z)) < 1e-9 for hh, (x, z) in zip(hs, ((6, 6), (20, 17.5), (34.9, 29.9), (12.3, 27.1)))),
               "inside, the surface is the ground as surveyed")
            ck(all([await height(gid, x, z) is None for x, z in ((2, 2), (38, 20), (20, 33), (4.9, 10))]), "outside, there is no surface")
            def clip(A, Bp, r):
                t0, t1 = 0.0, 1.0
                d = (Bp[0] - A[0], Bp[1] - A[1])
                for k, lo, hi in ((0, r[0], r[2]), (1, r[1], r[3])):
                    if abs(d[k]) < 1e-12:
                        continue
                    a_, b_ = (lo - A[k]) / d[k], (hi - A[k]) / d[k]
                    t0, t1 = max(t0, min(a_, b_)), min(t1, max(a_, b_))
                return max(0.0, t1 - t0) * math.hypot(*d)
            ins = [(covered(T3, A, Bp), clip(A, Bp, rect)) for A, Bp in segs]
            ck(all(abs(a_ - b_) < 1e-6 for a_, b_ in ins) and sum(b_ for a_, b_ in ins) > 20, "the breaklines are still held, as far as they run inside (%s)" % [(round(a_, 3), round(b_, 3)) for a_, b_ in ins])
            rep = await safe("(i)=>window.__a3dSurveyCheck(i)", gid) or {}
            fid = [x for x in rep.get('items', []) if x['key'] == 'fidelity']
            ck(fid and fid[0]['status'] == 'pass' and ('%d points outside the boundary, left out' % nout) in fid[0]['text'],
               "the survey check passes, saying the points outside were left out (%s)" % (fid[0]['text'] if fid else rep))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. LandXML out")
            N0, E0 = 5000123.456, 300456.789
            lines = []
            for i in range(5):
                for j in range(5):
                    lines.append('P%d,%.3f,%.3f,%.3f,GND' % (i * 5 + j + 1, N0 + 10 * i + 0.3 * j, E0 + 10 * j, 100 + 0.5 * i + 0.25 * j * j))
            await safe("()=>window.__a3dSetTrueNorth(30)")
            si = await safe("(a)=>window.__a3dSurveyImport(a[0],'PNEZD','usft',{n:a[1],e:a[2],z:90})", ['\n'.join(lines), N0, E0]) or {}
            sv = si.get('id')
            doc = await safe("(i)=>window.__a3dLandXmlDoc([i])", sv) or {}
            root = ET.fromstring(doc.get('xml', '<x/>').split('\n', 1)[1])
            ns = {'l': 'http://www.landxml.org/schema/LandXML-1.2'}
            ck(root.tag.endswith('LandXML') and root.get('version') == '1.2', "a LandXML 1.2 document, in its namespace")
            imp = root.find('l:Units/l:Imperial', ns)
            ck(imp is not None and imp.get('linearUnit') == 'USSurveyFoot', "in US survey feet, as surveyed")
            app = root.find('l:Application', ns)
            ck(app is not None and app.get('version') == 'V%d' % vn, "naming the app and its version")   # AMENDED FOR V145: this build's
            P = root.findall('.//l:Pnts/l:P', ns)
            F = root.findall('.//l:Faces/l:F', ns)
            got = sorted(tuple(round(float(v), 3) for v in p.text.split()) for p in P)
            want_ = sorted((round(float(l.split(',')[1]), 3), round(float(l.split(',')[2]), 3), round(float(l.split(',')[3]), 3)) for l in lines)
            ck(got == want_, "every point back in its own northing, easting and elevation, through True North 30")
            Ts = await tin(sv)
            ck(len(F) == len(Ts['tris']) and all(1 <= int(q) <= len(P) for f in F for q in f.text.split()), "every triangle, by point number (%d)" % len(F))
            # read back in: the same surface
            r2 = await safe("(t)=>window.__a3dLandXmlImport(t,'rt.xml')", doc['xml']) or {}
            rid = (r2.get('ids') or [None])[0]
            Tr = await tin(rid)
            ck(Tr and Tr['ownFaces'] and len(Tr['tris']) == len(Ts['tris']), "read back, it keeps the same triangles")
            dev = 0
            for x, z in ((3.1, -4.2), (10.7, -20.3), (-5.5, -15.0), (20.0, -30.0)):
                h1, h2 = await height(sv, x, z), await height(rid, x, z)
                dev = max(dev, abs(h1 - h2) if (h1 is not None and h2 is not None) else (0 if h1 is None and h2 is None else 99))
            ck(dev < 1e-3, "and is the same surface, to the file's 4 decimals (%.2g m)" % dev)
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSetTrueNorth(0)")
            # the breaklines and the boundary go out as SourceData
            doc2 = await safe("(i)=>window.__a3dLandXmlDoc([i])", gid) or {}
            r3 = ET.fromstring(doc2['xml'].split('\n', 1)[1])
            bl = r3.findall('.//l:SourceData/l:Breaklines/l:Breakline', ns)
            bd = r3.findall('.//l:SourceData/l:Boundaries/l:Boundary', ns)
            ck(len(bl) == 2 and len(bd) == 1 and bd[0].get('bndType') == 'outer', "the breaklines and the outer boundary go out as source data")
            p3 = bl[0].find('l:PntList3D', ns).text.split()
            ck(len(p3) == 12, "a breakline's every vertex, with its height on the ground (%d numbers)" % len(p3))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the app")
            await safe("()=>window.__a3dSetPlanView&&window.__a3dSetPlanView()")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}", gid)
            await page.wait_for_timeout(150)
            hb = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('Terrain Analysis' in hb and 'data-propf="terrview"' in hb, "a surface's Properties have a Terrain Analysis group, Colour By")
            ck('2 drawn' in hb and 'terrdrop:breaklines' in hb and '4 corners, 750' in hb and 'terrdrop:boundary' in hb and 'terrlandxml' in hb,
               "with its breaklines, its boundary (each with Remove) and Export LandXML")
            await page.select_option('#a3d-propsbody [data-propf="terrview"]', 'slope')
            await page.wait_for_timeout(200)
            o = await obj(gid)
            ck(o and o.get('tview') == 'slope', "choosing Slope colours the surface by slope")
            rows = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody .a3d-terrband'),function(r){return r.textContent;})") or []
            ck(len(rows) == 7 and any(r.startswith('5 to 8.33%') and '750' in r and '100%' in r for r in rows), "the band table: all 750 m2 in 5 to 8.33%% (%s)" % [r for r in rows if '100%' in r])
            await page.wait_for_timeout(200)
            sh = await safe("()=>window.__a3dTerrainShown()") or []
            me = [d for d in sh if d['id'] == gid]
            ck(me and me[0]['view'] == 'slope' and me[0]['constraints'] >= 6 and me[0]['boundary'], "the plan draws it coloured, its breaklines and boundary (%s)" % (me[0] if me else sh))
            lg = await safe("()=>window.__a3dTerrainLegend()")
            ck(lg and lg['rows'] == ['5 to 8.33%'], "with a legend of the bands it has (%s)" % lg)
            # the Analyze card
            await page.click('#a3d-rail [data-tab="analyze"]')
            await page.wait_for_timeout(250)
            # AMENDED FOR V148: a row's other buttons are inside it, so the row is opened first
            await page.click('.a3d-analyze-wrap [data-anztog="terrain"]')
            await page.wait_for_timeout(100)
            cards = await safe("()=>window.__a3dAnalyzeCards()") or []
            C = {c['id']: c for c in cards}
            ck('terrain' in C and C['terrain']['state'] == 'on' and 'coloured by slope' in C['terrain']['status'], "an Analyze card says the terrain is coloured by slope (%s)" % C.get('terrain', {}).get('status'))
            await page.click('.a3d-analyze-wrap [data-anzact="terrain:aspect"]')
            await page.wait_for_timeout(200)
            ck((await obj(gid)).get('tview') == 'aspect' and 'Facing W' in await toast(), "its Aspect button colours it by aspect (%s)" % await toast())
            await page.click('.a3d-analyze-wrap [data-anzact="terrain:off"]')
            await page.wait_for_timeout(200)
            ck(not any(x.get('tview') for x in (await safe("()=>window.__a3dState().objs")) or []), "Off takes the colours off every surface")
            await page.click('#a3d-rail [data-tab="analyze"]')
            await page.wait_for_timeout(150)
            # commands
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return /^(BREAKLINE|TERRAINBOUNDARY|SLOPEMAP|ELEVATIONMAP|ASPECTMAP|TERRAINANALYSISOFF|LANDXMLOUT|LANDXMLIN)$/.test(c.name);}).map(function(c){return c.name;})") or []
            ck(len(cat) == 8, "the eight commands are in the catalogue (%s)" % sorted(cat))
            for q_, n_ in (('slope', 'SLOPEMAP'), ('aspect', 'ASPECTMAP'), ('landxml', 'LANDXMLOUT'), ('breakline', 'BREAKLINE'), ('civil 3d', 'LANDXMLIN')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
            await safe("(i)=>window.__a3dSelectFor([i])", gid)
            ck(await safe("()=>window.__a3dRunCmd('elevationmap')") and (await obj(gid)).get('tview') == 'elevation', "ELEVATIONMAP colours the selected surface by elevation")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dRunCmd('slopemap')")
            T_ = [x for x in (await safe("()=>window.__a3dState().objs")) if x['t'] == 'terrain']
            ck(T_ and all(x.get('tview') == 'slope' for x in T_), "with nothing selected, SLOPEMAP colours every surface (%d)" % len(T_))
            await safe("()=>window.__a3dRunCmd('terrainviewoff')")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dRunCmd('breakline')")
            ck('Select one or more polylines' in await toast(), "BREAKLINE with nothing selected says what to select")
            # Remove, from Properties
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}", gid)
            await page.wait_for_timeout(100)
            await page.click('#a3d-propsbody [data-propf="terrdrop:boundary"]')
            await page.wait_for_timeout(150)
            T4 = await tin(gid)
            ck(not (await obj(gid)).get('boundary') and abs(sum(abs(tri_area(T4['P'], t)) for t in T4['tris']) - 1600) < 1e-6, "Remove the boundary: the whole surface again")
            await safe("()=>window.__a3dUndo()")
            ck((await obj(gid)).get('boundary'), "undo puts the boundary back")
            # IMPORTCAD reads LandXML
            f = TMP / 'ground.xml'
            f.write_text(xmlin.replace('Existing Ground', 'From IMPORTCAD'), encoding='utf-8')
            n0 = len(await safe("()=>window.__a3dState().objs"))
            await page.set_input_files('#a3d-filein', str(f))
            await page.wait_for_timeout(500)
            objs = await safe("()=>window.__a3dState().objs")
            ck(len(objs) == n0 + 1 and objs[-1]['t'] == 'terrain' and objs[-1]['name'] == 'From IMPORTCAD' and len(objs[-1]['faces']) == 2,
               "IMPORTCAD reads a .xml as LandXML (%s)" % await toast())
            acc = await safe("()=>document.getElementById('a3d-filein').getAttribute('accept')")
            ck('.xml' in acc and '.landxml' in acc, "and offers .xml and .landxml")
            # the reload
            await safe("(i)=>window.__a3dTerrainSetView(i,'aspect')", gid)
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            o = await obj(gid)
            ck(o and len(o.get('breaklines', [])) == 2 and len(o.get('boundary', [])) == 4 and o.get('tview') == 'aspect', "the breaklines, the boundary and the colouring are saved with the project")
            T5 = await tin(gid)
            ck(T5 and abs(sum(abs(tri_area(T5['P'], t)) for t in T5['tris']) - 750) < 1e-6 and len(T5['constraints']) == len(T3['constraints']), "and the surface is rebuilt the same")
            # LANDXMLOUT downloads
            async with page.expect_download(timeout=STALL * 1000) as dl:
                await safe("()=>window.__a3dRunCmd('landxmlout')")
            d = await dl.value
            ck(d.suggested_filename.endswith('.xml') and 'LandXML 1.2' in await toast(), "LANDXMLOUT downloads %s (%s)" % (d.suggested_filename, await toast()))
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
