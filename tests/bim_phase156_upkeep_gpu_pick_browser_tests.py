#!/usr/bin/env python3
"""bim_phase156_upkeep_gpu_pick_browser_tests.py -- V156: the frame's upkeep cut down, and a click on a
large model picked by the GPU.

Chromium with WebGPU on (SwiftShader), the engine offscreen; the pick is WebGL's id pass.

  1. UPKEEP: nothing gone, no search for the gone; one gone, found and its slot freed; one back.
  2. A CLICK: from above, the top of each element as the old walk says, and sooner; empty ground
     nothing; in perspective, where the click was.
  3. LEFT TO THE OLD WALK: a locked layer over the click; a small model; WebGL drawing too.

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

        async def at(x, y, mode):
            await safe("(m)=>window.__a3dPickMode(m)", mode)
            r = await safe("(a)=>window.__a3dPickInfo(a[0],a[1])", [x, y])
            await safe("()=>window.__a3dPickMode('auto')")
            return r

        try:
            has = await safe("()=>window.__acad3dV156")
            ck(bool(has) and 'gpupick' in has, "__acad3dV156 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 156, "the app says V156 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');}")
            ck(await safe("()=>window.__a3dGpuWait(8000)") == 'ready', "WebGPU is ready (it draws; the pick is WebGL's, whose read is immediate)")

            print("\n-- 1. the frame's upkeep")
            await safe("()=>window.__a3dStressModel(20000)")
            await frame()
            st = await frame()
            ck(st.get('objects') == 20000 and not st.get('scanned'), "nothing gone: the search for the gone is not made (%s)" % st.get('scanned'))
            await safe("()=>window.__a3dTestSetObjs(window.__a3dState().objs.slice(1))")   # no paint between
            st = await frame()
            I = await safe("()=>window.__a3dGlBatchInfo()")
            ck(st.get('scanned') == 1 and I['slots'] == 19999 and I['free'] == 1, "one gone: found, its slot free (%s)" % {k: I[k] for k in ('slots', 'free')})
            st = await frame()
            ck(not st.get('scanned'), "and the next frame does not search again")
            await safe("()=>window.__a3dStressModel(20000)")
            st = await frame()
            I = await safe("()=>window.__a3dGlBatchInfo()")
            ck(I['slots'] == 20000 and I['free'] == 0, "one back: the free slot taken (%s)" % I['free'])

            print("\n-- 2. a click on a large model")
            await safe("()=>{window.__a3dFlat(true);window.__a3dCamSet({tx:20,tz:20,dist:30,pitch:1.5707,yaw:0});}")
            await frame()
            agree, n, gpu_ms, cpu_ms = 0, 0, 0.0, 0.0
            k = 142
            for i in [r * k + c for r in (10, 12, 14, 16) for c in (9, 13, 17)]:
                x, z, hgt = (i % k) * 1.5, (i // k) * 1.5, 1 + (i % 7) * 0.4
                p = await safe("(a)=>window.__a3dToScreen([a[0],a[1]],a[2])", [x, z, hgt])
                if not p or not (0 < p[0] < 900 and 0 < p[1] < 800):
                    continue
                g = await at(p[0], p[1], 'auto')
                c = await at(p[0], p[1], 'off')
                n += 1
                agree += (g['id'] == 'stress-%d' % i and c['id'] == g['id'] and g['path'] == 'gpu')
                gpu_ms += g['ms']
                cpu_ms += c['ms']
            ck(n >= 10 and agree == n, "the top of an element, clicked from above: the GPU says it, as the old walk did (%d of %d)" % (agree, n))
            ck(gpu_ms < cpu_ms, "and sooner (%.1f ms against %.1f ms a click, here, software)" % (gpu_ms / max(1, n), cpu_ms / max(1, n)))
            print('      a click on 20,000 elements: GPU %.1f ms, the walk %.1f ms' % (gpu_ms / max(1, n), cpu_ms / max(1, n)))
            far = await safe("()=>window.__a3dToScreen([-40,-40],0)")
            g = await at(far[0], far[1], 'auto')
            ck(g['path'] == 'gpu' and g['id'] is None, "on empty ground beside it: nothing (%s)" % g)
            await safe("()=>{window.__a3dFlat(false);window.__a3dCamSet({tx:20,tz:20,dist:60,pitch:0.6,yaw:0.7});}")
            await frame()
            hits = 0
            for (x, y) in ((450, 400), (300, 300), (600, 500), (200, 600), (700, 250)):
                g = await at(x, y, 'auto')
                if g['id']:
                    o = await safe("(i)=>{var o=window.__a3dState().objs.filter(function(o){return o.id===i;})[0];return o&&o.pos;}", g['id'])
                    s = await safe("(a)=>window.__a3dToScreen([a[0],a[1]],a[2])", [o[0], o[2], 0.5])
                    hits += (s is not None and abs(s[0] - x) < 60 and abs(s[1] - y) < 120)
            ck(hits >= 4, "in perspective: what it says is where the click was (%d of 5)" % hits)
            tall = await safe("()=>window.__a3dColumnAt([40,40],0,3,3,12)")   # behind the boxes, drawn after them
            same_front, tried = 0, 0
            for yaw, dy in [(y, h) for y in (0.785, 3.927) for h in (0.3, 0.6, 1.0, 1.4)]:
                await safe("(y)=>window.__a3dCamSet({tx:30,tz:30,dist:40,pitch:0.12,yaw:y})", yaw)
                await frame()
                p = await safe("(h)=>window.__a3dToScreen([40,40],h)", dy)
                g = await at(p[0], p[1], 'on')
                c = await at(p[0], p[1], 'off')
                if c['id'] and c['id'] != tall:
                    tried += 1
                    same_front += (g['id'] == c['id'])
            ck(tried >= 1 and same_front == tried, "a low view, a tall column behind lower elements: the element in front, not the column drawn after it (%d of %d)" % (same_front, tried))
            await safe("()=>window.__a3dStressModel(20000)")

            print("\n-- 3. what the GPU leaves to the old walk")
            await safe("()=>{window.__a3dFlat(true);window.__a3dCamSet({tx:20,tz:20,dist:30,pitch:1.5707,yaw:0});}")
            ly = await safe("()=>window.__a3dLayerNew({name:'Locked'})")
            await safe("(l)=>window.__a3dLayerCurrent(l)", ly)
            col = await safe("()=>window.__a3dColumnAt([15,15],0,2.5,2.5,9)")
            await safe("()=>window.__a3dLayerCurrent(window.__a3dLayers()[0].id)")
            await safe("(l)=>window.__a3dLayerSet(l,'locked',true)", ly)
            await frame()
            p = await safe("()=>window.__a3dToScreen([15,15],9)")
            g = await at(p[0], p[1], 'auto')
            ck(g['path'] == 'cpu' and g['id'] and g['id'] != col and g['id'].startswith('stress-'),
               "a column on a locked layer over the click: the old walk finds the element under it (%s by %s)" % (g['id'], g['path']))
            await safe("()=>window.__a3dStressModel(500)")
            await frame()
            p = await safe("()=>window.__a3dToScreen([18,18],1.4)")   # in view of the camera at 20, 20
            g = await at(p[0], p[1], 'auto')
            ck(g['path'] == 'cpu' and g['id'], "a small model (3,000 faces): the old walk, exactly as before (%s)" % g)
            g2 = await at(p[0], p[1], 'on')
            ck(g2['path'] == 'gpu' and g2['id'] == g['id'], "and the GPU, asked, says the same (%s)" % g2['id'])
            await safe("()=>window.__a3dGraphics('webgl')")
            await safe("()=>window.__a3dStressModel(20000)")
            await frame()
            p = await safe("()=>window.__a3dToScreen([19.5,19.5],1.4)")
            g = await at(p[0], p[1], 'auto')
            ck(g['path'] == 'gpu' and g['id'] and (await safe("()=>window.__a3dGlStats().mode")) == 'batched', "with WebGL drawing too (%s)" % g['id'])
            await safe("()=>window.__a3dGraphics('auto')")
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
