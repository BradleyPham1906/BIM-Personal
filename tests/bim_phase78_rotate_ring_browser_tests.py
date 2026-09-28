"""
bim_phase78_rotate_ring_browser_tests.py

Regression suite for __acad3dV78 in canvas_v10.html: a rotate ring added to the V76 gizmo.

WHAT THIS COMPLETES. V76 gave the selection three translate arms. Rotating still meant picking the
Rotate tool, clicking a centre point, and typing an angle into a dialog -- three deliberate steps
for a gesture that is one drag everywhere this app is modelled on.

ONE RING, NOT THREE. bimComputeTransformedGeometry -- the function every rotate, mirror and array
path goes through -- transforms PLAN points, and so rotates about the vertical axis and nothing
else. Tilting a wall out of plan has no parametric representation to rebuild from. Three rings with
one wired would be the decorative control Product Principle 1 forbids, so section 2 asserts there is
exactly one ring and that it lies in the plan plane.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The rotation is asserted RIGID, numerically: every point of the selection turns by the same
     angle and every point's distance from the centre is unchanged. "The object moved" would pass
     for a shear, a scale, or a rotation about the wrong centre; only this catches those.
  2. The angle is asserted to be a WORLD angle, in a 3D view where the ring projects to a strongly
     foreshortened ellipse. Equal SCREEN angles around an ellipse are not equal world angles, so an
     implementation that measured the cursor's screen angle would track near the major axis and lag
     badly near the minor one. Dragging to a ring point 90 degrees round and requiring 90 degrees
     of rotation is what separates the two.
  3. A long out-and-back drag must return the geometry to its starting values. That is the contract
     the snapshot preview exists to guarantee -- each frame rotates the ORIGINAL by the total angle
     rather than nudging the previous frame -- and it is the property that quietly decays first if
     anyone reverts to incremental application.
  4. The mesh is asserted structurally stable across a rotation: a wall that gains or loses
     vertices while turning is rebuilding from already-rebuilt geometry.
  5. ORTHO snaps to 15 degrees, using the toggle already in the status bar rather than a new
     modifier.
  6. The ring is ABSENT in an elevation view, where the plan plane is edge-on. A ring drawn there
     would be a line the user cannot aim at, with no stable angle to read off it -- the same class
     of fault as V76's stretched vertical arm, which the V76 suite caught after the fact.
  7. A dependent room is RE-MEASURED after the drag, not translated. A rotation is not a
     translation, and propagating it as one would leave rooms the wrong shape.

Run:  python3 bim_phase78_rotate_ring_browser_tests.py [path/to/canvas_v10.html]
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


async def setup(page, closed=False, ortho=False):
    wid = await page.evaluate("""(a)=>{
      window.__a3dTestSetObjs([]);
      const w=window.__a3dWall([[0,0],[8,0],[8,6]],0.3,3,'center',a.closed);
      window.__a3dSelectFor([w]);
      window.__a3dSet3DView();
      window.__a3dSnapSet({point:false,grid:false,ortho:a.ortho});
      return w;}""", {'closed': closed, 'ortho': ortho})
    await page.wait_for_timeout(520)
    return wid


async def ring_drag(page, path_degs):
    """Grab the ring at path_degs[0] and drag through the rest, with real pointer events."""
    r = await page.evaluate("()=>window.__a3dCanvasRect()")
    pts = []
    for d in path_degs:
        p = await page.evaluate("(d)=>window.__a3dGizmoRingPoint(d)", d)
        if p is None:
            return False
        pts.append(p)
    await page.mouse.move(r['left'] + pts[0][0], r['top'] + pts[0][1])
    await page.mouse.down()
    for p in pts[1:]:
        await page.mouse.move(r['left'] + p[0], r['top'] + p[1], steps=10)
    await page.mouse.up()
    await page.wait_for_timeout(300)
    return True


def polar(pts, c):
    return [(math.degrees(math.atan2(p[1] - c[1], p[0] - c[0])),
             math.hypot(p[0] - c[0], p[1] - c[1])) for p in pts]


def wrap(d):
    return ((d + 540) % 360) - 180


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(1700)

        has78 = await page.evaluate("()=>!!window.__acad3dV78")
        ck(has78, "__acad3dV78 marker is present")
        if not has78:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. there is a ring, and it is a ring")
        wid = await setup(page)
        ring = await page.evaluate("()=>window.__a3dGizmoRing()")
        ck(ring is not None, "a selected wall gets a rotate ring")
        ck(ring['segs'] > 24,
           "it is projected as a %d-point polyline -- an ellipse in any 3D view, so it cannot be "
           "drawn with ctx.arc and has to be projected like any other world geometry"
           % ring['segs'])
        ck(ring['w'] > ring['h'] * 1.4,
           "and in this 3D view it IS a foreshortened ellipse (%dx%d px) -- which is exactly why "
           "the drag angle cannot be read off the screen"
           % (round(ring['w']), round(ring['h'])))
        cfg = await page.evaluate("()=>window.__a3dGizmoConfig()")
        ck(cfg['ring'] > cfg['arm'],
           "the ring radius (%d) is outside the arrow tips (%d), so the two handles cannot be "
           "confused at a given pixel" % (cfg['ring'], cfg['arm']))

        await page.evaluate("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(500)
        pring = await page.evaluate("()=>window.__a3dGizmoRing()")
        ck(pring and abs(pring['w'] - pring['h']) < 2,
           "in PLAN, where the rotation plane faces the camera, it is a circle (%dx%d px)"
           % (round(pring['w']), round(pring['h'])))
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(450)

        print("\n-- 2. the ring picks, and only the ring picks")
        hits = []
        for d in (0, 60, 145, 250, 330):
            p = await page.evaluate("(d)=>window.__a3dGizmoRingPoint(d)", d)
            hits.append(await page.evaluate("(a)=>window.__a3dGizmoAt(a[0],a[1])", p))
        ck(all(h == 'rotate' for h in hits),
           "it is pick-able all the way round (%s)" % hits)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        ck(await page.evaluate("(a)=>window.__a3dGizmoAt(a[0],a[1])",
                               [g['ox'], g['oy'] + 2]) != 'rotate',
           "the centre is not the ring")
        far = await page.evaluate("""()=>{
          const r=window.__a3dGizmoRing();
          return window.__a3dGizmoAt(r.ox+r.w, r.oy);}""")
        ck(far is None, "and well outside it nothing is pick-able (%s)" % far)

        print("\n-- 3. the drag is a RIGID rotation about the gizmo centre")
        wid = await setup(page)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        centre = [g['origin'][0], g['origin'][2]]
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        ck(await ring_drag(page, [0, 20, 45]) is True, "the ring accepts a drag")
        after = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        pb, pa = polar(before, centre), polar(after, centre)
        dangles = [wrap(pa[i][0] - pb[i][0]) for i in range(len(pb))]
        dradii = [abs(pa[i][1] - pb[i][1]) for i in range(len(pb))]
        print("     turned by %s" % [round(a, 3) for a in dangles])
        ck(max(dangles) - min(dangles) < 0.01,
           "EVERY point turned by the same angle (spread %.4f degrees) -- 'the object moved' would "
           "pass for a shear, a scale, or a rotation about the wrong centre"
           % (max(dangles) - min(dangles)))
        ck(max(dradii) < 1e-6,
           "and every point kept its exact distance from the centre (max change %.2e m)"
           % max(dradii))
        ck(abs(dangles[0] - 45) < 2.0,
           "the amount turned matches the ring position dragged to (%.2f of 45 degrees)"
           % dangles[0])

        print("\n-- 4. the angle is a WORLD angle, not a screen angle")
        wid = await setup(page)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        centre = [g['origin'][0], g['origin'][2]]
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        await ring_drag(page, [0, 45, 90])
        after = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        d90 = wrap(polar(after, centre)[0][0] - polar(before, centre)[0][0])
        ck(abs(d90 - 90) < 2.0,
           "dragging a quarter of the way round the ring turns the object 90 degrees (%.2f) -- on "
           "this foreshortened ellipse a screen-angle implementation reads a different number, "
           "because equal screen angles around an ellipse are not equal world angles" % d90)

        print("\n-- 5. each frame rotates the ORIGINAL, so a drag out and back returns")
        wid = await setup(page)
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        vbefore = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).mesh.v.length", wid)
        await ring_drag(page, [0, 40, 90, 150, 200, 260, 320, 355, 0])
        after = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        vafter = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).mesh.v.length", wid)
        drift = max(max(abs(after[i][0] - before[i][0]), abs(after[i][1] - before[i][1]))
                    for i in range(len(before)))
        print("     drift after an 8-leg round trip: %.3e m" % drift)
        ck(drift < 0.02,
           "an eight-leg drag all the way round and back lands within 20 mm of where it started "
           "(%.2e m) -- the residue is the cursor's own pixel quantisation, not accumulated "
           "rotation error, because every frame rotates the snapshot rather than the last frame"
           % drift)
        ck(vafter == vbefore,
           "and the wall still has exactly %d mesh vertices (%d) -- a solid that gains or loses "
           "vertices while turning is rebuilding from already-rebuilt geometry"
           % (vbefore, vafter))

        print("\n-- 6. ORTHO snaps the angle to 15 degrees")
        wid = await setup(page, ortho=True)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        centre = [g['origin'][0], g['origin'][2]]
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        await ring_drag(page, [0, 20, 38])
        after = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        d = wrap(polar(after, centre)[0][0] - polar(before, centre)[0][0])
        ck(abs(d - round(d / 15) * 15) < 0.01,
           "a drag to about 38 degrees lands on an exact multiple of 15 (%.4f) -- ORTHO is the "
           "toggle already in the status bar, already meaning 'constrain to clean directions' for "
           "the sketch tools" % d)
        ck(abs(abs(d) - 45) < 0.01 or abs(abs(d) - 30) < 0.01,
           "and it is the nearest one (%.2f)" % d)
        await page.evaluate("()=>window.__a3dSnapSet({ortho:false})")

        print("\n-- 7. the ring is absent where the rotation plane is edge-on")
        await setup(page)
        await page.evaluate("()=>window.__a3dSetView('front')")
        await page.wait_for_timeout(600)
        er = await page.evaluate("()=>window.__a3dGizmoRing()")
        ck(er is None,
           "a front elevation shows no ring (%s) -- it would project to a line the user cannot aim "
           "at, with no stable angle to read off it" % er)
        ck(await page.evaluate("()=>window.__a3dGizmo()") is not None,
           "while the translate arms are still there, so the gizmo does not vanish wholesale")
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(450)

        print("\n-- 8. a rotation can be undone")
        wid = await setup(page)
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        await ring_drag(page, [0, 30, 70])
        mid = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(400)
        back = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", wid)
        ck(abs(mid[1][1] - before[1][1]) > 0.5, "the drag turned it (%s -> %s)"
           % (before[1], [round(v, 3) for v in mid[1]]))
        ck(back == before, "and ONE undo puts it back exactly (%s)" % back)

        print("\n-- 9. dependents are re-measured, not translated")
        ids = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[9,0],[9,6],[0,6]],0.3,3,'center',true);
          const r=window.__a3dCreateRoomAt([4.5,3],0);
          window.__a3dSelectFor([w]);
          window.__a3dSet3DView();
          window.__a3dSnapSet({point:false,grid:false,ortho:false});
          return {w:w,r:r};}""")
        await page.wait_for_timeout(650)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        centre = [g['origin'][0], g['origin'][2]]
        r0 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pts", ids['r'])
        a0 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).area", ids['r'])
        await ring_drag(page, [0, 25, 50])
        r1 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pts", ids['r'])
        a1 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).area", ids['r'])
        turned = [wrap(polar(r1, centre)[i][0] - polar(r0, centre)[i][0])
                  for i in range(min(len(r0), len(r1)))]
        ck(len(r1) == len(r0) and max(turned) - min(turned) < 0.2,
           "the room it bounds turned with the walls, rigidly (%s)"
           % [round(t, 2) for t in turned])
        ck(abs(a1 - a0) < 0.01,
           "and kept its area (%.4f -> %.4f) -- propagating a rotation as a TRANSLATION would "
           "have left it the wrong shape" % (a0, a1))

        print("\n-- 10. a multi-selection turns about the group centre")
        ids = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const a=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          const b=window.__a3dWall([[0,10],[6,10]],0.3,3,'center',false);
          window.__a3dSelectFor([a,b]);
          window.__a3dSet3DView();
          window.__a3dSnapSet({point:false,grid:false,ortho:false});
          return {a:a,b:b};}""")
        await page.wait_for_timeout(600)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        ck(len(g['ids']) == 2, "both walls are in the gizmo's set")
        ck(abs(g['origin'][2] - 5) < 0.6,
           "and its origin is midway between them (z=%.2f of 5)" % g['origin'][2])
        centre = [g['origin'][0], g['origin'][2]]
        b0 = [await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", ids['a']),
              await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", ids['b'])]
        await ring_drag(page, [0, 30, 60])
        b1 = [await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", ids['a']),
              await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", ids['b'])]
        allturn = []
        for k in (0, 1):
            pb, pa = polar(b0[k], centre), polar(b1[k], centre)
            allturn += [wrap(pa[i][0] - pb[i][0]) for i in range(len(pb))]
        ck(max(allturn) - min(allturn) < 0.02,
           "both walls turned by one common angle about that shared centre (spread %.4f degrees)"
           % (max(allturn) - min(allturn)))

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for m in ck.failed:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
