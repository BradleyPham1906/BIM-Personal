"""
bim_phase97_associativity_browser_tests.py

Regression suite for __acad3dV97 in canvas_v10.html: everything built on a boundary follows it.

WHAT THIS PHASE CLAIMS: a room, floor, ceiling, roof or hatch built on a sketch or closed wall
records that source and re-derives itself whenever the source changes -- through ONE reader of
the source's boundary, into the dependent's own frame; a dependent that is moved away on its own
is detached AND TOLD; and a vertex can be ADDED to a sketch, which is the edit the user was
making when they found the gap.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE USER'S OWN SCENARIO IS DRIVEN WITH THE MOUSE. Rectangle, room, select the rectangle,
     press a midpoint grip, drag it out. The room must gain a vertex and exactly the triangle's
     area. Every engine-level check could pass while the grip was never reachable by a hand.
  2. EACH OF THE THREE BROKEN CASES IS DRIVEN ON ITS OWN -- a curved source, a source moved
     before the room was made, and a room moved TOGETHER with its source -- because each was a
     different bug and a fix to one said nothing about the others.
  3. THE DEPENDENT'S FRAME IS ASSERTED IN WORLD TERMS: a room and its source moved together
     must be DRAWN in the same place. Comparing stored points alone passes while the room is
     drawn at twice the offset.
  4. EVERY KIND OF DEPENDENT IS DRIVEN: floor, ceiling, roof, hatch, and a CHAIN (a hatch on a
     room on a sketch), since the old edge was room-only and a type-by-type fix is exactly how
     the next one gets missed.
  5. ADDING A VERTEX TO AN ARC is asserted on the bulges and on the unchanged area, so an insert
     cannot quietly straighten a curve; and on a CONSTRAINED sketch, on the constraint indices,
     so an insert cannot quietly make a constraint hold two different points.
  6. THE CUT IS ASSERTED AUDIBLE: the toast names the object and says it is no longer linked.
     Before this phase the link was nulled in silence.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase97_associativity_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


def near(a, b, tol=1e-6):
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


def sk(i, pts, bul=None, pos=None):
    o = {'id': i, 't': 'sketch', 'name': i, 'col': '#5ec4b8', 'pos': pos or [0, 0, 0],
         'pts': pts, 'y': 0}
    if bul:
        o['bulges'] = bul
    return o


RECT = [[0, 0], [4, 0], [4, 3], [0, 3]]


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def snap(page, oid):
    return await page.evaluate("(id)=>id?window.__a3dObjSnapshot(id):null", oid)


async def toast(page):
    return await page.evaluate(
        "()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        has97 = await page.evaluate("()=>!!window.__acad3dV97")
        ck(has97, "__acad3dV97 marker is present")
        if not has97:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------- 1. the user's scenario, by hand
        print("\n-- 1. the reported scenario, driven with the mouse")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('R', RECT)])
        await page.evaluate("()=>window.__a3dFlat(true)")
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(300)
        rid = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        r0 = await snap(page, rid)
        ck(r0 and near(r0['area'], 12, 1e-9) and r0.get('sourceId') == 'R',
           "a room on the 4 x 3 rectangle records it as its source (%s, %s)"
           % (r0 and r0['area'], r0 and r0.get('sourceId')))
        await page.evaluate("()=>window.__a3dSelectFor(['R'])")
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(300)
        grips = await page.evaluate("()=>window.__a3dGrips()")
        mids = [g for g in grips if g.get('mid') and g.get('objId') == 'R']
        ck(len(mids) == 4, "the selected rectangle shows a midpoint grip on each of its 4 sides (%d)"
           % len(mids))
        # the top edge runs (4,3)->(0,3), segment 2; its midpoint is (2,3)
        top = [g for g in mids if g.get('seg') == 2]
        box = await page.evaluate(
            "()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();"
            "return [r.left,r.top];}")
        dest = await page.evaluate("()=>window.__a3dToScreen([2,5],0)")
        if top:
            gx, gy = box[0] + top[0]['x'], box[1] + top[0]['y']
            await page.mouse.move(gx, gy)
            await page.mouse.down()
            await page.mouse.move(box[0] + dest[0], box[1] + dest[1], steps=8)
            await page.mouse.up()
            await page.wait_for_timeout(350)
        skr = await snap(page, 'R')
        ck(skr and len(skr['pts']) == 5,
           "pressing the grip ADDED a vertex to the rectangle (%s points)"
           % (len(skr['pts']) if skr else None))
        r1 = await snap(page, rid)
        ck(r1 and len(r1['pts']) == 5,
           "and the room followed it to five points (%s)" % (len(r1['pts']) if r1 else None))
        ck(r1 and near(r1['area'], 16, 0.05),
           "gaining the 4 x 2 triangle: 12 -> 16 m2 (%.4f)" % (r1['area'] if r1 else -1))

        # undo must take the added vertex back out -- the snapshot has to precede the insert
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(250)
        su = await snap(page, 'R')
        ru = await snap(page, rid)
        # "exactly the insert": the room made BEFORE it must survive the undo. Without a
        # snapshot at the insert, undo reaches back one step too far -- to before the room --
        # and the sketch still ends with four points, so the count alone proves nothing.
        ck(su and len(su['pts']) == 4 and ru is not None and len(ru['pts']) == 4,
           "UNDO takes back exactly the added vertex: sketch %s points, room %s"
           % (len(su['pts']) if su else None, ('%d points' % len(ru['pts'])) if ru else 'GONE'))

        print("\n-- 1b. a click is not a drag, and a stale grip is dead")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('P', RECT)])
        await page.evaluate("()=>window.__a3dSelectFor(['P'])")
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(300)
        grips = await page.evaluate("()=>window.__a3dGrips()")
        pm = [g for g in grips if g.get('mid') and g.get('objId') == 'P']
        if pm:
            await page.mouse.click(box[0] + pm[0]['x'], box[1] + pm[0]['y'])
            await page.wait_for_timeout(250)
        sp = await snap(page, 'P')
        ck(pm and sp and len(sp['pts']) == 4,
           "a plain CLICK on a midpoint grip, with no drag, adds nothing (%s points)"
           % (len(sp['pts']) if sp else None))
        # deselect WITHOUT a repaint: the grips from the last paint are still in the list
        await page.evaluate("()=>window.__a3dSelectFor([])")
        if pm:
            await page.mouse.move(box[0] + pm[0]['x'], box[1] + pm[0]['y'])
            await page.mouse.down()
            await page.mouse.move(box[0] + pm[0]['x'] + 40, box[1] + pm[0]['y'] - 40, steps=6)
            await page.mouse.up()
            await page.wait_for_timeout(250)
        # With the stale grip dead, the press lands on the sketch's own edge and a drag there
        # legitimately MOVES the sketch -- the ordinary body drag. So what is asserted is the
        # thing a live stale grip would have done: insert a vertex. The shape must come out
        # the same shape, merely translated.
        sp2 = await snap(page, 'P')
        same_shape = False
        if sp2 and sp and len(sp2['pts']) == len(sp['pts']):
            d0 = (sp2['pts'][0][0] - sp['pts'][0][0], sp2['pts'][0][1] - sp['pts'][0][1])
            same_shape = all(near(sp2['pts'][i][0] - sp['pts'][i][0], d0[0], 1e-9) and
                             near(sp2['pts'][i][1] - sp['pts'][i][1], d0[1], 1e-9)
                             for i in range(len(sp['pts'])))
        ck(sp2 and len(sp2['pts']) == 4 and same_shape,
           "and a drag on a STALE grip of a deselected sketch inserts nothing -- still 4 "
           "vertices, the same shape (%s points)" % (len(sp2['pts']) if sp2 else None))

        # ------------------------------------------------- 2. the three broken cases
        print("\n-- 2. the three cases that did not follow before")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('C', [[-2, 0], [2, 0]], [1, 1])])
        cid = await page.evaluate("()=>window.__a3dCreateRoomAt([0,0],0)")
        await page.evaluate("()=>window.__a3dDragGripTo('C',1,3,0)")
        c1 = await snap(page, cid)
        exact = math.pi * 2.5 ** 2
        ck(c1 and abs(c1['area'] - exact) / exact < 0.005,
           "a CURVED source: the circle's room follows a vertex move, %.4f against pi*2.5^2 = %.4f"
           % (c1['area'] if c1 else -1, exact))

        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)",
                            [sk('M', RECT, None, [10, 0, 0])])
        mid = await page.evaluate("()=>window.__a3dCreateRoomAt([12,1.5],0)")
        ck(mid is not None,
           "a source MOVED before the room was made can be picked where it is drawn (%s)" % mid)
        await page.evaluate("()=>window.__a3dDragGripTo('M',2,6,5)")
        m1 = await snap(page, mid)
        ck(m1 and near(m1['area'], 19, 1e-6),
           "and the room follows it (%s)" % (m1['area'] if m1 else None))

        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('G', RECT)])
        gid = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        await page.evaluate("(r)=>window.__a3dMoveObjects(['G',r],5,0,0)", gid)
        await page.evaluate("()=>window.__a3dDragGripTo('G',0,0,0)")
        g1 = await snap(page, gid)
        gs = await snap(page, 'G')
        drawn_room = [g1['pts'][0][0] + g1['pos'][0], g1['pts'][0][1] + g1['pos'][2]] if g1 else None
        drawn_src = [gs['pts'][0][0] + gs['pos'][0], gs['pts'][0][1] + gs['pos'][2]] if gs else None
        ck(g1 and gs and near(drawn_room[0], drawn_src[0]) and near(drawn_room[1], drawn_src[1]),
           "a room moved TOGETHER with its source is drawn where the source is, not twice as "
           "far: room at %s, source at %s" % (drawn_room, drawn_src))
        ck(g1 and g1.get('sourceId') == 'G', "and it kept its link, since they moved together")

        # ------------------------------------------------- 3. every kind of dependent
        print("\n-- 3. floor, ceiling, roof and hatch follow too")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('F', RECT)])
        fid = await page.evaluate("()=>window.__a3dCreateFloorAt?null:null")
        await page.evaluate("()=>window.__a3dSelectFor(['F'])")
        await palette_run(page, 'FLOOR')
        dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        if dlg:
            await page.click('.a3d-dlg [data-a3dlg="ok"]')
            await page.wait_for_timeout(400)
        else:
            await page.evaluate("()=>window.__a3dPlacePoint(2,1.5)")
            await page.wait_for_timeout(300)
            if await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
                await page.click('.a3d-dlg [data-a3dlg="ok"]')
                await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        fl = [o for o in objs if o.get('bim') and o['bim'].get('type') == 'floor']
        ck(len(fl) == 1 and fl[0].get('sourceId') == 'F',
           "a floor made on a sketch records it as its source (%s)"
           % (fl[0].get('sourceId') if fl else 'no floor'))
        if fl:
            await page.evaluate("()=>window.__a3dDragGripTo('F',2,6,5)")
            f1 = await snap(page, fl[0]['id'])
            prof = f1['bim']['profile'] if f1 else []
            ck(len(prof) == 4 and any(near(p[0], 6) and near(p[1], 5) for p in prof),
               "and its slab profile follows the moved vertex to (6,5) (%s)" % prof)

        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('K', RECT)])
        await palette_run(page, 'CEILING')
        await page.evaluate("()=>window.__a3dPlacePoint(2,1.5)")
        await page.wait_for_timeout(300)
        if await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
            await page.click('.a3d-dlg [data-a3dlg="ok"]')
            await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        ce = [o for o in objs if o.get('bim') and o['bim'].get('type') == 'ceiling']
        ck(len(ce) == 1 and ce[0].get('sourceId') == 'K',
           "a ceiling records its source (%s)" % (ce[0].get('sourceId') if ce else 'no ceiling'))
        if ce:
            await page.evaluate("()=>window.__a3dDragGripTo('K',2,6,5)")
            k1 = await snap(page, ce[0]['id'])
            prof = k1['bim']['profile'] if k1 else []
            ck(any(near(p[0], 6) and near(p[1], 5) for p in prof),
               "and follows its sketch (%s)" % prof)
        await page.keyboard.press('Escape')

        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('T', RECT)])
        await palette_run(page, 'ROOF')
        await page.evaluate("()=>window.__a3dPlacePoint(2,1.5)")
        await page.wait_for_timeout(300)
        if await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
            await page.click('.a3d-dlg [data-a3dlg="ok"]')
            await page.wait_for_timeout(450)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        rf = [o for o in objs if o.get('bim') and o['bim'].get('type') == 'roof']
        ck(len(rf) == 1 and rf[0]['bim'].get('sourceId') == 'T',
           "a roof records its source, as it always has (%s)"
           % (rf[0]['bim'].get('sourceId') if rf else 'no roof'))
        if rf:
            await page.evaluate("()=>window.__a3dDragGripTo('T',2,6,5)")
            t1 = await snap(page, rf[0]['id'])
            fp = t1['bim']['footprint'] if t1 else []
            ck(any(near(p[0], 6) and near(p[1], 5) for p in fp),
               "and NOW its footprint follows -- the source was stored and ignored before (%s)" % fp)
        await page.keyboard.press('Escape')

        print("\n-- 4. a chain: hatch on a room on a sketch")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('H', RECT)])
        hr = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        await page.evaluate("(r)=>window.__a3dSelectFor([r])", hr)
        await palette_run(page, 'HATCH')
        if await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"):
            await page.click('.a3d-dlg [data-a3dlg="ok"]')
            await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hs = [o for o in objs if o.get('t') == 'hatch']
        ck(len(hs) == 1 and hs[0].get('sourceId') == hr,
           "the hatch records the ROOM as its source (%s)" % (hs[0].get('sourceId') if hs else None))
        if hs:
            await page.evaluate("()=>window.__a3dDragGripTo('H',2,6,5)")
            ha = await page.evaluate("(id)=>window.__a3dHatchArea(id)", hs[0]['id'])
            ck(near(ha, 19, 1e-6),
               "editing the SKETCH moves the room, and the room moves the hatch: 12 -> %.4f" % ha)

        print("\n-- 5. a picked hatch has no single source, and says so")
        GRID = [sk('L%d' % i, p) for i, p in enumerate(
            [[[-5, 0], [5, 0]], [[-5, 1], [5, 1]], [[0, -5], [0, 5]], [[1, -5], [1, 5]]])]
        for g in GRID:
            g['closed'] = False
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", GRID)
        pid = await page.evaluate("()=>window.__a3dApplyHatchAt([0.5,0.5],0)")
        src = await page.evaluate("(id)=>window.__a3dSourceOf(id)", pid)
        ck(src and src['id'] is None,
           "a hatch traced from four crossing lines records no source (%s)" % src)

        # ------------------------------------------------- 6. add vertex, precisely
        print("\n-- 6. adding a vertex keeps curves and constraints intact")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)",
                            [sk('A', [[2, 0], [-2, 0]], [1, 1])])
        a0 = await page.evaluate("()=>window.__a3dBulgedArea([[2,0],[-2,0]],[1,1],true)")
        r = await page.evaluate("()=>window.__a3dInsertSketchVertex('A',0)")
        a = await snap(page, 'A')
        ck(not r.get('error') and len(a['pts']) == 3,
           "inserting at the midpoint of a semicircle gives three vertices (%s)" % len(a['pts']))
        mp = a['pts'][1]
        ck(near(mp[0], 0, 1e-9) and near(mp[1], 2, 1e-9),
           "and the new one sits at the SWEEP midpoint, on the curve, not the chord (%s)" % mp)
        q = math.tan(math.pi / 8)
        ck(near(a['bulges'][0], q, 1e-9) and near(a['bulges'][1], q, 1e-9),
           "each half is a quarter circle, bulge tan(pi/8) (%s)" % a['bulges'][:2])
        a1 = await page.evaluate("(o)=>window.__a3dBulgedArea(o.pts,o.bulges,true)", a)
        ck(near(a1, a0, 1e-9), "so the circle's area is exactly unchanged (%.9f)" % a1)

        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [dict(
            sk('Q', [[0, 0], [4, 0], [4, 3], [0, 3]]),
            constraints=[{'id': 'c1', 'type': 'horizontal', 'refs': [2, 3], 'value': None}])])
        await page.evaluate("()=>window.__a3dInsertSketchVertex('Q',0)")
        qq = await snap(page, 'Q')
        ck(qq['constraints'][0]['refs'] == [3, 4],
           "a constraint on vertices 2 and 3 now names 3 and 4, the same two points (%s)"
           % qq['constraints'][0]['refs'])
        # caught INSIDE the page: a throw here is the very thing being tested, so it has to
        # come back as a failed check rather than end the run
        bad = await page.evaluate(
            "()=>{try{return window.__a3dInsertSketchVertex('Q',99);}"
            "catch(e){return {threw:String(e)};}}")
        ck(bool(bad.get('error')) and not bad.get('threw'),
           "an insert on a segment that does not exist is REFUSED, not thrown (%s)"
           % (bad.get('error') or bad.get('threw')))

        # ------------------------------------------------- 7. the cut is audible
        print("\n-- 7. detaching a dependent says so")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [sk('D', RECT)])
        did = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        await page.evaluate("(r)=>window.__a3dMoveObjects([r],3,0,0)", did)
        d1 = await snap(page, did)
        ck(d1 and d1.get('sourceId') is None,
           "a room moved away on its own is detached from its sketch (%s)" % d1.get('sourceId'))
        t = await toast(page)
        ck('no longer linked' in t and 'D' in t,
           "and the user is TOLD, by name (%r)" % t[:90])

        # The class behind two phases of shadowed exports: a name assigned twice, the later
        # one winning without a word. Asserted over the whole file so the next one fails here.
        print("\n-- 7b. no test export is defined twice")
        dup = await page.evaluate(r'''()=>{
          const s=document.documentElement.outerHTML;
          const re=/window\.(__a3d[A-Za-z0-9_]*)=function/g;
          const seen={},dups=[];let m;
          while((m=re.exec(s))){if(seen[m[1]])dups.push(m[1]);seen[m[1]]=1;}
          return dups;}''')
        ck(not dup, "every __a3d function export is defined exactly once (%s)" % (dup or 'none'))

        # ------------------------------------------------- 8. hygiene
        print("\n-- 8. hygiene")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        badk = [k for k, v in (audit or {}).items()
                if isinstance(v, list) and v] if isinstance(audit, dict) else []
        ck(not badk, "V80 shell audit is clean (%s)" % (badk or 'clean'))
        ck(not errs, "no uncaught page errors (%s)" % (errs[:3] or 'none'))

        passed = ck.n - len(ck.failed)
        print("\n%d/%d checks passed" % (passed, ck.n))
        print("RESULT: %s" % ('PASS' if not ck.failed else 'FAIL'))
        if ck.failed:
            print("FAILURES:")
            for f in ck.failed:
                print("  - " + f)
        await browser.close()
        return 1 if ck.failed else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
