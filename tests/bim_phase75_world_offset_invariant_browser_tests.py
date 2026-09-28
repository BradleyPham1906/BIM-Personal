"""
bim_phase75_world_offset_invariant_browser_tests.py

Regression suite for __acad3dV75 in canvas_v10.html: an object's world geometry is its local
geometry plus o.pos, and EVERY consumer honours that.

THE BUG AS REPORTED: "i tried to drag the wall for example, and then the knots/dots control still
stay in one place instead of attaching to the wall."

THE BUG AS MEASURED, on the V74 build, before anything was changed:

    wall moved (4, 0, 3)      grips stayed put; 135.2 px from the wall
    sketch moved (5, 0, 0)    did not move on screen at all,
                              still PICKED at its old position,
                              did NOT pick at its new one

o.pos was applied by the solid renderer and by rooms, and silently dropped by grips, sketch
drawing, sketch picking, marquee testing and snap-candidate generation. Five holes, one cause.
Patching bimDrawGrips alone would have closed the reported symptom and left the other four -- so
the fix states the invariant once (bimObjOffset / bimWorldPt) and routes every consumer through it.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. Grips are compared against the object's OWN projected geometry, not against a remembered
     pixel. A camera change, a DPR change or a projection change moves both together, so the check
     measures agreement rather than a coordinate that happens to be right today. Asserted after a
     move in X, in Z, in Y, and after a nudge -- vertical movement is the case a 2D-only fix misses.
  2. bimPickGrip is probed at the grip's REPORTED position. Drawing grips correctly while still
     matching clicks against stale coordinates would pass a drawing-only check and fail the user,
     since the stranded squares were the live drag handles.
  3. A grip drag on a MOVED object lands where the cursor is. This is the inverse transform: a
     world cursor point being written into a local array. It was wrong by exactly -pos, which is
     invisible until an object has been moved at least once.
  4. A moved sketch is drawn, picked and marquee-selected at its new place AND NOT at its old one.
     Both halves matter: a consumer that applied the offset twice would pass "picks at the new
     place" while being just as broken.
  5. Rooms become marquee-selectable. They never were: bimObjScreenPoints could read a mesh or a
     sketch, a room is neither, so it returned [] and bimMarqueeTest([]) is false for every
     rectangle. Found by writing this suite, not by reading the code.
  6. Snap candidates move with their object. A moved wall that still advertises its old corners
     does not merely fail to help -- it actively pulls new geometry to the wrong place.
  7. The public grip-write hooks still take LOCAL coordinates. They are a geometry-write surface,
     not a cursor; changing their meaning would silently break every suite that calls them.

Run:  python3 bim_phase75_world_offset_invariant_browser_tests.py [path/to/canvas_v10.html]
"""

import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

# The screen points the object's plan geometry actually occupies, computed from the object itself
# through the app's own projection -- the thing grips have to agree with.
PLAN = "(id)=>window.__a3dPlanScreenPoints(id)"


def maxdev(a, b):
    return max(max(abs(a[i][0] - b[i][0]), abs(a[i][1] - b[i][1])) for i in range(len(a)))


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

        has75 = await page.evaluate("()=>!!window.__acad3dV75")
        ck(has75, "__acad3dV75 marker is present")
        if not has75:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        print("\n-- 1. grips follow the object they belong to")
        wid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[8,0],[8,6]],0.3,3,'center',false);
          window.__a3dSelectFor([w]);
          return w;}""")
        await page.wait_for_timeout(400)
        g = await page.evaluate("()=>window.__a3dGrips()")
        p = await page.evaluate(PLAN, wid)
        ck(len(g) == 3 and len(p) == 3, "the 3-point wall has 3 grips")
        ck(maxdev([[x['x'], x['y']] for x in g], p) < 0.01,
           "they sit on the wall before any move (%.3f px)"
           % maxdev([[x['x'], x['y']] for x in g], p))

        for label, d in (("in plan (4, 0, 3)", (4, 0, 3)),
                         ("again, cumulatively (-9, 0, 2)", (-9, 0, 2)),
                         ("and vertically (0, 2.5, 0)", (0, 2.5, 0))):
            await page.evaluate("(a)=>window.__a3dMoveObjects([a.id],a.d[0],a.d[1],a.d[2])",
                                {'id': wid, 'd': list(d)})
            await page.wait_for_timeout(250)
            g = await page.evaluate("()=>window.__a3dGrips()")
            p = await page.evaluate(PLAN, wid)
            dev = maxdev([[x['x'], x['y']] for x in g], p)
            ck(dev < 0.01,
               "after moving %s the grips are still on it (%.3f px) -- on the V74 build a "
               "(4,0,3) move alone left them 135.2 px away" % (label, dev))

        await page.evaluate("(id)=>window.__a3dNudgeObject(id,'ArrowRight')", wid)
        await page.wait_for_timeout(250)
        g = await page.evaluate("()=>window.__a3dGrips()")
        p = await page.evaluate(PLAN, wid)
        ck(maxdev([[x['x'], x['y']] for x in g], p) < 0.01,
           "and after a keyboard nudge, which moves the object by a different code path")

        print("\n-- 2. the grip you can SEE is the grip that picks")
        picks = await page.evaluate("""()=>{
          const g=window.__a3dGrips();
          return g.map(function(x){return window.__a3dGripAt(x.x,x.y);});}""")
        ck(all(q and q['objId'] == wid for q in picks),
           "every grip is pick-able at its own reported position (%s)"
           % [(q or {}).get('idx') for q in picks])
        idxs = sorted(q['idx'] for q in picks)
        ck(idxs == [0, 1, 2], "and each returns its own index (%s)" % idxs)
        off = await page.evaluate("""()=>{
          const g=window.__a3dGrips()[0];
          return window.__a3dGripAt(g.x-140,g.y);}""")
        ck(off is None,
           "and nothing is pick-able 140 px away, which is where the stale grips used to sit")

        print("\n-- 3. a grip drag on a MOVED object lands under the cursor")
        # A fresh wall, moved in plan only: the wall above was lifted 2.5m, which puts its far grip
        # low enough on screen to sit behind the tool dock, and a pointer event aimed there never
        # reaches the canvas at all.
        wid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[7,0],[7,5]],0.3,3,'center',false);
          window.__a3dMoveObjects([w],6,0,-4);
          window.__a3dSelectFor([w]);
          // Snapping off for this check only: its whole job is to move a dragged point AWAY from
          // the cursor, which is the very thing being measured here.
          window.__a3dSnapSet({point:false,grid:false,ortho:false});
          return w;}""")
        await page.wait_for_timeout(400)
        start = await page.evaluate("()=>{const g=window.__a3dGrips()[2];return [g.x,g.y];}")
        rect = await page.evaluate("()=>window.__a3dCanvasRect()")
        tx, ty = start[0] + 70, start[1] - 45
        reach = await page.evaluate("""(a)=>{
          function at(x,y){const e=document.elementFromPoint(x,y);return e?e.id||e.tagName:null;}
          return [at(a.x0,a.y0),at(a.x1,a.y1)];}""",
                                    {'x0': rect['left'] + start[0], 'y0': rect['top'] + start[1],
                                     'x1': rect['left'] + tx, 'y1': rect['top'] + ty})
        ck(reach == ['a3d-canvas', 'a3d-canvas'],
           "both ends of the drag are on the canvas and not behind a panel (%s) -- asserted "
           "because a pointer event aimed at a covered grip silently does nothing, which would "
           "make the drag check below pass for the wrong reason" % reach)
        # Real events through the real handlers: no synthetic shortcut around onDown/onMove/onUp.
        await page.mouse.move(rect['left'] + start[0], rect['top'] + start[1])
        await page.mouse.down()
        await page.mouse.move(rect['left'] + tx, rect['top'] + ty, steps=6)
        await page.mouse.up()
        await page.wait_for_timeout(300)
        drag = await page.evaluate("""(a)=>{
          const g=window.__a3dGrips()[2];
          return {want:a.want,got:[g.x,g.y],pos:window.__a3dObjSnapshot(a.id).pos,
                  cl:window.__a3dObjSnapshot(a.id).bim.centerline};}""",
                                   {'id': wid, 'want': [tx, ty]})
        await page.evaluate("()=>window.__a3dSnapSet({point:true})")
        print("     " + str(drag))
        dv = max(abs(drag['got'][0] - drag['want'][0]), abs(drag['got'][1] - drag['want'][1]))
        ck(dv < 2.0,
           "the dragged grip ends within 2 px of the cursor (%.2f px) -- before this phase the "
           "world cursor point was written straight into a LOCAL point array, so the first drag "
           "after a move threw the point by -pos" % dv)
        ck(drag['pos'] == [6, 0, -4],
           "the drag edited the wall's GEOMETRY and left its offset alone (%s) -- writing the "
           "world point into the local array would have produced a centreline shifted by -pos "
           "instead (%s)" % (drag['pos'], drag['cl'][2]))
        g = await page.evaluate("()=>window.__a3dGrips()")
        p = await page.evaluate(PLAN, wid)
        ck(maxdev([[x['x'], x['y']] for x in g], p) < 0.01,
           "and the rebuilt wall's grips still agree with the rebuilt wall")

        print("\n-- 4. a moved sketch is drawn, picked and marquee-hit where it now is")
        sk = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const id=window.__a3dSketch('poly',[[0,0],[6,0],[6,4],[0,4]]);
          window.__a3dSelectFor([id]);
          return id;}""")
        await page.wait_for_timeout(350)
        base = await page.evaluate("""(id)=>{
          const o=window.__a3dObjSnapshot(id);
          const m=window.__a3dProject([3,o.y,0]);
          return {mid:[m.x,m.y],pick:window.__a3dPick(m.x,m.y)};}""", sk)
        ck(base['pick'] == sk, "it picks on its own edge to begin with")
        await page.evaluate("(id)=>window.__a3dMoveObjects([id],5,0,2)", sk)
        await page.wait_for_timeout(300)
        after = await page.evaluate("""(id)=>{
          const o=window.__a3dObjSnapshot(id);
          const old=window.__a3dProject([3,o.y,0]);
          const now=window.__a3dProject([3+o.pos[0],o.y+o.pos[1],0+o.pos[2]]);
          return {pos:o.pos, oldPick:window.__a3dPick(old.x,old.y),
                  newPick:window.__a3dPick(now.x,now.y),
                  oldPt:[old.x,old.y], nowPt:[now.x,now.y]};}""", sk)
        print("     " + str(after))
        ck(after['newPick'] == sk,
           "after a (5,0,2) move it picks at its NEW edge -- on the V74 build it did not")
        ck(after['oldPick'] is None,
           "and no longer at its old one (%s) -- a consumer that applied the offset twice would "
           "pass the previous check and still be wrong" % after['oldPick'])
        sp = await page.evaluate("(id)=>window.__a3dObjScreenPoints(id)", sk)
        pl = await page.evaluate(PLAN, sk)
        ck(maxdev(sp, pl) < 0.01,
           "the points marquee tests against are the points it is drawn at (%.3f px)"
           % maxdev(sp, pl))
        m = await page.evaluate("""(id)=>{
          const s=window.__a3dObjScreenPoints(id);
          const xs=s.map(function(p){return p[0];}), ys=s.map(function(p){return p[1];});
          const pad=25;
          return {atNew:window.__a3dMarquee(Math.min.apply(null,xs)-pad,Math.min.apply(null,ys)-pad,
                                            Math.max.apply(null,xs)+pad,Math.max.apply(null,ys)+pad)};}""", sk)
        ck(sk in m['atNew'], "and a marquee over its new position selects it (%s)" % m['atNew'])

        print("\n-- 5. rooms are marquee-selectable at all")
        rid = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          window.__a3dWall([[0,0],[9,0],[9,6],[0,6]],0.3,3,'center',true);
          return window.__a3dCreateRoomAt([4.5,3],0);}""")
        await page.wait_for_timeout(450)
        rpts = await page.evaluate("(id)=>window.__a3dObjScreenPoints(id)", rid)
        ck(rpts and len(rpts) >= 3,
           "a room reports screen points (%d) -- it reported NONE before this phase, because "
           "bimObjScreenPoints could read a mesh or a sketch and a room is neither"
           % (len(rpts or [])))
        rsel = await page.evaluate("""(id)=>{
          const s=window.__a3dObjScreenPoints(id);
          const xs=s.map(function(p){return p[0];}), ys=s.map(function(p){return p[1];});
          return window.__a3dMarquee(Math.min.apply(null,xs)-6,Math.min.apply(null,ys)-6,
                                     Math.max.apply(null,xs)+6,Math.max.apply(null,ys)+6);}""", rid)
        ck(rid in rsel, "and a window marquee over it selects it (%s)" % rsel)
        await page.evaluate("(id)=>window.__a3dMoveObjects([id],3,0,0)", rid)
        await page.wait_for_timeout(250)
        rmoved = await page.evaluate("""(id)=>{
          const s=window.__a3dObjScreenPoints(id);
          const xs=s.map(function(p){return p[0];}), ys=s.map(function(p){return p[1];});
          return window.__a3dMarquee(Math.min.apply(null,xs)-6,Math.min.apply(null,ys)-6,
                                     Math.max.apply(null,xs)+6,Math.max.apply(null,ys)+6);}""", rid)
        ck(rid in rmoved, "and still does after the room is moved")

        print("\n-- 6. snap candidates move with their object")
        snap = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
          const before=window.__a3dSnapCandidates(0);
          window.__a3dMoveObjects([w],10,0,0);
          const after=window.__a3dSnapCandidates(0);
          function has(a,x,z){return a.some(function(p){
            return Math.abs(p[0]-x)<1e-6&&Math.abs(p[1]-z)<1e-6;});}
          return {oldStill:has(after,0,0), newThere:has(after,10,0),
                  hadOld:has(before,0,0), n:after.length};}""")
        print("     " + str(snap))
        ck(snap['hadOld'] is True, "the unmoved wall offers its own end as a snap point")
        ck(snap['newThere'] is True, "after a 10m move the snap point is at the new end")
        ck(snap['oldStill'] is False,
           "and no longer at the old one -- a stale snap candidate does not merely fail to help, "
           "it pulls the NEXT piece of geometry to a place nothing occupies")
        elev = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
          window.__a3dMoveObjects([w],0,4,0);
          return {atGround:window.__a3dSnapCandidates(0).length,
                  atFour:window.__a3dSnapCandidates(4).length};}""")
        ck(elev['atFour'] > elev['atGround'],
           "a wall lifted 4m offers its snap points at elevation 4, not 0 (%s)" % elev)

        print("\n-- 7. the public grip-write hooks still speak LOCAL coordinates")
        loc = await page.evaluate("""()=>{
          window.__a3dTestSetObjs([]);
          const id=window.__a3dSketch('poly',[[0,0],[6,0],[6,4],[0,4]]);
          window.__a3dMoveObjects([id],5,0,0);
          const pts=window.__a3dDragGripTo(id,1,7,0);
          return {pts:pts, off:window.__a3dObjOffset(id)};}""")
        ck(loc['pts'][1] == [7, 0],
           "__a3dDragGripTo writes the value it was given straight into the local array (%s) -- it "
           "is a geometry-write surface, not a cursor, and every suite that calls it passes local "
           "values" % loc['pts'][1])
        ck(loc['off'] == [5, 0, 0], "while the object keeps its offset (%s)" % loc['off'])

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
