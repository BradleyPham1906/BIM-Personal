#!/usr/bin/env python3
"""bim_phase112_gizmo_input_browser_tests.py -- V112: what a gizmo drag understands.

Every claim is driven with real pointer and key events and asserted on the model.

  1. OBJECT SNAP: with POINT snap on, a drag lands one of the selection's own points exactly on
     another object's point, through the freedom the handle allows -- and with it off, the same
     drag does not.
  2. TYPED VALUES: a distance, an angle and a factor typed during a drag finish it exactly; the
     gesture keeps deciding the direction, Backspace edits, and what depends on the objects
     catches up as it does for the mouse.
  3. ESCAPE: puts everything back where the press found it, mid-drag, for a move and for a scale.
  4. CTRL COPIES: the originals stay, the copies move, one undo removes them, and Escape mid-drag
     takes the copies away again.
  5. SHIFT IS FINE: the same cursor travel moves a quarter as far.
  6. THE PIVOT: Alt on the centre square moves the gizmo and nothing else; rotation then happens
     about that point; the menu puts it back; Escape restores it.
"""
import asyncio, math, pathlib, sys
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
        print(('ok    ' if cond else 'FAIL  ') + msg)


HELPERS = r"""()=>{
  window.__t112={
    pos:function(id){var o=window.__a3dObjSnapshot(id);return o?o.pos.slice():null;},
    ends:function(id){
      var o=window.__a3dObjSnapshot(id);
      if(!o||!o.bim||!o.bim.centerline)return null;
      var q=o.pos||[0,0,0];
      return o.bim.centerline.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
    },
    bounds:function(id){var b=window.__a3dWorldBounds([id]);return b?{mn:b.mn.slice(),mx:b.mx.slice()}:null;},
    count:function(){return window.__a3dState().objs;},
    walls:function(){return (window.__a3dLiveWalls()||[]).length;}
  };
  return true;}"""


def ext(b):
    return [b['mx'][k] - b['mn'][k] for k in range(3)]


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

        async def safe(js, arg=None):
            try:
                return await (page.evaluate(js, arg) if arg is not None else page.evaluate(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        has = await safe("()=>!!window.__acad3dV112")
        ck(bool(has), "__acad3dV112 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        await safe(HELPERS)

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def gizmo():
            return await safe("()=>window.__a3dGizmo()")

        async def rect():
            return await safe("()=>window.__a3dCanvasRect()")

        def arm(g, axis):
            for a in (g or {}).get('arms', []):
                if a['axis'] == axis:
                    return a
            return None

        def mid(a):
            return [(a['x0'] + a['x1']) / 2, (a['y0'] + a['y1']) / 2]

        async def press(p, mods=()):
            r = await rect()
            if not r or p is None:
                return False
            for m in mods:
                await page.keyboard.down(m)
            await page.mouse.move(r['left'] + p[0], r['top'] + p[1])
            await page.mouse.down()
            return True

        async def move_to(p, steps=8):
            r = await rect()
            await page.mouse.move(r['left'] + p[0], r['top'] + p[1], steps=steps)
            await page.wait_for_timeout(120)

        async def release(mods=()):
            await page.mouse.up()
            for m in mods:
                await page.keyboard.up(m)
            await page.wait_for_timeout(300)

        async def scene(js, view='plan', point=False, grid=False, ortho=False):
            await blur()
            out = await safe("(a)=>{window.__a3dTestSetObjs([]);var r=(" + js + ")();"
                             "if(a.view==='plan')window.__a3dSetPlanView();else window.__a3dSet3DView();"
                             "window.__a3dSnapSet({point:a.point,grid:a.grid,ortho:a.ortho,gridSize:0.5});"
                             "window.__a3dFit();return r;}",
                             {'view': view, 'point': point, 'grid': grid, 'ortho': ortho})
            await page.wait_for_timeout(500)
            return out

        TWO_WALLS = """function(){
          const a=window.__a3dWall([[0,4],[6,4]],0.3,3,'center',false);
          const b=window.__a3dWall([[10,4],[16,4]],0.3,3,'center',false);
          window.__a3dSelectFor([b]);
          return {a:a,b:b};}"""

        # ------------------------------------------------------------------------------
        print("\n-- 1. a drag lands on real geometry")
        for snap_on in (True, False):
            ids = await scene(TWO_WALLS, point=snap_on)
            g = await gizmo()
            ax = arm(g, 'x')
            if not (ids and ax):
                ck(False, "the two-wall scene and its X arrow are there (snap %s)" % snap_on)
                continue
            # aim about 4.15 m back along X: the end at x=10 is then a fifth of a metre short of
            # the end at x=6, which is well inside the snap threshold and nowhere near a whole
            # grid step of the position it starts from.
            m = mid(ax)
            await press(m)
            await move_to([m[0] + ax['sx'] * -4.15, m[1] + ax['sy'] * -4.15])
            live = await safe("()=>window.__a3dGizmoDrag()")
            await release()
            p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
            if snap_on:
                ck(p is not None and abs(p[0] + 4) < 1e-9 and abs(p[1]) < 1e-12 and abs(p[2]) < 1e-12,
                   "with POINT snap the wall end lands exactly on the other wall's end (%s)" %
                   [round(v, 6) for v in (p or [])])
                ck(live is not None and live['snapAt'] is not None
                   and abs(live['snapAt'][0] - 6) < 1e-9 and abs(live['snapAt'][2] - 4) < 1e-9,
                   "and the drag marks the point it caught (%s)" % (live and live['snapAt']))
            else:
                ck(p is not None and abs(p[0] + 4) > 1e-6 and abs(p[0] + 4.15) < 0.25,
                   "with it off the same drag stops where the cursor did, not on the point (%s)" %
                   [round(v, 4) for v in (p or [])])

        # An arrow moves along ONE axis. A point a few pixels off its line still pulls the drag to
        # where that line passes the point -- and never sideways to sit on it, which is what a
        # snap that ignored the handle's freedom would do.
        pxm0 = await safe("()=>{const a=window.__a3dProject([0,0,0]),b=window.__a3dProject([1,0,0]);"
                          "return Math.hypot(b.x-a.x,b.y-a.y);}")
        off = (8.0 / pxm0) if pxm0 else 0.3
        ids = await scene("""function(){
          const a=window.__a3dWall([[0,OFF],[6,OFF],0.3,3,'center',false);}""".replace('a=window', 'a=window')
                          .replace("[[0,OFF],[6,OFF],0.3,3,'center',false);}",
                                   "[[0,%(o)r],[6,%(o)r]],0.3,3,'center',false);\n          const b=window.__a3dWall([[10,4],[16,4]],0.3,3,'center',false);\n          window.__a3dSelectFor([b]);\n          return {a:a,b:b};}" % {'o': 4 - off}),
                          point=True)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax) if ax else None
        if m:
            await press(m)
            await move_to([m[0] + ax['sx'] * -4.15, m[1] + ax['sy'] * -4.15])
            await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(p is not None and abs(p[2]) < 1e-12 and abs(p[1]) < 1e-12 and abs(p[0] + 4) < 1e-9,
           "a point just off the axis pulls the drag along the axis to meet it, and never off the "
           "axis to reach it (%s)" % [round(v, 6) for v in (p or [])])

        # A short drag still moves: the thing being dragged is not its own snap target.
        ids = await scene(TWO_WALLS, point=True)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax) if ax else None
        if m:
            await press(m)
            await move_to([m[0] + ax['sx'] * 0.3, m[1] + ax['sy'] * 0.3])
            await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(p is not None and abs(p[0] - 0.3) < 0.06,
           "a short drag still moves: what is being dragged is not offered as its own snap "
           "target (%s)" % [round(v, 4) for v in (p or [])])

        # Far from everything, the cursor decides.
        ids = await scene(TWO_WALLS, point=True)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax) if ax else None
        if m:
            await press(m)
            await move_to([m[0] + ax['sx'] * -1.0, m[1] + ax['sy'] * -1.0])
            await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(p is not None and abs(p[0] + 1.0) < 0.06,
           "and a drag that ends nowhere near a point is left where the cursor put it (%s)" %
           [round(v, 4) for v in (p or [])])

        # Two points close enough that both are in reach: the nearer one wins.
        pxm = await safe("()=>{const a=window.__a3dProject([0,0,0]),b=window.__a3dProject([1,0,0]);"
                         "return Math.hypot(b.x-a.x,b.y-a.y);}")
        gap = (9.0 / pxm) if pxm else 0.15
        ids = await scene("""function(a){
          const w1=window.__a3dWall([[0,4],[6,4]],0.3,3,'center',false);
          const w2=window.__a3dWall([[6+a.gap,4],[9,4]],0.3,3,'center',false);
          const b=window.__a3dWall([[10,4],[16,4]],0.3,3,'center',false);
          window.__a3dSelectFor([b]);
          return {b:b,gap:a.gap};}""".replace('function(a){', 'function(){var a={gap:%r};' % gap),
                         point=True)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax) if ax else None
        if m:
            await press(m)
            # aim just past the nearer of the two ends, so both are within reach of the cursor
            # nearer to the second end than to the first, with both inside the threshold
            await move_to([m[0] + ax['sx'] * -(4 - gap * 0.7), m[1] + ax['sy'] * -(4 - gap * 0.7)])
            await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        near_target = -(4 - gap)
        ck(p is not None and abs(p[0] - near_target) < 1e-9,
           "with two points in reach it takes the nearer (%s, wanted %s)" %
           (p and round(p[0], 4), round(near_target, 4)))

        ids = await scene("""function(){
          const a=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          const b=window.__a3dWall([[9,5],[15,5]],0.3,3,'center',false);
          window.__a3dSelectFor([b]);
          return {a:a,b:b};}""", point=True)
        g = await gizmo()
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        if 'xz' in pl:
            c = pl['xz']['c']
            r = await rect()
            # where the moved end would have to go to sit on the other wall's end
            want = await safe("(a)=>{const p=window.__a3dProject([a[0],0,a[1]]);return [p.x,p.y];}", [6, 0])
            hereP = await safe("(a)=>{const p=window.__a3dProject([a[0],0,a[1]]);return [p.x,p.y];}", [9, 5])
            await press(c)
            await move_to([c[0] + (want[0] - hereP[0]) * 0.97, c[1] + (want[1] - hereP[1]) * 0.97])
            await release()
            p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
            ck(p is not None and abs(p[0] + 3) < 1e-9 and abs(p[2] + 5) < 1e-9,
               "a plane square snaps in both of its directions at once (%s)" % [round(v, 6) for v in (p or [])])
        else:
            ck(False, "the plan square is there to drag")

        # ------------------------------------------------------------------------------
        print("\n-- 2. typing an exact value")
        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m)
        await move_to([m[0] + ax['sx'] * 1.2, m[1] + ax['sy'] * 1.2])
        await page.keyboard.type('3.5')
        typing = await safe("()=>window.__a3dGizmoDrag()")
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        after = await safe("()=>window.__a3dGizmoDrag()")
        await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(typing is not None and typing['typing'] == '3.5',
           "the digits typed during a drag are held and shown (%s)" % (typing and typing['typing']))
        ck(p is not None and abs(p[0] - 3.5) < 1e-12 and after is None,
           "Enter moves it exactly 3.5 m and the drag is over (%s)" % [round(v, 6) for v in (p or [])])

        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m)
        await move_to([m[0] - ax['sx'] * 1.2, m[1] - ax['sy'] * 1.2])
        await page.keyboard.type('2')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        await release()
        p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(p is not None and abs(p[0] + 2) < 1e-12,
           "the gesture decides the direction and the number only the distance: dragged back, "
           "typing 2 moves it 2 m back (%s)" % [round(v, 6) for v in (p or [])])

        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m)
        await move_to([m[0] + ax['sx'] * 1.2, m[1] + ax['sy'] * 1.2])
        await page.keyboard.type('47')
        await page.keyboard.press('Backspace')
        await page.keyboard.press('Backspace')
        mid_state = await safe("()=>window.__a3dGizmoDrag()")
        await release()
        ck(mid_state is not None and mid_state['typing'] is None,
           "Backspace clears it back to the drag (%s)" % (mid_state and mid_state['typing']))

        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        before = await safe("(id)=>window.__t112.ends(id)", ids['b'])
        rp = [await safe("(d)=>window.__a3dGizmoRingPoint(d)", d) for d in (20, 35)]
        if rp[0] and rp[1] and before:
            await press(rp[0])
            await move_to(rp[1])
            await page.keyboard.type('30')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(250)
            await release()
            aft = await safe("(id)=>window.__t112.ends(id)", ids['b'])
            O = g['origin']
            want = []
            t = math.radians(30)
            for p0 in before:
                dx, dz = p0[0] - O[0], p0[1] - O[2]
                # Revit's sense: counter-clockwise seen from above, which is -t in the model
                want.append([O[0] + dx * math.cos(-t) - dz * math.sin(-t),
                             O[2] + dx * math.sin(-t) + dz * math.cos(-t)])
            err = max(max(abs(aft[i][k] - want[i][k]) for k in (0, 1)) for i in range(len(want))) \
                if aft and len(aft) == len(want) else 1e9
            ck(err < 1e-9, "typing 30 on the rotate ring turns it exactly 30 degrees the way the "
                           "read-out counts them (error %.2e)" % err)
        else:
            ck(False, "the rotate ring is there to type on")

        box = await scene("""function(){var o=window.__a3dAdd('box',{Length:10,Width:6,Height:8});
          window.__a3dSelectFor([o.id]);return o.id;}""", view='3d')
        g = await gizmo()
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        b0 = await safe("(id)=>window.__t112.bounds(id)", box)
        if 'x' in sc:
            await press([sc['x']['x'], sc['x']['y']])
            await move_to([sc['x']['x'] + 10, sc['x']['y'] + 6])
            await page.keyboard.type('2')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(250)
            await release()
            b1 = await safe("(id)=>window.__t112.bounds(id)", box)
            e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([1, 1, 1], [0, 0, 0])
            ck(abs(e1[0] - 2 * e0[0]) < 1e-9 and abs(e1[1] - e0[1]) < 1e-9,
               "typing 2 on a scale box doubles that axis and leaves the others (%s -> %s)" %
               ([round(v, 3) for v in e0], [round(v, 3) for v in e1]))
        else:
            ck(False, "a scale box is there to type on")

        ids = await scene("""function(){
          const w=window.__a3dWall([[0,0],[9,0],[9,6],[0,6]],0.3,3,'center',true);
          const r=window.__a3dCreateRoomAt([4.5,3],0);
          window.__a3dSelectFor([w]);
          return {w:w,r:r};}""", point=False)
        r0 = await safe("(id)=>window.__a3dObjSnapshot(id).pts", ids['r'])
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m)
        await move_to([m[0] + ax['sx'] * 1.0, m[1] + ax['sy'] * 1.0])
        await page.keyboard.type('4')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(350)
        await release()
        r1 = await safe("(id)=>window.__a3dObjSnapshot(id).pts", ids['r'])
        shifted = (r0 and r1 and len(r0) == len(r1)
                   and all(abs((r1[i][0] - r0[i][0]) - 4) < 1e-6 and abs(r1[i][1] - r0[i][1]) < 1e-6
                           for i in range(len(r0))))
        ck(shifted, "a typed move carries what depends on the objects with it, exactly as the "
                    "mouse does -- one end-of-drag path (room moved %s)" %
           (r0 and r1 and [round(r1[0][0] - r0[0][0], 4), round(r1[0][1] - r0[0][1], 4)]))

        # ------------------------------------------------------------------------------
        print("\n-- 3. Escape puts it back")
        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        p0 = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        await press(m)
        await move_to([m[0] + ax['sx'] * 3, m[1] + ax['sy'] * 3])
        moved = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        cancelled = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        live = await safe("()=>window.__a3dGizmoDrag()")
        await release()
        settled = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        ck(moved and abs(moved[0] - p0[0]) > 1 and cancelled == p0 and live is None and settled == p0,
           "a move cancels back to where it started, and the release afterwards changes nothing "
           "(%s -> %s -> %s)" % (p0, [round(v, 2) for v in (moved or [])], cancelled))

        box = await scene("""function(){var o=window.__a3dAdd('box',{Length:10,Width:6,Height:8});
          window.__a3dSelectFor([o.id]);return o.id;}""", view='3d')
        g = await gizmo()
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        b0 = await safe("(id)=>window.__t112.bounds(id)", box)
        t0 = await safe("(id)=>{var o=window.__a3dObjSnapshot(id);return {t:o.t,prm:!!o.prm};}", box)
        if 'x' in sc:
            await press([sc['x']['x'], sc['x']['y']])
            await move_to([sc['x']['x'] + (sc['x']['x'] - g['ox']) * 0.4,
                           sc['x']['y'] + (sc['x']['y'] - g['oy']) * 0.4])
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(200)
            await release()
            b1 = await safe("(id)=>window.__t112.bounds(id)", box)
            t1 = await safe("(id)=>{var o=window.__a3dObjSnapshot(id);return {t:o.t,prm:!!o.prm};}", box)
            ck(b0 and b1 and max(abs(ext(b1)[k] - ext(b0)[k]) for k in range(3)) < 1e-12 and t1 == t0,
               "a scale cancels back to the shape AND the type it started as (%s, %s)" %
               (t1, [round(v, 4) for v in ext(b1 or b0)]))
        else:
            ck(False, "a scale box is there to cancel")

        # ------------------------------------------------------------------------------
        print("\n-- 4. Ctrl leaves a copy")
        ids = await scene(TWO_WALLS, point=False)
        n0 = await safe("()=>window.__t112.walls()")
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m, mods=['Control'])
        await move_to([m[0] + ax['sx'] * 4, m[1] + ax['sy'] * 4])
        live = await safe("()=>window.__a3dGizmoDrag()")
        await release(mods=['Control'])
        n1 = await safe("()=>window.__t112.walls()")
        orig = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        newid = (live or {}).get('copies') or []
        cpos = await safe("(id)=>window.__t112.pos(id)", newid[0]) if newid else None
        sel = await safe("()=>window.__a3dState().sel")
        ck(n1 == n0 + 1 and orig and abs(orig[0]) < 1e-12 and cpos and abs(cpos[0] - 4) < 0.35
           and sel == newid[0],
           "Ctrl-dragging an arrow leaves the original where it was and moves a new copy, which "
           "is what is selected afterwards (%s walls, original %s, copy %s)" %
           (n1, orig and round(orig[0], 4), cpos and round(cpos[0], 3)))
        await safe("()=>window.__a3dUndo()")
        await page.wait_for_timeout(300)
        n2 = await safe("()=>window.__t112.walls()")
        ck(n2 == n0, "and one undo takes the copy away again (%s -> %s)" % (n1, n2))

        ids = await scene(TWO_WALLS, point=False)
        n0 = await safe("()=>window.__t112.walls()")
        g = await gizmo()
        ax = arm(g, 'x')
        m = mid(ax)
        await press(m, mods=['Control'])
        await move_to([m[0] + ax['sx'] * 3, m[1] + ax['sy'] * 3])
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        await release(mods=['Control'])
        n3 = await safe("()=>window.__t112.walls()")
        sel = await safe("()=>window.__a3dState().sel")
        ck(n3 == n0 and sel == ids['b'],
           "Escape during a Ctrl-drag takes the copy away and gives the selection back (%s walls, "
           "selection %s)" % (n3, sel == ids['b']))

        # ------------------------------------------------------------------------------
        print("\n-- 5. Shift is precision")
        dists = {}
        for fine in (False, True):
            ids = await scene(TWO_WALLS, point=False)
            g = await gizmo()
            ax = arm(g, 'x')
            m = mid(ax)
            await press(m, mods=['Shift'] if fine else ())
            await move_to([m[0] + ax['sx'] * 4, m[1] + ax['sy'] * 4])
            await release(mods=['Shift'] if fine else ())
            p = await safe("(id)=>window.__t112.pos(id)", ids['b'])
            dists[fine] = p[0] if p else 0
        ck(abs(dists[False]) > 1 and abs(dists[True] / dists[False] - 0.25) < 1e-9,
           "the same cursor travel with Shift moves exactly a quarter as far (%s vs %s)" %
           (round(dists[True], 4), round(dists[False], 4)))

        # ------------------------------------------------------------------------------
        print("\n-- 6. the pivot")
        ids = await scene(TWO_WALLS, point=False)
        g = await gizmo()
        c = [g['centre']['x'], g['centre']['y']]
        p0 = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        await press(c, mods=['Alt'])
        await move_to([c[0] - 90, c[1] + 40])
        await release(mods=['Alt'])
        st = await safe("()=>window.__a3dGizmoState()")
        p1 = await safe("(id)=>window.__t112.pos(id)", ids['b'])
        g2 = await gizmo()
        piv = st and st['pivot']
        ck(piv is not None and p1 == p0 and g2 and
           max(abs(g2['origin'][k] - piv[k]) for k in range(3)) < 1e-9,
           "Alt on the centre square moves the gizmo and not the model, and every handle follows "
           "it (%s)" % (piv and [round(v, 3) for v in piv]))
        before = await safe("(id)=>window.__t112.ends(id)", ids['b'])
        rp = [await safe("(d)=>window.__a3dGizmoRingPoint(d)", d) for d in (20, 50, 80, 110)]
        if before and all(rp) and piv:
            await press(rp[0])
            for q in rp[1:]:
                await move_to(q, steps=6)
            await release()
            aft = await safe("(id)=>window.__t112.ends(id)", ids['b'])
            radii0 = [math.hypot(p[0] - piv[0], p[1] - piv[2]) for p in before]
            radii1 = [math.hypot(p[0] - piv[0], p[1] - piv[2]) for p in (aft or [])]
            turned = abs(math.degrees(math.atan2(aft[1][1] - aft[0][1], aft[1][0] - aft[0][0]))) if aft else 0
            ck(len(radii1) == len(radii0)
               and max(abs(radii1[i] - radii0[i]) for i in range(len(radii0))) < 1e-6 and turned > 30,
               "and the rotate ring then turns the wall about the PIVOT, keeping every distance to "
               "it (%s -> %s)" % ([round(v, 3) for v in radii0], [round(v, 3) for v in radii1]))
        else:
            ck(False, "the ring is there to turn about the pivot")
        r = await rect()
        await page.mouse.move(r['left'] + c[0], r['top'] + c[1])
        await page.mouse.down(button='right')
        await page.mouse.up(button='right')
        await page.wait_for_timeout(250)
        st = await safe("()=>window.__a3dGizmoState()")
        acts = [b['act'] for b in ((st or {}).get('menu') or [])]
        ck('pivot' in acts, "the gizmo menu offers Reset Pivot while a pivot is set (%s)" % acts)
        try:
            await page.click('#a3d-gizmenu [data-a3dgiz="pivot"]', timeout=2000)
        except Exception as e:
            print('      (menu click failed: %s)' % str(e)[:100])
        await page.wait_for_timeout(250)
        st = await safe("()=>window.__a3dGizmoState()")
        g3 = await gizmo()
        ck(st and st['pivot'] is None and g3 is not None,
           "and clicking it puts the gizmo back on the selection (%s)" % (st and st['pivot']))
        g4 = await gizmo()
        if g4:
            await page.mouse.move(r['left'] + g4['centre']['x'], r['top'] + g4['centre']['y'])
            await page.mouse.down(button='right')
            await page.mouse.up(button='right')
            await page.wait_for_timeout(250)
        st2 = await safe("()=>window.__a3dGizmoState()")
        acts2 = [b['act'] for b in ((st2 or {}).get('menu') or [])]
        ck(len(acts2) >= 4 and 'pivot' not in acts2,
           "with no pivot set the menu does not offer to reset one (%s)" % acts2)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        g = await gizmo()
        c = [g['centre']['x'], g['centre']['y']]
        await press(c, mods=['Alt'])
        await move_to([c[0] - 60, c[1] - 30])
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        await release(mods=['Alt'])
        st = await safe("()=>window.__a3dGizmoState()")
        ck(st and st['pivot'] is None,
           "Escape during a pivot drag leaves the pivot as it was (%s)" % (st and st['pivot']))

        ck(not errs, "no page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
