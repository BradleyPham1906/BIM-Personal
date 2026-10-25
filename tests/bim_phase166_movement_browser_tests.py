#!/usr/bin/env python3
"""bim_phase166_movement_browser_tests.py -- V166: site analysis in the model III, movement.

The neighbourhood is tests/movement_fixture.py's: V161's street grid with a case of each rule added
(tags, crossings and their controls, doors, a garage, car parks, headways, a driveway). Everything the
six analyses draw is worked out again here, in tests/movement_reference.py: level of traffic stress from
the published 2012 criteria, the 2016 crossing table, the low-stress reach by two Dijkstras, PTAL by
TfL's method; the paths against the walk times; the drawing against the data.

  1. THE RUN: the access step asks for movement's parts and keeps them; V161's layer no longer added.
  2. THE DATA: the streets within 800 m with their tags, thinned; the crossings, doors, garage and car
     parks; the lines' headways and streets; the paths to the nearest of each need and stop.
  3. STRESS: the criteria case by case, every street's level, the speeds, rows, intervals and parking.
  4. CROSSINGS AND REACH: the junctions against the 2016 table; the reach against two Dijkstras.
  5. PTAL: the index and its band, a floor, none; the bands' edges.
  6. THE LAYERS: the hierarchy, cycling, transit, walk times, daily needs, vehicles -- each element
     against the data; the colours for a dark plan and a light map; the pixels.
  7. FINDINGS AND ROWS: transit's PTAL, cycling, vehicles; the rows in their categories.
  8. ELSEWHERE: no driveway (a provisional entry), the node budget, a project from before V166,
     Overpass down, a phone and a tablet.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import movement_fixture as FX     # noqa: E402
import movement_reference as MR   # noqa: E402
import access_reference as AR     # noqa: E402
import access_fixture as AFX      # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
LOT = [list(p) for p in AFX.LOT]
DARK = {'mt': '#f6c780', 'ar': '#e99d4c', 'co': '#cf7a33', 'lo': '#a85a26', 'sv': '#8b9098', 'pa': '#6fc6a0'}
LIGHT = {'mt': '#6e2a0a', 'ar': '#9e4313', 'co': '#c2641d', 'lo': '#d98a2b', 'sv': '#7a7f87', 'pa': '#2e8a62'}
WEIGHT = {'mt': 5.5, 'ar': 4.4, 'co': 3.3, 'lo': 2.2, 'sv': 1.2, 'pa': 1.3}
LTS_DK = [None, '#3987e5', '#199e70', '#c98500', '#e34948']
LTS_LT = [None, '#2a78d6', '#1baf7a', '#eda100', '#e34948']


def klass(hw):
    hw = str(hw or '')
    for k, rx in (('mt', r'^(motorway|trunk)(_link)?$'), ('ar', r'^primary(_link)?$'), ('co', r'^(secondary|tertiary)(_link)?$'),
                  ('lo', r'^(residential|unclassified|living_street|road)$'), ('sv', r'^service$'), ('pa', r'^(pedestrian|footway|path|cycleway|bridleway|steps|track)$')):
        if re.match(rx, hw):
            return k
    return None


def seg_len(P):
    return sum(math.hypot(P[i][0] - P[i - 1][0], P[i][-1] - P[i - 1][-1]) for i in range(1, len(P)))


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def fresh(store, vw=(1440, 900), mobile=False):
            c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
            for h in FX.HOSTS:
                await c.route(h, FX.route_handler(store))
            for h in BLOCKERS:
                await c.route(h, lambda r: r.abort())
            p = await c.new_page()
            e = []
            p.on('pageerror', lambda x: e.append(str(x)))
            await within(p.goto('file://' + str(HTML)), 'goto')
            await p.wait_for_timeout(2000)
            await p.evaluate("()=>window.__a3dEnter()")
            await p.evaluate("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT)
            await p.evaluate("()=>window.__a3dAnzView(true)")
            await p.wait_for_timeout(200)
            return c, p, e

        ST = {}
        ctx, page, errs = await fresh(ST)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def wait_run(pg=None, bound=120):
            for _ in range(bound * 4):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    await safe("()=>window.__a3dAwClassic&&window.__a3dAwClassic()", pg=pg)   # V171b: a run ends in the analysis workspace with none shown; this suite reads each analysis as a run drew it before
                    return s
                await (pg or page).wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def analyze(pg=None):
            await (pg or page).fill('[data-saaddr]', '1 Market Street')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=pg)
            return await wait_run(pg=pg)

        async def diags(a=None, pg=None):
            return [o for o in ((await safe("()=>window.__a3dState().objs", pg=pg)) or []) if o.get('t') == 'diag' and (a is None or o['dg']['a'] == a)]

        async def el(a, k, pg=None):
            for o in await diags(a, pg=pg):
                if o['dg']['k'] == k:
                    return o
            return None

        def rows(o):
            return {r[0]: r[1] for r in o['dg']['info'].get('rows', [])}

        def P2(o):
            return [[p[0], p[2]] for p in o['dg']['g'].get('pts', [])]

        try:
            fin = await analyze()
            steps = {s['id']: s for s in fin.get('steps', [])}
            ACC = (await safe("()=>window.__a3dAcc()") or {}).get('access') or {}
            mv = await safe("()=>window.__a3dMvGet()") or {}
            Lr = AR.Lot(ring=LOT)

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The run")
            ck(await safe("()=>typeof window.__acad3dV166==='string'&&/lts2012/.test(window.__acad3dV166)&&/ptal/.test(window.__acad3dV166)") is True, "the V166 marker")
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(re.match(r'^V\d+$', ver) and int(ver[1:]) >= 166, "the app says V166 or later (%s)" % ver)
            ck(steps.get('access', {}).get('state') == 'ok' and steps.get('draw', {}).get('state') == 'ok', "the access step and the drawing are done (%s)" % steps.get('access', {}).get('text'))
            qs = [h[1] for h in ST.get('hits', []) if h[0] == 'acc' and '/api/interpreter' in h[1]]
            from urllib.parse import unquote
            q = unquote(qs[-1]) if qs else ''
            ck('node["highway"~"^(traffic_signals|stop|crossing)$"]' in q and 'node["crossing"]' in q and 'node["entrance"]' in q and 'node["amenity"="parking_entrance"]' in q
               and 'way["amenity"="parking"]' in q and 'out tags geom qt' in q, "one access request asks for the crossings, the doors, the garage entrances and the car parks")
            m1 = re.findall(r'\(around:(\d+),', q)
            rl = max(math.hypot(x, z) for x, z in LOT)
            ck(str(round(800 + rl + 50)) in m1 and str(round(400 + rl)) in m1, "the crossings within the window, the car parks within 400 m, from the site (%s)" % sorted(set(m1)))
            ck(isinstance(mv.get('w'), list) and mv.get('r') == 800 and not mv.get('error'), "the movement data kept with the access data (%s ways)" % len(mv.get('w') or []))
            ck(not [x for x in (await safe("()=>window.__a3dResultLayers()") or []) if x['kind'] == 'walk'], "V161's Walk times layer is not added: Analyze site draws the walk times in the model")
            await safe("()=>window.__a3dRunCmd('walktimes')")
            ck(len([x for x in (await safe("()=>window.__a3dResultLayers()") or []) if x['kind'] == 'walk']) == 1, "WALKTIMES still adds it on request")
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The data")
            X, Z, T, Wr = mv['x'], mv['z'], mv['t'], mv['w']
            allowed = re.compile(r'^(highway|name|ref|maxspeed|maxspeed:type|zone:maxspeed|source:maxspeed|lanes|lanes:forward|lanes:backward|oneway|oneway:bicycle|junction|cycleway(:[a-z_:]+)?|parking(:[a-z_:]+)?|sidewalk(:[a-z_:]+)?|service|access|bicycle|motor_vehicle|motorcar|foot|segregated|lane_markings|bridge|tunnel|layer|bicycle_road|cyclestreet|shoulder(:[a-z_:]+)?)$')
            ck(all(allowed.match(k) for t in T for k in t), "each way keeps only the tags movement reads")
            side = [r for r in Wr if all(X[i] in (55.0, 65.0) for i in r[1:])]   # the fixture's sidewalks, 5 m either side of 5th Street
            ck(not side and all(t.get('highway') for t in T), "sidewalks drawn on their own are not kept (%d); every way a street or a path" % len(side))
            far = []
            for rec in Wr:
                inside = [Lr.dist(X[i], Z[i]) <= 850 for i in rec[1:]]
                if not any(inside):
                    far.append(rec)
                # the ends may lie one node beyond the window, so the line reaches its edge
                if not all(inside[1:-1]):
                    far.append(rec)
            ck(not far, "every way's nodes within 800 m of the lot (and 50 more), but an end node beyond (%d)" % len(far))
            ck(any(Lr.dist(X[r[1]], Z[r[1]]) > 850 or Lr.dist(X[r[-1]], Z[r[-1]]) > 850 for r in Wr), "a way crossing the window's edge keeps its node beyond, so its line reaches the edge")
            # the junctions: where two of the fixture's ways share a node within the window, the kept ways share one there too
            idx = {(round(X[i], 1), round(Z[i], 1)): i for i in range(len(X))}
            uses = {}
            for rec in Wr:
                for i in set(rec[1:]):
                    uses[i] = uses.get(i, 0) + 1
            want = [(-60, -400), (180, -400), (420, -400), (60, 0), (180, 0), (300, 0), (60, -100), (540, -200), (660, -100), (40, 0)]
            ck(all(idx.get((float(x), float(z))) is not None and uses.get(idx[(float(x), float(z))], 0) >= 2 for x, z in want),
               "junctions kept as one node shared by the ways meeting there (the driveway's on Market Street among them)")
            xs = {(c[0], c[1]): c[2] for c in mv.get('xs', [])}
            ck(xs.get((-60.0, -400.0)) == 's' and xs.get((180.0, -400.0)) == 'a' and xs.get((420.0, -400.0)) == 'p' and xs.get((300.0, 0.0)) == 'ci',
               "the crossings' controls: a signal, an all-way stop, a stop on the approach only, a marked crossing with an island (%s)" % xs)
            en = mv.get('en') or []
            ck(sorted((d[0], d[1], d[2]) for d in en) == [(12.0, -38.0, 'service'), (30.0, -10.0, 'main')] and [d[3] for d in en if d[2] == 'main'] == ['Main door'],
               "the doors on the lot: on its line and inside it, not one 20 m off (%s)" % en)
            REF = AR.Ref(AR.Lot(ring=LOT))
            pe = mv.get('pe') or []
            ck(len(pe) == 1 and pe[0][3] == 'Garage A' and pe[0][4] == 'customers' and abs(pe[0][2] - REF.point(100, -60)['t']) <= 0.05,
               "the garage entrance, its walk along the streets (%s)" % pe)
            cp = {c['n']: c for c in mv.get('cp') or []}
            ck(sorted(cp) == ['Deck P2', 'Lot P1'], "the car parks within 400 m, not the one beyond (%s)" % sorted(cp))
            p1 = cp.get('Lot P1', {})
            rt1 = REF.ring_time(FX.CARPARKS[0][0], step=15.0, maxR=60.0)
            ck(p1.get('k') == 'surface' and p1.get('cap') == 40 and p1.get('ac') == 'yes' and p1.get('fee') == 'yes' and abs(p1.get('a', 0) - 1200) <= 1 and
               p1.get('t') is not None and abs(p1['t'] - rt1) <= 0.06, "Lot P1: surface, 40 spaces, public, a fee, 1200 m2, its walk to its edge (%s against %.2f)" % (p1, rt1))
            ck(cp.get('Deck P2', {}).get('cap') is None and cp.get('Deck P2', {}).get('k') == 'multi-storey', "Deck P2: its spaces not mapped, said as such")
            iv = mv.get('iv') or {}
            ck(iv == {'bus|12': 10, 'bus|42': 15, 'metro|A': 5, 'tram|T1': None, 'bus|7': 20, 'rail|R': None},
               "each line's headway, the least of its relations' (12: 10 and 12 minutes) (%s)" % iv)
            rt = {r['m'] + '|' + r['l']: r for r in mv.get('rt') or []}
            ms_w = sorted(i for i, rec in enumerate(Wr) if T[rec[0]].get('name') == 'Market Street')
            st5 = sorted(i for i, rec in enumerate(Wr) if T[rec[0]].get('name') == '5th Street')
            ck(rt.get('bus|12', {}).get('w') == ms_w and rt.get('bus|42', {}).get('w') == st5 and rt.get('metro|A', {}).get('w') == [],
               "each line's streets within the window: 12 along Market Street, 42 along 5th Street, none for A")
            # the paths: from the lot line to the place, their length the walk time's
            bad = []
            places = {p['k']: p for p in ACC.get('places', [])}
            for p in mv.get('paths', []):
                pts = [(p['pts'][i], p['pts'][i + 1]) for i in range(0, len(p['pts']), 2)]
                tgt = places[p['k']]['near'][0] if p['k'] in places else ACC['stops'][ACC['bus' if p['k'] == 'bus' else 'rail']]
                L = seg_len(pts)
                if Lr.dist(*pts[0]) > 0.05 or math.hypot(pts[-1][0] - tgt['x'], pts[-1][1] - tgt['z']) > 0.15 or abs(L / 80 - tgt['t']) > 0.05:
                    bad.append((p['k'], round(L / 80, 3), tgt['t'], Lr.dist(*pts[0])))
            ck(len(mv.get('paths', [])) == len([p for p in ACC.get('places', []) if p['near']]) + (ACC.get('bus', -1) >= 0) + (ACC.get('rail', -1) >= 0) and not bad,
               "a path to the nearest of each daily need and to the nearest stop and station: from the lot line to the place, as long as its walk (%s)" % bad)
            for p in mv.get('paths', []):
                if p['k'] == 'eat':
                    ck(len(p['pts']) == 4, "a place across the street from the lot: the straight step, as the walk takes it (%s)" % p['pts'])

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Stress")
            CASES = [
                ({'highway': 'cycleway'}, 1), ({'highway': 'path'}, 1), ({'highway': 'footway'}, 0), ({'highway': 'footway', 'bicycle': 'yes'}, 1),
                ({'highway': 'pedestrian'}, 0), ({'highway': 'pedestrian', 'bicycle': 'designated'}, 1), ({'highway': 'steps'}, 0), ({'highway': 'track'}, 2),
                ({'highway': 'living_street'}, 1), ({'highway': 'primary', 'motor_vehicle': 'no'}, 1), ({'highway': 'motorway'}, 0), ({'highway': 'trunk', 'bicycle': 'no'}, 0),
                ({'highway': 'residential', 'access': 'private'}, 0), ({'highway': 'service'}, 2), ({'highway': 'service', 'maxspeed': '30 mph'}, 3),
                ({'highway': 'primary', 'cycleway': 'track'}, 1), ({'highway': 'primary', 'cycleway:right': 'track', 'maxspeed': '50 mph'}, 1),
                # a bike lane beside parking: the lanes each way, the speed
                ({'highway': 'residential', 'cycleway:both': 'lane', 'parking:both': 'lane', 'maxspeed': '25 mph', 'lanes': '2'}, 1),
                ({'highway': 'residential', 'cycleway:both': 'lane', 'parking:both': 'lane', 'maxspeed': '30 mph', 'lanes': '2'}, 2),
                ({'highway': 'tertiary', 'cycleway': 'lane', 'parking:lane:both': 'parallel', 'maxspeed': '35 mph', 'lanes': '2'}, 3),
                ({'highway': 'secondary', 'cycleway': 'lane', 'parking:right': 'lane', 'maxspeed': '40 mph', 'lanes': '2'}, 4),
                ({'highway': 'secondary', 'cycleway': 'lane', 'parking:both': 'lane', 'maxspeed': '25 mph', 'lanes': '4'}, 3),
                # a bike lane with no parking: lanes each way (a divided road's carriageway), width, speed
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '2'}, 1),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '4'}, 3),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '2', 'oneway': 'yes'}, 2),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '3', 'oneway': 'yes'}, 3),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '2', 'cycleway:width': '1.5'}, 2),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '30 mph', 'lanes': '2', 'cycleway:width': '2'}, 1),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '35 mph', 'lanes': '2'}, 3),
                ({'highway': 'secondary', 'cycleway': 'lane', 'maxspeed': '40 mph', 'lanes': '2'}, 4),
                # mixed traffic: speed rows, lanes columns, the lower value on a residential street of under 3 lanes
                ({'highway': 'residential', 'maxspeed': '25 mph', 'lanes': '2'}, 1), ({'highway': 'tertiary', 'maxspeed': '25 mph', 'lanes': '2'}, 2),
                ({'highway': 'residential', 'maxspeed': '25 mph', 'lanes': '3'}, 2), ({'highway': 'tertiary', 'maxspeed': '25 mph', 'lanes': '4'}, 3),
                ({'highway': 'tertiary', 'maxspeed': '25 mph', 'lanes': '6'}, 4), ({'highway': 'residential', 'maxspeed': '30 mph'}, 2),
                ({'highway': 'tertiary', 'maxspeed': '30 mph', 'lanes': '2'}, 3), ({'highway': 'tertiary', 'maxspeed': '30 mph', 'lanes': '4'}, 4),
                ({'highway': 'residential', 'maxspeed': '35 mph'}, 4), ({'highway': 'tertiary', 'lanes': '2', 'lane_markings': 'no', 'maxspeed': '25 mph'}, 1),
                ({'highway': 'residential'}, 1), ({'highway': 'unclassified'}, 1), ({'highway': 'secondary'}, 3), ({'highway': 'primary'}, 4),
                ({'highway': 'residential', 'maxspeed': '30'}, 1), ({'highway': 'residential', 'maxspeed': '50'}, 2), ({'highway': 'residential', 'maxspeed': 'DE:urban'}, 2),
                ({'highway': 'residential', 'zone:maxspeed': 'DE:30'}, 1), ({'highway': 'residential', 'lanes:forward': '1', 'lanes:backward': '2'}, 2),
                ({'highway': 'trunk', 'oneway': 'yes'}, 4), ({'highway': 'trunk', 'oneway': 'yes', 'maxspeed': '25 mph'}, 2),
                ({'highway': 'tertiary', 'zone:maxspeed': 'DE:30'}, 2),
            ]
            got = await safe("(L)=>L.map(function(t){return window.__a3dMvLts(t).lts;})", [c[0] for c in CASES]) or []
            badc = [(c[0], c[1], g, MR.lts(c[0])) for c, g in zip(CASES, got) if not (g == c[1] == MR.lts(c[0]))]
            ck(len(got) == len(CASES) and not badc, "the 2012 criteria, case by case: %d tags, each level as the published tables give it, and as the reference does (%s)" % (len(CASES), badc[:4]))
            why = await safe("()=>window.__a3dMvLts({highway:'tertiary',cycleway:'lane',maxspeed:'35 mph',lanes:'2',parking:'no'})") or {}
            ck('bike lane, no parking' in why.get('why', '') and 'its width not mapped' in why.get('why', '') and '(LTS 3)' in why.get('why', '') and why.get('sp', {}).get('src') == 'mapped',
               "each level says why, and what was mapped or assumed (%s)" % why.get('why'))
            S1 = await safe("()=>window.__a3dMvStress()") or {}
            W = S1.get('W') or []
            badw = [(i, T[rec[0]].get('name'), W[i], MR.lts(T[rec[0]])) for i, rec in enumerate(Wr) if i >= len(W) or W[i] != MR.lts(T[rec[0]])]
            ck(len(W) == len(Wr) and not badw, "every street's level as the reference works it out (%d streets; %s)" % (len(Wr), badw[:3]))
            lv = {}
            for i, rec in enumerate(Wr):
                lv.setdefault(T[rec[0]].get('name') or T[rec[0]].get('highway'), set()).add(W[i] if i < len(W) else None)
            ck(lv.get('S1 Street') == {2} and lv.get('N1 Street') == {4} and lv.get('Avenue 18') == {1} and lv.get('Avenue 14') == {4} and lv.get('North Boulevard') == {4} and
               lv.get('Market Street') == {3} and lv.get('5th Street') == {2} and lv.get('Expressway') == {0} and lv.get('Hill Steps') == {0} and lv.get('Park Path') == {1} and
               lv.get('Avenue 17') == {1} and lv.get('Avenue 20') == {3}, "the streets the fixture tags: a lane beside parking 2, 35 mph 4, a track 1, six lanes 4, 40 mph 4, Market Street's lane 3, 25 mph 2 (%s)" %
               {k: sorted(x for x in v if x is not None) for k, v in lv.items() if k in ('S1 Street', 'N1 Street', 'Avenue 18', 'Avenue 14', 'North Boulevard', 'Market Street', '5th Street', 'Expressway', 'Hill Steps', 'Park Path', 'Avenue 17', 'Avenue 20')})
            kmh = await safe("(L)=>L.map(function(s){return window.__a3dMvKmh(s);})", ['30 mph', '50', '48 km/h', 'walk', 'none', 'DE:urban', 'FR:rural', 'GB:nsl_single', 'DE:zone30', 'x', '']) or []
            ck(len(kmh) == 11 and abs(kmh[0] - 48.28) < 0.01 and kmh[1] == 50 and kmh[2] == 48 and kmh[3] == 7 and kmh[4] == 130 and kmh[5] == 50 and kmh[6] == 90 and abs(kmh[7] - 96.6) < 0.01 and kmh[8] == 30 and kmh[9] is None and kmh[10] is None,
               "speed limits read: mph, km/h, walk, none, a country's urban and rural, the UK's national limit, a zone (%s)" % kmh)
            rows_ = await safe("(L)=>L.map(function(v){return window.__a3dMvRow(v);})", [40, 40.23, 41, 41.1, 48.28, 50, 51, 56.33, 60, 61, 64.37]) or []
            ck(rows_ == [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3], "the rows: 40 km/h and 25 mph together, 50 and 30 mph, 60 and 35 mph, then 40 mph and over (%s)" % rows_)
            ivs = await safe("(L)=>L.map(function(v){return window.__a3dMvInterval(v);})", ['10', '00:12', '1:05', '00:07:30', '7.5', 'every 10', '0', '800', '']) or []
            ck(ivs == [10, 12, 65, 7.5, 7.5, None, None, None, None], "a route's interval: minutes, HH:MM, HH:MM:SS; not a sentence, nothing, or past 12 hours (%s)" % ivs)
            pk = await safe("(L)=>L.map(function(t){var p=window.__a3dMvParking(t);return [p.l,p.r];})", [{'parking:both': 'lane'}, {'parking:left': 'street_side', 'parking:right': 'no'},
                                                                                                         {'parking:lane:both': 'parallel'}, {'parking:lane:right': 'no_stopping'}, {}]) or []
            ck(pk == [[True, True], [True, False], [True, True], [None, False], [None, None]], "parking by side: the street parking scheme, the older lanes, not mapped (%s)" % pk)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Crossings and reach")
            Xa = {c['n']: c for c in S1.get('X') or []}
            Xr = {c['n']: c for c in MR.crossings(mv, W)}
            ck(sorted(Xa) == sorted(Xr) and all(Xa[n]['lts'] == Xr[n]['lts'] and Xa[n]['ctl'] == Xr[n]['ctl'] and sorted(Xa[n]['minors']) == Xr[n]['minors'] for n in Xr),
               "every junction where a calm street meets a main one, as the reference finds it: its level and control (%d)" % len(Xr))
            at = {(X[n], Z[n]): c for n, c in Xa.items()}
            ck(at.get((-60.0, -400.0), {}).get('ctl') is True and at.get((180.0, -400.0), {}).get('ctl') is True and at.get((420.0, -400.0), {}).get('ctl') is False and at.get((420.0, -400.0), {}).get('lts') == 4,
               "North Boulevard (40 mph, 4 lanes): a signal and an all-way stop control their crossings; a stop on the approach only does not, LTS 4")
            ck(at.get((180.0, 0.0), {}).get('lts') == 2 and at.get((180.0, 0.0), {}).get('ctl') is False, "Market Street (30 mph, 4 lanes): an uncontrolled crossing at LTS 2, no bar to the reach")
            R1 = await safe("()=>window.__a3dMvReach()") or {}
            okA = set()
            for wi, ks in (R1.get('ok') or {}).items():
                for k in ks:
                    okA.add((int(wi), int(k)))
            okR, Da, Dl = MR.reach(mv, W, list(Xr.values()), LOT)
            dd = max([abs((a if a is not None else math.inf) - b) if b < math.inf else (0 if a is None else 99) for a, b in zip(R1.get('Da') or [], Da)] or [99])
            ck(okA == okR and dd <= 0.01, "the low-stress reach as two Dijkstras find it: %d pieces of %d (%s; distances within %.3f m)" % (len(okR), sum(len(r) - 2 for r in Wr), okA ^ okR and list(okA ^ okR)[:4], dd))
            def at_node(name, x, z):
                n0 = idx.get((float(x), float(z)))
                return [(i, k) for i, rec in enumerate(Wr) if T[rec[0]].get('name') == name for k in range(2, len(rec)) if n0 in (rec[k - 1], rec[k])]
            sig_p, stop_p, bar_p = at_node('Avenue 15', -60, -400), at_node('Avenue 17', 180, -400), at_node('Avenue 19', 420, -400)
            ck(len(sig_p) == 2 and all(p in okR for p in sig_p) and len(bar_p) == 2 and not [p for p in bar_p if p in okR],
               "across North Boulevard at its signal, at low stress; at Avenue 19, where only a stop sign faces the avenue, its pieces at the crossing barred (%s, %s)" % (sig_p, bar_p))
            ck(len(stop_p) == 2 and all(p in okR for p in stop_p), "and at Avenue 17, where an all-way stop controls it (%s)" % stop_p)

            # ---------------------------------------------------------------------------------
            print("\n-- 5. PTAL")
            Pa = await safe("()=>window.__a3dMvPtal()") or {}
            Pr = MR.ptal(ACC.get('stops', []), iv)
            ck(abs(Pa.get('ai', -1) - round(Pr['ai'], 2)) <= 0.011 and Pa.get('band') == Pr['band'] and Pa.get('have') == Pr['have'] and Pa.get('floor') is True and len(Pa.get('lines', [])) == len(Pr['lines']),
               "the index by TfL's method: %s from %d of %d lines, a floor (T1's headway not mapped) (%s, %s)" % (Pr['band'], Pr['have'], len(Pr['lines']), Pa.get('ai'), round(Pr['ai'], 2)))
            bus12 = [b for b in Pa.get('lines', []) if b['m'] == 'bus' and b['l'] == '12']
            ck(bus12 and abs(bus12[0]['edf'] - 30 / (bus12[0]['t'] + 5 + 2)) < 1e-6 and abs(bus12[0]['tat'] - (bus12[0]['t'] + 7)) < 1e-6,
               "bus 12: its walk, half its 10-minute headway and 2 minutes for a bus make its access time; 30 over it its doorstep frequency")
            ck(not [b for b in Pa.get('lines', []) if b['m'] == 'bus' and b['t'] > 8] and not [b for b in Pa.get('lines', []) if b['m'] != 'bus' and b['t'] > 12],
               "a bus counts within 8 minutes, rail, metro and tram within 12")
            bd = await safe("(L)=>L.map(function(v){return window.__a3dMvPtalBand(v);})", [0, 0.01, 2.5, 2.51, 5, 5.01, 10, 15, 20, 25, 25.01, 40, 40.01]) or []
            ck(bd == ['0', '1a', '1a', '1b', '1b', '2', '2', '3', '4', '5', '6a', '6a', '6b'], "the bands: 0, 1a to 2.5, 1b to 5, 2 to 10, ... 6a to 40, 6b over it (%s)" % bd)
            pt = await el('transit', 'ptal')
            ck(pt and pt['dg']['lb'] and pt['dg']['lb'][0]['t'] == 'PTAL at least %s (index %s)' % (Pr['band'], ('%.1f' % Pr['ai'])), "the site says it: PTAL at least %s (%s)" % (Pr['band'], pt and pt['dg']['lb'][0]['t']))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. The layers")
            L0 = {l['name']: l for l in await safe("()=>window.__a3dLayers()") or []}
            names = ['Street hierarchy', 'Cycling stress', 'Transit', 'Walk times', 'Daily needs', 'Vehicle access']
            ck(all(('Site analysis - ' + n) in L0 for n in names), "six layers under Site analysis")
            ck([L0['Site analysis - ' + n]['visible'] for n in names] == [True, False, True, False, True, True], "cycling stress and walk times off at first: they colour the streets the hierarchy does")
            # the hierarchy
            G = {}
            for rec in Wr:
                t = T[rec[0]]
                k = klass(t.get('highway'))
                if k:
                    G.setdefault(k + '|' + str(t.get('name') or t.get('ref') or '')[:60], []).append(rec)
            light = (await safe("()=>window.__a3dMapSettings().style")) in ('street', 'custom')
            PAL, LTSC = (LIGHT, LTS_LT) if light else (DARK, LTS_DK)
            SE = {o['dg']['k']: o for o in await diags('streets')}
            ck(sorted(SE) == sorted('street:' + k for k in G), "a street element for each street and class, the unnamed of a class one (%d)" % len(G))
            badS = [k for k, o in SE.items() if o['dg']['s']['stroke'] != PAL[k.split(':')[1].split('|')[0]] or
                    abs(o['dg']['s']['w'] - WEIGHT[k.split(':')[1].split('|')[0]] - (1.5 if k in ('street:ar|Market Street', 'street:co|5th Street') else 0)) > 1e-6]
            ck(light and not badS, "the address found puts the street map on: each in its class's colour for a light map, the heavier the higher the class, the frontage heavier still (%s)" % [(k, SE[k]['dg']['s']) for k in badS[:3]])
            ms = SE.get('street:ar|Market Street')
            ck(ms and ms['dg']['lb'] and ms['dg']['lb'][0]['t'] == 'Frontage: Market Street, arterial, 30 mph', "the frontage named: Market Street, arterial, 30 mph")
            ck(sorted(sum(len(L) for L in o['dg']['g']['lines']) for o in [ms]) == [sum(len(r) - 1 for r in G['ar|Market Street'])], "its line every kept node")
            nb = SE.get('street:co|North Boulevard')
            ck(nb and nb['dg']['lb'] and nb['dg']['lb'][0]['t'] == 'North Boulevard \u00b7 40 mph' and rows(nb).get('Speed limit') == '40 mph',
               "a main street labelled with its speed; Properties says its class, limit, lanes")
            lg = {b['title']: b for b in (await safe("()=>window.__a3dDgLegend()") or {}).get('blocks', [])}
            ck(lg.get('Street hierarchy', {}).get('rows') == ['motorway', 'arterial', 'collector', 'local', 'service', 'path'], "the key: the classes in order (%s)" % lg.get('Street hierarchy', {}).get('rows'))
            await safe("()=>window.__a3dMapSet('style','off')")
            await safe("()=>window.__a3dDgRun('streets')")
            ms2 = await el('streets', 'street:ar|Market Street')
            ck(ms2 and ms2['dg']['s']['stroke'] == DARK['ar'], "with the map off, on the dark plan, the ramp turns: the higher class the brighter (%s)" % (ms2 and ms2['dg']['s']['stroke']))
            await safe("()=>window.__a3dMapSet('style','street')")
            await safe("()=>window.__a3dDgRun('streets')")
            # cycling
            CE = {o['dg']['k']: o for o in await diags('cycling')}
            grp = {}
            for i, rec in enumerate(Wr):
                if W[i] >= 1:
                    t = T[rec[0]]
                    nm = str(t.get('name') or t.get('ref') or '')[:60]
                    grp.setdefault((W[i], nm or 'u:' + (klass(t.get('highway')) or 'lo')), 0)
            ck(len([k for k in CE if k.startswith('lts:')]) >= len(grp) and all(o['dg']['s']['stroke'] == LTSC[int(k.split(':')[1].split('|')[0])] for k, o in CE.items() if k.startswith('lts:')),
               "a cycling element for each street and level, in its level's colour (%d for %d; %s)" % (len([k for k in CE if k.startswith('lts:')]), len(grp), [(k, o['dg']['s']['stroke']) for k, o in CE.items() if k.startswith('lts:') and o['dg']['s']['stroke'] != LTSC[int(k.split(':')[1].split('|')[0])]][:3]))
            reach = CE.get('reach')
            rp = 0
            if reach:
                rp = sum(len(L) - 1 for L in reach['dg']['g']['lines'])
            ck(reach and rp == len(okR) and reach['dg']['s']['w'] == 11 and reach['dg']['s']['op'] == 0.22, "the reach: a wide pale band under them, piece for piece (%d of %d)" % (rp, len(okR)))
            cr = CE.get('crossings')
            stress_x = sorted([c for c in Xr.values() if c['pen']], key=lambda c: Lr.dist(X[c['n']], Z[c['n']]))
            ck(cr and [[m['p'][0], m['p'][2]] for m in cr['dg']['g']['marks']] == [[X[c['n']], Z[c['n']]] for c in stress_x] and
               [bool(m['t']) for m in cr['dg']['g']['marks']] == [i < 3 for i in range(len(stress_x))],
               "the stressful crossings marked, nearest first, the three nearest named (%d)" % len(stress_x))
            sl = CE.get('site')
            okL = sum(math.hypot(X[Wr[w][k]] - X[Wr[w][k - 1]], Z[Wr[w][k]] - Z[Wr[w][k - 1]]) for w, k in okR)
            allL = sum(math.hypot(X[r[k]] - X[r[k - 1]], Z[r[k]] - Z[r[k - 1]]) for i, r in enumerate(Wr) if W[i] >= 1 for k in range(2, len(r)))

            def km(m):
                return '%d m' % round(m) if m < 1000 else ('%.1f km' % (m / 1000))
            ck(sl and sl['dg']['lb'][0]['t'] == 'Low-stress reach: %s of %s' % (km(okL), km(allL)), "the site says the reach: %s of %s (%s)" % (km(okL), km(allL), sl and sl['dg']['lb'][0]['t']))
            s1o = [o for k, o in CE.items() if k.startswith('lts:2|S1 Street')]
            ck(s1o and 'a bike lane beside parking' in rows(s1o[0]).get('Why', '') and rows(s1o[0]).get('Parking') == 'parking on both sides', "S1 Street: why LTS 2, its parking (%s)" % (s1o and rows(s1o[0])))
            # transit
            TE = {o['dg']['k']: o for o in await diags('transit')}
            want_stops = [s['n'] for s in ACC['stops'] if s['t'] <= (12 if [m for m in s['m'] if m in ('metro', 'rail', 'light', 'tram')] else 8)]
            ck(sorted(k[5:] for k in TE if k.startswith('stop:')) == sorted(want_stops), "the stops within reach: a bus within 8 minutes, rail and tram within 12 (%s)" % want_stops)
            s0 = TE.get('stop:Market St & 5th St')
            rail_s = [o for k, o in TE.items() if k.startswith('stop:') and [s for s in ACC['stops'] if s['n'] == k[5:] and [m for m in s['m'] if m in ('metro', 'rail', 'light', 'tram')]]]
            ck(rail_s and all(o['dg']['sym']['col'] == ('#2a78d6' if light else '#3987e5') for o in rail_s), "a station or tram stop in blue (%s)" % [(o['name'], o['dg']['sym']['col']) for o in rail_s])
            ck(s0 and s0['dg']['lb'][0]['t'].startswith('Market St & 5th St, ') and s0['dg']['lb'][0]['t'].endswith(': 12, 42') and s0['dg']['sym']['col'] == ('#eb6834' if light else '#d95926'), "a stop: its name, its walk, its lines; a bus stop orange (%s, %s)" % (s0 and s0['dg']['lb'][0]['t'], s0 and s0['dg']['sym']['col']))

            def band_ok(o, t0, t1):
                segs = ACC['segs']
                pieces = []
                for g in segs:
                    for i in range(4, len(g) - 2, 3):
                        pieces.append((g[i - 3], g[i - 2], g[i - 1], g[i], g[i + 1], g[i + 2]))
                pts = o['dg']['g']['pts']
                bad = 0
                for j in range(0, len(pts) - 1, 2):
                    mx, mz = (pts[j][0] + pts[j + 1][0]) / 2, (pts[j][2] + pts[j + 1][2]) / 2
                    tm = None
                    for x1, z1, a, x2, z2, b in pieces:
                        L2 = (x2 - x1) ** 2 + (z2 - z1) ** 2
                        if L2 < 1e-9:
                            continue
                        u = ((mx - x1) * (x2 - x1) + (mz - z1) * (z2 - z1)) / L2
                        if -1e-6 <= u <= 1 + 1e-6 and math.hypot(x1 + u * (x2 - x1) - mx, z1 + u * (z2 - z1) - mz) < 0.01:
                            tm = a + u * (b - a)
                            break
                    if tm is None or tm < t0 - 1e-6 or tm > t1 + 1e-6:
                        bad += 1
                        continue
                    # and its ends: a piece crossing a band's edge is cut there
                    for q in (pts[j], pts[j + 1]):
                        uq = ((q[0] - x1) * (x2 - x1) + (q[2] - z1) * (z2 - z1)) / L2
                        tq = a + uq * (b - a)
                        if tq < t0 - 1e-3 or tq > t1 + 1e-3:
                            bad += 1
                            break
                return bad, len(pts) // 2
            b8 = band_ok(TE['catch8'], 0, 8) if 'catch8' in TE else (1, 0)
            b12 = band_ok(TE['catch12'], 8, 12) if 'catch12' in TE else (1, 0)
            ck(b8[0] == 0 and b12[0] == 0 and b8[1] > 50 and b12[1] > 50, "the catchment along the streets: every piece within 8 minutes, or 8 to 12 (%s, %s)" % (b8, b12))
            r1 = TE.get('routes1')
            ck(r1 and sum(len(L) for L in r1['dg']['g']['lines']) == sum(len(Wr[i]) - 1 for i in ms_w + st5) and sorted(k for k in TE if k.startswith('routes')) == ['routes1'],
               "the bus routes along their streets: Market Street and 5th Street, one line each, so none in the heavier bands (%s)" % sorted(k for k in TE if k.startswith('routes')))
            ck(TE.get('way:bus') and TE.get('way:rail') and P2(TE['way:rail'])[0] == [mv['paths'][-1]['pts'][0], mv['paths'][-1]['pts'][1]], "the way to the nearest stop and station, from the lot")
            # walk times
            WE = {o['dg']['k']: o for o in await diags('walk')}
            bw = [band_ok(WE[k], t0, t1) for k, t0, t1 in (('w5', 0, 5), ('w10', 5, 10), ('w15', 10, 15)) if k in WE]
            ck(len(bw) == 3 and all(b[0] == 0 and b[1] > 10 for b in bw), "walk times: the streets reached in 5, 10 and 15 minutes, every piece in its band (%s)" % bw)
            # daily needs
            NE = {o['dg']['k']: o for o in await diags('needs')}
            kinds = [p for p in ACC['places'] if p['near']]
            pathk = {p['k']: p for p in mv['paths']}
            badn = []
            for p in kinds:
                o = NE.get('need:' + p['k'])
                q0 = p['near'][0]
                if not o or P2(o) != [[pathk[p['k']]['pts'][i], pathk[p['k']]['pts'][i + 1]] for i in range(0, len(pathk[p['k']]['pts']), 2)] or \
                        [o['dg']['sym']['p'][0], o['dg']['sym']['p'][2]] != [q0['x'], q0['z']] or not o['dg']['lb'][0]['t'].endswith(': ' + ('under a minute' if q0['t'] < 0.5 else '%d min' % round(q0['t']))):
                    badn.append(p['k'])
            ck(len(NE) == len(kinds) and not badn, "daily needs: the way to the nearest of each kind, the place marked with its walk (%s)" % badn)
            fo = NE.get('need:food')
            ck(fo and 'within the 800 m they check to shops' in rows(fo).get('Design guides', ''), "and the design guides' 800 m to shops said (%s)" % (fo and rows(fo).get('Design guides')))
            # vehicles
            VE = {o['dg']['k']: o for o in await diags('vehicles')}
            ent = VE.get('entry:0')
            dwr = [i for i, rec in enumerate(Wr) if T[rec[0]].get('service') == 'driveway']
            ck(ent and ent['name'] == 'Vehicle entry' and P2(ent)[1] == [40, -10] and abs(math.hypot(P2(ent)[0][0] - 40, P2(ent)[0][1] + 10) - 10) < 0.01 and P2(ent)[0][1] > -10 and ent['dg']['s']['head'],
               "the driveway's entry: an arrow into the lot where it crosses the lot line, from 10 m back along it (%s)" % (ent and P2(ent)))
            ck(sorted(k for k in VE if k.startswith('entry:')) == ['entry:0'], "one entry: the driveway into the lot, not the alley 10 m behind it (%s)" % sorted(k for k in VE if k.startswith('entry:')))
            ck(VE.get('driveways') and len(VE['driveways']['dg']['g']['lines']) == len([i for i, rec in enumerate(Wr) if T[rec[0]].get('highway') == 'service' and min(Lr.dist(X[j], Z[j]) for j in rec[1:]) <= 40]) and dwr,
               "the driveways and service roads within 40 m of the lot")
            dr = VE.get('doors')
            ck(dr and sorted((m['p'][0], m['p'][2], m['t']) for m in dr['dg']['g']['marks']) == [(12.0, -38.0, 'Entrance (service)'), (30.0, -10.0, 'Entrance (main) Main door')], "the doors marked and named")
            c1 = [o for k, o in VE.items() if k.startswith('carpark:') and 'Lot P1' in o['name']]
            ck(c1 and c1[0]['dg']['lb'][0]['t'] == 'Car park Lot P1: surface, 40 spaces, %s' % ('under a minute' if p1['t'] < 0.5 else '%d min' % round(p1['t'])) and
               c1[0]['dg']['g']['bands'][0]['rings'][0] and c1[0]['dg']['s']['fill'] == '#7d8a9c', "a car park: its outline filled, its kind, spaces and walk (%s)" % (c1 and c1[0]['dg']['lb'][0]['t']))
            c2 = [o for k, o in VE.items() if k.startswith('carpark:') and 'Deck P2' in o['name']]
            ck(c2 and c2[0]['dg']['lb'][0]['t'].endswith('(customers)') and rows(c2[0]).get('Spaces') == 'not mapped', "a car park for customers says so; spaces not mapped")
            onst = VE.get('onstreet')
            ns_ = [L for L in (onst['dg']['g']['lines'] if onst else []) if abs(L[0][0] - L[-1][0]) < 1e-6]   # north-south lines
            ew_ = [L for L in (onst['dg']['g']['lines'] if onst else []) if abs(L[0][2] - L[-1][2]) < 1e-6]   # east-west lines
            xs5 = sorted(set(round(L[0][0], 1) for L in ns_ if 50 < L[0][0] < 75))
            zs1 = sorted(set(round(L[0][2], 1) for L in ew_ if 90 < L[0][2] < 110))
            ck(onst and xs5 == [64.5] and zs1 == [95.5, 104.5], "parking along the streets: 5th Street's left side only, 4.5 m off it; S1 Street both sides (%s, %s)" % (xs5, zs1))
            # the pixels: Market Street in the arterial's colour; the cycling colours when shown
            await safe("()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name==='Site analysis - Street hierarchy');});}")
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:400,tz:0,dist:500});}")
            await page.wait_for_timeout(500)
            near = "(a)=>{var s=window.__a3dDgToScreen(a[0]),c=document.getElementById('a3d-canvas'),r=window.devicePixelRatio||1,d=c.getContext('2d').getImageData(Math.round(s[0]*r)-2,Math.round(s[1]*r)-2,5,5).data,n=0,i;for(i=0;i<d.length;i+=4)if(d[i+3]>100&&Math.abs(d[i]-a[1][0])+Math.abs(d[i+1]-a[1][1])+Math.abs(d[i+2]-a[1][2])<60)n++;return n;}"

            def rgb(h):
                return [int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]
            n1 = await safe(near, [[470, 0.06, 0], rgb(PAL['ar'])])
            n2 = await safe(near, [[470, 0.06, 100], rgb(PAL['lo'])])
            ck((n1 or 0) >= 5 and (n2 or 0) >= 5, "on the plan: Market Street in the arterial's colour, S1 Street in the local's (%s, %s)" % (n1, n2))
            await safe("()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name==='Site analysis - Cycling stress');});}")
            await page.wait_for_timeout(400)
            n3 = await safe(near, [[470, 0.07, 100], rgb(LTSC[2])])
            n4 = await safe(near, [[470, 0.07, 0], rgb(LTSC[3])])
            ck((n3 or 0) >= 5 and (n4 or 0) >= 5, "cycling shown: S1 Street easygoing (LTS 2), Market Street tense (LTS 3) (%s, %s)" % (n3, n4))
            await safe("()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name!=='Site analysis - Cycling stress'&&l.name!=='Site analysis - Walk times'&&l.name!=='Site analysis - Slope'&&l.name!=='Site analysis - Aspect');});}")
            # a click picks a street, and Properties says why its level
            await safe("()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name==='Site analysis - Street hierarchy');});}")
            await page.wait_for_timeout(300)
            sp = await safe("()=>window.__a3dDgToScreen([470,0.06,100])")
            if sp:
                cb = await safe("()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top];}")
                await page.mouse.click(cb[0] + sp[0], cb[1] + sp[1])
                await page.wait_for_timeout(250)
            sel = await safe("()=>{var s=window.__a3dState(),o=s.objs.filter(function(x){return x.id===s.sel;})[0];return o?{a:o.dg&&o.dg.a,k:o.dg&&o.dg.k}:null;}")
            ck(sel and sel.get('a') == 'streets' and sel.get('k') == 'street:lo|S1 Street', "a click on S1 Street picks it (%s)" % sel)
            await safe("()=>{var L=window.__a3dLayers();L.forEach(function(l){if(/^Site analysis - /.test(l.name))window.__a3dLayerSet(l.id,'visible',l.name!=='Site analysis - Cycling stress'&&l.name!=='Site analysis - Walk times'&&l.name!=='Site analysis - Slope'&&l.name!=='Site analysis - Aspect');});}")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Findings and rows")
            F = {f['auto']: f for f in (await safe("()=>window.__a3dSa()") or {}).get('findings', []) if f.get('auto')}
            tr = F.get('access.transit', {}).get('value', '')
            ck(('PTAL at least %s by TfL\'s method' % Pr['band']) in tr and ('from the %d of %d lines whose headway OpenStreetMap maps' % (Pr['have'], len(Pr['lines']))) in tr, "Transit says PTAL now, and its floor (%s)" % tr[-160:])
            cy = F.get('access.cycling', {})
            ck('The lot fronts Market Street LTS 3 (tense), 5th Street LTS 2 (easygoing)' in cy.get('value', '') and ('%s of the %s' % (km(okL), km(allL))) in cy.get('value', ''),
               "Cycling: the frontage streets' levels and the reach (%s)" % cy.get('value', '')[:200])
            vh = F.get('access.vehicles', {})
            ck(vh.get('value', '').startswith('1 driveway or service road into the lot; 2 car parks within 400 m (40 spaces mapped in 1); 1 garage entrance within 400 m') and '5th Street: left: parking; right: none' in vh.get('value', ''),
               "Vehicle access: the driveway, the car parks and their spaces, the garage, the frontage's parking (%s)" % vh.get('value', '')[:240])
            grp = await safe("()=>['dgstreets','dgcycling','dgtransit','dgwalk','dgneeds','dgvehicles'].map(function(i){var r=document.querySelector('[data-anzcard=\"'+i+'\"]'),c=r&&r.closest('[data-sacat]');return c?c.getAttribute('data-sacat'):null;})")
            ck(grp == ['access', 'access', 'access', 'access', 'people', 'access'], "the rows in Access and circulation, daily needs in People and place (%s)" % grp)
            s1 = await safe("(q)=>window.__a3dAnzSearch(q)", 'cycling')
            ck(s1 and 'dgcycling' in s1, "a search for cycling finds its row")
            reg = await safe("()=>JSON.stringify(window.__wsRegistry.filter(function(c){return c.name==='ANALYZESITE';}))") or ''
            ck('street hierarchy, cycling stress, transit, walk times, daily needs, vehicle access' in reg, "ANALYZESITE says the movement analyses")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Elsewhere")
            ST2 = {'mv': ('nodrive',)}
            c2x, p2, e2 = await fresh(ST2)
            await analyze(pg=p2)
            en2 = [o for o in await diags('vehicles', pg=p2) if o['dg']['k'] == 'entry:0']
            ck(en2 and en2[0]['name'] == 'Vehicle entry, provisional' and en2[0]['dg']['lb'][0]['t'] == 'Entry, provisional: from the alley' and en2[0]['dg']['s']['dash'],
               "no driveway into the lot: a provisional entry, dashed, from its lowest street, the alley behind (%s)" % (en2 and en2[0]['dg']['lb'][0]['t']))
            ep = P2(en2[0]) if en2 else [[0, 0], [0, 0]]
            ck(abs(ep[1][1] + 40) < 1e-6 and 10 <= ep[1][0] <= 50 and abs(ep[0][1] + 50) < 1e-6, "on the lot's line along the alley, pointing in from it (%s)" % ep)
            F2 = {f['auto']: f for f in (await safe("()=>window.__a3dSa()", pg=p2) or {}).get('findings', []) if f.get('auto')}
            ck(F2.get('access.vehicles', {}).get('value', '').startswith('No driveway mapped into the lot: an entry from the alley, its lowest street, is marked provisional'), "the finding says so (%s)" % F2.get('access.vehicles', {}).get('value', '')[:120])
            await c2x.close()
            ST3 = {'mv': ('dense', 'alliv')}
            c3, p3, e3 = await fresh(ST3)
            await analyze(pg=p3)
            mv3 = await safe("()=>window.__a3dMvGet()", pg=p3) or {}
            ck(mv3.get('cut') and 650 <= mv3['cut'] <= 760 and mv3['n']['dropped'] >= 1 and len(mv3['x']) <= 6000 and not [t for t in mv3['t'] if t.get('name') == 'Maze Walk' and
                                                                                                                       any(mv3['t'][r[0]].get('name') == 'Maze Walk' for r in mv3['w'])],
               "past 6,000 nodes the farthest ways go, and the window kept is said (cut at %s m, %s dropped, %d nodes)" % (mv3.get('cut'), (mv3.get('n') or {}).get('dropped'), len(mv3.get('x') or [])))
            ns = [o for o in await diags('streets', pg=p3) if o['dg']['k'] == 'street:ar|Market Street']

            def line_gap(r):   # how near the lot a kept way's line comes, along its pieces
                P = [(mv3['x'][i], mv3['z'][i]) for i in r[1:]]
                best = math.inf
                for (x1, z1), (x2, z2) in zip(P, P[1:]):
                    n = max(1, int(math.hypot(x2 - x1, z2 - z1) // 2) + 1)
                    best = min([best] + [Lr.dist(x1 + j / n * (x2 - x1), z1 + j / n * (z2 - z1)) for j in range(n + 1)])
                return best
            beyond = [r for r in mv3.get('w', []) if line_gap(r) > (mv3.get('cut') or 0) + 1.5]
            ck(ns and mv3.get('cut') and not beyond, "the nearest go last: the frontage street still drawn, no way kept that lies beyond the cut (%d)" % len(beyond))
            P3 = await safe("()=>window.__a3dMvPtal()", pg=p3) or {}
            ck(P3.get('floor') is False and P3.get('have') == len(P3.get('lines', [])), "every line's headway mapped (T1 every 8): PTAL in full, not a floor")
            pt3 = [o for o in await diags('transit', pg=p3) if o['dg']['k'] == 'ptal']
            ck(pt3 and pt3[0]['dg']['lb'][0]['t'].startswith('PTAL ' + P3.get('band', '?') + ' (index'), "the site says PTAL %s" % P3.get('band'))
            await c3.close()
            ST4 = {'mv': ('noiv',)}
            c4, p4, e4 = await fresh(ST4)
            await analyze(pg=p4)
            pt4 = [o for o in await diags('transit', pg=p4) if o['dg']['k'] == 'ptal']
            F4 = {f['auto']: f for f in (await safe("()=>window.__a3dSa()", pg=p4) or {}).get('findings', []) if f.get('auto')}
            ck(pt4 and pt4[0]['dg']['lb'][0]['t'] == 'No PTAL: how often the lines run is not mapped' and 'is not mapped in OpenStreetMap, so no PTAL' in F4.get('access.transit', {}).get('value', ''),
               "no headway mapped: no PTAL, and why")
            # a project from before V166: the access data without its movement part
            await safe("()=>window.__a3dMvSet(null)", pg=p4)
            r4 = await safe("()=>window.__a3dDgRun('streets')", pg=p4) or {}
            ck('from before V166' in (r4.get('streets') or {}).get('note', '') and not await diags('streets', pg=p4), "access data from before V166: the movement layers say to Analyze site again")
            await safe("()=>window.__a3dSaFill()", pg=p4)
            F4b = {f['auto']: f for f in (await safe("()=>window.__a3dSa()", pg=p4) or {}).get('findings', []) if f.get('auto')}
            ck('needs the operator\'s timetable (GTFS)' in F4b.get('access.transit', {}).get('value', '') and 'access.cycling' not in F4b, "and the findings say what V161 said")
            await c4.close()
            ST5 = {'mode': {'acc': 'abort'}}
            c5, p5, e5 = await fresh(ST5)
            fin5 = await analyze(pg=p5)
            D5 = (await safe("()=>window.__a3dDgState()", pg=p5) or {}).get('runs', {})
            ck({s['id']: s['state'] for s in fin5.get('steps', [])}.get('access') in ('fail', 'part') and 'Not fetched yet' in (D5.get('streets') or {}).get('note', '') and
               'Not fetched yet' in (D5.get('transit') or {}).get('note', ''), "Overpass down: the access step fails, and the movement layers say they were not fetched")
            ck(not e5, "no page error")
            await c5.close()
            for vw, nm, mob in (((390, 844), 'phone', True), ((820, 1180), 'tablet', True)):
                c6, p6, e6 = await fresh({}, vw=vw, mobile=mob)
                await analyze(pg=p6)
                await safe("()=>window.__a3dAnzView(true)", pg=p6)
                await p6.wait_for_timeout(300)
                g6 = await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap'),R=['dgstreets','dgcycling','dgtransit','dgwalk','dgneeds','dgvehicles'].map(function(i){return document.querySelector('[data-anzcard="'+i+'"]');});
                  return {rows:R.filter(Boolean).length,sw:w.scrollWidth,cw:w.clientWidth,doc:document.documentElement.scrollWidth};}""", pg=p6) or {}
                ck(g6.get('rows') == 6 and g6.get('sw', 9) <= g6.get('cw', 0) + 1 and g6.get('doc', 9999) <= vw[0] + 1, "on a %s: the six rows in Analyze, nothing spilling (%s)" % (nm, g6))
                ck(not e6, "no page error on a %s" % nm)
                await c6.close()
            ck(not errs, "no page error (%s)" % errs[:3])
        except Stalled as e:
            ck(False, 'the harness stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
        await browser.close()
    print('\n%d/%d checks passed' % (CK.n - len(CK.bad), CK.n))
    print('RESULT: ' + ('PASS' if not CK.bad else 'FAIL'))
    return not CK.bad


if __name__ == '__main__':
    ok_ = asyncio.run(run())
    sys.exit(0 if ok_ else 1)
