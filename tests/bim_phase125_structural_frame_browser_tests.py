#!/usr/bin/env python3
"""bim_phase125_structural_frame_browser_tests.py -- V125: the structural object model and a frame solve.

PIPELINE, Track B item 1: supports, loads, load combinations and results. The analytical model is
derived from the live columns and beams; the solve is the direct stiffness method. Every number is
checked against a closed form, an independent solve, or equilibrium -- never against the solver's own
earlier answer (V104: a round trip proves consistency, not correctness).

  1. THE MODEL: nodes, supports and why, section properties and modulus from the material, a beam
     that meets a column part way up splits it, a secondary beam splits its girder, walls are named
     as not in the frame.
  2. CLOSED FORMS: a cantilever column (PL^3/3EI, PL) in both planes; a simply supported beam (wL^2/8,
     5wL^4/384EI, wL/2 a side; Pab/L at the load); pinned ends put no moment in the columns.
  3. AN INDEPENDENT SOLVE: a fixed-base portal under a lateral load against a plane-frame stiffness
     solve written here, in Python, from the textbook.
  4. LOADS: self-weight = rho A g L; the combinations' factors; each case alone.
  5. REFUSALS: nothing holding the frame up, and a sway mechanism, are refused by name; no NaN.
  6. PROPERTIES: a column's support and a beam's end connections, loads added and removed through the
     Structural page, one undo step each; a bad load refused; the Analysis page's settings.
  7. THE DISPLAY: ANALYZE from the command line and the toolbar; the diagram drawn from the solve and
     labelled with its peak; out of date the moment the model changes; ANALYZEOFF; SUPPORT and LOAD
     open Properties at their fields.
  8. KEPT: loads survive a reload and a copy; the schedules read the same solve.

The harness never waits without a bound (V123).
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
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


def rel(a, b, tol=1e-9):
    if a is None or b is None:
        return False
    return abs(a - b) <= tol * max(1.0, abs(b))


def saint_venant_J(hy, hz):
    a, b = max(hy, hz), min(hy, hz)
    return a * b ** 3 * (1 / 3 - 0.21 * (b / a) * (1 - (b / a) ** 4 / 12))


def solve_linear(A, b):
    """Gaussian elimination with partial pivoting -- the reference, independent of the app's banded
    Cholesky."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n + 1):
                M[r][c] -= f * M[i][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][c] * x[c] for c in range(i + 1, n))) / M[i][i]
    return x


def portal_2d(h, L, Ec, Ac, Ic, Eb, Ab, Ib, P):
    """A fixed-base portal in its own plane, x across and y up: the textbook plane-frame stiffness
    (u, v, theta at each node), assembled and solved here. Returns the sway of the loaded top and the
    base moments."""
    nodes = [(0, 0), (0, h), (L, h), (L, 0)]
    els = [(0, 1, Ec, Ac, Ic), (1, 2, Eb, Ab, Ib), (3, 2, Ec, Ac, Ic)]
    K = [[0.0] * 12 for _ in range(12)]
    for (i, j, E, A, I) in els:
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        Le = math.hypot(x2 - x1, y2 - y1)
        c, s = (x2 - x1) / Le, (y2 - y1) / Le
        a, b1, b2, b3, b4 = E * A / Le, 12 * E * I / Le ** 3, 6 * E * I / Le ** 2, 4 * E * I / Le, 2 * E * I / Le
        k = [[a, 0, 0, -a, 0, 0], [0, b1, b2, 0, -b1, b2], [0, b2, b3, 0, -b2, b4],
             [-a, 0, 0, a, 0, 0], [0, -b1, -b2, 0, b1, -b2], [0, b2, b4, 0, -b2, b3]]
        T = [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
             [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]]
        kg = [[sum(T[m][r] * sum(k[m][n] * T[n][q] for n in range(6)) for m in range(6)) for q in range(6)] for r in range(6)]
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        for r in range(6):
            for q in range(6):
                K[d[r]][d[q]] += kg[r][q]
    free = [3, 4, 5, 6, 7, 8]
    F = [0.0] * 12
    F[3] = P
    x = solve_linear([[K[r][q] for q in free] for r in free], [F[r] for r in free])
    D = [0.0] * 12
    for i, r in enumerate(free):
        D[r] = x[i]
    R = [sum(K[r][q] * D[q] for q in range(12)) - F[r] for r in range(12)]
    return {'sway': D[3], 'M0': R[2], 'M3': R[11], 'H0': R[0], 'H3': R[9]}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
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

        has = await safe("()=>!!window.__acad3dV125")
        ck(bool(has), "__acad3dV125 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def command(name):
            await blur()
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type(name)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(400)

        async def scene(js):
            """a fresh model: levels 0 and 1 (3 m), empty undo, the display off, self-weight off"""
            return await safe("""()=>{window.__a3dTestSetObjs([]);
              var lv=window.__a3dLevels();if(lv.length<2)window.__a3dAddLevel();
              window.__a3dSetLevel(window.__a3dLevels()[0].id);
              window.__a3dStructSettings({show:false,selfWeight:false,combo:'D',diagram:'M',deflected:true,res:null});
              window.__a3dTestClearUndo();window.__a3dSelectFor([]);
              var up=function(){window.__a3dSetLevel(window.__a3dLevels()[1].id);};
              var down=function(){window.__a3dSetLevel(window.__a3dLevels()[0].id);};
              var set=function(id,st){window.__a3dStructPut(id,st);};
              return (""" + js + """)();}""")

        # a test-only setter: through the same edit Properties uses, so it is one undo step
        await safe("""()=>{window.__a3dStructPut=function(id,st){
          var o=window.__a3dObjSnapshot(id);if(!o)return false;
          window.__a3dSelectFor([id]);window.__a3dStructEditFor(id,st);window.__a3dSelectFor([]);return true;};return 1;}""")

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the analytical model")
            r = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.3,3),b=window.__a3dColumnAt([6,0],0,0.4,0.3,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);down();
              window.__a3dWall([[0,4],[6,4]],0.2,3,'center',false);
              return {a:a,b:b,bm:bm,m:window.__a3dStructModel()};}""")
            m = r and r['m']
            ck(m and len(m['nodes']) == 4 and len(m['els']) == 3,
               "two columns and a beam between their tops: four nodes, three members (%s)" % (m and [len(m['nodes']), len(m['els'])]))
            sups = m and sorted([(n['sup'], n['why']) for n in m['nodes'] if n['sup']])
            ck(sups == [('fixed', 'on the lowest level'), ('fixed', 'on the lowest level')],
               "each column's base is Fixed, on the lowest level, and says why (%s)" % sups)
            col = m and [e for e in m['els'] if e['kind'] == 'column'][0]
            beam = m and [e for e in m['els'] if e['kind'] == 'beam'][0]
            # a column: local y is its width direction (X at no rotation): hy = width 0.4, hz = depth 0.3
            ck(col and rel(col['A'], 0.12) and rel(col['Iz'], 0.3 * 0.4 ** 3 / 12) and rel(col['Iy'], 0.4 * 0.3 ** 3 / 12)
               and rel(col['J'], saint_venant_J(0.4, 0.3)),
               "a 400 x 300 column: A, both second moments, and J by the Saint-Venant series for a rectangle")
            ck(beam and rel(beam['Iz'], 0.3 * 0.5 ** 3 / 12) and rel(beam['Iy'], 0.5 * 0.3 ** 3 / 12) and rel(beam['ey'][1], 1),
               "a 300 x 500 beam bends about its strong axis under gravity: its local y is up, Iz = b d^3/12")
            ck(col and rel(col['E'], 32e6) and rel(col['G'], 32e6 / (2 * 1.17)) and rel(col['rho'], 2400),
               "E from the Concrete card's 32 GPa (in kPa), G = E / 2(1 + 0.17), density 2400 (%s)" % (col and col['E']))
            ck(m and m['notAnalysed'].get('wall') == 1, "the wall is named as not in the frame (%s)" % (m and m['notAnalysed']))
            r = await scene("""function(){
              var c=window.__a3dColumnAt([0,0],0,0.4,0.4,6);up();
              var g=window.__a3dBeam([0,0],[8,0],0.3,0.6),s=window.__a3dBeam([4,0],[4,5],0.25,0.45);
              return window.__a3dStructModel();}""")
            els = r and r['els'] or []
            ck(len([e for e in els if e['kind'] == 'column']) == 2 and len([e for e in els if e['name'].startswith('Beam_1') or e['L'] == 4]) >= 2,
               "a 6 m column met at 3 m by a beam is split there, and the girder a secondary beam lands on is split under it (%s)"
               % sorted([(e['name'], round(e['L'], 3)) for e in els]))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. closed forms")
            r = await scene("""function(){
              var c=window.__a3dColumnAt([0,0],0,0.4,0.3,3);
              set(c,{loads:[{lc:'D',kind:'lateral',v:10,dir:'x'},{lc:'L',kind:'lateral',v:4,dir:'z'}]});
              return {c:c,d:window.__a3dStructSolve('D',false),l:window.__a3dStructSolve('L',false),m:window.__a3dStructModel()};}""")
            if r and not r['d'].get('error'):
                E, e = 32e6, r['m']['els'][0]
                tip = r['d']['disp'][[i for i, n in enumerate(r['m']['nodes']) if not n['sup']][0]]
                ck(rel(tip[0], 10 * 27 / (3 * E * e['Iz'])) and rel(abs(r['d']['members'][0]['Mz']['v']), 30),
                   "a 3 m cantilever column, 10 kN along X at its top: sway PL^3/3EI and base moment PL (%.6e m)" % tip[0])
                tipz = r['l']['disp'][[i for i, n in enumerate(r['m']['nodes']) if not n['sup']][0]]
                ck(rel(tipz[2], 4 * 27 / (3 * E * e['Iy'])) and rel(abs(r['l']['members'][0]['My']['v']), 12),
                   "and 4 kN along Z bends it about its other axis, with the other I (%.6e m)" % tipz[2])
            else:
                ck(False, "the cantilever solves (%s)" % (r and r['d']))
                ck(False, "and in its other plane")
            r = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);
              set(bm,{ends:'pinned',loads:[{lc:'D',kind:'line',v:10}]});
              var one=window.__a3dStructSolve('D',false);
              set(bm,{ends:'pinned',loads:[{lc:'D',kind:'point',v:20,at:2}]});
              var two=window.__a3dStructSolve('D',false);
              set(bm,{ends:'pinned',loads:[{lc:'D',kind:'line',v:10},{lc:'D',kind:'point',v:20,at:2}]});
              return {one:one,two:two,both:window.__a3dStructSolve('D',false),m:window.__a3dStructModel()};}""")
            if r and not r['one'].get('error') and not r['two'].get('error') and not r['both'].get('error'):
                bI = [e for e in r['m']['els'] if e['kind'] == 'beam'][0]
                EI = bI['E'] * bI['Iz']
                B = [x for x in r['one']['members'] if x['kind'] == 'beam'][0]
                ck(rel(B['Mz']['v'], 10 * 36 / 8) and rel(B['Mz']['at'], 3),
                   "a 6 m pinned beam under 10 kN/m: wL^2/8 = 45 kN.m at midspan (%s)" % B['Mz'])
                ck(rel(B['drel'], 5 * 10 * 6 ** 4 / (384 * EI)),
                   "deflecting 5wL^4/384EI from the line of its supports (%.6e m)" % B['drel'])
                Ry = sorted(round(x['R'][1], 9) for x in r['one']['reactions'])
                ck(Ry == [30.0, 30.0], "each column base carries wL/2 = 30 kN (%s)" % Ry)
                cm = [abs(x['Mz']['v']) + abs(x['My']['v']) for x in r['one']['members'] if x['kind'] == 'column']
                ck(all(v < 1e-9 for v in cm), "pinned ends put no moment into the columns (%s)" % cm)
                B2 = [x for x in r['two']['members'] if x['kind'] == 'beam'][0]
                ck(rel(B2['Mz']['v'], 20 * 2 * 4 / 6) and rel(B2['Mz']['at'], 2),
                   "20 kN at 2 m: Pab/L = 26.667 kN.m under the load (%s)" % B2['Mz'])
                # both: the peak is where the shear passes zero, x = (R1 - P) / w, between any samples
                R1 = 10 * 6 / 2 + 20 * 4 / 6
                x0 = (R1 - 20) / 10
                M0 = R1 * x0 - 10 * x0 * x0 / 2 - 20 * (x0 - 2)
                B3 = [x for x in r['both']['members'] if x['kind'] == 'beam'][0]
                ck(rel(B3['Mz']['v'], M0) and rel(B3['Mz']['at'], x0),
                   "both at once: the peak is found where the shear passes zero, %.4f kN.m at %.4f m -- not the nearest sample (%s)"
                   % (M0, x0, B3['Mz']))
            else:
                for _ in range(6):
                    ck(False, "the simply supported beam solves (%s)" % (r and [r['one'].get('error'), r['two'].get('error')]))

            # a column turned 30 degrees: the load along X splits between its two axes -- the one case
            # where the member's axes are not the model's and a transposed turn would show
            cid = await scene("""function(){var c=window.__a3dColumnAt([0,0],0,0.4,0.3,3);
              set(c,{loads:[{lc:'D',kind:'lateral',v:10,dir:'x'}]});window.__a3dSelectFor([c]);window.__a3dRefreshProps();return c;}""")
            await page.wait_for_timeout(200)
            await page.fill('[data-propf="crot"]', '30')
            await page.press('[data-propf="crot"]', 'Enter')
            await page.wait_for_timeout(300)
            r = await safe("()=>({s:window.__a3dStructSolve('D',false),m:window.__a3dStructModel()})")
            if r and not r['s'].get('error'):
                E, L, P = 32e6, 3.0, 10.0
                c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
                Iz, Iy = 0.3 * 0.4 ** 3 / 12, 0.4 * 0.3 ** 3 / 12
                dy, dz = P * c30 * L ** 3 / (3 * E * Iz), P * s30 * L ** 3 / (3 * E * Iy)
                ey, ez = (c30, 0, s30), (s30, 0, -c30)
                want = [dy * ey[0] + dz * ez[0], 0, dy * ey[2] + dz * ez[2]]
                tip = r['s']['disp'][[i for i, n in enumerate(r['m']['nodes']) if not n['sup']][0]]
                ck(rel(tip[0], want[0], 1e-9) and rel(tip[2], want[2], 1e-9) and rel(r['m']['els'][0]['ey'][0], c30, 1e-9),
                   "a column turned 30 degrees bends about both axes under a load along X: its top moves (%.6e, %.6e) as the two "
                   "cantilever formulas combine (%.6e, %.6e)" % (tip[0], tip[2], want[0], want[2]))
                mb = r['s']['members'][0]
                ck(rel(abs(mb['Mz']['v']), P * c30 * L, 1e-9) and rel(abs(mb['My']['v']), P * s30 * L, 1e-9),
                   "and its base moments are the load's two parts times the height, %.3f and %.3f kN.m, in its own axes (%s, %s)"
                   % (P * c30 * L, P * s30 * L, mb['Mz']['v'], mb['My']['v']))
            else:
                ck(False, "the turned column solves (%s)" % (r and r['s']))
            # a support set on an upper column holds the node it stands on, even with a load there
            r = await scene("""function(){var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3);up();
              var b=window.__a3dColumnAt([0,0],3,0.4,0.4,3);set(b,{support:'fixed'});
              set(a,{loads:[{lc:'D',kind:'lateral',v:10,dir:'x'}]});return window.__a3dStructSolve('D',false);}""")
            if r and not r.get('error'):
                at3 = [x for x in r['reactions'] if abs(x['p'][1] - 3) < 1e-9]
                at0 = [x for x in r['reactions'] if abs(x['p'][1]) < 1e-9]
                ck(at3 and at0 and rel(at3[0]['R'][0], -10) and abs(at0[0]['R'][0]) < 1e-9 and r['equilibrium']['err'] < 1e-9,
                   "a load on a node a support holds goes straight into that support: -10 kN there, none at the ground (%s)"
                   % (at3 and at3[0]['R'][0]))
            else:
                ck(False, "the stacked columns solve (%s)" % r)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. an independent solve: a fixed-base portal under a lateral load")
            r = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);
              set(a,{loads:[{lc:'D',kind:'lateral',v:10,dir:'x'}]});
              return {s:window.__a3dStructSolve('D',false),m:window.__a3dStructModel(),a:a};}""")
            if r and not r['s'].get('error'):
                cI = [e for e in r['m']['els'] if e['kind'] == 'column'][0]
                bI = [e for e in r['m']['els'] if e['kind'] == 'beam'][0]
                ref = portal_2d(3, 6, cI['E'], cI['A'], cI['Iz'], bI['E'], bI['A'], bI['Iz'], 10)
                top = [i for i, n in enumerate(r['m']['nodes']) if abs(n['p'][0]) < 1e-9 and abs(n['p'][1] - 3) < 1e-9][0]
                sway = r['s']['disp'][top][0]
                ck(rel(sway, ref['sway'], 1e-9), "the sway matches the plane-frame solve to 1e-9 (%.9e vs %.9e m)" % (sway, ref['sway']))
                base = {round(x['p'][0]): x['R'] for x in r['s']['reactions']}
                ck(rel(base[0][5], ref['M0'], 1e-8) and rel(base[6][5], ref['M3'], 1e-8)
                   and rel(base[0][0], ref['H0'], 1e-8) and rel(base[6][0], ref['H3'], 1e-8),
                   "and so do both base moments and horizontal reactions (%.6f, %.6f kN.m)" % (base[0][5], base[6][5]))
            else:
                ck(False, "the portal solves (%s)" % (r and r['s']))
                ck(False, "and its reactions")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. loads and combinations")
            r = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);
              set(bm,{loads:[{lc:'D',kind:'line',v:10},{lc:'L',kind:'line',v:5}]});
              return {sw:window.__a3dStructSolve('1.4D',true),c2:window.__a3dStructSolve('1.2D+1.6L',false),
                      l:window.__a3dStructSolve('L',false),sl:window.__a3dStructSolve('D+L',false),m:window.__a3dStructModel()};}""")
            if r and all(not r[k].get('error') for k in ('sw', 'c2', 'l', 'sl')):
                selfw = sum(e['rho'] * e['A'] * 9.80665 / 1000 * e['L'] for e in r['m']['els'])
                ck(rel(-r['sw']['equilibrium']['load'][1], 1.4 * (10 * 6 + selfw), 1e-9)
                   and rel(r['sw']['equilibrium']['reaction'][1], 1.4 * (10 * 6 + selfw), 1e-9),
                   "1.4D with self-weight: 1.4 x (10 kN/m x 6 m + rho A g L of every member), and the reactions carry it (%.4f kN)"
                   % r['sw']['equilibrium']['reaction'][1])
                ck(rel(r['c2']['equilibrium']['reaction'][1], (1.2 * 10 + 1.6 * 5) * 6),
                   "1.2D + 1.6L: (12 + 8) kN/m x 6 m = 120 kN (%s)" % r['c2']['equilibrium']['reaction'][1])
                ck(rel(r['l']['equilibrium']['reaction'][1], 30) and rel(r['sl']['equilibrium']['reaction'][1], 90),
                   "L alone 30 kN, D + L 90 kN")
            else:
                for _ in range(3):
                    ck(False, "the combinations solve (%s)" % r)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. refusals")
            r = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3);set(a,{support:'free'});
              var one=window.__a3dStructSolve('D',false);
              var b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);set(a,{support:'pinned'});set(b,{support:'pinned'});up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);set(bm,{ends:'pinned',loads:[{lc:'D',kind:'line',v:10}]});
              return {none:one,mech:window.__a3dStructSolve('D',false)};}""")
            ck(r and r['none'].get('error', '').startswith('Nothing holds the frame up'),
               "a column set Free with nothing else is refused: nothing holds the frame up (%r)" % (r and r['none'].get('error')))
            ck(r and 'unstable' in (r['mech'].get('error') or '') and 'freely' in r['mech']['error'] and r['mech'].get('node') is not None,
               "pinned bases under a pinned beam is a sway mechanism: refused, naming the node and how it moves (%r)" % (r and r['mech'].get('error')))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Properties: the Structural and Analysis pages")
            ids = await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);down();
              window.__a3dTestClearUndo();return {a:a,b:b,bm:bm};}""")
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", ids['a'])
            await page.wait_for_timeout(250)
            opts = await safe("""()=>{var s=document.querySelector('[data-propstr="support"]');
              return s?[].map.call(s.options,function(o){return o.value+'|'+o.textContent;}):null;}""")
            ck(opts and opts[0].startswith('|Automatic (Fixed, on the lowest level)') and [o.split('|')[0] for o in opts] == ['', 'fixed', 'pinned', 'free'],
               "a column's Structural page offers its support, Automatic saying what it is and why (%s)" % (opts and opts[0]))
            await page.select_option('[data-propstr="support"]', 'pinned')
            await page.wait_for_timeout(250)
            st = await safe("(id)=>window.__a3dStructOf(id)", ids['a'])
            dep = await safe("()=>window.__a3dDocs.undoDepth().undo")
            ck(st and st.get('support') == 'pinned' and dep == 1, "Pinned is stored on the column, one undo step (%s, %s)" % (st, dep))
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(200)
            ck((await safe("(id)=>window.__a3dStructOf(id)", ids['a'])).get('support') is None, "and Undo takes it back to Automatic")
            # a lateral load, through the form
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", ids['a'])
            await page.wait_for_timeout(200)
            await page.fill('[data-propstrnew="v"]', '12.5')
            await page.select_option('[data-propstrnew="dir"]', 'z')
            await page.click('[data-propstract="addload"]')
            await page.wait_for_timeout(250)
            st = await safe("(id)=>window.__a3dStructOf(id)", ids['a'])
            ck(st and st.get('loads') == [{'lc': 'D', 'kind': 'lateral', 'v': 12.5, 'dir': 'z'}],
               "Add load puts a 12.5 kN dead lateral load along Z on the column (%s)" % (st and st.get('loads')))
            # a beam: its ends, and a bad point load refused
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", ids['bm'])
            await page.wait_for_timeout(200)
            await page.select_option('[data-propstr="ends"]', 'pinned')
            await page.wait_for_timeout(200)
            await page.select_option('[data-propstrnew="kind"]', 'point')
            await page.fill('[data-propstrnew="v"]', '20')
            await page.fill('[data-propstrnew="at"]', '99')
            await page.click('[data-propstract="addload"]')
            await page.wait_for_timeout(250)
            st = await safe("(id)=>window.__a3dStructOf(id)", ids['bm'])
            ck(st and st.get('ends') == 'pinned' and not st.get('loads') and 'between 0 and 6' in await toast(),
               "a beam's ends set Pinned; a point load at 99 m on a 6 m beam is refused and says the range (%r)" % await toast())
            await page.fill('[data-propstrnew="at"]', '2')
            await page.click('[data-propstract="addload"]')
            await page.wait_for_timeout(250)
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", ids['bm'])
            await page.wait_for_timeout(200)
            await page.click('[data-propstrdel="0"]')
            await page.wait_for_timeout(250)
            st = await safe("(id)=>window.__a3dStructOf(id)", ids['bm'])
            ck(st and st.get('loads') == [] and 'removed' in await toast(),
               "at 2 m it is added, and the remove button takes it off (%s)" % (st and st.get('loads')))
            # the Analysis page with nothing selected
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(250)
            combos = await safe("""()=>{var s=document.querySelector('[data-propstr="combo"]');return s?[].map.call(s.options,function(o){return o.value;}):null;}""")
            ck(combos == ['1.2D+1.6L', '1.4D', 'D+L', 'D', 'L'] and combos == await safe("()=>window.__a3dCombos()"),
               "with nothing selected, Properties' Analysis page offers the combinations (%s)" % combos)
            ck(await safe("()=>!document.querySelector('.a3d-dlg')"), "and nothing opened a window to do any of this")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. the display")
            await scene("""function(){
              var a=window.__a3dColumnAt([0,0],0,0.4,0.4,3),b=window.__a3dColumnAt([6,0],0,0.4,0.4,3);up();
              var bm=window.__a3dBeam([0,0],[6,0],0.3,0.5);set(bm,{ends:'pinned',loads:[{lc:'D',kind:'line',v:10}]});
              window.__a3dOpenView('3d');return bm;}""")
            await command('ANALYZE')
            dr = await safe("()=>window.__a3dStructDrawn()")
            stt = await safe("()=>window.__a3dStructSettings()")
            ck(stt and stt['show'] and stt['current'] and dr and not dr['stale'] and dr['lines'] == 3 and dr['diagPts'] > 20,
               "ANALYZE on the command line solves and draws: three analytical lines and the moment diagram (%s)" % dr)
            lab = dr and [x for x in dr['labels'] if x['member'].startswith('Beam')]
            ck(lab and abs(lab[0]['v'] - 45) < 1e-9 and dr['caption'].startswith('D  '),
               "the beam is labelled with its peak, the solve's 45.0 kN.m, and the caption names the combination (%s)" % (lab, ))
            ck('Largest moment 45.0' in await toast() and 'Loads 60.0 kN, reactions 60.0 kN' in await toast(),
               "it says the largest moment and that the reactions balance the loads (%r)" % (await toast())[-160:])
            await safe("()=>{var s=window.__a3dState();}")
            ids2 = await safe("()=>window.__a3dState().objs.filter(o=>o.bim&&o.bim.type==='beam').map(o=>o.id)")
            await safe("(id)=>{var st=window.__a3dStructOf(id);st.loads[0].v=20;window.__a3dStructPut(id,st);}", ids2[0])
            dr = await safe("()=>window.__a3dStructDrawn()")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(200)
            res = await safe("""()=>{var r=[].filter.call(document.querySelectorAll('.a3d-prow'),function(x){return x.textContent.indexOf('Result')===0;})[0];return r?r.textContent:null;}""")
            ck(dr and dr.get('stale') and 'labels' not in dr and res and 'Out of date' in res,
               "a changed load puts the display out of date: no result drawn, and Properties says so (%s, %r)" % (dr, res))
            await safe("()=>{var s=document.querySelector('[data-propstr=\"display\"]');}")
            await page.select_option('[data-propstr="display"]', 'N')
            await page.wait_for_timeout(300)
            await command('ANALYZE')
            dr = await safe("()=>window.__a3dStructDrawn()")
            ck(dr and dr['diagram'] == 'N' and not dr['stale'] and 'Axial force' in dr['caption'],
               "Display: Axial force, then ANALYZE again: current, and the axial diagram (%s)" % (dr and dr['caption']))
            await command('ANALYZEOFF')
            ck(await safe("()=>window.__a3dStructDrawn()") is None and not (await safe("()=>window.__a3dStructSettings()"))['show'],
               "ANALYZEOFF turns the display off")
            # AMENDED FOR V128: the Structure strip is the Structure discipline's; its Analyze button was
            # in the page under Architecture only through the dock's retired search popover.
            await safe("()=>window.__a3dSetDiscipline('struct')")
            acts = await safe("()=>window.__a3dDockActions()") or []
            ok = await safe("""()=>{var b=document.querySelector('#a3d-dock [data-a3dr="bim:analyze"]');if(!b)return false;
              var p=b.closest('.a3d-dockpop');if(p&&!p.classList.contains('open')){var id=p.getAttribute('data-dockpop');window.__a3dDockOpenGroup(id);}
              b.click();return true;}""")
            await page.wait_for_timeout(300)
            ck('bim:analyze' in acts and ok and (await safe("()=>window.__a3dStructSettings()"))['show'],
               "the toolbar's Analyze button, in the Structure strip, runs it too")
            await safe("()=>window.__a3dSetDiscipline('arch')")
            await safe("()=>window.__a3dSelectFor([])")
            await command('SUPPORT')
            ck('Select a column' in await toast(), "SUPPORT with nothing selected says what to select (%r)" % await toast())
            col = await safe("()=>window.__a3dState().objs.filter(o=>o.bim&&o.bim.type==='column').map(o=>o.id)[0]")
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", col)
            await command('SUPPORT')
            foc = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propstr')")
            ck(foc == 'support', "with a column selected it opens Properties at the column's support (%s)" % foc)
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", ids2[0])
            await command('LOAD')
            foc = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propstrnew')")
            ck(foc == 'v', "LOAD opens it at a new load's value (%s)" % foc)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. kept")
            sched = await safe("""()=>{window.__a3dStructSettings({combo:'D',selfWeight:false,res:null});
              return {mf:window.__a3dScheduleRows('memberforces'),re:window.__a3dScheduleRows('reactions')};}""")
            beamrow = sched and [x for x in sched['mf']['rows'] if x['kind'] == 'Beam']
            ck(beamrow and abs(beamrow[0]['mz'] - 90) < 1e-9 and len(sched['re']['rows']) == 2
               and abs(sum(x['fy'] for x in sched['re']['rows']) - 120) < 1e-9,
               "the Member Forces and Reactions schedules read the same solve (%s)" % (beamrow and beamrow[0]['mz']))
            await blur()
            await safe("(id)=>window.__a3dSelectFor([id])", ids2[0])
            await page.keyboard.press('Control+d')
            await page.wait_for_timeout(400)
            cp = await safe("()=>window.__a3dState().sel")
            cst = await safe("(id)=>window.__a3dStructOf(id)", cp)
            ck(cp and cp != ids2[0] and cst and cst.get('ends') == 'pinned' and cst.get('loads') and cst['loads'][0]['v'] == 20,
               "a copy keeps its beam's end connections and loads (%s)" % cst)
            ccol = await safe("""()=>{var c=window.__a3dState().objs.filter(o=>o.bim&&o.bim.type==='column')[0];
              window.__a3dStructPut(c.id,{support:'pinned'});window.__a3dSelectFor([c.id]);return c.id;}""")
            await blur()
            await page.keyboard.press('Control+d')
            await page.wait_for_timeout(400)
            cc = await safe("()=>window.__a3dState().sel")
            ck(cc and cc != ccol and (await safe("(id)=>window.__a3dStructOf(id)", cc)).get('support') == 'pinned',
               "and a column's copy -- rebuilt through bimCarryBim, not copied whole -- keeps its support")
            await safe("(id)=>window.__a3dSelectFor([id])", ids2[0])
            await safe("(id)=>{var st=window.__a3dStructOf(id);st.loads[0].v=7;window.__a3dStructPut(id,st);}", cp)
            ck((await safe("(id)=>window.__a3dStructOf(id)", ids2[0]))['loads'][0]['v'] == 20,
               "as its own: changing the copy's load leaves the original's")
            await page.wait_for_timeout(600)
            await page.reload()
            await page.wait_for_timeout(2300)
            st = await safe("(id)=>window.__a3dStructOf(id)", ids2[0])
            ck(st and st.get('ends') == 'pinned' and st.get('loads') and st['loads'][0]['v'] == 20,
               "and everything set survives a reload (%s)" % st)
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        ck(not errs, "zero uncaught page errors (%s)" % (errs[:3] or 'none'))
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
