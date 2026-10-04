#!/usr/bin/env python3
"""bim_phase154_webgpu_map_terrain_browser_tests.py -- V154: the map and terrain in WebGPU; outlines
pulled toward the eye in both engines.

Chromium with WebGPU on (SwiftShader), the engine drawing offscreen (a headless browser cannot
present a WebGPU canvas), each frame compared with WebGL's of the same view. Tiles are served in
the browser: coloured, gridded PNGs, with CORS, and from one host without it.

  1. OUTLINES: the same pull in all three shaders; perspective, a bright selected outline, far off.
  2. TERRAIN: the surface drawn with WebGPU, as WebGL draws it; selected.
  3. THE MAP: on the ground and draped on the surface; tiles with their mipmaps; in plan and in 3D;
     the textures given back with the tiles. (A server without CORS cannot be tested here: a
     response the harness serves is not checked for CORS. Such a tile fails as it loads, before
     either engine sees it.)

The harness never waits without a bound (V123).
"""
import asyncio, io, json, pathlib, re, sys, traceback
from PIL import Image, ImageDraw, ImageChops
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


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=['--enable-unsafe-webgpu'])
        page = await browser.new_page(viewport={'width': 1500, 'height': 950})
        await page.add_init_script('window.__BIM_GPU_OFFSCREEN=true')   # a headless browser cannot present a WebGPU canvas

        def png(x, y, z):
            im = Image.new('RGB', (256, 256), ((x * 53) % 256, (y * 97) % 256, (z * 31 + 80) % 256))
            d = ImageDraw.Draw(im)
            for k in range(0, 256, 32):
                d.line([(k, 0), (k, 255)], fill=(255, 255, 255))
                d.line([(0, k), (255, k)], fill=(0, 0, 0))
            b = io.BytesIO()
            im.save(b, 'PNG')
            return b.getvalue()

        async def tile(route, cors=True):
            m = re.search(r'/(\d+)/(\d+)/(\d+)\.png$', route.request.url)
            z, x, y = (int(v) for v in m.groups()) if m else (0, 0, 0)
            h = {'Content-Type': 'image/png'}
            if cors:
                h['Access-Control-Allow-Origin'] = '*'
            try:
                await route.fulfill(status=200, body=png(x, y, z), headers=h)
            except Exception:
                pass
        await page.route('https://tiles.example.org/**', tile)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2000)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def frame():
            await safe("()=>window.__a3dGlBatch(true)")
            return await safe("()=>window.__a3dGlStats()") or {}

        async def gpu():
            return await safe("()=>window.__a3dGpu()") or {}

        async def same(what, near=0):
            r = await safe("()=>window.__a3dGpuCompare()") or {}
            ok = r.get('pixels') and r.get('over48near') <= near and r['over48'] <= r['pixels'] * 0.001 and r['over16'] <= r['pixels'] * 0.005 and r.get('gpuStats', {}).get('mode') == 'webgpu'
            ck(bool(ok), "WebGPU draws what WebGL draws: %s (of %s pixels, %s differ by more than 16, %s by more than 48, %s not explained by a pixel over or a sample of an edge)"
               % (what, r.get('pixels'), r.get('over16'), r.get('over48'), r.get('over48near')))
            await frame()
            return r

        async def settle(n=8):
            for _ in range(n):
                await frame()
                await page.wait_for_timeout(200)

        try:
            has = await safe("()=>window.__acad3dV154")
            ck(bool(has) and 'gpumap' in has, "__acad3dV154 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 154, "the app says V154 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');}")
            ck(await safe("()=>window.__a3dGpuWait(8000)") == 'ready', "WebGPU is ready")

            print("\n-- 1. outlines pulled toward the eye")
            src = HTML.read_text(encoding='utf-8')
            ck(src.count("BIM_EDGE_PULL.toFixed(6)") == 2 and "w+=(uEye-w)*uPull" in src, "the same pull in the batched WebGL shader, the WebGPU shader and the object-by-object one")
            w1 = await safe("()=>window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false)")
            await safe("()=>window.__a3dColumnAt([3,3],0,0.6,0.6,3.2)")
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({pitch:0.55,yaw:0.7});window.__a3dRunCmd('zoomextents');window.__a3dSelectFor([]);}")
            await frame()
            await same('outlines on their faces, in perspective')
            await safe("(i)=>window.__a3dSelectFor([i])", w1)
            await same('a selected wall, its outline bright on dark', near=10)
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dCamSet({dist:400})")
            await same('the same from 400 m')
            await safe("()=>window.__a3dCamSet({dist:30})")
            await safe("()=>window.__a3dGraphics('webgl')")
            await frame()
            clip = {'x': 300, 'y': 80, 'width': 900, 'height': 760}
            ia = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            await safe("()=>window.__a3dGlBatch(false)")
            await page.wait_for_timeout(150)
            ib = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            await safe("()=>window.__a3dGlBatch(true)")
            mx = max(e[1] for e in ImageChops.difference(ia, ib).getextrema())
            ck((await safe("()=>window.__a3dGlStats().mode")) == 'batched' and mx <= 2, "in WebGL, batched and object by object draw the outlines the same (largest difference %d)" % mx)
            await safe("()=>window.__a3dGraphics('auto')")
            await safe("()=>window.__a3dGpuWait(8000)")
            await frame()

            print("\n-- 2. a terrain surface")
            await safe("()=>window.__a3dTestSetObjs([])")
            t1 = await safe("(m)=>window.__a3dMakeTerrain(m)", [[-30, -30, 0, '', ''], [30, -30, 1, '', ''], [30, 30, 3, '', ''], [-30, 30, 0, '', ''], [0, 0, 6, '', ''], [10, -15, 2, '', '']])
            await safe("()=>{window.__a3dColumnAt([0,0],6,0.6,0.6,3);window.__a3dFlat(false);window.__a3dCamSet({pitch:0.5,yaw:0.7});window.__a3dRunCmd('zoomextents');window.__a3dSelectFor([]);}")
            st = await frame()
            G = await gpu()
            sh = await safe("()=>window.__a3dTerrainShown3d?null:null")
            ck(G.get('engine') == 'webgpu' and st.get('siteDraws') == 1, "WebGPU draws the surface: one draw (%s)" % st.get('siteDraws'))
            await same('a terrain surface and a column on it')
            await safe("(i)=>window.__a3dSelectFor([i])", t1)
            await same('the surface selected')
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dColumnAt([1,1],0,1.2,1.2,4)")
            await frame()
            await same('a column inside the hill, hidden by it')

            print("\n-- 3. the map, and the map on the terrain")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            await safe("""()=>{var a=document.querySelector('#a3d-propsbody [data-propmodel="sunlat"]');a.value='39.95';a.dispatchEvent(new Event('change',{bubbles:true}));
              var b=document.querySelector('#a3d-propsbody [data-propmodel="sunlon"]');b.value='-75.16';b.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await safe("()=>{window.__a3dMapSet('url','https://tiles.example.org/{z}/{x}/{y}.png');window.__a3dMapSet('style','custom');}")
            await settle()
            st = await frame()
            md = await safe("()=>window.__a3dMapDrawn()") or {}
            ck(md.get('path') == 'webgpu' and md.get('drawn', 0) >= 1 and st.get('siteDraws', 0) > 1 + md['drawn'] - 1,
               "WebGPU draws the map under the surface and drapes it on it (%s tiles on the ground, %s draws)" % (md.get('drawn'), st.get('siteDraws')))
            await same('the map draped on the terrain', near=10)
            T = await safe("()=>window.__a3dGpuTiles()") or {}
            ck(T.get('textures', 0) >= 1 and all(l == 9 for l in T.get('levels', [])), "each tile a texture with its 9 mipmap levels, as WebGL's (%s)" % T.get('levels', [])[:3])
            await settle(3)
            T2 = await safe("()=>window.__a3dGpuTiles()") or {}
            ck(T2.get('live') == T2.get('textures') == T.get('textures'), "made once and kept: as many on the GPU as tiles, frame after frame (%s)" % T2.get('live'))
            await safe("()=>window.__a3dTestSetObjs([])")
            await safe("()=>{window.__a3dFlat(true);window.__a3dCamSet({pitch:1.5707});window.__a3dRunCmd('zoomextents');}")
            await settle(4)
            await same('the map in plan')
            await safe("()=>window.__a3dMapSet('opacity',55)")
            await settle(2)
            await same('the map at 55% opacity')
            await safe("()=>window.__a3dMapSet('opacity',100)")
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({pitch:0.6,yaw:0.4,dist:600});}")
            await settle(6)
            md = await safe("()=>window.__a3dMapDrawn()") or {}
            ck(md.get('path') == 'webgpu' and md.get('drawn', 0) >= 2, "in 3D, many tiles (%s)" % md.get('drawn'))
            await same('the map in 3D, tiles drawn smaller than their pixels (the mipmaps)')
            n = await safe("()=>window.__a3dMapDropAll()")
            T = await safe("()=>window.__a3dGpuTiles()")
            ck(n and T['textures'] == 0 and T['live'] == 0, "the tiles given back: their textures with them (%s live)" % T['live'])
            await settle(4)
            T = await safe("()=>window.__a3dGpuTiles()")
            ck(T['textures'] >= 1, "and made again as they come back (%s)" % T['textures'])
            await safe("()=>window.__a3dMapSet('style','off')")
            await frame()
            ck((await gpu()).get('engine') == 'webgpu', "WebGPU throughout: the map and the terrain no longer hand a frame to WebGL")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()

    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        print("RESULT: FAIL")
        for m in CK.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
