#!/usr/bin/env python3
"""bim_phase127_alignment_profile_browser_tests.py -- V127: the alignment and its profile.

PIPELINE, Track B item 3. An alignment is a route of tangents and circular curves through its PIs,
stationed along itself; its profile is grades and symmetric parabolic vertical curves; a point has
a station and an offset. Every number is checked against the textbook, written out here -- never
against the app's own earlier answer -- on a route that does not run along the model's axes (V125:
a fixture along the axes agrees with a wrong rule by accident).

  1. THE HORIZONTAL GEOMETRY: deflection, T = R tan(D/2), L = R D, E = R (sec(D/2) - 1), the PC and
     PT stations and the length, for curves turning both ways, from a start station that is not 0.
  2. STATION AND OFFSET: a point set off the route at a known station and offset, on tangents and
     on arcs, left and right, reads back exactly; a point past an end says so.
  3. REFUSALS: curves that overlap, a curve longer than its leg, a closed shape, a polyline with arcs.
  4. THE PROFILE: elevations on the parabola, the grade, the high point of a crest and the low point
     of a sag at x = -g1 L / (g2 - g1), K; a profile off the alignment and overlapping vertical
     curves refused.
  5. THE GROUND: on a planar surface the TIN height is the plane's, everywhere; the ground profile
     along the route is the plane's at the route's points; off the surface there is none.
  6. THE INTERFACE: ALIGNMENT from the command line on a drawn open polyline; the Alignment and
     Profile pages, each edit one undo, a bad radius refused; Add PVI; PROFILEVIEW and STATION by
     clicking; the drawn ticks and labels; the Site button.
  7. KEPT: a copy is independent; Rotate and Mirror move the route and keep its curves; a reload
     keeps it; the schedules and the DXF read the same geometry.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, sys, traceback
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


def near(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b))


def rot(p, ang, c=(0.0, 0.0), off=(0.0, 0.0)):
    x, z = p[0] - c[0], p[1] - c[1]
    return [c[0] + x * math.cos(ang) - z * math.sin(ang) + off[0], c[1] + x * math.sin(ang) + z * math.cos(ang) + off[1]]


def route(P, R, sta0):
    """the textbook: each interior PI's deflection, T, L, E, and the PC and PT stations"""
    n = len(P)
    legs = [math.hypot(P[j + 1][0] - P[j][0], P[j + 1][1] - P[j][1]) for j in range(n - 1)]
    u = [((P[j + 1][0] - P[j][0]) / legs[j], (P[j + 1][1] - P[j][1]) / legs[j]) for j in range(n - 1)]
    out, T = [], [0.0] * n
    for i in range(1, n - 1):
        a, b = u[i - 1], u[i]
        D = abs(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))
        T[i] = R[i - 1] * math.tan(D / 2)
        out.append({'D': D, 'T': T[i], 'L': R[i - 1] * D, 'E': R[i - 1] * (1 / math.cos(D / 2) - 1),
                    'turn': 1 if a[0] * b[1] - a[1] * b[0] > 0 else -1})
    s, k = sta0, 0
    for j in range(n - 1):
        s += legs[j] - T[j] - T[j + 1]
        if j + 1 < n - 1:
            out[k]['pc'] = s
            s += out[k]['L']
            out[k]['pt'] = s
            k += 1
    return out, s


def parabola(pvi_prev, pvi, pvi_next, s):
    g1 = (pvi['elev'] - pvi_prev['elev']) / (pvi['sta'] - pvi_prev['sta'])
    g2 = (pvi_next['elev'] - pvi['elev']) / (pvi_next['sta'] - pvi['sta'])
    L = pvi['L']
    x = s - (pvi['sta'] - L / 2)
    return pvi['elev'] - g1 * L / 2 + g1 * x + (g2 - g1) * x * x / (2 * L), g1 + (g2 - g1) * x / L, g1, g2


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

        has = await safe("()=>!!window.__acad3dV127")
        ck(bool(has), "__acad3dV127 marker is present")
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
            return await safe("""()=>{window.__a3dTestSetObjs([]);window.__a3dTestClearUndo();window.__a3dSelectFor([]);
              return (""" + js + """)();}""")

        async def geom(aid):
            return await safe("(id)=>window.__a3dAlignGeom(id)", aid)

        async def snap(oid):
            return await safe("(id)=>window.__a3dObjSnapshot(id)", oid)

        async def frame(aid):
            """plan view, framed on the alignment, settled"""
            await safe("()=>window.__a3dOpenView('plan')")
            await page.wait_for_timeout(900)
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dZoomToSelection();}", aid)
            await page.wait_for_timeout(300)

        async def screen_of(p):
            r = await safe("()=>window.__a3dCanvasRect()")
            s = await safe("(p)=>window.__a3dProject(p)", p)
            return [r['left'] + s['x'], r['top'] + s['y']] if r and s else None

        async def prop_set(key, value, oid=None):
            if oid:
                await safe("(id)=>window.__a3dSelectFor([id])", oid)
            return await safe("""(a)=>{window.__a3dRefreshProps();var f=document.querySelector('[data-propalign="'+a[0]+'"]');if(!f)return 'no field';
              f.value=String(a[1]);f.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [key, value])

        async def prop_act(act):
            return await safe("""(a)=>{window.__a3dRefreshProps();var b=document.querySelector('[data-propalignact="'+a+'"]');if(!b)return 'no button';b.click();return true;}""", act)

        # a route turned 30 degrees and set off the origin: right, then left, then a straight-through PI
        ANG, OFF = math.radians(30), (37.5, -12.25)
        P = [rot(p, ANG, off=OFF) for p in [[0, 0], [120, 0], [210, 70], [340, 70], [460, 70], [560, 150]]]
        RAD = [150, 90, 0, 60]
        STA0 = 1250.0

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the horizontal geometry")
            aid = await scene("function(){return window.__a3dAlignFromPts(%s,%s,%s);}" % (json.dumps(P), json.dumps(RAD), STA0))
            g = await geom(aid)
            want, s_end = route(P, RAD, STA0)
            ck(g and not g.get('error'), "the route builds (%s)" % (g and g.get('error')))
            pis = g['pis'][1:-1] if g else []
            curved = [(p, w) for p, w in zip(pis, want) if w['T'] > 0]
            ck(len(pis) == 4 and all(near(p['D'], w['D']) for p, w in zip(pis, want)),
               "each PI's deflection (%s deg)" % [round(w['D'] * 180 / math.pi, 4) for w in want])
            ck(curved and all(near(p['T'], w['T']) and near(p['L'], w['L']) and near(p['E'], w['E']) for p, w in curved),
               "T = R tan(D/2), L = R D and E = R (sec(D/2) - 1) at every curve")
            ck(curved and all(near(p['pc'], w['pc']) and near(p['pt'], w['pt']) for p, w in curved),
               "every PC and PT station, from a start station of 1+250 (%s)" % [(round(w['pc'], 3), round(w['pt'], 3)) for p, w in curved])
            ck(g and near(g['sta1'], s_end) and near(g['length'], s_end - STA0),
               "the end station: the legs less 2T at each curve plus each curve's L (%.4f)" % s_end)
            ck(pis and [p['turn'] for p in pis[:2]] == [w['turn'] for w in want[:2]] and pis[0]['turn'] != pis[1]['turn'],
               "the first curve turns one way and the second the other")
            ck(pis and pis[2]['T'] == 0 and pis[2]['D'] < 1e-9, "a PI the route runs straight through has no curve")
            ck(await safe("()=>[window.__a3dFmtStation(0),window.__a3dFmtStation(1250),window.__a3dFmtStation(1234.567),window.__a3dFmtStation(99.999)].join(' ')")
               == '0+000.00 1+250.00 1+234.57 0+100.00', "stations are written k+mmm.mm")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. station and offset")
            trips = []
            c0 = curved[0][1]
            for s in [STA0 + 40, (c0['pc'] + c0['pt']) / 2, c0['pt'] + 3, (curved[1][1]['pc'] + curved[1][1]['pt']) / 2, s_end - 10]:
                for off in (-7.5, 4.25):
                    pa = await safe("(a)=>window.__a3dAlignPointAt(a[0],a[1])", [aid, s])
                    q = [pa['p'][0] - pa['d'][1] * off, pa['p'][1] + pa['d'][0] * off]
                    so = await safe("(a)=>window.__a3dStationOffset(a[0],a[1])", [aid, q])
                    trips.append((s, off, so['sta'], so['off']))
            ck(all(near(a, c, 1e-9) and near(b, d, 1e-9) for a, b, c, d in trips),
               "a point set off the route at a station and offset reads back exactly, on tangents and on both arcs (%d points)" % len(trips))
            cen = [p for p in g['els'] if p['kind'] == 'arc'][0]['c']
            so = await safe("(a)=>window.__a3dStationOffset(a[0],a[1])", [aid, cen])
            ck(so and near(abs(so['off']), RAD[0], 1e-9) and ((so['off'] > 0) == (pis[0]['turn'] > 0)),
               "the first curve's centre is R off the route, on the side it turns to (%s)" % (so and round(so['off'], 6)))
            beyond = await safe("(a)=>window.__a3dStationOffset(a[0],a[1])", [aid, rot([-30, 0], ANG, off=OFF)])
            ck(beyond and beyond['beyond'] == 'before the start' and near(beyond['sta'], STA0), "a point behind the start says so (%s)" % (beyond and beyond['beyond']))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. refusals")
            r1 = await safe("(id)=>window.__a3dAlignEditFor(id,{radii:[150,400,0,60]})", aid)
            t1 = await toast()
            ck(r1 is False and 'overlap' in t1 and (await snap(aid))['radii'] == RAD, "curves that would overlap are refused by name, and nothing changes (%s)" % t1)
            r2 = await safe("(id)=>window.__a3dAlignEditFor(id,{radii:[150,90,0,500]})", aid)
            ck(r2 is False and 'runs past the end of its leg' in await toast(), "a curve longer than its end leg is refused (%s)" % await toast())
            sk = await safe("()=>window.__a3dSketch('poly',[[0,0],[40,0],[40,30]])")
            await safe("(id)=>window.__a3dSelectFor([id])", sk)
            await command('ALIGNMENT')
            ck((await snap(sk))['t'] == 'sketch' and 'open polyline' in await toast(), "ALIGNMENT on a closed shape is refused, and says why (%s)" % await toast())
            ob = await safe("()=>window.__a3dOpenPolyline([[0,50],[40,50],[80,70]],[0.3,0])")
            await safe("(id)=>window.__a3dSelectFor([id])", ob)
            await command('ALIGNMENT')
            ck(ob and (await snap(ob))['t'] == 'sketch' and (await snap(ob)).get('bulges') and 'arcs' in await toast(),
               "ALIGNMENT on a polyline with arcs is refused, and says why (%s)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the profile")
            L1 = g['sta1']
            PV = [{'sta': STA0, 'elev': 100.0, 'L': 0}, {'sta': STA0 + 180, 'elev': 106.3, 'L': 120},
                  {'sta': STA0 + 380, 'elev': 99.1, 'L': 160}, {'sta': L1, 'elev': 104.0, 'L': 0}]
            ok = await safe("(a)=>window.__a3dAlignEditFor(a[0],{profile:{pvis:a[1]}})", [aid, PV])
            ck(ok is True, "a profile of four PVIs, a crest and a sag")
            errs_p = []
            for i, s in enumerate([STA0 + 20, STA0 + 130, STA0 + 180, STA0 + 235, STA0 + 300, STA0 + 330, STA0 + 380, STA0 + 450, L1 - 1]):
                e = await safe("(a)=>window.__a3dProfileElevAt(a[0],a[1])", [aid, s])
                k = 1 if abs(s - PV[1]['sta']) <= PV[1]['L'] / 2 else (2 if abs(s - PV[2]['sta']) <= PV[2]['L'] / 2 else 0)
                if k:
                    we, wg, g1, g2 = parabola(PV[k - 1], PV[k], PV[k + 1], s)
                else:
                    j = max(jj for jj in range(3) if PV[jj]['sta'] <= s)
                    wg = (PV[j + 1]['elev'] - PV[j]['elev']) / (PV[j + 1]['sta'] - PV[j]['sta'])
                    we = PV[j]['elev'] + wg * (s - PV[j]['sta'])
                errs_p.append(abs(e['elev'] - we) + abs(e['grade'] - wg))
            ck(max(errs_p) < 1e-9, "elevation and grade on the grades and on both parabolas (worst %.1e)" % max(errs_p))
            pg = await safe("(id)=>window.__a3dProfileGeom(id)", aid)
            crest, sag = pg['pvis'][1], pg['pvis'][2]
            for nm, v, k in (('crest', crest, 1), ('sag', sag, 2)):
                _, _, g1, g2 = parabola(PV[k - 1], PV[k], PV[k + 1], PV[k]['sta'])
                x = -g1 * PV[k]['L'] / (g2 - g1)
                we, _, _, _ = parabola(PV[k - 1], PV[k], PV[k + 1], PV[k]['sta'] - PV[k]['L'] / 2 + x)
                ck(v['kind'] == nm and near(v['turnSta'], PV[k]['sta'] - PV[k]['L'] / 2 + x) and near(v['turnElev'], we)
                   and near(v['K'], PV[k]['L'] / abs((g2 - g1) * 100)),
                   "the %s's %s point at x = -g1 L / (g2 - g1) = %.3f m, and K = L / |A| = %.2f" % (nm, 'high' if nm == 'crest' else 'low', x, PV[k]['L'] / abs((g2 - g1) * 100)))
            bad1 = await safe("(a)=>window.__a3dAlignEditFor(a[0],{profile:{pvis:a[1]}})", [aid, PV[:-1] + [{'sta': L1 + 5, 'elev': 104, 'L': 0}]])
            ck(bad1 is False and 'runs off the alignment' in await toast(), "a profile past the alignment's end is refused (%s)" % await toast())
            bad2 = await safe("(a)=>window.__a3dAlignEditFor(a[0],{profile:{pvis:a[1]}})",
                              [aid, [PV[0], dict(PV[1], L=250), PV[2], PV[3]]])
            ck(bad2 is False and 'overlaps' in await toast(), "vertical curves that overlap are refused (%s)" % await toast())

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the ground")
            A0, BX, CZ = 50.0, 0.013, -0.021
            tid = await safe("""(p)=>{var m=[];for(var x=-100;x<=700;x+=50)for(var z=-150;z<=450;z+=50)m.push([x,z,p[0]+p[1]*x+p[2]*z]);
              return window.__a3dMakeTerrain(m);}""", [A0, BX, CZ])
            pts = [[13.7, 22.9], [250.3, 101.1], [611.2, 377.7], [-40.5, 90.25]]
            hs = [await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [tid, p[0], p[1]]) for p in pts]
            ck(all(h is not None and abs(h - (A0 + BX * p[0] + CZ * p[1])) < 1e-9 for h, p in zip(hs, pts)),
               "on a planar surface the TIN height is the plane's, in any triangle")
            ck(await safe("(a)=>window.__a3dTinHeightAt(a[0],a[1],a[2])", [tid, 900, 900]) is None, "and there is none off the surface")
            gr = await safe("(id)=>window.__a3dAlignGround(id)", aid) or []
            worst = 0
            for run in gr:
                for s, h in run[::7]:
                    pa = await safe("(a)=>window.__a3dAlignPointAt(a[0],a[1])", [aid, s])
                    worst = max(worst, abs(h - (A0 + BX * pa['p'][0] + CZ * pa['p'][1])))
            ck(len(gr) == 1 and gr[0][0][0] == STA0 and near(gr[0][-1][0], L1) and worst < 1e-9,
               "the ground profile runs the route's length and is the plane under the route (worst %.1e)" % worst)

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the interface")
            await scene("function(){return 1;}")
            pl = await safe("()=>window.__a3dOpenPolyline([[0,0],[100,0],[180,60],[300,60]])")
            await safe("(id)=>window.__a3dSelectFor([id])", pl)
            await command('ALIGNMENT')
            al = await safe("()=>window.__a3dState().sel")
            alo = al and await snap(al)
            ck(alo and alo['t'] == 'alignment' and not [o for o in await safe("()=>window.__a3dState().objs.map(o=>o.id)") if o == pl],
               "ALIGNMENT makes the selected open polyline an alignment, in its place")
            ck(alo and alo['radii'] == [100, 100] and 'curve' in await toast(), "with a 100 m curve at each PI its legs leave room for (%s)" % (alo and alo['radii']))
            await safe("()=>window.__a3dUndo()")
            ck((await snap(pl) or {}).get('t') == 'sketch', "and one Undo brings the polyline back")
            tight = await safe("()=>window.__a3dOpenPolyline([[400,0],[430,0],[450,20],[480,20]])")
            await safe("(id)=>window.__a3dSelectFor([id])", tight)
            await command('ALIGNMENT')
            ta = await safe("()=>window.__a3dState().sel")
            tt = math.tan(math.pi / 8)
            fit = min(30 / tt, math.hypot(20, 20) / (2 * tt))
            tg = ta and await geom(ta)
            ck(tg and not tg.get('error') and (await snap(ta))['radii'] == [math.floor(fit * 0.95)] * 2,
               "on short legs it takes the largest radius they leave room for, 95%% of %.2f m, rounded down (%s)" % (fit, ta and (await snap(ta)).get('radii')))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dRedo&&window.__a3dRedo()")
            if not await snap(al):
                await safe("(id)=>window.__a3dSelectFor([id])", pl)
                await command('ALIGNMENT')
                al = await safe("()=>window.__a3dState().sel")
            await safe("()=>window.__a3dTestClearUndo()")
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", al)
            txt = await safe("()=>{var g=document.querySelector('.a3d-pgrp[data-a3dpgrp=\"Alignment\"]');return g&&g.nextElementSibling?g.nextElementSibling.textContent:null;}")
            ck(txt and '0+000.00 to 0+315.37' in txt and 'PC 0+066.67' in txt and 'right' in txt and 'left' in txt,
               "the Alignment page gives the stations and each curve, which way it turns, and its PC and PT")
            ck(await prop_set('r:0', 60) is True and near((await geom(al))['pis'][1]['R'], 60), "a radius typed in Properties rebuilds the curve")
            await safe("()=>window.__a3dUndo()")
            ck(near((await geom(al))['pis'][1]['R'], 100), "and one Undo takes it back")
            await prop_set('r:0', 900, al)
            ck(near((await geom(al))['pis'][1]['R'], 100) and 'was not changed' in await toast() and 'leg' in await toast(),
               "a radius that does not fit is refused and says why (%s)" % await toast())
            await safe("(id)=>window.__a3dSelectFor([id])", al)
            ck(await prop_act('pvadd') is True, "Add PVI starts a profile")
            p2 = await safe("(id)=>window.__a3dObjSnapshot(id).profile", al)
            ck(p2 and len(p2['pvis']) == 2 and near(p2['pvis'][1]['sta'], (await geom(al))['sta1']),
               "on the alignment's ends, at its own elevation with no surface under it (%s)" % p2)
            await prop_act('pvadd')
            await prop_set('pvi:1:elev', 4)
            await prop_set('pvi:1:L', 60)
            pg2 = await safe("(id)=>window.__a3dProfileGeom(id)", al)
            ck(pg2 and not pg2.get('error') and len(pg2['pvis']) == 3 and pg2['pvis'][1]['kind'] == 'crest' and pg2['pvis'][1]['L'] == 60,
               "a second Add PVI splits the grade; raised 4 m with a 60 m curve it is a crest")
            ptxt = await safe("()=>{var g=document.querySelector('.a3d-pgrp[data-a3dpgrp=\"Profile\"]');return g&&g.nextElementSibling?g.nextElementSibling.textContent:null;}")
            ck(ptxt and 'crest' in ptxt and 'high point' in ptxt and 'Grade 1 to 2' in ptxt, "the Profile page gives the grades and the curve's K and high point")
            await prop_set('sta0', 1000)
            g3 = await geom(al)
            p3 = await safe("(id)=>window.__a3dObjSnapshot(id).profile", al)
            ck(near(g3['sta0'], 1000) and near(p3['pvis'][0]['sta'], 1000) and near(p3['pvis'][2]['sta'], g3['sta1']),
               "a new start station moves the profile with it: its PVIs stay on the same ground")
            # PROFILEVIEW, by clicking
            await frame(al)
            await command('PROFILEVIEW')
            tgt = await screen_of([0, 0, 120])
            await page.mouse.click(tgt[0], tgt[1])
            await page.wait_for_timeout(300)
            pv = (await snap(al)).get('profileView')
            ck(pv and abs(pv['at'][0]) < 1.5 and abs(pv['at'][1] - 120) < 1.5 and pv['vx'] == 10,
               "PROFILEVIEW places the profile view where it is clicked (%s)" % pv)
            dr = (await safe("()=>window.__a3dAlignDrawn()") or {}).get(al, {})
            ck(dr.get('profileView') and len(dr.get('pvLabels', [])) == 3, "and it is drawn, with its three PVIs labelled (%s)" % dr.get('pvLabels'))
            await safe("()=>window.__a3dSelectFor([])")
            fr = dr.get('frame')
            if fr:
                r = await safe("()=>window.__a3dCanvasRect()")
                await page.mouse.click(r['left'] + (fr[0] + fr[2]) / 2, r['top'] + fr[3] - 6)
                await page.wait_for_timeout(250)
            ck(await safe("()=>window.__a3dState().sel") == al, "a click in the profile view selects its alignment")
            ck(dr.get('majors') == [1000, 1100, 1200, 1300] and 'PC 1+066.67' in dr.get('pcpt', []) and 'END 1+315.37' in dr.get('pcpt', []),
               "stations are ticked and labelled every 100 m, and every PC, PT and end is marked (%s)" % dr.get('majors'))
            # STATION, by clicking
            await command('STATION')
            tgt = await screen_of([50, 0, -6])
            await page.mouse.click(tgt[0], tgt[1])
            await page.wait_for_timeout(300)
            mk = await safe("()=>window.__a3dStationMark()")
            chk = mk and await safe("(a)=>window.__a3dStationOffset(a[0],a[1])", [al, mk['p']])
            ck(mk and abs(mk['sta'] - 1050) < 1.5 and abs(mk['off'] + 6) < 1.5 and near(chk['sta'], mk['sta']) and near(chk['off'], mk['off']),
               "STATION reads a clicked point's station and offset: about 1+050, 6 m left (%s)" % str(mk and (round(mk['sta'], 3), round(mk['off'], 3))))
            ck(('Sta %s' % (await safe("(s)=>window.__a3dFmtStation(s)", mk['sta']) if mk else '?')) in await toast() and 'left' in await toast(), "and says so (%s)" % await toast())
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(200)
            ck(await safe("()=>!window.__a3dState().sk||!window.__a3dState().sk.tool") is not False, "Escape ends STATION")
            btn = await safe("()=>!!document.querySelector('[data-a3dr=\"bim:alignment\"]')")
            ck(btn, "one Alignment button, in the Site panel")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. kept")
            await safe("(id)=>window.__a3dSelectFor([id])", al)
            await blur()
            await page.keyboard.press('Control+d')
            await page.wait_for_timeout(400)
            cp = await safe("()=>window.__a3dState().sel")
            await safe("(id)=>window.__a3dAlignEditFor(id,{radii:[40,40]})", cp)
            ck(cp and cp != al and near((await geom(cp))['pis'][1]['R'], 40) and near((await geom(al))['pis'][1]['R'], 100),
               "a copy is its own: its radius changes and the original's does not")
            g0 = await geom(al)
            await safe("(id)=>window.__a3dRotateSelection([id],[0,0],Math.PI/3)", al)
            g1r = await geom(al)
            ck(near(g1r['length'], g0['length']) and near(g1r['sta1'], g0['sta1'])
               and near(g1r['start'][0], 0) and near(g1r['end'][0], 300 * math.cos(math.pi / 3) - 60 * math.sin(math.pi / 3), 1e-9),
               "turned 60 degrees, the route keeps its curves and length, and its end turns with it")
            mids = await safe("(id)=>window.__a3dMirrorSelection([id],[0,0],[10,0])", al)
            mg = mids and await geom(mids[0])
            ck(mg and near(mg['length'], g0['length']) and mg['pis'][1]['turn'] == -g1r['pis'][1]['turn'],
               "mirrored, it keeps its length and its curves turn the other way")
            rows = (await safe("()=>window.__a3dScheduleRows('alignment')") or {}).get('rows', [])
            r_al = [r for r in rows if r.get('alignment') == (await snap(al))['name']]
            ck(len(r_al) == 4 and r_al[1]['pc'] == '1+066.67' and near(r_al[1]['radius'], 100) and near(r_al[1]['tangent'], g0['pis'][1]['T']),
               "the Alignment schedule reads the same geometry (%s)" % (r_al[1] if len(r_al) > 1 else r_al))
            prow = (await safe("()=>window.__a3dScheduleRows('profile')") or {}).get('rows', [])
            ck(any(r.get('kind') == 'crest' and 'High' in r.get('turn', '') for r in prow), "and so does the Profile schedule")
            dxf = (await safe("()=>window.__a3dBuildDXF().text") or "")
            ck('PC 1+066.67' in dxf and 'END 1+315.37' in dxf, "the DXF carries the route and its stations")
            await page.wait_for_timeout(700)
            await page.reload()
            await page.wait_for_timeout(2300)
            gl = await geom(al)
            ck(gl and near(gl['length'], g0['length']) and (await snap(al)).get('profile'), "the alignment and its profile survive a reload")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        await browser.close()
    print("%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
