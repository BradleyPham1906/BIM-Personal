#!/usr/bin/env python3
"""bim_phase153_webgpu_engine_browser_tests.py -- V153: the WebGPU engine, WebGL kept.

Chromium is started with WebGPU on (SwiftShader). A headless browser cannot present a WebGPU
canvas, so the engine draws into a texture of the canvas's size, read back and compared with
WebGL's frame of the same view.

  1. THE SAME PICTURE: WebGPU against WebGL -- plain, a selection, a transparent layer, a lens, a
     layer off, a move.
  2. RECORDED ONCE: the camera replays the bundle; a move or a selection is one row; a new shape
     or a change of passes records it again.
  3. SCALE: 5,000 and 20,000 elements in a few draws, replayed.
  4. WEBGL STILL DRAWS: a terrain surface in 3D, the map.
  5. GRAPHICS chooses WebGL and back, kept, in Statistics; a lost device hands over to WebGL.
  6. A BROWSER WITHOUT WEBGPU: WebGL, batched.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback
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

        async def gpu():
            return await safe("()=>window.__a3dGpu()") or {}

        async def same(what):
            r = await safe("()=>window.__a3dGpuCompare()") or {}
            # an outline lying on its own face is a depth tie each engine breaks its own way: at most 0.02%
            ok = r.get('pixels') and r.get('over48near') <= r['pixels'] * 0.0002 and r['over48'] <= r['pixels'] * 0.001 and r['over16'] <= r['pixels'] * 0.005 and r.get('gpuStats', {}).get('mode') == 'webgpu'
            ck(bool(ok), "WebGPU draws what WebGL draws: %s (of %s pixels, %s differ by more than 16 of 255, %s by more than 48, %s of them not explained by a line a pixel over)"
               % (what, r.get('pixels'), r.get('over16'), r.get('over48'), r.get('over48near')))
            await frame()

        try:
            has = await safe("()=>window.__acad3dV153")
            ck(bool(has) and 'webgpu' in has, "__acad3dV153 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 153, "the app says V153 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');}")
            st = await safe("()=>window.__a3dGpuWait(8000)")
            await frame()
            G = await gpu()
            ck(st == 'ready' and G.get('engine') == 'webgpu' and G.get('label') == 'WebGPU', "where the browser has WebGPU, it draws (%s)" % G)

            print("\n-- 1. the same picture")
            c1 = await safe("()=>window.__a3dColumnAt([0,0],0,0.6,0.6,3)")
            w1 = await safe("()=>window.__a3dWall([[2,0],[9,0]],0.3,3,'center',false)")
            c2 = await safe("()=>window.__a3dColumnAt([4,4],0,0.6,0.6,4)")
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({pitch:0.55,yaw:0.7});window.__a3dRunCmd('zoomextents');window.__a3dSelectFor([]);}")
            st = await frame()
            ck(st.get('mode') == 'webgpu' and st.get('draws') == 2 and st.get('chunks') == 1, "three elements: one chunk, two draws, from V152's description (%s)" % st)
            await same('three elements')
            await safe("(i)=>window.__a3dSelectFor([i])", w1)
            await same('a selected wall')
            ly = await safe("()=>window.__a3dLayerNew({name:'Glass'})")
            await safe("(l)=>window.__a3dLayerCurrent(l)", ly)
            g = await safe("()=>window.__a3dColumnAt([1,3],0,1.2,1.2,3.5)")
            await safe("()=>window.__a3dLayerCurrent(window.__a3dLayers()[0].id)")
            await safe("(l)=>window.__a3dLayerSet(l,'transparency',60)", ly)
            await safe("()=>window.__a3dSelectFor([])")
            await same('a column on a layer 60% transparent')
            await safe("()=>window.__a3dLens('type')")
            await same('coloured by type')
            await safe("()=>window.__a3dLens('none')")
            await safe("(l)=>window.__a3dLayerSet(l,'visible',false)", ly)
            await same('the Glass layer off')
            ck(await safe("()=>window.__a3dGlFaces()") == 22, "and the Glass column is not drawn")
            await safe("(l)=>window.__a3dLayerSet(l,'visible',true)", ly)
            await safe("(i)=>window.__a3dMoveObjects([i],2,0,0)", c1)
            await same('a column moved')
            await safe("()=>window.__a3dFlat(true)")
            await same('flat, looking straight down')
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({pitch:0.55,yaw:0.7});}")

            print("\n-- 2. recorded once, replayed")
            await frame()
            b0 = await safe("()=>window.__a3dRenderBench(4)")
            ck(b0 and b0['engine'] == 'webgpu' and not b0['stats'].get('recorded') and b0['stats']['uploads'] == 0,
               "the camera turning: the draws replayed, not recorded again, nothing sent but the camera (%s)" % (b0 and b0['stats']))
            async def tot():
                return await safe("()=>window.__a3dGlTotals()") or {}

            async def did(action, *arg):
                a = await tot()
                await safe(action, *arg)
                await frame()
                z = await tot()
                return {k: z[k] - a.get(k, 0) for k in z}
            d = await did("(i)=>window.__a3dMoveObjects([i],0,0,1)", c2)
            ck(d['recorded'] == 0 and d['uploads'] >= 1 and d['uploadBytes'] == 32 * d['uploads'], "a move: one row of the table, 32 bytes, the draws replayed (%s)" % d)
            d = await did("(i)=>window.__a3dSelectFor([i])", c2)
            ck(d['recorded'] == 0 and d['uploadBytes'] == 32 * d['uploads'] and d['uploads'] >= 1, "a selection: the same (%s)" % d)
            await safe("()=>window.__a3dSelectFor([])")
            await frame()
            d = await did("(i)=>window.__a3dRebuildColumn(i,0.6,0.6,5)", c2)
            ck(d['recorded'] >= 1 and d['rebuilt'] >= 1, "a new shape: its chunk rebuilt and the draws recorded again (%s)" % d)
            d = await did("(l)=>window.__a3dLayerSet(l,'transparency',0)", ly)
            st = await safe("()=>window.__a3dGlStats()")
            ck(d['recorded'] >= 1 and st.get('draws') == 2, "no transparent layer left: recorded again without the blended passes (%s draws)" % st.get('draws'))
            d = await did("(l)=>window.__a3dLayerSet(l,'transparency',60)", ly)
            st = await safe("()=>window.__a3dGlStats()")
            ck(d['recorded'] >= 1 and st.get('draws') == 4, "and with them again (%s draws)" % st.get('draws'))
            await same('after the changes')

            print("\n-- 3. scale")
            for n in (5000, 20000):
                await safe("(n)=>window.__a3dStressModel(n)", n)
                await safe("()=>window.__a3dRunCmd('zoomextents')")
                await safe("()=>window.__a3dRenderBench(2)")
                on = await safe("()=>window.__a3dRenderBench(6)")
                print('      %d elements with WebGPU: %.1f ms a frame, %d draws' % (n, on['avg'], on['stats']['draws']))
                ck(on['engine'] == 'webgpu' and on['stats']['draws'] <= 8 and not on['stats'].get('recorded') and on['stats']['uploads'] == 0,
                   "%d elements: %d draws, replayed, nothing sent" % (n, on['stats']['draws']))
            await same('20,000 elements')
            await safe("()=>window.__a3dTestSetObjs([])")
            await frame()

            print("\n-- 4. where WebGL still draws")
            t = await safe("(m)=>window.__a3dMakeTerrain(m)", [[-5, -5, 0, '', ''], [5, -5, 0, '', ''], [5, 5, 0, '', ''], [-5, 5, 0, '', ''], [0, 0, 2, '', '']])
            await frame()
            G = await gpu()
            ck(G.get('engine') == 'webgl' and G.get('fallback') == 'terrain' and G.get('label') == 'WebGL (for the terrain)', "a terrain surface in 3D: WebGL draws the frame (%s)" % G.get('label'))
            await safe("()=>window.__a3dTestSetObjs([])")
            await frame()
            ck((await gpu()).get('engine') == 'webgpu', "gone: WebGPU again")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            await page.wait_for_timeout(100)
            await safe("""()=>{var a=document.querySelector('#a3d-propsbody [data-propmodel="sunlat"]'),b=document.querySelector('#a3d-propsbody [data-propmodel="sunlon"]');
              a.value='39.95';a.dispatchEvent(new Event('change',{bubbles:true}));b=document.querySelector('#a3d-propsbody [data-propmodel="sunlon"]');b.value='-75.16';b.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await safe("()=>{window.__a3dMapSet('url','https://tiles.invalid/{z}/{x}/{y}.png');window.__a3dMapSet('style','custom');}")
            await frame()
            G = await gpu()
            ck(G.get('engine') == 'webgl' and G.get('fallback') == 'map', "the map on: WebGL draws the frame (%s)" % G.get('label'))
            await safe("()=>window.__a3dMapSet('style','off')")
            await frame()
            ck((await gpu()).get('engine') == 'webgpu', "the map off: WebGPU again")

            print("\n-- 5. the choice, Statistics, a lost device")
            await safe("()=>window.__a3dColumnAt([0,0],0,0.6,0.6,3)")
            await frame()
            f0 = await safe("()=>window.__a3dGlFaces()")
            await safe("()=>window.__a3dRunCmd('graphics')")
            await frame()
            G = await gpu()
            ck(G.get('pref') == 'webgl' and G.get('engine') == 'webgl' and (await safe("()=>window.__a3dGlStats().mode")) == 'batched', "GRAPHICS: WebGL chosen, WebGL draws (%s)" % G.get('label'))
            ck(await safe("()=>localStorage.getItem('acad3dGraphics')") == 'webgl', "kept in this browser")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            lab = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-graphics]');return e&&e.textContent;}")
            ck(lab == 'WebGL (chosen)', "Statistics says so (%s)" % lab)
            await safe("()=>window.__a3dRunCmd('graphics')")
            await frame()
            await safe("()=>window.__a3dRefreshProps()")
            lab = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-graphics]');return e&&e.textContent;}")
            ck((await gpu()).get('engine') == 'webgpu' and lab == 'WebGPU', "GRAPHICS again: WebGPU where there is one (%s)" % lab)
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'webgpu') or [])]
            ck('GRAPHICS' in nm[:2], "searching 'webgpu' finds GRAPHICS (%s)" % nm)
            await safe("()=>window.__a3dGpuBreakNext()")
            await frame()
            G = await gpu()
            ck(G.get('engine') == 'webgl' and 'a frame failed' in G.get('why', '') and (await safe("()=>window.__a3dGlStats().mode")) == 'batched' and not errs,
               "a WebGPU frame that fails: WebGL draws that frame and after it, no error reaches the page (%s)" % G.get('why'))
            await safe("()=>window.__a3dGraphics('auto')")
            st2 = await safe("()=>{window.__a3dGpuRestart();return window.__a3dGpuWait(8000);}")
            await frame()
            ck(st2 == 'ready' and (await gpu()).get('engine') == 'webgpu', "started again, WebGPU draws (%s)" % st2)
            ck(await safe("()=>window.__a3dGpuLose()"), "the device lost, as a driver reset would")
            await page.wait_for_timeout(500)
            await frame()
            G = await gpu()
            ck(G.get('state') == 'failed' and 'lost' in G.get('why', '') and G.get('engine') == 'webgl' and (await safe("()=>window.__a3dGlStats().mode")) == 'batched',
               "WebGL takes over, nothing lost from the model (%s)" % G.get('why'))
            ck(f0 and await safe("()=>window.__a3dGlFaces()") == f0, "and the column is still drawn (%s faces)" % f0)
            ck(not errs, "no page errors (%s)" % errs[:3])

            print("\n-- 6. a browser without WebGPU")
            b2 = await pw.chromium.launch()
            p2 = await b2.new_page(viewport={'width': 1200, 'height': 800})
            await within(p2.goto('file://' + str(HTML)), 'goto 2')
            await p2.wait_for_timeout(1500)
            await within(p2.evaluate("()=>{window.__a3dEnter();window.__a3dRunCmd('3d');window.__a3dColumnAt([0,0],0,0.6,0.6,3);}"), 'enter 2')
            s2 = await within(p2.evaluate("()=>window.__a3dGpuWait(8000)"), 'wait 2')
            await within(p2.evaluate("()=>window.__a3dGlBatch(true)"), 'paint 2')
            G2 = await within(p2.evaluate("()=>window.__a3dGpu()"), 'gpu 2')
            ck(s2 in ('none', 'failed') and G2['engine'] == 'webgl' and (await within(p2.evaluate("()=>window.__a3dGlStats().mode"), 's2')) == 'batched',
               "without WebGPU: WebGL, batched, as before (%s: %s)" % (s2, G2.get('why')))
            await b2.close()
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
