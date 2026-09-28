"""
bim_phase91_arc_trim_break_browser_tests.py

Regression suite for __acad3dV91 in canvas_v10.html: arc-aware Trim and Break.

WHAT THIS PHASE CLAIMS: Trim and Break work on curved walls; both run through ONE implementation
that reduces to the straight answer when there are no bulges; the parameter along an arc is the
fraction of its SWEEP; and picking a wall measures to the curve rather than the chord.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE SWEEP PARAMETER IS ASSERTED AGAINST THE CHORD PARAMETER. The midpoint of a semicircle
     from (0,0) to (0,2) is (1,1); its chord midpoint is (0,1). Every "which side did the user
     click" decision rests on the difference, and a build using the chord looks right on anything
     close to straight.
  2. THE SWEPT-RANGE FILTER IS ASSERTED BOTH WAYS. Two arcs whose CIRCLES cross but whose swept
     parts do not must report nothing; two that really cross must report both points. Only the
     pair proves the filter does anything.
  3. WHAT SURVIVES A TRIM IS MEASURED AS AN ARC. A quarter of a unit semicircle is pi/2, not the
     chord. A build that dropped the bulge on the way out would leave a straight wall between the
     same two endpoints and pass an endpoint check.
  4. BREAK IS ASSERTED TO KEEP BOTH PIECES CURVED and to leave their cut ends exactly on the
     original circle.
  5. DEGENERATE CUTS ARE REFUSED BY LENGTH, NOT BY VERTEX COUNT. Splitting at an endpoint yields
     two identical points - a two-point wall of no length - which a count accepts. This is the
     bug the V87 suite caught the moment it was repointed at the live function.
  6. STRAIGHT TRIM AND BREAK STILL BEHAVE EXACTLY AS THEY DID, because there is now only one
     implementation and it must reduce to the old answer.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase91_arc_trim_break_browser_tests.py [path/to/canvas_v10.html]
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


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(200)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(400)


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

        has91 = await page.evaluate("()=>!!window.__acad3dV91")
        ck(has91, "__acad3dV91 marker is present")
        if not has91:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. the parameter
        print("\n-- 1. the parameter along an arc is the SWEEP fraction")
        mid = await page.evaluate("""()=>{
          const a=window.__a3dBulgeArc([0,0],[0,2],1);
          return window.__a3dArcPointAt(a,0.5);
        }""")
        ck(near(mid[0], 1, 1e-9) and near(mid[1], 1, 1e-9),
           "halfway along the semicircle (0,0)-(0,2) is (1,1) -> %s" % mid)
        ck(not (near(mid[0], 0) and near(mid[1], 1)),
           "which is NOT the chord midpoint (0,1) - the distinction the parameter exists for")
        d = await page.evaluate("()=>window.__a3dPtDistToBulgedSeg([2,1],[0,0],[0,2],1)")
        ck(near(d['dist'], 1, 1e-9) and near(d['t'], 0.5, 1e-9),
           "a point 2 right of the centre is 1 from the arc, halfway along it (%s)" % d)
        d2 = await page.evaluate("()=>window.__a3dPtDistToBulgedSeg([0,-3],[0,0],[0,2],1)")
        ck(near(d2['dist'], 3, 1e-9) and near(d2['t'], 0),
           "and a point past the start measures to the START endpoint (%s)" % d2)
        d3 = await page.evaluate("()=>window.__a3dPtDistToBulgedSeg([5,0],[0,0],[10,0],0)")
        ck(near(d3['dist'], 0) and near(d3['t'], 0.5),
           "a straight segment behaves exactly as it always did (%s)" % d3)

        # ---------------------------------------------------------------- 2. intersections
        print("\n-- 2. intersections, and the swept-range filter that makes them mean something")
        ll = await page.evaluate("()=>window.__a3dIntersectBulgedSegs([0,0],[10,0],0,[5,-5],[5,5],0)")
        ck(len(ll) == 1 and near(ll[0][0], 5) and near(ll[0][1], 0),
           "line-line crosses at (5,0) -> %s" % ll)
        la = await page.evaluate("()=>window.__a3dIntersectBulgedSegs([0,0],[0,2],1,[0,1],[3,1],0)")
        ck(len(la) == 1 and near(la[0][0], 1, 1e-9),
           "line-arc crosses the semicircle at (1,1) -> %s" % la)
        la2 = await page.evaluate("()=>window.__a3dIntersectBulgedSegs([0,0],[0,2],1,[0,1],[-3,1],0)")
        ck(len(la2) == 0, "a line running the other way misses the swept part entirely")
        aa = await page.evaluate("()=>window.__a3dIntersectBulgedSegs([0,0],[0,2],1,[1,0],[1,2],-1)")
        ck(len(aa) == 2 and near(aa[0][0], 0.5, 1e-9) and near(aa[1][0], 0.5, 1e-9),
           "arc-arc finds both crossings at x=0.5 -> %s" % aa)
        aa2 = await page.evaluate("()=>window.__a3dIntersectBulgedSegs([0,0],[0,2],1,[1,0],[1,2],1)")
        ck(len(aa2) == 0,
           "while two arcs whose CIRCLES cross but whose swept parts do not report nothing")

        # ---------------------------------------------------------------- 3. splitting
        print("\n-- 3. splitting a curve recomputes both halves")
        sp = await page.evaluate("()=>window.__a3dSplitBulgedAt([[0,0],[0,2]],[1,0],false,{seg:0,t:0.5})")
        ck(near(sp['at'][0], 1, 1e-9) and near(sp['at'][1], 1, 1e-9),
           "a semicircle splits at (1,1) -> %s" % sp['at'])
        q = math.tan(math.pi / 8)
        ck(near(sp['a']['bulges'][0], q, 1e-9) and near(sp['b']['bulges'][0], q, 1e-9),
           "into two QUARTER arcs, bulge tan(22.5deg) each, not two semicircles -> %.6f / %.6f"
           % (sp['a']['bulges'][0], sp['b']['bulges'][0]))
        lens = await page.evaluate("""(sp)=>[
          window.__a3dBulgedLength(sp.a.pts,sp.a.bulges,false),
          window.__a3dBulgedLength(sp.b.pts,sp.b.bulges,false)]""", sp)
        ck(near(sum(lens), math.pi, 1e-9),
           "and the halves measure exactly the whole, pi (%.6f)" % sum(lens))

        # ---------------------------------------------------------------- 4. TRIM on a curve
        print("\n-- 4. TRIM, driven on a real curved wall")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        curved = await page.evaluate("""()=>window.__a3dCurvedWall(
            [[0,0],[0,2]],[1,0],0.3,3,'center',false)""")
        cutter = await page.evaluate("()=>window.__a3dWall([[1,-5],[1,5]],0.3,3,'center',false)")
        await page.wait_for_timeout(350)
        ck(bool(curved) and bool(cutter), "a curved wall and a straight cutter exist")
        before_len = await page.evaluate("(id)=>window.__a3dWallLength(id)", curved)
        ck(near(before_len, math.pi, 1e-6),
           "the curved wall measures pi before trimming (%.6f)" % before_len)

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", cutter)
        await palette_run(page, 'TRIM')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'trim',
           "TRIM starts and does NOT refuse the curve (%s)" % (st['sk'] and st['sk']['tool']))
        # click near the start end, so the start side is what goes
        await page.evaluate("()=>window.__a3dPlacePoint(0.2,0.1)")
        await page.wait_for_timeout(450)
        snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", curved)
        ck(snap and snap['bim'].get('bulges'),
           "the trimmed wall is still CURVED (%s)" % (snap['bim'].get('bulges') if snap else None))
        after_len = await page.evaluate("(id)=>window.__a3dWallLength(id)", curved)
        ck(near(after_len, math.pi / 2, 1e-5),
           "and what is left measures a quarter circle, pi/2, not the chord (%.6f)" % after_len)
        cl = snap['bim']['centerline'] if snap else None
        ck(cl and near(cl[0][0], 1, 1e-6) and near(cl[0][1], 1, 1e-6),
           "cut exactly at (1,1), where the cutter crosses the arc -> %s" % cl)

        # ---------------------------------------------------------------- 5. BREAK on a curve
        print("\n-- 5. BREAK, driven on a real curved wall")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        curved = await page.evaluate("""()=>window.__a3dCurvedWall(
            [[0,0],[0,2]],[1,0],0.3,3,'center',false)""")
        await page.wait_for_timeout(300)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", curved)
        await palette_run(page, 'BREAK')
        await page.evaluate("()=>window.__a3dPlacePoint(0.3,0.4)")
        await page.wait_for_timeout(200)
        await page.evaluate("()=>window.__a3dPlacePoint(0.3,1.6)")
        await page.wait_for_timeout(450)
        walls = await page.evaluate("""()=>window.__a3dState().objs
            .filter(o=>o.bim&&o.bim.type==='wall')
            .map(o=>({id:o.id,cl:o.bim.centerline,bulges:o.bim.bulges||null}))""")
        ck(len(walls) == 2, "the curved wall became two objects (%d)" % len(walls))
        ck(all(w['bulges'] and abs(w['bulges'][0]) > 1e-9 for w in walls),
           "and BOTH pieces are still arcs, not chords (%s)"
           % [w['bulges'][0] if w['bulges'] else None for w in walls])
        on_circle = await page.evaluate("""(walls)=>walls.every(w=>
            w.cl.every(p=>Math.abs(Math.hypot(p[0]-0,p[1]-1)-1)<1e-6))""", walls)
        ck(on_circle, "every endpoint still lies exactly on the original circle")
        total = 0.0
        for w in walls:
            total += await page.evaluate("(id)=>window.__a3dWallLength(id)", w['id'])
        ck(total < math.pi - 1e-3,
           "and together they are shorter than the original, because the middle is gone "
           "(%.6f < %.6f)" % (total, math.pi))

        print("\n   breaking at a point removes nothing")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        curved = await page.evaluate("""()=>window.__a3dCurvedWall(
            [[0,0],[0,2]],[1,0],0.3,3,'center',false)""")
        await page.wait_for_timeout(300)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", curved)
        await palette_run(page, 'BREAKATPOINT')
        await page.evaluate("()=>window.__a3dPlacePoint(2,1)")
        await page.wait_for_timeout(450)
        ids = await page.evaluate("""()=>window.__a3dState().objs
            .filter(o=>o.bim&&o.bim.type==='wall').map(o=>o.id)""")
        tot = 0.0
        for i in ids:
            tot += await page.evaluate("(id)=>window.__a3dWallLength(id)", i)
        ck(len(ids) == 2 and near(tot, math.pi, 1e-5),
           "two pieces, still measuring the whole semicircle (%d pieces, %.6f)" % (len(ids), tot))

        # ---------------------------------------------------------------- 6. degenerate cuts
        print("\n-- 6. a cut at an endpoint is refused by LENGTH, not by vertex count")
        for at, why in (('[0,0]', 'start'), ('[0,2]', 'end')):
            r = await page.evaluate("()=>window.__a3dBreakBulged([[0,0],[0,2]],[1,0],false,%s,null)" % at)
            ck(bool(r.get('error')),
               "breaking a curve exactly at its %s is refused (%s)" % (why, r.get('error')))
        r = await page.evaluate("()=>window.__a3dBreakBulged([[0,0],[10,0]],null,false,[0,0],null)")
        ck(bool(r.get('error')),
           "and the same on a straight wall, where the pieces would be two identical points (%s)"
           % r.get('error'))

        # ---------------------------------------------------------------- 7. straight unchanged
        print("\n-- 7. one implementation, and it still gives the straight answer")
        r = await page.evaluate("""()=>window.__a3dTrimBulged(
            [[0,0],[10,0]],null,false,[[6,-5],[6,5]],null,false,[1,0])""")
        ck(r.get('pts') and near(r['pts'][0][0], 6) and near(r['pts'][1][0], 10),
           "straight TRIM keeps the far side, 6 to 10 -> %s" % r.get('pts'))
        ck(r.get('cutAt') and near(r['cutAt'][0], 6) and near(r['cutAt'][1], 0),
           "cutting at (6,0) -> %s" % r.get('cutAt'))
        r2 = await page.evaluate("""()=>window.__a3dBreakBulged(
            [[0,0],[10,0]],null,false,[3,0],[7,0])""")
        ck(r2.get('a') and near(r2['a']['pts'][1][0], 3) and near(r2['b']['pts'][0][0], 7),
           "straight BREAK gives 0-3 and 7-10 -> %s | %s"
           % (r2['a']['pts'] if r2.get('a') else None, r2['b']['pts'] if r2.get('b') else None))
        r3 = await page.evaluate("""()=>window.__a3dTrimBulged(
            [[0,0],[10,0]],null,false,[[20,-5],[20,5]],null,false,[1,0])""")
        ck(bool(r3.get('error')),
           "and a cutter that does not reach is still refused (%s)" % r3.get('error'))

        # ---------------------------------------------------------------- 8. hygiene
        print("\n-- 8. hygiene")
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
