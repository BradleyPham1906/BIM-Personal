#!/usr/bin/env python3
"""bim_phase137_terrain_3d_browser_tests.py -- V137: the map on 3D terrain.

The owner's Cửu Long screenshot: the satellite map over the hills, the buildings standing on them.
A surface (V108) drawn in 3D, the basemap draped over it, and the site context's buildings stood on
the ground. Tiles, Overpass and the terrain are routed in the browser (V132's and V133's fixtures).

  1. PLAN IS AS IT WAS: no 3D surface in plan; the contours.
  2. IN 3D: the surface shaded in its colour, every triangle; hidden with its layer.
  3. DRAPED: with the map on, the tiles over the surface, each drawn; a point on the hill shows the
     tile its place is in (two tiles, not the last drawn).
  4. THE 2D RENDERER draws the surface's triangles in 3D, not in plan.
  5. BUILDINGS ON THE TERRAIN: a fetch stands each on the lowest ground under its footprint; the
     setting takes them back to the level and up again, one undo step; the panel; Properties.

The harness never waits without a bound (V123).
"""
import asyncio, io, json, math, pathlib, re, sys, traceback
from playwright.async_api import async_playwright
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bim_phase132_map_browser_tests as M132     # the tile colours
import bim_phase133_site_context_browser_tests as M133   # the Overpass fixture, the ground

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


def hill(x, z):
    return 25 * math.exp(-(x * x + z * z) / (2 * 70 * 70))


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def shaded_like(px, c, tol=0.12):
    ks = [px[i] / c[i] for i in range(3) if c[i] > 30]
    return len(ks) >= 2 and max(ks) - min(ks) <= tol and 0.25 <= sum(ks) / len(ks) <= 1.5


def tile_of(x, z, zz):
    lon, lat = M133.m2g(x, z)
    return (int(math.floor(M133.tx(lon, zz))), int(math.floor(M133.ty(lat, zz))))


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def tiles(route):
            me = re.search(r'/tile/(\d+)/(\d+)/(\d+)$', route.request.url)
            z, y, x = (int(v) for v in me.groups()) if me else (0, 0, 0)
            await route.fulfill(status=200, body=M132.png(M132.col(x, y, z)), headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://server.arcgisonline.com/**', tiles)

        async def ovp(route):
            await route.fulfill(status=200, body=json.dumps(M133.fixture(False)), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        for h in ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**'):
            await ctx.route(h, ovp)

        async def ter(route):
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

        has = await safe("()=>!!window.__acad3dV137")
        ck(bool(has), "__acad3dV137 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(150)
            return ok

        async def paint(n=1):
            for _ in range(n):
                await safe("()=>window.__a3dTestPaint()")
                await page.wait_for_timeout(250)

        async def shot():
            return Image.open(io.BytesIO(await page.screenshot())).convert('RGB')

        async def at(p):
            return await safe("(p)=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect(),q=window.__a3dProject([p[0],p[1],p[2]]);return [r.left+q.x,r.top+q.y];}", p)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. plan is as it was")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);}")
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            await safe("()=>window.__a3dSetTrueNorth(0)")
            pts = []
            for i in range(25):
                for j in range(25):
                    x, z = -150 + 300 * i / 24, -150 + 300 * j / 24
                    pts.append([x, z, round(hill(x, z), 3), '', ''])
            tid = await safe("(m)=>window.__a3dMakeTerrain(m)", pts)
            await nosel()
            ck(bool(tid), "a hill: 25 x 25 points over 300 m, 25 m high")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await paint()
            ck(await safe("()=>window.__a3dTerrain3d()") is None and await safe("()=>window.__a3dTerrainShown()") is not None,
               "in plan: no 3D surface, V108's contours")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. in 3D")
            await safe("()=>window.__a3dSetView('iso')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:420})")
            await paint()
            r = await safe("()=>window.__a3dTerrain3d()") or []
            tri = len((await safe("(i)=>window.__a3dTerrainTin(i)", tid) or {}).get('tris', []))
            ck(len(r) == 1 and r[0]['id'] == tid and r[0]['triangles'] == tri == 1152, "drawn in 3D: all %d triangles" % tri)
            ck(r and r[0]['tiles'] == [] and r[0]['drawn'] == 0, "with the map off, no tiles")
            img = await shot()
            s = await at([0, hill(0, 0), 0])
            px = img.getpixel((int(s[0]), int(s[1])))
            ck(shaded_like(px, rgb('#b08559')), "the hilltop in the surface's colour, shaded (%s)" % (px,))
            s2 = await at([0, 0, 0])
            ck(abs(s2[1] - s[1]) > 30, "standing 25 m up: its top is above model 0,0 on screen (%d px)" % abs(s2[1] - s[1]))
            ly = await safe("()=>{var l=window.__a3dAddLayer('Ground');return l&&l.id;}")
            await safe("(a)=>window.__a3dTestObjSet(a[0],'layer',a[1])", [tid, ly])
            await safe("(i)=>window.__a3dLayerSet(i,'visible',false)", ly)
            await paint()
            ck(await safe("()=>window.__a3dTerrain3d()") is None, "hidden with its layer")
            await safe("(i)=>window.__a3dLayerSet(i,'visible',true)", ly)
            await paint()

            # ---------------------------------------------------------------------------------
            print("\n-- 3. draped")
            await safe("()=>window.__a3dMapSet('style','satellite')")
            await paint(6)
            r = (await safe("()=>window.__a3dTerrain3d()") or [{}])[0]
            zz = r.get('z')
            got = {(t['x'], t['y']) for t in r.get('tiles', [])}
            need = {tile_of(x, z, zz) for x in (-150, 0, 150) for z in (-150, 0, 150)} if zz else set()
            ck(zz and need <= got and len(got) <= 36, "the tiles over the surface at zoom %s: %d, every corner's and the middle's" % (zz, len(got)))
            ck(r.get('drawn') == len(got) and all(t['up'] == 0 for t in r.get('tiles', [])), "each drawn, its own tile")
            last = (r['tiles'][-1]['x'], r['tiles'][-1]['y']) if r.get('tiles') else None
            cands = []
            for x in range(-120, 121, 30):
                for z in range(-120, 121, 30):
                    t = tile_of(x, z, zz)
                    if t != last and math.hypot(x, z) < 130:
                        cands.append((x, z, t))
            picks, seen = [], set()
            for x, z, t in cands:
                if t not in seen:
                    seen.add(t)
                    picks.append((x, z, t))
                if len(picks) == 2:
                    break
            img = await shot()
            for x, z, t in picks:
                s = await at([x, hill(x, z), z])
                want = M132.col(t[0], t[1], zz)
                px = img.getpixel((int(s[0]), int(s[1])))
                ck(shaded_like(px, want, 0.16), "(%d, %d) on the hill shows its own tile's colour %s (%s)" % (x, z, want, px))
            await safe("()=>window.__a3dMapSet('opacity',30)")
            await paint()
            s = await at([picks[0][0], hill(picks[0][0], picks[0][1]), picks[0][1]])
            px = (await shot()).getpixel((int(s[0]), int(s[1])))
            ck(not shaded_like(px, M132.col(picks[0][2][0], picks[0][2][1], zz), 0.16), "at 30%% opacity the surface shows through (%s)" % str(px))
            await safe("()=>window.__a3dMapSet('opacity',100)")
            await safe("()=>window.__a3dMapSet('style','off')")
            await paint()

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the 2D renderer")
            await safe("()=>window.__a3dSetPresentMode(true)")
            await paint()
            ck(await safe("()=>window.__a3dTerrainPolys()") == 1152, "draws its triangles in 3D")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await paint()
            ck(await safe("()=>window.__a3dTerrainPolys()") == 0, "and none in plan")
            await safe("()=>window.__a3dSetPresentMode(false)")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. buildings on the terrain")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);}")
            await nosel()
            ck(await safe("()=>window.__a3dCtxSettings().onGround") is True, "on the terrain unless turned off")
            r = await safe("()=>window.__a3dCtxFetch()")
            for _ in range(80):
                if not await safe("()=>window.__a3dCtxBusy()"):
                    break
                await page.wait_for_timeout(100)
            ob = await safe("()=>window.__a3dState().objs") or []
            mill = [o for o in ob if o.get('context') and o['context'].get('kind') == 'buildings' and o['context'].get('id') == 101]
            ter = [o for o in ob if o.get('context') and o['context'].get('kind') == 'terrain']
            ck(mill and ter, "CONTEXT brings the mill and the terrain")
            mid = mill[0]['id'] if mill else None
            want = min(M133.ground_xz(x, z) for x, z in M133.B_SQ) - 120
            y = (mill[0].get('pos') or [0, 0, 0])[1] if mill else None
            ck(y is not None and abs(y - want) < 0.03 and abs(mill[0]['context'].get('standY', 0) - y) < 1e-9,
               "the mill stands on the lowest ground under it: %.3f m (%.3f)" % (y or 0, want))
            ck(abs(want - (M133.ground_xz(35, -5) - 120)) > 0.05, "which is not the ground at its middle")
            await safe("(i)=>window.__a3dSelectFor([i])", mid)
            await safe("()=>window.__a3dRefreshProps()")
            ck('Stands at' in await props_html(), "its Properties say where it stands")
            await nosel()
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the setting's undo is its own
            ok = await set_field('[data-propctx="onGround"]', False)
            y0 = ((await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]", mid) or {}).get('pos') or [0, 9, 0])[1]
            ck(ok and y0 == 0 and 'back on the level' in await toast(), "turned off in the Site Context group: back on the level")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            y1 = ((await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]", mid) or {}).get('pos') or [0, 0, 0])[1]
            ck(abs(y1 - want) < 0.03 and await safe("()=>window.__a3dCtxSettings().onGround") is True and
               (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7, "one undo step, its own: on the ground again")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(100)
            await safe("(v)=>window.__a3dCtxSet('onGround',true)", True)
            y2 = ((await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]", mid) or {}).get('pos') or [0, 0, 0])[1]
            ck(abs(y2 - want) < 0.03 and 'stand on the terrain: ' in await toast(), "turned on: up again")
            hh = await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [ter[0]['id'] if ter else None, 35, -5])
            ck(hh is not None and abs(hh - (M133.ground_xz(35, -5) - 120)) < 0.03, "the surface's height at a point is read from its triangles")
            ck(await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [ter[0]['id'] if ter else None, 5000, 5000]) is None, "and is none outside it")
            ck(not errs, "no page errors (%s)" % errs[:2])
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the harness crashed')
        await browser.close()
    print("\n%d/%d checks passed\nRESULT: %s" % (ck.n - len(ck.bad), ck.n, 'PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
