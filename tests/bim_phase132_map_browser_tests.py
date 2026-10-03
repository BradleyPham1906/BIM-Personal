#!/usr/bin/env python3
"""bim_phase132_map_browser_tests.py -- V132: the map.

The owner wants the map "just like how giraffe do", with free sources only, and as much open public
data as possible (reference/research-map.md, research-open-data.md). Every server here is routed
inside the browser -- the tile servers, Nominatim -- so the suite runs offline and knows exactly
what was asked of them.

  1. OFF UNTIL ASKED: no request at all until the map is turned on; the Map group in Properties.
  2. GEOREFERENCING: model 0,0 at the site's latitude and longitude, true north turning it, against
     the closed form and against an independent geodesic (Vincenty) on the WGS84 ellipsoid.
  3. WHICH TILES: the zoom from metres per pixel, the extent from the screen on the ground, the
     URL templates, the 80-tile cap, the corners on the model.
  4. THE STORE: nearest the centre first, at most 12 in flight, a parent while a tile loads, the
     store kept to about 400 tiles.
  5. ON SCREEN: a tile's pixels where its corners say, in WebGL and on the 2D canvas, with true
     north; opacity; a solid over the map; nothing in an elevation, nothing on paper.
  6. FAILURES SAID: a server that does not allow browser access is named in the credit line.
  7. SETTINGS: refusals, custom tiles, undo; the credit line.
  8. THE ADDRESS: one Nominatim request per Find, the place becomes model 0,0, one undo; the
     second inside a second refused; nothing found; a server error.
  9. SITE DATA IN: GeoJSON and KML -- rings, holes, lines, points, properties; a projected file
     refused; with no place yet, the data's centre becomes it; one undo.
 10. THE PLAN OUT: GeoJSON in longitude and latitude, back onto the model within a millimetre.
 11. COMMANDS AND A RELOAD.

The harness never waits without a bound (V123).
"""
import asyncio, io, json, math, pathlib, re, struct, sys, tempfile, traceback, zlib
from playwright.async_api import async_playwright
from PIL import Image

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


# ---- the earth, independently of the page ----
WA, WE2, WF = 6378137.0, 0.00669437999014, 1 / 298.257223563


def radii(lat):
    s = math.sin(math.radians(lat))
    w = 1 - WE2 * s * s
    return WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)


def m2g(x, z, lat0, lon0, tn=0.0):
    t = math.radians(tn)
    E, N = x * math.cos(t) + z * math.sin(t), x * math.sin(t) - z * math.cos(t)
    M, Nr = radii(lat0)
    return lon0 + math.degrees(E / (Nr * math.cos(math.radians(lat0)))), lat0 + math.degrees(N / M)


def g2m(lon, lat, lat0, lon0, tn=0.0):
    M, Nr = radii(lat0)
    E = math.radians(lon - lon0) * Nr * math.cos(math.radians(lat0))
    N = math.radians(lat - lat0) * M
    t = math.radians(tn)
    return E * math.cos(t) + N * math.sin(t), E * math.sin(t) - N * math.cos(t)


def vincenty(lat1, lon1, lat2, lon2):
    """the ellipsoidal distance and initial azimuth: a second opinion, not the page's formula"""
    a, f = WA, WF
    b = a * (1 - f)
    L = math.radians(lon2 - lon1)
    U1, U2 = math.atan((1 - f) * math.tan(math.radians(lat1))), math.atan((1 - f) * math.tan(math.radians(lat2)))
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    for _ in range(200):
        sl, cl = math.sin(lam), math.cos(lam)
        sS = math.sqrt((cU2 * sl) ** 2 + (cU1 * sU2 - sU1 * cU2 * cl) ** 2)
        if sS == 0:
            return 0.0, 0.0
        cS = sU1 * sU2 + cU1 * cU2 * cl
        sig = math.atan2(sS, cS)
        sA = cU1 * cU2 * sl / sS
        c2A = 1 - sA * sA
        c2M = cS - 2 * sU1 * sU2 / c2A if c2A else 0
        C = f / 16 * c2A * (4 + f * (4 - 3 * c2A))
        lp = lam
        lam = L + (1 - C) * f * sA * (sig + C * sS * (c2M + C * cS * (-1 + 2 * c2M * c2M)))
        if abs(lam - lp) < 1e-13:
            break
    u2 = c2A * (a * a - b * b) / (b * b)
    A_ = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B_ = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    dS = B_ * sS * (c2M + B_ / 4 * (cS * (-1 + 2 * c2M * c2M) - B_ / 6 * c2M * (-3 + 4 * sS * sS) * (-3 + 4 * c2M * c2M)))
    s = b * A_ * (sig - dS)
    az = math.degrees(math.atan2(cU2 * math.sin(lam), cU1 * sU2 - sU1 * cU2 * math.cos(lam))) % 360
    return s, az


def tx(lon, z):
    return (lon + 180) / 360 * 2 ** z


def ty(lat, z):
    la = math.radians(lat)
    return (1 - math.log(math.tan(la) + 1 / math.cos(la)) / math.pi) / 2 * 2 ** z


def tlon(x, z):
    return x / 2 ** z * 360 - 180


def tlat(y, z):
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2 ** z))))


# ---- the routed servers ----
PALETTE = [(220, 40, 40), (40, 200, 60), (50, 90, 220), (230, 200, 40), (200, 60, 200), (40, 200, 200)]
BG = (29, 32, 36)


def col(x, y, z):
    return PALETTE[(x + 2 * y + 3 * z) % 6]


_PNG = {}


def png(rgb):
    if rgb not in _PNG:
        raw = b''.join(b'\x00' + bytes(rgb) * 256 for _ in range(256))

        def ch(t, d):
            c = struct.pack('>I', len(d)) + t + d
            return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        _PNG[rgb] = b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', 256, 256, 8, 2, 0, 0, 0)) + \
            ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
    return _PNG[rgb]


SRV = {'req': [], 'delay': 0.0, 'cur': 0, 'max': 0, 'hold': None, 'ev': None, 'nom': [], 'ext': []}


def nocors_server():
    """a real tile server on this machine that sends no CORS header: the browser itself refuses its
    tiles to the page (a routed response cannot show this -- the harness answers CORS for it)"""
    import http.server, threading
    hits = []

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            body = png((90, 90, 90))
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, hits


def near(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


def same_col(p, c, tol=10):
    return p is not None and all(abs(p[i] - c[i]) <= tol for i in range(3))


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

        async def tile_route(route):
            u = route.request.url
            SRV['req'].append(u)
            m = re.search(r'/(\d+)/(\d+)/(\d+)\.png$', u)
            z, x, y = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)
            SRV['cur'] += 1
            SRV['max'] = max(SRV['max'], SRV['cur'])
            try:
                if SRV['hold'] in (z, 'all') and SRV['ev'] is not None:
                    try:
                        await asyncio.wait_for(SRV['ev'].wait(), 30)
                    except asyncio.TimeoutError:
                        pass
                if SRV['delay']:
                    await asyncio.sleep(SRV['delay'])
            finally:
                SRV['cur'] -= 1
            try:
                await route.fulfill(status=200, body=png(col(x, y, z)),
                                    headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
            except Exception:
                pass
        # AMENDED FOR V133d: the street map is CARTO's (OSM's own servers refuse a page opened as a file)
        await ctx.route('https://basemaps.cartocdn.com/**', tile_route)
        await ctx.route('https://tiles.example.org/**', tile_route)

        async def esri_route(route):
            SRV['req'].append(route.request.url)
            await route.abort('internetdisconnected')   # offline, as far as the page can tell
        await ctx.route('https://server.arcgisonline.com/**', esri_route)

        async def nom_route(route):
            u = route.request.url
            SRV['nom'].append(u)
            q = re.search(r'[?&]q=([^&]*)', u)
            q = q.group(1) if q else ''
            if 'error' in q:
                await route.fulfill(status=500, body='busy', headers={'Access-Control-Allow-Origin': '*'})
                return
            body = [] if 'nowhere' in q else [{'lat': '51.5007292', 'lon': '-0.1246254', 'display_name': 'Big Ben, Westminster, London'}]
            await route.fulfill(status=200, body=json.dumps(body),
                                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://nominatim.openstreetmap.org/**', nom_route)

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

        has = await safe("()=>!!window.__acad3dV132")
        ck(bool(has), "__acad3dV132 marker is present")
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
              e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(120)
            return ok

        async def place(lat, lon):
            await nosel()
            a = await set_field('[data-propmodel="sunlat"]', '' if lat is None else repr(lat))
            b = await set_field('[data-propmodel="sunlon"]', '' if lon is None else repr(lon))
            return a and b

        async def north(deg):
            await safe("(d)=>window.__a3dSetTrueNorth(d)", deg)
            await page.wait_for_timeout(60)

        async def cam(**c):
            r = await safe("(c)=>window.__a3dCamSet(c)", c)
            await page.wait_for_timeout(60)
            return r

        async def settle(ms=2500):
            """until nothing is in flight, at most ms"""
            t = 0
            while t < ms:
                c = await safe("()=>window.__a3dMapCache()") or {}
                if c.get('inflight', 0) == 0:
                    await page.wait_for_timeout(120)
                    c = await safe("()=>window.__a3dMapCache()") or {}
                    if c.get('inflight', 0) == 0:
                        break
                await page.wait_for_timeout(100)
                t += 100
            await safe("()=>window.__a3dTestPaint()")
            await page.wait_for_timeout(80)

        async def tiles():
            return await safe("()=>window.__a3dMapTiles()") or {}

        async def drawn():
            return await safe("()=>window.__a3dMapDrawn()") or {}

        async def canvas_box():
            return await safe("""()=>{var c=document.getElementById('a3d-canvas'),r=c.getBoundingClientRect();
              return {left:r.left,top:r.top,w:c.width/(window.devicePixelRatio||1),h:c.height/(window.devicePixelRatio||1)};}""")

        async def shot():
            return Image.open(io.BytesIO(await page.screenshot())).convert('RGB')

        async def at(img, world):
            p = await safe("""(w)=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();var q=window.__a3dProject(w);
              return [r.left+q.x,r.top+q.y];}""", world)
            if not p:
                return None
            x, y = int(round(p[0])), int(round(p[1]))
            if x < 0 or y < 0 or x >= img.width or y >= img.height:
                return None
            return img.getpixel((x, y))

        def mix(c, a):
            return tuple(round(BG[i] + (c[i] - BG[i]) * a) for i in range(3))

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. off until asked")
            ck(SRV['ext'] == [], "the page asked no server for anything on its way up (%s)" % SRV['ext'][:3])
            st = await safe("()=>window.__a3dMapSettings()")
            ck(st == {'style': 'off', 'opacity': 1, 'url': '', 'credit': ''}, "the map is off, at full opacity, by default (%s)" % st)
            ck((await drawn()).get('reason') == 'off', "and nothing is drawn: off")
            ck(await safe("()=>document.getElementById('a3d-mapattr').hidden") is True, "the credit line is hidden while the map is off")
            await nosel()
            h = await props_html()
            ck('data-a3dpgrp="Map"' in h and 'data-propmap="style"' in h and 'data-propmapact="find"' in h and
               'data-propmapact="import"' in h and 'data-propmapact="export"' in h,
               "with nothing selected, Properties has a Map group: basemap, find, import, export")
            ck(h.index('data-a3dpgrp="Identity Data"') < h.index('data-a3dpgrp="Map"') < h.index('data-a3dpgrp="View"'),
               "the Map group sits after the latitude and longitude, before View")
            opts = await safe("()=>Array.prototype.map.call(document.querySelectorAll('#a3d-propsbody [data-propmap=\"style\"] option'),function(o){return o.value+'|'+o.textContent;})")
            ck(opts == ['off|Off', 'street|Street (CARTO, OpenStreetMap data)', 'satellite|Satellite (Esri World Imagery)', 'custom|Custom tiles'],   # AMENDED FOR V133d
               "four choices, each saying whose it is (%s)" % opts)
            ck('not placed' in h, "Model 0,0 says it is not placed yet")
            await set_field('[data-propmap="style"]', 'street')
            await page.wait_for_timeout(300)
            ck(SRV['ext'] == [] and (await drawn()).get('reason') == 'place',
               "turned on with no latitude and longitude: still no request, and it says why")
            ck('set the site latitude and longitude' in (await safe("()=>window.__a3dMapFooter()") or ''),
               "the credit line asks for the site's place")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. georeferencing")
            LAT0, LON0 = 40.0, -75.0
            ck(await place(LAT0, LON0), "the site's latitude and longitude set in Properties")
            await north(0)
            g = await safe("()=>window.__a3dModelToGeo(0,0)")
            ck(g and near(g[0], LON0, 1e-12) and near(g[1], LAT0, 1e-12), "model 0,0 is the site's latitude and longitude (%s)" % g)
            for (x, z) in ((100, 0), (0, -100), (-250, 75), (1234.5, 987.6)):
                g = await safe("(p)=>window.__a3dModelToGeo(p[0],p[1])", [x, z])
                e = m2g(x, z, LAT0, LON0)
                ck(g and near(g[0], e[0], 1e-11) and near(g[1], e[1], 1e-11), "model (%g, %g) to the closed form on the WGS84 radii" % (x, z))
            g = await safe("()=>window.__a3dModelToGeo(0,-100)")
            ck(g and near(g[0], LON0, 1e-12) and g[1] > LAT0, "model -z is north with true north 0")
            g = await safe("()=>window.__a3dModelToGeo(100,0)")
            ck(g and g[0] > LON0 and near(g[1], LAT0, 1e-12), "model +x is east")
            for tn in (0, 30, -47.5):
                await north(tn)
                for az, d in ((0, 250), (90, 180), (225, 300), (311, 90)):
                    a = math.radians(az + tn)
                    g = await safe("(p)=>window.__a3dModelToGeo(p[0],p[1])", [math.sin(a) * d, -math.cos(a) * d])
                    s, az2 = vincenty(LAT0, LON0, g[1], g[0]) if g else (None, None)
                    ck(near(s, d, 0.02) and near((az2 - az + 180) % 360 - 180, 0, 0.005),
                       "true north %g: %g m along true azimuth %g is %.4f m at %.4f deg by an independent geodesic" % (tn, d, az, s or -1, az2 or -1))
                back = await safe("(p)=>{var g=window.__a3dModelToGeo(p[0],p[1]);return window.__a3dGeoToModel(g[0],g[1]);}", [321.25, -654.5])
                ck(back and near(back[0], 321.25, 1e-7) and near(back[1], -654.5, 1e-7), "true north %g: there and back is the same point" % tn)
            await north(30)
            gm = await safe("(p)=>window.__a3dGeoToModel(p[0],p[1])", [LON0 + 0.003, LAT0 - 0.002])
            em = g2m(LON0 + 0.003, LAT0 - 0.002, LAT0, LON0, 30)
            ck(gm and near(gm[0], em[0], 1e-7) and near(gm[1], em[1], 1e-7), "a longitude and latitude onto the model, turned by true north (%s)" % gm)
            await north(0)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. which tiles")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            c0 = await cam(tx=60, tz=-60, dist=150)
            cb = await canvas_box()
            W, H = cb['w'], cb['h']
            T = await tiles()
            mpp = 150 / (H * 1.2)
            z0 = max(1, min(19, round(math.log2(156543.03392 * math.cos(math.radians(LAT0)) / mpp))))
            ck(T.get('z') == z0 and near(T.get('mpp'), mpp, 1e-9), "plan: zoom %s from %.4f m a pixel, as the formula gives %d" % (T.get('z'), mpp, z0))

            # the screen's corners on the ground, by the camera's own formulas, done again here
            def camvecs(c):
                cy, sy, cp, sp = math.cos(c['yaw']), math.sin(c['yaw']), math.cos(c['pitch']), math.sin(c['pitch'])
                d = [cp * sy, sp, cp * cy]
                r = [d[2], 0, -d[0]]
                rl = math.hypot(r[0], r[2])
                r = [r[0] / rl, 0, r[2] / rl]
                u = [d[1] * r[2] - d[2] * r[1], d[2] * r[0] - d[0] * r[2], d[0] * r[1] - d[1] * r[0]]
                eye = [c['tx'] + d[0] * c['dist'], c['ty'] + d[1] * c['dist'], c['tz'] + d[2] * c['dist']]
                return d, r, u, eye

            def ground_flat(sx, sy, c, y0=0.0):
                d, r, u, eye = camvecs(c)
                k = H * 1.2 / max(c['dist'], 0.5)
                xc, yc = (sx - W / 2) / k, (H / 2 - sy) / k
                px, pz, py = eye[0] + r[0] * xc + u[0] * yc, eye[2] + r[2] * xc + u[2] * yc, eye[1] + r[1] * xc + u[1] * yc
                t2 = (y0 - py) / (-d[1])
                return px - d[0] * t2, pz - d[2] * t2
            gp = [ground_flat(sx, sy, c0) for sx, sy in ((0, 0), (W, 0), (0, H), (W, H), (W / 2, H / 2))]
            gg = [m2g(p[0], p[1], LAT0, LON0) for p in gp]
            lo0, lo1, la0, la1 = min(q[0] for q in gg), max(q[0] for q in gg), min(q[1] for q in gg), max(q[1] for q in gg)
            ex = T.get('extent') or [0, 0, 0, 0]
            ck(all(near(ex[i], v, 1e-9) for i, v in enumerate((lo0, la0, lo1, la1))), "the extent is the screen's corners on the ground (%s)" % ex)
            want = set((x, y) for x in range(int(math.floor(tx(lo0, z0))), int(math.floor(tx(lo1, z0))) + 1)
                       for y in range(int(math.floor(ty(la1, z0))), int(math.floor(ty(la0, z0))) + 1))
            got = set((t['x'], t['y']) for t in T.get('tiles', []))
            ck(got == want and len(got) <= 80, "every tile the extent touches, and no other (%d tiles)" % len(got))
            ck(all(t['url'] == 'https://basemaps.cartocdn.com/rastertiles/voyager/%d/%d/%d.png' % (t['z'], t['x'], t['y']) for t in T.get('tiles', [])),
               "street tiles are CARTO's Voyager, {z}/{x}/{y}, no @2x on a 1x screen")   # AMENDED FOR V133d
            cx_, cy_ = tx((lo0 + lo1) / 2, z0), ty((la0 + la1) / 2, z0)
            ks = [(t['x'] + 0.5 - cx_) ** 2 + (t['y'] + 0.5 - cy_) ** 2 for t in T.get('tiles', [])]
            ck(ks == sorted(ks), "nearest the centre first")
            tc = await safe("(a)=>window.__a3dMapTileCorners(a[0],a[1],a[2])", [1000, 2000, 12])
            e_nw = g2m(tlon(1000, 12), tlat(2000, 12), LAT0, LON0)
            e_se = g2m(tlon(1001, 12), tlat(2001, 12), LAT0, LON0)
            ck(tc and near(tc['nw'][0], e_nw[0], 1e-6) and near(tc['nw'][2], e_nw[1], 1e-6) and near(tc['se'][0], e_se[0], 1e-6) and near(tc['se'][2], e_se[1], 1e-6),
               "a tile's corners on the model: Web Mercator's inverse, then onto the model")
            def zf(dist):
                return max(1, min(19, round(math.log2(156543.03392 * math.cos(math.radians(LAT0)) / (dist / (H * 1.2))))))

            def count(ex, z):
                n = 2 ** z
                return (math.floor(tx(ex[2], z)) - math.floor(tx(ex[0], z)) + 1) * \
                    (min(n - 1, math.floor(ty(ex[1], z))) - max(0, math.floor(ty(ex[3], z))) + 1)
            await cam(dist=40000)
            T2 = await tiles()
            ck(T2.get('z') == zf(40000) and len(T2.get('tiles', [])) <= 80, "zoomed far out in plan, the zoom still follows the scale (z%s)" % T2.get('z'))
            await cam(dist=2)
            ck((await tiles()).get('z') == 19, "zoomed right in, no deeper than the street map's zoom 19")
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(300)
            await cam(pitch=0.35, yaw=0.6, dist=900, tx=0, tz=0)
            T3 = await tiles()
            ck(0 < len(T3.get('tiles', [])) <= 80 and T3.get('z') < zf(900) and count(T3['extent'], T3['z'] + 1) > 80,
               "3D toward the horizon: the zoom stepped down from z%d to z%s, the first with at most 80 tiles (%d; %d one finer)" %
               (zf(900), T3.get('z'), len(T3.get('tiles', [])), count(T3.get('extent') or [0, 0, 0, 0], (T3.get('z') or 0) + 1)))
            ex3 = T3.get('extent') or [0, 0, 0, 0]
            far = max(abs(v) for v in g2m(ex3[0], ex3[1], LAT0, LON0) + g2m(ex3[2], ex3[3], LAT0, LON0))
            ck(far <= 900 * 3 * 1.001 + 1, "and nothing past three camera distances from the target (%.0f m)" % far)
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the store")
            SRV['req'].clear()
            SRV['ev'] = asyncio.Event()
            SRV['hold'] = 'all'   # every answer held, so what is in flight does not depend on timing
            await cam(tx=-300, tz=200, dist=600, pitch=c0['pitch'], yaw=c0['yaw'])
            for _ in range(30):
                if len(SRV['req']) >= 12:
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(300)
            T4 = await tiles()
            c4 = await safe("()=>window.__a3dMapCache()") or {}
            ck(c4.get('inflight') == 12 and c4.get('states', {}).get('loading') == 12,
               "a view needing %d tiles asks for 12 at once, no more (%s in flight)" % (len(T4.get('tiles', [])), c4.get('inflight')))
            first = set(SRV['req'][:12])
            ck(len(SRV['req']) == 12 and first == set(t['url'] for t in T4.get('tiles', [])[:12]), "the first 12 asked are the 12 nearest the centre")
            SRV['delay'] = 0.2
            SRV['ev'].set()
            SRV['hold'] = None
            await settle(15000)
            SRV['delay'] = 0.0
            c4 = await safe("()=>window.__a3dMapCache()") or {}
            d4 = await drawn()
            ck(SRV['max'] <= 12 and d4.get('drawn') == len(T4.get('tiles', [])) and d4.get('path') == 'gl',
               "all %d came, never more than 12 at the server at once (%d), all drawn in WebGL" % (len(T4.get('tiles', [])), SRV['max']))
            ck(len(SRV['req']) == len(set(SRV['req'])), "no tile asked for twice")
            n_req = len(SRV['req'])
            await safe("()=>window.__a3dTestPaint()")
            await page.wait_for_timeout(200)
            ck(len(SRV['req']) == n_req, "a repaint asks for nothing it has")
            # a parent while the tile loads
            await cam(tx=2500, tz=2500, dist=600)   # an area none of whose tiles is stored yet
            await settle()
            zP = (await tiles()).get('z')
            SRV['ev'] = asyncio.Event()
            SRV['hold'] = zP + 1
            await cam(dist=300)
            await page.wait_for_timeout(500)
            dP = await drawn()
            ups = [t['up'] for t in dP.get('tiles', [])]
            ck(dP.get('z') == zP + 1 and ups and all(u == 1 for u in ups),
               "zoomed in, each tile still loading is drawn from its parent meanwhile (z%s from z%s)" % (dP.get('z'), zP))
            # a point whose tile and parent differ in colour
            img = await shot()
            pick = None
            for t in dP.get('tiles', [])[:6]:
                if t['up'] == 1 and col(t['x'], t['y'], t['z']) != col(t['x'] // 2, t['y'] // 2, t['z'] - 1):
                    pick = t
                    break
            if pick:
                cm = g2m(tlon(pick['x'] + 0.5, pick['z']), tlat(pick['y'] + 0.5, pick['z']), LAT0, LON0)
                ck(same_col(await at(img, [cm[0], 0, cm[1]]), col(pick['x'] // 2, pick['y'] // 2, pick['z'] - 1)),
                   "on screen: the parent's colour, stretched over the tile")
            SRV['ev'].set()
            SRV['hold'] = None
            await settle()
            img = await shot()
            if pick:
                ck(same_col(await at(img, [cm[0], 0, cm[1]]), col(pick['x'], pick['y'], pick['z'])), "and the tile's own once it comes")
            dP = await drawn()
            ck(all(t['up'] == 0 for t in dP.get('tiles', [])), "every tile its own now")
            # the store kept to about 400
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(200)
            for i in range(16):
                if len(SRV['req']) > 450:
                    break
                await cam(pitch=0.35, yaw=0.6 + i, dist=700, tx=4000 * (i + 1), tz=-3000 * i)
                await settle(6000)
            c5 = await safe("()=>window.__a3dMapCache()") or {}
            ck(len(SRV['req']) > 450 and c5.get('n') <= 400 + 12 and c5.get('n') == c5.get('count'),
               "after %d tiles fetched, the store keeps %s: the least recently drawn went" % (len(SRV['req']), c5.get('n')))
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. on screen")

            async def edge_checks(tn, label):
                await north(tn)
                await cam(tx=60, tz=-60, dist=150, pitch=c0['pitch'], yaw=c0['yaw'])
                await settle()
                img = await shot()
                gc = m2g(60, -60, LAT0, LON0, tn)
                zz = (await tiles()).get('z')
                X, Y = int(math.floor(tx(gc[0], zz))), int(math.floor(ty(gc[1], zz)))
                lonE, latM = tlon(X + 1, zz), tlat(Y + 0.5, zz)
                latS, lonM = tlat(Y + 1, zz), tlon(X + 0.5, zz)
                dlon = 0.6 / (radii(LAT0)[1] * math.cos(math.radians(LAT0))) * 180 / math.pi
                dlat = 0.6 / radii(LAT0)[0] * 180 / math.pi
                res = []
                for (lon, lat, want) in ((lonE - dlon, latM, col(X, Y, zz)), (lonE + dlon, latM, col(X + 1, Y, zz)),
                                         (lonM, latS + dlat, col(X, Y, zz)), (lonM, latS - dlat, col(X, Y + 1, zz))):
                    m = g2m(lon, lat, LAT0, LON0, tn)
                    res.append(same_col(await at(img, [m[0], 0, m[1]]), want, 14))
                ck(all(res), "%s: 0.6 m either side of a tile's east and south edges, each tile's own colour (%s)" % (label, res))
                return img
            await edge_checks(0, "WebGL, plan")
            await edge_checks(30, "WebGL, plan, true north 30")
            await safe("()=>{document.getElementById('a3d-present').click();}")
            await page.wait_for_timeout(300)
            ck(await safe("()=>window.__a3dPresentMode()") is True, "the presentation appearance draws on the 2D canvas")
            await edge_checks(30, "2D canvas, plan, true north 30")
            ck((await drawn()).get('path') == '2d', "drawn by the 2D canvas there")
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dTestPaint()")
            dd = await drawn()
            ck(dd.get('path') == '2d' and dd.get('reason') == '3d' and dd.get('drawn') == 0,
               "the 2D canvas has no perspective texture: in 3D it draws no map, and says why")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            # a plot leaves the map out
            await cam(tx=60, tz=-60, dist=150)
            await settle()
            pngb = b''
            try:
                async with page.expect_download() as dl:
                    await safe("()=>window.__a3dRunAct('m:exportpng')")
                pngb = pathlib.Path(await (await dl.value).path()).read_bytes()
            except Exception as e:
                print('      (download failed: %s)' % str(e)[:160])
            im = Image.open(io.BytesIO(pngb)).convert('RGB') if pngb else None
            hit = 0
            if im:
                for yy in range(0, im.height, 7):
                    for xx in range(0, im.width, 7):
                        if any(same_col(im.getpixel((xx, yy)), c, 6) for c in PALETTE):
                            hit += 1
            ck(im is not None and hit == 0, "the PNG export, a plot, has none of the map in it (%s tile-coloured samples)" % hit)
            await safe("()=>{document.getElementById('a3d-present').click();}")
            await page.wait_for_timeout(300)
            ck(await safe("()=>window.__a3dPresentMode()") is False, "back to the technical appearance, and WebGL")
            await north(0)
            # opacity, and a solid over the map
            await nosel()
            await set_field('[data-propmap="opacity"]', '50')
            ck((await safe("()=>window.__a3dMapSettings()") or {}).get('opacity') == 0.5, "opacity 50%")
            await settle()
            img = await shot()
            gc = m2g(75, -45, LAT0, LON0)
            zz = (await tiles()).get('z')
            want = col(int(math.floor(tx(gc[0], zz))), int(math.floor(ty(gc[1], zz))), zz)
            ck(same_col(await at(img, [75, 0, -45]), mix(want, 0.5), 12), "at 50%% the tile is half way to the background (%s, %s)" % (await at(img, [75, 0, -45]), mix(want, 0.5)))
            await set_field('[data-propmap="opacity"]', '100')
            await safe("()=>{window.__a3dTestSetObjs([]);}")
            await safe("()=>{var o=window.__a3dAdd('box',{Length:20,Width:20,Height:20});window.__a3dSetPos(o.id,75,0,-45);window.__a3dSelectFor([]);}")
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(300)
            await cam(pitch=0.9, yaw=0.4, dist=60, tx=75, tz=-45)
            await settle()
            img = await shot()
            pb = await at(img, [75, 7, -45])
            ck(pb is not None and not any(same_col(pb, c, 25) for c in PALETTE), "a solid stands over the map: its top is not a tile's colour (%s)" % (pb,))
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dTestPaint();}")
            await safe("()=>window.__a3dSetView('front')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dTestPaint()")
            ck((await drawn()).get('reason') == 'side', "an elevation looks along the ground: no map, and it says so")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await cam(tx=60, tz=-60, dist=150)

            # ---------------------------------------------------------------------------------
            print("\n-- 6. failures are said")
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck('href="https://www.openstreetmap.org/copyright"' in ft and '© OpenStreetMap contributors © CARTO' in ft,
               "the street map's credit: OpenStreetMap contributors and CARTO, linked to OSM's copyright page")   # AMENDED FOR V133d
            ck(await safe("()=>{var f=document.getElementById('a3d-mapattr');return !f.hidden&&f.textContent;}") == '© OpenStreetMap contributors © CARTO',
               "and it is on screen over the viewport")
            n0 = len(SRV['req'])
            await nosel()
            await set_field('[data-propmap="style"]', 'satellite')
            await settle()
            sat = [u for u in SRV['req'][n0:] if 'arcgisonline' in u]
            T6 = await tiles()
            ck(sat and all(re.search(r'/World_Imagery/MapServer/tile/%d/\d+/\d+$' % T6['z'], u) for u in sat) and
               set(sat) <= set(t['url'] for t in T6.get('tiles', [])) and
               all(t['url'].endswith('/tile/%d/%d/%d' % (t['z'], t['y'], t['x'])) for t in T6.get('tiles', [])),
               "satellite asks Esri's World Imagery, {z}/{y}/{x} (%d asked)" % len(sat))
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck('Esri, Maxar, Earthstar Geographics' in ft, "with Esri's credit")
            ck('server.arcgisonline.com: %d tiles did not load (offline, or the server does not allow browser access)' % len(sat) in ft,
               "offline: every tile failed, and the credit line names the server and counts them (%s)" % re.sub('<[^>]+>', '', ft)[:160])
            ck((await drawn()).get('drawn') == 0, "and nothing of it is drawn")
            srv, hits = nocors_server()
            host = '127.0.0.1:%d' % srv.server_address[1]
            await safe("(u)=>window.__a3dMapSet('url',u)", 'http://%s/{z}/{x}/{y}.png' % host)
            await safe("()=>window.__a3dMapSet('style','custom')")
            await settle()
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck(hits and ('%s: %d tile' % (host, len(hits))) in ft and 'does not allow browser access' in ft and (await drawn()).get('drawn') == 0,
               "a real server that sends no CORS header answered %d times, yet the browser kept its tiles from the page: named, nothing drawn (%s)" %
               (len(hits), re.sub('<[^>]+>', '', ft)[:120]))
            ck(not [u for u in SRV['ext'] if 'proxy' in u], "and nothing was sent round it through a proxy")
            srv.shutdown()
            await safe("()=>window.__a3dMapSet('url','')")
            await set_field('[data-propmap="style"]', 'street')
            await settle()
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck('did not load' not in ft and (await safe("()=>window.__a3dMapCache()") or {}).get('fail') == {},
               "a new style forgets the failures")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. settings")
            await nosel()
            await set_field('[data-propmap="opacity"]', '5')
            ck((await safe("()=>window.__a3dMapSettings()"))['opacity'] == 1 and '10 to 100' in await toast(), "opacity 5%% is refused, with the range")
            await set_field('[data-propmap="style"]', 'custom')
            ck((await drawn()).get('reason') == 'url' or (await tiles()).get('reason') == 'url', "custom tiles with no URL: nothing asked, and it says why")
            ck('give the custom tile URL' in (await safe("()=>window.__a3dMapFooter()") or ''), "the credit line asks for the URL")
            await nosel()
            ck('data-propmap="url"' in await props_html() and 'data-propmap="credit"' in await props_html(), "custom shows its URL and credit fields")
            await set_field('[data-propmap="url"]', 'https://tiles.example.org/{z}/{x}.png')
            ck((await safe("()=>window.__a3dMapSettings()"))['url'] == '' and '{z}, {x} and {y}' in await toast(), "a URL without {y} is refused, saying what it needs")
            await set_field('[data-propmap="url"]', 'ftp://tiles.example.org/{z}/{x}/{y}.png')
            ck((await safe("()=>window.__a3dMapSettings()"))['url'] == '', "so is one that is not http or https")
            n0 = len(SRV['req'])
            await set_field('[data-propmap="url"]', 'https://tiles.example.org/{z}/{x}/{y}.png')
            await set_field('[data-propmap="credit"]', '  Example   Council  ')
            await settle()
            ex_ = [u for u in SRV['req'][n0:] if 'tiles.example.org' in u]
            ck(ex_ and (await drawn()).get('drawn') == len((await tiles()).get('tiles', [])), "custom tiles come from the URL given (%d)" % len(ex_))
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck(ft == 'Example Council', "with the credit given, tidied (%r)" % ft)
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck((await safe("()=>window.__a3dMapSettings()"))['credit'] == '', "a setting is one undo step")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck((await safe("()=>window.__a3dMapSettings()"))['url'] == '' and (await safe("()=>window.__a3dMapSettings()"))['style'] == 'custom', "and the URL before it")
            await nosel()
            await set_field('[data-propmap="style"]', 'street')
            ck(await safe("()=>{document.querySelector('.a3d-sheetview').classList.add('open');return getComputedStyle(document.getElementById('a3d-mapattr')).display;}") == 'none',
               "on a sheet the credit line is not shown: the paper has no map")
            await safe("()=>document.querySelector('.a3d-sheetview').classList.remove('open')")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. the address")
            await nosel()
            await set_field('[data-propmap="style"]', 'off')
            before = await safe("()=>window.__a3dSunSettings()")
            await safe("()=>window.__a3dCamSet({tx:40,tz:40})")
            SRV['nom'].clear()
            r = await safe("()=>window.__a3dMapFind('  Big   Ben ')")
            ck(r and r.get('found') and len(SRV['nom']) == 1, "Find asks Nominatim once (%s)" % SRV['nom'])
            ck(SRV['nom'] and SRV['nom'][0] == 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=Big%20Ben',
               "for the first result, as JSON, the query tidied")
            s = await safe("()=>window.__a3dSunSettings()")
            ck(s and s['lat'] == 51.5007292 and s['lon'] == -0.1246254, "the place found is the site's latitude and longitude (%s)" % s)
            ck((await safe("()=>window.__a3dMapSettings()"))['style'] == 'street', "the street map came on, the map having been off")
            stt = await safe("()=>window.__a3dState()")
            ck(stt and stt['cam']['tx'] == 0 and stt['cam']['tz'] == 0, "the view went to model 0,0")
            ck('Big Ben' in await toast() and 'Model 0,0 is there now' in await toast() and 'Nominatim' in await toast(),
               "and it says what it found, what that did, and whose search it was")
            await nosel()
            h = await props_html()
            ck('value="Big Ben, Westminster, London"' in h and '51.500729' in h, "Properties shows the address and where model 0,0 is")
            r2 = await safe("()=>window.__a3dMapFind('Big Ben')")
            ck(r2 is None and len(SRV['nom']) == 1 and 'One search a second' in await toast(), "a second Find inside the second is refused, not sent")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            s = await safe("()=>window.__a3dSunSettings()")
            ck(s['lat'] == before['lat'] and s['lon'] == before['lon'] and (await safe("()=>window.__a3dMapSettings()"))['style'] == 'off',
               "one undo puts the site and the map back")
            await safe("()=>window.__a3dMapFindReset()")
            r = await safe("()=>window.__a3dMapFind('nowhere at all')")
            ck(r and r.get('found') is False and 'Nothing found for nowhere at all' in await toast() and
               (await safe("()=>window.__a3dSunSettings()"))['lat'] == before['lat'], "nothing found: said, nothing changed")
            await safe("()=>window.__a3dMapFindReset()")
            r = await safe("()=>window.__a3dMapFind('error please')")
            ck(r and r.get('found') is False and 'Address search failed: nominatim.openstreetmap.org answered HTTP 500' in await toast(),
               "a server error: said, naming the server and the status")   # AMENDED FOR V133d
            await safe("()=>window.__a3dMapFindReset()")
            await nosel()
            n0 = len(SRV['nom'])
            await safe("""()=>{var e=document.querySelector('#a3d-propsbody [data-propmap="addr"]');e.value='Big Ben';e.focus();}""")
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(500)
            ck(len(SRV['nom']) == n0 + 1 and (await safe("()=>window.__a3dSunSettings()"))['lat'] == 51.5007292,
               "Enter in the Address field finds it")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            await safe("()=>window.__a3dMapFindReset()")
            await safe("()=>window.__a3dRunCmd('findaddress')")
            await page.wait_for_timeout(150)
            ck(await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d&&d.textContent;}") == 'Find Address',
               "FINDADDRESS opens a Find Address box")
            n0 = len(SRV['nom'])
            await safe("()=>{var e=document.querySelector('.a3d-dlg [data-a3dp=\"q\"]');e.value='Big Ben';}")
            await safe("()=>{document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]').click();}")
            await page.wait_for_timeout(500)
            ck(len(SRV['nom']) == n0 + 1 and (await safe("()=>window.__a3dSunSettings()"))['lat'] == 51.5007292 and
               not await safe("()=>!!document.querySelector('.a3d-dlg')"), "and Find in it finds the place and closes")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. site data in")
            await place(LAT0, LON0)
            await north(0)
            await safe("()=>{window.__a3dTestSetObjs([]);}")
            cx, cy = LON0 + 0.001, LAT0 + 0.001
            d = 0.0005
            outer = [[cx - d, cy - d], [cx + d, cy - d], [cx + d, cy + d], [cx - d, cy + d], [cx - d, cy - d]]
            hole = [[cx - d / 4, cy - d / 4], [cx + d / 4, cy - d / 4], [cx + d / 4, cy + d / 4], [cx - d / 4, cy - d / 4]]
            fc = {'type': 'FeatureCollection', 'features': [
                {'type': 'Feature', 'properties': {'name': 'Lot 12', 'zoning': 'R2', 'area_m2': 8800.5, 'tags': {'a': 1}},
                 'geometry': {'type': 'Polygon', 'coordinates': [outer, hole]}},
                {'type': 'Feature', 'properties': {'name': 'Kerb'},
                 'geometry': {'type': 'LineString', 'coordinates': [[cx - d, cy - 2 * d], [cx + d, cy - 2 * d, 12.5]]}},
                {'type': 'Feature', 'properties': {'name': 'Hydrant'}, 'geometry': {'type': 'Point', 'coordinates': [cx, cy - 3 * d]}},
                {'type': 'Feature', 'properties': None, 'geometry': {'type': 'MultiPolygon', 'coordinates': [
                    [[[cx + 2 * d, cy], [cx + 3 * d, cy], [cx + 3 * d, cy + d]]], [[[cx + 4 * d, cy], [cx + 5 * d, cy], [cx + 5 * d, cy + d]]]]}},
                {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'GeometryCollection', 'geometries': [
                    {'type': 'Point', 'coordinates': [cx, cy + 3 * d]}]}},
            ]}
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before the import, so its undo has to be its own
            res = await safe("(a)=>window.__a3dGeoImportText(a[0],a[1])", [json.dumps(fc), 'parcels.geojson'])
            ck(res and res.get('shapes') == 5 and res.get('points') == 2 and not res.get('placedSite'),
               "GeoJSON in: a polygon's outer ring and hole, a line, two triangles, two points (%s)" % res)
            objs = (await safe("()=>window.__a3dState().objs") or [])
            byname = {}
            for o in objs:
                byname.setdefault(o['name'], []).append(o)
            lots = byname.get('Lot 12', [])
            ck(len(lots) == 2 and all(o['t'] == 'sketch' and o.get('closed') for o in lots), "a ring is a closed sketch, the hole too")
            if lots:
                o = lots[0]
                ok = len(o['pts']) == 4
                for p, g_ in zip(o['pts'], outer[:4]):
                    e = g2m(g_[0], g_[1], LAT0, LON0)
                    ok = ok and near(p[0], e[0], 1e-6) and near(p[1], e[1], 1e-6)
                ck(ok, "its corners where their longitude and latitude are, the closing repeat dropped")
                ck(o.get('y') == 0 and o.get('pos') == [0, 0, 0], "on the ground, the lowest level")
            gl = await safe("(i)=>window.__a3dGeoOf(i)", lots[0]['id'] if lots else '')
            ck(gl and gl['source'] == 'parcels.geojson' and gl['props'] == {'name': 'Lot 12', 'zoning': 'R2', 'area_m2': 8800.5, 'tags': '{"a":1}'},
               "each keeps its feature's properties and where it came from (%s)" % gl)
            gh = await safe("(i)=>window.__a3dGeoOf(i)", lots[1]['id'] if len(lots) > 1 else '')
            ck(gh and gh.get('part') == 'hole', "and the hole knows it is one")
            kerb = byname.get('Kerb', [{}])[0]
            ck(kerb.get('t') == 'sketch' and kerb.get('closed') is False and len(kerb.get('pts', [])) == 2, "a line is an open sketch")
            hyd = byname.get('Hydrant', [{}])[0]
            eh = g2m(cx, cy - 3 * d, LAT0, LON0)
            ck(hyd.get('kind') == 'point' and near(hyd['pts'][0][0], eh[0], 1e-6) and near(hyd['pts'][0][1], eh[1], 1e-6), "a point is a point, where it is")
            lids = set(o.get('layer') for o in objs)
            lname = await safe("(id)=>(window.__a3dLayers().filter(function(x){return x.id===id;})[0]||{}).name", list(lids)[0] if lids else '')
            ck(len(lids) == 1 and lname == 'Site data', "all on one layer, Site data (%s)" % lname)
            await nosel()
            cur = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-propmodel=\"layer\"]');return e&&e.value;}")
            ck(cur and cur not in lids, "and the current layer stays the one it was (%s)" % cur)
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", lots[0]['id'] if lots else '')
            h = await props_html()
            ck('data-a3dpgrp="Site Data"' in h and 'zoning' in h and 'R2' in h and 'parcels.geojson' in h, "Properties shows a Site Data group with them")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(len(await safe("()=>window.__a3dState().objs") or []) == 0 and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7,
               "one undo takes the whole import back, and only it")
            await safe("()=>window.__a3dMapSet('opacity',100)")
            # refusals
            n_obj = 0
            bad = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [512000.5, 180000.25]}}]}
            r = await safe("(a)=>window.__a3dGeoImportText(a,'grid.geojson')", json.dumps(bad))
            ck(r and 'not longitude and latitude' in r.get('error', '') and '512000.5, 180000.25' in r.get('error', '') and
               len(await safe("()=>window.__a3dState().objs") or []) == n_obj, "a projected grid is refused, naming the position, nothing placed")
            bad = {'type': 'FeatureCollection', 'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::27700'}}, 'features': []}
            r = await safe("(a)=>window.__a3dGeoImportText(a,'osgb.geojson')", json.dumps(bad))
            ck(r and 'EPSG::27700' in r.get('error', '') and 'WGS84' in r.get('error', ''), "a file naming another CRS is refused, saying which")
            r = await safe("()=>window.__a3dGeoImportText('{\"name\":\"a project\"}','x.json')")
            ck(r and 'not GeoJSON' in r.get('error', ''), "a JSON that is not GeoJSON is refused")
            r = await safe("()=>window.__a3dGeoImportText('{nope','x.geojson')")
            ck(r and 'is not GeoJSON or KML' in r.get('error', ''), "nor is text that does not read")
            # no site place yet: the data's centre
            await place(None, None)
            ck(await safe("()=>window.__a3dSunSettings().lat") is None, "the site's place cleared")
            r = await safe("(a)=>window.__a3dGeoImportText(a,'p.geojson')", json.dumps(fc))
            s = await safe("()=>window.__a3dSunSettings()")
            e_lat = round(((cy - 3 * d) + (cy + 3 * d)) / 2 * 1e7) / 1e7
            e_lon = round(((cx - d) + (cx + 5 * d)) / 2 * 1e7) / 1e7
            ck(r and r.get('placedSite') and s and near(s['lat'], e_lat, 1e-9) and near(s['lon'], e_lon, 1e-9),
               "with no place yet, the data's centre becomes the site's (%s, %s)" % (s and s['lat'], s and s['lon']))
            ck('set to the data' in await toast(), "and it says so")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            s = await safe("()=>window.__a3dSunSettings()")
            ck(s and s['lat'] is None and s['lon'] is None and len(await safe("()=>window.__a3dState().objs") or []) == 0,
               "the same undo takes the place back with the data, and only that")
            await place(LAT0, LON0)
            # KML, through GEOIMPORT and the file picker
            kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document>
<Placemark><name>Parcel 7</name><description>Corner lot</description>
<ExtendedData><Data name="zone"><value>C1</value></Data><SchemaData><SimpleData name="apn">123-45</SimpleData></SchemaData></ExtendedData>
<Polygon><outerBoundaryIs><LinearRing><coordinates>
%f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0 %f,%f,0
</coordinates></LinearRing></outerBoundaryIs>
<innerBoundaryIs><LinearRing><coordinates>%f,%f %f,%f %f,%f %f,%f</coordinates></LinearRing></innerBoundaryIs></Polygon></Placemark>
<Placemark><name>Gate</name><Point><coordinates>%f,%f,0</coordinates></Point></Placemark>
<Placemark><name>Path</name><LineString><coordinates>%f,%f %f,%f %f,%f</coordinates></LineString></Placemark>
</Document></kml>''' % (cx - d, cy - d, cx + d, cy - d, cx + d, cy + d, cx - d, cy + d, cx - d, cy - d,
                        cx, cy, cx + d / 4, cy, cx + d / 4, cy + d / 4, cx, cy,
                        cx, cy - 2 * d, cx - d, cy - 3 * d, cx, cy - 3 * d, cx + d, cy - 3 * d)
            tmp = pathlib.Path(tempfile.mkdtemp()) / 'site.kml'
            tmp.write_text(kml)
            try:
                async with page.expect_file_chooser(timeout=5000) as fcw:
                    await safe("()=>window.__a3dRunCmd('geoimport')")
                chooser = await fcw.value
                ck(set(chooser.element and (await chooser.element.get_attribute('accept') or '').split(',')) == {'.geojson', '.json', '.kml'},
                   "GEOIMPORT opens a file picker for .geojson, .json and .kml")
                await chooser.set_files(str(tmp))
            except Exception as e:
                ck(False, "GEOIMPORT opens a file picker (%s)" % str(e)[:120])
            await page.wait_for_timeout(600)
            objs = await safe("()=>window.__a3dState().objs") or []
            names = sorted(o['name'] for o in objs)
            ck(names == ['Gate', 'Parcel 7', 'Parcel 7', 'Path'], "KML in: the parcel and its hole, the gate, the path (%s)" % names)
            p7 = [o for o in objs if o['name'] == 'Parcel 7']
            g7 = await safe("(i)=>window.__a3dGeoOf(i)", p7[0]['id'] if p7 else '')
            ck(g7 and g7['props'] == {'name': 'Parcel 7', 'description': 'Corner lot', 'zone': 'C1', 'apn': '123-45'} and g7['source'] == 'site.kml',
               "with its name, description and extended data (%s)" % (g7 and g7['props']))
            if p7:
                e = g2m(cx + d, cy + d, LAT0, LON0)
                ck(len(p7[0]['pts']) == 4 and near(p7[0]['pts'][2][0], e[0], 1e-6) and near(p7[0]['pts'][2][1], e[1], 1e-6),
                   "its corners where the KML puts them")
            r = await safe("()=>window.__a3dGeoImportText('<kml><Placemark>','bad.kml')")
            ck(r and 'not well-formed' in r.get('error', ''), "a KML that is not well-formed XML is refused")
            await safe("()=>{window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. the plan out")
            await north(25)
            fl = await safe("()=>window.__a3dFloorAt([[0,0],[12,0],[12,8],[0,8]],0,0.2)")
            wl = await safe("()=>window.__a3dWall([[0,20],[10,20],[10,26]],0.2,3,'center',false)")
            await safe("""()=>{var o=window.__a3dState().objs;o.push({id:'RM1',t:'room',name:'Room_1',col:'#7fd4c4',pos:[0,0,0],
              pts:[[20,0],[26,0],[26,5],[20,5]],y:0,area:30,levelId:'lvl-0',layer:'layer-0'});window.__a3dTestSetObjs(o);}""")
            bx = await safe("()=>{var o=window.__a3dAdd('box',{Length:40,Width:20,Height:30});window.__a3dSetPos(o.id,-30,0,-30);return o.id;}")
            await safe("(i)=>window.__a3dUsageAssign([i],'use-off')", bx)
            pt = await safe("()=>{var o=window.__a3dState().objs;o.push({id:'PT1',t:'sketch',kind:'point',name:'Point 1',col:'#ffd479',pos:[0,0,0],pts:[[5,-5]],y:0,closed:false,layer:'layer-0'});window.__a3dTestSetObjs(o);return 'PT1';}")
            await safe("""()=>{var o=window.__a3dState().objs;o.push({id:'SK1',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:[[40,0],[60,0],[60,30],[40,30]],y:0,closed:true,layer:'layer-0'});window.__a3dTestSetObjs(o);}""")
            pl = await safe("()=>window.__a3dPropertyFromSketch('SK1')")
            fcx = await safe("()=>window.__a3dGeoExport()") or {}
            feats = fcx.get('features', [])
            by = {}
            for f in feats:
                by.setdefault(f['properties']['kind'], []).append(f)
            ck(fcx.get('type') == 'FeatureCollection' and fcx.get('bim_site', {}).get('latitude') == LAT0 and fcx['bim_site'].get('trueNorth') == 25,
               "a FeatureCollection, saying where model 0,0 is and the true north")
            ck(set(by) >= {'floor', 'wall', 'room', 'mass', 'point', 'property'}, "a floor, a wall, a room, a mass, a point, a property line (%s)" % sorted(by))

            def back(c):
                return g2m(c[0], c[1], LAT0, LON0, 25)
            f = (by.get('floor') or [{}])[0]
            ring = f.get('geometry', {}).get('coordinates', [[]])[0]
            bk = [back(c) for c in ring]
            want = [(0, 0), (12, 0), (12, 8), (0, 8), (0, 0)]
            ck(f.get('geometry', {}).get('type') == 'Polygon' and len(bk) == 5 and all(near(a[0], b[0], 0.002) and near(a[1], b[1], 0.002) for a, b in zip(bk, want)),
               "the floor goes out as a closed ring that comes back onto the model within 2 mm")
            ck(f.get('properties', {}).get('area') == 96 and f['properties'].get('level') == 'Level 0' and f['properties'].get('layer'),
               "with its area, level and layer (%s)" % f.get('properties'))
            ck(all(len(str(c[0]).split('.')[-1]) <= 8 and len(str(c[1]).split('.')[-1]) <= 8 for c in ring), "coordinates to 8 decimals, about a millimetre")
            w = (by.get('wall') or [{}])[0]
            wb = [back(c) for c in w.get('geometry', {}).get('coordinates', [])]
            ck(w.get('geometry', {}).get('type') == 'LineString' and len(wb) == 3 and near(wb[2][0], 10, 0.002) and near(wb[2][1], 26, 0.002),
               "a wall goes out as its centreline")
            rm = (by.get('room') or [{}])[0]
            ck(rm.get('properties', {}).get('area') == 30 and rm['properties'].get('name') == 'Room_1', "a room with its area and name")
            m = (by.get('mass') or [{}])[0]
            mp = m.get('properties', {})
            ck(m.get('geometry', {}).get('type') == 'MultiPolygon' and near(mp.get('area'), 40 * 0.35 * 20 * 0.35, 0.01) and mp.get('usage') == 'Office' and
               near(mp.get('height'), 30 * 0.35, 0.01) and 'gfa' in mp, "a mass goes out as its footprint, with its usage, height and GFA (%s)" % mp)
            mb = [back(c) for c in m.get('geometry', {}).get('coordinates', [[[]]])[0][0]]
            xs, zs = [p[0] for p in mb], [p[1] for p in mb]
            ck(mb and near(min(xs), -30 - 7, 0.01) and near(max(xs), -30 + 7, 0.01) and near(min(zs), -30 - 3.5, 0.01) and near(max(zs), -30 + 3.5, 0.01),
               "its footprint where the box stands")
            p = (by.get('point') or [{}])[0]
            pb2 = back(p.get('geometry', {}).get('coordinates', [0, 0]))
            ck(p.get('geometry', {}).get('type') == 'Point' and near(pb2[0], 5, 0.002) and near(pb2[1], -5, 0.002), "a point goes out as a point")
            pr = (by.get('property') or [{}])[0]
            ck(pr.get('geometry', {}).get('type') == 'Polygon', "a property line goes out as its parcel")
            # site data goes back out with what it came with
            await safe("(a)=>window.__a3dGeoImportText(a[0],a[1])", [json.dumps(fc), 'parcels.geojson'])
            fcx = await safe("()=>window.__a3dGeoExport()") or {}
            sd = [f for f in fcx.get('features', []) if f['properties'].get('kind') == 'site data' and f['properties'].get('zoning') == 'R2']
            ck(sd and sd[0]['properties'].get('source') == 'parcels.geojson' and sd[0]['properties'].get('area_m2') == 8800.5,
               "imported site data goes back out with its own properties and source")
            ring = sd[0]['geometry']['coordinates'][0] if sd else []
            ck(ring and all(near(a[0], b[0], 1e-8) and near(a[1], b[1], 1e-8) for a, b in zip(ring, outer)), "and on its own longitudes and latitudes")
            try:
                async with page.expect_download() as dl:
                    await safe("()=>window.__a3dRunCmd('geoexport')")
                dv = await dl.value
                body = json.loads(pathlib.Path(await dv.path()).read_text())
                ck(dv.suggested_filename.endswith('.geojson') and len(body.get('features', [])) == len(fcx.get('features', [])),
                   "GEOEXPORT downloads it as %s (%d features)" % (dv.suggested_filename, len(body.get('features', []))))
            except Exception as e:
                ck(False, "GEOEXPORT downloads a .geojson (%s)" % str(e)[:120])
            await north(0)
            await place(None, None)
            r = await safe("()=>window.__a3dGeoExport()")
            ck(r and 'latitude and longitude' in r.get('error', ''), "with no site place, the export is refused, saying why")
            await place(LAT0, LON0)

            # ---------------------------------------------------------------------------------
            print("\n-- 11. commands and a reload")
            await nosel()
            await set_field('[data-propmap="style"]', 'off')
            seq = []
            for _ in range(3):
                seq.append(await safe("()=>window.__a3dMapCommand()"))
            ck(seq == ['street', 'satellite', 'off'], "MAP steps off, street, satellite, off: custom skipped with no URL (%s)" % seq)
            await safe("()=>window.__a3dMapSet('url','https://tiles.example.org/{z}/{x}/{y}.png')")
            seq = [await safe("()=>window.__a3dMapCommand()") for _ in range(4)]
            ck(seq == ['street', 'satellite', 'custom', 'off'], "and custom once it has one (%s)" % seq)
            await safe("()=>window.__a3dRunCmd('map')")
            ck((await safe("()=>window.__a3dMapSettings()"))['style'] == 'street' and 'Map: Street (CARTO, OpenStreetMap data)' in await toast(),   # AMENDED FOR V133d
               "MAP runs as a command and says what is on, with its credit (%r)" % await toast())
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>['MAP','FINDADDRESS','GEOIMPORT','GEOEXPORT'].indexOf(c.name)>=0).map(c=>({n:c.name,where:c.where}))") or []
            wh = {c['n']: ' '.join(c['where']) for c in cat}
            ck(len(cat) == 4 and all('Site' in wh[n] for n in ('MAP', 'FINDADDRESS', 'GEOIMPORT')) and 'Export' in wh['GEOEXPORT'],
               "all four are on the ribbon, the map's in Site, GeoJSON in Export (%s)" % wh)
            for q, n in (('satellite', 'MAP'), ('aerial', 'MAP'), ('geocode', 'FINDADDRESS'), ('nominatim', 'FINDADDRESS'), ('kml', 'GEOIMPORT'),
                         ('parcels', 'GEOIMPORT'), ('geojson', 'GEOIMPORT')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q) or [])]
                ck(n in nm[:3], "searching %r finds %s (%s)" % (q, n, nm))
            acc = await safe("()=>document.getElementById('a3d-filein').getAttribute('accept')")
            ck('.geojson' in acc and '.kml' in acc, "Import CAD takes .geojson and .kml too")
            await settle()
            before = await safe("()=>window.__a3dMapSettings()")
            nsd = len([o for o in (await safe("()=>window.__a3dState().objs") or []) if o['name'] == 'Lot 12'])
            await page.wait_for_timeout(600)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(await safe("()=>window.__a3dMapSettings()") == before, "the map's settings outlive a reload (%s)" % before)
            objs = await safe("()=>window.__a3dState().objs") or []
            lots = [o for o in objs if o['name'] == 'Lot 12']
            ck(len(lots) == nsd == 2 and (await safe("(i)=>window.__a3dGeoOf(i)", lots[0]['id']) or {}).get('props', {}).get('zoning') == 'R2',
               "and so does the site data, with its properties")
            await settle()
            ck((await drawn()).get('drawn', 0) > 0, "and the map comes back on its own")
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
