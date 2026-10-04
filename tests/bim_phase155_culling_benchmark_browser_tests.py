#!/usr/bin/env python3
"""bim_phase155_culling_benchmark_browser_tests.py -- V155: chunks by place, what is out of view
left out, a bundle a chunk, and BENCHMARK.

Chromium with WebGPU on (SwiftShader), the engine offscreen, compared with WebGL's frame.

  1. CHUNKS BY PLACE: 64 m cells of the ground, each chunk's box inside its cell.
  2. LEFT OUT: close to a corner, along the ground (behind the eye), flat from above; the same
     picture as WebGL's, and WebGL's the same as with every chunk drawn.
  3. A CHUNK'S BOX goes where its objects go: an element moved 600 m is still drawn.
  4. A BUNDLE A CHUNK: the view sweeping the model records nothing again.
  5. BENCHMARK: both engines timed; the model, the view and the engine put back; Statistics.

The harness never waits without a bound (V123).
"""
import asyncio, io, json, pathlib, re, sys, traceback
from PIL import Image, ImageChops
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
        await page.route('https://tiles.invalid/**', lambda r: r.abort())
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

        async def same(what):
            r = await safe("()=>window.__a3dGpuCompare()") or {}
            ok = r.get('pixels') and r.get('over48near', 99) <= 10 and r['over48'] <= r['pixels'] * 0.001 and r['over16'] <= r['pixels'] * 0.005 and r.get('gpuStats', {}).get('mode') == 'webgpu'
            ck(bool(ok), "WebGPU draws what WebGL draws: %s (%s differ by more than 48, %s unexplained)" % (what, r.get('over48'), r.get('over48near')))
            await frame()

        clip = {'x': 300, 'y': 80, 'width': 900, 'height': 760}

        async def gl_same_without_culling(what):
            await safe("()=>window.__a3dGraphics('webgl')")
            await frame()
            a = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            sa = await safe("()=>window.__a3dGlStats()")
            await safe("()=>window.__a3dCull(false)")
            b = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            sb = await safe("()=>window.__a3dGlStats()")
            await safe("()=>window.__a3dCull(true)")
            await safe("()=>window.__a3dGraphics('auto')")
            await safe("()=>window.__a3dGpuWait(8000)")
            await frame()
            mx = max(e[1] for e in ImageChops.difference(a, b).getextrema())
            ck(mx <= 2 and sa['culled'] > 0 and sb['culled'] == 0 and sa['draws'] < sb['draws'],
               "%s: WebGL with the chunks out of view left out draws the same as with every chunk (%d of %d chunks left out, %d draws against %d, largest difference %d)"
               % (what, sa['culled'], sa['chunks'], sa['draws'], sb['draws'], mx))

        try:
            has = await safe("()=>window.__acad3dV155")
            ck(bool(has) and 'culling' in has, "__acad3dV155 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 155, "the app says V155 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');}")
            ck(await safe("()=>window.__a3dGpuWait(8000)") == 'ready', "WebGPU is ready")

            print("\n-- 1. chunks by place")
            await safe("()=>window.__a3dStressModel(20000)")
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({tx:106,tz:106,dist:420,pitch:0.9,yaw:0.7});}")
            st = await frame()
            C = await safe("()=>window.__a3dChunkCells()")
            ok = len(C) == 16 and sum(c['objects'] for c in C) == 20000
            for c in C:
                gx, gz = (int(v) for v in c['cell'].split(','))
                ok = ok and gx * 64 - 1 <= c['box'][0] and c['box'][3] <= (gx + 1) * 64 + 1 and gz * 64 - 1 <= c['box'][2] and c['box'][5] <= (gz + 1) * 64 + 1
            ck(ok, "20,000 elements over 212 m: 16 chunks, one a 64 m cell, each box inside its cell (%d)" % len(C))
            ck(st['culled'] == 0 and st['draws'] == 16, "all of it in view: nothing left out, a draw a chunk (%s)" % st['draws'])

            print("\n-- 2. what is out of view, left out")
            await safe("()=>window.__a3dCamSet({tx:10,tz:10,dist:25,pitch:0.4,yaw:0.7})")
            st = await frame()
            ck(st['culled'] >= 12 and st['draws'] <= 4, "close to a corner: most chunks left out (%d of 16, %d draws)" % (st['culled'], st['draws']))
            await same('close to a corner, most chunks left out')
            await gl_same_without_culling('close to a corner')
            await safe("()=>window.__a3dCamSet({tx:106,tz:106,dist:60,pitch:0.15,yaw:0.0})")
            st = await frame()
            ck(st['culled'] >= 1, "looking along the ground from the middle: the chunks behind the eye left out (%d)" % st['culled'])
            await same('from the middle, the chunks behind left out')
            await gl_same_without_culling('from the middle')
            await safe("()=>window.__a3dFlat(true)")
            await safe("()=>window.__a3dCamSet({tx:30,tz:30,dist:20,pitch:1.5707})")
            st = await frame()
            ck(st['culled'] >= 12, "flat, looking straight down at one corner: the rest left out (%d)" % st['culled'])
            await same('flat, from above')
            await safe("()=>window.__a3dFlat(false)")

            await safe("()=>window.__a3dTestSetObjs([])")
            await safe("()=>{window.__a3dColumnAt([0,0],0,0.6,0.6,3);window.__a3dColumnAt([0,9000],0,0.6,0.6,3);window.__a3dColumnAt([0,-9000],0,0.6,0.6,3);}")
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:20,pitch:0.05,yaw:0})")
            st = await frame()
            C = await safe("()=>window.__a3dChunkCells()")
            near = [c for c in C if abs(c['box'][2]) < 100]
            ck(len(C) == 3 and st['culled'] == 2 and near and not near[0]['cull'],
               "level with the ground, 9 km ahead and 9 km behind: both left out, past the far plane and behind the eye (%d of %d)" % (st['culled'], len(C)))
            await same('a column near, two 9 km away')
            await safe("()=>window.__a3dStressModel(20000)")

            print("\n-- 3. a chunk's box goes where its objects go")
            await safe("()=>window.__a3dMoveObjects(['stress-0'],600,0,0)")
            await safe("()=>window.__a3dCamSet({tx:600,tz:0,dist:15,pitch:0.5,yaw:0.7})")
            st = await frame()
            C = await safe("()=>window.__a3dChunkCells()")
            c0 = [c for c in C if c['cell'] == '0,0'][0]
            ck(c0['box'][3] >= 600 and not c0['cull'] and st['culled'] == 15, "an element moved 600 m: its chunk's box reaches it, so it is drawn there (%s)" % [round(v) for v in c0['box']])
            await same('the element far from its chunk')
            await gl_same_without_culling('the element far from its chunk')

            print("\n-- 4. a bundle a chunk, kept")
            sweep = ({'tx': 10, 'tz': 10, 'dist': 25}, {'tx': 200, 'tz': 200, 'dist': 25}, {'tx': 200, 'tz': 10, 'dist': 25}, {'tx': 106, 'tz': 106, 'dist': 420})
            for cam in sweep:
                await safe("(c)=>window.__a3dCamSet(c)", cam)
                await frame()
            a = await safe("()=>window.__a3dGlTotals()")
            for cam in sweep:
                await safe("(c)=>window.__a3dCamSet(c)", cam)
                await frame()
            b = await safe("()=>window.__a3dGlTotals()")
            ck(b['frames'] - a['frames'] >= 4 and b['recorded'] == a['recorded'] and b['rebuilt'] == a['rebuilt'],
               "the view sweeping the model again: chunks come and go, every bundle kept, nothing recorded (%d)" % (b['recorded'] - a['recorded']))

            print("\n-- 5. BENCHMARK")
            await safe("()=>window.__a3dTestSetObjs([])")
            c1 = await safe("()=>window.__a3dColumnAt([0,0],0,0.6,0.6,3)")
            await safe("()=>window.__a3dCamSet({tx:1,tz:2,dist:33,pitch:0.5,yaw:0.3})")
            await frame()
            before = await safe("()=>({ids:window.__a3dState().objs.map(function(o){return o.id;}),cam:window.__a3dCamSet({}),undo:window.__a3dUndoDepth?window.__a3dUndoDepth():null})")
            R = await within(page.evaluate("()=>window.__a3dBenchmark()"), 'benchmark')
            rows = R.get('rows') or []
            ok = len(rows) == 2 and [r['n'] for r in rows] == [5000, 20000] and all(r.get('webgpu') and r.get('webgl') for r in rows)
            ck(ok and not R.get('running') and R.get('gpu'), "5,000 and 20,000 elements timed with WebGPU and with WebGL (%s)" % ['%d: %.0f / %.0f ms' % (r['n'], r.get('webgpu') or -1, r.get('webgl') or -1) for r in rows])
            for r in rows:
                print('      this machine (software GPU): %d elements, WebGPU %.1f ms, WebGL %.1f ms a frame' % (r['n'], r['webgpu'], r['webgl']))
            after = await safe("()=>({ids:window.__a3dState().objs.map(function(o){return o.id;}),cam:window.__a3dCamSet({}),undo:window.__a3dUndoDepth?window.__a3dUndoDepth():null})")
            ck(after == before and (await safe("()=>window.__a3dGpu()"))['engine'] == 'webgpu', "the model, the view and the engine as they were (%s)" % after['ids'])
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            txt = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-bench]');return e&&e.textContent;}")
            ck(txt and '5,000: WebGPU' in txt and '20,000:' in txt and 'ms a frame' in txt, "Statistics shows the times (%s)" % txt)
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'benchmark') or [])]
            ck('BENCHMARK' in nm[:2], "searching 'benchmark' finds BENCHMARK (%s)" % nm)
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
