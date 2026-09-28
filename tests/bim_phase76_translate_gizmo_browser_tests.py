"""
bim_phase76_translate_gizmo_browser_tests.py

Regression suite for __acad3dV76 in canvas_v10.html: a translate gizmo attached to the selection.

WHAT THE USER ASKED FOR: "when moving 3d objects, i think there should be a gizmo that attach to
the object."

A BUG THIS SUITE'S FIRST RUN FOUND, in the gizmo's own first implementation. Each arm is scaled so
all three draw at the same pixel length, and an arm too foreshortened to drag was meant to be
hidden -- but the hidden-test was applied AFTER the scaling, and scaling makes every arm exactly
74px by construction, so the test could never fail. In a plan view the vertical axis points
straight at the camera; its true projection is ~0 px per world unit; it was stretched to a full
74px arm that looked draggable and moved the object by kilometres per pixel. The test now runs on
the UNSCALED pixels-per-world-unit, compared against the best-projecting axis so the rule holds at
any zoom. Section 3 is that check, and it is why section 3 asserts plan and 3D separately.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. The gizmo's origin is compared against the object's OWN live centre after each move, not
     against a remembered pixel. This is the Phase 75 lesson applied before the fact: a handle
     that caches where the object was at selection time is precisely the bug that started this
     work, and it would be invisible until someone moved something.
  2. Each axis is dragged and the OTHER TWO components are asserted unchanged. A gizmo that moved
     the object in roughly the right direction would pass a "did it move" check and still be
     useless, because the whole point of the handle is the constraint.
  3. Distance is asserted PROPORTIONAL across two different drag lengths rather than against a
     hardcoded world figure, so the check survives a camera or projection change while still
     failing if the axis-projection maths breaks.
  4. Grid snapping is checked to quantize the DISTANCE MOVED and not the resulting position,
     starting from a deliberately off-grid object. Snapping the position instead would silently
     re-align anything placed off-grid the moment its gizmo was touched -- a data change the user
     never asked for, which no "does snapping work" check would catch.
  5. A locked object gets no gizmo at all. A handle that refuses every drag is worse than no
     handle: it advertises an operation the app will not perform.
  6. Undo restores the pre-drag position, since a gesture that cannot be taken back is not a
     finished tool.
  7. A dependent room follows the wall after the drag. The gizmo writes .pos live and walks the
     dependency graph once on release, the same contract the body drag has used since V55; a
     gizmo that skipped it would leave rooms behind.

Run:  python3 bim_phase76_translate_gizmo_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, pathlib, sys

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


async def wall(page, closed=False):
    wid = await page.evaluate("""(c)=>{
      window.__a3dTestSetObjs([]);
      const w=window.__a3dWall([[0,0],[8,0],[8,6]],0.3,3,'center',c);
      window.__a3dSelectFor([w]);
      window.__a3dSet3DView();
      window.__a3dSnapSet({point:true,grid:false,ortho:false});
      return w;}""", closed)
    await page.wait_for_timeout(500)
    return wid


async def arm(page, axis):
    g = await page.evaluate("()=>window.__a3dGizmo()")
    for a in g['arms']:
        if a['axis'] == axis:
            return g, a
    return g, None


async def drag_arm(page, axis, dx, dy):
    """Grab the middle of an arm and drag it with real pointer events."""
    g, a = await arm(page, axis)
    if not a:
        return None
    mx, my = (a['x0'] + a['x1']) / 2, (a['y0'] + a['y1']) / 2
    r = await page.evaluate("()=>window.__a3dCanvasRect()")
    await page.mouse.move(r['left'] + mx, r['top'] + my)
    await page.mouse.down()
    await page.mouse.move(r['left'] + mx + dx, r['top'] + my + dy, steps=8)
    await page.mouse.up()
    await page.wait_for_timeout(280)
    return True


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

        has76 = await page.evaluate("()=>!!window.__acad3dV76")
        ck(has76, "__acad3dV76 marker is present")
        if not has76:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. the gizmo is attached to the selection and follows it")
        wid = await wall(page)
        g = await page.evaluate("()=>window.__a3dGizmo()")
        ck(g is not None and g['ids'] == [wid], "a selected wall gets a gizmo (%s)" % (g and g['ids']))
        ck(len(g['arms']) == 3, "three arms in a 3D view (%s)"
           % [a['axis'] for a in g['arms']])

        for d in ((5, 0, 0), (0, 3, 0), (-2, 0, 4)):
            await page.evaluate("(a)=>window.__a3dMoveObjects([a.id],a.d[0],a.d[1],a.d[2])",
                                {'id': wid, 'd': list(d)})
            await page.wait_for_timeout(220)
            agree = await page.evaluate("""(id)=>{
              const g=window.__a3dGizmo();
              const p=window.__a3dProject(g.origin);
              return {dx:Math.abs(p.x-g.ox),dy:Math.abs(p.y-g.oy),origin:g.origin};}""", wid)
            ck(agree['dx'] < 0.01 and agree['dy'] < 0.01,
               "after a %s move the gizmo is drawn at its own live origin (%.3f, %.3f px)"
               % (d, agree['dx'], agree['dy']))
        moved = await page.evaluate("()=>window.__a3dGizmo().origin")
        ck(abs(moved[0] - (4.075 + 3)) < 0.5 and abs(moved[1] - (1.5 + 3)) < 0.5,
           "and the origin has actually tracked the accumulated (3,3,4) move (%s) -- a cached "
           "origin would still read the selection-time centre" % [round(v, 2) for v in moved])

        await page.evaluate("()=>{window.__a3dSelectFor([]);}")
        await page.wait_for_timeout(250)
        ck(await page.evaluate("()=>window.__a3dGizmo()") is None,
           "with nothing selected there is no gizmo")

        print("\n-- 2. each arm constrains the move to its own axis")
        for axis, dx, dy, comp in (('x', 95, 0, 0), ('y', 0, -80, 1), ('z', 70, 40, 2)):
            wid = await wall(page)
            before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
            hit = await page.evaluate("""(a)=>{
              const g=window.__a3dGizmo();
              const arm=g.arms.filter(function(x){return x.axis===a;})[0];
              return window.__a3dGizmoAt((arm.x0+arm.x1)/2,(arm.y0+arm.y1)/2);}""", axis)
            ck(hit == axis, "the %s arm is pick-able along its shaft (%s)" % (axis.upper(), hit))
            await drag_arm(page, axis, dx, dy)
            after = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
            others = [i for i in (0, 1, 2) if i != comp]
            ck(abs(after[comp] - before[comp]) > 0.4,
               "dragging it moves the object along %s (%s -> %s)"
               % (axis.upper(), before, [round(v, 3) for v in after]))
            ck(all(abs(after[i] - before[i]) < 1e-9 for i in others),
               "and leaves the other two components untouched (%s) -- the constraint is the whole "
               "point of the handle" % [round(after[i], 9) for i in others])

        print("\n-- 3. an axis too foreshortened to drag is hidden, not stretched")
        cfg = await page.evaluate("()=>window.__a3dGizmoConfig()")
        ck(0 < cfg['edgeOn'] < 1,
           "the edge-on test is a FRACTION of the best-projecting axis (%s), so it holds at any "
           "zoom rather than at one camera distance" % cfg['edgeOn'])
        await wall(page)
        await page.evaluate("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(500)
        gp = await page.evaluate("()=>window.__a3dGizmo()")
        axes = sorted(a['axis'] for a in gp['arms'])
        ck(axes == ['x', 'z'],
           "in a PLAN view the vertical axis is gone and the gizmo is X/Z only (%s) -- the first "
           "implementation tested the arm length AFTER scaling it to 74px, which every arm passes "
           "by construction, so it drew a full-size Y arm that moved the object by kilometres per "
           "pixel" % axes)
        lens = [a['len'] for a in gp['arms']]
        ck(max(lens) - min(lens) < 0.5,
           "the arms that remain are the same pixel length (%s)" % [round(v, 1) for v in lens])
        # V110: in plan the Y arm now points NORTH, which is screen-up -- the spot this check
        # used to probe. The claim itself is unchanged and is now tested all the way round: no
        # point near the origin picks the hidden vertical handle.
        vert = await page.evaluate("""()=>{
             const g=window.__a3dGizmo(),hits=[];let i,r;
             for(i=0;i<24;i++)for(r=18;r<=80;r+=6){
               const a=i/24*Math.PI*2,h=window.__a3dGizmoAt(g.ox+Math.cos(a)*r,g.oy+Math.sin(a)*r);
               if(h==='y')hits.push([i,r]);}
             return hits;}""")
        ck(vert == [],
           "and nothing anywhere around the origin picks the hidden vertical arm (%s)" % vert[:4])
        await page.evaluate("()=>window.__a3dSet3DView()")
        await page.wait_for_timeout(450)
        g3 = await page.evaluate("()=>window.__a3dGizmo()")
        lens3 = [a['len'] for a in g3['arms']]
        ck(len(g3['arms']) == 3 and max(lens3) - min(lens3) < 8,
           "back in 3D all three arms are present and within 8px of each other (%s) -- a single "
           "world length could not do that, because perspective foreshortens the three axes by "
           "different amounts" % [round(v, 1) for v in lens3])

        print("\n-- 4. the distance moved is proportional to the drag")
        wid = await wall(page)
        await drag_arm(page, 'x', 50, 0)
        d1 = (await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos", wid))[0]
        wid = await wall(page)
        await drag_arm(page, 'x', 100, 0)
        d2 = (await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos", wid))[0]
        ck(d1 > 0 and abs(d2 / d1 - 2.0) < 0.08,
           "twice the drag is twice the distance (%.3f then %.3f, ratio %.3f) -- asserted as a "
           "ratio rather than against a hardcoded world figure, so a camera change cannot make "
           "this fail for the wrong reason" % (d1, d2, d2 / d1))

        print("\n-- 5. grid snapping quantizes the DISTANCE, not the position")
        wid = await wall(page)
        await page.evaluate("""(id)=>{
          window.__a3dSetPos(id,0.37,0,0);
          window.__a3dSnapSet({point:false,grid:true,ortho:false});}""", wid)
        await page.wait_for_timeout(300)
        await drag_arm(page, 'x', 90, 0)
        pos = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
        await page.evaluate("()=>window.__a3dSnapSet({point:true,grid:false})")
        rem = round(pos[0] - 0.37, 6)
        ck(abs(rem / 0.5 - round(rem / 0.5)) < 1e-6,
           "the distance moved is a whole number of grid steps (%s of 0.5 m)" % rem)
        ck(abs((pos[0] % 0.5) - 0.37) < 1e-6,
           "and the object's deliberate 0.37 m off-grid placement SURVIVES (x=%s) -- snapping the "
           "resulting position instead would have silently re-aligned it" % round(pos[0], 4))

        print("\n-- 6. a locked object gets no gizmo")
        wid = await wall(page)
        await page.evaluate("(id)=>window.__a3dSetLockedById(id,true)", wid)
        await page.wait_for_timeout(250)
        ck(await page.evaluate("()=>window.__a3dGizmo()") is None,
           "a pinned wall shows no handle at all -- a gizmo that refuses every drag advertises an "
           "operation the app will not perform")
        await page.evaluate("(id)=>window.__a3dSetLockedById(id,false)", wid)
        await page.wait_for_timeout(250)
        ck(await page.evaluate("()=>window.__a3dGizmo()") is not None,
           "and it comes back when the pin is released")

        print("\n-- 7. a gizmo move can be undone")
        wid = await wall(page)
        before = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
        await drag_arm(page, 'x', 90, 0)
        mid = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(350)
        aft = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", wid)
        ck(abs(mid[0] - before[0]) > 0.4, "the drag moved it (%s -> %s)"
           % (before, [round(v, 3) for v in mid]))
        ck(aft and abs(aft[0] - before[0]) < 1e-6,
           "and undo puts it back exactly (%s)" % [round(v, 6) for v in (aft or [])])

        print("\n-- 8. dependents follow, once, on release")
        ids = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[9,0],[9,6],[0,6]],0.3,3,'center',true);
          const r=window.__a3dCreateRoomAt([4.5,3],0);
          window.__a3dSelectFor([w]);
          window.__a3dSet3DView();
          window.__a3dSnapSet({point:true,grid:false,ortho:false});
          return {w:w,r:r};}""")
        await page.wait_for_timeout(600)
        # A room does not follow by gaining an offset -- V52/V55 RE-MEASURE it from the walls that
        # bound it, so its own point array changes. Asserting .pos here would assert the wrong
        # mechanism and fail against correct code, which is what the first version of this check
        # did. The honest question is where the room ends up in the world.
        CENTRE = """(id)=>{const o=window.__a3dObjSnapshot(id);
          const q=o.pos||[0,0,0];let sx=0,sz=0;
          for(let i=0;i<o.pts.length;i++){sx+=o.pts[i][0];sz+=o.pts[i][1];}
          return [sx/o.pts.length+q[0], sz/o.pts.length+q[2]];}"""
        r0 = await page.evaluate(CENTRE, ids['r'])
        await drag_arm(page, 'x', 95, 0)
        w1 = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).pos.slice()", ids['w'])
        r1 = await page.evaluate(CENTRE, ids['r'])
        ck(abs(w1[0]) > 0.4, "the wall moved (%s)" % [round(v, 3) for v in w1])
        ck(abs((r1[0] - r0[0]) - w1[0]) < 1e-6 and abs(r1[1] - r0[1]) < 1e-6,
           "and the room it bounds is re-measured onto the wall's new position (centre moved %s "
           "against the wall's %s) -- the gizmo walks the dependency graph once on release, the "
           "contract the body drag has used since V55"
           % (round(r1[0] - r0[0], 4), round(w1[0], 4)))

        print("\n-- 9. the gizmo yields to a running sketch tool")
        wid = await wall(page)
        ck(await page.evaluate("()=>window.__a3dActiveSketchTool()") is None,
           "no tool is running to begin with")
        ck(await page.evaluate("()=>window.__a3dGizmo()") is not None,
           "and the gizmo is up")
        await page.evaluate("()=>window.__a3dStairToolStart()")
        await page.wait_for_timeout(300)
        tool = await page.evaluate("()=>window.__a3dActiveSketchTool()")
        ck(tool is not None, "a sketch tool is now running (%s)" % tool)
        ck(await page.evaluate("()=>window.__a3dGizmo()") is None,
           "the gizmo is suppressed while it runs -- an arm sitting under the cursor would "
           "swallow the tool's first click, which is the click that sets its start point")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)
        ck(await page.evaluate("()=>window.__a3dActiveSketchTool()") is None
           and await page.evaluate("()=>window.__a3dGizmo()") is not None,
           "and it returns when the tool is cancelled")

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
