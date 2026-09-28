"""
bim_phase99_region_associativity_browser_tests.py

Regression suite for __acad3dV99 in canvas_v10.html: a room -- or a hatch, floor, ceiling, roof
-- bounded by SEVERAL shapes follows every one of them.

THE OWNER'S DIRECTION: "room should not just be bounded by walls but the shape they are bounded
to. That's why the relation graph is important."

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE ROOM IS MADE WITH THE ROOM TOOL AND THE MOUSE, inside four SEPARATE lines -- no closed
     shape anywhere -- which was the case that produced a frozen snapshot, or no room at all.
  2. THE RELATION GRAPH IS ASSERTED DIRECTLY: every bounding line has a 'region' edge to the
     room. That is the owner's point, and a room that followed by some side channel would pass
     every geometry check while the graph stayed empty.
  3. EACH KIND OF CHANGE IS DRIVEN SEPARATELY, because each reaches the room by a different
     path: a member edited by its grips (graph), a NEW shape splitting the room (plane
     signature), a member DELETED (signature, then the region opens), and Undo.
  4. THE SEED STAYS WHERE IT WAS CLICKED: split, the room keeps the side it was placed on.
  5. MIXED BOUNDARIES: a wall, a sketch and a construction line bound one room together, and
     moving the construction line with the mouse re-sizes it.
  6. EVERY KIND OF DEPENDENT: hatch and floor on a region follow a member edit.
  7. OWN-FRAME AND MOVED-ON-ITS-OWN rules: a region room dragged into the next region re-bounds
     there; a region hatch moved on its own is detached and says so.
  8. BACKWARD COMPATIBILITY: an old-build 'wallgroup' room is adopted without changing shape,
     then follows; a room whose single source is deleted is detached and says so; a lone
     closed rectangle is still a single-source room.
  9. PERSISTENCE: the relationship survives a save and a reload, and still works after it.
 10. Zero uncaught page errors.

Run:  python3 bim_phase99_region_associativity_browser_tests.py [path/to/canvas_v10.html]
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


def ln(i, a, b):
    return {'id': i, 't': 'sketch', 'name': i, 'col': '#5ec4b8', 'pos': [0, 0, 0],
            'pts': [a, b], 'y': 0, 'closed': False}


# four SEPARATE lines crossing at the corners: 6 x 4 inside, nothing closed anywhere
FOUR = [ln('L1', [-1, 0], [10, 0]), ln('L2', [6, -1], [6, 5]),
        ln('L3', [10, 4], [-1, 4]), ln('L4', [0, 5], [0, -1])]


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

        has = await page.evaluate("()=>!!window.__acad3dV99")
        ck(has, "__acad3dV99 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        box = await page.evaluate(
            "()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();"
            "return [r.left,r.top];}")

        async def scr(p):
            s = await page.evaluate("(p)=>window.__a3dToScreen(p,0)", p)
            return [box[0] + s[0], box[1] + s[1]]

        async def snap(oid):
            # a missing object comes back as a harmless placeholder, so an earlier failure makes
            # the NEXT checks fail instead of crashing the run (no RESULT line = runner error)
            o = await page.evaluate("(id)=>id?window.__a3dObjSnapshot(id):null", oid)
            if o:
                return o
            return {'area': -1.0, 'pts': [[0, 0], [0, 1]], 'region': {}, 'bim': {'profile': [[0, 0]]},
                    'pos': [0, 0, 0], 'missing': True}

        async def toast():
            return await page.evaluate(
                "()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")

        async def ids():
            return await page.evaluate("()=>window.__a3dState().objs.map(o=>o.id)")

        async def scene(objs):
            await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", objs)
            await page.evaluate("()=>{window.__a3dFlat(true);window.__a3dFit();window.__a3dTestPaint();}")
            await page.wait_for_timeout(200)

        async def drag_screen(a, b):
            await page.mouse.move(a[0], a[1])
            await page.mouse.down()
            await page.mouse.move(b[0], b[1], steps=10)
            await page.mouse.up()
            await page.wait_for_timeout(250)

        async def grip_drag(oid, idx, to):
            await page.evaluate("(id)=>window.__a3dSelectFor([id])", oid)
            await page.evaluate("()=>window.__a3dTestPaint()")
            gs = await page.evaluate("()=>window.__a3dGrips()")
            g = [x for x in gs if x.get('objId') == oid and x.get('idx') == idx and not x.get('mid')]
            if not g:
                return False
            await drag_screen([box[0] + g[0]['x'], box[1] + g[0]['y']], await scr(to))
            return True

        async def click_delete(p):
            await page.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")
            s = await scr(p)
            await page.mouse.click(s[0], s[1])
            await page.wait_for_timeout(150)
            sel = (await page.evaluate("()=>window.__a3dState()")).get('sel')
            await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
            await page.keyboard.press('Delete')
            await page.wait_for_timeout(250)
            return sel

        # ------------------------------------------------ 1. the owner's scenario
        print("\n-- 1. a room inside four separate lines, made with the Room tool")
        await scene(FOUR + [ln('L5', [12, -1], [12, 5])])   # L5: on the plan, bounding nothing
        await palette_run(page, 'Room')
        c = await scr([1.5, 2.0])
        await page.mouse.click(c[0], c[1])
        await page.wait_for_timeout(300)
        rooms = [i for i in await ids() if i not in ('L1', 'L2', 'L3', 'L4', 'L5')]
        rid = rooms[0] if rooms else None
        r0 = await snap(rid)
        reg0 = (r0 or {}).get('region') or {}
        ck(not r0.get('missing') and r0.get('t') == 'room' and near(r0['area'], 24.0, 1e-6),
           "clicking inside four separate lines makes a 6 x 4 room (%s)" % (r0 and r0.get('area')))
        ck(sorted(reg0.get('members') or []) == ['L1', 'L2', 'L3', 'L4'] and r0.get('sourceType') == 'region',
           "it records ALL FOUR lines as what bounds it (%s, %s)" % (reg0.get('members'), r0 and r0.get('sourceType')))
        rel_ok = True
        for lid in ('L1', 'L2', 'L3', 'L4'):
            rel = await page.evaluate("(id)=>window.__a3dGraphRelationsOf(id)", lid)
            deps = [d for d in (rel or {}).get('dependents', []) if d.get('objId') == rid and d.get('rel') == 'region']
            rel_ok = rel_ok and len(deps) == 1
        ck(rel_ok, "the relation graph links every one of the four lines to the room")
        ft = await page.evaluate("(id)=>window.__a3dFollowsText(id)", rid)
        ck(ft and all(n in ft for n in ('L1', 'L2', 'L3', 'L4')),
           "Properties names the four shapes it follows (%r)" % ft)

        print("\n-- 1b. a member edited by its grips -> the room follows (graph)")
        ok1 = await grip_drag('L2', 0, [8.0, -1.0])
        ok2 = await grip_drag('L2', 1, [8.0, 5.0])
        r1 = await snap(rid)
        ck(ok1 and ok2 and near(r1['area'], 32.0, 0.3),
           "dragging the right-hand line out to x=8 grows the room 24 -> 32 m2 (%.3f)" % r1['area'])

        print("\n-- 1c. a NEW line across the room -> the room re-bounds, on the side it was placed")
        await palette_run(page, 'Line')
        for p in ('3,-1', '3,5'):
            await page.evaluate("(p)=>window.__a3dTypedPoint(p)", p)
            await page.wait_for_timeout(150)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(300)
        new_ids = [i for i in await ids() if i not in ('L1', 'L2', 'L3', 'L4', 'L5', rid)]
        split = new_ids[0] if new_ids else None
        r2 = await snap(rid)
        ck(split and near(r2['area'], 12.0, 0.05),
           "a line drawn at x=3 cuts the room to the 3 x 4 part it was placed in (%.3f)" % r2['area'])
        ck(split in ((r2.get('region') or {}).get('members') or []),
           "and the new line is now one of its members")
        xs = [p[0] for p in r2['pts']]
        ck(max(xs) <= 3.0 + 0.06, "the room stayed on the LEFT, where it was clicked (max x %.3f)" % max(xs))

        print("\n-- 1d. that line deleted -> the room grows back")
        sel_split = await click_delete([3.0, 3.0])
        r3 = await snap(rid)
        ck(sel_split == split and split not in await ids(),
           "the split line was clicked and deleted (%s)" % sel_split)
        ck(near(r3['area'], 32.0, 0.3), "and the room grows back to 32 m2 (%.3f)" % r3['area'])

        print("\n-- 1d2. a line that bounded NOTHING dragged across the room -> the room re-bounds")
        # nothing is added or deleted, so only a plane signature that sees POSITIONS notices it
        ok5 = await grip_drag('L5', 0, [5.0, -1.0])
        ok6 = await grip_drag('L5', 1, [5.0, 5.0])
        l5 = (await snap('L5'))['pts']
        rL = await snap(rid)
        want5 = ((l5[0][0] + (0 - l5[0][1]) * (l5[1][0] - l5[0][0]) / (l5[1][1] - l5[0][1])) +
                 (l5[0][0] + (4 - l5[0][1]) * (l5[1][0] - l5[0][0]) / (l5[1][1] - l5[0][1]))) / 2 * 4
        ck(ok5 and ok6 and 'L5' in ((rL.get('region') or {}).get('members') or []) and near(rL['area'], want5, 0.05),
           "L5 becomes a member and the room is cut at it: %.3f m2 (expected %.3f)" % (rL['area'], want5))
        await grip_drag('L5', 0, [12.0, -1.0])
        await grip_drag('L5', 1, [12.0, 5.0])
        rL2 = await snap(rid)
        ck(near(rL2['area'], r3['area'], 0.3) and 'L5' not in ((rL2.get('region') or {}).get('members') or []),
           "dragged back out, the room is whole again and L5 is no longer a member (%.3f)" % rL2['area'])

        print("\n-- 1e. a bounding line deleted -> the room is no longer enclosed and says so")
        await click_delete([5.0, 4.0])
        r4 = await snap(rid)
        t4 = await toast()
        ck('L3' not in await ids(), "the top line was deleted")
        ck(r4 and (r4.get('region') or {}).get('open') is True and near(r4['area'], r3['area'], 1e-9),
           "the room is marked not enclosed and KEEPS its last shape (%.3f)" % (r4 and r4['area']))
        ck('no longer enclosed' in (t4 or ''), "and a toast says so (%r)" % t4)
        ft4 = await page.evaluate("(id)=>window.__a3dFollowsText(id)", rid)
        ck('NOT ENCLOSED' in (ft4 or ''), "Properties says it is not enclosed (%r)" % ft4)
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(250)
        r5 = await snap(rid)
        ck('L3' in await ids() and not r5.get('missing') and (r5.get('region') or {}).get('open') is False,
           "UNDO brings the line back and the room is enclosed again")
        # L1 and L3 start at x=-1, so the left line can move to x=-0.5 and still close the room
        ok3 = await grip_drag('L4', 0, [-0.5, 5.0])
        ok4 = await grip_drag('L4', 1, [-0.5, -1.0])
        r6 = await snap(rid)
        # the expected area is DERIVED from where the line actually landed (a mouse drag snaps),
        # as the trapezoid between it, L1 (z=0), L3 (z=4) and the right line where IT landed
        l4 = (await snap('L4'))['pts']
        l2 = (await snap('L2'))['pts']
        def xl(line, z):
            (xa, za), (xb, zb) = line
            return xa + (z - za) * (xb - xa) / (zb - za)
        def x_at(z):
            return xl(l4, z)
        want = (xl(l2, 0) - x_at(0) + xl(l2, 4) - x_at(4)) / 2 * 4
        ck(ok3 and ok4 and x_at(0) < -0.2 and near(r6['area'], want, 0.02),
           "and it still follows after the undo: left line moved out to x=%.3f..%.3f, area %.3f "
           "== %.3f" % (x_at(0), x_at(4), r6['area'], want))

        # ------------------------------------------------ 2. mixed boundary
        print("\n-- 2. a wall, a sketch and a construction line bound one room together")
        await scene([])
        mix = await page.evaluate("""()=>{
            var w=window.__a3dWall([[-1,0],[7,0]],0.2,3,'center',false);
            var cl=window.__a3dAddCline([0,4],[1,0],false,0);
            window.__a3dTestSetObjs(window.__a3dState().objs.concat([
              {id:'S1',t:'sketch',name:'S1',col:'#5ec4b8',pos:[0,0,0],pts:[[0,-1],[0,6]],y:0,closed:false},
              {id:'S2',t:'sketch',name:'S2',col:'#5ec4b8',pos:[0,0,0],pts:[[6,-1],[6,6]],y:0,closed:false}]));
            window.__a3dFit();window.__a3dTestPaint();
            return {w:w,cl:cl&&cl.id?cl.id:cl};}""")
        mid = await page.evaluate("()=>window.__a3dCreateRoomAt([3,2],0)")
        m0 = await snap(mid)
        mem = (m0 or {}).get('region', {}).get('members') or []
        # __acad3dV105b: a room stops at the FACE of a wall that bounds it, not at its centreline.
        # The 0.2 wall along z=0 takes 0.1 off the bottom; a sketch and a construction line have no
        # body, so the other three sides are where they are drawn. 6 x 3.9, not 6 x 4.
        ck(m0 and near(m0['area'], 23.4, 1e-6) and mix['w'] in mem and mix['cl'] in mem and 'S1' in mem and 'S2' in mem,
           "the room is 6 x 3.9 = 23.4 m2 to the wall's face, and its members are the wall, the construction line and both sketches (%s)" % mem)
        ck(m0 and m0.get('sourceType') == 'region', "its sourceType is 'region' (%s)" % (m0 and m0.get('sourceType')))
        # move the construction line up by 1 with the mouse: select it, drag its body
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", mix['cl'])
        await page.evaluate("()=>window.__a3dTestPaint()")
        await drag_screen(await scr([4.5, 4.0]), await scr([4.5, 5.0]))
        clx = await snap(mix['cl'])
        m1 = await snap(mid)
        dz = (clx or {}).get('pos', [0, 0, 0])[2]
        dx = (clx or {}).get('pos', [0, 0, 0])[0]
        # V99 found the body drag TELEPORTED an object: its origin jumped under the cursor
        ck(near(dz, 1.0, 0.1) and near(dx, 0.0, 0.1),
           "a body drag of 1 m moves the line BY the drag, not to the cursor (dx %.3f, dz %.3f)" % (dx, dz))
        ck(abs(dz) > 0.3 and near(m1['area'], 6.0 * (3.9 + dz), 0.05),
           "dragging the construction line by %.3f re-sizes the room to 6 x %.3f = %.3f m2 (%.3f)"
           % (dz, 3.9 + dz, 6 * (3.9 + dz), m1['area']))

        # ------------------------------------------------ 3. other dependents
        print("\n-- 3. a hatch and a floor on a region follow it")
        await scene([dict(x) for x in FOUR])
        hid = await page.evaluate("()=>window.__a3dApplyHatchAt([3,2],0)")
        fid = await page.evaluate("()=>window.__a3dFloorOnRegionAt([3,2],0,0.2)")
        h0 = await snap(hid)
        f0 = await snap(fid)
        ck(h0 and (h0.get('region') or {}).get('members') and f0 and (f0.get('region') or {}).get('members'),
           "a hatch and a floor made on the region record it")
        await page.evaluate("()=>{window.__a3dDragGripTo('L2',0,9,-1);window.__a3dDragGripTo('L2',1,9,5);}")
        await page.wait_for_timeout(150)
        h1 = await snap(hid)
        f1 = await snap(fid)
        harea = await page.evaluate("(id)=>{var o=window.__a3dObjSnapshot(id);var p=o.pts,a=0;for(var i=0;i<p.length;i++){var j=(i+1)%p.length;a+=p[i][0]*p[j][1]-p[j][0]*p[i][1];}return Math.abs(a)/2;}", hid)
        fx = max(p[0] for p in f1['bim']['profile']) if f1 else None
        ck(near(harea, 36.0, 0.05), "the hatch follows the line to x=9: 9 x 4 = 36 m2 (%.3f)" % harea)
        ck(near(fx, 9.0, 1e-6), "and so does the floor (max x %s)" % fx)

        print("\n-- 3b. moved on its own: a room re-bounds, a hatch detaches")
        # a fresh plan with a dividing line, and nothing on top of the room to take the click
        await scene([dict(x) for x in FOUR] + [ln('MID', [4, -1], [4, 5])])
        await page.evaluate("()=>{window.__a3dDragGripTo('L2',0,9,-1);window.__a3dDragGripTo('L2',1,9,5);}")
        rr = await page.evaluate("()=>window.__a3dCreateRoomAt([2,2],0)")
        rr0 = await snap(rr)
        ck(rr0 and near(rr0['area'], 16.0, 0.05), "a room in the left part is 4 x 4 (%.3f)" % (rr0 and rr0['area']))
        await page.evaluate("()=>window.__a3dFit()")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", rr)
        await page.evaluate("()=>window.__a3dTestPaint()")
        # V110: the gizmo's Y arrow points north, over (2,1), where this drag used to grab the
        # room, so the press became a gizmo drag. The grab point is now chosen where no gizmo
        # handle is -- which is what the comment above has always meant.
        grab = [2.0, 1.0]
        for cand in ([1.0, 3.2], [3.2, 3.2], [0.8, 0.8], [3.0, 1.0]):
            cs = await page.evaluate("(p)=>window.__a3dToScreen(p,0)", cand)
            if await page.evaluate("(p)=>window.__a3dGizmoAt(p[0],p[1])", [cs[0], cs[1]]) is None:
                grab = cand
                break
        await drag_screen(await scr(grab), await scr([grab[0] + 5.0, grab[1]]))
        rr1 = await snap(rr)
        ck(rr1 and (rr1.get('region') or {}).get('seed') and near(rr1['area'], 20.0, 0.1),
           "dragged into the right-hand part, the room RE-BOUNDS there: 5 x 4 = 20 m2 (%.3f)" % (rr1 and rr1['area']))
        hid = await page.evaluate("()=>window.__a3dApplyHatchAt([2,2],0)")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", hid)
        await page.evaluate("(id)=>window.__a3dPropagateFrom([id],'transform',[1,0,0])", hid)
        h2 = await snap(hid)
        t2 = await toast()
        ck(not h2.get('missing') and not h2.get('region') and 'no longer linked' in (t2 or ''),
           "a hatch moved on its own is detached, and the toast says so (%r)" % t2)

        # ------------------------------------------------ 4. compatibility
        print("\n-- 4. older rooms and single sources")
        await scene([])
        legacy = await page.evaluate("""()=>{
            var a=window.__a3dWall([[-1,0],[9,0]],0.2,3,'center',false);
            var b=window.__a3dWall([[5,-1],[5,4]],0.2,3,'center',false);
            var c=window.__a3dWall([[9,3],[-1,3]],0.2,3,'center',false);
            var d=window.__a3dWall([[0,4],[0,-1]],0.2,3,'center',false);
            var objs=window.__a3dState().objs;
            objs.push({id:'OLD',t:'room',name:'Room_old',col:'#7fd4c4',pos:[0,0,0],
              pts:[[0,0],[5,0],[5,3],[0,3]],y:0,area:15,levelId:'lvl-0',sourceType:'wallgroup',sourceId:null,layer:'layer-0'});
            window.__a3dTestSetObjs(objs);
            window.__a3dRegenerateRegions();
            return {b:b};}""")
        o0 = await snap('OLD')
        ck(o0 and (o0.get('region') or {}).get('want') == 'walls' and near(o0['area'], 15.0, 1e-9)
           and len((o0.get('region') or {}).get('members') or []) == 4,
           "an older build's wallgroup room is ADOPTED: walls-only, four members, shape unchanged")
        await page.evaluate("(b)=>{window.__a3dDragWallGripTo(b,0,7,-1);window.__a3dDragWallGripTo(b,1,7,4);}", legacy['b'])
        o1 = await snap('OLD')
        # __acad3dV105b: 0.2 walls all round, so the room measures 6.8 x 2.8 inside their faces.
        ck(o1 and near(o1['area'], 19.04, 0.01),
           "and then follows its walls: right wall moved to x=7 -> 6.8 x 2.8 = 19.04 m2 inside the faces (%.3f)" % (o1 and o1['area']))

        await scene([{'id': 'RECT', 't': 'sketch', 'name': 'RECT', 'col': '#5ec4b8', 'pos': [0, 0, 0],
                      'pts': [[0, 0], [4, 0], [4, 3], [0, 3]], 'y': 0}])
        sr = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        s0 = await snap(sr)
        ck(s0 and s0.get('sourceType') == 'sketch' and s0.get('sourceId') == 'RECT' and not s0.get('region'),
           "a lone closed rectangle still makes a SINGLE-source room (%s)" % (s0 and s0.get('sourceType')))
        await click_delete([4.0, 1.5])
        s1 = await snap(sr)
        t3 = await toast()
        ck('RECT' not in await ids() and not s1.get('missing') and s1.get('sourceId') is None and 'source was deleted' in (t3 or ''),
           "deleting its source detaches it and says so (%r)" % t3)

        # ------------------------------------------------ 5. persistence
        print("\n-- 5. the relationship survives a save and a reload")
        await scene([dict(x) for x in FOUR])
        pr = await page.evaluate("()=>window.__a3dCreateRoomAt([3,2],0)")
        await page.wait_for_timeout(700)
        await page.reload()
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(200)
        p0 = await snap(pr)
        ck(p0 and sorted((p0.get('region') or {}).get('members') or []) == ['L1', 'L2', 'L3', 'L4'],
           "after a reload the room still knows its four members")
        await page.evaluate("()=>{window.__a3dDragGripTo('L2',0,7,-1);window.__a3dDragGripTo('L2',1,7,5);}")
        p1 = await snap(pr)
        ck(p1 and near(p1['area'], 28.0, 0.01), "and still follows them: 7 x 4 = 28 m2 (%.3f)" % (p1 and p1['area']))

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
