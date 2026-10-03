#!/usr/bin/env python3
"""bim_phase110_transform_gizmo_browser_tests.py -- V110: the transform gizmo, reworked.

Every handle is driven with real pointer events and every claim is asserted on the model.

  1. REVIT'S AXES: X red east, Y green north (the model's -z), Z blue up -- on the arms and on the
     origin -- and dragging the Y arrow moves the object north.
  2. THE DISPATCHER, FIXED AS A CLASS: a moved wall turns about the gizmo centre instead of a point
     offset by its move; ROTATE on a moved object turns about the picked centre; a Box turned with
     the ring really turns (and becomes a plain solid, and says so); a mirrored mesh is not inside
     out and lands mirrored; a polar array of a moved object lands where it should.
  3. PLANE SQUARES AND THE CENTRE: each square moves in its own plane only, keeps the grab point
     under the cursor, and steps by the grid; the centre moves in plan in 2D and across the screen
     in 3D.
  4. SCALE BOXES: one axis about the centre with the other extents untouched; Shift is even; a
     sketch scales in plan; a sketch with arcs refuses a one-way scale and accepts Shift; a wall
     offers none, and a wall with a box offers none.
  5. TILT ARCS: a rigid right-handed turn about X and about Y -- exactly 30 degrees under ORTHO, and
     not the mirror-image turn; undo restores the primitive; the tilted solid survives a reload.
  6. THE MENU: a right-click on a handle opens it; a right-drag still pans; Local follows a column's
     rotation and a wall's direction and says when it cannot; View drags along the screen; Escape
     closes it and keeps the selection; Hide removes every handle; GIZMO shows it and opens the menu.
  7. NAMES: the occlusion notice names handles by Revit's letters.
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
  window.__t110={
    snap:function(id){return window.__a3dObjSnapshot(id);},
    verts:function(id){
      var o=window.__a3dObjSnapshot(id);
      if(!o||!o.mesh)return null;
      var q=o.pos||[0,0,0];
      return o.mesh.v.map(function(v){return [v[0]+q[0],v[1]+q[1],v[2]+q[2]];});
    },
    vol:function(id){
      var o=window.__a3dObjSnapshot(id);
      if(!o||!o.mesh)return null;
      var q=o.pos||[0,0,0],V=o.mesh.v.map(function(v){return [v[0]+q[0],v[1]+q[1],v[2]+q[2]];}),s=0;
      o.mesh.f.forEach(function(f){
        for(var k=1;k+1<f.length;k++){
          var a=V[f[0]],b=V[f[k]],c=V[f[k+1]];
          s+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
        }
      });
      return s;
    },
    bounds:function(id){var b=window.__a3dWorldBounds([id]);return b?{mn:b.mn.slice(),mx:b.mx.slice()}:null;},
    toast:function(){var t=document.getElementById('a3d-toast');return t?t.textContent:'';},
    clearToast:function(){var t=document.getElementById('a3d-toast');if(t)t.textContent='';}
  };
  return true;}"""


def ext(b):
    return [b['mx'][k] - b['mn'][k] for k in range(3)]


def centre(b):
    return [(b['mx'][k] + b['mn'][k]) / 2 for k in range(3)]


def rodrigues(A, t):
    c, s, k = math.cos(t), math.sin(t), 1 - math.cos(t)
    x, y, z = A
    return [[c + x * x * k, x * y * k - z * s, x * z * k + y * s],
            [y * x * k + z * s, c + y * y * k, y * z * k - x * s],
            [z * x * k - y * s, z * y * k + x * s, c + z * z * k]]


def corners(b):
    return [[(b['mn'], b['mx'])[i][0], (b['mn'], b['mx'])[j][1], (b['mn'], b['mx'])[k][2]]
            for i in (0, 1) for j in (0, 1) for k in (0, 1)]


def set_err(expect, got):
    """Largest distance from an expected point to its nearest got point, and back."""
    if not got:
        return 1e9

    def d(p, q):
        return math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(3)))
    a = max(min(d(p, q) for q in got) for p in expect)
    b = max(min(d(p, q) for q in expect) for p in got)
    return max(a, b)


def rotate_about(pts, O, A, t):
    R = rodrigues(A, t)
    out = []
    for p in pts:
        w = [p[i] - O[i] for i in range(3)]
        out.append([O[i] + R[i][0] * w[0] + R[i][1] * w[1] + R[i][2] * w[2] for i in range(3)])
    return out


def cross_norm(a, b):
    c = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    return math.sqrt(sum(v * v for v in c))


def norm(a):
    return math.sqrt(sum(v * v for v in a))


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(260)
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

        async def safe(js, arg=None):
            try:
                return await (page.evaluate(js, arg) if arg is not None else page.evaluate(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        has = await safe("()=>!!window.__acad3dV110")
        ck(bool(has), "__acad3dV110 marker is present")
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

        async def drag(pts, button='left', shift=False, steps=8):
            r = await rect()
            if not r or not pts or any(p is None for p in pts):
                print('      (drag skipped: no target)')
                return False
            if shift:
                await page.keyboard.down('Shift')
            await page.mouse.move(r['left'] + pts[0][0], r['top'] + pts[0][1])
            await page.mouse.down(button=button)
            for p in pts[1:]:
                await page.mouse.move(r['left'] + p[0], r['top'] + p[1], steps=steps)
            await page.mouse.up(button=button)
            if shift:
                await page.keyboard.up('Shift')
            await page.wait_for_timeout(300)
            return True

        async def setup(js, view='3d', ortho=False, grid=False):
            await blur()
            oid = await safe("(a)=>{window.__a3dTestSetObjs([]);var id=(" + js + ")();"
                             "window.__a3dSelectFor([id]);"
                             "if(a.view==='plan')window.__a3dSetPlanView();else window.__a3dSet3DView();"
                             "window.__a3dSnapSet({point:false,grid:a.grid,ortho:a.ortho,gridSize:0.5});"
                             "window.__a3dZoomToSelection();return id;}",
                             {'view': view, 'ortho': ortho, 'grid': grid})
            await page.wait_for_timeout(450)
            return oid

        BOX = "function(){return window.__a3dAdd('box',{Length:10,Width:6,Height:8}).id;}"

        def arm(g, axis):
            for a in (g or {}).get('arms', []):
                if a['axis'] == axis:
                    return a
            return None

        def mid(a):
            return [(a['x0'] + a['x1']) / 2, (a['y0'] + a['y1']) / 2]

        # ------------------------------------------------------------------------------------
        print("\n-- 1. Revit's axes")
        box = await setup(BOX)
        g = await gizmo()
        got = {a['axis']: (a['lab'], a['col'], [round(v, 9) for v in a['dir']]) for a in (g or {}).get('arms', [])}
        ck(got.get('x') == ('X', '#ff5f56', [1, 0, 0]) and got.get('z') == ('Y', '#5ec98a', [0, 0, -1])
           and got.get('y') == ('Z', '#4ea1ff', [0, 1, 0]),
           "X is red and east, Y is green and NORTH (-z), Z is blue and up (%s)" % got)
        oa = await safe("()=>window.__a3dOriginAxes()")
        oad = {a['k']: (a['to'], a['col']) for a in (oa or [])}
        ck(oad.get('X') == ([13, 0, 0], '#8a4a4a') and oad.get('Y') == ([0, 0, -13], '#4f8a5f')
           and oad.get('Z') == ([0, 13, 0], '#3f5b82'),
           "the origin agrees: red east, green north, blue up (%s)" % oad)
        p0 = (await safe("(id)=>window.__t110.snap(id).pos", box)) or [0, 0, 0]
        ay = arm(g, 'z')
        if ay:
            await drag([mid(ay), [mid(ay)[0] + (ay['x1'] - ay['x0']) * 0.6, mid(ay)[1] + (ay['y1'] - ay['y0']) * 0.6]])
        p1 = (await safe("(id)=>window.__t110.snap(id).pos", box)) or p0
        ck(p1[2] < p0[2] - 0.3 and abs(p1[0] - p0[0]) < 1e-9 and abs(p1[1] - p0[1]) < 1e-9,
           "dragging the Y arrow toward its tip moves the object NORTH and only north (%s -> %s)"
           % ([round(v, 3) for v in p0], [round(v, 3) for v in p1]))
        await safe("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(400)
        gp = await gizmo()
        apy = arm(gp, 'z')
        ck(apy is not None and apy['y1'] < apy['y0'] - 40 and abs(apy['x1'] - apy['x0']) < 2,
           "in plan the Y arrow points straight up the screen (%s)"
           % (apy and [round(apy['x1'] - apy['x0'], 1), round(apy['y1'] - apy['y0'], 1)]))

        # ------------------------------------------------------------------------------------
        print("\n-- 2. the transform dispatcher, fixed as a class")
        wid = await setup("function(){return window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);}")
        g = await gizmo()
        ax = arm(g, 'x')
        if ax:
            await drag([mid(ax), [mid(ax)[0] + ax['sx'] * 5, mid(ax)[1] + ax['sy'] * 5]])
        g = await gizmo()
        O = g['origin'] if g else [0, 0, 0]
        pts = []
        for d in (20, 50, 80, 110):
            pts.append(await safe("(d)=>window.__a3dGizmoRingPoint(d)", d))
        await drag(pts, steps=6)
        w = await safe("(id)=>{var o=window.__t110.snap(id);return {cl:o.bim.centerline,pos:o.pos};}", wid)
        if w:
            ends = [[p[0] + w['pos'][0], p[1] + w['pos'][2]] for p in w['cl']]
            dists = [math.hypot(e[0] - O[0], e[1] - O[2]) for e in ends]
            midp = [(ends[0][0] + ends[1][0]) / 2, (ends[0][1] + ends[1][1]) / 2]
            turned = abs(math.degrees(math.atan2(ends[1][1] - ends[0][1], ends[1][0] - ends[0][0])))
            ck(abs(dists[0] - 4) < 0.02 and abs(dists[1] - 4) < 0.02
               and math.hypot(midp[0] - O[0], midp[1] - O[2]) < 0.02 and 45 < turned < 135,
               "a wall moved 5 m and then turned stays centred on the gizmo (ends %s m from it, "
               "turned %.1f deg) -- before V110 it swung 5 m east and 5 m north" %
               ([round(v, 3) for v in dists], turned))
        else:
            ck(False, "a moved wall could be read back after turning")

        wid2 = await setup("function(){return window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false);}")
        r2 = await safe("""(id)=>{window.__a3dMoveObjects([id],10,0,4);
          window.__a3dRotateSelection([id],[13,4],Math.PI/2);
          var o=window.__t110.snap(id);
          return o.bim.centerline.map(function(p){return [p[0]+o.pos[0],p[1]+o.pos[2]];});}""", wid2)
        ck(r2 is not None and max(abs(r2[0][0] - 13), abs(r2[0][1] - 1), abs(r2[1][0] - 13), abs(r2[1][1] - 7)) < 1e-9,
           "ROTATE on a moved wall turns it about the centre that was picked (%s, expected [13,1] "
           "and [13,7])" % (r2 and [[round(v, 6) for v in p] for p in r2]))

        box = await setup(BOX, ortho=True)
        b0 = await safe("(id)=>window.__t110.bounds(id)", box)
        await safe("()=>window.__t110.clearToast()")
        pts = []
        for d in (20, 50, 80, 110):
            pts.append(await safe("(d)=>window.__a3dGizmoRingPoint(d)", d))
        await drag(pts, steps=6)
        b1 = await safe("(id)=>window.__t110.bounds(id)", box)
        sn = await safe("(id)=>{var o=window.__t110.snap(id);return {t:o.t,prm:!!o.prm,mesh:!!o.mesh};}", box)
        e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([0, 0, 0], [1, 1, 1])
        ck(abs(e1[0] - e0[2]) < 1e-6 and abs(e1[2] - e0[0]) < 1e-6 and abs(e1[1] - e0[1]) < 1e-9,
           "a Box turned 90 degrees on the ring really turns: its plan extents swap (%s -> %s) -- "
           "before V110 only its position moved and nothing turned" %
           ([round(v, 4) for v in e0], [round(v, 4) for v in e1]))
        ck(sn == {'t': 'solid', 'prm': False, 'mesh': True},
           "and it is now a plain solid with the new shape in its mesh and no dead size fields (%s)" % sn)
        tt = await safe("()=>window.__t110.toast()") or ''
        ck('plain solid' in tt, "and the user is told so (%r)" % tt[-120:])

        pad = await safe("""()=>{window.__a3dTestSetObjs([]);
          window.__a3dSketch('rect',[[1,1],[5,3]]);
          var id=window.__a3dPad(2.5);
          window.__a3dMoveObjects([id],3,0,2);
          return id;}""")
        await page.wait_for_timeout(300)
        v0 = await safe("(id)=>window.__t110.vol(id)", pad)
        pb0 = await safe("(id)=>window.__t110.bounds(id)", pad)
        new = await safe("(id)=>window.__a3dMirrorSelection([id],[20,0],[20,5])", pad)
        cid = new[0] if new else None
        v1 = await safe("(id)=>window.__t110.vol(id)", cid) if cid else None
        pb1 = await safe("(id)=>window.__t110.bounds(id)", cid) if cid else None
        ck(v0 is not None and v1 is not None and abs(v0) > 1e-6 and abs(v1 - v0) < 1e-9 * max(1, abs(v0)),
           "a mirrored solid is not inside out: its signed volume keeps its sign (%s -> %s)" % (v0, v1))
        ck(pb0 and pb1 and abs(pb1['mn'][0] - (40 - pb0['mx'][0])) < 1e-9 and abs(pb1['mx'][0] - (40 - pb0['mn'][0])) < 1e-9
           and abs(pb1['mn'][2] - pb0['mn'][2]) < 1e-9,
           "and a MOVED solid mirrors about the line that was picked (x %s -> %s)" %
           (pb0 and [round(pb0['mn'][0], 4), round(pb0['mx'][0], 4)], pb1 and [round(pb1['mn'][0], 4), round(pb1['mx'][0], 4)]))

        arr = await safe("""()=>{window.__a3dTestSetObjs([]);
          var id=window.__a3dSketch('rect',[[1,0],[3,1]]);
          window.__a3dMoveObjects([id],5,0,0);
          var all=window.__a3dBuildPolarArray([id],[0,0],2,180);
          var c=all.filter(function(x){return x!==id;})[0],o=window.__t110.snap(c);
          return o?o.pts.map(function(p){return [p[0]+o.pos[0],p[1]+o.pos[2]];}):null;}""")
        want = [[-p[1], p[0]] for p in ([6, 0], [8, 0], [8, 1], [6, 1])]   # +90 in the model's sense
        ck(arr is not None and set_err([[p[0], 0, p[1]] for p in want], [[p[0], 0, p[1]] for p in arr]) < 1e-9,
           "a polar array of a MOVED sketch lands where the moved sketch turns to (%s)" %
           (arr and [[round(v, 4) for v in p] for p in arr]))

        cb = await safe("""()=>{window.__a3dTestSetObjs([]);
          var id=window.__a3dSketch('poly',[[0,0],[4,0],[4,2]]);var o=window.__a3dObjSnapshot(id);o.bulges=[0.4,0,0];
          window.__a3dTestSetObjs([o]);
          var m=window.__a3dMirrorSelection([id],[10,0],[10,5]);
          var a=window.__a3dBuildPolarArray([id],[0,0],2,180);
          var mc=window.__a3dObjSnapshot(m[0]),ac=window.__a3dObjSnapshot(a.filter(function(x){return x!==id;})[0]);
          return {m:mc&&mc.bulges,a:ac&&ac.bulges};}""")
        ck(cb == {'m': [-0.4, 0, 0], 'a': [0.4, 0, 0]},
           "a mirrored sketch keeps its arc, reflected, and an arrayed one keeps it as it was (%s) -- "
           "both copies used to come out with every arc straight" % cb)

        # ------------------------------------------------------------------------------------
        print("\n-- 3. plane squares and the centre")
        box = await setup(BOX)
        g = await gizmo()
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        ck(sorted(pl) == ['xy', 'xz', 'zy'] and pl['xz']['lab'] == 'XY' and pl['xz']['col'] == '#4ea1ff'
           and pl['xy']['lab'] == 'XZ' and pl['zy']['lab'] == 'YZ',
           "three plane squares in 3D, named and coloured Revit's way (%s)" %
           {k: (v['lab'], v['col']) for k, v in pl.items()})
        hit = await safe("(c)=>window.__a3dGizmoAt(c[0],c[1])", pl['xz']['c']) if 'xz' in pl else None
        ck(hit == 'plane:xz', "the plan square picks as itself (%s)" % hit)
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        start = pl['xz']['c'] if 'xz' in pl else None
        P0 = await safe("(a)=>window.__a3dRayPlane(a.s[0],a.s[1],a.O,[0,1,0])", {'s': start, 'O': g['origin']}) if start else None
        end = [start[0] + 60, start[1] + 25] if start else None
        await drag([start, end])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 0, 0]
        ck(abs(dv[1]) < 1e-9 and math.hypot(dv[0], dv[2]) > 0.3,
           "the plan square moves in X and Y only (delta %s)" % [round(v, 4) for v in dv])
        pe = await safe("(p)=>window.__a3dProject(p)", [P0[k] + dv[k] for k in range(3)]) if P0 else None
        ck(pe is not None and abs(pe['x'] - end[0]) < 1.0 and abs(pe['y'] - end[1]) < 1.0,
           "and the point grabbed stays under the cursor (%s vs %s)" %
           (pe and [round(pe['x'], 2), round(pe['y'], 2)], end))

        box = await setup(BOX)
        g = await gizmo()
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        if 'xy' in pl:
            await drag([pl['xy']['c'], [pl['xy']['c'][0] + 40, pl['xy']['c'][1] - 45]])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 0, 0]
        ck('xy' in pl and abs(dv[2]) < 1e-9 and abs(dv[0]) > 0.1 and abs(dv[1]) > 0.1,
           "the XZ square moves east and up only (delta %s)" % [round(v, 4) for v in dv])

        box = await setup(BOX, grid=True)
        g = await gizmo()
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        if 'xz' in pl:
            await drag([pl['xz']['c'], [pl['xz']['c'][0] + 71, pl['xz']['c'][1] + 23]])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0.1, 0, 0.1]
        ck(abs(dv[0] / 0.5 - round(dv[0] / 0.5)) < 1e-9 and abs(dv[2] / 0.5 - round(dv[2] / 0.5)) < 1e-9
           and (abs(dv[0]) + abs(dv[2])) > 0.4,
           "with GRID on the plane move is whole grid steps along each axis (%s)" % [round(v, 6) for v in dv])

        box = await setup(BOX, view='plan')
        g = await gizmo()
        c = [g['centre']['x'], g['centre']['y']] if g else None
        ck(c is not None and await safe("(c)=>window.__a3dGizmoAt(c[0],c[1])", c) == 'centre',
           "the centre square picks as itself")
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        P0 = await safe("(a)=>window.__a3dRayPlane(a.s[0],a.s[1],a.O,[0,1,0])", {'s': c, 'O': g['origin']}) if c else None
        end = [c[0] + 50, c[1] - 35] if c else None
        await drag([c, end])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 1, 0]
        pe = await safe("(p)=>window.__a3dProject(p)", [P0[k] + dv[k] for k in range(3)]) if P0 else None
        ck(abs(dv[1]) < 1e-9 and dv[0] > 0.2 and dv[2] < -0.2 and pe is not None
           and abs(pe['x'] - end[0]) < 1.0 and abs(pe['y'] - end[1]) < 1.0,
           "in plan the centre moves freely in the plan plane, under the cursor (delta %s)" %
           [round(v, 4) for v in dv])

        box = await setup(BOX)
        g = await gizmo()
        c = [g['centre']['x'], g['centre']['y']] if g else None
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        await drag([c, [c[0] + 40, c[1] - 50]] if c else None)
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 0, 0]
        po = await safe("(p)=>window.__a3dProject(p)", g['origin']) if g else None
        pm = await safe("(p)=>window.__a3dProject(p)", [g['origin'][k] + dv[k] for k in range(3)]) if g else None
        ck(po and pm and abs((pm['x'] - po['x']) - 40) < 1.5 and abs((pm['y'] - po['y']) + 50) < 1.5 and abs(dv[1]) > 0.1,
           "in 3D the centre moves in the screen plane: the origin follows the cursor exactly "
           "(%s px for a (40,-50) drag), rising as it goes up the screen" %
           (po and pm and [round(pm['x'] - po['x'], 2), round(pm['y'] - po['y'], 2)]))

        # ------------------------------------------------------------------------------------
        print("\n-- 4. scale boxes")
        box = await setup(BOX, ortho=True)
        g = await gizmo()
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        ck(sorted(sc) == ['x', 'y', 'z'] and g['caps']['tilt'] is True,
           "a Box offers a scale box on every axis and the tilt arcs (%s)" % sorted(sc))
        b0 = await safe("(id)=>window.__t110.bounds(id)", box)
        s = sc.get('x')
        if s:
            u = [(s['x'] - g['ox']) / s['L'], (s['y'] - g['oy']) / s['L']]
            ck(await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", [s['x'], s['y']]) == 'scale:x',
               "the X scale box picks as itself")
            await drag([[s['x'], s['y']], [s['x'] + u[0] * s['L'] * 0.5, s['y'] + u[1] * s['L'] * 0.5]])
        b1 = await safe("(id)=>window.__t110.bounds(id)", box)
        e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([1, 1, 1], [0, 0, 0])
        c0, c1 = (centre(b0), centre(b1)) if (b0 and b1) else ([0, 0, 0], [1, 1, 1])
        ck(abs(e1[0] - 1.5 * e0[0]) < 1e-9 and abs(e1[1] - e0[1]) < 1e-9 and abs(e1[2] - e0[2]) < 1e-9
           and max(abs(c1[k] - c0[k]) for k in range(3)) < 1e-9,
           "dragging it out half its distance scales X by exactly 1.5 under ORTHO, about the centre, "
           "Y and Z untouched (%s -> %s)" % ([round(v, 4) for v in e0], [round(v, 4) for v in e1]))
        g = await gizmo()
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        s = sc.get('y')
        b0 = b1
        if s:
            u = [(s['x'] - g['ox']) / s['L'], (s['y'] - g['oy']) / s['L']]
            await blur()
            await drag([[s['x'], s['y']], [s['x'] + u[0] * s['L'] * 0.5, s['y'] + u[1] * s['L'] * 0.5]], shift=True)
        b2 = await safe("(id)=>window.__t110.bounds(id)", box)
        e0, e2 = (ext(b0), ext(b2)) if (b0 and b2) else ([1, 1, 1], [0, 0, 0])
        ck(all(abs(e2[k] - 1.5 * e0[k]) < 1e-9 for k in range(3)),
           "Shift on a scale box scales evenly (%s -> %s)" % ([round(v, 4) for v in e0], [round(v, 4) for v in e2]))
        st = await safe("(id)=>window.__t110.snap(id).pos", box)
        ck(st is not None, "and Shift did not pan instead")

        # AMENDED FOR V130: a 4 x 2 rectangle zoomed to fill the view put its left edge's midpoint grip
        # exactly under the X box once the slimmer dock gave the drawing more room, and a grip wins a
        # press (V97). A rectangle deeper than it is wide keeps its edges inside the box at any fit.
        sk = await setup("function(){return window.__a3dSketch('rect',[[0,0],[2,4]]);}", ortho=True)
        g = await gizmo()
        ck(g is not None and g['caps']['scale'] == {'x': True, 'y': False, 'z': True} and g['caps']['tilt'] is False
           and not g['tilts'],
           "a sketch scales in plan only and never tilts (%s)" % (g and g['caps']))
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        b0 = await safe("(id)=>window.__t110.bounds(id)", sk)
        s = sc.get('x')
        if s:
            u = [(s['x'] - g['ox']) / s['L'], (s['y'] - g['oy']) / s['L']]
            await drag([[s['x'], s['y']], [s['x'] + u[0] * s['L'] * 0.5, s['y'] + u[1] * s['L'] * 0.5]])
        b1 = await safe("(id)=>window.__t110.bounds(id)", sk)
        sn = await safe("(id)=>{var o=window.__t110.snap(id);return {t:o.t,y:o.y||0};}", sk)
        e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([1, 1, 1], [0, 0, 0])
        ck(abs(e1[0] - 1.5 * e0[0]) < 1e-9 and abs(e1[2] - e0[2]) < 1e-9 and sn and sn['t'] == 'sketch',
           "its X box stretches it along X only, and it is still a sketch (%s -> %s)" %
           ([round(v, 4) for v in e0], [round(v, 4) for v in e1]))

        arcs = await setup("""function(){var id=window.__a3dSketch('poly',[[0,0],[4,0],[4,2]]);
          var o=window.__a3dObjSnapshot(id);o.bulges=[0.4,0,0];window.__a3dTestSetObjs([o]);return id;}""", ortho=True)
        g = await gizmo()
        ck(g is not None and g['caps']['arcs'] == 1, "a sketch with an arc is recognised (%s)" % (g and g['caps']))
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        p0 = await safe("(id)=>window.__t110.snap(id).pts", arcs)
        await safe("()=>window.__t110.clearToast()")
        s = sc.get('x')
        if s:
            u = [(s['x'] - g['ox']) / s['L'], (s['y'] - g['oy']) / s['L']]
            await drag([[s['x'], s['y']], [s['x'] + u[0] * s['L'] * 0.5, s['y'] + u[1] * s['L'] * 0.5]])
        p1 = await safe("(id)=>window.__t110.snap(id).pts", arcs)
        tt = await safe("()=>window.__t110.toast()") or ''
        ck(p0 is not None and p0 == p1 and 'evenly' in tt,
           "a one-way scale is refused, and the user is told to hold Shift (%r)" % tt[-90:])
        b0 = await safe("(id)=>window.__t110.bounds(id)", arcs)
        if s:
            await blur()
            await drag([[s['x'], s['y']], [s['x'] + u[0] * s['L'] * 0.5, s['y'] + u[1] * s['L'] * 0.5]], shift=True)
        b1 = await safe("(id)=>window.__t110.bounds(id)", arcs)
        bl = await safe("(id)=>window.__t110.snap(id).bulges", arcs)
        e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([1, 1, 1], [0, 0, 0])
        ck(abs(e1[0] - 1.5 * e0[0]) < 1e-6 and abs(e1[2] - 1.5 * e0[2]) < 1e-6 and bl == [0.4, 0, 0],
           "with Shift it scales evenly in plan and its arc is kept (%s -> %s, bulges %s)" %
           ([round(v, 4) for v in e0], [round(v, 4) for v in e1], bl))

        wid = await setup("function(){return window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);}")
        g = await gizmo()
        ck(g is not None and not g['scales'] and not g['tilts'] and g['ring'],
           "a wall offers the ring but no scale box and no tilt arc -- a wall that leans is not a wall")
        both = await safe("""()=>{window.__a3dTestSetObjs([]);
          var w=window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);
          var b=window.__a3dAdd('box',{Length:10,Width:6,Height:8}).id;
          window.__a3dSelectFor([w,b]);var g=window.__a3dGizmo();
          return g?{s:g.scales.length,t:g.tilts.length,n:g.ids.length}:null;}""")
        ck(both == {'s': 0, 't': 0, 'n': 2},
           "a wall and a box together offer neither -- a handle is drawn only when the whole "
           "selection can follow it (%s)" % both)

        # ------------------------------------------------------------------------------------
        print("\n-- 5. tilt arcs")
        for axis, A, name in (('x', [1, 0, 0], 'X'), ('z', [0, 0, -1], 'Y')):
            box = await setup(BOX, ortho=True)
            g = await gizmo()
            tl = {t['axis']: t for t in (g or {}).get('tilts', [])}
            b0 = await safe("(id)=>window.__t110.bounds(id)", box)
            O = g['origin'] if g else [0, 0, 0]
            ptsA = []
            for d in (225, 235, 245, 255):
                ptsA.append(await safe("(a)=>window.__a3dGizmoArcPoint(a[0],a[1])", [axis, d]))
            hitA = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", ptsA[0]) if ptsA[0] else None
            ck(axis in tl and tl[axis]['lab'] == name and hitA == 'tilt:' + axis,
               "the %s arc is drawn and picks as itself (%s)" % (name, hitA))
            await drag(ptsA, steps=6)
            vv = await safe("(id)=>window.__t110.verts(id)", box)
            cs = corners(b0) if b0 else []
            good = set_err(rotate_about(cs, O, A, math.radians(30)), vv) if vv else 1e9
            bad = set_err(rotate_about(cs, O, A, math.radians(-30)), vv) if vv else 0
            ck(good < 1e-6 and bad > 0.01,
               "dragging it 30 degrees tilts the box rigidly by exactly +30 about %s, right-handed "
               "(error %.2e; the opposite turn would be off by %.3f)" % (name, good, bad))
        und = await safe("""(id)=>{window.__a3dUndo();var o=window.__a3dObjSnapshot(id);
          return o?{t:o.t,prm:o.prm,mesh:!!o.mesh}:null;}""", box)
        ck(und is not None and und['t'] == 'box' and und['prm'] and not und['mesh'],
           "one undo gives back the parametric Box (%s)" % und)
        await safe("()=>window.__a3dRedo&&window.__a3dRedo()")
        box = await setup(BOX, ortho=True)
        ptsA = []
        for d in (225, 240, 255):
            ptsA.append(await safe("(a)=>window.__a3dGizmoArcPoint(a[0],a[1])", ['x', d]))
        await drag(ptsA, steps=6)
        v_before = await safe("(id)=>window.__t110.verts(id)", box)
        await page.wait_for_timeout(1400)
        await page.reload()
        await page.wait_for_timeout(2300)
        await safe(HELPERS)
        v_after = await safe("(id)=>window.__t110.verts(id)", box)
        t_after = await safe("(id)=>{var o=window.__a3dObjSnapshot(id);return o?o.t:null;}", box)
        ck(v_before and v_after and t_after == 'solid' and set_err(v_before, v_after) < 1e-9,
           "the tilted solid survives a reload exactly (%s, err %s)" %
           (t_after, v_before and v_after and '%.1e' % set_err(v_before, v_after)))

        # ------------------------------------------------------------------------------------
        print("\n-- 6. the gizmo menu")
        box = await setup(BOX)
        g = await gizmo()
        r = await rect()
        ax = arm(g, 'x')
        m = mid(ax) if ax else [0, 0]
        await page.mouse.move(r['left'] + m[0], r['top'] + m[1])
        await page.mouse.down(button='right')
        await page.mouse.up(button='right')
        await page.wait_for_timeout(250)
        stt = await safe("()=>window.__a3dGizmoState()")
        acts = [(b['act'], b['on']) for b in ((stt or {}).get('menu') or [])]
        ck(acts == [('world', True), ('local', False), ('view', False), ('hide', False)],
           "a right-click on a handle opens the gizmo menu, World ticked (%s)" % acts)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        stt = await safe("()=>window.__a3dGizmoState()")
        sel = await safe("()=>window.__a3dState().sel")
        ck(stt and stt['menu'] is None and sel == box,
           "Escape closes it and the selection stays (%s)" % sel)
        g0 = await gizmo()
        await page.mouse.move(r['left'] + m[0], r['top'] + m[1])
        await page.mouse.down(button='right')
        await page.mouse.move(r['left'] + m[0] + 70, r['top'] + m[1] + 30, steps=6)
        await page.mouse.up(button='right')
        await page.wait_for_timeout(250)
        stt = await safe("()=>window.__a3dGizmoState()")
        g1 = await gizmo()
        ck(stt and stt['menu'] is None and g0 and g1 and abs(g1['ox'] - g0['ox']) > 20,
           "a right-DRAG from a handle still pans, and opens no menu (origin moved %s px)" %
           (g0 and g1 and round(g1['ox'] - g0['ox'], 1)))

        async def menu_pick(act):
            gg = await gizmo()
            a = arm(gg, 'x') or arm(gg, 'z')
            if not a:
                return False
            mm = mid(a)
            rr = await rect()
            await page.mouse.move(rr['left'] + mm[0], rr['top'] + mm[1])
            await page.mouse.down(button='right')
            await page.mouse.up(button='right')
            await page.wait_for_timeout(200)
            try:
                await page.click('#a3d-gizmenu [data-a3dgiz="%s"]' % act, timeout=2000)
            except Exception as e:
                print('      (menu click %s failed: %s)' % (act, str(e)[:100]))
                return False
            await page.wait_for_timeout(250)
            return True

        col = await setup("""function(){var c=window.__a3dColumnAt([2,3],0,0.4,0.6,3);
          window.__a3dRotateSelection([c],[2,3],0.5);return c;}""")
        await menu_pick('local')
        g = await gizmo()
        fx = g['frame']['x'] if g else [1, 0, 0]
        ck(g and g['frame']['mode'] == 'local' and abs(fx[0] - math.cos(0.5)) < 1e-9 and abs(fx[2] - math.sin(0.5)) < 1e-9,
           "Align to Local turns the gizmo to the column's own rotation (x = %s)" % [round(v, 4) for v in fx])
        s0 = await safe("(id)=>window.__t110.snap(id).pos", col)
        ax = arm(g, 'x')
        if ax:
            await drag([mid(ax), [mid(ax)[0] + ax['sx'] * 1.5, mid(ax)[1] + ax['sy'] * 1.5]])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", col)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 0, 0]
        ck(norm(dv) > 0.5 and cross_norm(dv, fx) < 1e-9 * max(1, norm(dv)),
           "and its X arrow moves the column along that direction only (delta %s)" % [round(v, 4) for v in dv])
        await safe("()=>{window.__a3dSetPlanView();window.__a3dSnapSet({point:false,grid:true,ortho:false,gridSize:0.5});}")
        await page.wait_for_timeout(400)
        g = await gizmo()
        c = [g['centre']['x'], g['centre']['y']] if g else None
        fx, fz = (g['frame']['x'], g['frame']['z']) if g else ([1, 0, 0], [0, 0, -1])
        s0 = await safe("(id)=>window.__t110.snap(id).pos", col)
        await drag([c, [c[0] + 57, c[1] - 38]] if c else None)
        s1 = await safe("(id)=>window.__t110.snap(id).pos", col)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0.1, 0, 0]
        la = sum(dv[k] * fx[k] for k in range(3))
        lb = sum(dv[k] * fz[k] for k in range(3))
        ck(abs(la / 0.5 - round(la / 0.5)) < 1e-9 and abs(lb / 0.5 - round(lb / 0.5)) < 1e-9
           and abs(dv[1]) < 1e-9 and norm(dv) > 0.4,
           "in plan with Local and GRID, the centre square steps along the column's own axes "
           "(%.4f, %.4f)" % (la, lb))
        wl = await setup("function(){return window.__a3dWall([[0,0],[3,4]],0.3,3,'center',false);}")
        g = await gizmo()
        fx = g['frame']['x'] if g else [0, 0, 0]
        ck(g and g['frame']['mode'] == 'local' and abs(fx[0] - 0.6) < 1e-9 and abs(fx[2] - 0.8) < 1e-9,
           "Local stays chosen, and for a wall follows its direction (x = %s)" % [round(v, 4) for v in fx])
        box = await setup(BOX)
        await safe("()=>window.__t110.clearToast()")
        await menu_pick('local')
        g = await gizmo()
        tt = await safe("()=>window.__t110.toast()") or ''
        ck(g and g['frame']['mode'] == 'world' and g['frame']['fallback'] and 'no orientation' in tt,
           "for a Box, which stores no orientation, Local says so and stays World (%r)" % tt[-80:])
        await menu_pick('view')
        g = await gizmo()
        fx, fz = (g['frame']['x'], g['frame']['z']) if g else ([0, 1, 0], [0, 0, 0])
        ck(g and g['frame']['mode'] == 'view' and abs(fx[1]) < 1e-9 and abs(fz[1]) > 0.1,
           "Align to View puts X along the screen's right (level) and Y up the screen (%s, %s)" %
           ([round(v, 3) for v in fx], [round(v, 3) for v in fz]))
        s0 = await safe("(id)=>window.__t110.snap(id).pos", box)
        ax = arm(g, 'x')
        if ax:
            await drag([mid(ax), [mid(ax)[0] + 60, mid(ax)[1]]])
        s1 = await safe("(id)=>window.__t110.snap(id).pos", box)
        dv = [s1[k] - s0[k] for k in range(3)] if (s0 and s1) else [0, 0, 0]
        ck(norm(dv) > 0.2 and cross_norm(dv, fx) < 1e-9 * max(1, norm(dv)),
           "and a drag of its X arrow moves the object along the screen's right (delta %s)" % [round(v, 4) for v in dv])
        await menu_pick('world')
        g = await gizmo()
        ck(g and g['frame']['mode'] == 'world', "Align to World puts it back")
        await menu_pick('hide')
        g = await gizmo()
        stt = await safe("()=>window.__a3dGizmoState()")
        ck(g is None and stt and stt['hidden'] is True,
           "Hide Gizmo removes every handle while the object stays selected (%s)" %
           (await safe("()=>window.__a3dState().sel") == box))
        await blur()
        await palette_run(page, 'GIZMO')
        g = await gizmo()
        stt = await safe("()=>window.__a3dGizmoState()")
        ck(g is not None and stt and stt['hidden'] is False, "the GIZMO command brings it back")
        await blur()
        await palette_run(page, 'GIZMO')
        stt = await safe("()=>window.__a3dGizmoState()")
        ck(stt and stt['menu'] and [b['act'] for b in stt['menu']] == ['world', 'local', 'view', 'hide'],
           "and run again it opens the gizmo menu (%s)" % (stt and stt['menu'] and [b['act'] for b in stt['menu']]))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        # ------------------------------------------------------------------------------------
        print("\n-- 7. names")
        box = await setup(BOX)
        g = await gizmo()
        r = await rect()
        ay = arm(g, 'z')
        nm = await safe("(p)=>window.__a3dHandleUnderPoint(p[0],p[1])",
                        [r['left'] + mid(ay)[0], r['top'] + mid(ay)[1]]) if ay else None
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        nm2 = await safe("(p)=>window.__a3dHandleUnderPoint(p[0],p[1])",
                         [r['left'] + pl['xz']['c'][0], r['top'] + pl['xz']['c'][1]]) if 'xz' in pl else None
        ck(nm == 'the Y move handle' and nm2 == 'the XY move square',
           "the occlusion notice names handles by Revit's letters (%s; %s)" % (nm, nm2))

        ck(not errs, "no page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
