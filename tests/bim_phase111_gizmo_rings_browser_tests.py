#!/usr/bin/env python3
"""bim_phase111_gizmo_rings_browser_tests.py -- V111: the gizmo completed against the reference tools.

Every claim is driven with real pointer events and asserted on the model.

  1. RINGS: one full ring about each axis and one about the camera's own direction, in Revit's
     colours, the screen ring outermost; a sketch and a wall keep the vertical ring alone; in plan
     the vertical rings that are edge-on are gone and the screen ring does not duplicate the
     vertical one.
  2. NEAR AND FAR: each axis ring is about half near and half far, the screen ring is all near, and
     where a near half crosses a far half the NEAR ring takes the click. The far half is still
     reachable where nothing is in front of it.
  3. ROTATION: the screen ring turns the object about the camera direction, rigidly and by the
     angle dragged; the vertical ring still answers as V78's rotate and turns about the vertical.
  4. THE EVEN-SCALE TRIANGLE: drawn only when all three axes can scale, and a radial drag scales
     every extent by the same factor about the centre.
  5. HOVER: every handle reports itself under the cursor, by Revit's letters, and hovering moves
     and selects nothing.
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
  window.__t111={
    verts:function(id){
      var o=window.__a3dObjSnapshot(id);
      if(!o||!o.mesh)return null;
      var q=o.pos||[0,0,0];
      return o.mesh.v.map(function(v){return [v[0]+q[0],v[1]+q[1],v[2]+q[2]];});
    },
    bounds:function(id){var b=window.__a3dWorldBounds([id]);return b?{mn:b.mn.slice(),mx:b.mx.slice()}:null;},
    pos:function(id){var o=window.__a3dObjSnapshot(id);return o?o.pos.slice():null;}
  };
  return true;}"""


def norm3(a):
    return math.sqrt(sum(v * v for v in a))


def ext(b):
    return [b['mx'][k] - b['mn'][k] for k in range(3)]


def centre(b):
    return [(b['mx'][k] + b['mn'][k]) / 2 for k in range(3)]


def corners(b):
    return [[(b['mn'], b['mx'])[i][0], (b['mn'], b['mx'])[j][1], (b['mn'], b['mx'])[k][2]]
            for i in (0, 1) for j in (0, 1) for k in (0, 1)]


def rodrigues(A, t):
    c, s, k = math.cos(t), math.sin(t), 1 - math.cos(t)
    x, y, z = A
    return [[c + x * x * k, x * y * k - z * s, x * z * k + y * s],
            [y * x * k + z * s, c + y * y * k, y * z * k - x * s],
            [z * x * k - y * s, z * y * k + x * s, c + z * z * k]]


def rotate_about(pts, O, A, t):
    R = rodrigues(A, t)
    return [[O[i] + sum(R[i][j] * (p[j] - O[j]) for j in range(3)) for i in range(3)] for p in pts]


def set_err(expect, got):
    if not got:
        return 1e9

    def d(p, q):
        return math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(3)))
    return max(max(min(d(p, q) for q in got) for p in expect),
               max(min(d(p, q) for q in expect) for p in got))


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

        has = await safe("()=>!!window.__acad3dV111")
        ck(bool(has), "__acad3dV111 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        await safe(HELPERS)

        async def gizmo():
            return await safe("()=>window.__a3dGizmo()")

        async def rect():
            return await safe("()=>window.__a3dCanvasRect()")

        async def hover(p):
            r = await rect()
            if not r or p is None:
                return None
            await page.mouse.move(r['left'] + p[0], r['top'] + p[1])
            await page.wait_for_timeout(180)
            return await safe("()=>window.__a3dGizmoHover()")

        async def drag(pts, steps=8):
            r = await rect()
            if not r or not pts or any(p is None for p in pts):
                print('      (drag skipped: no target)')
                return False
            await page.mouse.move(r['left'] + pts[0][0], r['top'] + pts[0][1])
            await page.mouse.down()
            for p in pts[1:]:
                await page.mouse.move(r['left'] + p[0], r['top'] + p[1], steps=steps)
            await page.mouse.up()
            await page.wait_for_timeout(300)
            return True

        async def setup(js, view='3d', ortho=False):
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")
            oid = await safe("(a)=>{window.__a3dTestSetObjs([]);var id=(" + js + ")();"
                             "window.__a3dSelectFor([id]);"
                             "if(a.view==='plan')window.__a3dSetPlanView();else window.__a3dSet3DView();"
                             "window.__a3dSnapSet({point:false,grid:false,ortho:a.ortho,gridSize:0.5});"
                             "window.__a3dZoomToSelection();return id;}", {'view': view, 'ortho': ortho})
            await page.wait_for_timeout(450)
            return oid

        BOX = "function(){return window.__a3dAdd('box',{Length:10,Width:6,Height:8}).id;}"
        WALL = "function(){return window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false);}"

        def by_axis(g, key='rings'):
            return {r['axis']: r for r in (g or {}).get(key, [])}

        # -------------------------------------------------------------------------------
        print("\n-- 1. a ring about every axis, and one about the camera")
        box = await setup(BOX)
        g = await gizmo()
        rings = by_axis(g)
        ck(sorted(rings) == ['view', 'x', 'y', 'z'],
           "four rings on a solid: X, Y, Z and the screen ring (%s)" % sorted(rings))
        ck(rings.get('x', {}).get('col') == '#ff5f56' and rings.get('z', {}).get('col') == '#5ec98a'
           and rings.get('y', {}).get('col') == '#4ea1ff' and rings.get('view', {}).get('lab') == 'VIEW',
           "in Revit's colours, the screen ring neutral (%s)" %
           {k: (v['lab'], v['col']) for k, v in rings.items()})
        ck(rings.get('y', {}).get('kind') == 'vertical' and rings.get('x', {}).get('kind') == 'tilt'
           and rings.get('view', {}).get('kind') == 'view',
           "the vertical one is still the rotate ring every selection gets (%s)" %
           {k: v['kind'] for k, v in rings.items()})
        rv = await safe("()=>window.__a3dGizmoRing()")
        ck(rv is not None and 'y' in rings and abs(rings['y']['R'] - rv['R']) < 1e-9,
           "and it is the SAME ring V78 publishes, at the same radius (%s vs %s)"
           % (rings.get('y', {}).get('R'), rv and rv['R']))
        axmax = [rings[k]['rmax'] for k in ('x', 'y', 'z') if k in rings]
        ck('view' in rings and axmax and rings['view']['rmax'] > max(axmax) * 1.1,
           "the screen ring is drawn outside the axis rings (%s px vs %s)" %
           (rings.get('view', {}).get('rmax'), [round(v) for v in axmax]))

        wall = await setup(WALL)
        gw = await gizmo()
        ck(sorted(by_axis(gw)) == ['y'] and by_axis(gw)['y']['kind'] == 'vertical',
           "a wall keeps the vertical ring and gets no others -- it turns about the vertical and "
           "nothing else (%s)" % sorted(by_axis(gw)))
        sk = await setup("function(){return window.__a3dSketch('rect',[[0,0],[4,2]]);}")
        gs = await gizmo()
        ck(sorted(by_axis(gs)) == ['y'], "and so does a sketch (%s)" % sorted(by_axis(gs)))

        box = await setup(BOX, view='plan')
        gp = await gizmo()
        rp = by_axis(gp)
        ck(sorted(rp) == ['y'],
           "in PLAN only the vertical ring survives: the other two are edge-on, and the screen "
           "ring would be the vertical one drawn twice (%s)" % sorted(rp))

        # -------------------------------------------------------------------------------
        print("\n-- 2. near and far halves")
        box = await setup(BOX)
        g = await gizmo()
        rings = by_axis(g)
        fr = {k: rings[k]['near'] / float(rings[k]['n']) for k in ('x', 'y', 'z') if k in rings}
        ck(len(fr) == 3 and all(0.25 < v < 0.75 for v in fr.values()),
           "each axis ring is about half in front of the object and half behind it (%s)" %
           {k: round(v, 2) for k, v in fr.items()})
        ck('view' in rings and rings['view']['near'] == rings['view']['n'],
           "the screen ring faces the camera, so all of it is near (%s of %s)" %
           (rings.get('view', {}).get('near'), rings.get('view', {}).get('n')))
        # The flag is checked against the depth the projection reports -- the measure the renderer
        # sorts by -- so a flag that is inverted, constant, or read off some other vector cannot
        # agree with what is actually in front.
        depth = await safe("""(o)=>{
          const g=window.__a3dGizmo(),out={};
          g.rings.forEach(r=>{
            if(r.kind==='view')return;
            let nearW=-1e9,farW=1e9,nn=0,nf=0;
            for(let i=0;i<r.pts.length;i++){
              const t=i*3/(r.n-1)*Math.PI*2;   // the ring is sampled n-1 times round
              const p=[o[0]+r.B[0]*Math.cos(t)*r.R+r.C[0]*Math.sin(t)*r.R,
                       o[1]+r.B[1]*Math.cos(t)*r.R+r.C[1]*Math.sin(t)*r.R,
                       o[2]+r.B[2]*Math.cos(t)*r.R+r.C[2]*Math.sin(t)*r.R];
              const w=window.__a3dProject(p).w;
              if(r.pts[i][2]){nearW=Math.max(nearW,w);nn++;}else{farW=Math.min(farW,w);nf++;}
            }
            out[r.axis]={nearW:nearW,farW:farW,nn:nn,nf:nf};
          });
          return out;}""", g['origin'] if g else [0, 0, 0])
        okdepth = depth and len(depth) >= 3 and all(
            v['nn'] > 0 and v['nf'] > 0 and v['nearW'] <= v['farW'] + 1e-6 for v in depth.values())
        ck(okdepth,
           "and every sample flagged near really is nearer the camera than every sample flagged "
           "far, measured by the projection's own depth (%s)" %
           {k: [round(v['nearW'], 3), round(v['farW'], 3)] for k, v in (depth or {}).items()})

        # The probe sits ON the far segment, with a near segment of another ring a few pixels
        # away: the near ring must still win, which a picker that ignored the halves could not do
        # -- it would answer with whichever segment is closest, and that is the far one.
        cross = await safe("""()=>{
          const g=window.__a3dGizmo();
          function segs(r){const o=[];for(let i=0;i<r.pts.length-1;i++)
            o.push({a:r.pts[i],b:r.pts[i+1],near:!!(r.pts[i][2]&&r.pts[i+1][2]),axis:r.axis});return o;}
          function d(p,a,b){const vx=b[0]-a[0],vy=b[1]-a[1],L2=vx*vx+vy*vy||1;
            let t=((p[0]-a[0])*vx+(p[1]-a[1])*vy)/L2;t=Math.max(0,Math.min(1,t));
            return Math.hypot(p[0]-(a[0]+vx*t),p[1]-(a[1]+vy*t));}
          const all=[];g.rings.forEach(r=>segs(r).forEach(s=>all.push(s)));
          for(const s of all){
            if(s.near)continue;
            const p=[(s.a[0]+s.b[0])/2,(s.a[1]+s.b[1])/2];
            for(const t of all){
              if(!t.near||t.axis===s.axis)continue;
              const dn=d(p,t.a,t.b);
              if(dn>0.6&&dn<4)return {p:p,near:t.axis,far:s.axis,dn:dn};
            }
          }
          return null;}""")
        if cross:
            hit = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", cross['p'])
            want = 'rotate' if cross['near'] == 'y' else 'tilt:' + cross['near']
            ck(hit == want,
               "where the near half of the %s ring crosses the far half of the %s ring, the NEAR "
               "one takes the click (%s)" % (cross['near'], cross['far'], hit))
        else:
            ck(False, "a crossing of a near half and a far half could be found to test precedence")

        farpt = await safe("""()=>{
          const g=window.__a3dGizmo(),r=g.rings.filter(x=>x.axis==='x')[0];
          function near(p){return g.rings.some(q=>{for(let i=0;i<q.pts.length-1;i++){
              if(!(q.pts[i][2]&&q.pts[i+1][2]))continue;
              const a=q.pts[i],b=q.pts[i+1],vx=b[0]-a[0],vy=b[1]-a[1],L2=vx*vx+vy*vy||1;
              let t=((p[0]-a[0])*vx+(p[1]-a[1])*vy)/L2;t=Math.max(0,Math.min(1,t));
              if(Math.hypot(p[0]-(a[0]+vx*t),p[1]-(a[1]+vy*t))<12)return true;}
            return false;});}
          for(let i=0;i<r.pts.length;i++)if(!r.pts[i][2]&&!near(r.pts[i]))return [r.pts[i][0],r.pts[i][1]];
          return null;}""")
        hitf = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", farpt) if farpt else None
        ck(hitf == 'tilt:x',
           "and the far half is still reachable where nothing is in front of it (%s)" % hitf)

        # -------------------------------------------------------------------------------
        print("\n-- 3. the screen ring turns the object about the camera")
        box = await setup(BOX, ortho=True)
        g = await gizmo()
        vr = by_axis(g).get('view')
        A = vr['A'] if vr else None
        ck(A is not None, "there is a screen ring to turn the object by")
        b0 = await safe("(id)=>window.__t111.bounds(id)", box)
        O = g['origin'] if g else [0, 0, 0]
        proj = await safe("(a)=>{const p=window.__a3dProject(a.o),q=window.__a3dProject("
                          "[a.o[0]+a.A[0],a.o[1]+a.A[1],a.o[2]+a.A[2]]);"
                          "return {d:Math.hypot(q.x-p.x,q.y-p.y),w:p.w-q.w};}",
                          {'o': O, 'A': A}) if A else None
        ck(proj is not None and proj['d'] < 1.5 and proj['w'] > 0.5,
           "its axis points AT the camera: a world unit along it projects to the same pixel and "
           "comes nearer (%s px, %s nearer)" %
           (proj and round(proj['d'], 3), proj and round(proj['w'], 3)))
        pts = [await safe("(a)=>window.__a3dGizmoArcPoint(a[0],a[1])", ['view', d]) for d in (0, 10, 20, 30)]
        hitv = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", pts[0]) if pts[0] else None
        ck(hitv == 'tilt:view', "the screen ring picks as itself (%s)" % hitv)
        await drag(pts, steps=6)
        vv = await safe("(id)=>window.__t111.verts(id)", box)
        cs = corners(b0) if b0 else []
        good = set_err(rotate_about(cs, O, A, math.radians(30)), vv) if vv else 1e9
        bad = set_err(rotate_about(cs, O, A, math.radians(-30)), vv) if vv else 0
        ck(good < 1e-6 and bad > 0.01,
           "dragging it 30 degrees turns the box rigidly about the camera's own direction "
           "(error %.2e; the opposite turn is off by %.3f)" % (good, bad))

        # The object must turn the way the CURSOR swept on screen, which is what a ring drawn
        # from a left-handed basis gets backwards while every angle it reports still agrees with
        # itself. Measured from the screen sweep and from a vertex, with nothing in common.
        # a pad, so the mesh exists before the drag as well as after: a parametric Box has none
        # until something transforms it, and this check needs the same vertex at both ends.
        pad = await setup("function(){window.__a3dSketch('rect',[[0,0],[6,4]]);return window.__a3dPad(3);}",
                          ortho=True)
        g = await gizmo()
        rv2 = by_axis(g).get('view')
        v0 = await safe("(id)=>window.__t111.verts(id)", pad)
        sweep = None
        if rv2 and v0:
            p = rv2['pts']
            i0, i1 = 2, 2 + max(2, len(p) // 8)
            if i1 < len(p):
                a0 = math.atan2(-(p[i0][1] - g['oy']), p[i0][0] - g['ox'])
                a1 = math.atan2(-(p[i1][1] - g['oy']), p[i1][0] - g['ox'])
                dsw = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
                await drag([[p[i0][0], p[i0][1]], [p[i1][0], p[i1][1]]], steps=6)
                v1 = await safe("(id)=>window.__t111.verts(id)", pad)
                if v1 and len(v1) == len(v0):
                    A2, O2 = rv2['A'], g['origin']

                    def comp(v):
                        w = [v[i] - O2[i] for i in range(3)]
                        d = sum(w[i] * A2[i] for i in range(3))
                        return [w[i] - d * A2[i] for i in range(3)]
                    k = max(range(len(v0)), key=lambda i: norm3(comp(v0[i])))
                    a, b = comp(v0[k]), comp(v1[k])
                    crossA = sum(A2[i] * (a[(i + 1) % 3] * b[(i + 2) % 3] - a[(i + 2) % 3] * b[(i + 1) % 3])
                                 for i in range(3))
                    sweep = {'cursor': dsw, 'model': crossA}
        ck(sweep is not None and abs(sweep['cursor']) > 0.05 and sweep['cursor'] * sweep['model'] > 0,
           "and it turns the way the cursor swept round the gizmo, not the other way (%s)" %
           (sweep and {k: round(v, 4) for k, v in sweep.items()}))

        box = await setup(BOX, ortho=True)
        g = await gizmo()
        O = g['origin'] if g else [0, 0, 0]
        b0 = await safe("(id)=>window.__t111.bounds(id)", box)
        pts = [await safe("(d)=>window.__a3dGizmoRingPoint(d)", d) for d in (20, 50, 80, 110)]
        hitz = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", pts[0]) if pts[0] else None
        await drag(pts, steps=6)
        vv = await safe("(id)=>window.__t111.verts(id)", box)
        cs = corners(b0) if b0 else []
        gz = set_err(rotate_about(cs, O, [0, 1, 0], math.radians(-90)), vv) if vv else 1e9
        ck(hitz == 'rotate' and gz < 1e-6,
           "the vertical ring still answers as V78's rotate and turns about the vertical "
           "(%s, error %.2e)" % (hitz, gz))

        # -------------------------------------------------------------------------------
        print("\n-- 4. the even-scale triangle")
        box = await setup(BOX, ortho=True)
        g = await gizmo()
        ck(bool(g and g['uniform'] and len(g['uniform']['tri']) == 3 and len(g['scales']) == 3),
           "a solid with three scalable axes gets the triangle, and only then (%s boxes)" %
           (g and len(g['scales'])))
        hitu = await safe("(p)=>window.__a3dGizmoAt(p[0],p[1])", g['uniform']['c']) if (g and g['uniform']) else None
        ck(hitu == 'uniform', "which picks as itself (%s)" % hitu)
        for factor in (1.5, 0.6):
            box = await setup(BOX, ortho=True)
            g = await gizmo()
            if not (g and g['uniform'] and g['scales']):
                ck(False, "the triangle is there to drag by %s" % factor)
                continue
            b0 = await safe("(id)=>window.__t111.bounds(id)", box)
            c = g['uniform']['c']
            dx, dy = c[0] - g['ox'], c[1] - g['oy']
            L = math.hypot(dx, dy) or 1
            end = [g['ox'] + dx / L * (L * factor), g['oy'] + dy / L * (L * factor)]
            await drag([c, end])
            b1 = await safe("(id)=>window.__t111.bounds(id)", box)
            e0, e1 = (ext(b0), ext(b1)) if (b0 and b1) else ([1, 1, 1], [0, 0, 0])
            c0, c1 = (centre(b0), centre(b1)) if (b0 and b1) else ([0, 0, 0], [1, 1, 1])
            ck(all(abs(e1[k] - factor * e0[k]) < 1e-9 for k in range(3))
               and max(abs(c1[k] - c0[k]) for k in range(3)) < 1e-9,
               "a radial drag to %s of its distance scales every extent by %s about the centre, "
               "in and out (%s -> %s)" % (factor, factor,
                                          [round(v, 3) for v in e0], [round(v, 3) for v in e1]))
        sk = await setup("function(){return window.__a3dSketch('rect',[[0,0],[4,2]]);}")
        gsk = await gizmo()
        ck(gsk is not None and gsk['uniform'] is None,
           "a sketch, which scales in two directions only, gets no triangle -- it would be a line")
        wall = await setup(WALL)
        gw2 = await gizmo()
        ck(gw2 is not None and gw2['uniform'] is None, "and a wall, which does not scale, gets none")

        # -------------------------------------------------------------------------------
        print("\n-- 5. hover")
        box = await setup(BOX)
        g = await gizmo()
        arm = ([a for a in (g or {}).get('arms', []) if a['axis'] == 'x'] or [None])[0]
        pl = {p['k']: p for p in (g or {}).get('planes', [])}
        sc = {s['axis']: s for s in (g or {}).get('scales', [])}
        want = [
            (arm and [(arm['x0'] + arm['x1']) / 2, (arm['y0'] + arm['y1']) / 2], 'axis:x', 'X MOVE HANDLE'),
            (pl.get('xz', {}).get('c'), 'plane:xz', 'XY MOVE SQUARE'),
            (sc.get('x') and [sc['x']['x'], sc['x']['y']], 'scale:x', 'X SCALE BOX'),
            ((g or {}).get('uniform') and g['uniform']['c'], 'uniform', 'EVEN SCALE TRIANGLE'),
            (g and [g['centre']['x'], g['centre']['y']], 'centre', 'FREE-MOVE SQUARE'),
        ]
        for p, key, name in want:
            h = await hover(p) if p else None
            ck(h is not None and h['key'] == key and h['name'] == name,
               "the cursor over %s reports it (%s)" % (key, h))
        ringpt = await safe("(a)=>window.__a3dGizmoArcPoint(a[0],a[1])", ['x', 225])
        h = await hover(ringpt)
        ck(h is not None and h['key'] == 'tilt:x' and h['name'] == 'X ROTATE RING',
           "and a rotation ring names itself by Revit's letter (%s)" % h)
        vpt = await safe("(a)=>window.__a3dGizmoArcPoint(a[0],a[1])", ['view', 90])
        h = await hover(vpt)
        ck(h is not None and h['key'] == 'tilt:view' and h['name'] == 'SCREEN ROTATE RING',
           "the screen ring calls itself the screen ring (%s)" % h)
        p0 = await safe("(id)=>window.__t111.pos(id)", box)
        sel0 = await safe("()=>window.__a3dState().sel")
        r = await rect()
        away = [g['ox'] + (g['ox'] > r['width'] / 2 and -1 or 1) * 330, g['oy'] + 300] if g else [40, 40]
        h = await hover(away)
        p1 = await safe("(id)=>window.__t111.pos(id)", box)
        sel1 = await safe("()=>window.__a3dState().sel")
        ck(h is not None and h['key'] is None and p0 == p1 and sel0 == sel1 == box,
           "off every handle it reports nothing, and hovering has moved and selected nothing (%s)" % h)

        ck(not errs, "no page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
