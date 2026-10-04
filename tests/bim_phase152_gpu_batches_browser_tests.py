#!/usr/bin/env python3
"""bim_phase152_gpu_batches_browser_tests.py -- V152: the 3D scene drawn in GPU-friendly batches.

  1. BATCHES: the objects' triangles and edges in merged chunks, one table of each object's
     offset, transparency, colour and selection; a handful of draw calls where there were two an
     object.
  2. THE SAME PICTURE: batched and object by object give the same pixels -- plain, a selection,
     a transparent layer, a colour lens, a hidden layer.
  3. ONLY WHAT CHANGED: the camera alone rebuilds and uploads nothing; a move or a selection is a
     row of the table; a hidden layer stays in its chunk; a new mesh rebuilds its chunk; a deleted
     object frees its slot for the next.
  4. SCALE: 5,000 and 20,000 elements in a few draw calls, chunks under their cap, a frame
     quicker than object by object.
  5. THE FALLBACK: object by object when switched off, and the batches given back.

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
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1500, 'height': 950})
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

        async def shot():
            b = await page.screenshot(clip={'x': 300, 'y': 80, 'width': 900, 'height': 760})
            return Image.open(io.BytesIO(b)).convert('RGB')

        async def same(what):
            await safe("()=>window.__a3dGlBatch(true)")
            await page.wait_for_timeout(150)
            a = await shot()
            sa = await safe("()=>[window.__a3dGlStats().mode,window.__a3dGlFaces()]")
            await safe("()=>window.__a3dGlBatch(false)")
            await page.wait_for_timeout(150)
            b = await shot()
            sb = await safe("()=>[window.__a3dGlStats().mode,window.__a3dGlFaces()]")
            await safe("()=>window.__a3dGlBatch(true)")
            d = ImageChops.difference(a, b)
            mx = max(e[1] for e in d.getextrema())
            ck(sa[0] == 'batched' and sb[0] == 'object' and sa[1] == sb[1] and mx <= 2,
               "the same picture batched and object by object: %s (largest difference %d, faces %s)" % (what, mx, [sa, sb]))
            return a

        async def tot():
            return await safe("()=>window.__a3dGlTotals()") or {}

        try:
            has = await safe("()=>window.__acad3dV152")
            ck(bool(has) and 'batches' in has, "__acad3dV152 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 152, "the app says V152 or later (%s)" % (mv and mv.group(1)))
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);window.__a3dRunCmd('3d');}")
            ck(await safe("()=>window.__a3dGlRender()"), "3D is drawn with WebGL here")
            await safe("()=>window.__a3dColumnAt([0,0],0,0.6,0.6,3)")
            await page.wait_for_timeout(300)
            ck(await safe("()=>window.__a3dGlBatch()") is True and (await safe("()=>window.__a3dGlStats()") or {}).get('mode') == 'batched',
               "batched from the start, nothing switched")
            await safe("()=>window.__a3dTestSetObjs([])")

            print("\n-- 1. batches")
            c1 = await safe("()=>window.__a3dColumnAt([0,0],0,0.6,0.6,3)")
            w1 = await safe("()=>window.__a3dWall([[2,0],[9,0]],0.3,3,'center',false)")
            c2 = await safe("()=>window.__a3dColumnAt([4,4],0,0.6,0.6,4)")
            await safe("()=>{window.__a3dRunCmd('zoomextents');window.__a3dSelectFor([]);}")
            st = await frame()
            info = await safe("()=>window.__a3dGlBatchInfo()") or {}
            ck(st.get('mode') == 'batched' and st.get('chunks') == 1 and (info.get('chunks') or [{}])[0].get('objects') == 3,
               "three elements, one chunk (%s)" % info)
            ck(st.get('draws') == 2, "two draw calls: the solids and the edges (%s)" % st.get('draws'))
            t1 = await safe("(i)=>window.__a3dGlTableOf(i)", c2)
            o2 = await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]", c2)
            ck(t1 and abs(t1[0] - o2['pos'][0]) < 1e-5 and abs(t1[2] - o2['pos'][2]) < 1e-5 and t1[3] == 1 and t1[7] == 0,
               "its row: offset, opaque, not selected (%s)" % t1)
            await safe("()=>window.__a3dGlBatch(false)")
            so = await safe("()=>window.__a3dGlStats()") or {}
            ck(so.get('mode') == 'object' and so.get('draws') == 6, "object by object it was six: two an element (%s)" % so.get('draws'))
            await frame()

            print("\n-- 2. the same picture")
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
            st = await frame()
            ck(st.get('draws') == 4, "a transparent layer adds a pass for solids and one for edges (%s)" % st.get('draws'))
            tg = await safe("(i)=>window.__a3dGlTableOf(i)", g)
            ck(tg and abs(tg[3] - 0.4) < 1e-3, "its row holds the transparency, 0.4 (%s)" % (tg and tg[3]))
            await safe("()=>window.__a3dLens('type')")
            await same('coloured by type')
            await safe("()=>window.__a3dLens('none')")
            await safe("(l)=>window.__a3dLayerSet(l,'visible',false)", ly)
            await same('the Glass layer off')
            ck(await safe("()=>window.__a3dGlFaces()") == 22, "and the Glass column is not drawn (%s faces)" % await safe("()=>window.__a3dGlFaces()"))

            print("\n-- 3. only what changed")
            await frame()
            a = await tot()
            await safe("()=>window.__a3dRenderBench(3)")
            b = await tot()
            ck(b['frames'] > a['frames'] and b['rebuilt'] == a['rebuilt'] and b['uploads'] == a['uploads'],
               "the camera turning: nothing rebuilt, nothing sent (%s -> %s)" % (a, b))
            tg = await safe("(i)=>window.__a3dGlTableOf(i)", g)
            ck(tg and tg[3] < 0, "a column on a layer that is off: still in its chunk, marked hidden (%s)" % (tg and tg[3]))
            await safe("(l)=>window.__a3dLayerSet(l,'visible',true)", ly)
            await frame()
            c = await tot()
            ck(c['rebuilt'] == b['rebuilt'] and c['uploads'] > b['uploads'], "turned back on: a row sent, nothing rebuilt")
            await safe("(i)=>window.__a3dMoveObjects([i],2,0,0)", c1)
            await frame()
            d = await tot()
            t1 = await safe("(i)=>window.__a3dGlTableOf(i)", c1)
            o1 = await safe("(i)=>window.__a3dState().objs.filter(function(o){return o.id===i;})[0]", c1)
            ck(d['rebuilt'] == c['rebuilt'] and d['uploads'] > c['uploads'] and abs(t1[0] - o1['pos'][0]) < 1e-5,
               "a move: its row's offset, nothing rebuilt (%s)" % t1[:3])
            ck(d['uploadBytes'] - c['uploadBytes'] <= 1024 * 16, "and only the table's rows that changed are sent (%d bytes)" % (d['uploadBytes'] - c['uploadBytes']))
            await safe("(i)=>window.__a3dSelectFor([i])", c1)
            await frame()
            e = await tot()
            t1 = await safe("(i)=>window.__a3dGlTableOf(i)", c1)
            ck(e['rebuilt'] == d['rebuilt'] and t1[7] == 1, "a selection: its row, nothing rebuilt")
            await safe("()=>window.__a3dSelectFor([])")
            await safe("(i)=>window.__a3dRebuildColumn(i,0.6,0.6,5)", c2)
            await frame()
            f = await tot()
            ck(f['rebuilt'] == e['rebuilt'] + 1, "a new shape: its chunk rebuilt, once (%d)" % (f['rebuilt'] - e['rebuilt']))
            await same('after the changes')
            s0 = await safe("()=>window.__a3dGlBatchInfo()")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRunCmd('del');}", g)
            await frame()
            s1 = await safe("()=>window.__a3dGlBatchInfo()")
            ck(s1['slots'] == s0['slots'] - 1 and s1['free'] == s0['free'] + 1 and await safe("(i)=>window.__a3dGlTableOf(i)", g) is None,
               "deleted: out of its chunk, its slot free (%s)" % s1)
            await safe("()=>window.__a3dColumnAt([7,4],0,0.6,0.6,3)")
            await frame()
            s2 = await safe("()=>window.__a3dGlBatchInfo()")
            ck(s2['slots'] == s0['slots'] and s2['free'] == s0['free'], "the next element takes the free slot (%s)" % s2)
            await same('after a delete and an add')

            print("\n-- 4. scale")
            for n in (5000, 20000):
                await safe("(n)=>window.__a3dStressModel(n)", n)
                await safe("()=>window.__a3dRunCmd('zoomextents')")
                await safe("()=>window.__a3dRenderBench(2)")
                on = await safe("()=>window.__a3dRenderBench(8)")
                info = await safe("()=>window.__a3dGlBatchInfo()")
                await safe("()=>window.__a3dGlBatch(false)")
                await safe("()=>window.__a3dRenderBench(2)")
                off = await safe("()=>window.__a3dRenderBench(8)")
                await safe("()=>window.__a3dGlBatch(true)")
                print('      %d elements: batched %.1f ms a frame, %d draws; object by object %.1f ms, %d draws' % (n, on['avg'], on['stats']['draws'], off['avg'], off['stats']['draws']))
                ck(on['stats']['draws'] <= 8 and off['stats']['draws'] >= n, "%d elements: %d draw calls, where there were %d" % (n, on['stats']['draws'], off['stats']['draws']))
                ck(all(cc['verts'] <= 196608 for cc in info['chunks']) and sum(cc['objects'] for cc in info['chunks']) == n,
                   "every element in a chunk, each chunk under its cap (%d chunks)" % len(info['chunks']))
                ck(on['avg'] < off['avg'], "a frame batched is quicker than object by object (%.1f against %.1f ms)" % (on['avg'], off['avg']))
                ck(on['stats']['rebuilt'] == 0 and on['stats']['uploads'] == 0, "turning around it, nothing rebuilt and nothing sent")
                u0 = await tot()
                await safe("()=>window.__a3dMoveObjects(['stress-7'],0,0,0.5)")
                await frame()
                u1 = await tot()
                ck(0 < u1['uploadBytes'] - u0['uploadBytes'] <= 16384 and u1['rebuilt'] == u0['rebuilt'],
                   "one element moved among %d: one row of the table sent (%d bytes), nothing rebuilt" % (n, u1['uploadBytes'] - u0['uploadBytes']))

            print("\n-- 5. the fallback")
            await safe("()=>window.__a3dTestSetObjs([])")
            await safe("()=>window.__a3dGlBatch(false)")
            so = await safe("()=>window.__a3dGlStats()")
            info = await safe("()=>window.__a3dGlBatchInfo()")
            ck(so['mode'] == 'object' and info and info['chunks'] == [] and info['slots'] == 0, "switched off: object by object, the batches given back (%s)" % info)
            await safe("()=>window.__a3dGlBatch(true)")
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
