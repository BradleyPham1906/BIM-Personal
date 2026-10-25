#!/usr/bin/env python3
"""bim_phase171_traffic_browser_tests.py -- V171: traffic and people around the site, simulated.

Every service is answered inside the browser by tests/traffic_fixture.py: V166's neighbourhood with two signals, an
all-way stop, a stop on one approach, a mapped width and an on-ramp near the lot. What the simulation should do is
worked out again in tests/traffic_reference.py from its sources (the IDM's paper, the Signal Timing Manual and the
MUTCD, Florida's K, NCHRP 255, San Diego's rates); what reaches the screen is read back from the canvas.

  1. THE RECORDS: the marker and the version; the ten Traffic topics with their editions and values; the analysis in
     Access; TRAFFIC and TRAFFICOFF.
  2. THE CAR, THE PLAN, THE TURNS, THE TRIPS: the IDM's acceleration; a follower settling at the steady gap; plans
     from Webster, Kell and Fullerton and the least greens; NCHRP 255's balancing; San Diego's trips.
  3. THE NETWORK: cut at the reach; lanes and the width; each junction's kind; right of way; turns; the lot's entry
     and its doors; the walkers' ways crossing only where a crossing is.
  4. THE DEMAND: each street's traffic and each junction's turns, against the reference.
  5. THE RUN: each signal's plan and its lights; the design's trips; twenty minutes of the peak: no car through a red,
     no walker starting late, no two cars in one place, every car accounted for; the tallies; the pools allocated
     once and the memory settling.
  6. ON THE CLOCK: TRAFFIC plays it, Pause keeps the moment, the speed, Stop gives it up; the settings undoable and
     kept; the quality.
  7. DRAWN: in plan and 3D, on the canvas; the stop lines; nothing when the layer is off.
  8. THE RESULTS AS LAYERS: Run lays the signals' plans, the entry, the doors and the delays; the row.
  9. WITHOUT A DRIVEWAY, WITHOUT SIGNALS.
 10. A PHONE, A TABLET, A COMPUTER: the row on each; a phone's thumb; the quality the device suggests.
 11. A RELOAD: the settings kept, the simulation still.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import traffic_fixture as FX   # noqa: E402
import traffic_reference as R   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
SC = 0.35   # a primitive's parameters are multiplied by it (V131)
LOT = [list(p) for p in FX.LOT]
# the design: a mass of each usage on the lot (x, z, width, depth, height, usage)
MASSES = [(20, -25, 18, 28, 31, 'use-res'), (40, -25, 18, 28, 18, 'use-off'), (30, -15, 38, 8, 4.5, 'use-ret'), (30, -35, 38, 8, 16, 'use-hot')]
TOPICS = ['idm.car', 'mobil', 'stm.signal', 'mutcd.signal', 'fdot.k', 'nchrp255', 'sd.trips', 'hm.walk', 'sumo.rules', 'app.traffic']
LAUNCH = ['--enable-precise-memory-info', '--js-flags=--expose-gc']


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


def lot_dist(x, z):
    """a point's distance to the lot (a rectangle): 0 inside"""
    xs, zs = [p[0] for p in LOT], [p[1] for p in LOT]
    dx = max(min(xs) - x, 0, x - max(xs))
    dz = max(min(zs) - z, 0, z - max(zs))
    return math.hypot(dx, dz)


def seg_cross(p, q, a, b):
    """two plan segments cross (strictly)"""
    def o(u, v, w):
        return (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])
    d1, d2, d3, d4 = o(a, b, p), o(a, b, q), o(p, q, a), o(p, q, b)
    return d1 * d2 < -1e-9 and d3 * d4 < -1e-9


def ref_plan(net, j):
    """the reference's plan for a signalled junction of the app's network"""
    L = {l['i']: l for l in net['links']}
    ap = [{'bear': j['arms'][L[li]['arm']]['bear'], 'q': L[li]['q'], 'lanes': L[li]['lanes'], 'v': L[li]['v0'],
           'cls': R.green_class(L[li]['base'], L[li]['v0'])} for li in j['ins']]
    arms = [{'k': a['k'], 'bear': a['bear'], 'w': a['w']} for a in j['arms'] if a['car']]
    return R.plan(ap, arms)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=LAUNCH)
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        ST = {'tr': ()}
        for h in FX.HOSTS:
            await ctx.route(h, FX.route_handler(ST))
        for h in BLOCKERS:
            await ctx.route(h, lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def summary(pg=None):
            return await safe("()=>window.__a3dTrSummary()", pg=pg)

        async def steps(n, pg=None):
            return await safe("(n)=>window.__a3dTrSteps(n)", n, pg=pg)

        async def anim(pg=None):
            return await safe("()=>window.__a3dAnim()", pg=pg) or {}

        async def setup(pg=None):
            """the lot and its design, then the site analysed with the fixture's neighbourhood"""
            pg = pg or page
            await safe("()=>window.__a3dEnter()", pg=pg)
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT'&&x.t!=='box';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT, pg=pg)
            for (x, z, w, d, h, u) in MASSES:
                bid = await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [w / SC, d / SC, h / SC], pg=pg)
                await safe("(a)=>{var L=window.__a3dState().objs;L.forEach(function(o){if(o.id===a[0])o.pos=[a[1],a[2],a[3]];});window.__a3dTestSetObjs(L);}", [bid, x, h / 2, z], pg=pg)
                await safe("(a)=>window.__a3dUsageAssign([a[0]],a[1])", [bid, u], pg=pg)
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            if await safe("()=>!!document.querySelector('[data-saaddr]')", pg=pg):
                await pg.fill('[data-saaddr]', '1 Market Street')
                await pg.press('[data-saaddr]', 'Enter')
            else:   # analysed already: Analyze site again
                await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=pg)
            for _ in range(240):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await pg.wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def only(keep, pg=None):
            """the Site analysis's layers shown: these analyses only"""
            return await safe("""(keep)=>{var D=window.__a3dDgState(),k,n=0;for(k in D.layers)if(D.layers.hasOwnProperty(k)&&k!=='root'){
              var v=keep.indexOf(k)>=0||keep.some(function(a){return k.indexOf(a+':')===0;});window.__a3dLayerSet(D.layers[k],'visible',v);n++;}
              window.__a3dLayerSet(D.layers.root,'visible',true);return n;}""", keep, pg=pg)

        async def heap():
            return await safe("()=>{if(window.gc){window.gc();window.gc();}return performance.memory?performance.memory.usedJSHeapSize:null;}")

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV171") or ''
            ck(all(w in mk for w in ('network', 'signals', 'webster', 'kellfullerton', 'furness', 'sandiego', 'idm', 'mobil', 'walkers', 'crossings', 'pools', 'draw2d', 'draw3d', 'analysis', 'command')),
               "the V171 marker (%s)" % mk)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 171, "the app says V171 or later (%s)" % (mv and mv.group(1)))
            vals = {t: await safe("(t)=>{var E=window.__a3dStdEdition(t);return E?{id:E.id,lv:E.src&&E.src.lv,area:null}:null;}", t) for t in TOPICS}
            ck(all(vals[t] for t in TOPICS), "the ten Traffic topics are in the registry, each with an edition in force (%s)" % [t for t in TOPICS if not vals[t]])
            st = lambda t, n: safe("(a)=>window.__a3dStd(a[0],a[1])", [t, n])   # noqa: E731
            got = {k: await st('idm.car', k) for k in ('T', 's0', 'a', 'b', 'delta')}
            ck(got == {'T': R.IDM['T'], 's0': R.IDM['s0'], 'a': R.IDM['a'], 'b': R.IDM['b'], 'delta': R.IDM['delta']}, "the IDM's car is the authors' (Table 1): %s" % got)
            got = [await st('mobil', k) for k in ('p', 'thr', 'bsafe')]
            ck(got == [R.MOBIL['p'], R.MOBIL['thr'], R.MOBIL['bsafe']], "MOBIL's politeness, threshold and safe braking (%s)" % got)
            got = [await st('stm.signal', k) for k in ('sat', 'lost', 'webster', 'cycle_min', 'cycle_max', 'kf_t', 'kf_a', 'kf_lv', 'min_green')]
            ck(got[:5] == [R.SAT, R.LOST, list(R.WEBSTER), R.CYCLE[0], R.CYCLE[1]] and near(got[5], R.KF_T) and near(got[6], R.KF_A, 1e-3) and near(got[7], R.KF_LV, 1e-3) and got[8] == R.MIN_GREEN,
               "the timing manual's saturation flow, lost time, Webster, cycles, Kell and Fullerton and least greens (%s)" % got)
            got = [await st('mutcd.signal', k) for k in ('yel_min', 'yel_max', 'red_max', 'walk')] + [await st('mutcd.walk', 'clear')]
            ck(got[:4] == [R.YELLOW[0], R.YELLOW[1], R.RED_MAX, R.WALK] and near(got[4], R.CLEAR, 1e-3), "the MUTCD's yellow, red clearance, WALK and clearance speed (%s)" % got)
            ck(await st('fdot.k', 'k') == R.K and await st('nchrp255', 'iter') == R.ITER, "Florida's K of 9% and NCHRP 255's ten rounds")
            tb = await st('sd.trips', 'table') or {}
            ck(all(tb.get(k, {}).get('am') == list(v['am']) and tb.get(k, {}).get('pm') == list(v['pm']) and tb.get(k, {}).get('rate') == v.get('rate') and tb.get(k, {}).get('ln') == (list(v['ln']) if 'ln' in v else None)
                   for k, v in R.SD.items()) and await st('sd.trips', 'dense') == R.DENSE, "San Diego's rates, peak shares and splits for the five uses, and the density split")
            got = [await st('hm.walk', k) for k in ('mean', 'sd', 'cap')]
            ck(got == [R.WALK_MEAN, R.WALK_SD, R.WALK_CAP] and vals['hm.walk'] and vals['hm.walk']['lv'] == 'S' and vals['sumo.rules']['lv'] == 'S',
               "Helbing and Molnar's walking speeds, and the two secondary sources said as such (%s)" % got)
            cats = await safe("()=>window.__a3dAnzCats()") or []
            ck(any(c['id'] == 'dgtraffic' and c['group'] == 'access' for c in cats), "Traffic and people is an analysis of Access (%s)" % [c for c in cats if 'traffic' in c['id']])
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return c.name==='TRAFFIC'||c.name==='TRAFFICOFF';})") or []
            tr = [c for c in cat if c['name'] == 'TRAFFIC']
            ck(tr and set(['TRAFFICSIM', 'SIMULATETRAFFIC', 'PEDESTRIANS', 'TRAFFICON']).issubset(set(tr[0].get('aliases') or [])) and any(c['name'] == 'TRAFFICOFF' for c in cat),
               "TRAFFIC with its aliases, and TRAFFICOFF, in the commands (%s)" % [c.get('aliases') for c in cat])
            found = [x['name'] for x in (await safe("()=>window.__a3dCommandSearch('pedestrians',5)") or [])]
            ck('TRAFFIC' in found[:3], "searching 'pedestrians' finds TRAFFIC (%s)" % found)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The car, the plan, the turns, the trips")
            cases = [(v, v0, s, dv) for v in (0, 5, 13.4) for v0 in (8.33, 13.4, 22.2) for s in (2.5, 10, 40, 1000) for dv in (-3, 0, 4)]
            app = await safe("(c)=>c.map(function(x){return window.__a3dTrIdm(x[0],x[1],x[2],x[3]);})", cases) or []
            bad = [(c, a, R.idm(*c)) for c, a in zip(cases, app) if not near(a, R.idm(*c), 1e-9)]
            ck(len(app) == len(cases) and not bad, "the IDM's acceleration at %d speeds, gaps and closing speeds, as the paper's equations give it (%s)" % (len(cases), bad[:2]))
            for (v0, vl) in ((13.4, 10.0), (13.4, 5.0), (22.2, 15.0)):
                pl = await safe("(o)=>window.__a3dTrPlatoon(o)", {'v0': v0, 'vl': vl, 'vf': vl, 's0': 2, 'gap': 40, 'secs': 300}) or []
                se = R.gap_eq(vl, v0)
                last = pl[-1] if pl else [0, 0, 0]
                ck(pl and abs(last[1] - se) < 0.05 and abs(last[2] - vl) < 0.01 and min(p[1] for p in pl) > 0,
                   "a follower behind a car held at %.1f m/s (desired %.1f) settles at the steady gap %.2f m (%.2f m after 300 s), never touching it" % (vl, v0, se, last[1]))
            free = await safe("(o)=>window.__a3dTrPlatoon(o)", {'v0': 13.4, 'vl': 13.4, 'vf': 0, 's0': 2, 'gap': 5000, 'secs': 60}) or []
            ck(free and free[-1][2] > 0.97 * 13.4 and all(p[2] <= 13.4 + 1e-6 for p in free), "on a free road a car reaches its desired speed and never passes it (%.2f m/s after 60 s)" % (free[-1][2] if free else -1))
            plans = [
                ([{'bear': 90, 'q': 200, 'lanes': 2, 'v': 13.4, 'cls': 'major'}, {'bear': 270, 'q': 180, 'lanes': 2, 'v': 13.4, 'cls': 'major'},
                  {'bear': 0, 'q': 50, 'lanes': 1, 'v': 8.3, 'cls': 'local'}, {'bear': 180, 'q': 40, 'lanes': 1, 'v': 8.3, 'cls': 'local'}],
                 [{'k': 0, 'bear': 0, 'w': 6.6}, {'k': 1, 'bear': 90, 'w': 13.2}, {'k': 2, 'bear': 180, 'w': 6.6}, {'k': 3, 'bear': 270, 'w': 13.2}], 'light traffic: the least cycle'),
                ([{'bear': 90, 'q': 1700, 'lanes': 2, 'v': 13.4, 'cls': 'major'}, {'bear': 270, 'q': 1500, 'lanes': 2, 'v': 13.4, 'cls': 'major'},
                  {'bear': 0, 'q': 650, 'lanes': 1, 'v': 11.1, 'cls': 'minor'}, {'bear': 180, 'q': 600, 'lanes': 1, 'v': 11.1, 'cls': 'minor'}],
                 [{'k': 0, 'bear': 0, 'w': 6.6}, {'k': 1, 'bear': 90, 'w': 13.2}, {'k': 2, 'bear': 180, 'w': 6.6}, {'k': 3, 'bear': 270, 'w': 13.2}], 'busy: Webster\'s cycle'),
                ([{'bear': 90, 'q': 1800, 'lanes': 2, 'v': 13.4, 'cls': 'major'}, {'bear': 0, 'q': 900, 'lanes': 1, 'v': 11.1, 'cls': 'minor'}],
                 [{'k': 0, 'bear': 0, 'w': 6.6}, {'k': 1, 'bear': 90, 'w': 13.2}, {'k': 2, 'bear': 270, 'w': 13.2}], 'at capacity: the longest'),
                ([{'bear': 90, 'q': 300, 'lanes': 3, 'v': 24.6, 'cls': 'fast'}, {'bear': 270, 'q': 300, 'lanes': 3, 'v': 24.6, 'cls': 'fast'},
                  {'bear': 5, 'q': 30, 'lanes': 1, 'v': 8.3, 'cls': 'local'}],
                 [{'k': 0, 'bear': 5, 'w': 6.0}, {'k': 1, 'bear': 90, 'w': 40.0}, {'k': 2, 'bear': 270, 'w': 40.0}], 'a wide road: the walkers\' least green grows the cycle'),
                ([{'bear': 45, 'q': 600, 'lanes': 2, 'v': 15.6, 'cls': 'major'}, {'bear': 140, 'q': 250, 'lanes': 1, 'v': 11.1, 'cls': 'local'}],
                 [{'k': 0, 'bear': 45, 'w': 10.0}, {'k': 1, 'bear': 140, 'w': 7.0}, {'k': 2, 'bear': 225, 'w': 10.0}], 'skewed: phases by axis within 45 degrees'),
            ]
            for ap, arms, what in plans:
                P = await safe("(a)=>window.__a3dTrPlanOf(a[0],a[1])", [[dict(a, li=i) for i, a in enumerate(ap)], arms]) or {}
                Q = R.plan(ap, arms)
                okp = P and near(P['C'], Q['C'], 1e-6) and (P['C0'] is None) == (Q['C0'] == math.inf) and P['grown'] == Q['grown'] and \
                    all(near(a['G'], b['G'], 1e-6) and near(a['Y'], b['Y'], 1e-9) and near(a['AR'], b['AR'], 1e-9) and near(a['t0'], b['t0'], 1e-6) and sorted(a['arms']) == sorted(b['arms'])
                        for a, b in zip(P['ph'], Q['ph']))
                ck(okp, "%s: cycle %.1f s (Webster %s), greens %s, yellows %s, all-reds %s%s" % (what, Q['C'], 'at capacity' if Q['C0'] == math.inf else '%.1f' % Q['C0'],
                   [round(o['G'], 1) for o in Q['ph']], [round(o['Y'], 2) for o in Q['ph']], [round(o['AR'], 2) for o in Q['ph']], ', grown' if Q['grown'] else ''))
            P1 = R.plan(*plans[0][:2])
            P2 = R.plan(*plans[1][:2])
            ck(P1['C'] == 60 and all(o['G'] >= o['gmin'] - 1e-9 for o in P1['ph']) and 60 < P2['C'] == P2['C0'] < 120 and R.plan(*plans[2][:2])['C'] == 120 and R.plan(*plans[3][:2])['grown'],
               "the reference's own cases are the ones meant: the least cycle, Webster's own, the longest, a cycle grown to hold the least greens")
            fcs = [
                ([400, 300, 100], [350, 350, 100], [[0, 1, 1], [1, 0, 1], [1, 1, 0]]),
                ([765, 765, 166, 166], [765, 765, 166, 166], [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]),
                ([500, 0.000001], [200, 800], [[1, 1], [1, 0]]),
                ([100, 100], [0, 0], [[1, 1], [0, 1]]),
            ]
            for qi, qo, okm in fcs:
                A = await safe("(a)=>window.__a3dTrFurness(a[0],a[1],a[2].map(function(r){return r.map(Boolean);}),10)", [qi, qo, okm]) or []
                B = R.furness(qi, qo, okm)
                ck(A and all(near(x, y, 1e-9) for ra, rb in zip(A, B) for x, y in zip(ra, rb)) and all(near(sum(r), 1, 1e-9) for r in A if sum(r) > 0) and
                   all(A[i][j] == 0 for i in range(len(qi)) for j in range(len(qo)) if not okm[i][j]),
                   "NCHRP 255's balancing of %s in, %s out: each approach's shares as the reference, summing to one, none on a turn not allowed" % (qi, qo))
            for rows, acres, peak in (([('mdu', 40)], 5.0, 'pm'), ([('mdu', 40)], 1.0, 'am'), ([('office', 52.4)], 1, 'pm'), ([('office', 52.4)], 1, 'am'),
                                      ([('retail', 12.3)], 1, 'pm'), ([('hotel', 120)], 1, 'am'), ([('mdu', 30), ('retail', 8), ('hotel', 0)], 0.3, 'pm')):
                A = await safe("(a)=>window.__a3dTrTrips(a[0].map(function(r){return {use:r[0],n:r[1]};}),a[1],a[2])", [rows, acres, peak]) or {}
                tin, tout, per = R.trips(rows, acres, peak)
                ck(near(A.get('tin'), tin, 1e-9) and near(A.get('tout'), tout, 1e-9) and [r['key'] for r in A.get('rows', [])] == [p[0] for p in per],
                   "San Diego's trips for %s on %.1f acres, %s peak: %.2f in, %.2f out (%s)" % (rows, acres, peak.upper(), tin, tout, [p[0] for p in per]))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The network")
            fin = await setup()
            S = {s['id']: s['state'] for s in fin.get('steps', [])}
            ck(S.get('draw') == 'ok', "the fixture's run draws the analyses (%s)" % S)
            net = await safe("()=>window.__a3dTrNet()") or {}
            ck(not net.get('err') and len(net.get('links', [])) > 100, "the network: %d edges, %d links, %d junctions" % (len(net.get('edges', [])), len(net.get('links', [])), len(net.get('J', []))))
            L = {l['i']: l for l in net.get('links', [])}
            J = net.get('J', [])
            bnd = [j for j in J if j['bnd']]
            ck(bnd and all(abs(lot_dist(j['x'], j['z']) - 300) < 0.5 for j in bnd) and all(lot_dist(net['x'][e['a']], net['z'][e['a']]) <= 300.5 for e in net['edges']),
               "every street cut at the reach, 300 m from the lot: %d boundaries, each on it" % len(bnd))
            byedge = {}
            for l in net['links']:
                byedge.setdefault(l['e'], []).append(l)
            ck(all(len(byedge.get(i, [])) == (1 if e['lanes']['ow'] else 2) for i, e in enumerate(net['edges']) if e['car']),
               "each street a link each way it may be driven: one on a one-way street, two on the others")
            mk_ = [l for l in net['links'] if l['name'] == 'Market Street']
            av14 = [l for l in net['links'] if l['name'] == 'Avenue 14']
            ck(mk_ and all(l['lanes'] == 2 for l in mk_) and av14 and sorted(set(l['lanes'] for l in av14)) == [1, 2] and net.get('lanesCapped', 0) >= 1,
               "Market Street's four lanes two each way; Avenue 14's six, under its mapped 10 m, three: two one way, one the other (%s)" % sorted(set((l['lanes'], l['w']) for l in av14)))

            def jat(x, z):
                for j in J:
                    if abs(j['x'] - x) < 0.6 and abs(j['z'] - z) < 0.6:
                        return j
                return None
            sig = [j for j in J if j['kind'] == 'signal']
            ck(sorted((round(j['x']), round(j['z'])) for j in sig) == [(-180, 0), (60, 0)] and net.get('sigOff') == 1,
               "the two signals near the lot signal their junctions; V166's, 400 m away, is beyond the reach and said (%s, %s off)" % ([(j['x'], j['z']) for j in sig], net.get('sigOff')))
            ja = jat(180, -100)
            ck(ja and ja['kind'] == 'allstop', "the all-way stop at Avenue 17 and N1 Street (%s)" % (ja and ja['kind']))
            js = jat(-60, -100)
            stl = [L[li] for li in (js or {}).get('stop', [])]
            ck(js and js['kind'] == 'yield' and len(stl) == 1 and stl[0]['name'] == 'Avenue 15' and net['z'][stl[0]['a']] > -100,
               "the stop on Avenue 15's approach from Market Street stops that approach only (%s)" % [(l['name'], net['x'][l['a']], net['z'][l['a']]) for l in stl])
            maj_ok = True
            for x in (-60, 180, 300, 120):
                j = jat(x, 0)
                mj = [L[i]['name'] for i in (j or {}).get('major', [])]
                maj_ok = maj_ok and j and j['kind'] == 'yield' and mj == ['Market Street', 'Market Street']
            ck(maj_ok, "where nothing signals Market Street's junctions, its two ways in have the way")
            jr = jat(120, -60)
            mj = [(L[i]['hw']) for i in (jr or {}).get('major', [])]
            ck(jr and mj == ['motorway'] and len(jr['ins']) == 2, "where the ramp merges, the Expressway has the way and the ramp gives it (%s)" % mj)
            uturns = [(j['i'], len(j['arms'])) for j in J for k, T in j['tr'].items() for t in T if t[3]]
            ck(all(n == 1 for _, n in uturns) and not any(t[3] for j in J for k, T in j['tr'].items() for t in T if len(j['arms']) > 1),
               "a car turns back only at a dead end (%d dead ends)" % len(uturns))
            lot = net.get('lot') or {}
            ck(lot.get('prov') is False and lot.get('name') == 'Driveway' and abs(net['x'][lot['at']] - 40) < 0.6 and abs(net['z'][lot['at']]) < 0.6,
               "the lot's entry is its mapped driveway, meeting Market Street at x 40 (%s)" % lot)
            doors = net.get('doors', [])
            ck([d['name'] for d in doors] == ['Main door', 'Entrance (service)'] and all(d['mapped'] for d in doors),
               "the lot's two mapped doors; the one 20 m off the lot is not the lot's (%s)" % [d['name'] for d in doors])

            # ---------------------------------------------------------------------------------
            print("\n-- 4. The demand")
            bad = [(l['i'], l['hw'], l['q'], R.link_volume(l['base'])) for l in net['links'] if not l['hw'].endswith('_link') and not near(l['q'], R.link_volume(l['base']), 1e-9)]
            ck(not bad, "each street's traffic a way in the peak hour: its class's typical daily traffic (the middle of FHWA's urban range) at Florida's 9%%, half each way (%s)" % bad[:3])
            ramp = [l for l in net['links'] if l['hw'] == 'motorway_link']
            exp = []
            for l in ramp:
                m = math.inf
                for ji in (l['ja'], l['jb']):
                    j = J[ji]
                    b = max([L[i]['q'] for i in j['ins'] + j['outs'] if not L[i]['hw'].endswith('_link')] or [-1])
                    if b >= 0:
                        m = min(m, b)
                exp.append(m)
            ck(ramp and all(near(l['q'], m, 1e-9) for l, m in zip(ramp, exp)) and near(ramp[0]['q'], R.link_volume('primary'), 1e-9),
               "the ramp carries what the busiest street at its quieter end carries: Market Street's %.1f an hour, not the Expressway's %.1f" % (ramp[0]['q'] if ramp else -1, R.link_volume('motorway')))
            badj = []
            for j in J:
                if not j['ins']:
                    continue
                qi = [max(L[i]['q'], 1e-6) for i in j['ins']]
                qo = [min(L[o]['q'], max(qi)) for o in j['outs']]
                okm = [[any(t[0] == o for t in j['tr'][str(i)]) for o in j['outs']] for i in j['ins']]
                B = R.furness(qi, qo, okm)
                for a, i in enumerate(j['ins']):
                    for t in j['tr'][str(i)]:
                        want = 1 if t[3] else B[a][j['outs'].index(t[0])]
                        if not near(t[1], want, 1e-9):
                            badj.append((j['i'], i, t[0], t[1], want))
            ck(not badj, "each junction's turns by NCHRP 255's balancing of its streets' traffic, no exit drawing more than its busiest way in brings (%s)" % badj[:3])
            j5 = jat(60, 0)
            ex = [t for i in j5['ins'] for t in j5['tr'][str(i)] if L[t[0]]['hw'] == 'motorway']
            ck(j5 and ex and max(t[1] for t in ex) < 0.5, "so the Expressway beginning at Market and 5th takes under half of each way in, not nearly all (%s)" % [round(t[1], 3) for t in ex])

            # ---------------------------------------------------------------------------------
            print("\n-- 5. The run")
            a0 = await safe("()=>window.__a3dTrPools().allocs")
            s0 = await safe("()=>window.__a3dTrStart()") or {}
            ck(not s0.get('err') and s0.get('warm') is True and near(s0.get('t'), 300, 1e-6) and s0['res']['t0'] == s0['t'],
               "Play from still builds the run and warms it up %.0f s before tallying (%s cars by then, %.0f ms)" % (s0.get('t', -1), s0.get('cars'), s0.get('warmMs', -1)))
            ck(s0.get('warmMs', 1e9) < 3000, "the warm-up, 1,500 steps, takes %.0f ms" % s0.get('warmMs', -1))
            ck(await safe("()=>window.__a3dTrPools().allocs") == (a0 or 0) + 1, "the pools allocated once for the run")
            badp = []
            for ji, P in (s0.get('plans') or {}).items():
                Q = ref_plan(net, J[int(ji)])
                if not (near(P['C'], Q['C'], 1e-6) and all(near(a['G'], b['G'], 1e-6) and near(a['Y'], b['Y'], 1e-9) and near(a['AR'], b['AR'], 1e-9) for a, b in zip(P['ph'], Q['ph']))):
                    badp.append((ji, P['C'], Q['C']))
            ck(len(s0.get('plans') or {}) == 2 and not badp, "each signal's plan from its own streets, as the reference times it (%s)" % [(round(P['C'], 1), [round(o['G'], 1) for o in P['ph']]) for P in (s0.get('plans') or {}).values()])
            sb = []
            for ji, P in (s0.get('plans') or {}).items():
                Q = ref_plan(net, J[int(ji)])
                for t in (300.0, 301.7, 317.2, 333.3, 349.9, 362.1, 377.7, 399.9, 421.4, 455.5):
                    A = await safe("(a)=>window.__a3dTrSigAt(a[0],a[1])", [int(ji), t]) or []
                    for k, (s_, left) in enumerate(A):
                        rs, rl = R.signal(Q, k, t)
                        if s_ != rs or not near(left, rl, 1e-6):
                            sb.append((ji, t, k, s_, rs))
            ck(not sb, "each signal's lights through its cycle: green, yellow and red as its plan gives them (%s)" % sb[:3])
            U = await safe("()=>window.__a3dTrUses()") or {}
            rows = [(r['use'], r['n']) for r in U.get('rows', [])]
            tin, tout, _ = R.trips(rows, s0.get('acres'), 'pm')
            ck(sorted(r[0] for r in rows) == ['hotel', 'mdu', 'office', 'retail'] and near(s0['trips']['tin'], tin, 1e-9) and near(s0['trips']['tout'], tout, 1e-9) and near(s0.get('acres'), 1200 / R.ACRE, 1e-9),
               "the design's own trips by its usages: %.1f in and %.1f out in the PM peak on %.3f acres (%s)" % (tin, tout, s0.get('acres') or 0, rows))
            ck(s0.get('share') and s0['share']['t'] > 0 and len(s0.get('stops', [])) >= 1 and len(s0.get('edgeW', [])) >= 1,
               "people by transit and on foot at the census tract's shares, from %d stops and %d edges" % (len(s0.get('stops', [])), len(s0.get('edgeW', []))))
            RT = await safe("()=>window.__a3dTrRoutes()") or []
            sw = [(e, i) for i, e in enumerate(net['edges']) if e['car'] and e['hw'] not in ('service',)]
            jay = []
            for r in RT:
                P = r['P']
                for seg in ((P[0], P[1]), (P[-2], P[-1])):
                    for e, i in sw:
                        if any(seg_cross(seg[0], seg[1], e['P'][q - 1], e['P'][q]) for q in range(1, len(e['P']))):
                            jay.append((r['kind'], r['door'], e['name']))
            xok = all(J[c['j']]['kind'] in ('signal', 'allstop', 'yield') or net['edges'][J[c['j']]['arms'][c['k']]['e']]['hw'] == 'service' for r in RT for c in r['cr'])
            mkt0 = [r for r in RT for c in r['cr'] if abs(J[c['j']]['x'] - 40) < 1 and abs(J[c['j']]['z']) < 1 and L.get(J[c['j']]['arms'][c['k']]['lin'], {}).get('name') == 'Market Street']
            ck(RT and not jay and xok and not mkt0,
               "the walkers' %d ways: onto and off a street on its own side, crossing only at junctions, never Market Street at the driveway's mouth (%s)" % (len(RT), jay[:3]))
            sig_x = sum(1 for r in RT for c in r['cr'] if c['sig'])
            ck(sig_x > 0, "and across Market Street at its signals: %d crossings on the ways" % sig_x)
            h0 = await heap()
            vmax = max(l['v0'] for l in net['links'])
            worst, over, alive, fast = [], 0, 0, 0
            for k in range(60):
                s = await steps(100)
                cars = await safe("()=>window.__a3dTrCars()") or []
                by = {}
                for c in cars:
                    by.setdefault((c[1], c[2]), []).append(c)
                    if c[4] > vmax + 1e-6:
                        fast += 1
                for key, cs in by.items():
                    cs.sort(key=lambda c: c[3])
                    for a_, b_ in zip(cs, cs[1:]):
                        worst.append(b_[3] - R.CAR_L - a_[3])
                alive = max(alive, len(cars))
            r = s['res']
            ck(r['red'] == 0, "twenty minutes of the PM peak: no car crossed its stop line on a red (%d; %s)" % (r['red'], r.get('redAt')))
            ck(r['walkBad'] == 0 and sum(r['cw'][1::2]) > 0, "no walker started across a signalled crossing without its green's time to finish at 3.5 ft/s (%d late; %d crossings)" % (r['walkBad'], sum(r['cw'][1::2])))
            ck(worst and min(worst) >= -1e-3, "no two cars in one place: the smallest gap in a lane over 60 looks %.2f m" % (min(worst) if worst else -1))
            ck(fast == 0, "no car faster than the fastest street's desired speed")
            ck(r['na0'] + r['spawned'] == s['cars'] + r['exited'] + r['lotIn'] and r['spawned'] > 500,
               "every car accounted for: %d at the start and %d come in = %d here + %d gone out + %d into the lot" % (r['na0'], r['spawned'], s['cars'], r['exited'], r['lotIn']))
            ck(r['lotIn'] > 0 and r['lotOut'] > 0 and r['lotIn'] <= tin * 1200 / 3600 + 5 and r['lotOut'] <= tout * 1200 / 3600 + 5,
               "the lot's own cars came in (%d) and went out (%d), no more than its trips in twenty minutes" % (r['lotIn'], r['lotOut']))
            ck(r['lc'] > 0 and r['q']['n'] >= 100, "cars changed lanes (%d) and the lot's queue was sampled every 10 s (%d)" % (r['lc'], r['q']['n']))
            ck(r['carsCap'] == 0 and r['walkCap'] == 0 and alive <= 600 and s0['cap'] == 'Normal', "never more cars or walkers than the pools hold (%d at most; %s)" % (alive, s0.get('cap')))
            ck(await safe("()=>window.__a3dTrPools().allocs") == (a0 or 0) + 1, "still the one allocation after 6,000 steps")
            h1 = await heap()
            for k in range(30):
                await steps(200)
            h2 = await heap()
            ck(h0 and h2 and h2 - h1 < 2e6, "the memory settles: %.2f MB more after 6,000 more steps (%.1f MB in use)" % (((h2 or 0) - (h1 or 0)) / 1e6, (h2 or 0) / 1e6))
            Wk = await safe("()=>window.__a3dTrWalkers()") or []
            ck(all(0.5 - 1e-6 <= w[8] <= R.WALK_MEAN * R.WALK_CAP + 1e-6 for w in Wk) and all(w[3] <= w[8] + 1e-6 for w in Wk),
               "each walker's own speed from Helbing and Molnar's, capped at 1.3 times the mean; none walks faster (%d walking)" % len(Wk))
            res = await safe("()=>window.__a3dTrResults()") or {}
            ck(res.get('doors') and sum(d['n'] for d in res['doors']) > 0 and res.get('q') and any(x['carDelay'] is not None for x in res.get('j', [])),
               "what the run found: people at the doors (%s), the lot's queue, each junction's delays" % [(d['name'], round(d['inH']), round(d['outH'])) for d in res.get('doors', [])])

            # ---------------------------------------------------------------------------------
            print("\n-- 6. On the clock")
            await safe("()=>window.__a3dTrStop()")
            await safe("()=>{window.__a3dAnzView(false);window.__a3dSelectFor([]);window.__a3dSetPlanView();window.__a3dCamSet({tx:20,tz:-10,dist:200});}")
            u0 = await safe("()=>window.__a3dUndoDepth()")
            ok = await safe("()=>window.__a3dRunCmd('traffic')")
            await page.wait_for_timeout(200)
            a1 = await anim()
            s1 = await summary() or {}
            ck(ok and a1.get('on') is True and s1.get('warm') is True and (await safe("()=>window.__a3dTrSettings()") or {}).get('on') is True,
               "TRAFFIC turns it on and plays it: the run built and warmed up, the clock running (%s)" % {k: a1.get(k) for k in ('on', 'live')})
            ck(await safe("()=>window.__a3dUndoDepth()") == (u0 or 0) + 1, "turning it on is one undo step")
            t0 = await safe("()=>performance.now()")
            await page.wait_for_timeout(2000)
            el = ((await safe("()=>performance.now()")) - t0) / 1000
            s2 = await summary() or {}
            adv = s2.get('t', 0) - s1.get('t', 0)
            ck(0.4 * el <= adv <= el + 0.2, "it runs with the clock: %.2f s of traffic in %.2f s" % (adv, el))
            await safe("()=>document.getElementById('a3d-animplay').click()")
            p1 = await summary() or {}
            await page.wait_for_timeout(600)
            p2 = await summary() or {}
            ck((await anim()).get('paused') is True and p2.get('t') == p1.get('t') and p2.get('cars') == p1.get('cars'), "Pause keeps the moment (t %.1f s)" % p1.get('t', -1))
            al = await safe("()=>window.__a3dTrPools().allocs")
            await safe("()=>document.getElementById('a3d-animplay').click()")
            await page.wait_for_timeout(500)
            p3 = await summary() or {}
            ck(p3.get('t', 0) > p1.get('t', 0) and await safe("()=>window.__a3dTrPools().allocs") == al, "Play goes on from it, the same run")
            await safe("()=>window.__a3dTrAct('speed:16')")
            q1 = await summary() or {}
            t0 = await safe("()=>performance.now()")
            await page.wait_for_timeout(1500)
            el = ((await safe("()=>performance.now()")) - t0) / 1000
            q2 = await summary() or {}
            ck((q2.get('t', 0) - q1.get('t', 0)) > 6 * el, "at 16 times the clock: %.1f s of traffic in %.2f s" % (q2.get('t', 0) - q1.get('t', 0), el))
            await safe("()=>window.__a3dTrAct('speed:1')")
            await safe("()=>document.getElementById('a3d-animstop').click()")
            await page.wait_for_timeout(300)
            ck(await summary() is None and (await safe("()=>window.__a3dTrResults()") or {}).get('t', 0) > 0 and (await anim()).get('on') is False,
               "Stop gives the run up and keeps what it found")
            ck(await safe("()=>window.__a3dTrAct('peak:am')") is True and (await safe("()=>window.__a3dTrSettings()") or {}).get('peak') == 'am', "the AM peak chosen")
            await safe("()=>window.__a3dUndo()")
            ck((await safe("()=>window.__a3dTrSettings()") or {}).get('peak') == 'pm', "and undone: the PM peak again")
            await safe("()=>window.__a3dTrAct('q:light')")
            await safe("()=>window.__a3dAnimPlay(true)")
            await page.wait_for_timeout(300)
            sl = await summary() or {}
            ck(sl.get('qk') == 'light' and sl.get('cap') == 'Light' and (await safe("()=>window.__a3dTrPools()") or {}).get('cars') == 200,
               "Light chosen by hand: the next Play from still runs 200 cars and 300 walkers (%s)" % sl.get('cap'))
            ms = await safe("()=>{var t=performance.now();window.__a3dTrSteps(500);return (performance.now()-t)/500;}") or 1e9
            per = math.ceil(16 * 0.1 / R.STEP) + 1   # the most steps a frame takes at 16 times the clock
            ck(ms * per < 1000 / 20 * 0.6, "a frame within its budget at Light (20 a second): %.2f ms a step, %d steps at 16 times %.1f ms of a 50 ms frame" % (ms, per, ms * per))
            ck(await safe("()=>window.__a3dTrAct('sim:off')") is True and await summary() is None and (await safe("()=>window.__a3dTrSettings()") or {}).get('on') is False,
               "the row's Stop the simulation turns it off")
            await safe("()=>window.__a3dTrAct('q:auto')")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Drawn")
            await safe("()=>window.__a3dRunCmd('traffic')")
            await only(['traffic'])
            await safe("()=>{window.__a3dAnzView(false);window.__a3dSetPlanView();window.__a3dCamSet({tx:20,tz:-10,dist:180});}")
            await page.wait_for_timeout(700)
            await safe("()=>document.getElementById('a3d-animplay').click()")   # paused: the moment drawn is the run's
            await page.wait_for_timeout(200)
            d1 = await safe("()=>window.__a3dTrDrawn()") or {}
            s3 = await summary() or {}
            ck(d1.get('cars') == s3.get('cars') and d1.get('walkers') == s3.get('walkers') and d1.get('lines') == 8,
               "in plan every car and walker is drawn, and the eight signalled approaches' stop lines (%s)" % d1)
            ink = await safe("""()=>{var C=window.__a3dTrCars(),c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width,g=c.getContext('2d'),n=0,hit=0,i;
              for(i=0;i<C.length&&n<40;i++){var p=window.__a3dDgToScreen([C[i][7],0.1,C[i][8]]);if(!p||p[0]<5||p[1]<5||p[0]>c.getBoundingClientRect().width-5||p[1]>c.getBoundingClientRect().height-5)continue;
                n++;var d=g.getImageData(Math.round(p[0]*s)-2,Math.round(p[1]*s)-2,5,5).data,m=0,k;for(k=3;k<d.length;k+=4)if(d[k]>m)m=d[k];if(m>200)hit++;}return [n,hit];}""") or [0, 0]
            ck(ink[0] >= 5 and ink[1] >= 0.8 * ink[0], "and on the canvas: ink where %d of %d cars in view are" % (ink[1], ink[0]))
            await safe("()=>{window.__a3dSet3DView();window.__a3dCamSet({tx:40,tz:0,dist:140});}")
            await page.wait_for_timeout(700)
            d2 = await safe("()=>window.__a3dTrDrawn()") or {}
            ck(d2.get('cars', 0) > 0 and d2.get('faces', 0) > d2.get('cars', 0) * 5, "in 3D the cars as V169's design car, face by face (%s)" % d2)
            await safe("()=>document.getElementById('a3d-animplay').click()")
            D = await safe("()=>window.__a3dDgState()") or {}
            await safe("(id)=>window.__a3dLayerSet(id,'visible',false)", D.get('layers', {}).get('traffic'))
            await page.wait_for_timeout(400)
            d3 = await safe("()=>window.__a3dTrDrawn()") or {}
            ck(d3.get('cars') == 0 and d3.get('lines') == 0, "with its layer off, none drawn (%s)" % d3)
            await safe("(id)=>window.__a3dLayerSet(id,'visible',true)", D.get('layers', {}).get('traffic'))
            await safe("()=>window.__a3dSetPlanView()")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. The results as layers")
            await page.wait_for_timeout(1500)
            out = (await safe("()=>window.__a3dDgRun('traffic')") or {}).get('traffic') or {}
            el_ = await safe("()=>window.__a3dDgList('traffic')") or []
            keys = sorted(e['k'] for e in el_)
            n5 = jat(60, 0)['n']
            n3 = jat(-180, 0)['n']
            ck('sig:%d' % n5 in keys and 'sig:%d' % n3 in keys and 'entry' in keys and 'door:0' in keys and 'door:1' in keys and any(k.startswith('xing:') for k in keys),
               "Run lays each signal's plan, the lot's entry, its doors and each junction's delays (%s)" % keys)
            lys = set(e['layer'] for e in el_)
            ck(len(lys) == 1 and D.get('layers', {}).get('traffic') in lys, "all on Layers > Site analysis - Traffic and people")
            obj = await safe("(k)=>{var o=window.__a3dState().objs.filter(function(x){return x.t==='diag'&&x.dg.a==='traffic'&&x.dg.k===k;})[0];return o?o.dg:null;}", 'sig:%d' % n5) or {}
            mt = ((obj.get('g') or {}).get('marks') or [{}])[0].get('t', '')
            P5 = ref_plan(net, jat(60, 0))
            ck(re.match(r'^Signal: \d+ s cycle', mt) and str(int(round(P5['C']))) in mt, "a signal's mark says its cycle (%s)" % mt)
            await safe("()=>window.__a3dAnzView(true)")
            await safe("()=>window.__a3dAnzOpenAll(true)")
            await page.wait_for_timeout(400)
            card = await safe("""()=>{var c=document.querySelector('[data-anzcard="dgtraffic"]');if(!c)return null;
              return {acts:Array.prototype.map.call(c.querySelectorAll('[data-anzact]'),function(b){return b.getAttribute('data-anzact');}),text:c.textContent,
                pressed:Array.prototype.filter.call(c.querySelectorAll('[aria-pressed="true"]'),function(){return true;}).length};}""") or {}
            ck(set(['tr:sim:off', 'tr:peak:am', 'tr:peak:pm', 'tr:q:auto', 'tr:q:light', 'tr:q:normal', 'tr:q:detailed', 'tr:speed:1', 'tr:speed:4', 'tr:speed:16']).issubset(set(card.get('acts', []))) and card.get('pressed') == 3,
               "its row: Stop the simulation, the peak hour, the quality and the speed, the chosen one pressed in each (%s)" % card.get('acts'))
            ck('San Diego' in card.get('text', '') and 'Not a calibrated model' in card.get('text', ''), "and what the run assumes, in words")
            await safe("""()=>{var b=document.querySelector('[data-anzcard="dgtraffic"] [data-anzact="tr:peak:am"]');if(b)b.click();}""")
            await page.wait_for_timeout(300)
            ck((await safe("()=>window.__a3dTrSettings()") or {}).get('peak') == 'am', "its AM button sets the peak hour")
            await safe("()=>window.__a3dTrAct('peak:pm')")
            await safe("()=>window.__a3dTrAct('sim:off')")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Without a driveway, without signals")
            ST['tr'] = ('nodrive', 'nosig')
            await setup()
            n2 = await safe("()=>window.__a3dTrNet()") or {}
            lt = n2.get('lot') or {}
            pe = [e for e in n2.get('edges', []) if e.get('lot')]
            ck(lt.get('prov') is True and lt.get('name') == 'Provisional entry from the alley' and pe and abs(n2['z'][lt['at']] + 50) < 0.6 and not [j for j in n2.get('J', []) if j['kind'] == 'signal'],
               "no driveway mapped: a provisional entry from the lot's lowest street, the alley, as V166 marks it (%s); no signal mapped: none simulated" % lt.get('name'))
            s4 = await safe("()=>window.__a3dTrStart()") or {}
            s4 = await steps(1500) or {}
            ck(s4.get('lotOk') and not s4.get('plans') and s4['res']['red'] == 0 and s4['res']['na0'] + s4['res']['spawned'] == s4['cars'] + s4['res']['exited'] + s4['res']['lotIn'],
               "and it still runs, the lot's trips through its provisional entry, every car accounted for")
            await safe("()=>window.__a3dTrStop()")
            ST['tr'] = ()
            await setup()

            # ---------------------------------------------------------------------------------
            print("\n-- 10. A phone, a tablet, a computer")
            await safe("()=>window.__a3dAnzView(true)")
            await safe("()=>window.__a3dAnzOpenAll(true)")
            for (vw, vh, name) in ((390, 844, 'a phone'), (820, 1180, 'a tablet held upright'), (1440, 900, 'a computer')):
                await page.set_viewport_size({'width': vw, 'height': vh})
                await page.wait_for_timeout(500)
                await safe("()=>{window.__a3dAnzView(true);window.__a3dAnzOpenAll(true);}")   # a narrow screen closes the panel: Analyze opened again
                await page.wait_for_timeout(400)
                lay = await safe("""()=>{var c=document.querySelector('[data-anzcard="dgtraffic"]'),w=document.querySelector('.a3d-analyze-wrap');if(!c||!w)return null;
                  var B=c.querySelectorAll('.a3d-trset button'),o=[],i,wr=w.getBoundingClientRect(),cr=c.getBoundingClientRect();
                  for(i=0;i<B.length;i++){var r=B[i].getBoundingClientRect();o.push([r.left,r.right,r.width]);}
                  return {b:o,card:[cr.left,cr.right],wrap:[wr.left,wr.right],sw:w.scrollWidth,cw:w.clientWidth,vw:window.innerWidth,doc:document.documentElement.scrollWidth};}""") or {}
                bs, cd = lay.get('b') or [], lay.get('card') or [0, 0]
                ck(bs and lay['wrap'][0] >= -0.5 and lay['wrap'][1] <= lay['vw'] + 0.5 and all(b[0] >= cd[0] - 0.5 and b[1] <= cd[1] + 0.5 and b[2] > 20 for b in bs) and
                   lay.get('sw', 1e9) <= lay.get('cw', 0) + 1 and lay.get('doc', 1e9) <= lay.get('vw', 0) + 1,
                   "%s: in Analyze, the row's %d buttons within it, none cut, nothing spilling sideways (%s)" % (name, len(bs), {k: lay.get(k) for k in ('card', 'wrap', 'sw', 'cw', 'vw')}))
            await page.set_viewport_size({'width': 1440, 'height': 900})
            for mem, cores, want in ((2, 8, 'light'), (4, 2, 'light'), (4, 4, 'normal'), (8, 8, 'detailed'), (None, 8, 'normal')):
                pc = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
                await pc.add_init_script("(function(){%s Object.defineProperty(navigator,'hardwareConcurrency',{get:function(){return %d;}});})()" %
                                         ("Object.defineProperty(navigator,'deviceMemory',{get:function(){return %d;}});" % mem if mem else "Object.defineProperty(navigator,'deviceMemory',{get:function(){return undefined;}});", cores))
                pp = await pc.new_page()
                await within(pp.goto('file://' + str(HTML)), 'goto')
                await pp.wait_for_timeout(1500)
                q = await safe("()=>window.__a3dTrDeviceQ()", pg=pp)
                th = await safe("()=>{var b=document.createElement('button');b.className='a3d-anzbtn';b.textContent='AM';document.body.appendChild(b);var h=b.getBoundingClientRect().height;b.remove();return h;}", pg=pp)
                ck(q == want and (th or 0) >= 34, "%s GB and %d cores: the quality suggested is %s; a phone's row buttons a thumb's height (%s px)" % (mem, cores, q, th))
                await pc.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 11. A reload")
            await safe("()=>window.__a3dTrAct('peak:am')")
            await safe("()=>window.__a3dTrAct('speed:4')")
            await safe("()=>window.__a3dRunCmd('traffic')")
            await page.wait_for_timeout(1200)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter&&window.__a3dEnter()")
            await page.wait_for_timeout(500)
            sr = await safe("()=>window.__a3dTrSettings()") or {}
            ck(sr.get('on') is True and sr.get('peak') == 'am' and sr.get('speed') == 4 and await summary() is None and (await anim()).get('on') is False,
               "reloaded: the simulation's settings kept (on, AM, 4 times), and it opens still, to play when asked (%s)" % sr)

            # ---------------------------------------------------------------------------------
            print("")
            ck(not errs, "zero uncaught page errors (%s)" % (errs[:3] or 'none'))
        except Stalled as e:
            ck(False, "STALLED: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite raised")
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
