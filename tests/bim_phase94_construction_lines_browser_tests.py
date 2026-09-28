"""
bim_phase94_construction_lines_browser_tests.py

Regression suite for __acad3dV94 in canvas_v10.html: XLINE and RAY.

WHAT THIS PHASE CLAIMS: a construction line is stored as a root and a direction and clipped for
every consumer; a RAY differs from an XLINE only in one end of the parameter range; the
construction modes offered are the ones the keys implement; a construction line can be snapped
to where it CROSSES things and picked where it is drawn; and it never sets the extent it is
drawn across.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE VERTICAL CASE IS ASSERTED SEPARATELY. A clipper written from a slope works for every
     direction a casual test picks and divides by zero on the one a drafter uses most.
  2. RAY AND XLINE ARE COMPARED AT THE SAME ROOT. Both are lines through the same point in the
     same direction; only where the drawn segment STARTS separates them, so that is the check.
  3. THE DRAWING EXTENT IS MEASURED BEFORE AND AFTER THE DRAWING GROWS. A hard-coded extent
     gives a construction line that looks right on a room and stops in mid-air on a bridge, and
     it passes every fixed-geometry check. The same measurement proves a construction line does
     NOT enlarge the extent itself, which would otherwise run away.
  4. THE BRACKET LIST IS COMPARED AGAINST THE KEY TABLE, and Bisect is asserted ABSENT. V86's
     lesson: a prompt offering an option nothing implements is the same bug as a dead control.
  5. THE CROSSING SNAP IS ASSERTED ON THE CROSSING POINT, and on a RAY pointing away it is
     asserted ABSENT. A build that ignores the ray's half-line still produces a crossing, in a
     place the drafter cannot see it.
  6. PICKING IS DRIVEN THROUGH pick(), at screen coordinates taken from the projection -- both
     for a construction line and for a V93 POINT, which could not be clicked at all until now.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase94_construction_lines_browser_tests.py [path/to/canvas_v10.html]
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
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


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

        has94 = await page.evaluate("()=>!!window.__acad3dV94")
        ck(has94, "__acad3dV94 marker is present")
        if not has94:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------- 1. the clipper
        print("\n-- 1. clipping a line that has no ends")
        BOX = {'minX': -10, 'maxX': 10, 'minZ': -10, 'maxZ': 10}
        v = await page.evaluate("(b)=>window.__a3dClipInfinite([3,0],[0,1],false,b)", BOX)
        ck(v and near(v[0][0], 3) and near(v[1][0], 3)
           and near(min(v[0][1], v[1][1]), -10) and near(max(v[0][1], v[1][1]), 10),
           "a VERTICAL construction line clips without ever forming a slope (%s)" % v)
        h = await page.evaluate("(b)=>window.__a3dClipInfinite([0,-4],[1,0],false,b)", BOX)
        ck(h and near(h[0][1], -4) and near(min(h[0][0], h[1][0]), -10),
           "a horizontal one likewise (%s)" % h)
        d = await page.evaluate("(b)=>window.__a3dClipInfinite([0,0],[1,1],false,b)", BOX)
        ck(d and near(min(d[0][0], d[1][0]), -10) and near(max(d[0][0], d[1][0]), 10),
           "and a diagonal spans corner to corner (%s)" % d)
        miss = await page.evaluate("(b)=>window.__a3dClipInfinite([0,40],[1,0],false,b)", BOX)
        ck(miss is None, "a line that misses clips to nothing, not a zero-length stub (%s)" % miss)
        zero = await page.evaluate("(b)=>window.__a3dClipInfinite([0,0],[0,0],false,b)", BOX)
        ck(zero is None, "a zero direction is refused")

        # RAY vs XLINE at the SAME root and direction: only the start separates them
        r = await page.evaluate("(b)=>window.__a3dClipInfinite([0,0],[1,0],true,b)", BOX)
        x = await page.evaluate("(b)=>window.__a3dClipInfinite([0,0],[1,0],false,b)", BOX)
        ck(r and near(r[0][0], 0) and near(r[1][0], 10),
           "a RAY starts AT its root, not at the box edge (%s)" % r)
        ck(x and near(min(x[0][0], x[1][0]), -10),
           "the XLINE through the same root runs both ways (%s)" % x)
        away = await page.evaluate("(b)=>window.__a3dClipInfinite([20,0],[1,0],true,b)", BOX)
        back = await page.evaluate("(b)=>window.__a3dClipInfinite([20,0],[-1,0],true,b)", BOX)
        ck(away is None, "a ray pointing away from the drawing clips to nothing")
        ck(back and near(back[0][0], 10),
           "one pointing back into it clips at the crossing, not at its root (%s)" % back)

        # ------------------------------------------------- 2. the modes are derived
        print("\n-- 2. the offered modes are the implemented ones")
        labels = await page.evaluate("()=>window.__a3dClineModeLabels()")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'XLINE')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'xline',
           "XLINE starts from the palette (%s)" % (st['sk'] and st['sk']['tool']))
        prompt = await page.evaluate("()=>window.__a3dPrompt()")
        ck(all(('[' in prompt and lbl in prompt) for lbl in labels),
           "the prompt offers exactly the table's labels: %s in %r" % (labels, prompt))
        ck('Bisect' not in prompt and 'Offset' not in prompt,
           "and does NOT advertise Bisect or Offset, which are not built (%r)" % prompt)
        for key, mode in (('H', 'hor'), ('V', 'ver'), ('A', 'ang')):
            got = await page.evaluate("(k)=>window.__a3dClineModeForKey(k)", key)
            ck(got == mode, "key %s resolves to the %s mode (%s)" % (key, mode, got))
        ck(await page.evaluate("()=>window.__a3dClineModeForKey('B')") is None,
           "and B resolves to nothing, because Bisect is not in the table")

        # ------------------------------------------------- 3. driving the tool
        print("\n-- 3. driving XLINE: two points, then a fan from the same root")
        await page.evaluate("()=>window.__a3dPlacePoint(2,2)")
        await page.wait_for_timeout(150)
        sk = await page.evaluate("()=>window.__a3dSkCline()")
        ck(sk and sk['pts'] == 1, "the first click sets a root and makes nothing yet (%s)" % sk)
        await page.evaluate("()=>window.__a3dPlacePoint(2,9)")
        await page.wait_for_timeout(300)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        cl = [o for o in objs if o.get('t') == 'cline']
        ck(len(cl) == 1, "the second click makes one construction line (%d)" % len(cl))
        ck(cl and near(abs(cl[0]['dir'][1]), 1, 1e-9) and near(cl[0]['dir'][0], 0, 1e-9),
           "running vertically through both points (%s)" % (cl[0]['dir'] if cl else None))
        ck(cl and near(cl[0]['p'][0], 2) and near(cl[0]['p'][1], 2),
           "and rooted at the FIRST point (%s)" % (cl[0]['p'] if cl else None))
        # the root is kept, which is what makes a fan possible
        await page.evaluate("()=>window.__a3dPlacePoint(9,2)")
        await page.wait_for_timeout(300)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        cl = [o for o in objs if o.get('t') == 'cline']
        ck(len(cl) == 2, "a third click fans a SECOND line from the same root (%d)" % len(cl))
        ck(len(cl) == 2 and near(cl[1]['p'][0], 2) and near(cl[1]['p'][1], 2)
           and near(abs(cl[1]['dir'][0]), 1, 1e-9),
           "rooted at the same point and running the other way (%s %s)"
           % (cl[1]['p'] if len(cl) == 2 else None, cl[1]['dir'] if len(cl) == 2 else None))

        print("\n-- 4. the modes, driven by their keys")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'XLINE')
        await page.keyboard.press('v')
        await page.wait_for_timeout(180)
        sk = await page.evaluate("()=>window.__a3dSkCline()")
        ck(sk and sk['mode'] == 'ver' and sk['readyDir'] and near(sk['readyDir'][1], 1),
           "V sets vertical mode and a direction is ready with no second point (%s)" % sk)
        ck('through point' in (await page.evaluate("()=>window.__a3dPrompt()")),
           "and the prompt switches to asking for a through point")
        await page.evaluate("()=>window.__a3dPlacePoint(5,5)")
        await page.wait_for_timeout(300)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        cl = [o for o in objs if o.get('t') == 'cline']
        ck(len(cl) == 1 and near(cl[0]['dir'][0], 0, 1e-9),
           "ONE click then makes a vertical construction line (%d)" % len(cl))

        # H, the other letter the Canvas-era gates were swallowing
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'XLINE')
        await page.keyboard.press('h')
        await page.wait_for_timeout(180)
        sk = await page.evaluate("()=>window.__a3dSkCline()")
        ck(sk and sk['mode'] == 'hor' and sk['readyDir'] and near(abs(sk['readyDir'][0]), 1),
           "H sets horizontal mode -- the second letter two gates were swallowing (%s)" % sk)

        # the gate delegates rather than duplicating: a letter the drawing does not want is
        # still swallowed, which is what stops this fix becoming a regression for Canvas
        wants_live = await page.evaluate(
            "()=>window.__a3dWantsKey({key:'v',target:document.body})")
        ck(wants_live is False,
           "once a mode is set the drawing no longer wants V, so the gate keeps swallowing it")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        wants_idle = await page.evaluate(
            "()=>window.__a3dWantsKey({key:'v',target:document.body})")
        ck(wants_idle is False, "and with no command running it wants no letters at all")
        names = await page.evaluate("()=>window.__a3dSketchKeyNames()")
        ck('clineMode' in names and 'arcOn' in names and 'close' in names,
           "the claimed-key table is one list that both the handler and the gate read (%s)"
           % names)

        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'XLINE')
        await page.keyboard.press('a')
        await page.wait_for_timeout(180)
        pr = await page.evaluate("()=>window.__a3dPrompt()")
        ck('angle' in pr.lower(), "A asks for an angle in degrees (%r)" % pr)
        await page.keyboard.type('30')
        await page.wait_for_timeout(120)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        sk = await page.evaluate("()=>window.__a3dSkCline()")
        ck(sk and sk['angle'] == 30,
           "the typed 30 is taken as an ANGLE, not a direct distance (%s)" % sk)
        await page.evaluate("()=>window.__a3dPlacePoint(0,0)")
        await page.wait_for_timeout(300)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        cl = [o for o in objs if o.get('t') == 'cline']
        ck(len(cl) == 1 and near(cl[0]['dir'][0], math.cos(math.pi / 6), 1e-9)
           and near(cl[0]['dir'][1], math.sin(math.pi / 6), 1e-9),
           "and the line runs at 30 degrees (%s)" % (cl[0]['dir'] if cl else None))

        print("\n-- 4b. RAY, driven end to end")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await palette_run(page, 'RAY')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'xline',
           "RAY starts its own command (%s)" % (st['sk'] and st['sk']['tool']))
        sk = await page.evaluate("()=>window.__a3dSkCline()")
        ck(sk and sk['ray'] is True, "and it is a ray, not an xline (%s)" % sk)
        await page.evaluate("()=>window.__a3dPlacePoint(0,0)")
        await page.wait_for_timeout(120)
        await page.evaluate("()=>window.__a3dPlacePoint(6,0)")
        await page.wait_for_timeout(300)
        objs = await page.evaluate("()=>window.__a3dState().objs")
        rays = [o for o in objs if o.get('t') == 'cline']
        ck(len(rays) == 1 and rays[0]['ray'] is True,
           "one ray created (%d, ray=%s)" % (len(rays), rays[0]['ray'] if rays else None))
        seg = await page.evaluate("(id)=>window.__a3dClineVisibleSeg(id)", rays[0]['id'])
        ck(seg and (near(seg[0][0], 0, 1e-6) or near(seg[1][0], 0, 1e-6)),
           "and the drawn piece starts at its root rather than running behind it (%s)" % seg)

        # ------------------------------------------------- 5. the extent is derived
        print("\n-- 5. the drawn extent follows the drawing")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cid = await page.evaluate("()=>window.__a3dAddCline([0,0],[0,1],false,0)")
        e_bare = await page.evaluate("()=>window.__a3dDrawingExtent2D()")
        await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[4,0],[4,4]])")
        await page.wait_for_timeout(250)
        e_small = await page.evaluate("()=>window.__a3dDrawingExtent2D()")
        await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[400,0],[400,90]])")
        await page.wait_for_timeout(250)
        e_big = await page.evaluate("()=>window.__a3dDrawingExtent2D()")
        ck(e_big['maxX'] > e_small['maxX'] + 100,
           "a bridge-sized drawing gets a far wider extent than a room-sized one (%.1f vs %.1f)"
           % (e_big['maxX'], e_small['maxX']))
        seg_big = await page.evaluate("(id)=>window.__a3dClineVisibleSeg(id)", cid)
        ck(seg_big and abs(seg_big[0][1] - seg_big[1][1]) > 400,
           "so the construction line is drawn right across it (%.1f long)"
           % (abs(seg_big[0][1] - seg_big[1][1]) if seg_big else 0))
        # and a construction line must never enlarge the extent it needs
        before_ext = await page.evaluate("()=>window.__a3dDrawingExtent2D()")
        await page.evaluate("()=>window.__a3dAddCline([9000,9000],[1,1],false,0)")
        after_ext = await page.evaluate("()=>window.__a3dDrawingExtent2D()")
        ck(near(before_ext['maxX'], after_ext['maxX'], 1e-9),
           "a construction line 9 km away does NOT enlarge the extent (%.1f -> %.1f)"
           % (before_ext['maxX'], after_ext['maxX']))

        # ------------------------------------------------- 6. crossings and snapping
        print("\n-- 6. snapping to where a construction line crosses")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("()=>window.__a3dCurvedWall([[-5,3],[5,3]],null,0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        await page.evaluate("()=>window.__a3dAddCline([0,0],[0,1],false,0)")
        await page.wait_for_timeout(200)
        cands = await page.evaluate("()=>window.__a3dSnapCandidates(0)")
        hit = [c for c in (cands or []) if near(c[0], 0, 1e-6) and near(c[1], 3, 1e-6)]
        ck(len(hit) >= 1, "the crossing with a wall is a snap candidate (%d)" % len(hit))
        root = [c for c in (cands or []) if near(c[0], 0, 1e-9) and near(c[1], 0, 1e-9)]
        ck(len(root) >= 1, "and so is the construction line's own root (%d)" % len(root))

        # a RAY pointing away from the wall must NOT produce that crossing
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("()=>window.__a3dCurvedWall([[-5,3],[5,3]],null,0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        await page.evaluate("()=>window.__a3dAddCline([0,0],[0,-1],true,0)")
        await page.wait_for_timeout(200)
        cands = await page.evaluate("()=>window.__a3dSnapCandidates(0)")
        hit = [c for c in (cands or []) if near(c[0], 0, 1e-6) and near(c[1], 3, 1e-6)]
        ck(not hit, "a RAY pointing away from the wall offers no crossing there (%s)" % hit)

        # the arc case, through the engine
        cr = await page.evaluate(
            "()=>window.__a3dClineCrossings([-9,0.5],[1,0],false,[[-2,0],[2,0]],[1,1],true)")
        ck(len(cr) == 2, "a construction line crosses a V93 two-vertex circle twice (%d)" % len(cr))
        ck(len(cr) == 2 and all(near(math.hypot(p[0], p[1]), 2, 1e-7) for p in cr),
           "both crossings exactly on the circle (%s)" % cr)
        swept = await page.evaluate(
            "()=>window.__a3dClineArcIntersect([0,-5],[0,1],false,[2,0],[-2,0],1)")
        ck(len(swept) == 1 and near(swept[0][1], 2, 1e-9),
           "and on a half circle only the SWEPT half is met (%s)" % swept)

        # ------------------------------------------------- 7. picking
        print("\n-- 7. picked where it is drawn")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        cid = await page.evaluate("()=>window.__a3dAddCline([0,0],[1,0],false,0)")
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(300)
        sp = await page.evaluate("()=>window.__a3dToScreen([3,0],0)")
        got = await page.evaluate("(p)=>window.__a3dPickAt(p[0],p[1])", sp)
        ck(got == cid, "clicking on the drawn construction line selects it (%s)" % got)
        off = await page.evaluate("()=>window.__a3dToScreen([3,40],0)")
        got_off = await page.evaluate("(p)=>window.__a3dPickAt(p[0],p[1])", off)
        ck(got_off != cid, "and clicking well off it does not (%s)" % got_off)

        # the V93 gap: a point had no segments, so bimPickSketch could never reach it
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        pid = await page.evaluate("()=>window.__a3dAddPoint(1,2,0)")
        await page.evaluate("()=>window.__a3dFit()")
        await page.wait_for_timeout(300)
        sp = await page.evaluate("()=>window.__a3dToScreen([1,2],0)")
        got = await page.evaluate("(p)=>window.__a3dPickAt(p[0],p[1])", sp)
        ck(got == pid, "a V93 POINT can now be selected by clicking it (%s)" % got)

        # ------------------------------------------------- 8. it reaches the exports
        print("\n-- 8. every consumer draws it")
        await page.evaluate("()=>window.__a3dTestSetObjs([])")
        await page.evaluate("()=>window.__a3dSketch('poly',[[0,0],[6,0],[6,6]])")
        await page.wait_for_timeout(250)
        d0 = await page.evaluate("()=>window.__a3dBuildDXF().stats.line")
        await page.evaluate("()=>window.__a3dAddCline([3,-9],[0,1],false,0)")
        await page.wait_for_timeout(200)
        d1 = await page.evaluate("()=>window.__a3dBuildDXF().stats.line")
        ck(d1 == d0 + 1,
           "the DXF gains exactly one LINE for it -- R12 has no XLINE entity (%d -> %d)" % (d0, d1))

        # ------------------------------------------------- 9. hygiene
        print("\n-- 9. hygiene")
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
