#!/usr/bin/env python3
"""bim_phase139_lod_cityjson_browser_tests.py -- V139 (LOD-A): LOD1.3 from building parts, labelled
LODs, valid solids, CityJSON out and in.

The owner wants buildings to progress LOD1 -> LOD2 -> LOD3, each level verified
(reference/research-lod-reconstruction.md). This phase is the first step:

  1. THE QUERY AND THE TAGS: building:part is asked for; a part's base and top read from
     min_height, building:min_level, height and levels.
  2. PARTS: an outline with parts is not extruded; each part is, from its base to its top (LOD1.3),
     tied to its building and standing on its building's lowest ground; a part with no height above
     its base is left out and said; a part outside any building still placed; parts sharing the
     outline's edges still found inside it. Whole buildings stay LOD1.2.
  3. LOD LABELS: each building's LOD group says its LOD, what it means, how it was made, and its
     solid check.
  4. THE SOLID CHECK, against hand-made meshes with each of val3dity's errors.
  5. CITYJSON OUT: CityJSON 2.0 in the site's UTM zone (checked against pyproj's numbers), heights
     above sea level, Building and BuildingPart, typed surfaces, attributes and credit; every solid
     closed and outward by a second, independent check here in Python; cjio's validation when cjio is
     installed.
  6. CITYJSON IN: our own file back to the millimetre, the same LODs and records; a re-export the
     same; a foreign grid placed by its centre and named; concave faces; MultiSurface; holes and
     templates counted; a wrongly turned face caught; files that are not CityJSON refused.
  7. LODCHECK, COMMANDS, UNDO AND A RELOAD.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, shutil, subprocess, sys, tempfile, traceback
from playwright.async_api import async_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bim_phase133_site_context_browser_tests as M133   # the Overpass fixture, the ground, the tiles

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
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


LAT0, LON0 = M133.LAT0, M133.LON0
G, ring = M133.G, M133.ring

# ---- building parts (OSM Simple 3D Buildings), placed by model metres ----
OUT_901 = [(-100, -60), (-60, -60), (-60, -30), (-100, -30)]            # the outline: 40 x 30
PODIUM = OUT_901                                                        # 0 to 10
TOWER = [(-90, -55), (-75, -55), (-75, -40), (-90, -40)]                # 10 to 60
WING = [(-70, -55), (-62, -55), (-62, -35), (-70, -35)]                 # min level 2, 5 levels: 6 to 15
BADP = [(-98, -35), (-92, -35), (-92, -32), (-98, -32)]                 # min 20, height 15: left out
OUT_931 = [(100, -60), (120, -60), (120, -40), (100, -40)]
HALF_932 = [(100, -60), (110, -60), (110, -40), (100, -40)]             # shares three of the outline's edges
LONE_921 = [(120, 120), (130, 120), (130, 130), (120, 130)]             # a part in no building: 2 to 8
BIG_941 = [(-140, 80), (-100, 80), (-100, 120), (-140, 120)]            # a building drawn around another
SMALL_942 = [(-130, 90), (-110, 90), (-110, 110), (-130, 110)]          # the one inside: its part is its own
P_943 = [(-125, 95), (-115, 95), (-115, 105), (-125, 105)]
A_951 = [(40, 100), (60, 100), (60, 120), (40, 120)]                    # two buildings sharing a wall
B_952 = [(60, 100), (70, 100), (70, 120), (60, 120)]
P_953 = [(60, 110), (60, 120), (50, 120), (50, 100), (60, 100)]         # in A, its first corner on the shared wall


def fixture():
    js = M133.fixture(True)
    js['elements'] += [
        {'type': 'way', 'id': 901, 'tags': {'building': 'office', 'name': 'Tower Hall', 'height': '60'}, 'geometry': G(ring(OUT_901))},
        {'type': 'way', 'id': 911, 'tags': {'building:part': 'yes', 'height': '10'}, 'geometry': G(ring(PODIUM))},
        {'type': 'way', 'id': 912, 'tags': {'building:part': 'yes', 'min_height': '10', 'height': '60', 'name': 'Tower'}, 'geometry': G(ring(TOWER))},
        {'type': 'way', 'id': 913, 'tags': {'building:part': 'yes', 'building:min_level': '2', 'building:levels': '5'}, 'geometry': G(ring(WING))},
        {'type': 'way', 'id': 914, 'tags': {'building:part': 'yes', 'min_height': '20', 'height': '15'}, 'geometry': G(ring(BADP))},
        {'type': 'way', 'id': 931, 'tags': {'building': 'yes', 'height': '20'}, 'geometry': G(ring(OUT_931))},
        {'type': 'way', 'id': 932, 'tags': {'building:part': 'yes', 'height': '20'}, 'geometry': G(ring(HALF_932))},
        {'type': 'relation', 'id': 921, 'tags': {'building:part': 'yes', 'type': 'multipolygon', 'height': '8', 'min_height': '2'}, 'members': [
            {'type': 'way', 'ref': 9, 'role': 'outer', 'geometry': G(ring(LONE_921))}]},
        {'type': 'way', 'id': 941, 'tags': {'building': 'yes', 'height': '30'}, 'geometry': G(ring(BIG_941))},
        {'type': 'way', 'id': 942, 'tags': {'building': 'yes', 'height': '12', 'name': 'Inner Hall'}, 'geometry': G(ring(SMALL_942))},
        {'type': 'way', 'id': 943, 'tags': {'building:part': 'yes', 'height': '20'}, 'geometry': G(ring(P_943))},
        {'type': 'way', 'id': 951, 'tags': {'building': 'yes', 'height': '15'}, 'geometry': G(ring(A_951))},
        {'type': 'way', 'id': 952, 'tags': {'building': 'yes', 'height': '9'}, 'geometry': G(ring(B_952))},
        {'type': 'way', 'id': 953, 'tags': {'building:part': 'yes', 'height': '25'}, 'geometry': G(ring(P_953))},
    ]
    return js


# pyproj's numbers (EPSG:4326 -> EPSG:32618) for model points, through the app's own model-to-geo
UTM_REF = {(0, 0): (500000.0000, 4427757.2187), (30, -10): (500029.9880, 4427767.2148),
           (40, 0): (500039.9840, 4427757.2188), (-40, -40): (499960.0162, 4427797.2028)}
UTM_INV_REF = ((500100.0, 4427800.0), (-74.99882848038419, 40.00038544480348))


def shell_check(faces, V):
    """An independent check of one solid's shell, from its integer vertices: every edge used once
    each way, and a positive volume."""
    E = {}
    vol = 0.0
    for f in faces:
        r = f[0]
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            E[(a, b)] = E.get((a, b), 0) + 1
        p0 = V[r[0]]
        for i in range(1, len(r) - 1):
            p1, p2 = V[r[i]], V[r[i + 1]]
            vol += (p0[0] * (p1[1] * p2[2] - p1[2] * p2[1]) - p0[1] * (p1[0] * p2[2] - p1[2] * p2[0]) +
                    p0[2] * (p1[0] * p2[1] - p1[1] * p2[0])) / 6.0
    closed = all(E.get((b, a), 0) == 1 and n == 1 for (a, b), n in E.items())
    return closed, vol


def cjval():
    """cityjson.org's validator (Rust), when installed: a function from a path to its JSON report."""
    exe = shutil.which('cjval') or (str(pathlib.Path.home() / '.cargo/bin/cjval') if (pathlib.Path.home() / '.cargo/bin/cjval').exists() else None)
    if not exe:
        return None

    def run(path):
        pr = subprocess.run([exe, '-r', str(path)], capture_output=True, text=True, timeout=120)
        try:
            return json.loads(pr.stdout)
        except ValueError:
            return {'valid': None, 'raw': (pr.stdout + pr.stderr)[-300:]}
    return run


def box(x0, y0, z0, x1, y1, z1):
    v = [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]]
    f = [[0, 1, 2, 3], [7, 6, 5, 4], [1, 0, 4, 5], [2, 1, 5, 6], [3, 2, 6, 7], [0, 3, 7, 4]]
    return v, f


def foreign_file():
    """A file in the Dutch grid (EPSG:7415): an L-shaped block with its ground and roof as single
    concave faces, a wall with an opening, a MultiSurface, a template, and a cube with a face turned
    the wrong way."""
    V, ix = [], {}

    def vi(p):
        k = tuple(int(round(c * 1000)) for c in p)
        if k not in ix:
            ix[k] = len(V)
            V.append(list(k))
        return ix[k]
    E0, N0 = 85000.0, 446000.0
    L = [(0, 0), (20, 0), (20, 10), (10, 10), (10, 20), (0, 20)]          # 300 m2
    H = 7.5
    g = [vi((E0 + x, N0 + y, 2.0)) for x, y in reversed(L)]               # down
    r = [vi((E0 + x, N0 + y, 2.0 + H)) for x, y in L]                     # up
    walls = []
    for i in range(len(L)):
        j = (i + 1) % len(L)
        a, b = L[i], L[j]
        walls.append([[vi((E0 + a[0], N0 + a[1], 2.0)), vi((E0 + b[0], N0 + b[1], 2.0)), vi((E0 + b[0], N0 + b[1], 2.0 + H)), vi((E0 + a[0], N0 + a[1], 2.0 + H))]])
    # an opening (inner ring) in the first wall
    walls[0].append([vi((E0 + 5, N0, 4.0)), vi((E0 + 5, N0, 5.0)), vi((E0 + 7, N0, 5.0)), vi((E0 + 7, N0, 4.0))])
    lsolid = [[g], [r]] + walls
    # a cube, 4 m, with its top turned the wrong way
    C = (E0 + 40, N0)
    cv = [(C[0], C[1], 2.0), (C[0] + 4, C[1], 2.0), (C[0] + 4, C[1] + 4, 2.0), (C[0], C[1] + 4, 2.0)]
    cu = [(p[0], p[1], 6.0) for p in cv]
    cb = [vi(p) for p in cv]
    ct = [vi(p) for p in cu]
    cube = [[[cb[3], cb[2], cb[1], cb[0]]], [[ct[3], ct[2], ct[1], ct[0]]]]   # the top's ring as the bottom's: wrong
    for i in range(4):
        j = (i + 1) % 4
        cube.append([[cb[i], cb[j], ct[j], ct[i]]])
    ms = [[[vi((E0 - 20, N0, 2.0)), vi((E0 - 10, N0, 2.0)), vi((E0 - 10, N0 + 10, 2.0)), vi((E0 - 20, N0 + 10, 2.0))]]]
    mn = [min(v[k] for v in V) for k in range(3)]
    Vt = [[v[0] - mn[0], v[1] - mn[1], v[2] - mn[2]] for v in V]
    return {'type': 'CityJSON', 'version': '2.0',
            'transform': {'scale': [0.001, 0.001, 0.001], 'translate': [mn[0] / 1000, mn[1] / 1000, mn[2] / 1000]},
            'metadata': {'referenceSystem': 'https://www.opengis.net/def/crs/EPSG/0/7415'},
            'CityObjects': {
                'NL.L': {'type': 'Building', 'attributes': {'name': 'L Block', 'yearOfConstruction': 1931},
                         'geometry': [{'type': 'Solid', 'lod': '1.2', 'boundaries': [lsolid]},
                                      {'type': 'MultiSurface', 'lod': '0', 'boundaries': [[g]]}]},
                'NL.cube': {'type': 'Building', 'geometry': [{'type': 'Solid', 'lod': '2.2', 'boundaries': [cube]}]},
                'NL.plaza': {'type': 'TransportSquare', 'geometry': [{'type': 'MultiSurface', 'lod': '1', 'boundaries': ms}]},
                'NL.tree': {'type': 'SolitaryVegetationObject', 'geometry': [{'type': 'GeometryInstance', 'template': 0, 'boundaries': [0],
                                                                              'transformationMatrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]}]},
                'NL.empty': {'type': 'Building', 'geometry': []}},
            'vertices': Vt}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        ext = []
        page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:')) else None)
        QS = []

        async def ovp(route):
            QS.append(route.request.url)
            await route.fulfill(status=200, body=json.dumps(fixture()), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        for h in ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**'):
            await ctx.route(h, ovp)

        async def ter(route):
            import re
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', route.request.url)
            if not m:
                return await route.abort('internetdisconnected')
            z, x, y = (int(v) for v in m.groups())
            await route.fulfill(status=200, body=M133.terrarium_png(z, x, y), headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://s3.amazonaws.com/**', ter)

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

        has = await safe("()=>window.__acad3dV139")
        ck(bool(has) and all(k in has for k in ('buildingparts', 'lod13', 'solidcheck', 'cityjsonout', 'cityjsonin')),
           "__acad3dV139 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def sel(i):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", i)
            await page.wait_for_timeout(80)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def set_field(s, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [s, val])
            await page.wait_for_timeout(150)
            return ok

        async def objs():
            return await safe("()=>window.__a3dState().objs") or []

        async def bld():
            return [o for o in await objs() if o.get('context') and o['context']['kind'] == 'buildings']

        def by_osm(L, i):
            return [o for o in L if o['context'].get('id') == i]

        def yr(o):
            ys = [v[1] for v in o['mesh']['v']]
            return round(min(ys), 3), round(max(ys), 3)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the query and the tags")
            ck(ext == [], "the page asked no server for anything on its way up")
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            q = await safe("()=>window.__a3dCtxQuery()") or ''
            ck('way["building:part"]' in q and 'relation["building:part"]["type"="multipolygon"]' in q and 'way["building"]' in q,
               "the query asks for building parts, ways and multipolygons, beside the buildings")
            await safe("()=>window.__a3dCtxSet('kind:buildings',false)")
            q2 = await safe("()=>window.__a3dCtxQuery()") or ''
            ck('building:part' not in q2, "and not when buildings are not asked for")
            await safe("()=>window.__a3dCtxSet('kind:buildings',true)")
            PR = "(t)=>window.__a3dCtxPartRange(t)"
            r = await safe(PR, {'min_height': '10', 'height': '60'})
            ck(r == {'min': 10, 'minFrom': 'min_height', 'h': 60, 'from': 'height'}, "min_height 10, height 60: 10 to 60 (%s)" % r)
            r = await safe(PR, {'building:min_level': '2', 'building:levels': '5'})
            ck(r and r['min'] == 6 and r['minFrom'] == 'levels' and r['h'] == 15 and r['from'] == 'levels', "min level 2, 5 levels: 6 to 15 m (%s)" % r)
            r = await safe(PR, {'min_height': '10 ft', 'height': '40 ft'})
            ck(r and abs(r['min'] - 3.048) < 1e-9 and abs(r['h'] - 12.192) < 1e-9, "feet read as feet (%s)" % r)
            r = await safe(PR, {'min_height': 'tall', 'building:min_level': '1', 'height': '9'})
            ck(r and r['min'] == 3 and r['minFrom'] == 'levels', "a min_height that does not read falls back to the min level (%s)" % r)
            r = await safe(PR, {'height': '9'})
            ck(r == {'min': 0, 'minFrom': '', 'h': 9, 'from': 'height'}, "no base: from the ground (%s)" % r)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. parts")
            res = await safe("()=>Promise.resolve(window.__a3dCtxFetch())") or {}
            B = await bld()
            ck(res.get('parts') == 7 and res.get('wholes') == 4 and res.get('lowParts') == 1,
               "seven parts placed, four outlines stood for by their parts, one part left out (%s)" % {k: res.get(k) for k in ('parts', 'wholes', 'lowParts')})
            ck(not by_osm(B, 901) and not by_osm(B, 931) and not by_osm(B, 942), "an outline with parts is not extruded itself")
            ck(len(B) == 7 + 7, "the five whole buildings of V133's fixture are there as before, and two more, beside the parts (%d)" % len(B))
            p953 = by_osm(B, 953)
            ck(p953 and p953[0]['context'].get('building', {}).get('id') == 951 and by_osm(B, 952) and not by_osm(B, 951),
               "a part beside a shared wall is the building it is inside, though its first corner is on the wall")
            p943 = by_osm(B, 943)
            ck(by_osm(B, 941) and p943 and p943[0]['context'].get('building', {}).get('id') == 942 and by_osm(B, 941)[0]['context'].get('lod') == '1.2',
               "a part inside a building inside another is the inner one's; the outer stays whole")
            tst = await toast()
            ck('7 building parts at their own heights (LOD1.3)' in tst and '1 part with no height above its base left out' in tst,
               "the toast says so (%s)" % tst[-160:])
            pod, tow, wng, half, lone = (by_osm(B, i)[0] if by_osm(B, i) else None for i in (911, 912, 913, 932, 921))
            ck(all((pod, tow, wng, half, lone)), "the podium, tower, wing, half and lone part are placed")
            if all((pod, tow, wng, half, lone)):
                ck(yr(pod) == (0, 10) and yr(tow) == (10, 60) and yr(wng) == (6, 15) and yr(lone) == (2, 8),
                   "each from its base to its top: 0-10, 10-60, 6-15, 2-8 (%s %s %s %s)" % (yr(pod), yr(tow), yr(wng), yr(lone)))
                c = tow['context']
                ck(c.get('lod') == '1.3' and c.get('buildingPart') is True and c.get('minHeight') == 10 and c.get('minFrom') == 'min_height' and
                   c.get('building') == {'osm': 'way', 'id': 901, 'name': 'Tower Hall'}, "the tower is LOD1.3, a part of way 901 (%s)" % {k: c.get(k) for k in ('lod', 'building', 'minHeight')})
                ck(tow['name'] == 'Tower' and pod['name'] == 'Tower Hall part' and wng['name'] == 'Tower Hall part',
                   "a part keeps its own name, else its building's ('%s', '%s')" % (tow['name'], pod['name']))
                ck(half['context'].get('building', {}).get('id') == 931, "a part sharing its outline's edges is still found inside it")
                ck(lone['context'].get('lod') == '1.3' and 'building' not in lone['context'] and 'standFp' not in lone['context'],
                   "a part in no building is still placed, LOD1.3, with no building")
                ck(wng['context'].get('minFrom') == 'levels' and wng['context'].get('minHeight') == 6, "the wing's base from its min level")
                # standing on the building's lowest ground
                dat = await safe("()=>window.__a3dCtxDatum()")
                g_out = min(M133.ground_xz(x, z) for x, z in OUT_901) - dat
                g_tow = min(M133.ground_xz(x, z) for x, z in TOWER) - dat
                sy = [o['pos'][1] for o in (pod, tow, wng)]
                ck(max(sy) - min(sy) < 1e-9 and abs(sy[0] - g_out) < 0.03 and g_tow - g_out > 0.05,
                   "all three parts stand on the lowest ground under the whole building (%.3f; %.3f there, %.3f under the tower alone)" % (sy[0], g_out, g_tow))
            whole = by_osm(B, 101)[0]
            ck(whole['context'].get('lod') == '1.2' and not whole['context'].get('buildingPart'), "a building with no parts is LOD1.2")
            await nosel()
            h = await props_html()
            ck('7 building parts, LOD1.3' in h, "the last fetch, in the Site Context group, counts its parts")
            ck(len(QS) == 1 and 'building%3Apart' in QS[0], "one Overpass request, carrying the part statements")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. LOD labels")
            for o, lod, how in ((whole, '1.2', 'the OpenStreetMap footprint, extruded to 12.5 m (its height tag)'),
                                (tow, '1.3', 'an OpenStreetMap building part, from 10 m (its min_height) up to 60 m (its height tag)'),
                                (wng, '1.3', 'an OpenStreetMap building part, from 6 m (its min level) up to 15 m (its levels at 3 m each)'),
                                (pod, '1.3', 'an OpenStreetMap building part, from the ground up to 10 m (its height tag)')):
                L = await safe("(i)=>window.__a3dLodOf(i)", o['id'])
                ck(L == {'lod': lod, 'how': how}, "%s: LOD%s, %s (%s)" % (o['name'], lod, how, L))
            nb = [o for o in B if o['context'].get('id') == 103][0]
            L = await safe("(i)=>window.__a3dLodOf(i)", nb['id'])
            ck(L and 'an assumed 6 m (OSM gives no height or levels)' in L['how'], "an assumed height is said (%s)" % L)
            ck(await safe("()=>{var o=window.__a3dState().objs.filter(o=>o.context&&o.context.kind==='roads')[0];return window.__a3dLodOf(o.id);}") is None,
               "a road has no LOD")
            await sel(tow['id'])
            h = await props_html()
            ck('data-a3dpgrp="LOD"' in h and h.index('data-a3dpgrp="LOD"') < h.index('data-a3dpgrp="Context"'), "a selected part has an LOD group, before its Context")
            ck('>LOD1.3<' in h and 'a part of a building, extruded to its own height' in h and 'from 10 m (its min_height) up to 60 m' in h,
               "saying LOD1.3, what that means, and how it was made")
            ck('a3d-svck-pass' in h and 'a valid solid: 8 faces, 11250 m\u00b3' in h,
               "and that it is a valid solid: 8 faces (two triangles at top and bottom), 15 x 15 x 50 m")
            ck('Tower Hall (way 901)' in h and 'Base' in h and '10 m up, from its min_height tag' in h.replace('10.00', '10'), "with its building and its base")
            await sel(whole['id'])
            h = await props_html()
            ck('>LOD1.2<' in h and 'the whole footprint extruded to one height' in h, "a whole building's group says LOD1.2")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the solid check")
            SC = "(a)=>window.__a3dSolidCheckMesh({v:a[0],f:a[1]},a[2])"
            v, f = box(0, 0, 0, 10, 5, 10)
            r = await safe(SC, [v, f, False])
            ck(r and r['valid'] and r['volume'] == 500 and r['faces'] == 6 and r['pieces'] == 1, "a 10 x 5 x 10 box: valid, 500 m3 (%s)" % r)

            def codes(r):
                return sorted((e['code'], e['count']) for e in (r or {}).get('errors', []))
            r = await safe(SC, [v, f[:-1], False])
            ck(codes(r) == [(302, 4)], "a face missing: not closed (302), four open edges (%s)" % codes(r))
            ff = [x[:] for x in f]
            ff[1] = ff[1][::-1]
            r = await safe(SC, [v, ff, False])
            ck(codes(r) == [(307, 4)], "a face turned: 307, its four edges (%s)" % codes(r))
            r = await safe(SC, [v, [x[::-1] for x in f], False])
            ck(codes(r) == [(405, 1)], "every face turned: inside out (405) (%s)" % codes(r))
            r = await safe(SC, [v, f + [f[0]], False])
            ck(codes(r) == [(303, 4)], "a face twice: non-manifold edges (303) (%s)" % codes(r))
            vb = [p[:] for p in v]
            vb[6] = [10, 5.5, 10]
            r = await safe(SC, [vb, f, False])
            ck(codes(r) == [(203, 1)], "a top corner lifted 0.5 m: the top is not flat (203); the walls it ends stay flat (%s)" % codes(r))
            vb[6] = [10, 5.004, 10]
            r = await safe(SC, [vb, f, False])
            ck(r and r['valid'], "lifted 4 mm, under val3dity's 1 cm: flat enough")
            v2, f2 = box(20, 0, 0, 25, 5, 5)
            r = await safe(SC, [v + v2, f + [[i + 8 for i in x] for x in f2], False])
            ck(codes(r) == [(305, 2)], "two boxes: more than one piece (305) (%s)" % codes(r))
            r = await safe(SC, [v + [[5, 0, 0]], f + [[0, 1, 8], [2, 2, 3]], False])
            ck((105, 1) in codes(r) and (101, 1) in codes(r), "a face with no area (105) and one with too few points (101) (%s)" % codes(r))
            r = await safe(SC, [v + [[0.0004, 0, 0]], [[8 if i == 0 else i for i in x] for x in f], False])
            ck(r and r['valid'] and r['vertices'] == 8, "vertices within a millimetre are one")
            r = await safe(SC, [v, f[:2], True])
            ck(r and r['valid'] and r['surface'], "surfaces (not a solid) are not asked to close")
            ck(await safe("()=>window.__a3dSolidCheckMesh({v:[[0,0,0],[1,0,0],[0,1,0]],f:[[0,1,2]]})") and
               [e['code'] for e in (await safe("()=>window.__a3dSolidCheckMesh({v:[[0,0,0],[1,0,0],[0,1,0]],f:[[0,1,2]]})"))['errors']] == [301, 302],
               "one triangle: too few faces, not closed")
            allok = True
            for o in B:
                r = await safe("(i)=>window.__a3dSolidCheck(i)", o['id'])
                allok = allok and bool(r and r['valid'])
            ck(allok, "every context building and part is a valid solid")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. CityJSON out")
            for p, (E, N) in UTM_REF.items():
                lon, lat = M133.m2g(*p)
                u = await safe("(a)=>window.__a3dUtm(a[0],a[1])", [lon, lat])
                ck(u and abs(u[0] - E) < 0.0005 and abs(u[1] - N) < 0.0005, "UTM 18N of model %s within 0.5 mm of pyproj (%s)" % (p, u))
            b = await safe("(a)=>window.__a3dUtmInv(a[0],a[1],18,false)", list(UTM_INV_REF[0]))
            ck(b and abs(b[0] - UTM_INV_REF[1][0]) < 1e-8 and abs(b[1] - UTM_INV_REF[1][1]) < 1e-8, "and back, to 1e-8 degrees (%s)" % b)
            u = await safe("()=>window.__a3dUtm(151.2,-33.86,56,true)")
            ck(u and abs(u[0] - 333491.2299) < 0.0005 and abs(u[1] - 6251909.2060) < 0.0005, "south of the equator, with its false northing (%s)" % u)
            D = await safe("()=>window.__a3dCityJson()") or {}
            ck(D.get('type') == 'CityJSON' and D.get('version') == '2.0' and D.get('transform', {}).get('scale') == [0.001, 0.001, 0.001],
               "CityJSON 2.0, its vertices in millimetres")
            ck(D.get('metadata', {}).get('referenceSystem') == 'https://www.opengis.net/def/crs/EPSG/0/32618' and
               'heights above sea level' in D.get('metadata', {}).get('title', ''), "in UTM zone 18N (EPSG:32618), heights above sea level")
            CO = D.get('CityObjects', {})
            Vx = [[v[0] * 0.001 + D['transform']['translate'][0], v[1] * 0.001 + D['transform']['translate'][1],
                   v[2] * 0.001 + D['transform']['translate'][2]] for v in D.get('vertices', [])]
            ck(set(CO) >= {'osm-way-101', 'osm-way-901', 'osm-way-911-part', 'osm-way-912-part', 'osm-way-913-part', 'osm-relation-921-part', 'osm-way-931', 'osm-way-932-part'} and
               len(CO) == 19, "each building and part by its OSM id (%d objects)" % len(CO))
            ck(CO.get('osm-way-901', {}).get('type') == 'Building' and sorted(CO['osm-way-901'].get('children', [])) == ['osm-way-911-part', 'osm-way-912-part', 'osm-way-913-part'] and
               'geometry' not in CO['osm-way-901'] and CO['osm-way-912-part'].get('parents') == ['osm-way-901'] and CO['osm-way-912-part']['type'] == 'BuildingPart',
               "a building with parts: a Building with no geometry, its BuildingParts as children")
            lp = CO.get('osm-relation-921', {})
            ck(CO.get('osm-relation-921-part', {}).get('type') == 'BuildingPart' and CO['osm-relation-921-part'].get('parents') == ['osm-relation-921'] and
               lp.get('type') == 'Building' and lp.get('children') == ['osm-relation-921-part'] and 'no building outline' in lp.get('attributes', {}).get('note', ''),
               "a part in no building: a BuildingPart under a Building of its own, which says why (CityJSON wants every part to have one)")
            g = (CO.get('osm-way-101', {}).get('geometry') or [{}])[0]
            ck(g.get('type') == 'Solid' and g.get('lod') == '1.2' and len(g.get('boundaries', [[]])[0]) == 6, "the Old Mill: a Solid at LOD1.2, six faces")
            sem = g.get('semantics', {})
            types = [sem.get('surfaces', [{}])[i]['type'] for i in (sem.get('values') or [[]])[0]] if sem else []
            ck(types.count('GroundSurface') == 1 and types.count('RoofSurface') == 1 and types.count('WallSurface') == 4,
               "one ground, one roof, four walls (%s)" % types)
            if len(types) == 6:
                Vq = [[v[0] * 0.001, v[1] * 0.001, v[2] * 0.001] for v in D['vertices']]
                fz = [[Vq[i][2] for i in g['boundaries'][0][k][0]] for k in range(6)]
                rz, gz = fz[types.index('RoofSurface')], fz[types.index('GroundSurface')]
                top, bot = max(max(z) for z in fz), min(min(z) for z in fz)
                ck(min(rz) == top and max(gz) == bot, "the roof is the top face and the ground the bottom one")
            gt = (CO.get('osm-way-912-part', {}).get('geometry') or [{}])[0]
            ck(gt.get('lod') == '1.3', "the tower's geometry is LOD1.3")
            # the corner (30,-10) of the Old Mill, at its ground and its top
            dat = await safe("()=>window.__a3dCtxDatum()")
            E, N = UTM_REF[(30, -10)]
            sy_m = whole['pos'][1]
            hit = [p for p in Vx if abs(p[0] - E) < 0.002 and abs(p[1] - N) < 0.002]
            zs = sorted(round(p[2], 3) for p in hit)
            ck(len(hit) == 2 and abs(zs[0] - (dat + sy_m)) < 0.0015 and abs(zs[1] - (dat + sy_m + 12.5)) < 0.0015,
               "its corner at pyproj's easting and northing, at %.3f and %.3f m above sea level (%s)" % (dat + sy_m, dat + sy_m + 12.5, zs))
            a = CO.get('osm-way-101', {}).get('attributes', {})
            ck(a.get('lod') == '1.2' and a.get('lodMethod', '').startswith('the OpenStreetMap footprint') and a.get('measuredHeight') == 12.5 and
               a.get('credit') == '© OpenStreetMap contributors (ODbL)' and a.get('osmId') == 101 and a.get('osm:name') == 'Old Mill' and a.get('name') == 'Old Mill',
               "its attributes: LOD, how made, height, OSM's credit and tags")
            a = CO.get('osm-way-912-part', {}).get('attributes', {})
            ck(a.get('minHeight') == 10 and a.get('lod') == '1.3', "a part's base height")
            bad = []
            for k, co in CO.items():
                for gg in co.get('geometry', []):
                    if gg['type'] == 'Solid':
                        cl, vol = shell_check(gg['boundaries'][0], Vx)
                        if not cl or vol <= 0:
                            bad.append((k, cl, vol))
            ck(not bad and len([1 for co in CO.values() if co.get('geometry')]) == 14,
               "every solid in the file is closed and outward, by an independent check (%s)" % bad[:3])
            cl, vol = shell_check(gt['boundaries'][0], Vx)
            ck(abs(vol - 15 * 15 * 50 * 0.9996 ** 2) < 0.5, "the tower's volume in the file: 15 x 15 x 50 m, at UTM's scale (%.2f)" % vol)
            tmpd = pathlib.Path(tempfile.mkdtemp())
            (tmpd / 'site.city.json').write_text(json.dumps(D))
            cv = cjval()
            if cv:
                rep = cv(tmpd / 'site.city.json')
                ck(rep.get('valid') is True and rep.get('has_warnings') is False,
                   "cjval (cityjson.org's validator) finds the file valid, with no warnings: schema, parents and children, vertex indices, semantics, duplicate and unused vertices (%s)" %
                   [k for d_ in rep.get('checks', {}).values() for k, v_ in d_.items() if v_.get('valid') is False])
                (tmpd / 'nl.city.json').write_text(json.dumps(foreign_file()))
                rep = cv(tmpd / 'nl.city.json')
                ck(rep.get('valid') is True, "and so is this suite's own foreign test file")
            else:
                print('      (cjval is not installed -- cargo install cjval --features build-binary: its validation is skipped)')
            # the download
            async with page.expect_download() as dl:
                await safe("()=>window.__a3dCityJsonExport()")
            d = await dl.value
            ck(d.suggested_filename.endswith('.city.json'), "CITYJSONOUT downloads a .city.json (%s)" % d.suggested_filename)
            ck('EPSG:32618' in await toast() and 'UTM zone 18N' in await toast(), "and says its grid (%s)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 6. CityJSON in")
            before = {o['context'].get('id'): o for o in B}
            n0 = len(await objs())
            await safe("()=>window.__a3dCtxRemove()")
            r = await safe("(t)=>window.__a3dCityJsonImport(t,'site.city.json')", json.dumps(D)) or {}
            ck(r.get('valid') == 14 and r.get('bad') == 0 and not r.get('local') and r.get('epsg') == 32618,
               "our file back: fourteen solids, all valid, placed by UTM (%s)" % {k: r.get(k) for k in ('valid', 'bad', 'local', 'epsg')})
            O = [o for o in await objs() if o.get('cityjson')]
            ck(len(O) == 14 and all(o['locked'] for o in O), "fourteen objects on the CityJSON layer, locked")
            lay = await safe("()=>window.__a3dLayers()") or []
            ck(any(l['name'] == 'CityJSON' for l in lay), "on a CityJSON layer")
            back = {o['cityjson']['id']: o for o in O}
            o2 = back.get('osm-way-912-part')
            o1 = before.get(912)
            if o1 and o2:
                def wb(o):
                    ys = [v[1] + o['pos'][1] for v in o['mesh']['v']]
                    xs = [v[0] + o['pos'][0] for v in o['mesh']['v']]
                    zs = [v[2] + o['pos'][2] for v in o['mesh']['v']]
                    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]
                d1, d2 = wb(o1), wb(o2)
                ck(max(abs(a - b) for a, b in zip(d1, d2)) < 0.002, "the tower back where it was, to the millimetre (%s / %s)" % (d1, d2))
                ck(o2['cityjson']['lod'] == '1.3' and o2['cityjson']['type'] == 'BuildingPart' and o2['cityjson']['parent'] == 'osm-way-901' and
                   o2['cityjson']['parentAttributes'].get('name') == 'Tower Hall', "a BuildingPart at LOD1.3, of Tower Hall")
                L = await safe("(i)=>window.__a3dLodOf(i)", o2['id'])
                ck(L == {'lod': '1.3', 'how': 'an OpenStreetMap building part, from 10 m (its min_height) up to 60 m (its height tag)'},
                   "its LOD and how it was made come back with it (%s)" % L)
                r2 = await safe("(i)=>window.__a3dSolidCheck(i)", o2['id'])
                ck(r2 and r2['valid'] and abs(r2['volume'] - 11250) < 0.1, "a valid solid of the same volume (%s)" % (r2 and r2['volume']))
                await sel(o2['id'])
                h = await props_html()
                ck('>LOD1.3<' in h and 'BuildingPart osm-way-912-part, Solid' in h and 'Tower Hall (osm-way-901)' in h and 'site.city.json, EPSG:32618' in h and
                   'credit' in h, "its LOD group: LOD, CityJSON id, its building, the file and grid, its attributes")
            D2 = await safe("()=>window.__a3dCityJson()") or {}
            def wv(Dx):
                tr_ = Dx['transform']['translate']
                return sorted(tuple(int(round(v[i] + tr_[i] * 1000)) for i in range(3)) for v in Dx.get('vertices', []))
            ck(sorted(D2.get('CityObjects', {})) == sorted(CO) and D2.get('vertices') and
               max(max(abs(a - b) for a, b in zip(p, q)) for p, q in zip(wv(D2), wv(D))) <= 1 and len(D2['vertices']) == len(D['vertices']),
               "exported again: the same objects, every vertex within a millimetre")
            same = all(D2['CityObjects'][k].get('attributes') == CO[k].get('attributes') and D2['CityObjects'][k].get('type') == CO[k].get('type') and
                       D2['CityObjects'][k].get('parents') == CO[k].get('parents') and sorted(D2['CityObjects'][k].get('children', [])) == sorted(CO[k].get('children', []))
                       for k in CO)
            ck(same, "with the same types, attributes, parents and children")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(not [o for o in await objs() if o.get('cityjson')], "an import is one undo step")
            # a foreign grid
            F = foreign_file()
            r = await safe("(t)=>window.__a3dCityJsonImport(t,'nl.city.json')", json.dumps(F)) or {}
            tst = await toast()
            ck(r.get('local') and r.get('epsg') == 7415 and 'EPSG:7415 is not a grid this app converts: placed by its centre at model 0,0, heights from its lowest point' in tst,
               "a Dutch file (EPSG:7415): placed by its centre and said so")
            ck(r.get('valid') == 2 and r.get('bad') == 1 and '2 valid, 1 with problems' in tst, "each solid checked as it comes in: two valid, one with problems, said")
            ck(r.get('templates') == 1 and '1 template geometry not read' in tst and r.get('holes') == 1 and '1 opening in faces filled' in tst,
               "its template and its wall's opening counted and said")
            ck(r.get('types') == {'Building': 2, 'TransportSquare': 1} and r.get('lods') == {'1.2': 1, '2.2': 1, '1': 1}, "three objects, each its highest LOD (%s)" % r.get('lods'))
            NO = {o['cityjson']['id']: o for o in await objs() if o.get('cityjson')}
            lb = NO.get('NL.L')
            if lb:
                c2 = await safe("(i)=>window.__a3dSolidCheck(i)", lb['id'])
                ck(c2 and c2['valid'] and abs(c2['volume'] - 300 * 7.5) < 0.01, "the L block's concave ground and roof: a valid solid, 300 m2 x 7.5 m (%s)" % (c2 and c2['volume']))
                def convex(face):
                    P_ = [lb['mesh']['v'][i] for i in face]
                    n_ = [0.0, 0.0, 0.0]
                    for i in range(len(P_)):
                        a_, b_ = P_[i], P_[(i + 1) % len(P_)]
                        n_[0] += (a_[1] - b_[1]) * (a_[2] + b_[2]); n_[1] += (a_[2] - b_[2]) * (a_[0] + b_[0]); n_[2] += (a_[0] - b_[0]) * (a_[1] + b_[1])
                    sg = set()
                    for i in range(len(P_)):
                        a_, b_, c_ = P_[i], P_[(i + 1) % len(P_)], P_[(i + 2) % len(P_)]
                        u_ = [b_[k] - a_[k] for k in range(3)]; w_ = [c_[k] - b_[k] for k in range(3)]
                        cr = [u_[1] * w_[2] - u_[2] * w_[1], u_[2] * w_[0] - u_[0] * w_[2], u_[0] * w_[1] - u_[1] * w_[0]]
                        d_ = sum(cr[k] * n_[k] for k in range(3))
                        if abs(d_) > 1e-9:
                            sg.add(d_ > 0)
                    return len(sg) <= 1
                ck(all(convex(fc) for fc in lb['mesh']['f']) and len(lb['mesh']['f']) == 6 + 4 + 4,
                   "its concave faces are split into triangles, each turned as its face was (the viewport fans a face): %d faces" % len(lb['mesh']['f']))
                ys = [v[1] for v in lb['mesh']['v']]
                ck(abs(min(ys)) < 1e-9 and abs(max(ys) - 7.5) < 1e-9, "standing at 0, 7.5 m tall")
                L = await safe("(i)=>window.__a3dLodOf(i)", lb['id'])
                ck(L == {'lod': '1.2', 'how': 'from nl.city.json (EPSG:7415)'} and lb['name'] == 'L Block' and lb['cityjson']['attributes'].get('yearOfConstruction') == 1931,
                   "LOD1.2 from nl.city.json, by its name, with its attributes (%s)" % L)
            cu = NO.get('NL.cube')
            if cu:
                c3 = await safe("(i)=>window.__a3dSolidCheck(i)", cu['id'])
                ck(c3 and [e['code'] for e in c3['errors']] == [307], "the cube's turned top is caught: 307 (%s)" % (c3 and c3['errors']))
                await sel(cu['id'])
                h = await props_html()
                ck('a3d-svck-fail' in h and 'faces turned the wrong way (307, 4)' in h, "and shown in its LOD group")
            pz = NO.get('NL.plaza')
            if pz:
                c4 = await safe("(i)=>window.__a3dSolidCheck(i)", pz['id'])
                ck(c4 and c4['valid'] and c4['surface'], "a MultiSurface square: valid surfaces, not asked to close")
            ck('NL.tree' not in NO and 'NL.empty' not in NO, "a template-only object and one with no geometry are not placed")
            r = await safe("()=>window.__a3dCityJsonImport('{nope','bad.json')") or {}
            ck('is not JSON' in r.get('error', ''), "a file that is not JSON is refused")
            r = await safe("()=>window.__a3dCityJsonImport(JSON.stringify({type:'FeatureCollection',features:[]}),'x.json')") or {}
            ck(r.get('error') == 'x.json is not a CityJSON file', "nor CityJSON")
            r = await safe("()=>window.__a3dCityJsonImport(JSON.stringify({type:'CityJSONFeature',CityObjects:{},vertices:[]}),'x.jsonl')") or {}
            ck('CityJSON Lines' in r.get('error', ''), "CityJSON Lines is named")
            r = await safe("()=>window.__a3dCityJsonImport(JSON.stringify({type:'CityJSON',version:'2.0',CityObjects:{a:{type:'Building'}},vertices:[[0,0,0]]}),'e.city.json')") or {}
            ck('Nothing in e.city.json with surfaces to place' in r.get('error', ''), "nor one with nothing to place")
            # the file chooser's way in
            nn = len([o for o in await objs() if o.get('cityjson')])
            await safe("(t)=>window.__a3dImportFileText(t,'again.cityjson')", json.dumps(F))
            for _ in range(30):
                if len([o for o in await objs() if o.get('cityjson')]) > nn:
                    break
                await page.wait_for_timeout(100)
            ck(len([o for o in await objs() if o.get('cityjson')]) == nn + 3, "a .cityjson file through IMPORT goes to CityJSON")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. LODCHECK, commands, a reload")
            await nosel()
            r = await safe("()=>window.__a3dLodCheck()") or {}
            tst = await toast()
            sel_now = await safe("()=>window.__a3dState().sel")
            ck(r.get('buildings') == 6 and r.get('valid') == 4 and r.get('codes') == [307] and sel_now == r.get('bad', [None])[0],
               "LODCHECK: six, four valid, the turned cube's 307, the first bad one selected (%s)" % {k: r.get(k) for k in ('buildings', 'valid', 'codes')})
            ck('6 buildings (' in tst and '4 valid; 2 with problems (faces turned the wrong way 307), the first selected' in tst, "and says so (%s)" % tst)
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>['LODCHECK','CITYJSONOUT','CITYJSONIN'].indexOf(c.name)>=0).map(c=>c.name)") or []
            ck(sorted(cat) == ['CITYJSONIN', 'CITYJSONOUT', 'LODCHECK'], "the three commands are in the catalog")
            for q_, n_ in (('cityjson', 'CITYJSONOUT'), ('val3dity', 'LODCHECK'), ('level of detail', 'LODCHECK'), ('3dbag', 'CITYJSONIN')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
            await safe("()=>window.__a3dRunCmd('lodcheck')")
            ck('6 buildings' in await toast(), "LODCHECK runs as a command")
            await nosel()
            h = await props_html()
            ck('data-propctxact="lodcheck"' in h and 'data-propctxact="cjout"' in h and 'data-propctxact="cjin"' in h,
               "the Site Context group has Check LODs, Export CityJSON and Import CityJSON")
            await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")
            await safe("()=>document.querySelector('#a3d-propsbody [data-propctxact=\"lodcheck\"]').click()")
            ck('6 buildings' in await toast(), "Check LODs checks them")
            await nosel()   # it selected the first with a problem
            async with page.expect_download() as dl:
                await safe("()=>document.querySelector('#a3d-propsbody [data-propctxact=\"cjout\"]').click()")
            ck((await dl.value).suggested_filename.endswith('.city.json'), "Export CityJSON exports")
            async with page.expect_file_chooser() as fcI:
                await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();document.querySelector('#a3d-propsbody [data-propctxact=\"cjin\"]').click();}")
            fch = await fcI.value
            nn = len([o for o in await objs() if o.get('cityjson')])
            await fch.set_files(files=[{'name': 'chosen.city.json', 'mimeType': 'application/json', 'buffer': json.dumps(foreign_file()).encode()}])
            for _ in range(30):
                if len([o for o in await objs() if o.get('cityjson')]) > nn:
                    break
                await page.wait_for_timeout(100)
            ck(len([o for o in await objs() if o.get('cityjson')]) == nn + 3 and 'chosen.city.json' in await toast(), "Import CityJSON opens a file and places it")
            await safe("()=>window.__a3dCtxFetch()")
            for _ in range(60):
                if not await safe("()=>window.__a3dCtxBusy()"):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            O = await objs()
            tw = [o for o in O if o.get('context') and o['context'].get('id') == 912]
            cj = [o for o in O if o.get('cityjson')]
            ck(tw and (await safe("(i)=>window.__a3dLodOf(i)", tw[0]['id']) or {}).get('lod') == '1.3' and len(cj) == 9 and
               (await safe("(i)=>window.__a3dLodOf(i)", [o for o in cj if o['cityjson']['id'] == 'NL.L'][0]['id']) or {}).get('lod') == '1.2',
               "parts and CityJSON objects keep their LODs through a reload")
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
