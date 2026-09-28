#!/usr/bin/env python3
"""bim_phase123_direct_manipulation_browser_tests.py -- V123: taking hold of the model.

The owner: "geometry manipulation for objects, shapes and assets ... quite limited for my push,
pull, rotate when I click on these kinds of objects, even though we have the gizmo." V123 studied
Rhino's gumball, AutoCAD's PRESSPULL and grips, Revit's shape handles and temporary dimensions and
SketchUp's Push/Pull, and built what they share.

Every claim is driven with real pointer and key events and asserted on the MODEL -- positions,
parameters, centerlines, types, undo depth -- never on how the screen looks.

  1. UNITS: a length is read out and typed in the project's unit -- in a millimetre project 500 is
     half a metre -- on the gizmo, and in the coordinates typed while drawing. Two and three
     numbers are typed on the squares.
  2. CLICK TO TYPE: a click on a handle opens its value box and changes nothing -- no undo step --
     and a Ctrl+click makes no copy. The box moves, turns and scales exactly; Escape and a bad
     number change nothing. A Ctrl+drag still copies. The status bar says what a handle does.
  3. THE BODY DRAG is the gizmo's move: one undo step (on V122 Ctrl+Z after it deleted the object),
     snapping to points and the grid, typed X,Y, Escape, Alt to lift in 3D, groups.
  4. WHAT A REBUILD KEEPS: a wall's type through Properties and grips; copies of moved elements
     land where the original is and keep their types; a turned floor keeps its turn; a floor
     mirrors; Pad and Pocket work on a sketch where it is.
  5. FACES: taken by double-click, Ctrl+Shift+click and PRESSPULL; Tab and Shift+Tab step, Escape
     lets go; in a plan an outline takes the side seen edge-on; each kind of object says which of
     its faces move and why the others do not; a sketch on a solid is taken before the solid.
  6. PUSH AND PULL: a box's face moves alone and the box stays parametric; a cylinder's side is its
     radius; a wall's top and end; a column's top snaps to a level; a face snaps to a point the
     cursor is on and to grid steps; Shift is fine; typed distances; Escape gives the undo step
     back; the value box takes a size; the range stops a push exactly; a sketch becomes a pad, up
     or down, and a sketch on a solid refuses to be pushed into it.
  7. PROPERTIES shows a primitive's sizes in the project's unit and a changed height keeps the base;
     Push/Pull is on the toolbar.

The harness never waits without a bound: every page step has STALL seconds, and a page that stops
answering, or a suite that stops at an exception, is reported as a FAIL with where it stopped --
not as a hang the falsify runner can only time out, nor a crash that prints no RESULT line.
"""
import asyncio, math, pathlib, sys, traceback
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
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60   # seconds: no single step of this suite takes more than a few


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


HELPERS = r"""()=>{
  window.__t123={
    obj:function(id){return window.__a3dObjSnapshot(id);},
    pos:function(id){var o=window.__a3dObjSnapshot(id);return o?o.pos.slice():null;},
    b:function(id){var b=window.__a3dWorldBounds([id]);return b?{mn:b.mn.slice(),mx:b.mx.slice()}:null;},
    n:function(){return window.__a3dState().objs.length;},
    ids:function(){return window.__a3dState().objs.map(function(o){return o.id;});},
    undo:function(){return window.__a3dDocs.undoDepth().undo;},
    p:function(P){var s=window.__a3dProject(P);return [s.x,s.y];},
    sel:function(){return window.__a3dState().sel;},
    /* how many of an object's faces a line crosses, from P along D -- a door cut through a wall is
       a line through it that meets nothing; the solid above the door is two faces */
    cross:function(id,P,D){
      var o=window.__a3dObjSnapshot(id);if(!o||!o.mesh)return null;
      var q=o.pos||[0,0,0],m=o.mesh,n=0,i,k;
      for(i=0;i<m.f.length;i++){
        var pts=m.f[i].map(function(ix){var v=m.v[ix];return [v[0]+q[0],v[1]+q[1],v[2]+q[2]];});
        var N=[0,0,0];
        for(k=0;k<pts.length;k++){var a=pts[k],b=pts[(k+1)%pts.length];
          N[0]+=(a[1]-b[1])*(a[2]+b[2]);N[1]+=(a[2]-b[2])*(a[0]+b[0]);N[2]+=(a[0]-b[0])*(a[1]+b[1]);}
        var dn=N[0]*D[0]+N[1]*D[1]+N[2]*D[2];
        if(Math.abs(dn)<1e-12)continue;
        var t=((pts[0][0]-P[0])*N[0]+(pts[0][1]-P[1])*N[1]+(pts[0][2]-P[2])*N[2])/dn;
        if(t<0)continue;
        var X=[P[0]+D[0]*t,P[1]+D[1]*t,P[2]+D[2]*t];
        var ax=Math.abs(N[0]),ay=Math.abs(N[1]),az=Math.abs(N[2]),u,w,ins=false,j;
        if(ax>=ay&&ax>=az){u=1;w=2;}else if(ay>=az){u=0;w=2;}else{u=0;w=1;}
        for(k=0,j=pts.length-1;k<pts.length;j=k++){
          if(((pts[k][w]>X[w])!==(pts[j][w]>X[w]))&&(X[u]<(pts[j][u]-pts[k][u])*(X[w]-pts[k][w])/(pts[j][w]-pts[k][w])+pts[k][u]))ins=!ins;
        }
        if(ins)n++;
      }
      return n;
    }
  };
  return true;}"""


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


def mid(a):
    if not a:
        return None
    return [(a['x0'] + a['x1']) / 2, (a['y0'] + a['y1']) / 2]


def along(a, d):
    """the screen point d world units along an arrow from its base: the drag's own contract"""
    return [a['x0'] + a['sx'] * d, a['y0'] + a['sy'] * d]


def ahead(a, s0, d):
    """the screen point d world units further along the arrow from s0"""
    return [s0[0] + a['sx'] * d, s0[1] + a['sy'] * d]


def expect_dist(a, p0, p1, fine=1.0):
    dx, dy = (p1[0] - p0[0]) * fine, (p1[1] - p0[1]) * fine
    return (dx * a['sx'] + dy * a['sy']) / (a['sx'] ** 2 + a['sy'] ** 2)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
            """every key and pointer step answers within STALL seconds, or the suite says where it stopped"""
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV123")
        ck(bool(has), "__acad3dV123 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        await safe(HELPERS)

        async def rect():
            return await safe("()=>window.__a3dCanvasRect()")

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def align(p):
            """the canvas point the browser will actually deliver: it truncates to whole pixels, so a
            drag is aimed at points that are whole pixels already and the expectation uses them"""
            if p is None:
                return None
            r = await rect()
            return [round(r['left'] + p[0]) - r['left'], round(r['top'] + p[1]) - r['top']]

        async def body_pt(oid, cands):
            """a point on the object that is not on any gizmo handle"""
            for P in cands:
                q = await align(await safe("(P)=>window.__t123.p(P)", P))
                hit = await safe("(q)=>({g:window.__a3dGizmoAt(q[0],q[1]),o:window.__a3dPick(q[0],q[1])})", q)
                if hit and hit['g'] is None and hit['o'] == oid:
                    return q
            return None

        async def press(p, mods=()):
            if p is None:
                return
            r = await rect()
            for m in mods:
                await page.keyboard.down(m)
            await page.mouse.move(r['left'] + p[0], r['top'] + p[1])
            await page.mouse.down()

        async def move_to(p, steps=10):
            if p is None:
                return
            r = await rect()
            await page.mouse.move(r['left'] + p[0], r['top'] + p[1], steps=steps)
            await page.wait_for_timeout(80)

        async def release(mods=()):
            await page.mouse.up()
            for m in mods:
                await page.keyboard.up(m)
            await page.wait_for_timeout(250)

        async def drag(p0, p1, steps=10, mods=()):
            if p0 is None or p1 is None:
                return
            await press(p0, mods)
            await move_to(p1, steps)
            await release(mods)

        async def click(p, mods=(), wait=250):
            if p is None:
                return
            r = await rect()
            for m in mods:
                await page.keyboard.down(m)
            await page.mouse.click(r['left'] + p[0], r['top'] + p[1])
            for m in mods:
                await page.keyboard.up(m)
            await page.wait_for_timeout(wait)

        async def dbl(p):
            if p is None:
                return
            r = await rect()
            await page.mouse.dblclick(r['left'] + p[0], r['top'] + p[1])
            await page.wait_for_timeout(420)

        async def proj(P):
            return await safe("(P)=>window.__t123.p(P)", P)

        async def gizmo():
            return await safe("()=>window.__a3dGizmo()")

        async def face():
            return await safe("()=>window.__a3dFace()")

        async def vbox(wait=700):
            t = 0
            while t < wait:
                b = await safe("()=>window.__a3dValueBox()")
                if b:
                    return b
                await page.wait_for_timeout(50)
                t += 50
            return await safe("()=>window.__a3dValueBox()")

        async def undo():
            return await safe("()=>window.__t123.undo()")

        async def scene(js, view='3d', point=False, grid=False, gridSize=0.5, units='m'):
            await safe("()=>{var b=document.getElementById('a3d-valbox');if(b){var i=b.querySelector('input');if(i)i.blur();}}")
            await blur()
            out = await safe("(a)=>{window.__a3dSetUnits(a.units);window.__a3dTestSetObjs([]);window.__a3dTestClearUndo();var r=(" + js + ")();"
                             "if(a.view==='plan')window.__a3dSetPlanView();else window.__a3dSet3DView();"
                             "window.__a3dSnapSet({point:a.point,grid:a.grid,ortho:false});"
                             "window.__a3dSnapSize&&window.__a3dSnapSize(a.gridSize);"
                             "window.__a3dFit();return r;}",
                             {'view': view, 'point': point, 'grid': grid, 'gridSize': gridSize, 'units': units})
            await page.wait_for_timeout(450)
            return out

        def arm(g, axis):
            for a in (g or {}).get('arms', []):
                if a['axis'] == axis:
                    return a
            return None

        BOX = "function(){const o=window.__a3dAdd('box',{});window.__a3dSelectFor([o.id]);return o.id;}"

        # ==============================================================================
        print("\n-- 1. lengths in the project's unit")
        box = await scene(BOX, units='mm')
        g = await gizmo()
        ax = arm(g, 'x')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        if ax:
            m = mid(ax)
            await press(m)
            await move_to([m[0] + ax['sx'] * 0.8, m[1] + ax['sy'] * 0.8])
            await page.keyboard.type('500')
            dr = await safe("()=>window.__a3dGizmoDrag()")
            ck(dr is not None and 'mm' in (dr.get('readout') or '') and '500_' in (dr.get('readout') or ''),
               "typing on an arrow reads out in millimetres in a millimetre project (%r)" % (dr and dr.get('readout')))
            await page.keyboard.press('Enter')
            await release()
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p0 and p1 and near(p1[0] - p0[0], 0.5, 1e-9) and near(p1[2], p0[2], 1e-9),
           "and 500 typed is half a metre along X, exactly (moved %s; on V122 it was 500 m)" %
           (p0 and p1 and round(p1[0] - p0[0], 6)))

        # a face's size reads out in the project's unit, through the one length formatter
        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}", units='mm')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        f = await face()
        ck(f is not None and f['text'] == 'TOP  HEIGHT 3500 mm',
           "a face's size reads out in millimetres too (%r)" % (f and f['text']))

        # a plane square takes two numbers, in the project's unit, along its own two axes
        box = await scene(BOX, view='plan', units='mm')
        g = await gizmo()
        pl = [p for p in (g or {}).get('planes', []) if p['k'] == 'xz']
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        if pl:
            c = pl[0]['c']
            await press(c)
            await move_to([c[0] + 30, c[1] + 10])
            await page.keyboard.type('1000,2000')
            await page.keyboard.press('Enter')
            await release()
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(bool(pl) and p0 and p1 and near(p1[0] - p0[0], 1.0, 1e-9) and near(p1[2] - p0[2], -2.0, 1e-9),
           "the XY square takes X,Y: 1000,2000 moves 1 m east and 2 m north (%s)" %
           (p0 and p1 and [round(p1[k] - p0[k], 6) for k in range(3)]))

        # the free-move square in 3D takes X,Y,Z along the gizmo's frame
        box = await scene(BOX, units='m')
        g = await gizmo()
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        if g:
            c = [g['centre']['x'], g['centre']['y']]
            await press(c)
            await move_to([c[0] + 25, c[1] + 15])
            await page.keyboard.type('1,2,3')
            await page.keyboard.press('Enter')
            await release()
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p0 and p1 and near(p1[0] - p0[0], 1, 1e-9) and near(p1[1] - p0[1], 3, 1e-9) and near(p1[2] - p0[2], -2, 1e-9),
           "the free-move square in 3D takes X,Y,Z: 1,2,3 is 1 east, 2 north, 3 up (%s)" %
           (p0 and p1 and [round(p1[k] - p0[k], 6) for k in range(3)]))

        # coordinates typed while drawing are in the project's unit too
        await scene("function(){return null;}", view='plan', units='mm')
        await safe("()=>window.__a3dRunCmd('poly')")
        await page.wait_for_timeout(150)
        for s in ('0,0', '3000,0', '3000,2000'):
            await page.keyboard.type(s)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(120)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        pts = await safe("()=>{var id=window.__t123.sel();var o=id?window.__a3dObjSnapshot(id):null;return o&&o.pts?o.pts:null;}")
        ck(pts is not None and len(pts) == 3 and near(pts[1][0], 3) and near(pts[2][1], 2),
           "a polyline typed as 0,0 / 3000,0 / 3000,2000 in millimetres is 3 m by 2 m (%s)" % pts)
        await safe("()=>window.__a3dSetUnits('m')")

        # ==============================================================================
        print("\n-- 2. a click on a handle asks for a value, and changes nothing")
        box = await scene(BOX)
        g = await gizmo()
        ax = arm(g, 'x')
        u0, n0 = await undo(), await safe("()=>window.__t123.n()")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        # when the box appears, measured in the page from the release -- a suite slowed by a loaded
        # machine reads the box later, never sooner, so the delay is timed where it happens
        await safe("""()=>{var t=window.__t123;t.tUp=null;t.tBox=null;
          window.addEventListener('mouseup',function h(){t.tUp=performance.now();window.removeEventListener('mouseup',h,true);},true);
          var mo=new MutationObserver(function(){if(t.tBox===null&&document.getElementById('a3d-valbox')){t.tBox=performance.now();mo.disconnect();}});
          mo.observe(document.body,{childList:true,subtree:true});return true;}""")
        await click(mid(ax), wait=30)
        u1, n1 = await undo(), await safe("()=>window.__t123.n()")
        vb = await vbox(wait=2500)
        wait_ms = await safe("()=>{var t=window.__t123;return (t.tUp!==null&&t.tBox!==null)?t.tBox-t.tUp:null;}")
        ck(u1 == u0 and n1 == n0, "a click on the X arrow adds no undo step and nothing else (%s->%s, %s->%s)" % (u0, u1, n0, n1))
        ck(wait_ms is not None and wait_ms >= 250 and vb is not None and vb['label'] == 'Move X' and vb['focused'],
           "its value box opens once a double-click could not be under way (%s ms after the release), as "
           "'Move X', ready to type (%s)" % (wait_ms is not None and round(wait_ms), vb))
        await page.keyboard.type('2.5')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p0 and p1 and near(p1[0] - p0[0], 2.5, 1e-9) and await undo() == u0 + 1
           and await safe("()=>window.__a3dValueBox()") is None,
           "2.5 and Enter move it 2.5 along X exactly, as one undo step, and close the box (%s)" %
           (p0 and p1 and round(p1[0] - p0[0], 6)))

        g = await gizmo()
        ax = arm(g, 'x')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        u0 = await undo()
        await click(mid(ax), wait=30)
        await vbox()
        await page.keyboard.type('7')
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(await safe("()=>window.__a3dValueBox()") is None and p1 == p0 and await undo() == u0,
           "Escape closes the box with nothing changed")
        await click(mid(ax), wait=30)
        await vbox()
        await page.keyboard.type('abc')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        vb = await safe("()=>window.__a3dValueBox()")
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(vb is not None and 'number' in (vb.get('error') or '').lower() and p1 == p0,
           "a value that is not a number is refused in the box, which stays open (%r)" % (vb and vb.get('error')))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        g = await gizmo()
        ax = arm(g, 'x')
        u0, n0 = await undo(), await safe("()=>window.__t123.n()")
        await click(mid(ax), mods=('Control',), wait=500)
        ck(await safe("()=>window.__t123.n()") == n0 and await undo() == u0 and await safe("()=>window.__a3dValueBox()") is None,
           "a Ctrl+click on an arrow makes no copy, no undo step and no box (V122 left a copy on top)")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        m = mid(ax)
        if m:
            await drag(m, [m[0] + ax['sx'] * 1.2, m[1] + ax['sy'] * 1.2], mods=('Control',))
        ids = await safe("()=>window.__t123.ids()")
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        other = [i for i in (ids or []) if i != box]
        pc = await safe("(id)=>window.__t123.pos(id)", other[0]) if other else None
        ck(len(ids or []) == 2 and p1 == p0 and pc and pc[0] > p0[0] + 0.5 and await undo() == u0 + 1,
           "a Ctrl+drag still copies: the original stays, the copy moves, one undo step (%s)" % (pc and round(pc[0] - p0[0], 3)))

        # a ring takes an angle
        wall = await scene("function(){const w=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);window.__a3dSelectFor([w]);return w;}")
        u0 = await undo()
        rp = await safe("()=>window.__a3dGizmoArcPoint('y',40)")
        if rp:
            await click(rp, wait=30)
        vb = await vbox()
        ck(vb is not None and vb['label'] == 'Rotate Z', "a click on the ring asks for an angle (%s)" % (vb and vb['label']))
        await page.keyboard.type('90')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(300)
        w = await safe("(id)=>{var o=window.__a3dObjSnapshot(id);var q=o.pos||[0,0,0];return o.bim.centerline.map(p=>[p[0]+q[0],p[1]+q[2]]);}", wall)
        ck(w is not None and near(w[0][0], 3, 1e-6) and near(w[0][1], 3, 1e-6) and near(w[1][1], -3, 1e-6)
           and await undo() == u0 + 1,
           "90 turns the wall a quarter counter-clockwise seen from above, one undo step (ends %s)" %
           (w and [[round(v, 4) for v in p] for p in w]))

        # a scale box takes a factor
        box = await scene(BOX)
        g = await gizmo()
        sx = [s for s in (g or {}).get('scales', []) if s['axis'] == 'x']
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        if sx:
            await click([sx[0]['x'], sx[0]['y']], wait=30)
        vb = await vbox()
        ck(vb is not None and vb['label'] == 'Scale X', "a click on the X scale box asks for a factor (%s)" % (vb and vb['label']))
        await page.keyboard.type('2')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(300)
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(b0 and b1 and near(b1['mx'][0] - b1['mn'][0], 2 * (b0['mx'][0] - b0['mn'][0]), 1e-6)
           and near(b1['mx'][1] - b1['mn'][1], b0['mx'][1] - b0['mn'][1], 1e-6),
           "2 doubles its X extent and leaves its height (%s -> %s)" %
           (b0 and round(b0['mx'][0] - b0['mn'][0], 4), b1 and round(b1['mx'][0] - b1['mn'][0], 4)))

        # the status bar says what a handle does
        box = await scene(BOX)
        g = await gizmo()
        ax = arm(g, 'x')
        await move_to(mid(ax), steps=4)
        await page.wait_for_timeout(150)
        hint = await safe("()=>window.__a3dStatusHint()")
        ck(hint is not None and 'click to type a distance' in hint and 'Ctrl+drag copies' in hint,
           "over an arrow the status bar says drag, click to type, Ctrl+drag copies (%r)" % hint)

        # ==============================================================================
        print("\n-- 3. dragging an object by its body is the gizmo's move")
        box = await scene(BOX, view='plan')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        n0, u0 = await safe("()=>window.__t123.n()"), await undo()
        c = await proj([p0[0] + 1.3, p0[1], p0[2] + 1.3])
        await drag(c, [c[0] + 110, c[1]])
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p1 and p1[0] > p0[0] + 0.5 and await undo() == u0 + 1,
           "a body drag moves it, as one undo step (moved %s)" % (p1 and round(p1[0] - p0[0], 3)))
        await safe("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        p2 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p2 == p0 and await safe("()=>window.__t123.n()") == n0,
           "and Ctrl+Z puts it back where it was -- the object is still there (on V122 the undo deleted it)")

        TWO = """function(){
          const a=window.__a3dWall([[0,4],[6,4]],0.3,3,'center',false);
          const b=window.__a3dWall([[10,4],[16,4]],0.3,3,'center',false);
          window.__a3dSelectFor([b]);return {a:a,b:b};}"""
        # pressed on the wall away from every handle: at its centre the press is the gizmo's
        # free-move square, which snaps on its own, and the body drag would go untested
        BODY_B = [[11.2, 0, 4.05], [14.8, 0, 4.05], [11.6, 0, 3.97], [14.4, 0, 3.97], [12.2, 0, 4.1]]
        ws = await scene(TWO, view='plan', point=True)
        s0 = await body_pt(ws['b'], BODY_B)
        d0, d1 = await proj([10, 0, 4]), await proj([6.1, 0, 4])
        s1 = [s0[0] + d1[0] - d0[0], s0[1] + d1[1] - d0[1]] if s0 else None
        await drag(s0, s1, steps=14)
        e = await safe("(id)=>{var o=window.__a3dObjSnapshot(id),q=o.pos||[0,0,0];return o.bim.centerline.map(p=>[p[0]+q[0],p[1]+q[2]]);}", ws['b'])
        ck(s0 is not None and e is not None and near(e[0][0], 6, 1e-9) and near(e[0][1], 4, 1e-9),
           "with object snap on, the wall dragged by its body lands its end exactly on the other's (%s)" % e)
        ws = await scene(TWO, view='plan', point=False, grid=True)
        await safe("()=>{window.__a3dSnapSet({grid:true});}")
        p0 = await safe("(id)=>window.__t123.pos(id)", ws['b'])
        s0 = await body_pt(ws['b'], BODY_B)
        d0, d1 = await proj([13, 0, 4]), await proj([11.63, 0, 4])
        s1 = [s0[0] + d1[0] - d0[0], s0[1] + d1[1] - d0[1]] if s0 else None
        await drag(s0, s1)
        p1 = await safe("(id)=>window.__t123.pos(id)", ws['b'])
        gs = await safe("()=>window.__a3dSnapState().gridSize||0.5")
        dxg = (p1[0] - p0[0]) if (p0 and p1) else None
        ck(s0 is not None and dxg is not None and abs(dxg) > 0.2 and near(dxg / gs, round(dxg / gs), 1e-9),
           "with grid snap on, the body drag moves it in whole grid steps (%s of %s)" % (dxg, gs))

        box = await scene(BOX, view='plan')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        u0 = await undo()
        c = await proj([p0[0] + 1.3, p0[1], p0[2] + 1.3])
        await press(c)
        await move_to([c[0] + 80, c[1] + 20])
        await page.keyboard.press('Escape')
        await release()
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p1 == p0, "Escape during a body drag puts it back")
        await press(c)
        await move_to([c[0] + 60, c[1]])
        await page.keyboard.type('3,0')
        await page.keyboard.press('Enter')
        await release()
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p0 and p1 and near(p1[0] - p0[0], 3, 1e-9) and near(p1[2] - p0[2], 0, 1e-9),
           "3,0 typed during a body drag moves it exactly 3 along X (%s)" % (p1 and [round(p1[k] - p0[k], 6) for k in range(3)]))

        box = await scene(BOX)
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        c = await body_pt(box, [[p0[0] - 1.5, p0[1] + 1.75, p0[2] + 1.5], [p0[0] - 1.4, p0[1] - 1.2, p0[2] + 1.75],
                                [p0[0] + 1.4, p0[1] - 1.2, p0[2] + 1.75], [p0[0] - 1.75, p0[1] - 1.2, p0[2] + 1.2]])
        if c:
            await drag(c, [c[0], c[1] - 70], mods=('Alt',))
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p0 and p1 and p1[1] > p0[1] + 0.2 and near(p1[0], p0[0], 1e-9) and near(p1[2], p0[2], 1e-9),
           "Alt+drag in 3D lifts it straight up (%s)" % (p1 and [round(p1[k] - p0[k], 4) for k in range(3)]))
        box = await scene(BOX, view='plan')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        c = await proj([p0[0] + 1.3, p0[1], p0[2] + 1.3])
        await drag(c, [c[0], c[1] - 70], mods=('Alt',))
        p1 = await safe("(id)=>window.__t123.pos(id)", box)
        ck(p1 == p0, "and in a plan, which looks down the vertical, it refuses rather than guess")

        grp = await scene("""function(){const a=window.__a3dAdd('box',{}),b=window.__a3dAdd('box',{});
          window.__a3dSelectFor([a.id,b.id]);return {a:a.id,b:b.id};}""", view='plan')
        pa0 = await safe("(id)=>window.__t123.pos(id)", grp['a'])
        pb0 = await safe("(id)=>window.__t123.pos(id)", grp['b'])
        c = await body_pt(grp['a'], [[pa0[0] - 1.4, pa0[1], pa0[2] - 1.4], [pa0[0] - 1.4, pa0[1], pa0[2] + 1.4],
                                     [pa0[0] + 1.4, pa0[1], pa0[2] - 1.4]])
        if c:
            await drag(c, [c[0] + 90, c[1] + 30])
        pa1 = await safe("(id)=>window.__t123.pos(id)", grp['a'])
        pb1 = await safe("(id)=>window.__t123.pos(id)", grp['b'])
        ck(pa1 and pb1 and pa1[0] != pa0[0] and near(pa1[0] - pa0[0], pb1[0] - pb0[0], 1e-9)
           and near(pa1[2] - pa0[2], pb1[2] - pb0[2], 1e-9),
           "a selection of two moves together by one vector")

        # ==============================================================================
        print("\n-- 4. what a rebuild, a copy and a turn keep")
        wall = await scene("""function(){const w=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          window.__a3dSetWallType(w,'wt-ext400');window.__a3dSelectFor([w]);return w;}""")
        await page.wait_for_timeout(200)
        ok = await safe("()=>window.__a3dSetPropLen('height',4)")
        o = await safe("(id)=>window.__t123.obj(id)", wall)
        ck(ok and o and near(o['bim']['height'], 4) and o['bim'].get('typeId') == 'wt-ext400' and o['bim'].get('typeCat') == 'wall',
           "a wall's Height typed in Properties keeps its type (%s; V122 dropped it)" % (o and o['bim'].get('typeId')))
        await safe("(id)=>window.__a3dDragWallGripTo(id,1,8,0)", wall)
        o = await safe("(id)=>window.__t123.obj(id)", wall)
        ck(o and o['bim'].get('typeId') == 'wt-ext400' and near(o['bim']['centerline'][1][0], 8),
           "so does a grip drag of its end")
        await safe("(id)=>{window.__a3dMoveObjects([id],10,0,0);window.__a3dSelectFor([id]);}", wall)
        b0 = await safe("(id)=>window.__t123.b(id)", wall)
        await blur()
        await page.keyboard.press('Control+d')
        await page.wait_for_timeout(250)
        ids = await safe("()=>window.__t123.ids()")
        cp = [i for i in (ids or []) if i != wall]
        bc = await safe("(id)=>window.__t123.b(id)", cp[0]) if cp else None
        oc = await safe("(id)=>window.__t123.obj(id)", cp[0]) if cp else None
        ck(bc and b0 and near(bc['mn'][0] - b0['mn'][0], 1, 1e-6) and near(bc['mn'][2] - b0['mn'][2], 1, 1e-6)
           and oc['bim'].get('typeId') == 'wt-ext400',
           "a copy of a moved wall lands beside it, not where it was before the move, and keeps its type "
           "(offset %s; V122 put it 9 m away)" % (bc and b0 and round(bc['mn'][0] - b0['mn'][0], 4)))

        # ct-600 made the same size as ct-200x400 (which comes first), in steel: a copy that
        # re-guesses its type from its size comes out ct-200x400, only one that carries it ct-600
        col = await scene("""function(){window.__a3dApplyTypeParams('column','ct-600',{width:0.2,depth:0.4,material:'Steel'});
          const c=window.__a3dColumnAt([0,0],0,0.4,0.4,3);window.__a3dSelectFor([c]);return c;}""")
        await page.wait_for_timeout(200)
        await safe("""()=>{var s=document.querySelector('[data-propf="objtype"]');if(!s)return false;
          s.value='ct-600';s.dispatchEvent(new Event('change',{bubbles:true}));return true;}""")
        await safe("(id)=>{window.__a3dMoveObjects([id],5,0,0);window.__a3dSelectFor([id]);}", col)
        await blur()
        await page.keyboard.press('Control+d')
        await page.wait_for_timeout(250)
        ids = await safe("()=>window.__t123.ids()")
        cp = [i for i in (ids or []) if i != col]
        o0 = await safe("(id)=>window.__t123.obj(id)", col)
        oc = await safe("(id)=>window.__t123.obj(id)", cp[0]) if cp else None
        b0 = await safe("(id)=>window.__t123.b(id)", col)
        bc = await safe("(id)=>window.__t123.b(id)", cp[0]) if cp else None
        ck(o0 and o0['bim'].get('typeId') == 'ct-600' and oc and oc['bim'].get('typeId') == 'ct-600'
           and bc and near(bc['mn'][0] - b0['mn'][0], 1, 1e-6),
           "a copy of a moved column keeps its own type, not one of the same size, and lands beside it (%s)" %
           (oc and oc['bim'].get('typeId')))
        await safe("()=>window.__a3dApplyTypeParams('column','ct-600',{width:0.6,depth:0.6,material:'Concrete'})")

        fl = await scene("""function(){window.__a3dSketch('rect',[[0,0],[6,2]]);const f=window.__a3dFloor(0.2);return f;}""")
        await safe("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/2)", fl)
        b1 = await safe("(id)=>window.__t123.b(id)", fl)
        await safe("(id)=>window.__a3dRebuildFloor(id,0.3)", fl)
        b2 = await safe("(id)=>window.__t123.b(id)", fl)
        ck(b1 and b2 and near(b2['mn'][0], b1['mn'][0], 1e-6) and near(b2['mx'][2], b1['mx'][2], 1e-6)
           and near(b2['mx'][2] - b2['mn'][2], 6, 1e-6),
           "a turned floor keeps its turn through a thickness edit (V122 put it back)")
        mir = await safe("(id)=>{try{return window.__a3dMirrorSelection([id],[10,0],[10,5]);}catch(e){return 'THROW '+e.message;}}", fl)
        mo = await safe("(ids)=>ids&&ids.length?window.__t123.obj(ids[0]):null", mir) if isinstance(mir, list) else None
        ck(isinstance(mir, list) and len(mir) == 1 and mo and mo['bim'].get('profile') and len(mo['bim']['profile']) == 4,
           "and a floor mirrors, with an outline of its own (V122 threw: %s)" % (mir if not isinstance(mir, list) else 'ok'))

        pad = await scene("""function(){const s=window.__a3dSketch('rect',[[0,0],[4,3]]);window.__a3dMoveObjects([s],5,0,0);
          window.__a3dSelectFor([s]);return window.__a3dPad(2);}""")
        bp = await safe("(id)=>window.__t123.b(id)", pad)
        ck(bp and near(bp['mn'][0], 5) and near(bp['mx'][0], 9),
           "Pad of a moved sketch is made where the sketch is (x %s to %s)" % (bp and bp['mn'][0], bp and bp['mx'][0]))
        pk = await scene("""function(){window.__a3dSketch('rect',[[0,0],[4,4]]);const p=window.__a3dPad(2);window.__a3dSelectFor([p]);
          const s=window.__a3dSketch('rect',[[1,1],[2,2]]);window.__a3dMoveObjects([s],1,0,0);window.__a3dSelectFor([s]);
          return window.__a3dPocket(1);}""")
        vx = await safe("(id)=>{var o=window.__a3dObjSnapshot(id);if(!o||!o.mesh)return null;var q=o.pos||[0,0,0];"
                        "return o.mesh.v.map(function(v){return Math.round((v[0]+q[0])*1000)/1000;});}", pk)
        ck(vx is not None and 2 in vx and 3 in vx and 1 not in vx,
           "Pocket of a moved sketch cuts where the sketch is (hole edges at x 2 and 3, none at 1)")

        # ==============================================================================
        print("\n-- 5. taking a face")
        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        top = await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8])
        await dbl(top)
        f = await face()
        ck(f is not None and f['id'] == box and f['key'] == 'y+' and f['ok'] and f['dimName'] == 'Height' and near(f['dim'], 3.5),
           "a double-click on a box's top takes it: Height 3.5 m (%s)" % (f and [f['key'], f['dimName'], f['dim']]))
        ck(await gizmo() is None and (await safe("()=>window.__a3dGrips()") or []) == [],
           "and the gizmo and the grips step aside for its arrow")
        hint = await safe("()=>window.__a3dStatusHint()")
        ck(hint is not None and 'Tab' in hint and 'Esc' in hint and 'Height 3.5 m' in hint,
           "the status bar names the face and its keys (%r)" % hint)
        keys = []
        for i in range(6):
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(80)
            ff = await face()
            keys.append(ff and ff['key'])
        ck(len(set(keys)) == 6 and keys[-1] == 'y+', "Tab steps through all six faces and comes round (%s)" % keys)
        await page.keyboard.press('Shift+Tab')
        await page.wait_for_timeout(80)
        ff = await face()
        ck(ff is not None and ff['key'] == keys[-2], "Shift+Tab steps back (%s)" % (ff and ff['key']))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(120)
        ck(await face() is None and await safe("()=>window.__t123.sel()") == box and await gizmo() is not None,
           "Escape lets go of the face and the object stays selected, with its gizmo")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(120)
        ck(await safe("()=>window.__t123.sel()") is None, "a second Escape clears the selection")

        two = await scene("""function(){const a=window.__a3dAdd('box',{}),b=window.__a3dAdd('box',{});return {a:a.id,b:b.id};}""")
        pb = await safe("(id)=>window.__t123.pos(id)", two['b'])
        await click(await proj([pb[0] + 0.5, pb[1] + 1.75, pb[2] + 0.5]), mods=('Control', 'Shift'))
        f = await face()
        ck(f is not None and f['id'] == two['b'] and f['key'] == 'y+',
           "Ctrl+Shift+click takes a face of an object that was not selected (%s)" % (f and f['key']))
        await click(await proj([(await safe("(id)=>window.__t123.pos(id)", two['a']))[0], 1.75, (await safe("(id)=>window.__t123.pos(id)", two['a']))[2]]))
        ck(await face() is None and await safe("()=>window.__t123.sel()") == two['a'],
           "a click on another object lets the face go and selects that object")

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await safe("()=>window.__a3dRunCmd('presspull')")
        hint = await safe("()=>window.__a3dStatusHint()")
        await click(await proj([p0[0] + 0.5, p0[1] + 1.75, p0[2] + 0.5]))
        f = await face()
        ck(hint is not None and 'PRESSPULL' in hint and f is not None and f['key'] == 'y+',
           "PRESSPULL, then a click on a face, takes it (%r)" % hint)
        await safe("()=>window.__a3dRunCmd('presspull')")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(100)
        pend = await safe("()=>window.__a3dFacePending()")
        ck(pend is not None and not pend['facePick'], "Escape cancels a waiting PRESSPULL")

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}", view='plan')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 1.75, 0, p0[2] + 0.2]))
        f = await face()
        ck(f is not None and f['key'] == 'x+' and f['dimName'] == 'Length' and f['arrow'] is not None,
           "in a plan a double-click on the box's outline takes the side seen edge-on there, with an arrow (%s)" % (f and f['key']))
        await page.keyboard.press('Escape')
        await dbl(await proj([p0[0] + 0.4, 0, p0[2] + 0.3]))
        f = await face()
        ck(f is not None and f['key'] == 'y+' and f['arrow'] is None and f['dot'] is not None,
           "inside it, the top -- which points at the viewer, so a dot to click instead of an arrow")

        wall = await scene("""function(){const w=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          window.__a3dSetWallType(w,'wt-ext400');window.__a3dSelectFor([]);return w;}""")
        await dbl(await proj([3, 1.5, 0.2]))
        f = await face()
        ck(f is not None and f['key'] == 'side' and not f['ok'] and 'Exterior - 400mm' in (f['why'] or '') and f['arrow'] is None,
           "a wall's side does not move: its thickness is its type's, named (%r)" % (f and f['why']))
        ck(await safe("(id)=>window.__a3dFaceList(id)", wall) == ['top', 'start', 'end'],
           "an open wall's faces that move are its top and its two ends")

        # the faces of a wall's openings are the openings': on V123 before 123i a door's head was
        # part of the top (above half height), a window's sill part of the bottom, a jamb a side
        ow = await scene("""function(){const w=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          window.__a3dDoorAt(w,[1.5,0],0.9,2.1);window.__a3dWindowAt(w,[4.5,0],1.2,1.2,0.9);
          window.__a3dSelectFor([]);return w;}""")
        await dbl(await proj([2.6, 3, 0.05]))
        f = await face()
        ck(f is not None and f['key'] == 'top' and near(f['C'][1], 3, 1e-9),
           "the top of a wall with a door and a window is its top alone -- the openings' heads are not part of it "
           "(its centre at height %s)" % (f and f['C'][1]))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(80)
        await dbl(await proj([4.5, 0.9, 0]))
        f = await face()
        ck(f is not None and f['id'] == ow and f['key'] == 'opening' and not f['ok'] and 'opening' in (f['why'] or ''),
           "a window's sill is the opening's, not the wall's bottom (%s, %r)" % (f and f['key'], f and f['why']))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(80)
        jk = []
        for x in (1.05, 1.95):
            await dbl(await proj([x, 1.0, 0]))
            f = await face()
            jk.append(f and f['key'])
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(80)
        ck('opening' in jk, "and the door's jamb seen through it is the opening's, not a side whose thickness the "
           "type sets (%s)" % jk)
        loop = await scene("""function(){const w=window.__a3dWall([[0,0],[6,0],[6,4],[0,4]],0.3,3,'center',true);return w;}""")
        ck(await safe("(id)=>window.__a3dFaceList(id)", loop) == ['top'], "a closed wall has a top and no ends")

        col = await scene("""function(){return window.__a3dColumnAt([0,0],0,0.4,0.4,3);}""")
        await dbl(await proj([0, 1.5, 0.25]))
        f = await face()
        ck(f is not None and f['key'] == 'side' and not f['ok'] and 'type' in (f['why'] or ''),
           "a column's side refers to its type (%r)" % (f and f['why']))
        ck(await safe("(id)=>window.__a3dFaceList(id)", col) == ['top'], "a column's top is the face that moves")

        fl = await scene("""function(){window.__a3dSketch('rect',[[0,0],[6,4]]);const f=window.__a3dFloor(0.2);
          window.__a3dSelectFor([]);return f;}""")
        await dbl(await proj([3, 0, 2]))
        f = await face()
        ck(f is not None and f['id'] == fl and not f['ok'] and 'level' in (f['why'] or ''),
           "a floor's top says it is its level (%r)" % (f and f['why']))

        hs = await scene("""function(){const s=window.__a3dSketch('rect',[[0,0],[6,4]]);window.__a3dApplyHatchAt([3,2],0);
          window.__a3dSelectFor([]);return s;}""")
        await dbl(await proj([3, 0, 2]))
        f = await face()
        ck(f is not None and f['id'] == hs and f['key'] == 'region' and not f['ok'] and 'follow' in (f['why'] or ''),
           "a sketch a hatch is made from is not pulled out from under it (%r)" % (f and f['why']))

        cp = await scene("""function(){window.__a3dSketch('circle',[[0,0],[2,0]]);const p=window.__a3dPad(2);window.__a3dSelectFor([]);return p;}""")
        await dbl(await proj([0, 1, 2]))
        f = await face()
        ck(f is not None and f['id'] == cp and not f['ok'] and 'curved' in (f['why'] or ''),
           "a facet of a round pad's side is part of a curved surface, and says so (%r)" % (f and f['why']))
        await page.keyboard.press('Escape')
        await dbl(await proj([0.3, 2, 0.3]))
        f = await face()
        ck(f is not None and f['kind'] == 'solid' and f['ok'] and f['N'][1] > 0.999,
           "its flat top is a face, pointing out of the solid (%s)" % (f and f['N']))

        INSIDE_OUT = """function(){
          var v=[[0,0,0],[2,0,0],[2,2,0],[0,2,0],[0,0,2],[2,0,2],[2,2,2],[0,2,2]];
          /* every face's corners run inward by the engine's own faceNormal (Newell): each points
             into the cube, as an imported mesh may -- the order this suite first used ran outward
             and so tested nothing, which falsification found */
          var f=[[0,1,2,3],[5,4,7,6],[4,0,3,7],[1,5,6,2],[3,2,6,7],[4,5,1,0]];
          var o={id:'a3d-inside-out',t:'solid',name:'Imported',col:'#9db4c8',pos:[0,0,0],mesh:{v:v,f:f}};
          window.__a3dTestSetObjs([o]);return o.id;}"""
        io = await scene(INSIDE_OUT)
        await dbl(await proj([1, 2, 1]))
        f = await face()
        ck(f is not None and f['kind'] == 'solid' and f['N'][1] > 0.999,
           "a solid whose corners run the other way still has its top pointing out -- found by crossings, not order (%s)" %
           (f and f['N']))
        a = f['arrow'] if f else None
        if a:
            await click(mid(a), wait=30)
            await vbox()
            await page.keyboard.type('0.5')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(200)
        bi = await safe("(id)=>window.__t123.b(id)", io)
        ck(bi and near(bi['mx'][1], 2.5, 1e-9) and near(bi['mn'][1], 0, 1e-9),
           "and 0.5 typed on it pushes it out, up to 2.5 (%s)" % (bi and [bi['mn'][1], bi['mx'][1]]))
        # the faces facing away from the camera: a double-click only ever reaches faces that face
        # it, so only the ones Tab steps to show whether outward was found by crossings
        outs = []
        for i in range(6):
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(60)
            f = await face()
            if f and bi:
                cc = [(bi['mn'][k] + bi['mx'][k]) / 2 for k in range(3)]
                outs.append(round(sum(f['N'][k] * (f['C'][k] - cc[k]) for k in range(3)), 3))
        ck(len(outs) == 6 and min(outs) > 0.9,
           "every face Tab reaches on it points out of it, those facing away from the camera too (%s)" % outs)

        on = await scene("""function(){const o=window.__a3dAdd('box',{});window.__a3dSelectFor([o.id]);
          const s=window.__a3dSketch('rect',[[-7,-7],[-5,-5]]);window.__a3dSelectFor([]);return {box:o.id,sk:s};}""")
        await dbl(await proj([-6, 3.5, -6]))
        f = await face()
        ck(f is not None and f['id'] == on['sk'] and f['key'] == 'region',
           "a closed sketch drawn on a box's top is taken before the top it lies on (%s)" % (f and [f['id'] == on['sk'], f['key']]))

        two = await scene("""function(){const a=window.__a3dAdd('box',{}),b=window.__a3dAdd('box',{});
          window.__a3dMoveObjects([b.id],6,0,0);return {a:a.id,b:b.id};}""")
        p0 = await safe("(id)=>window.__t123.pos(id)", two['a'])
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        held = await face()
        await safe("()=>window.__a3dRunCmd('selAll')")
        await page.wait_for_timeout(150)
        sel = await safe("()=>window.__a3dSelSet()")
        ck(held is not None and await face() is None and sel is not None and len(sel) == 2,
           "a face lets go when a command changes the selection -- SELECT ALL takes both boxes (%s)" % sel)

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        await safe("(id)=>window.__a3dSetUnits('m')")
        await safe("()=>{window.__a3dUndo();}")
        await page.wait_for_timeout(150)
        ck(await face() is None, "an undo lets the face go")

        # ==============================================================================
        print("\n-- 6. push and pull")
        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        f = await face()
        a = f['arrow'] if f else None
        u0 = await undo()
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        if a:
            s0 = await align(mid(a))
            s1 = [s0[0] + 3, s0[1] - 55]
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        else:
            d_exp = None
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        o1 = await safe("(id)=>window.__t123.obj(id)", box)
        ck(d_exp is not None and b1 and near(b1['mx'][1] - b0['mx'][1], d_exp, 1e-6) and near(b1['mn'][1], b0['mn'][1], 1e-9),
           "dragging the top's arrow lifts the top by the cursor's travel along it, and the base stays (%s vs %s)" %
           (b1 and round(b1['mx'][1] - b0['mx'][1], 6), d_exp and round(d_exp, 6)))
        u1 = await undo()
        ck(o1 and o1['t'] == 'box' and near(o1['prm']['Height'] * 0.35, b1['mx'][1] - b1['mn'][1], 1e-6) and u1 == u0 + 1,
           "the box is still a parametric box, its Height the new height, and that was one undo step "
           "(%s, %s, undo %s->%s)" % (o1 and o1['t'], o1 and round(o1['prm']['Height'] * 0.35, 6), u0, u1))
        await safe("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        b2 = await safe("(id)=>window.__t123.b(id)", box)
        ck(b2 and near(b2['mx'][1], b0['mx'][1], 1e-9), "Ctrl+Z puts the top back")

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}", view='plan')
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        await dbl(await proj([p0[0] + 1.75, 0, p0[2] + 0.2]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            s0 = await align(mid(a))
            s1 = [s0[0] + 45, s0[1] + 4]
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(a and b1 and near(b1['mx'][0] - b0['mx'][0], d_exp, 1e-6) and near(b1['mn'][0], b0['mn'][0], 1e-9),
           "in a plan the east side moves east and the west side stays (%s)" % (b1 and round(b1['mx'][0] - b0['mx'][0], 4)))

        cyl = await scene("function(){const o=window.__a3dAdd('cyl',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", cyl)
        R0 = 2 * 0.35
        await dbl(await proj([p0[0], p0[1], p0[2] + R0]))
        f = await face()
        ck(f is not None and f['key'] == 'curved' and f['dimName'] == 'Radius' and near(f['dim'], R0),
           "a cylinder's curved side is its Radius (%s)" % (f and [f['key'], f['dim']]))
        a = f['arrow'] if f else None
        if a:
            s0 = await align(mid(a))
            s1 = await align(ahead(a, s0, 0.8))
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        o1 = await safe("(id)=>window.__t123.obj(id)", cyl)
        ck(a and o1 and near(o1['prm']['Radius'] * 0.35 - R0, d_exp, 1e-6) and o1['pos'] == p0,
           "pulling it widens the radius by the travel, about the same axis (%s)" % (o1 and round(o1['prm']['Radius'] * 0.35 - R0, 5)))

        tube = await scene("function(){const o=window.__a3dAdd('tube',{});return o.id;}")
        pt = await safe("(id)=>window.__t123.pos(id)", tube)
        await dbl(await proj([pt[0], pt[1] + 1.75, pt[2] + 1.2]))
        tries = 0
        f = await face()
        while f is not None and f['key'] != 'inner' and tries < 6:
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(60)
            f = await face()
            tries += 1
        ck(f is not None and f['key'] == 'inner' and f['dimName'] == 'Inner radius',
           "Tab reaches a tube's inner side (%s)" % (f and f['key']))
        if f and f['key'] == 'inner':
            await page.keyboard.type('0')
            vb = await vbox()
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(150)
            vb2 = await safe("()=>window.__a3dValueBox()")
            ck(vb is not None and vb['label'] == 'Inner radius' and vb2 is not None and 'nought' in (vb2.get('error') or ''),
               "a typed digit opens the size box; an inner radius of 0 is refused (%r)" % (vb2 and vb2.get('error')))
            await page.keyboard.press('Control+a')
            await page.keyboard.type('5')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(150)
            vb3 = await safe("()=>window.__a3dValueBox()")
            ck(vb3 is not None and 'smaller than the outer' in (vb3.get('error') or ''),
               "and one wider than the outer radius is refused too (%r)" % (vb3 and vb3.get('error')))
            await page.keyboard.press('Control+a')
            await page.keyboard.type('1')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(200)
            o1 = await safe("(id)=>window.__t123.obj(id)", tube)
            ck(o1 and near(o1['prm']['InnerRadius'] * 0.35, 1.0, 1e-9) and await safe("()=>window.__a3dValueBox()") is None,
               "1 sets the inner radius to exactly 1 m (%s)" % (o1 and o1['prm']['InnerRadius'] * 0.35))

        wall = await scene("""function(){const w=window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);
          window.__a3dSetWallType(w,'wt-ext400');window.__a3dDoorAt(w,[3,0],0.9,2.1);
          window.__a3dSelectFor([]);return w;}""")
        await dbl(await proj([2, 3, 0.05]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            s0 = await align(mid(a))
            s1 = [s0[0], s0[1] - 50]
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        o1 = await safe("(id)=>window.__t123.obj(id)", wall)
        ops = await safe("(id)=>window.__a3dOpeningsOf(id)", wall)
        ck(a and o1 and near(o1['bim']['height'] - 3, d_exp, 1e-6) and o1['bim'].get('typeId') == 'wt-ext400',
           "a wall's top is its height, and it keeps its type (%s)" % (o1 and round(o1['bim']['height'], 4)))
        thru = await safe("(id)=>window.__t123.cross(id,[3.001,1.003,-5],[0,0,1])", wall)
        above = await safe("(id)=>window.__t123.cross(id,[3.001,3.5,-5],[0,0,1])", wall)
        ck(ops and len(ops) == 1 and thru == 0 and above == 2,
           "its door is still cut through it after the push -- a line through the door meets nothing, one "
           "above it meets both faces of the taller wall (%s, %s)" % (thru, above))
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(80)
        f = await face()
        tries = 0
        while f is not None and f['key'] != 'end' and tries < 8:
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(60)
            f = await face()
            tries += 1
        a = f['arrow'] if f else None
        L0 = f['dim'] if f else None
        if a:
            s0 = await align(mid(a))
            s1 = await align(ahead(a, s0, 1.2))
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        o1 = await safe("(id)=>window.__t123.obj(id)", wall)
        ck(a and o1 and near(o1['bim']['centerline'][1][0] - 6, d_exp, 1e-6) and near(o1['bim']['centerline'][0][0], 0, 1e-9)
           and o1['bim'].get('typeId') == 'wt-ext400',
           "its end lengthens it along its line, the other end stays, the type stays (%s)" % (o1 and o1['bim']['centerline']))

        col = await scene("""function(){window.__a3dAddLevel();window.__a3dSetLevel(window.__a3dLevels()[0].id);
          return window.__a3dColumnAt([0,0],0,0.4,0.4,2.5);}""", point=True)
        lv = await safe("()=>window.__a3dLevels().map(l=>[l.name,l.elev])")
        await dbl(await proj([0, 2.5, 0.1]))
        f = await face()
        a = f['arrow'] if f else None
        snapped = None
        if a:
            s0 = mid(a)
            s1 = ahead(a, s0, 0.47)
            await press(s0)
            await move_to(s1)
            snapped = await safe("()=>window.__a3dPushDrag()")
            await release()
        o1 = await safe("(id)=>window.__t123.obj(id)", col)
        ck(snapped and snapped.get('snapLevel') == 'Level 1' and o1 and near(o1['bim']['height'], 3.0, 1e-12),
           "a column's top pulled near Level 1 stops on it exactly (%s, levels %s)" % (o1 and o1['bim']['height'], lv))

        ab = await scene("""function(){const a=window.__a3dAdd('box',{});const b=window.__a3dAdd('box',{Height:14});return {a:a.id,b:b.id};}""", point=True)
        pa = await safe("(id)=>window.__t123.pos(id)", ab['a'])
        bb = await safe("(id)=>window.__t123.b(id)", ab['b'])
        await dbl(await proj([pa[0] + 0.5, pa[1] + 1.75, pa[2] + 0.5]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            s0 = mid(a)
            await press(s0)
            await move_to([s0[0], s0[1] - 30])
            await move_to(await proj([bb['mn'][0], bb['mx'][1], bb['mx'][2]]))
            await release()
        b1 = await safe("(id)=>window.__t123.b(id)", ab['a'])
        ck(b1 and near(b1['mx'][1], bb['mx'][1], 1e-9),
           "a top pulled while the cursor is on another box's top corner stops at its height exactly (%s vs %s)" %
           (b1 and round(b1['mx'][1], 6), round(bb['mx'][1], 6)))

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}", grid=True)
        await safe("()=>window.__a3dSnapSet({grid:true,point:false})")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        f = await face()
        a = f['arrow'] if f else None
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        if a:
            s0 = mid(a)
            await drag(s0, [s0[0], s0[1] - 47])
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        dd = b1['mx'][1] - b0['mx'][1] if (b0 and b1) else None
        ck(dd is not None and abs(dd) > 0.2 and near(dd / 0.5, round(dd / 0.5), 1e-9),
           "with grid snap on a face moves in grid steps (%s)" % dd)

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        f = await face()
        a = f['arrow'] if f else None
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        if a:
            s0 = await align(mid(a))
            s1 = [s0[0], s0[1] - 60]
            await drag(s0, s1, mods=('Shift',))
            d_fine = expect_dist(a, s0, s1, fine=0.25)
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(a and b1 and near(b1['mx'][1] - b0['mx'][1], d_fine, 1e-6),
           "Shift pulls a quarter as far for the same travel (%s vs %s)" % (b1 and round(b1['mx'][1] - b0['mx'][1], 5), a and round(d_fine, 5)))

        box = await scene("function(){const o=window.__a3dAdd('box',{});return o.id;}")
        p0 = await safe("(id)=>window.__t123.pos(id)", box)
        await dbl(await proj([p0[0] + 0.8, p0[1] + 1.75, p0[2] + 0.8]))
        f = await face()
        a = f['arrow'] if f else None
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        pd = None
        if a:
            s0 = mid(a)
            await press(s0)
            await move_to([s0[0], s0[1] - 40])
            await page.keyboard.type('1.5')
            pd = await safe("()=>window.__a3dPushDrag()")
            await page.keyboard.press('Enter')
            await release()
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(pd and 'DISTANCE' in (pd.get('readout') or '') and b1 and near(b1['mx'][1] - b0['mx'][1], 1.5, 1e-9),
           "1.5 typed during the pull is 1.5 exactly (%s, %r)" % (b1 and round(b1['mx'][1] - b0['mx'][1], 6), pd and pd.get('readout')))
        f = await face()
        a = f['arrow'] if f else None
        b0 = b1
        if a:
            s0 = mid(a)
            await press(s0)
            await move_to([s0[0], s0[1] + 30])
            await page.keyboard.type('0.5')
            await page.keyboard.press('Enter')
            await release()
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(b1 and near(b1['mx'][1] - b0['mx'][1], -0.5, 1e-9),
           "and typed while pushing in, it goes in (%s)" % (b1 and round(b1['mx'][1] - b0['mx'][1], 6)))
        f = await face()
        a = f['arrow'] if f else None
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        u0 = await undo()
        if a:
            s0 = mid(a)
            await press(s0)
            await move_to([s0[0], s0[1] - 70])
            await page.keyboard.press('Escape')
            await release()
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        u1, fk = await undo(), (await face() or {}).get('key')
        ck(b1 == b0 and u1 == u0 and fk == 'y+',
           "Escape during a pull puts the face back, gives back its undo step and keeps the face held "
           "(%s, undo %s->%s, %s)" % (b1 == b0, u0, u1, fk))
        f = await face()
        a = f['arrow'] if f else None
        u0 = await undo()
        if a:
            await click(mid(a), wait=30)
        vb = await vbox()
        hnow = await safe("(id)=>{var b=window.__t123.b(id);return window.__a3dDispLen(b.mx[1]-b.mn[1]);}", box)
        ck(vb is not None and vb['label'] == 'Height' and vb['value'] == hnow,
           "a click on the arrow opens the size box with the height as it is (%s, %s)" % (vb, hnow))
        await page.keyboard.press('Control+a')
        await page.keyboard.type('5')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        ck(b1 and near(b1['mx'][1] - b1['mn'][1], 5, 1e-9) and near(b1['mn'][1], 0, 1e-9) and await undo() == u0 + 1,
           "5 makes it exactly 5 m tall on the same base, one undo step (%s)" % (b1 and [b1['mn'][1], b1['mx'][1]]))
        await page.keyboard.type('0.001')
        await vbox()
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        vb = await safe("()=>window.__a3dValueBox()")
        ck(vb is not None and 'cannot be less than' in (vb.get('error') or ''),
           "a height below the least a face allows is refused in the box (%r)" % (vb and vb.get('error')))
        await page.keyboard.press('Escape')

        pad = await scene("""function(){window.__a3dSketch('rect',[[0,0],[6,4]]);const p=window.__a3dPad(2);window.__a3dSelectFor([]);return p;}""")
        await dbl(await proj([2, 2, 1.5]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            s0 = mid(a)
            await press(s0)
            await move_to([s0[0], s0[1] + 500], steps=20)
            pd = await safe("()=>window.__a3dPushDrag()")
            await release()
        b1 = await safe("(id)=>window.__t123.b(id)", pad)
        ck(b1 and near(b1['mx'][1], 0.01, 1e-9) and pd and 'LIMIT' in (pd.get('readout') or ''),
           "a pad's top pushed down past its base stops exactly 1 cm above it, and says LIMIT (%s)" % (b1 and b1['mx'][1]))

        STEP = """function(){
          var v=[[0,0,0],[4,0,0],[4,2,0],[2,2,0],[2,1,0],[0,1,0],[0,0,2],[4,0,2],[4,2,2],[2,2,2],[2,1,2],[0,1,2]];
          var f=[[5,4,3,2,1,0],[6,7,8,9,10,11],[0,1,7,6],[1,2,8,7],[2,3,9,8],[3,4,10,9],[4,5,11,10],[5,0,6,11]];
          var o={id:'a3d-step-1',t:'solid',name:'Step',col:'#9db4c8',pos:[0,0,0],mesh:{v:v,f:f}};
          window.__a3dTestSetObjs([o]);return o.id;}"""
        st = await scene(STEP)
        await dbl(await proj([1, 1, 1]))
        f = await face()
        a = f['arrow'] if f else None
        ck(f is not None and f['kind'] == 'solid' and f['ok'] and f['N'][1] > 0.999,
           "the lower tread of a stepped solid is a face pointing up (%s)" % (f and f['N']))
        if a:
            s0 = mid(a)
            await drag(s0, [s0[0], s0[1] - 400], steps=20)
        o1 = await safe("(id)=>window.__t123.obj(id)", st)
        ys = sorted(set(round(v[1], 9) for v in o1['mesh']['v'])) if o1 else None
        ck(ys == [0.0, 2.0], "pulled up past the upper tread it stops level with it, exactly (heights %s)" % ys)

        sk = await scene("""function(){const s=window.__a3dSketch('rect',[[0,0],[6,4]]);window.__a3dSelectFor([]);return s;}""")
        await dbl(await proj([3, 0, 2]))
        f = await face()
        a = f['arrow'] if f else None
        u0 = await undo()
        if a:
            s0 = await align(mid(a))
            s1 = [s0[0], s0[1] - 60]
            await drag(s0, s1)
            d_exp = expect_dist(a, s0, s1)
        objs = await safe("()=>window.__a3dState().objs.map(o=>({id:o.id,t:o.t,name:o.name}))")
        pads = [o for o in (objs or []) if o['t'] == 'solid']
        bp = await safe("(id)=>window.__t123.b(id)", pads[0]['id']) if pads else None
        f2 = await face()
        ck(len(objs or []) == 1 and pads and bp and near(bp['mn'][1], 0, 1e-9) and near(bp['mx'][1], d_exp, 1e-6)
           and await undo() == u0 + 1,
           "a closed sketch pulled up becomes a pad of the pulled height, in its place (%s)" % (bp and [bp['mn'][1], round(bp['mx'][1], 5)]))
        ck(f2 is not None and f2['id'] == (pads[0]['id'] if pads else None) and f2['N'][1] > 0.999,
           "and the pad's top is the face held afterwards")
        await safe("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        objs = await safe("()=>window.__a3dState().objs.map(o=>({id:o.id,t:o.t}))")
        ck(objs == [{'id': sk, 't': 'sketch'}], "Ctrl+Z gives the sketch back")
        await safe("(id)=>window.__a3dSelectFor([])", sk)
        await dbl(await proj([3, 0, 2]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            s0 = mid(a)
            await drag(s0, [s0[0], s0[1] + 50])
        objs = await safe("()=>window.__a3dState().objs.map(o=>({id:o.id,t:o.t}))")
        pads = [o for o in (objs or []) if o['t'] == 'solid']
        bp = await safe("(id)=>window.__t123.b(id)", pads[0]['id']) if pads else None
        ck(pads and bp and near(bp['mx'][1], 0, 1e-9) and bp['mn'][1] < -0.1,
           "pushed down it becomes a pad below the sketch (%s)" % (bp and [round(bp['mn'][1], 4), bp['mx'][1]]))

        on = await scene("""function(){const o=window.__a3dAdd('box',{});window.__a3dSelectFor([o.id]);
          const s=window.__a3dSketch('rect',[[-7,-7],[-5,-5]]);window.__a3dSelectFor([]);return {box:o.id,sk:s};}""")
        await dbl(await proj([-6, 3.5, -6]))
        f = await face()
        a = f['arrow'] if f else None
        if a:
            await click(mid(a), wait=30)
        await vbox()
        await page.keyboard.type('-1')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(150)
        vb = await safe("()=>window.__a3dValueBox()")
        n = await safe("()=>window.__t123.n()")
        ck(vb is not None and 'Pocket' in (vb.get('error') or '') and n == 2,
           "a sketch drawn on a box is not pushed into it: the box says Pocket cuts (%r)" % (vb and vb.get('error')))
        await page.keyboard.press('Control+a')
        await page.keyboard.type('2')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(250)
        objs = await safe("()=>window.__a3dState().objs.map(o=>({id:o.id,t:o.t}))")
        pads = [o for o in (objs or []) if o['t'] == 'solid' and o['id'] != on['box']]
        bp = await safe("(id)=>window.__t123.b(id)", pads[0]['id']) if pads else None
        ck(pads and bp and near(bp['mn'][1], 3.5, 1e-9) and near(bp['mx'][1], 5.5, 1e-9),
           "and 2 typed pulls it up 2 m from the box's top into a pad (%s)" % (bp and [bp['mn'][1], bp['mx'][1]]))

        # ==============================================================================
        print("\n-- 7. a primitive's sizes in Properties, and Push/Pull on the toolbar")
        box = await scene(BOX)
        await page.wait_for_timeout(150)
        vals = await safe("""()=>['prm:Length','prm:Width','prm:Height'].map(function(f){
          var i=document.querySelector('[data-propf="'+f+'"]');return i?i.value:null;})""")
        ck(vals == ['3.5', '3.5', '3.5'], "Properties shows a box's Length, Width and Height in metres (%s)" % vals)
        POSY = """()=>{var i=document.querySelector('[data-propf="posy"]');return i?i.value:null;}"""
        bo0 = await safe(POSY)
        b0 = await safe("(id)=>window.__t123.b(id)", box)
        u0 = await undo()
        await safe("()=>window.__a3dSetPropLen('prm:Height',5)")
        b1 = await safe("(id)=>window.__t123.b(id)", box)
        u1 = await undo()
        ck(b1 and near(b1['mn'][1], b0['mn'][1], 1e-9) and near(b1['mx'][1] - b1['mn'][1], 5, 1e-9) and u1 == u0 + 1,
           "Height 5 there makes it 5 m tall on the same base, one undo step (%s, base %s, undo %s->%s)" %
           (b1 and [b1['mn'][1], b1['mx'][1]], b0 and b0['mn'][1], u0, u1))
        bo1 = await safe(POSY)
        ck(b0 and near(b0['mn'][1], 0, 1e-9) and bo0 == '0' and bo1 == '0',
           "a box standing on the ground reads Base Offset 0, before and after its Height changes -- its base, not "
           "its middle (%s, %s; before 123h 1.75 and 2.5)" % (bo0, bo1))
        await safe("()=>window.__a3dSetPropLen('posy',1)")
        b3 = await safe("(id)=>window.__t123.b(id)", box)
        ck(b3 and near(b3['mn'][1], 1, 1e-9) and near(b3['mx'][1] - b3['mn'][1], 5, 1e-9),
           "and Base Offset 1 stands its base at 1 m exactly (%s)" % (b3 and [b3['mn'][1], b3['mx'][1]]))
        await safe("()=>window.__a3dSetPropLen('posy',0)")
        await safe("()=>window.__a3dSetUnits('mm')")
        await page.wait_for_timeout(100)
        v = await safe("""()=>{var i=document.querySelector('[data-propf="prm:Height"]');return i?i.value:null;}""")
        await safe("()=>window.__a3dSetPropLen('prm:Height',6000)")
        b2 = await safe("(id)=>window.__t123.b(id)", box)
        ck(v == '5000' and b2 and near(b2['mx'][1] - b2['mn'][1], 6, 1e-9),
           "in millimetres it reads 5000, and 6000 makes it 6 m (%s)" % v)
        await safe("()=>window.__a3dSetUnits('m')")
        acts = await safe("()=>window.__a3dDockActions()")
        ck(acts is not None and 'bim:presspull' in acts, "Push/Pull is on the toolbar")
        ok = await safe("""()=>{var b=document.querySelector('#a3d-dock [data-a3dr="bim:presspull"]');if(!b)return false;
          var p=b.closest('.a3d-dockpop');if(p&&!p.classList.contains('open')){var id=p.getAttribute('data-dockpop');window.__a3dDockOpenGroup(id);}
          b.click();return true;}""")
        pend = await safe("()=>window.__a3dFacePending()")
        ck(ok and pend and pend['facePick'], "and clicking it waits for a face, as PRESSPULL does")
        await page.keyboard.press('Escape')

        keys = await safe("()=>window.__a3dFaceKeys().map(k=>k.act)")
        sheet = await safe("()=>{var s=window.__a3dShortcuts?window.__a3dShortcuts():null;return s?JSON.stringify(s):null;}")
        ck(keys == ['next', 'prev', 'type', 'back'] and sheet is not None and 'Faces' in sheet and 'Shift+Tab' in sheet,
           "the shortcut sheet's Faces group is read from the keys a held face listens to")

        ck(not errs, "no page errors (%s)" % (errs[:3] or 'none'))
        print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
        print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
        await browser.close()
        return 0 if not ck.bad else 1


if __name__ == '__main__':
    try:
        rc = asyncio.run(run())
    except Stalled as e:
        CK(False, "the page answers every step within %d s (it stopped answering at %s)" % (STALL, e))
        print("\n%d/%d checks passed\nRESULT: FAIL" % (CK.n - len(CK.bad), CK.n))
        rc = 1
    except Exception as e:
        CK(False, "the suite runs to its end (it stopped at %s: %s)" % (type(e).__name__, str(e)[:200]))
        print(''.join(traceback.format_exc().splitlines(True)[-6:]))
        print("\n%d/%d checks passed\nRESULT: FAIL" % (CK.n - len(CK.bad), CK.n))
        rc = 1
    sys.exit(rc)
