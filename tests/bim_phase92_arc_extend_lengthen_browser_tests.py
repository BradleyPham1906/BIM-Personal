"""
bim_phase92_arc_extend_lengthen_browser_tests.py

Regression suite for __acad3dV92 in canvas_v10.html: EXTEND and LENGTHEN on arcs.

WHAT THIS PHASE CLAIMS: both commands grow a free end through one shared operation; on an arc
that means the SWEEP changes while the centre and radius stay put; the two ends are not
symmetric; and the straight-only implementations are gone rather than kept alongside.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE RADIUS AND CENTRE ARE ASSERTED UNCHANGED after growing. Sliding the endpoint along the
     chord or the tangent also makes the wall longer and also moves the end - and produces a
     different arc. Length alone cannot tell those apart; the centre and radius can.
  2. BOTH ENDS ARE GROWN SEPARATELY, and the OTHER end is asserted not to move. A build that
     grows the wrong end passes a length check and fails this.
  3. EXTEND'S CANDIDATE IS RANKED BY ANGLE SWEPT FORWARD, not by distance. On a circle the
     nearest crossing in space can be behind you, so a distance ranking picks a point the arc
     would have to run backwards to reach.
  4. THE REFUSALS ARE ASSERTED: shrinking an arc away, shrinking past its other end, growing past
     a full circle, and a boundary the circle never reaches.
  5. STRAIGHT EXTEND AND LENGTHEN STILL GIVE THE OLD ANSWERS, because there is now one
     implementation and it must reduce to them.
  6. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase92_arc_extend_lengthen_browser_tests.py [path/to/canvas_v10.html]
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
    await page.wait_for_timeout(200)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(400)


async def dlg_ok(page, values=None):
    if values:
        for sel, val in values.items():
            await page.fill('.a3d-dlg [data-a3dp="%s"]' % sel, str(val))
            await page.wait_for_timeout(80)
    await page.click('.a3d-dlg [data-a3dlg="ok"]')
    await page.wait_for_timeout(450)


async def arc_of(page, pts, bulges, i=0):
    return await page.evaluate("([p,b,i])=>window.__a3dBulgeArc(p[i],p[i+1],b[i])",
                               [pts, bulges, i])


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

        has92 = await page.evaluate("()=>!!window.__acad3dV92")
        ck(has92, "__acad3dV92 marker is present")
        if not has92:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. growing an end
        print("\n-- 1. growing an arc end changes the SWEEP, not the radius")
        g = await page.evaluate("(q)=>window.__a3dGrowEnd([[2,0],[0,2]],[q,0],1,Math.PI)", Q)
        ck(not g.get('error'), "the END of a quarter circle grows (%s)" % (g.get('error') or 'ok'))
        ga = await arc_of(page, g['pts'], g['bulges']) if g.get('pts') else None
        ck(ga and near(ga['radius'], 2, 1e-9)
           and near(ga['center'][0], 0, 1e-9) and near(ga['center'][1], 0, 1e-9),
           "on the SAME circle - centre and radius unmoved -> c=%s r=%s"
           % (ga['center'] if ga else None, ga['radius'] if ga else None))
        ck(ga and near(abs(ga['sweep']), math.pi, 1e-9),
           "with the sweep grown to 180 degrees -> %s"
           % (round(ga['sweep'] * 180 / math.pi, 4) if ga else None))
        ck(g.get('pts') and near(g['pts'][1][0], -2, 1e-9) and near(g['pts'][1][1], 0, 1e-9),
           "the end landed at (-2,0) -> %s" % (g.get('pts') or [None, None])[1])
        ck(g.get('pts') and near(g['pts'][0][0], 2, 1e-9) and near(g['pts'][0][1], 0, 1e-9),
           "and THE OTHER END DID NOT MOVE -> %s" % (g.get('pts') or [None])[0])

        gs = await page.evaluate("(q)=>window.__a3dGrowEnd([[2,0],[0,2]],[q,0],0,Math.PI)", Q)
        gsa = await arc_of(page, gs['pts'], gs['bulges']) if gs.get('pts') else None
        ck(gsa and near(gsa['radius'], 2, 1e-9) and near(gsa['center'][0], 0, 1e-9),
           "growing the START stays on the same circle too -> c=%s r=%s"
           % (gsa['center'] if gsa else None, gsa['radius'] if gsa else None))
        ck(gs.get('pts') and near(gs['pts'][0][0], 0, 1e-9) and near(gs['pts'][0][1], -2, 1e-9),
           "retreating the other way, to (0,-2) - the ends are NOT symmetric -> %s"
           % (gs.get('pts') or [None])[0])
        ck(gs.get('pts') and near(gs['pts'][1][0], 0, 1e-9) and near(gs['pts'][1][1], 2, 1e-9),
           "and this time the far end is the one that stayed -> %s"
           % (gs.get('pts') or [None, None])[1])

        sh = await page.evaluate("(q)=>window.__a3dGrowEnd([[2,0],[0,2]],[q,0],1,-Math.PI/2)", Q)
        sha = await arc_of(page, sh['pts'], sh['bulges']) if sh.get('pts') else None
        ck(sha and near(sha['radius'], 2, 1e-9) and near(abs(sha['sweep']), math.pi / 4, 1e-9),
           "a negative delta shrinks the sweep to 45 degrees, radius unchanged -> %s"
           % (round(sha['sweep'] * 180 / math.pi, 4) if sha else None))

        # -Math.PI lands the sweep exactly on zero, which the "shrink away entirely" guard
        # catches; -1.5*Math.PI overshoots into a NEGATIVE sweep, which is a different guard and
        # was untested until a falsified build removed it and the suite still passed.
        for delta, why in (('-Math.PI', 'shrinking the arc away to nothing'),
                           ('-1.5*Math.PI', 'shrinking past the other end and flipping direction'),
                           ('100', 'growing past a full circle')):
            r = await page.evaluate("(q)=>window.__a3dGrowEnd([[2,0],[0,2]],[q,0],1,%s)" % delta, Q)
            ck(bool(r.get('error')), "%s is refused (%s)" % (why, r.get('error')))

        # ---------------------------------------------------------------- 2. LENGTHEN
        print("\n-- 2. LENGTHEN on a curve, driven through its dialog")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cw = await page.evaluate("(q)=>window.__a3dCurvedWall([[2,0],[0,2]],[q,0],0.3,3,'center',false)", Q)
        await page.wait_for_timeout(350)
        before = await page.evaluate("(id)=>window.__a3dWallLength(id)", cw)
        ck(near(before, math.pi, 1e-6),
           "a quarter circle of radius 2 measures pi to start with (%.6f)" % before)
        arc0 = await page.evaluate("""(id)=>{
          const b=window.__a3dObjSnapshot(id).bim;
          return window.__a3dBulgeArc(b.centerline[0],b.centerline[1],b.bulges[0]);
        }""", cw)

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", cw)
        await palette_run(page, 'LENGTHEN')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'lengthen',
           "LENGTHEN starts and does NOT refuse the curve (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(0.1,2.1)")   # near the (0,2) end
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "its dialog opens on a curved wall")
        await dlg_ok(page, {'v': math.pi})                            # delta +pi
        after = await page.evaluate("(id)=>window.__a3dWallLength(id)", cw)
        ck(near(after, 2 * math.pi, 1e-4),
           "delta +pi takes it from pi to 2pi (%.6f)" % after)
        arc1 = await page.evaluate("""(id)=>{
          const b=window.__a3dObjSnapshot(id).bim;
          return b.bulges?window.__a3dBulgeArc(b.centerline[0],b.centerline[1],b.bulges[0]):null;
        }""", cw)
        ck(arc1 and near(arc1['radius'], arc0['radius'], 1e-6)
           and near(arc1['center'][0], arc0['center'][0], 1e-6)
           and near(arc1['center'][1], arc0['center'][1], 1e-6),
           "and the arc is the SAME circle, only longer -> r %s -> %s, c %s -> %s"
           % (arc0['radius'], arc1['radius'] if arc1 else None,
              arc0['center'], arc1['center'] if arc1 else None))

        print("\n   total and percent are computed from the ARC length, not the chord")
        # Delta mode cannot see this bug: change = (L + value) - L = value whatever L is. Total
        # and percent both start from L, so a chord measurement (2.83 instead of pi) moves the
        # answer. This is what a falsified build measuring the chord slipped through.
        lt = await page.evaluate("""(q)=>{
          const r=window.__a3dLengthenBulged([[2,0],[0,2]],[q,0],false,'total',2*Math.PI,[0.1,2.1]);
          return r.error?r:{len:window.__a3dBulgedLength(r.pts,r.bulges,false)};
        }""", Q)
        ck(lt.get('len') is not None and near(lt['len'], 2 * math.pi, 1e-6),
           "total 2pi on a quarter circle gives exactly 2pi of ARC (%s)" % lt.get('len'))
        lp = await page.evaluate("""(q)=>{
          const r=window.__a3dLengthenBulged([[2,0],[0,2]],[q,0],false,'percent',200,[0.1,2.1]);
          return r.error?r:{len:window.__a3dBulgedLength(r.pts,r.bulges,false)};
        }""", Q)
        ck(lp.get('len') is not None and near(lp['len'], 2 * math.pi, 1e-6),
           "and percent 200 doubles pi to 2pi, not the chord to twice the chord (%s)"
           % lp.get('len'))

        # ---------------------------------------------------------------- 3. EXTEND
        print("\n-- 3. EXTEND on a curve, to a real boundary")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cw = await page.evaluate("(q)=>window.__a3dCurvedWall([[2,0],[0,2]],[q,0],0.3,3,'center',false)", Q)
        bound = await page.evaluate("()=>window.__a3dWall([[-5,0],[5,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(350)
        ck(bool(cw) and bool(bound), "a curved wall and a straight boundary exist")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", bound)
        await palette_run(page, 'EXTEND')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'extend',
           "EXTEND starts and does NOT refuse the curve (%s)" % (st['sk'] and st['sk']['tool']))
        await page.evaluate("()=>window.__a3dPlacePoint(0.1,2.1)")   # the (0,2) end
        await page.wait_for_timeout(450)
        snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", cw)
        cl = snap['bim']['centerline'] if snap else None
        ck(cl and near(cl[1][0], -2, 1e-6) and near(cl[1][1], 0, 1e-6),
           "the end swept forward to (-2,0), the first crossing going that way -> %s" % cl)
        ck(snap and snap['bim'].get('bulges'),
           "it is still a curve (%s)" % (snap['bim'].get('bulges') if snap else None))
        after = await page.evaluate("(id)=>window.__a3dWallLength(id)", cw)
        ck(near(after, 2 * math.pi, 1e-4),
           "now a semicircle of radius 2, measuring 2pi (%.6f)" % after)

        print("\n   the candidate is ranked by angle swept FORWARD, not by distance")
        # THE CASE HAS TO BE ASYMMETRIC OR IT MEASURES NOTHING. The first version used a
        # boundary through (2,0) and (-2,0) with the end at (0,2) - equidistant from both, so a
        # distance ranking and an angle ranking agree by accident and the check passed against a
        # build that ranked by distance.
        #
        # Here: a 20-degree arc of radius 2 ending at 20 degrees, and one boundary segment that
        # crosses its circle twice - at 120 degrees (100 forward, 3.06 away) and at 350 degrees
        # (330 forward, only 1.04 away). The right answer is the FAR one.
        r = await page.evaluate("""()=>{
          const b=Math.tan((20*Math.PI/180)/4);
          const end=[2*Math.cos(20*Math.PI/180),2*Math.sin(20*Math.PI/180)];
          return window.__a3dExtendBulged([[2,0],end],[b,0],false,
            [[-1.5939,2.1479],[2.5635,-0.7632]],null,false,[end[0],end[1]]);
        }""")
        ck(r.get('atPt') and near(r['atPt'][0], -1, 1e-3) and near(r['atPt'][1], 1.7321, 1e-3),
           "the first crossing FORWARD wins (-1,1.73) even though the other is a third the "
           "distance away -> %s" % r.get('atPt'))
        ck(near(r.get('added'), 2 * (100 * math.pi / 180), 1e-4),
           "adding 100 degrees of arc, not 330 (%s)"
           % (round(r['added'], 6) if r.get('added') else None))

        r = await page.evaluate("""(q)=>window.__a3dExtendBulged(
            [[2,0],[0,2]],[q,0],false,[[-5,0],[5,0]],null,false,[0.1,2.1])""", Q)
        ck(r.get('atPt') and near(r['atPt'][0], -2, 1e-9),
           "and the symmetric case still lands on (-2,0) -> %s" % r.get('atPt'))

        r2 = await page.evaluate("""(q)=>window.__a3dExtendBulged(
            [[2,0],[0,2]],[q,0],false,[[6,-5],[6,5]],null,false,[0.1,2.1])""", Q)
        ck(bool(r2.get('error')),
           "a boundary the circle never reaches is refused (%s)" % r2.get('error'))

        # ---------------------------------------------------------------- 4. straight unchanged
        print("\n-- 4. one implementation, and it still gives the straight answers")
        r = await page.evaluate("""()=>window.__a3dExtendBulged(
            [[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[9.5,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 15) and near(r.get('added'), 5),
           "straight EXTEND lands on (15,0) and reports 5 added -> %s" % r.get('pts'))
        r = await page.evaluate("""()=>window.__a3dExtendBulged(
            [[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[0.5,0])""")
        ck(bool(r.get('error')),
           "and picking the end facing away is still refused (%s)" % r.get('error'))
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'delta',2.5,[9.9,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 12.5),
           "straight LENGTHEN delta +2.5 -> %s" % r.get('pts'))
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'delta',2.5,[0.1,0])""")
        ck(r.get('pts') and near(r['pts'][0][0], -2.5),
           "picked at the START it moves the start -> %s" % r.get('pts'))
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[5,0],[10,0]],null,false,'delta',-7,[9.9,0])""")
        ck(bool(r.get('error')),
           "and shortening past the previous vertex is still refused (%s)" % r.get('error'))

        # ---------------------------------------------------------------- 5. hygiene
        print("\n-- 5. hygiene")
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
