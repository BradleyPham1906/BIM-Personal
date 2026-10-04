#!/usr/bin/env python3
"""bim_phase133_site_context_browser_tests.py -- V133: site context in one click.

The owner wants "as much open public data as possible" (reference/research-site-context.md). The
buildings, roads, water, green and trees around the site come from OpenStreetMap through the
Overpass API; the ground from AWS Terrain Tiles. Both are answered inside the browser here: Overpass
by a fixture in its own answer's shape, the tiles by PNGs encoding a known ground (linear in the
tile pixels, so bilinear sampling must give it back exactly).

  1. NOTHING UNTIL ASKED: no request at load; the Site Context group; refused with no place.
  2. THE AREA AND THE QUERY: the square around model 0,0 or the property lines, true north; each
     kind's statements; none ticked.
  3. READING OSM: heights (metres, feet, levels, assumed), multipolygon rings joined.
  4. ONE PRESS: one GET (V134d), the tiles over the area; buildings extruded where and as tall as OSM
     says, roads, water, green, trees; the ground under each building; the terrain to the
     millimetre; layers, pins, credits, Properties; not a mass; one undo.
  5. AGAIN: a fresh fetch replaces only what it brings; the datum kept; the survey base's used.
  6. FAILURES: busy, unreadable, unreachable, each named; what came is placed; nothing at all
     changes nothing; a second press while one runs.
  7. SETTINGS, REMOVE, EXPORT, COMMANDS AND A RELOAD.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, struct, sys, traceback, urllib.parse, zlib
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
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


WA, WE2 = 6378137.0, 0.00669437999014
LAT0, LON0 = 40.0, -75.0


def radii(lat):
    s = math.sin(math.radians(lat))
    w = 1 - WE2 * s * s
    return WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)


def m2g(x, z, tn=0.0, lat0=LAT0, lon0=LON0):
    t = math.radians(tn)
    E, N = x * math.cos(t) + z * math.sin(t), x * math.sin(t) - z * math.cos(t)
    M, Nr = radii(lat0)
    return lon0 + math.degrees(E / (Nr * math.cos(math.radians(lat0)))), lat0 + math.degrees(N / M)


def tx(lon, z):
    return (lon + 180) / 360 * 2 ** z


def ty(lat, z):
    la = math.radians(lat)
    return (1 - math.log(math.tan(la) + 1 / math.cos(la)) / math.pi) / 2 * 2 ** z


# ---- the ground: linear in the global pixel coordinates at zoom 15 ----
TZ = 15
GX0, GY0 = tx(LON0, TZ) * 256, ty(LAT0, TZ) * 256
GROUND = {'base': 120.0, 'ax': 0.03, 'ay': -0.02}


def ground_px(gx, gy):
    return GROUND['base'] + GROUND['ax'] * (gx - GX0) + GROUND['ay'] * (gy - GY0)


def ground_at(lon, lat):
    return ground_px(tx(lon, TZ) * 256, ty(lat, TZ) * 256)


def ground_xz(x, z):
    g = m2g(x, z)
    return ground_at(g[0], g[1])


_PNG = {}


def terrarium_png(z, x, y):
    key = (z, x, y, GROUND['base'], GROUND['ax'], GROUND['ay'])
    if key in _PNG:
        return _PNG[key]
    rows = []
    for j in range(256):
        row = bytearray(b'\x00')
        for i in range(256):
            v = ground_px(x * 256 + i + 0.5, y * 256 + j + 0.5) + 32768
            fl = math.floor(v)
            b = min(255, int(round((v - fl) * 256)))
            row += bytes((int(fl) // 256, int(fl) % 256, b))
        rows.append(bytes(row))

    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    _PNG[key] = b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', 256, 256, 8, 2, 0, 0, 0)) + \
        ch(b'IDAT', zlib.compress(b''.join(rows))) + ch(b'IEND', b'')
    return _PNG[key]


# ---- the OSM fixture, in Overpass's own answer shape, placed by model metres ----
def G(pts):
    out = []
    for p in pts:
        lon, lat = m2g(p[0], p[1])
        out.append({'lat': lat, 'lon': lon})
    return out


def ring(pts):
    return pts + [pts[0]]


B_SQ = [(30, -10), (40, -10), (40, 0), (30, 0)]                       # 10 x 10, height 12.5
B_L = [(-40, -40), (-20, -40), (-20, -30), (-30, -30), (-30, -20), (-40, -20)]   # L, 300 m2, 4 levels
B_NONE = [(60, 40), (70, 40), (70, 48), (60, 48)]                     # no height: assumed
B_FT = [(-70, 50), (-60, 50), (-60, 60), (-70, 60)]                   # 40 ft
MP_OUT_A = [(0, 60), (30, 60), (30, 90)]                              # the outer, in two halves
MP_OUT_B = [(30, 90), (0, 90), (0, 60)]
MP_IN = [(10, 70), (20, 70), (20, 80), (10, 80)]


def fixture(full=True):
    els = [
        {'type': 'way', 'id': 101, 'tags': {'building': 'yes', 'height': '12.5', 'name': 'Old Mill'}, 'geometry': G(ring(B_SQ))},
        {'type': 'way', 'id': 102, 'tags': {'building': 'apartments', 'building:levels': '4', 'addr:housenumber': '7', 'addr:street': 'Elm Street'},
         'geometry': G(ring(B_L))},
    ]
    if not full:
        return {'elements': els}
    els += [
        {'type': 'way', 'id': 103, 'tags': {'building': 'shed'}, 'geometry': G(ring(B_NONE))},
        {'type': 'way', 'id': 104, 'tags': {'building': 'yes', 'height': '40 ft'}, 'geometry': G(ring(B_FT))},
        {'type': 'relation', 'id': 201, 'tags': {'building': 'yes', 'type': 'multipolygon', 'building:levels': '2'}, 'members': [
            {'type': 'way', 'ref': 1, 'role': 'outer', 'geometry': G(MP_OUT_A)},
            {'type': 'way', 'ref': 2, 'role': 'outer', 'geometry': G(MP_OUT_B)},
            {'type': 'way', 'ref': 3, 'role': 'inner', 'geometry': G(ring(MP_IN))}]},
        {'type': 'way', 'id': 301, 'tags': {'highway': 'residential', 'name': 'Elm Street', 'lanes': '2'}, 'geometry': G([(-100, 5), (0, 5), (100, 5)])},
        {'type': 'way', 'id': 302, 'tags': {'highway': 'primary', 'junction': 'roundabout'}, 'geometry': G(ring([(100, 100), (110, 100), (110, 110), (100, 110)]))},
        {'type': 'way', 'id': 401, 'tags': {'natural': 'water', 'name': 'Mill Pond'}, 'geometry': G(ring([(-100, -100), (-80, -100), (-80, -80), (-100, -80)]))},
        {'type': 'way', 'id': 402, 'tags': {'waterway': 'stream'}, 'geometry': G([(-120, 0), (-110, 20), (-100, 40)])},
        {'type': 'relation', 'id': 403, 'tags': {'natural': 'water', 'type': 'multipolygon'}, 'members': [
            {'type': 'way', 'ref': 4, 'role': 'outer', 'geometry': G(ring([(80, -100), (120, -100), (120, -60), (80, -60)]))},
            {'type': 'way', 'ref': 5, 'role': 'inner', 'geometry': G(ring([(95, -85), (105, -85), (105, -75), (95, -75)]))}]},
        {'type': 'way', 'id': 501, 'tags': {'leisure': 'park', 'name': 'Elm Park'}, 'geometry': G(ring([(-60, 100), (-20, 100), (-20, 130), (-60, 130)]))},
        {'type': 'way', 'id': 601, 'tags': {'amenity': 'parking'}, 'geometry': G(ring([(0, -120), (10, -120), (10, -110), (0, -110)]))},
        {'type': 'node', 'id': 1, 'lat': 0, 'lon': 0},
    ]
    for i, (x, z) in enumerate(((15, 15), (18, 22), (-5, 30))):
        lon, lat = m2g(x, z)
        els.append({'type': 'node', 'id': 701 + i, 'lat': lat, 'lon': lon, 'tags': {'natural': 'tree', 'species': 'Quercus'}})
    return {'version': 0.6, 'generator': 'Overpass API (fixture)', 'elements': els}


SRV = {'ovp': [], 'ovp_mode': 'ok', 'ovp_full': True, 'ter': [], 'ter_mode': 'ok', 'hold': None, 'ext': [], 'other': []}


def near(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()

        def guard(obj, names):
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        def on_req(r):
            u = r.url
            if not (u.startswith('file:') or u.startswith('data:') or u.startswith('blob:')):
                SRV['ext'].append(u)
        page.on('request', on_req)

        async def ovp_route(route):
            rq = route.request
            SRV['ovp'].append({'url': rq.url, 'method': rq.method, 'body': rq.post_data or '',
                               'ctype': (await rq.all_headers()).get('content-type', '')})
            if SRV['hold'] is not None:
                try:
                    await asyncio.wait_for(SRV['hold'].wait(), 30)
                except asyncio.TimeoutError:
                    pass
            m = SRV['ovp_mode']
            if m == 'mainblocked':   # AMENDED FOR V134d: overpass-api.de refuses with no CORS header; the mirrors answer
                m = 'abort' if 'overpass-api.de' in route.request.url else 'ok'
            if m == 'abort':
                await route.abort('internetdisconnected')
            elif m == '429':
                await route.fulfill(status=429, body='rate limited', headers={'Access-Control-Allow-Origin': '*'})
            elif m == 'junk':
                await route.fulfill(status=200, body='<html>runtime error</html>', headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/html'})
            else:
                await route.fulfill(status=200, body=json.dumps(fixture(SRV['ovp_full'])),
                                    headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        await ctx.route('https://overpass-api.de/**', ovp_route)
        await ctx.route('https://overpass.example.org/**', ovp_route)
        # AMENDED FOR V134d: Overpass's other public instances, tried in turn when one fails
        for mirror in ('https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**'):
            await ctx.route(mirror, ovp_route)

        async def ter_route(route):
            u = route.request.url
            SRV['ter'].append(u)
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', u)
            if SRV['ter_mode'] == 'abort' or not m:
                await route.abort('internetdisconnected')
                return
            z, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            await route.fulfill(status=200, body=terrarium_png(z, x, y), headers={
                'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*',
                'Access-Control-Expose-Headers': 'x-amz-meta-x-imagery-sources',
                'x-amz-meta-x-imagery-sources': 'srtm/N39W076.tif, ned19/x75y40.tif' if x % 2 == 0 else 'srtm/N39W076.tif'})
        await ctx.route('https://s3.amazonaws.com/**', ter_route)

        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV133")
        ck(bool(has), "__acad3dV133 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(120)
            return ok

        async def place(lat, lon):
            await nosel()
            a = await set_field('[data-propmodel="sunlat"]', '' if lat is None else repr(lat))
            b = await set_field('[data-propmodel="sunlon"]', '' if lon is None else repr(lon))
            return a and b

        async def objs():
            return await safe("()=>window.__a3dState().objs") or []

        async def ctx_objs(kind=None):
            return [o for o in await objs() if o.get('context') and (kind is None or o['context']['kind'] == kind)]

        async def fetch():
            return await safe("()=>Promise.resolve(window.__a3dCtxFetch())")

        async def layers():
            return await safe("()=>window.__a3dLayers()") or []

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. nothing until asked")
            ck(SRV['ext'] == [], "the page asked no server for anything on its way up")
            st = await safe("()=>window.__a3dCtxSettings()")
            ck(st == {'radius': 150, 'kinds': {k: True for k in ('buildings', 'roads', 'water', 'green', 'trees', 'rail', 'airports', 'power', 'landuse', 'terrain')},   # AMENDED FOR V157: rail, airports, power, land use
                      'overpass': 'https://overpass-api.de/api/interpreter',
                      'onGround': True}, "150 m, all six kinds, overpass-api.de, by default (%s)" % st)   # AMENDED FOR V137: buildings on the terrain
            await nosel()
            h = await props_html()
            ck('data-a3dpgrp="Site Context"' in h and h.index('data-a3dpgrp="Map"') < h.index('data-a3dpgrp="Site Context"') < h.index('data-a3dpgrp="View"'),
               "with nothing selected, a Site Context group after the Map")
            ck(all('data-propctx="kind:%s"' % k in h for k in ('buildings', 'roads', 'water', 'green', 'trees', 'terrain')) and
               'data-propctxact="get"' in h and 'data-propctxact="remove"' in h and 'OpenStreetMap (ODbL)' in h,
               "with the radius, a box for each kind, Get and Remove, and its sources")
            r = await fetch()
            ck(r is None and 'Set the site latitude and longitude first' in await toast() and SRV['ext'] == [],
               "with no place yet, CONTEXT is refused, saying why, and asks nothing")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the area and the query")
            ck(await place(LAT0, LON0), "the site placed")
            a = await safe("()=>window.__a3dCtxArea()")
            gs = [m2g(x, z) for x, z in ((-150, -150), (150, -150), (150, 150), (-150, 150))]
            ck(a and a['cx'] == 0 and a['cz'] == 0 and a['half'] == 150 and not a['fromProperty'] and
               near(a['w'], min(g[0] for g in gs), 1e-12) and near(a['e'], max(g[0] for g in gs), 1e-12) and
               near(a['s'], min(g[1] for g in gs), 1e-12) and near(a['n'], max(g[1] for g in gs), 1e-12),
               "with no property line: 150 m around model 0,0, as longitude and latitude")
            q = await safe("()=>window.__a3dCtxQuery()") or ''
            box = '(%.7f,%.7f,%.7f,%.7f)' % (a['s'], a['w'], a['n'], a['e'])
            want = ['way["building"]', 'relation["building"]["type"="multipolygon"]', 'way["highway"]', 'way["natural"="water"]',
                    'relation["natural"="water"]', 'way["water"]', 'way["waterway"]', 'way["leisure"="park"]', 'node["natural"="tree"]']
            ck(q.startswith('[out:json][timeout:25];(') and q.endswith(');out geom;') and all((w + box + ';') in q for w in want),
               "the Overpass query: JSON, each kind's statements on the box, out geom")
            await safe("""()=>{var o=window.__a3dState().objs;o.push({id:'SKP',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:[[20,-10],[60,-10],[60,20],[20,20]],y:0,closed:true,layer:'layer-0'});window.__a3dTestSetObjs(o);}""")
            pl = await safe("()=>window.__a3dPropertyFromSketch('SKP')")
            a2 = await safe("()=>window.__a3dCtxArea()")
            ck(a2 and a2['fromProperty'] and near(a2['cx'], 40, 1e-9) and near(a2['cz'], 5, 1e-9) and near(a2['half'], 20 + 150, 1e-9),
               "with a property line: around it, the radius beyond its half-size (%s)" % str(a2 and (a2['cx'], a2['cz'], a2['half'])))
            await safe("()=>window.__a3dSetTrueNorth(30)")
            a3 = await safe("()=>window.__a3dCtxArea()")
            hh3 = a3['half'] if a3 else 0
            gs = [m2g(a3['cx'] + dx, a3['cz'] + dz, 30) for dx, dz in ((-hh3, -hh3), (hh3, -hh3), (hh3, hh3), (-hh3, hh3))] if a3 else []
            ck(a3 and gs and near(a3['w'], min(g[0] for g in gs), 1e-12) and near(a3['e'], max(g[0] for g in gs), 1e-12) and
               near(a3['s'], min(g[1] for g in gs), 1e-12) and near(a3['n'], max(g[1] for g in gs), 1e-12),
               "turned by true north, the box holds the turned square")
            await safe("()=>window.__a3dSetTrueNorth(0)")
            await safe("()=>{window.__a3dTestSetObjs([]);}")
            for k in ('roads', 'water', 'green', 'trees', 'rail', 'airports', 'power', 'landuse'):   # AMENDED FOR V157
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,false)", k)
            q = await safe("()=>window.__a3dCtxQuery()") or ''
            ck('way["building"]' in q and 'highway' not in q and 'water' not in q and 'park' not in q and 'tree' not in q,
               "unticked kinds leave the query")
            await safe("()=>window.__a3dCtxSet('kind:buildings',false)")
            ck(await safe("()=>window.__a3dCtxQuery()") == '', "with no OSM kind ticked, no query")
            await safe("()=>window.__a3dCtxSet('kind:terrain',false)")
            n0 = len(SRV['ext'])
            r = await fetch()
            ck(r is None and 'Tick at least one kind' in await toast() and len(SRV['ext']) == n0, "nothing ticked: refused, nothing asked")
            for k in ('buildings', 'roads', 'water', 'green', 'trees', 'rail', 'airports', 'power', 'landuse', 'terrain'):   # AMENDED FOR V157
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,true)", k)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. reading OSM")
            for tags, hh, frm in (({'height': '12.5'}, 12.5, 'height'), ({'height': '12 m'}, 12, 'height'), ({'height': '40 ft'}, 12.192, 'height'),
                                  ({'height': "40'"}, 12.192, 'height'), ({'height': '3,5'}, 3.5, 'height'),
                                  ({'building:levels': '4'}, 12, 'levels'), ({'height': 'tall', 'building:levels': '2'}, 6, 'levels'),
                                  ({'height': '0', 'building:levels': '3'}, 9, 'levels'), ({}, 6, 'assumed'), ({'building:levels': 'many'}, 6, 'assumed')):
                r = await safe("(t)=>window.__a3dCtxHeight(t)", tags)
                ck(r and near(r['h'], hh, 1e-9) and r['from'] == frm, "height %s: %g m, %s" % (tags, hh, frm))
            mem = [{'type': 'way', 'role': 'outer', 'geometry': [{'lon': 0, 'lat': 0}, {'lon': 1, 'lat': 0}, {'lon': 1, 'lat': 1}]},
                   {'type': 'way', 'role': 'outer', 'geometry': [{'lon': 0, 'lat': 0}, {'lon': 0, 'lat': 1}, {'lon': 1, 'lat': 1}]},
                   {'type': 'way', 'role': 'inner', 'geometry': [{'lon': .2, 'lat': .2}, {'lon': .4, 'lat': .2}, {'lon': .4, 'lat': .4}, {'lon': .2, 'lat': .2}]},
                   {'type': 'way', 'role': 'outer', 'geometry': [{'lon': 5, 'lat': 5}, {'lon': 6, 'lat': 5}]}]
            ro = await safe("(m)=>window.__a3dCtxRings(m,'outer')", mem) or []
            ck(len(ro) == 1 and len(ro[0]) == 5 and ro[0][0] == ro[0][-1] and sorted(map(tuple, ro[0][:-1])) == [(0, 0), (0, 1), (1, 0), (1, 1)],
               "a multipolygon's outer halves join into one closed ring, the second turned round; an open chain is dropped (%s)" % ro)
            ri = await safe("(m)=>window.__a3dCtxRings(m,'inner')", mem) or []
            ck(len(ri) == 1 and len(ri[0]) == 4, "its inner ring read on its own")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. one press")
            SRV['ovp'].clear()
            SRV['ter'].clear()
            before = len(await objs())
            r = await fetch()
            ck(r and r.get('counts') == {'buildings': 5, 'roads': 2, 'water': 4, 'green': 1, 'trees': 3, 'rail': 0, 'airports': 0, 'power': 0, 'landuse': 0, 'terrain': 1} and not r.get('errors'),   # AMENDED FOR V157: the new kinds, none in this fixture
               "one press: 5 buildings, 2 roads, 4 water (a pond, a stream, a lake and its island), a park, 3 trees, the terrain (%s)" % (r and r.get('counts')))
            tt = await toast()
            ck(r and r.get('assumed') == 1 and r.get('courtyards') == 1 and '1 building height assumed (6 m)' in tt and '1 courtyard filled' in tt,
               "it says how many heights it assumed and courtyards it filled (%r)" % tt)
            ck(len(SRV['ovp']) == 1 and SRV['ovp'][0]['method'] == 'GET' and SRV['ovp'][0]['url'].startswith('https://overpass-api.de/api/interpreter?data='),
               "one plain GET to Overpass, the simplest request a browser makes")   # AMENDED FOR V134d
            body = SRV['ovp'][0]['url'].split('?', 1)[1] if SRV['ovp'] else ''
            ck(body.startswith('data=') and urllib.parse.unquote(body[5:]) == await safe("()=>window.__a3dCtxQuery()"),
               "carrying exactly the query")
            want_t = set()
            for xx in range(int(math.floor(tx(a['w'], TZ))), int(math.floor(tx(a['e'], TZ))) + 1):
                for yy in range(int(math.floor(ty(a['n'], TZ))), int(math.floor(ty(a['s'], TZ))) + 1):
                    want_t.add('https://s3.amazonaws.com/elevation-tiles-prod/terrarium/%d/%d/%d.png' % (TZ, xx, yy))
            ck(set(SRV['ter']) == want_t and len(SRV['ter']) == len(want_t), "the Terrarium tiles over the area at zoom 15, each once (%d)" % len(want_t))
            B = {o['context'].get('id'): o for o in await ctx_objs('buildings')}

            def mesh_xz(o):
                return sorted(set((round(v[0], 6), round(v[2], 6)) for v in o['mesh']['v']))

            def mesh_y(o):
                ys = [v[1] for v in o['mesh']['v']]
                return min(ys), max(ys)

            def gm(pts):
                return sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
            o = B.get(101, {})
            ck(o.get('t') == 'solid' and mesh_xz(o) == gm(B_SQ), "a building is a solid on its footprint, where OSM puts it")
            ck(near(mesh_y(o)[0], 0, 1e-9) and near(mesh_y(o)[1], 12.5, 1e-9) and o['context']['heightFrom'] == 'height',
               "on the ground, 12.5 m tall from its height tag")
            ck(o.get('name') == 'Old Mill' and o.get('locked') is True, "named by OSM, and pinned")
            o = B.get(102, {})
            ck(mesh_xz(o) == gm(B_L) and near(mesh_y(o)[1], 12, 1e-9) and o['context']['heightFrom'] == 'levels' and o.get('name') == '7 Elm Street',
               "an L-shaped block, 4 levels at 3 m: 12 m, named by its address")
            ck(len(o.get('mesh', {}).get('f', [])) == 4 * 2 + 6 and near(await safe("(i)=>window.__a3dSliceArea(i,5)", o.get('id')), 300, 1e-6),
               "its concave footprint capped by ear-clipping: 300 m2 at any height")
            ck(near(mesh_y(B.get(103, {}))[1], 6, 1e-9) and B.get(103, {}).get('context', {}).get('heightFrom') == 'assumed', "no height or levels: 6 m, assumed, said")
            ck(near(mesh_y(B.get(104, {}))[1], 12.192, 1e-9), "40 ft is 12.192 m")
            o = B.get(201, {})
            ck(mesh_xz(o) == gm(MP_OUT_A + MP_OUT_B) and o['context'].get('courtyards') == 1 and near(mesh_y(o)[1], 6, 1e-9),
               "a multipolygon: its outer halves joined and extruded, its courtyard filled and counted")
            c = B.get(101, {}).get('context', {})
            ck(c.get('source') == 'OpenStreetMap' and c.get('credit') == '© OpenStreetMap contributors (ODbL)' and c.get('osm') == 'way' and
               c.get('tags') == {'building': 'yes', 'height': '12.5', 'name': 'Old Mill'}, "each keeps its source, credit, OSM type, id and tags")
            ck(near(c.get('ground'), round(ground_xz(35, -5) - 120, 2), 0.011), "and the ground under it, from the terrain (%s m)" % c.get('ground'))
            ck(await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", B.get(101, {}).get('id')) == 0, "a neighbour is not a mass: it takes no usage")
            R = {o['context']['id']: o for o in await ctx_objs('roads')}
            ck(R.get(301, {}).get('t') == 'sketch' and R[301].get('closed') is False and R[301].get('name') == 'Elm Street' and len(R[301]['pts']) == 3,
               "a road is its centreline, open, named")
            ck(R.get(302, {}).get('closed') is True and len(R[302]['pts']) == 4, "a roundabout a closed one")
            Wt = await ctx_objs('water')
            pond = [o for o in Wt if o['context']['id'] == 401]
            stream = [o for o in Wt if o['context']['id'] == 402]
            lake = [o for o in Wt if o['context']['id'] == 403]
            ck(pond and pond[0]['closed'] and stream and stream[0]['closed'] is False and len(lake) == 2 and
               sum(1 for o in lake if o['context'].get('part') == 'hole') == 1, "water: a pond's area, a stream's line, a lake and its island marked a hole")
            gr = await ctx_objs('green')
            ck(len(gr) == 1 and gr[0]['name'] == 'Elm Park' and gr[0]['closed'], "a park's area")
            tr = await ctx_objs('trees')
            ck(len(tr) == 3 and all(o.get('kind') == 'point' for o in tr) and tr[0]['context']['tags'] == {'natural': 'tree', 'species': 'Quercus'},
               "trees are points, with their tags")
            ck(not [o for o in await objs() if o.get('context') and o['context'].get('id') == 601], "a car park is none of the six: left out")
            ck(await safe("()=>window.__a3dState().sel") is None, "nothing is selected after it: the surface it made is not left selected")
            # the terrain
            te = (await ctx_objs('terrain') or [{}])[0]
            sv = te.get('survey', [])
            worst = max(abs(p[2] - (ground_xz(p[0], p[1]) - 120)) for p in sv) if sv else 99
            ck(te.get('t') == 'terrain' and len(sv) == 625, "the terrain is a V108 surface of 25 x 25 points")
            ck(worst < 0.006, "every point is the ground less the datum, to %.4f m (bilinear, 1/256 m encoding)" % worst)
            xs = sorted(set(round(p[0], 6) for p in sv))
            ck(len(xs) == 25 and near(xs[0], -150, 1e-6) and near(xs[-1], 150, 1e-6), "spread across the whole area")
            ck(await safe("()=>window.__a3dCtxDatum()") == 120, "the datum is the ground at model 0,0, kept on the site (120 m)")
            tc = te.get('context', {})
            ws = sorted(set(['srtm/N39W076.tif'] + (['ned19/x75y40.tif'] if any(int(u.split('/')[-2]) % 2 == 0 for u in want_t) else [])))
            ck(tc.get('sources') == ws and 'Terrain Tiles: Mapzen, AWS (%s)' % ', '.join(ws) == tc.get('credit'),
               "its credit names the sources the tiles' own header gave (%s)" % tc.get('credit'))
            ck(tc.get('zoom') == 15 and te.get('locked') is True, "zoom 15, pinned")
            # layers
            L = await layers()
            byid = {l['id']: l for l in L}
            par = [l for l in L if l['name'] == 'Context']
            kids = {l['name']: l for l in L if par and l.get('parent') == par[0]['id']}
            ck(par and set(kids) == {'Context ' + k for k in ('buildings', 'roads', 'water', 'green', 'trees', 'rail', 'airports', 'power', 'landuse', 'terrain')},   # AMENDED FOR V157
               "a Context layer with a sub-layer for each kind")
            ck(all(byid.get(o['layer'], {}).get('name') == 'Context ' + o['context']['kind'] for o in await ctx_objs()),
               "every object on its kind's layer")
            await nosel()
            cur = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-propmodel=\"layer\"]');return e&&e.value;}")
            ck(byid.get(cur, {}).get('name') == 'Model', "the current layer stays the one it was")
            # the credit line, Properties, undo
            ft = await safe("()=>{var f=document.getElementById('a3d-mapattr');return f.hidden?null:f.innerHTML;}") or ''
            ck('Context <a href="https://www.openstreetmap.org/copyright"' in ft and 'Terrain Tiles: Mapzen, AWS' in ft,
               "the credit line carries OSM's and the terrain's credits, the map being off")
            await safe("()=>window.__a3dMapSet('style','street')")
            await safe("()=>window.__a3dTestPaint()")
            ft = await safe("()=>document.getElementById('a3d-mapattr').innerHTML") or ''
            ck(ft.count('OpenStreetMap contributors') == 1 and 'Terrain Tiles' in ft, "with the street map on, OSM is credited once")
            await safe("()=>window.__a3dMapSet('style','off')")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", B.get(101, {}).get('id'))
            h = await props_html()
            ck('data-a3dpgrp="Context"' in h and 'from its height tag' in h and 'https://www.openstreetmap.org/way/101' in h and 'Old Mill' in h,
               "a building's page: its Context, height and where it came from, a link to it on OSM, its tags")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", B.get(103, {}).get('id'))
            ck('assumed: OSM gives no height or levels' in await props_html(), "an assumed height says so")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", te.get('id'))
            ck('model y 0 is 120 m above sea level' in await props_html(), "the terrain's page gives its datum")
            await nosel()
            ck('Last Fetch' in await props_html() and '5 buildings' in await props_html(), "the Site Context group says what the last fetch brought")
            await safe("()=>{window.__a3dUndo();window.__a3dUndo();}")   # the credit check's two map steps
            ck((await safe("()=>window.__a3dMapSettings()"))['style'] == 'off' and len(await ctx_objs()) == 16, "(the credit check's two map steps undone)")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            nob, nco, dtm = len(await objs()), len(await ctx_objs()), await safe("()=>window.__a3dCtxDatum()")
            ck(nob == before and nco == 0 and dtm is None, "one undo takes it all back, the datum too (%s objects, %s context, datum %s)" % (nob, nco, dtm))
            await safe("()=>window.__a3dRedo&&window.__a3dRedo()")
            await page.wait_for_timeout(100)
            if not await ctx_objs():
                await fetch()
            ck(len(await ctx_objs()) == 16, "and redo brings it back (16 objects)")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. again")
            for k in ('roads', 'water', 'green', 'trees', 'terrain'):
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,false)", k)
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the undo has to be the fetch's own
            SRV['ovp_full'] = False
            r = await fetch()
            ck(r and r['counts']['buildings'] == 2 and len(await ctx_objs('buildings')) == 2 and len(await ctx_objs('roads')) == 2 and
               len(await ctx_objs('terrain')) == 1, "a buildings-only fetch replaces the buildings and leaves roads and terrain")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(len(await ctx_objs('buildings')) == 5 and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7, "one undo, and only it, brings the five back")
            await safe("()=>window.__a3dMapSet('opacity',100)")
            SRV['ovp_full'] = True
            for k in ('roads', 'water', 'green', 'trees', 'terrain'):
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,true)", k)
            GROUND['base'] = 125.0   # the ground moved: the datum must not
            await fetch()
            sv = ((await ctx_objs('terrain')) or [{}])[0].get('survey', [])
            ck(sv and max(abs(p[2] - (ground_xz(p[0], p[1]) - 120)) for p in sv) < 0.006, "a second fetch keeps the first's datum: the ground reads 5 m higher")
            GROUND['base'] = 120.0
            # a survey base, when V108 set one, is the datum
            await safe("()=>window.__a3dRunCmd('survey')")
            await page.wait_for_timeout(150)
            ok = await safe("""()=>{var d=document.querySelector('.a3d-dlg');if(!d)return false;
              d.querySelector('[data-a3dp="pts"]').value='1, 5000, 2000, 101, A\\n2, 5010, 2000, 102, B\\n3, 5000, 2010, 103, C';
              d.querySelector('[data-a3dp="bz"]').value='100';d.querySelector('[data-a3dlg="ok"]').click();return true;}""")
            await page.wait_for_timeout(150)
            ck(ok and await safe("()=>window.__a3dCtxDatum()") == 100, "a survey base at 100 m is the datum")
            await fetch()
            sv = ((await ctx_objs('terrain')) or [{}])[0].get('survey', [])
            ck(sv and max(abs(p[2] - (ground_xz(p[0], p[1]) - 100)) for p in sv) < 0.006, "and the terrain is read against it: 20 m higher")
            await safe("()=>{window.__a3dUndo();window.__a3dUndo();}")
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dCtxDatum()") == 120, "undone, the kept datum is back")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. failures")
            n_obj = len(await objs())
            SRV['ovp_mode'] = '429'
            r = await fetch()
            ck(r and r['counts']['terrain'] == 1 and 'overpass-api.de is busy (HTTP 429): try again in a minute' in r.get('errors', []) and
               'overpass-api.de is busy' in await toast(), "Overpass busy: named, and the terrain that came is still placed")
            ck(len(await ctx_objs('buildings')) == 5, "and the buildings it could not refresh are left as they were")
            SRV['ovp_mode'] = 'junk'
            r = await fetch()
            ck(r and 'overpass-api.de sent an answer that does not read' in r.get('errors', []), "an answer that is not JSON: named")
            hosts = [urllib.parse.urlparse(x['url']).netloc for x in SRV['ovp'][-4:]]
            ck(hosts == ['overpass-api.de', 'overpass.private.coffee', 'maps.mail.ru', 'overpass.kumi.systems'] and
               all(h_ + ' sent an answer that does not read' in r.get('errors', []) for h_ in hosts), "each of Overpass's public instances was tried in turn, and each named (V134d)")
            SRV['ovp_mode'] = 'abort'
            SRV['ter_mode'] = 'abort'
            r = await fetch()
            ck(r and 'overpass-api.de could not be reached (offline, or it does not allow browser access)' in r.get('error', '') and
               's3.amazonaws.com could not be reached' in r.get('error', '') and len(await objs()) == n_obj,
               "both unreachable: each named, nothing changed")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(len(await ctx_objs('terrain')) == 1 and len(await ctx_objs('buildings')) == 5, "and no undo step was spent on nothing")
            await safe("()=>window.__a3dRedo&&window.__a3dRedo()")
            SRV['ovp_mode'] = 'mainblocked'
            SRV['ter_mode'] = 'ok'
            n_ovp = len(SRV['ovp'])
            r = await fetch()
            ck(r and r['counts']['buildings'] == 5 and not r.get('errors') and [urllib.parse.urlparse(x['url']).netloc for x in SRV['ovp'][n_ovp:]] ==
               ['overpass-api.de', 'overpass.private.coffee'], "the owner's case: overpass-api.de refuses, the next instance answers, and the context comes (V134d)")
            SRV['ovp_mode'] = 'ok'
            SRV['ter_mode'] = 'ok'
            SRV['hold'] = asyncio.Event()
            n_ovp = len(SRV['ovp'])
            p1 = asyncio.ensure_future(safe("()=>window.__a3dCtxFetch()"))
            await page.wait_for_timeout(400)
            ck(await safe("()=>window.__a3dCtxBusy()") is True, "while it runs, it is busy")
            r2 = await safe("()=>window.__a3dCtxFetch()")
            ck(r2 is None and 'already on its way' in await toast(), "a second press is refused")
            SRV['hold'].set()
            await within(p1, 'first fetch')
            SRV['hold'] = None
            ck(len(SRV['ovp']) == n_ovp + 1 and await safe("()=>window.__a3dCtxBusy()") is False, "one request went, and it is free again")
            await safe("()=>window.__a3dCtxSet('overpass','https://overpass.example.org/api/interpreter')")
            n_ovp = len(SRV['ovp'])
            await fetch()
            ck(len(SRV['ovp']) == n_ovp + 1 and SRV['ovp'][-1]['url'].startswith('https://overpass.example.org/api/interpreter?data='), "another Overpass server, when set, is the one asked")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. settings, remove, export, commands, a reload")
            await nosel()
            await set_field('[data-propctx="radius"]', '20')
            ck((await safe("()=>window.__a3dCtxSettings()"))['radius'] == 150 and '50 to 1000' in await toast(), "a radius of 20 m is refused, with the range")
            await set_field('[data-propctx="radius"]', '2000')
            ck((await safe("()=>window.__a3dCtxSettings()"))['radius'] == 150, "so is 2000 m")
            await set_field('[data-propctx="radius"]', '300')
            ck((await safe("()=>window.__a3dCtxSettings()"))['radius'] == 300 and (await safe("()=>window.__a3dCtxArea()"))['half'] == 300, "300 m taken")
            await safe("()=>window.__a3dUndo()")
            ck((await safe("()=>window.__a3dCtxSettings()"))['radius'] == 150, "a setting is one undo step")
            await nosel()
            await set_field('[data-propctx="kind:trees"]', False)
            ck((await safe("()=>window.__a3dCtxSettings()"))['kinds']['trees'] is False, "a kind's box in Properties unticks it")
            await set_field('[data-propctx="kind:trees"]', True)
            await set_field('[data-propctx="overpass"]', 'not a server')
            ck((await safe("()=>window.__a3dCtxSettings()"))['overpass'] == 'https://overpass.example.org/api/interpreter', "a server that is not a web address is refused")
            await set_field('[data-propctx="overpass"]', '')
            ck((await safe("()=>window.__a3dCtxSettings()"))['overpass'] == 'https://overpass-api.de/api/interpreter', "and an empty one goes back to overpass-api.de")
            # export
            fc = await safe("()=>window.__a3dGeoExport()") or {}
            cb = [f for f in fc.get('features', []) if f['properties'].get('osm_id') == 101]
            ck(cb and cb[0]['geometry']['type'] == 'Polygon' and cb[0]['properties']['kind'] == 'context buildings' and
               cb[0]['properties']['credit'] == '© OpenStreetMap contributors (ODbL)' and cb[0]['properties']['height'] == 12.5 and
               cb[0]['properties']['name'] == 'Old Mill', "GeoJSON export writes a neighbour as its footprint, with its credit, height and tags")
            cr = [f for f in fc.get('features', []) if f['properties'].get('osm_id') == 301]
            ck(cr and cr[0]['properties']['kind'] == 'context roads' and cr[0]['geometry']['type'] == 'LineString' and cr[0]['properties']['lanes'] == '2',
               "and a road as its line, with its credit")
            # commands
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>c.name==='CONTEXT'||c.name==='CONTEXTREMOVE').map(c=>({n:c.name,where:c.where}))") or []
            ck(any(c['n'] == 'CONTEXT' and 'Site' in ' '.join(c['where']) for c in cat) and any(c['n'] == 'CONTEXTREMOVE' for c in cat),
               "CONTEXT is on the ribbon's Site panel, CONTEXTREMOVE in the search")
            for q_, n_ in (('neighbours', 'CONTEXT'), ('overpass', 'CONTEXT'), ('osm', 'CONTEXT')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
            n_ovp = len(SRV['ovp'])
            await safe("()=>window.__a3dRunCmd('context')")
            for _ in range(40):
                if len(SRV['ovp']) > n_ovp and not await safe("()=>window.__a3dCtxBusy()"):
                    break
                await page.wait_for_timeout(100)
            ck(len(SRV['ovp']) == n_ovp + 1 and len(await ctx_objs()) == 16, "CONTEXT runs as a command")
            # a reload keeps it
            nb = len(await ctx_objs())
            await page.wait_for_timeout(600)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            co = await ctx_objs()
            ck(len(co) == nb and (await safe("(i)=>window.__a3dCtxOf(i)", [o for o in co if o['context'].get('id') == 101][0]['id']) or {}).get('height') == 12.5,
               "the context outlives a reload, with its records: it opens offline")
            ck(await safe("()=>window.__a3dCtxDatum()") == 120, "and so does the datum")
            # remove
            await safe("()=>window.__a3dRunCmd('contextremove')")
            ck(not await ctx_objs() and 'Site context removed: %d objects' % nb in await toast(), "CONTEXTREMOVE takes every context object away")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(len(await ctx_objs()) == nb, "in one undo step")
            await safe("()=>window.__a3dRedo&&window.__a3dRedo()")
            await page.wait_for_timeout(100)
            if await ctx_objs():
                await safe("()=>window.__a3dCtxRemove()")
            r = await safe("()=>window.__a3dCtxRemove()")
            ck(r == 0 and 'no site context to remove' in await toast(), "with none, it says so")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        await browser.close()
    print("%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
