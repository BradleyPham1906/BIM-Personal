#!/usr/bin/env python3
"""bim_phase133d_map_density_browser_tests.py -- V133d: the map, from the owner's first real use.

Run at device scale 2, as the owner's Retina screen is. The tile servers are routed in the browser.

  1. THE STREET MAP is Esri's World Street Map (OSM's and CARTO's servers refuse a page opened as a
     file -- V133f), its zoom counting the density; a custom URL with {r} gets @2x tiles instead.
  2. THE SATELLITE's zoom counts the screen's density; the tile cap grows with it.
  3. MIPMAPS on every tile.
  4. NOMINATIM's refusal and being busy are said as such.
  5. ZOOM (V133e): 0.5 m to 200 km, about the cursor, the far plane following the view.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, struct, sys, traceback, zlib
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


_PNG = {}


def png(size, rgb=(200, 120, 60)):
    if size not in _PNG:
        raw = b''.join(b'\x00' + bytes(rgb) * size for _ in range(size))

        def ch(t, d):
            c = struct.pack('>I', len(d)) + t + d
            return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        _PNG[size] = b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) + \
            ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
    return _PNG[size]


LAT0 = 40.0
REQ = []
NOM = {'status': 403}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1400, 'height': 900}, device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def tiles(route):
            u = route.request.url
            REQ.append(u)
            await route.fulfill(status=200, body=png(512 if '@2x' in u else 256),
                                headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://tiles.example.org/**', tiles)
        await ctx.route('https://server.arcgisonline.com/**', tiles)

        async def nom(route):
            await route.fulfill(status=NOM['status'], body='no', headers={'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://nominatim.openstreetmap.org/**', nom)
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

        has = await safe("()=>!!window.__acad3dV133d")
        ck(bool(has), "__acad3dV133d marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def settle():
            for _ in range(60):
                c = await safe("()=>window.__a3dMapCache()") or {}
                if c.get('inflight', 1) == 0:
                    break
                await page.wait_for_timeout(100)
            await safe("()=>window.__a3dTestPaint()")
            await page.wait_for_timeout(100)

        def zf(dist, H, dens):
            return max(1, min(19, round(math.log2(156543.03392 * math.cos(math.radians(LAT0)) * dens / (dist / (H * 1.2))))))

        try:
            print("\n-- 1. the street map")
            ck(await safe("()=>window.__a3dMapDpr()") == 2, "a density-2 screen, as the owner's")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            for k, v in (('sunlat', '40'), ('sunlon', '-75')):
                await safe("(a)=>{var e=document.querySelector('[data-propmodel=\"'+a[0]+'\"]');e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));}", [k, v])
            await safe("()=>window.__a3dMapSet('style','street')")
            await safe("()=>window.__a3dCamSet({tx:60,tz:-60,dist:600})")
            H = await safe("()=>document.getElementById('a3d-canvas').height/window.devicePixelRatio")
            T = await safe("()=>window.__a3dMapTiles()") or {}
            ck(T.get('tiles') and all(re.match(r'^https://server\.arcgisonline\.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/\d+/\d+/\d+$', t['url']) for t in T['tiles']),
               "street tiles are Esri's World Street Map, keyless (%s)" % (T.get('tiles') or [{}])[0].get('url'))
            ck(T.get('z') == zf(600, H, 2), "their zoom counts the density (z%s)" % T.get('z'))
            await settle()
            ft = await safe("()=>window.__a3dMapFooter()") or ''
            ck('Map: Esri, HERE, Garmin, USGS, © OpenStreetMap contributors, and the GIS User Community' in ft, "credited to Esri's sources, OpenStreetMap's contributors among them")
            ck(not [u for u in REQ if 'tile.openstreetmap.org' in u or 'cartocdn' in u], "and neither OpenStreetMap's own nor CARTO's servers are asked")
            await safe("()=>{window.__a3dMapSet('url','https://tiles.example.org/{z}/{x}/{y}{r}.png');window.__a3dMapSet('style','custom');}")
            T = await safe("()=>window.__a3dMapTiles()") or {}
            ck(T.get('tiles') and all(t['url'].endswith('@2x.png') for t in T['tiles']), "a URL with {r} gets @2x tiles on this screen (%s)" % (T.get('tiles') or [{}])[0].get('url'))
            ck(T.get('z') == zf(600, H, 1), "and its zoom is not raised for the density: @2x tiles carry it (z%s)" % T.get('z'))

            print("\n-- 2. the satellite")
            await safe("()=>window.__a3dMapSet('style','satellite')")
            T = await safe("()=>window.__a3dMapTiles()") or {}
            ck(T.get('z') == zf(600, H, 2) and T['z'] == zf(600, H, 1) + 1, "its zoom counts the density: one level finer than in CSS pixels (z%s)" % T.get('z'))
            ck(all('@2x' not in t['url'] for t in T.get('tiles', [])), "Esri has no @2x: plain tiles")
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dCamSet({pitch:0.35,yaw:0.6,dist:900,tx:0,tz:0})")
            T = await safe("()=>window.__a3dMapTiles()") or {}
            n = len(T.get('tiles', []))
            ex = T.get('extent') or [0, 0, 0, 0]

            def cnt(z):
                def tx(lon):
                    return (lon + 180) / 360 * 2 ** z

                def ty(lat):
                    la = math.radians(lat)
                    return (1 - math.log(math.tan(la) + 1 / math.cos(la)) / math.pi) / 2 * 2 ** z
                return (math.floor(tx(ex[2])) - math.floor(tx(ex[0])) + 1) * (math.floor(ty(ex[1])) - math.floor(ty(ex[3])) + 1)
            ck(n <= 160 and (T['z'] >= zf(900, H, 2) or cnt(T['z'] + 1) > 160), "at most 160 tiles, the finest zoom that fits (%d at z%s)" % (n, T.get('z')))
            seen = []
            for dd in range(300, 3000, 75):
                T2 = await safe("(d)=>{window.__a3dCamSet({dist:d});return window.__a3dMapTiles();}", dd) or {}
                seen.append(len(T2.get('tiles', [])))
                if 80 < seen[-1] <= 160:
                    break
            ck(seen and 80 < seen[-1] <= 160, "the cap grows with the density: a view needing %d tiles gets them all (80 is the cap at density 1)" % (seen[-1] if seen else -1))

            print("\n-- 3. mipmaps")
            await settle()
            m = await safe("()=>window.__a3dMapMipmapped()") or {}
            ck(m.get('textures', 0) > 0 and m.get('mipmapped') == m.get('textures'), "every tile on the GPU is mipmapped (%s)" % m)

            print("\n-- 4. Nominatim")
            await safe("()=>window.__a3dMapFindReset()")
            r = await safe("()=>window.__a3dMapFind('Big Ben')")
            ck(r and r.get('error') == 'HTTP 403' and 'refused it (HTTP 403)' in await toast() and 'set the latitude and longitude in Properties' in await toast(),
               "a refusal (HTTP 403) is said as one, with what to do instead")
            NOM['status'] = 429
            await safe("()=>window.__a3dMapFindReset()")
            await safe("()=>window.__a3dMapFind('Big Ben')")
            ck('is busy (HTTP 429): try again in a minute' in await toast(), "being busy (HTTP 429) is said as that")

            print("\n-- 5. zoom like AutoCAD and Revit (V133e)")
            ck(await safe("()=>window.__a3dZoomLimits()") == [0.5, 200000], "the view goes from 0.5 m to 200 km")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dMapSet('style','street')")
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:100})")
            box = await safe("()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top,r.width,r.height];}")
            P = [40, 0, -25]
            s0 = await safe("(p)=>window.__a3dProject(p)", P)
            await page.mouse.move(box[0] + s0['x'], box[1] + s0['y'])
            for _ in range(6):
                await page.mouse.wheel(0, 400)
                await page.wait_for_timeout(60)
            st = await safe("()=>window.__a3dState().cam")
            s1 = await safe("(p)=>window.__a3dProject(p)", P)
            ck(st and st['dist'] > 150, "the wheel zooms out past the old 150 m stop (%.0f m)" % (st and st['dist'] or 0))
            ck(s1 and abs(s1['x'] - s0['x']) < 1.5 and abs(s1['y'] - s0['y']) < 1.5,
               "about the cursor: the point under it stays under it (%.1f, %.1f -> %.1f, %.1f)" % (s0['x'], s0['y'], s1['x'], s1['y']))
            for _ in range(10):
                await page.mouse.wheel(0, 5000)
                await page.wait_for_timeout(40)
            ck((await safe("()=>window.__a3dState().cam"))['dist'] == 200000, "and stops at 200 km")
            for _ in range(20):
                await page.mouse.wheel(0, -5000)
                await page.wait_for_timeout(40)
            ck((await safe("()=>window.__a3dState().cam"))['dist'] == 0.5, "zooming in stops at 0.5 m")
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:50000})")
            await settle()
            d = await safe("()=>window.__a3dMapDrawn()") or {}
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
            c = img.getpixel((int((box[0] + box[2] * 0.3) * 2), int((box[1] + box[3] * 0.3) * 2)))
            ck(d.get('drawn', 0) > 0 and all(abs(c[i] - (200, 120, 60)[i]) <= 12 for i in range(3)),
               "50 km out the map is still drawn: the far plane follows the view (%s, %s tiles)" % (c, d.get('drawn')))
            await safe("()=>window.__a3dSetView('home')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dCamSet({dist:30000,pitch:0.6})")
            await settle()
            img = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
            c = img.getpixel((int((box[0] + box[2] * 0.5) * 2), int((box[1] + box[3] * 0.6) * 2)))
            ck(all(abs(c[i] - (200, 120, 60)[i]) <= 12 for i in range(3)), "and in 3D, 30 km out (%s)" % (c,))
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
