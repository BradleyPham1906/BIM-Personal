"""
bim_phase93_drawset_browser_tests.py

Regression suite for __acad3dV93 in canvas_v10.html: CIRCLE as a real circle, POLYGON, the
POINT node, and DIVIDE / MEASURE.

WHAT THIS PHASE CLAIMS: a circle is two vertices with bulge 1 and not a 24-sided polygon; the
viewport draws the CURVE and not the chord; POLYGON's two forms differ in the documented way;
POINT is a real entity that persists, snaps and is refused by the operations it cannot carry;
and DIVIDE and MEASURE step along ARC LENGTH.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE CIRCLE IS ASSERTED ON STORAGE AND ON EXACT AREA. A 24-gon still looks like a circle
     and still closes; only the vertex count and the exact pi*r^2 tell them apart.
  2. THE VIEWPORT RENDER IS MEASURED, not looked at. Two scenes with IDENTICAL bounding boxes
     -- a circle and a diagonal line -- are painted and the canvas lineTo calls counted. A
     renderer that draws o.pts raw gives the same count for both; one that flattens gives many
     more for the circle. This is the bug that made the phase: drawSketchPath was handed o.pts
     unflattened, so every committed arc since V88 drew as its chord.
  3. POLYGON IS CHECKED ON BOTH FORMS AT ONE RADIUS. Inscribed and circumscribed agree about
     vertex count, closure and centre; they disagree about where the circle touches, so the
     vertex distance and the edge-midpoint distance are what separate them.
  4. DIVIDE ON AN ARC IS ASSERTED AT THE SWEEP MIDPOINT, not the chord midpoint. They are
     0.414 m apart on a 2 m quarter circle. Measuring along chords passes every count check
     and fails this one.
  5. MEASURE'S LEFTOVER IS ASSERTED. A build that quietly stretched the spacing to fit would
     place the same number of points in the same kind of place.
  6. THE REFUSALS ARE DRIVEN, not assumed: Pad and Offset on a point, a spacing longer than the
     object, a fractional side count.
  7. THE COMMANDS ARE DRIVEN THROUGH THE PALETTE, including a TYPED circle radius -- which did
     nothing before this phase because CIRCLE was missing from the coordinate-tool gate.
  8. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase93_drawset_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

Q = math.tan(math.pi / 8)          # quarter-circle bulge


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


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def dlg_ok(page, values=None):
    if values:
        for sel, val in values.items():
            await page.fill('.a3d-dlg [data-a3dp="%s"]' % sel, str(val))
            await page.wait_for_timeout(80)
    await page.click('.a3d-dlg [data-a3dlg="ok"]')
    await page.wait_for_timeout(500)


async def dlg_select(page, sel, val):
    await page.select_option('.a3d-dlg [data-a3dp="%s"]' % sel, val)
    await page.wait_for_timeout(80)


async def count_lineTo(page):
    """Paint once with the canvas instrumented and report how many lineTo calls it took."""
    return await page.evaluate("""()=>{
      const P=CanvasRenderingContext2D.prototype;
      const real=P.lineTo;
      let n=0;
      P.lineTo=function(){n++;return real.apply(this,arguments);};
      try{ window.__a3dFit(); }finally{ P.lineTo=real; }
      return n;
    }""")


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

        has93 = await page.evaluate("()=>!!window.__acad3dV93")
        ck(has93, "__acad3dV93 marker is present")
        if not has93:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------- 1. a circle is a circle
        print("\n-- 1. CIRCLE stores a circle, driven from the palette with a TYPED radius")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'CIRCLE')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'circle',
           "CIRCLE starts from the palette (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(3,4)")
        await page.wait_for_timeout(150)
        # the typed radius: this is the path that did nothing before this phase
        await page.keyboard.type('5,4')
        await page.wait_for_timeout(120)
        typing = await page.evaluate("()=>window.__a3dTyping()")
        ck(typing['active'] and typing['buf'] == '5,4',
           "the typing buffer OPENS for CIRCLE -- it did not before V93 (%s)" % typing)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(420)

        objs = await page.evaluate("()=>window.__a3dState().objs")
        circles = [o for o in objs if o.get('t') == 'sketch' and o.get('kind') != 'point']
        ck(len(circles) == 1, "one sketch was created by the typed radius (%d)" % len(circles))
        cir = circles[0] if circles else None
        ck(cir and len(cir['pts']) == 2,
           "TWO vertices, not twenty-four (%s)" % (len(cir['pts']) if cir else None))
        ck(cir and cir.get('bulges') == [1, 1],
           "both bulges are exactly 1 (%s)" % (cir.get('bulges') if cir else None))
        ck(cir and cir.get('closed') is not False, "and it is closed")
        if cir:
            L = await page.evaluate("(o)=>window.__a3dBulgedLength(o.pts,o.bulges,true)", cir)
            A = await page.evaluate("(o)=>window.__a3dBulgedArea(o.pts,o.bulges,true)", cir)
            ck(near(L, 2 * math.pi * 2, 1e-9),
               "circumference is exactly 2*pi*r (%.9f)" % L)
            ck(near(A, math.pi * 4, 1e-9), "area is exactly pi*r^2 (%.9f)" % A)
            outline = await page.evaluate("(id)=>window.__a3dSketchOutline(id)", cir['id'])
            ck(outline and len(outline) >= 8,
               "the OUTLINE every consumer reads is the flattened curve (%d points)"
               % (len(outline) if outline else 0))

        # a 2-vertex circle must still extrude: bimSketchOutline is what makes that possible
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", cir['id'])
        pad = await page.evaluate("()=>window.__a3dPad(2)")
        ck(bool(pad), "Pad extrudes the two-vertex circle (%s)" % pad)

        # ------------------------------------------------- 2. the viewport draws the curve
        print("\n-- 2. the VIEWPORT draws the curve, measured by painting it")
        # Two scenes with the SAME bounding box, so fitScene gives the same camera and the
        # grid contributes the same number of lineTo calls to both counts.
        await page.evaluate("""(q)=>{window.__a3dTestSetObjs([{
          id:'cktest-c',t:'sketch',name:'C',col:'#5ec4b8',pos:[0,0,0],
          pts:[[-2,0],[2,0]],bulges:[1,1],y:0}]);}""", Q)
        n_curve = await count_lineTo(page)
        await page.evaluate("""()=>{window.__a3dTestSetObjs([{
          id:'cktest-l',t:'sketch',name:'L',col:'#5ec4b8',pos:[0,0,0],
          pts:[[-2,-2],[2,2]],y:0,closed:false}]);}""")
        n_line = await count_lineTo(page)
        ck(n_curve - n_line >= 8,
           "a circle costs many more strokes than a same-box line: %d vs %d"
           % (n_curve, n_line))

        # ------------------------------------------------- 3. POLYGON
        print("\n-- 3. POLYGON, both forms, driven through the palette")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'POLYGON')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "POLYGON opens its dialog")
        await dlg_ok(page, {'n': 6})
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'polygon',
           "and then takes points (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(0,0)")
        await page.wait_for_timeout(120)
        await page.evaluate("()=>window.__a3dPlacePoint(3,0)")
        await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hexes = [o for o in objs if o.get('t') == 'sketch']
        ck(len(hexes) == 1 and len(hexes[0]['pts']) == 6,
           "an inscribed hexagon of six vertices (%s)"
           % (len(hexes[0]['pts']) if hexes else None))
        if hexes:
            rs = [math.hypot(p[0], p[1]) for p in hexes[0]['pts']]
            ck(all(near(r, 3, 1e-9) for r in rs),
               "every VERTEX sits on the circle of radius 3 (%.9f..%.9f)" % (min(rs), max(rs)))
            A = await page.evaluate("(o)=>window.__a3dBulgedArea(o.pts,null,true)", hexes[0])
            ck(near(A, 6 * (math.sqrt(3) / 4) * 9, 1e-7),
               "and its area is the textbook 6*(sqrt3/4)*r^2 (%.9f)" % A)

        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'POLYGON')
        await dlg_select(page, 'f', 'c')
        await dlg_ok(page, {'n': 6})
        await page.evaluate("()=>window.__a3dPlacePoint(0,0)")
        await page.wait_for_timeout(120)
        await page.evaluate("()=>window.__a3dPlacePoint(3,0)")
        await page.wait_for_timeout(400)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        hexc = [o for o in objs if o.get('t') == 'sketch']
        if hexc:
            pts = hexc[0]['pts']
            mids = [math.hypot((pts[i][0] + pts[(i + 1) % 6][0]) / 2,
                               (pts[i][1] + pts[(i + 1) % 6][1]) / 2) for i in range(6)]
            vtx = [math.hypot(p[0], p[1]) for p in pts]
            ck(all(near(m, 3, 1e-9) for m in mids),
               "circumscribed: every EDGE MIDPOINT sits on the circle instead (%.9f)" % mids[0])
            ck(vtx[0] > 3 + 1e-6,
               "so its vertices lie OUTSIDE it -- the larger polygon (%.6f > 3)" % vtx[0])
        bad = await page.evaluate("()=>window.__a3dPolygonSketch([0,0],2,1,false)")
        ck(bool(bad.get('error')), "two sides is refused (%s)" % bad.get('error'))
        bad = await page.evaluate("()=>window.__a3dPolygonSketch([0,0],5.5,1,false)")
        ck(bool(bad.get('error')), "a fractional side count is refused (%s)" % bad.get('error'))

        # ------------------------------------------------- 4. POINT
        print("\n-- 4. POINT is a real entity")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'POINT')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'point',
           "POINT starts from the palette (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(1,2)")
        await page.wait_for_timeout(200)
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'point',
           "and KEEPS placing -- the tool survives the first point")
        await page.evaluate("()=>window.__a3dPlacePoint(4,5)")
        await page.wait_for_timeout(250)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        pts_objs = [o for o in objs if o.get('kind') == 'point']
        ck(len(pts_objs) == 2, "two points placed (%d)" % len(pts_objs))
        if pts_objs:
            isp = await page.evaluate("(id)=>window.__a3dIsPoint(id)", pts_objs[0]['id'])
            ck(isp, "and the engine recognises one as a point")
            ck(pts_objs[0]['name'].startswith('Point '),
               "named as a point, not a sketch (%s)" % pts_objs[0]['name'])
            segs = await page.evaluate("(p)=>window.__a3dPointMarkerSegs(p)", pts_objs[0]['pts'][0])
            ck(len(segs) == 2 and len(segs[0]) == 2,
               "its marker is derived once for every renderer (%d segments)" % len(segs))
            # refusals, driven
            await page.evaluate("(id)=>window.__a3dSelectFor([id])", pts_objs[0]['id'])
            padp = await page.evaluate("()=>window.__a3dPad(2)")
            ck(padp is None, "Pad refuses a point (%s)" % padp)
            src = await page.evaluate("(id)=>window.__a3dDivideSource(id)", pts_objs[0]['id'])
            ck(src is None, "and a point is not something to divide along")
            off = await page.evaluate(
                "(id)=>window.__a3dOffsetObject(window.__a3dObjSnapshot(id),0.5)",
                pts_objs[0]['id'])
            ck(off and 'point' in (off.get('error') or ''),
               "Offset refuses it BY NAME, not by tripping a guard meant for something else "
               "(%s)" % (off or {}).get('error'))
            # node snap: claimed in the code, so it is driven here rather than assumed
            cand = await page.evaluate("()=>window.__a3dSnapCandidates(0)")
            hit = [c for c in (cand or [])
                   if near(c[0], 1, 1e-9) and near(c[1], 2, 1e-9)]
            ck(len(hit) == 1, "and the point IS a snap candidate on its own plane (%d)" % len(hit))

        # ------------------------------------------------- 5. DIVIDE
        print("\n-- 5. DIVIDE steps along ARC LENGTH")
        r = await page.evaluate("()=>window.__a3dDividePoints([[0,0],[10,0]],null,false,4)")
        ck(len(r['points']) == 3,
           "dividing a straight 10 into 4 places THREE points, not four (%d)" % len(r['points']))
        ck(near(r['points'][0][0], 2.5) and near(r['points'][1][0], 5)
           and near(r['points'][2][0], 7.5),
           "at 2.5, 5 and 7.5 (%s)" % [round(p[0], 4) for p in r['points']])
        bad = await page.evaluate("()=>window.__a3dDividePoints([[0,0],[10,0]],null,false,1)")
        ck(bool(bad.get('error')), "one division is refused (%s)" % bad.get('error'))
        bad = await page.evaluate("()=>window.__a3dDividePoints([[0,0],[10,0]],null,false,3.5)")
        ck(bool(bad.get('error')), "a fractional count is refused (%s)" % bad.get('error'))

        # the check that separates arc length from chord length
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cw = await page.evaluate(
            "(q)=>window.__a3dCurvedWall([[2,0],[0,2]],[q,0],0.3,3,'center',false)", Q)
        await page.wait_for_timeout(350)
        made = await page.evaluate("(id)=>window.__a3dApplyDivide(id,2)", cw)
        ck(made and len(made) == 1, "dividing a quarter circle in two places one mark (%s)"
           % (len(made) if made else None))
        if made:
            snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", made[0])
            p = snap['pts'][0]
            root2 = math.sqrt(2)
            ck(near(p[0], root2, 1e-6) and near(p[1], root2, 1e-6),
               "at the SWEEP midpoint (%.6f,%.6f), which is on the arc" % (p[0], p[1]))
            ck(not (near(p[0], 1, 1e-3) and near(p[1], 1, 1e-3)),
               "and NOT at the chord midpoint (1,1), 0.414 m away")
            ck(await page.evaluate("(id)=>window.__a3dIsPoint(id)", made[0]),
               "the mark it placed is a POINT object")

        # driven through the palette once, because a function nobody can reach is not a command
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        sid = await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[10,0],[10,10]])")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", sid)
        await palette_run(page, 'DIVIDE')
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "DIVIDE opens its dialog from the palette")
        await dlg_ok(page, {'v': 5})
        objs = await page.evaluate("()=>window.__a3dState().objs")
        ck(len([o for o in objs if o.get('kind') == 'point']) == 4,
           "and placed 4 marks for 5 segments (%d)"
           % len([o for o in objs if o.get('kind') == 'point']))

        # ------------------------------------------------- 6. MEASURE
        print("\n-- 6. MEASURE steps a spacing off and reports the remainder")
        r = await page.evaluate("()=>window.__a3dMeasurePoints([[0,0],[10,0]],null,false,3)")
        ck(len(r['points']) == 3, "spacing 3 on a length of 10 places 3 marks (%d)"
           % len(r['points']))
        ck(near(r['points'][2][0], 9), "the last at 9 (%s)" % round(r['points'][2][0], 6))
        ck(near(r['leftover'], 1, 1e-9),
           "and the 1 m remainder is REPORTED, not absorbed (%.9f)" % r['leftover'])
        bad = await page.evaluate("()=>window.__a3dMeasurePoints([[0,0],[10,0]],null,false,0)")
        ck(bool(bad.get('error')), "zero spacing is refused (%s)" % bad.get('error'))
        bad = await page.evaluate("()=>window.__a3dMeasurePoints([[0,0],[10,0]],null,false,25)")
        ck(bool(bad.get('error')),
           "a spacing longer than the object is refused (%s)" % bad.get('error'))
        # a closed unit circle every quarter-circumference: 3 marks, not 4 stacked on the start
        r = await page.evaluate(
            "()=>window.__a3dMeasurePoints([[-1,0],[1,0]],[1,1],true,Math.PI/2)")
        ck(len(r['points']) == 3,
           "round a unit circle every quarter-circumference: 3 marks, not 4 with two on the "
           "start (%d)" % len(r['points']))

        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        sid = await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[10,0],[10,10]])")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", sid)
        await palette_run(page, 'MEASURE')
        hd = await page.evaluate(
            "()=>{const d=document.querySelector('.a3d-dlghd');return d?d.textContent:null;}")
        ck(hd == 'Measure',
           "MEASURE reaches the real command, not DIST which used to own the alias (%s)" % hd)
        await dlg_ok(page, {'v': 4})
        objs = await page.evaluate("()=>window.__a3dState().objs")
        # __a3dSketch('poly') builds a CLOSED profile, so the perimeter -- not the two drawn
        # legs -- is what MEASURE walks. The expected count is derived from the perimeter the
        # engine reports rather than hand-computed here, so the two cannot disagree.
        per = await page.evaluate(
            "(id)=>{const s=window.__a3dDivideSource(id);"
            "return window.__a3dBulgedLength(s.pts,s.bulges,s.closed);}", sid)
        want = int(math.floor(per / 4 + 1e-9))
        got = len([o for o in objs if o.get('kind') == 'point'])
        ck(got == want and want >= 8,
           "every 4 m round a %.3f m closed profile places %d marks (%d)" % (per, want, got))

        # ------------------------------------------------- 7. hygiene
        print("\n-- 7. hygiene")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        bad = [k for k, v in (audit or {}).items()
               if isinstance(v, list) and v] if isinstance(audit, dict) else []
        ck(not bad, "V80 shell audit is clean (%s)" % (bad or 'clean'))
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
