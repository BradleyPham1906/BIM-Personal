#!/usr/bin/env python3
"""bim_phase167_standards_registry_browser_tests.py -- V167: the standards registry.

Every standard, guideline and assumption an analysis applies is a record: a topic, its editions, where
and when each is in force, its source and the level it was read at, its values. tests/standards_reference.py
holds them again as their sources state them, the constants the analyses had before V167 (read from the
kept build), and the rules for the edition in force, so the app is asked and compared.

  1. THE RECORDS: every topic, edition, adoption, source level and value against the reference; the move
     kept every value the analyses had; FHWA's ranges give the old traffic; nothing unverified applied.
  2. READING NEVER WRITES: every value read and the Standards group drawn, the project unchanged.
  3. IN FORCE: the edition and how, for ten places and nine dates, against the reference's rules; the
     edges (London's boroughs, England and Wales, Pennsylvania on 31 December 2025 and 1 January 2026);
     an edition chosen; the date.
  4. THE PLACE: from Nominatim's address parts, from Find (one undo step with the site), by hand, cleared;
     the site moved since.
  5. OVERRIDES: a reason, a number, more than zero, in order, not a table, not the catalogue; the reader,
     the words, cleared, undone.
  6. THE WORDS FOLLOW: PTAL's walks in the transit layer's names, legend and method; the compass rings'
     minutes; LEED's prerequisite and the slope classes in the findings; the frame's combinations.
  7. OUT OF DATE: a row whose standards changed since it ran, and why; run again; the data fetched with
     other values (the access data, the site context, the climate) said to need Analyze site; runs from
     before V167.
  8. FINDINGS: each names its standards, an edition applied outside its place and an override said; the
     climate's findings state the values the data was worked out with, until Analyze site fetches again.
  9. PACKS: what a pack changes before it applies, its SHA-256 (Python's), its publisher, unsigned; Apply,
     the edition in force changed; refused packs; Remove; undo.
 10. THE GROUP: Properties > Site > Standards: the place set by hand, the date, the topics by area, values,
     Override, Save, Reset, an edition chosen, the codes in force in Pennsylvania, a pack looked at and
     applied; STANDARDS and its aliases.
 11. KEPT: a reload keeps the place, the date, the overrides and the packs.
 12. A PHONE, A TABLET, A DESKTOP: the group inside the panel, its buttons finger-sized on touch.

The harness never waits without a bound (V123).
"""
import asyncio, hashlib, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import movement_fixture as FX       # noqa: E402
import access_fixture as AFX        # noqa: E402
import standards_reference as R     # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
LOT = [list(p) for p in AFX.LOT]
HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
TODAY = '2026-10-18'


def near(a, b, tol=1e-9):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(near(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return sorted(a) == sorted(b) and all(near(a[k], b[k], tol) for k in a)
    return a == b


def pack(eds_walk=None, extra=None, **kw):
    """a standards pack's text: a slower walk for Pennsylvania from 2026, and a catalogue topic"""
    P = {'format': 'bim-standards-pack', 'version': 1, 'publisher': 'Example Planning Office', 'name': 'Example walking standard', 'date': '2026-09-01',
         'topics': [{'id': 'walk.speed', 'eds': eds_walk if eds_walk is not None else [
             {'id': 'walk.speed.pa2026', 'name': 'A slower walk for Pennsylvania (2026) \u2013 an example', 'pub': '2026-01-01', 'adopt': [{'at': 'us-pa', 'from': '2026-01-01'}],
              'src': {'t': 'Example Planning Office', 'w': 'section 1', 'u': 'https://example.org/walk', 'lv': 'P', 'read': '2026-09-01'},
              'v': [{'n': 'm_min', 'v': 70, 'u': 'm/min', 'say': 'the walking speed'}]}]},
             {'id': 'ex.parking', 'title': 'Example parking code', 'kind': 'code', 'area': 'Parking', 'eds': [
                 {'id': 'ex.parking.1', 'name': 'Example parking code, first edition', 'pub': '2025', 'adopt': [{'at': 'us-pa', 'from': '2025-01-01'}],
                  'src': {'t': 'Example Planning Office', 'lv': 'S'}, 'v': []}]}] + (extra or [])}
    P.update(kw)
    return json.dumps(P, ensure_ascii=False, indent=1)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        def handler(store):
            base = FX.route_handler(store)

            async def h(route):
                u = route.request.url
                if 'nominatim.openstreetmap.org' in u:
                    store.setdefault('nom', []).append(u)
                    a = store.get('addr', R.NOM_PHILADELPHIA)
                    lat, lon = store.get('at', (AFX.LAT0, AFX.LON0))
                    hit = {'lat': str(lat), 'lon': str(lon), 'display_name': store.get('name', '1 Market Street, Philadelphia, Pennsylvania, United States')}
                    if a is not None:
                        hit['address'] = a
                    await route.fulfill(status=200, body=json.dumps([hit]), headers=HDR)
                    return
                await base(route)
            return h

        async def fresh(store, vw=(1440, 900), mobile=False, lot=True):
            c = await browser.new_context(viewport={'width': vw[0], 'height': vw[1]}, has_touch=mobile, is_mobile=mobile)
            for hh in FX.HOSTS:
                await c.route(hh, handler(store))
            for hh in BLOCKERS:
                await c.route(hh, lambda r: r.abort())
            p = await c.new_page()
            e, w = [], []
            p.on('pageerror', lambda x: e.append(str(x)))
            p.on('console', lambda m: w.append(m.text) if m.type == 'warning' and '[BIM]' in m.text else None)
            await within(p.goto('file://' + str(HTML)), 'goto')
            await p.wait_for_timeout(1800)
            if lot:
                await p.evaluate("()=>window.__a3dEnter()")
                await p.evaluate("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
                  o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
                  window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT)
            return c, p, e, w

        ST = {}
        ctx, page, errs, warns = await fresh(ST, lot=False)

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

        async def wait_run(pg=None, bound=120):
            for _ in range(bound * 4):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await (pg or page).wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def analyze(pg):
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(150)
            if await safe("()=>!!document.querySelector('[data-saaddr]')", pg=pg):   # once placed, the site is analyzed where it is
                await pg.fill('[data-saaddr]', '1 Market Street')
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]').click()", pg=pg)
            return await wait_run(pg=pg)

        async def card(cid, pg=None):
            return await safe("""(k)=>{var c=document.querySelector('[data-anzcard="'+k+'"]');if(!c)return null;
              return {st:(c.querySelector('.a3d-anzst')||{textContent:''}).textContent,state:(c.querySelector('.a3d-anzstate')||{textContent:''}).textContent,
                std:(c.querySelector('[data-dgstd]')||{textContent:''}).textContent};}""", cid, pg=pg) or {}

        async def finding(auto, pg=None):
            return await safe("(a)=>{var f=window.__a3dSa().findings.filter(function(x){return x.auto===a;})[0];return f?f.value:null;}", auto, pg=pg)

        async def std_group(pg=None):
            return await safe("""()=>{var b=document.getElementById('a3d-propsbody'),g=b&&b.querySelector('[data-a3dpgrp="Standards"]'),body=g&&g.nextElementSibling;
              var tab=g&&g.closest('[data-ptab]');
              return g?{tab:tab?tab.getAttribute('data-ptab'):null,open:!!(body&&body.classList.contains('a3d-pgbody')),html:body?body.innerHTML:'',
                text:body?body.textContent:'',
                topics:body?[].map.call(body.querySelectorAll('[data-stdtopic]'),function(e){return e.getAttribute('data-stdtopic');}):[],
                cat:body?[].map.call(body.querySelectorAll('[data-stdcat]'),function(e){return e.getAttribute('data-stdcat');}):[],
                areas:body?[].map.call(body.querySelectorAll('.a3d-stdarea'),function(e){return e.textContent;}):[],
                prev:(function(){var L=[].filter.call(b.querySelectorAll('[data-a3dpgrp]'),function(e){var t=e.closest('[data-ptab]');return t&&t.getAttribute('data-ptab')==='site';})
                  .map(function(e){return e.getAttribute('data-a3dpgrp');}),i=L.indexOf('Standards');return i>0?L[i-1]:null;})()}:null;}""", pg=pg) or {}

        async def click(sel, pg=None):
            ok = await safe("(s)=>{var e=document.querySelector('#a3d-propsbody '+s);if(!e)return false;e.scrollIntoView({block:'center'});return true;}", sel, pg=pg)
            if not ok:
                return False
            await (pg or page).click('#a3d-propsbody ' + sel)
            await (pg or page).wait_for_timeout(120)
            return True

        async def fill(sel, val, pg=None):
            pg = pg or page
            await pg.fill('#a3d-propsbody ' + sel, val)
            await pg.wait_for_timeout(60)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV167") or ''
            ck(all(w_ in mk for w_ in ('registry', 'reader', 'overrides', 'packs', 'sha256', 'catalogue', 'standardsgroup', 'datastamps', 'framestd', 'refill')), "the V167 marker (%s)" % mk[:60])
            ver = (await safe("()=>window.__a3dVersion()") or {}).get('v', '')
            ck(re.match(r'^V\d+$', ver) and int(ver[1:]) >= 167, "the app says V167 or later (%s)" % ver)
            RECS = {r['id']: r for r in await safe("()=>window.__a3dStdRecords()") or []}
            ck(sorted(RECS) == sorted(R.TOPICS), "the topics are the reference's: %d (%s)" % (len(R.TOPICS), sorted(set(RECS) ^ set(R.TOPICS))))
            bad = []
            for tid, T in R.TOPICS.items():
                A = RECS.get(tid)
                if not A:
                    continue
                if A['kind'] != T['kind'] or A['cat'] != T['cat'] or A['anywhere'] != T['anywhere']:
                    bad.append((tid, 'kind', A['kind'], A['cat'], A['anywhere']))
                if [e['id'] for e in A['eds']] != [e['id'] for e in T['eds']]:
                    bad.append((tid, 'eds', [e['id'] for e in A['eds']]))
                    continue
                for ea, er in zip(A['eds'], T['eds']):
                    ad = [(a['at'], a.get('from'), a.get('to')) for a in ea['adopt']]
                    if ad != er['adopt']:
                        bad.append((er['id'], 'adopt', ad[:3]))
                    if ea['pub'] != er['pub'] or ea['st'] != er['st'] or ea['src'].get('lv') != er['lv']:
                        bad.append((er['id'], 'pub/st/lv', ea['pub'], ea['st'], ea['src'].get('lv')))
                    if er['v'] is not None:
                        got = {x['n']: x for x in ea['v']}
                        for n, ref in er['v'].items():
                            x = got.get(n)
                            if not x or not near(x['v'], ref[0], 1e-9) or (ref[1] and x.get('u') != ref[1]) or (len(ref) > 2 and x.get('lv', er['lv']) != ref[2]):
                                bad.append((er['id'], n, x and x['v'], ref))
                        if sorted(got) != sorted(er['v']) and tid not in ('who.aqg',):
                            bad.append((er['id'], 'names', sorted(set(got) ^ set(er['v']))))
            ck(not bad, "every topic's kind, every edition's place and dates, published, status, source level and values as the reference has them (%s)" % bad[:4])
            hosts = set()
            badu = []
            for A in RECS.values():
                for e in A['eds']:
                    u = e['src'].get('u') or ''
                    if u:
                        m = re.match(r'^https://([^/]+)/', u)
                        if not m:
                            badu.append(u)
                        else:
                            hosts.add(m.group(1))
                    if e['src'].get('lv') not in ('P', 'S', 'U', 'A') or not e['src'].get('t'):
                        badu.append(e['id'])
            ck(not badu and hosts == R.SOURCE_HOSTS, "every source names itself, its level, and links over https to its publisher (%s; %s)" % (badu[:3], sorted(hosts ^ R.SOURCE_HOSTS)))
            unv = [(A['id'], e['id']) for A in RECS.values() if not A['cat'] for e in A['eds'] if e['src'].get('lv') == 'U' or any(x.get('lv') == 'U' for x in e['v'])]
            ck(not unv, "nothing not yet verified is applied: the U records are catalogue entries without values (%s)" % unv)
            ck(all(not e['v'] for A in RECS.values() if A['cat'] and A['id'] != 'ada.2010' for e in A['eds']) and all(not A['anywhere'] for A in RECS.values() if A['cat']),
               "the catalogue holds editions, not values the app reads, and is never applied outside its place")
            # no standard's value left in code: the constants gone, no number beside its unit outside the registry
            left, said = R.scan(HTML.read_text(encoding='utf-8'))
            kl, ks = R.scan(R.KEPT.read_text(encoding='utf-8'))
            ck(not left and not said, "no constant V167 moved is left in the build, and no standard's number is written beside its unit outside the registry (%s; %s)" % (left, said))
            ck(len(kl) == len(R.MOVED) and len(ks) >= 12, "the same scan of the build before V167 finds them all: %d constants, %d kinds of phrase" % (len(kl), len(ks)))
            # the move: every value as the build before V167 had it
            K = R.kept()

            def v1(t, n, ed=0):
                return {x['n']: x['v'] for x in RECS[t]['eds'][ed]['v']}.get(n)
            ROADS = {x['n']: x['v'] for x in RECS['app.roads']['eds'][0]['v']}
            FC = v1('fhwa.fc', 'classes')
            moved = {
                'walking speed': (v1('walk.speed', 'm_min'), K['BIM_ACC_SPEED']),
                'LEED radius and thresholds': ([v1('leed.nd', 'radius')] + [v1('leed.nd', n) for n in ('case1', 'case2', 'pt1', 'pt2')], [K['BIM_ACC_IXR']] + [x[0] for x in K['BIM_ACC_LEED']]),
                'degree-day base, calm, bins': ([v1('app.climate', 'base'), v1('app.climate', 'calm')] + v1('app.climate', 'wind_bins'), [K['BIM_CLIM_BASE'], K['BIM_CLIM_CALM']] + K['BIM_CLIM_WIND_BINS'][1:]),
                'calm the first bin': (v1('app.climate', 'calm'), K['BIM_CLIM_WIND_BINS'][0]),
                'comfort band': ({k: v1('app.climate', 'comfort_' + k) for k in ('t0', 't1', 'rh0', 'rh1')}, K['BIM_CLIM_COMFORT']),
                'WHO levels': ([v1('who.aqg', 'pm25_24h'), v1('who.aqg', 'pm25_year'), v1('who.aqg', 'pm25_it1_year')], [K['BIM_CLIM_WHO24'], K['BIM_CLIM_WHO_YEAR'], K['WHO_IT1']]),
                'WHO 24-hour interim targets': ([v1('who.aqg', 'pm25_24h_it' + str(i)) for i in (4, 3, 2, 1)], K['WHO_IT24']),
                'CRTN range': (v1('crtn', 'range'), K['BIM_DG_CRTN_MAX']),
                "WHO's road noise": (v1('who.noise', 'road_lden'), K['WHO_NOISE']),
                'the crossing table': (v1('lts.xing2016', 'table'), K['BIM_MV_XTAB']),
                'design guides': ({'food': v1('guides.walk', 'shops'), 'learn': v1('guides.walk', 'school'), 'parks': v1('guides.walk', 'green')}, K['BIM_MV_GUIDE']),
                'PTAL walks': ({'bus': v1('tfl.ptal', 'walk_bus'), 'tram': v1('tfl.ptal', 'walk_tram'), 'metro': v1('tfl.ptal', 'walk_rail'), 'rail': v1('tfl.ptal', 'walk_rail'), 'light': v1('tfl.ptal', 'walk_rail')}, K['BIM_MV_PTAL_WALK']),
                'PTAL allowances': ({'bus': v1('tfl.ptal', 'k_bus'), 'tram': v1('tfl.ptal', 'k_rail'), 'metro': v1('tfl.ptal', 'k_rail'), 'rail': v1('tfl.ptal', 'k_rail'), 'light': v1('tfl.ptal', 'k_rail')}, K['BIM_MV_PTAL_K']),
                'PTAL bands': (v1('tfl.ptal', 'bands'), K['BIM_MV_PTAL']),
                'slope classes': ([v1('land.slope', 'b' + str(i)) for i in (1, 2, 3, 4)], [c[1] for c in K['BIM_LAND_SLOPE'][:4]]),
                'terrain bands': (v1('terrain.slope_bands', 'bands') + [None], K['BIM_SLOPE_BANDS']),
                'context sizes': ([v1('app.context', n) for n in ('storey', 'building', 'deck', 'deck_t', 'pier', 'tree', 'tower', 'line')],
                                  [K[n] for n in ('BIM_CTX_LEVEL_H', 'BIM_CTX_DEFAULT_H', 'BIM_CTX_DECK', 'BIM_CTX_DECK_T', 'BIM_CTX_PIER', 'BIM_CTX_TREE_H', 'BIM_CTX_TOWER_H', 'BIM_CTX_LINE_H')]),
                'road widths': (v1('app.context', 'road_w'), K['BIM_ROAD_W']),
                'occupant loads 2021': (v1('ibc.occupant_load', 'table', 0), K['BIM_OCC_LOADS']),
                'occupant loads 2018': (v1('ibc.occupant_load', 'table', 1), K['BIM_OCC_LOADS']),
                'combinations': ([v1('asce7.combos', 'c2_d'), v1('asce7.combos', 'c2_l'), v1('asce7.combos', 'c1_d')], [K['BIM_COMBOS'][0]['f']['D'], K['BIM_COMBOS'][0]['f']['L'], K['BIM_COMBOS'][1]['f']['D']]),
                'speeds where none is mapped': ([ROADS['service_v'], ROADS['track_v'], ROADS['other_v']], K['SPEED_ELSE']),
                'road classes': ({k: {'fc': FC[ROADS['classes'][k]]['name'], 'u': R.fc_mid(FC[ROADS['classes'][k]]['u']), 'r': R.fc_mid(FC[ROADS['classes'][k]]['r']),
                                      'v': ROADS[k + '_v'], 'p': ROADS[k + '_p'], 'l': ROADS[k + '_l']} for k in ROADS['classes']}, K['BIM_DG_ROADS']),
            }
            badm = [k for k, (a, b) in moved.items() if not near(a, b, 1e-9)]
            ck(not badm, "the move kept every value the analyses had: %d sets, among them FHWA's ranges giving the old traffic to the nearest 10 (%s)" %
               (len(moved), [(k, str(moved[k][0])[:60], str(moved[k][1])[:60]) for k in badm][:3]))
            ck(near(R.TFL_BUS_M / R.TFL_SPEED, 8) and near(R.TFL_RAIL_M / R.TFL_SPEED, 12) and near(R.TFL_SPEED, 80), "TfL's 640 m and 960 m at 4.8 km/h are 8 and 12 minutes, 80 m a minute")
            ck(R.OSM_FC == ROADS['classes'], "OpenStreetMap's classes read as FHWA's, as V164 had them")
            rc = await safe("(L)=>L.map(function(h){var c=window.__a3dDgRoadClass(h);return c&&[c.fc,c.u,c.r,c.v,c.p,c.l];})", list(K['BIM_DG_ROADS']) + ['primary_link']) or []
            want = [[d['fc'], d['u'], d['r'], d['v'], d['p'], d['l']] for d in K['BIM_DG_ROADS'].values()]
            pl = K['BIM_DG_ROADS']['primary']
            ck(rc[:-1] == want and rc[-1] == [pl['fc'] + ' (a slip road)', pl['u'] * 0.25, pl['r'] * 0.25, pl['v'], pl['p'], pl['l']], "and the noise analysis reads them as before, a slip road at a quarter (%s)" % rc[:2])
            ol = await safe("()=>window.__a3dOccLoads()") or []
            ck([[o['name'], o['ft2'], o['basis']] for o in ol] == K['BIM_OCC_LOADS'], "the occupant loads the rooms read: the table of the edition in force, 36 rows as before (%d)" % len(ol))
            cb = await safe("()=>window.__a3dCombos()") or []
            ck(cb == [c['name'] for c in K['BIM_COMBOS']], "the frame's combinations, named by their factors as before (%s)" % cb)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. Reading never writes")
            ck(await safe("()=>window.__a3dStdState()") is None, "a new project holds no standards of its own")
            got = await safe("""(T)=>{var n=0;window.__a3dStdRecords().forEach(function(r){if(r.cat)return;r.eds[0].v.forEach(function(x){window.__a3dStd(r.id,x.n);window.__a3dStdSay(r.id,x.n);n++;});
              window.__a3dStdEdition(r.id);window.__a3dStdUsed(r.id);window.__a3dStdStamp([r.id]);});return n;}""", None)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            await page.wait_for_timeout(150)
            gc = await std_group()
            ck(gc.get('tab') == 'site' and gc.get('open') is False, "on the Site tab the Standards group starts closed: it is long (%s)" % {k: gc.get(k) for k in ('tab', 'open')})
            await safe("()=>{window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            await safe("()=>window.__a3dStdCommand()")
            await page.wait_for_timeout(200)
            g0 = await std_group()
            on0 = await safe("()=>{var p=document.querySelector('#a3d-propsbody .a3d-ptabpane.on');return p&&p.getAttribute('data-ptab');}")
            ck(on0 == 'site', "STANDARDS from the Project tab turns Properties to Site (%s)" % on0)
            nv = sum(len(A['eds'][0]['v']) for A in RECS.values() if not A['cat'])
            ck(got == nv and nv > 70 and await safe("()=>window.__a3dStdState()") is None and g0.get('open'),
               "every value read (%s), every edition, stamp and sentence, and the Standards group drawn: the project still holds nothing (%s)" % (got, await safe("()=>window.__a3dStdState()")))
            ck(not [w_ for w_ in warns if 'standards registry has no' in w_], "no value the app reads is missing (%s)" % warns[:2])

            # ---------------------------------------------------------------------------------
            print("\n-- 3. In force, by place and date")
            badr, n_r = [], 0
            for nm, pl in R.PLACES:
                await safe("(p)=>window.__a3dStdSetPlace(p,'hand')", pl) if pl else await safe("()=>window.__a3dStdSetPlace(null)")
                for d in R.DATES:
                    await safe("(d)=>window.__a3dStdSetDate(d)", d)
                    app = await safe("(T)=>T.map(function(t){var e=window.__a3dStdEdition(t);return [e.id,e.how,e.atKey];})", list(R.TOPICS)) or []
                    for t, a in zip(R.TOPICS, app):
                        n_r += 1
                        ref = list(R.resolve(t, pl, d))
                        if a != ref:
                            badr.append((nm, d, t, a, ref))
            ck(n_r == len(R.PLACES) * len(R.DATES) * len(R.TOPICS) and not badr,
               "the edition in force and how, for %d places, %d dates and %d topics, as the reference's rules give them (%d asked; %s)" % (len(R.PLACES), len(R.DATES), len(R.TOPICS), n_r, badr[:3]))

            async def ed(t):
                return await safe("(t)=>window.__a3dStdEdition(t)", t) or {}
            await safe("()=>window.__a3dStdSetDate('')")
            await safe("(p)=>window.__a3dStdSetPlace(p,'hand')", {'cc': 'gb', 'r': 'gb-eng', 'd8': 'gb-wsm'})
            e1 = await ed('tfl.ptal')
            await safe("(p)=>window.__a3dStdSetPlace(p,'hand')", {'cc': 'gb', 'r': 'gb-eng', 'd8': 'gb-lds'})
            e2, e3 = await ed('tfl.ptal'), await ed('guides.walk')
            ck(e1.get('how') == 'adopted' and e1.get('atKey') == 'gb-wsm' and e2.get('how') == 'outside' and 'GB-LDS' not in e2.get('why', '') and e3.get('how') == 'adopted' and e3.get('atKey') == 'gb-eng',
               "PTAL is London's: in force in Westminster, applied outside its place in Leeds, where the English guides are in force (%s, %s, %s)" % (e1.get('how'), e2.get('how'), e3.get('atKey')))
            await safe("(p)=>window.__a3dStdSetPlace(p,'hand')", {'cc': 'us', 'r': 'us-pa', 'city': 'Philadelphia'})
            await safe("()=>window.__a3dStdSetDate('2025-12-31')")
            a1 = await ed('ibc.occupant_load')
            await safe("()=>window.__a3dStdSetDate('2026-01-01')")
            a2 = await ed('ibc.occupant_load')
            ck(a1.get('id') == 'ibc.2021.1004.5' and a1.get('how') == 'outside' and 'on 2025-12-31' in a1.get('why', '') and a2.get('how') == 'adopted' and a2.get('at') == 'US-PA',
               "the 2021 IBC in Pennsylvania: in force from 1 January 2026, applied outside its place the day before, saying so (%s %s; %s)" % (a1.get('how'), a1.get('why'), a2.get('how')))
            u1 = await safe("()=>window.__a3dStdUsed('tfl.ptal')") or ''
            ck(u1 == "Public Transport Accessibility Level (PTAL): Assessing transport connectivity in London (2015), applied outside its place (Greater London; no edition is recorded in force for Philadelphia, US on 2026-01-01)",
               "an edition used outside its place says where it is in force and why it is used here (%s)" % u1)
            ck(await safe("()=>window.__a3dStdPick('ibc.occupant_load','ibc.2018.1004.5')") is True and (await ed('ibc.occupant_load')).get('how') == 'chosen' and
               (await safe("()=>window.__a3dStdUsed('ibc.occupant_load')") or '').endswith('International Building Code 2018, Table 1004.5, chosen for this project'),
               "an edition chosen for the project is the one in force, and says so")
            ck(await safe("()=>window.__a3dStdPick('ibc.occupant_load','ibc.1997')") is False and 'has no edition ibc.1997' in await toast(), "an edition the topic does not have is refused")
            await safe("()=>window.__a3dStdPick('ibc.occupant_load',null)")
            ck((await ed('ibc.occupant_load')).get('how') == 'adopted', "and back to the one in force by place and date")
            ck(await safe("()=>window.__a3dStdSetDate('next week')") is False and 'A date is YYYY-MM-DD' in await toast() and (await safe("()=>window.__a3dStdState()") or {}).get('date') == '2026-01-01',
               "a date not YYYY-MM-DD is refused, the date kept")
            await safe("()=>window.__a3dStdSetDate('')")
            ck((await safe("()=>window.__a3dStdState()") or {}).get('date') == '' and 'today' in await toast(), "blank is today")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. The place")
            await safe("()=>window.__a3dTestClearUndo()")
            d0 = await safe("()=>window.__a3dUndoDepth()")
            ck(await safe("(a)=>window.__a3dStdPlaceFromAddress(a)", R.NOM_WESTMINSTER) is True, "a place from Nominatim's address parts")
            P = await safe("()=>window.__a3dStdPlace()") or {}
            ck(P.get('cc') == 'gb' and P.get('r') == 'gb-eng' and P.get('d8') == 'gb-wsm' and P.get('city') == 'City of Westminster' and P.get('src') == 'search' and P.get('rn') == 'England',
               "the country, the region and the district as ISO 3166-2 gives them, the city by name (%s)" % P)
            pth = [x['k'] for x in await safe("()=>window.__a3dStdPath()") or []]
            ck(pth == ['gb-eng:city of westminster', 'gb-wsm', 'gb-eng', 'gb', '*'], "the path most specific first: the city, the district, the region, the country, international (%s)" % pth)
            ck((await ed('tfl.ptal')).get('at') == 'City of Westminster' and await safe("()=>window.__a3dUndoDepth()") == d0 + 1, "PTAL in force there; one undo step")
            await safe("()=>window.__a3dUndo()")
            ck((await safe("()=>window.__a3dStdPlace()") or {}).get('d8') == 'gb-lds' or (await safe("()=>window.__a3dStdPlace()") or {}).get('city') == 'Philadelphia',
               "undone, the place before it is back")
            ck(await safe("()=>window.__a3dStdPlaceFromAddress({road:'x'})") is False, "an answer without a country sets no place")
            for bad_, msg in (({'cc': 'USA'}, 'A country is two letters'), ({'cc': 'us', 'r': 'PA'}, 'A region is its ISO 3166-2 code'), ({'cc': 'us', 'r': 'gb-eng'}, 'The region GB-ENG is not in US')):
                ck(await safe("(p)=>window.__a3dStdSetPlace(p,'hand')", bad_) is False and msg in await toast(), "by hand, %s is refused: %s" % (bad_, msg))
            ck(await safe("()=>window.__a3dStdSetPlace({cc:' US ',r:'us-PA'},'hand')") is True and (await safe("()=>window.__a3dStdPlace()") or {}).get('r') == 'us-pa' and
               'The site is in US-PA' not in await toast() and 'the standards in force there apply' in await toast(), "by hand, tidied: US, US-PA (%s)" % await toast())
            await safe("()=>window.__a3dStdSetPlace(null)")
            ck(await safe("()=>window.__a3dStdPlace()") is None and 'cleared' in await toast() and (await ed('tfl.ptal')).get('why') == "the site's place is not set", "cleared: no place, and every edition says so")
            # from Find: the site and its place in one step
            ST2 = {}
            c2, p2, e2_, w2 = await fresh(ST2, lot=False)
            sun0 = await safe("()=>window.__a3dSunSettings()", pg=p2)
            r2 = await safe("()=>window.__a3dMapFind('1401 John F. Kennedy Boulevard')", pg=p2)
            ck(r2 and r2.get('found') and ST2.get('nom') and 'addressdetails=1' in ST2['nom'][0] and ST2['nom'][0].startswith('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&addressdetails=1&q='),
               "Find asks Nominatim once, for the address's parts too (%s)" % (ST2.get('nom') or [''])[0][:110])
            P2 = await safe("()=>window.__a3dStdPlace()", pg=p2) or {}
            ck(P2.get('cc') == 'us' and P2.get('r') == 'us-pa' and P2.get('city') == 'Philadelphia' and P2.get('src') == 'search' and abs(P2.get('lat', 0) - AFX.LAT0) < 1e-6,
               "the place found is the site's place, and where it was found (%s)" % P2)
            await safe("()=>window.__a3dUndo()", pg=p2)
            await p2.wait_for_timeout(100)
            ck(await safe("()=>window.__a3dStdPlace()", pg=p2) is None and (await safe("()=>window.__a3dSunSettings()", pg=p2) or {}).get('lat') == sun0.get('lat'),
               "one undo puts back the site and its place")
            await safe("()=>window.__a3dRedo&&window.__a3dRedo()", pg=p2)
            await safe("()=>window.__a3dMapFindReset()", pg=p2)
            await safe("()=>window.__a3dMapFind('1401 John F. Kennedy Boulevard')", pg=p2)
            ST2['addr'] = None
            ST2['at'] = (AFX.LAT0 + 0.2, AFX.LON0)
            await safe("()=>window.__a3dMapFindReset()", pg=p2)
            await safe("()=>window.__a3dMapFind('somewhere north')", pg=p2)
            ck((await safe("()=>window.__a3dStdPlace()", pg=p2) or {}).get('city') == 'Philadelphia', "an answer without the address's parts leaves the place as it was")
            await safe("()=>window.__a3dStdCommand()", pg=p2)
            await p2.wait_for_timeout(200)
            gm = await std_group(pg=p2)
            ck('The site has moved since its place was found' in gm.get('text', ''), "and Properties says the site has moved since its place was found")
            ck(not e2_, "no page error (%s)" % e2_[:2])
            await c2.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Overrides")
            await safe("()=>window.__a3dStdSetPlace({cc:'us',r:'us-pa',city:'Philadelphia'},'hand')")
            for args, msg in ((('tfl.ptal', 'walk_bus', 9, ''), 'Say why the walk to a bus stop is overridden'),
                              (('tfl.ptal', 'walk_bus', 'nine', 'x'), 'Type a number for the walk to a bus stop'),
                              (('tfl.ptal', 'walk_bus', 0, 'x'), 'must be more than zero'),
                              (('tfl.ptal', 'walk_bus', 12, 'x'), 'must be less than 12 minutes (walk_rail)'),
                              (('tfl.ptal', 'walk_rail', 8, 'x'), 'must be more than 8 minutes (walk_bus)'),
                              (('land.slope', 'b3', 25, 'x'), 'must be less than 25% (b4)'),
                              (('app.climate', 'comfort_t1', 19, 'x'), 'must be more than 20\u00b0C (comfort_t0)'),
                              (('tfl.ptal', 'bands', 3, 'x'), 'is a table: change it with a standards pack'),
                              (('ada.2010', 'ramp_slope', 7, 'x'), 'is not applied by the app yet'),
                              (('walk.speed', 'kmh', 5, 'x'), 'There is no kmh in Walking speed')):
                r_ = await safe("(a)=>window.__a3dStdOverride(a[0],a[1],a[2],a[3])", list(args))
                ck(r_ is False and msg in await toast(), "refused: %s %s (%s)" % (args[1], args[2], msg))
            ck(await safe("()=>window.__a3dStdState().ov") == {}, "nothing refused is kept")
            ck(await safe("()=>window.__a3dStdOverride('app.climate','base',-2,'A cold store')") is True, "a temperature may be below zero")
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dStdOverride('land.slope','b1',0,'x')") is True, "a percentage may be zero")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dTestClearUndo()")
            ck(await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus','9,5','  A  slower walk, for older residents  ')") is True and await safe("()=>window.__a3dUndoDepth()") == 1,
               "a value with a decimal comma, and a reason: one undo step")
            o = (await safe("()=>window.__a3dStdState().ov") or {}).get('tfl.ptal|walk_bus') or {}
            ck(o.get('v') == 9.5 and o.get('why') == 'A slower walk, for older residents' and o.get('at') == TODAY, "kept with its reason, tidied, and its date (%s)" % o)
            ck(await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 9.5 and await safe("()=>window.__a3dStdSay('tfl.ptal','walk_bus')") == '9.5 minutes',
               "the reader returns it, and says it with its unit")
            ck('the walk to a bus stop is 9.5 minutes in this project (overridden; the standard has 8 minutes)' in await toast(), "and says what the standard has (%s)" % await toast())
            uo = await safe("()=>window.__a3dStdUsed('tfl.ptal')") or ''
            ck(uo.endswith('; overridden: the walk to a bus stop 9.5 minutes (A slower walk, for older residents)'), "what a result says names the override and why (%s)" % uo[-90:])
            ck(await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_rail',9,'x')") is False and 'must be more than 9.5 minutes' in await toast(), "the order holds against the override")
            ck(await safe("()=>window.__a3dStdClear('tfl.ptal','walk_bus')") is True and await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 8 and
               await safe("()=>window.__a3dUndoDepth()") == 2, "cleared: the standard's again, one undo step")
            ck(await safe("()=>window.__a3dStdClear('tfl.ptal','walk_bus')") is False and 'not overridden' in await toast(), "a value not overridden has nothing to clear")
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 9.5, "undo brings the override back")
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 8, "and undo again takes it away")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. The words follow")
            ST3 = {}
            c3, p3, e3_, w3 = await fresh(ST3)
            fin = await analyze(p3)
            ck({s['id']: s['state'] for s in fin.get('steps', [])}.get('access') == 'ok', "Analyze site in Philadelphia (%s)" % [(s['id'], s['state']) for s in fin.get('steps', [])][:6])
            P3 = await safe("()=>window.__a3dStdPlace()", pg=p3) or {}
            ck(P3.get('r') == 'us-pa' and P3.get('src') == 'search', "the address search set the site's place (%s)" % P3)

            async def els(a):
                return {x['k']: x for x in await safe("(a)=>window.__a3dState().objs.filter(function(o){return o.t==='diag'&&o.dg.a===a;}).map(function(o){return {k:o.dg.k,name:o.name,info:o.dg.info,lb:o.dg.lb};})", a, pg=p3) or []}
            T0 = await els('transit')
            ck(T0.get('catch8', {}).get('name') == 'Within an 8-minute walk' and T0.get('catch12', {}).get('name') == "8 to 12 minutes' walk", "the catchments named by PTAL's walks: 8 and 12 minutes")
            await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus',11,'An example')", pg=p3)
            await safe("()=>window.__a3dDgRun('transit')", pg=p3)
            T1 = await els('transit')
            ck(T1.get('catch8', {}).get('name') == 'Within an 11-minute walk' and T1.get('catch12', {}).get('name') == "11 to 12 minutes' walk" and
               T1.get('catch8', {}).get('info', {}).get('title') == "The streets within an 11-minute walk: PTAL's reach to a bus stop",
               "overridden to 11 minutes: 'Within an 11-minute walk', '11 to 12 minutes' walk' (%s)" % T1.get('catch8', {}).get('name'))
            await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus',9,'A slower walk')", pg=p3)
            await safe("()=>window.__a3dDgRun('transit')", pg=p3)
            T2 = await els('transit')
            ck(T2.get('catch8', {}).get('name') == 'Within a 9-minute walk' and 'TfL\'s PTAL: the walk at 4.8 km/h (9 minutes to a bus, 12 to rail), half the headway, and 2 minutes (bus) or 0.75 (rail)' in
               (T2.get('ptal', {}).get('info') or {}).get('method', ''), "9 minutes: 'Within a 9-minute walk', and PTAL's method says the walks it used (%s)" % (T2.get('ptal', {}).get('info') or {}).get('method', '')[:110])
            rl = [(x.get('name'), x.get('short')) for x in ((await safe("()=>window.__a3dDgState()", pg=p3) or {}).get('runs', {}).get('transit', {}).get('legend') or [])]
            ck(('Within 9 minutes', '9 min') in rl and ('9 to 12 minutes', '12 min') in rl, "the key says 9 minutes too (%s)" % rl)
            stops = [x for k, x in T2.items() if k.startswith('stop:')]
            reach = [dict(x['info'].get('rows', [])).get("Within PTAL's reach") for x in stops]
            ck(reach and all(r_ in ('9 minutes for a bus', '12 minutes for rail, metro, light rail and tram') for r_ in reach), "each stop says PTAL's reach to it (%s)" % reach[:3])
            await safe("()=>window.__a3dStdOverride('walk.speed','m_min',60,'A hilly site')", pg=p3)
            await safe("()=>window.__a3dDgRun('frame')", pg=p3)
            FR = await els('frame')
            rows = {k: dict(x['info'].get('rows', [])).get('On foot') for k, x in FR.items() if k.startswith('dist:')}
            ck(rows and all(v == 'about %d min, at 60 m a minute, as the crow flies' % max(1, int(math.floor(int(k[5:]) / 60 + 0.5))) for k, v in rows.items()),
               "the compass rings' minutes at the walking speed overridden to 60 m a minute (%s)" % list(rows.items())[:2])
            cn = await finding('access.connectivity', pg=p3)
            await safe("()=>window.__a3dStdOverride('leed.nd','case1',100,'A stricter test')", pg=p3)
            cn2 = await finding('access.connectivity', pg=p3)
            ck(cn and "LEED ND's 90 per square mile" in cn and cn2 and "LEED ND's 100 per square mile" in cn2 and cn2.replace('100 per square', '90 per square') == cn,
               "the connectivity finding is worked out again with LEED's prerequisite overridden to 100 (%s)" % (cn2 or '')[:120])
            sl = await finding('landform.slope', pg=p3)
            await safe("()=>window.__a3dStdOverride('land.slope','b1',6,'Gentler class')", pg=p3)
            sl2 = await finding('landform.slope', pg=p3)
            ck(sl and 'under 5%' in sl and sl2 and 'under 6%' in sl2, "the slope finding's gentle share by the first class's edge, 5%% then 6%% (%s -> %s)" % (sl, sl2))
            def scale_row(E):
                return [dict(x['info'].get('rows', [])).get('For scale') for x in E.values() if (x.get('info') or {}).get('rows') and dict(x['info']['rows']).get('For scale')]
            nz0 = scale_row(await els('noise'))
            await safe("()=>window.__a3dStdOverride('who.noise','road_lden',55,'An example')", pg=p3)
            await safe("()=>window.__a3dDgRun('noise')", pg=p3)
            nz1 = scale_row(await els('noise'))
            ck(nz0 and all(r_.startswith('WHO advises road noise below 53 dB Lden') for r_ in nz0) and nz1 and all(r_.startswith('WHO advises road noise below 55 dB Lden') for r_ in nz1),
               "the noise layer's sense of scale is WHO's road traffic guideline: 53 dB Lden, then 55 overridden (%s)" % (nz1 or [''])[0][:60])
            rf = await finding('landform.terrain', pg=p3) or ''
            await safe("()=>window.__a3dStdOverride('land.slope','b3',16,'An example')", pg=p3)
            rf2 = await finding('landform.terrain', pg=p3) or ''
            ck('steeper than 15%' in rf and 'steeper than 16%' in rf2, "the relief finding's steep share by the slope classes' edge, 15%% then 16%% (%s)" % rf2[-40:])
            await safe("()=>window.__a3dClbOpen('access')", pg=p3)
            ab_ = await safe("()=>window.__a3dClbHtml()", pg=p3) or ''
            await safe("()=>{window.__a3dClbClose();window.__a3dClbOpen('climate');window.__a3dClbClose();}", pg=p3)   # the climate board again, as the rest of the suite reads it
            ck('Connectivity after LEED v4 for Neighborhood Development (updated 2 July 2018) (Neighborhood Pattern and Design): 100 intersections per square mile within 400 m to qualify, 140 inside a project with streets of its own, points from 300.' in ab_,
               "the Access board's note says LEED's edition and thresholds from the registry, the prerequisite overridden to 100")
            sd = [c_['desc'] for c_ in await safe("()=>window.__a3dCommandCatalog()", pg=p3) or [] if c_.get('name') == 'SLOPEMAP']
            ck(sd and 'bands of the standards registry' in sd[0] and '%' not in sd[0], "SLOPEMAP names the registry's bands, not a copy of them (%s)" % sd)
            await safe("()=>window.__a3dStdOverride('asce7.combos','c2_l',1.5,'An example')", pg=p3)
            cb2 = await safe("()=>window.__a3dCombos()", pg=p3) or []
            ck(cb2[:2] == ['1.2D+1.5L', '1.4D'], "the frame's first combination named by its factors, 1.2D+1.5L (%s)" % cb2)
            await safe("()=>window.__a3dStdOverride('app.roads','residential_v',30,'A slow zone')", pg=p3)
            ck((await safe("()=>window.__a3dDgRoadClass('residential')", pg=p3) or {}).get('v') == 30, "a residential street's speed where none is mapped, overridden to 30 km/h")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Out of date")
            await safe("()=>window.__a3dAnzView(true)", pg=p3)
            await p3.wait_for_timeout(200)
            await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus',10,'Slower still')", pg=p3)
            await p3.wait_for_timeout(200)
            ct = await card('dgtransit', pg=p3)
            ck(ct.get('state') == 'Out of date' and 'Out of date: Public Transport Accessibility Level (PTAL): walk_bus overridden since it ran: Run again' in ct.get('st', ''),
               "Transit's row: Out of date, PTAL's walk to a bus overridden since it ran (%s)" % ct)
            ck('Walking speed: m_min overridden since the access data was fetched: Analyze site again' in ct.get('st', ''), "and the walking speed changed since the access data was fetched (%s)" % ct.get('st', '')[-120:])
            ch = await safe("()=>window.__a3dDgStdChanged('transit')", pg=p3) or {}
            ck([c['t'] for c in ch.get('run', [])] == ['tfl.ptal'] and [c['t'] for c in ch.get('data', [])] == ['walk.speed'] and ch.get('kind') == 'access', "what changed, by run and by data (%s)" % ch)
            await safe("()=>window.__a3dDgRun('transit')", pg=p3)
            await p3.wait_for_timeout(150)
            ct2 = await card('dgtransit', pg=p3)
            ck('since it ran' not in ct2.get('st', '') and 'since the access data was fetched: Analyze site again' in ct2.get('st', '') and ct2.get('state') == 'Out of date',
               "run again, its own standards are current; the access data still needs Analyze site (%s)" % ct2.get('st', '')[-90:])
            await safe("()=>window.__a3dStdClear('walk.speed','m_min')", pg=p3)
            await p3.wait_for_timeout(150)
            ct3 = await card('dgtransit', pg=p3)
            ck(ct3.get('state') != 'Out of date' and 'Out of date' not in ct3.get('st', ''), "with the walking speed back as fetched, Transit is current (%s)" % ct3)
            cf = await card('dgframe', pg=p3)
            ck('Out of date: Walking speed: m_min back to the standard since it ran: Run again' in cf.get('st', '') and cf.get('std', '').startswith('Standards: Walking speed: '),
               "the compass rings ran at 60 m a minute: out of date now the speed is back, and its row names the walking speed (%s)" % cf.get('st', '')[-90:])
            ck(cf.get('std', '') == "Standards: Walking speed: The app's walking speed, TfL's figure", "each row names the standards it uses (%s)" % cf.get('std'))
            ctr = await card('dgtransit', pg=p3)
            ck(ctr.get('std', '').startswith('Standards: Public Transport Accessibility Level (PTAL): Assessing transport connectivity in London (2015), applied outside its place (Greater London; ') and
               'overridden: the walk to a bus stop 10 minutes (Slower still)' in ctr.get('std', '') and ctr.get('std', '').endswith("Walking speed: The app's walking speed, TfL's figure"),
               "Transit's row: PTAL applied outside its place, its override and why, and the walking speed (%s)" % ctr.get('std', '')[:150])
            await safe("()=>window.__a3dStdOverride('app.context','storey',3.5,'Taller storeys here')", pg=p3)
            await p3.wait_for_timeout(150)
            cv, cno = await card('dgviews', pg=p3), await card('dgnoise', pg=p3)
            ck('Site context where OpenStreetMap does not say: storey overridden since the site context was fetched: Analyze site again' in cv.get('st', '') and
               'since the site context was fetched' in cno.get('st', ''), "views and noise are drawn from the site context: out of date with a storey's height changed (%s)" % cv.get('st', '')[-100:])
            ck('WHO environmental noise guidelines: road traffic: Environmental Noise Guidelines for the European Region (2018), applied outside its place (Guidance for the WHO European Region, adopted nowhere as a rule;' in cno.get('std', ''),
               "the noise row names WHO's road traffic guideline, applied outside its place, as it is everywhere (%s)" % cno.get('std', '')[-160:])
            await safe("()=>window.__a3dStdOverride('app.climate','base',20,'Our heating base')", pg=p3)
            await p3.wait_for_timeout(150)
            cw = await card('dgwind', pg=p3)
            ck('Climate readings: base overridden since the climate data was fetched: Analyze site again' in cw.get('st', ''), "the winds drawn from the climate data (%s)" % cw.get('st', '')[-90:])
            # a run from before V167: its stamp is the editions' own values
            await safe("()=>{var D=window.__a3dDgState();}", pg=p3)
            old = await safe("""()=>{var s=window.__a3dStdStamp(['walk.speed']);window.__a3dStdClear&&0;return s;}""", pg=p3)
            ck(old and old['list'][0]['ov'] == {}, "the walking speed as the edition has it (%s)" % old)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Findings")
            await safe("()=>document.querySelector('[data-saact=\"analyze\"]')&&0", pg=p3)
            line = await safe("()=>{var o={};[].forEach.call(document.querySelectorAll('[data-safstd]'),function(e){o[e.getAttribute('data-safstd')]=e.textContent;});return o;}", pg=p3) or {}
            ck(sorted(line) == sorted(['access.cycling', 'access.transit', 'access.walk', 'access.connectivity', 'people.daily', 'climate.comfort', 'climate.degreedays', 'climate.wind', 'risk.air',
                                       'landform.slope', 'landform.terrain', 'water.fema', 'location.built',
                                       'location.landuse', 'location.density', 'ecology.33300']), "each finding drawn from a standard names it: 16 (%s)" % sorted(line))   # AMENDED FOR V168: the land's three
            ck(line.get('water.fema') == "Standards: Flood zones: 44 CFR 64.3, the flood insurance rate map's zone symbols" and
               line.get('risk.air') == 'Standards: WHO air quality guidelines: fine particulate matter (PM2.5): WHO global air quality guidelines (2021)', "an edition in force for the place, by name")
            ck('applied outside its place (Greater London; no edition is recorded in force for Philadelphia, Pennsylvania, United States on %s)' % TODAY in line.get('access.transit', ''),
               "PTAL applied outside its place, said so, with Philadelphia named as Nominatim gave it")
            dd = await finding('climate.degreedays', pg=p3)
            ck(dd and '(base 18 \u00b0C)' in dd and 'Out of date: Climate readings: base overridden since the climate data was fetched: Analyze site again' in line.get('climate.degreedays', ''),
               "the degree days were worked out at 18 \u00b0C: the finding says 18, and that Analyze site is needed for 20 (%s)" % (dd or '')[:80])
            ck('overridden: the degree-day base temperature 20\u00b0C (Our heating base)' in line.get('climate.degreedays', ''), "and the override and its reason")
            ck("LEED ND's 100 per square mile" in (await finding('access.connectivity', pg=p3) or '') and 'Out of date' not in line.get('access.connectivity', ''),
               "a threshold applied as the finding is drawn is not out of date")
            await safe("()=>window.__a3dStdOverride('leed.nd','radius',500,'A wider count')", pg=p3)
            l2 = await safe("()=>window.__a3dSaStdText('access.connectivity')", pg=p3) or ''
            ck(l2.endswith('Out of date: LEED for Neighborhood Development: connectivity: radius overridden since the access data was fetched: Analyze site again') and
               'within 400 m' in (await finding('access.connectivity', pg=p3) or ''), "LEED's radius is the access data's: the count is still within 400 m, out of date (%s)" % l2[-120:])
            ck('Out of date' not in (await card('dgtransit', pg=p3)).get('st', 'Out of date'), "LEED's radius is not Transit's: its row stays current")
            ab = await safe("()=>window.__a3dSaStdText('location.built')", pg=p3) or ''
            ck('Out of date: Site context where OpenStreetMap does not say: storey overridden since the site context was fetched: Analyze site again' in ab, "the context's finding too")
            bh = await safe("()=>window.__a3dClbHtml()", pg=p3) or ''
            # the targets over the chart's top are not drawn: the fourth, brought under it, is
            await safe("()=>window.__a3dStdOverride('who.aqg','pm25_24h_it4',16,'An example')", pg=p3)
            bh2 = await safe("()=>window.__a3dClbHtml()", pg=p3) or ''
            ck('WHO 24-hour guideline, 15 ' in bh and 'interim target 4' not in bh and 'WHO interim target 4, 16 ' in bh2,
               "the climate board's air chart draws WHO's interim targets from the registry: the fourth overridden to 16 is drawn")
            ck('base 18 \u00b0C' in bh2 and 'base 20 \u00b0C' not in bh2, "and its degree days at the base they were worked out with, 18 \u00b0C")
            ck(bh.count('20\u201327 \u00b0C') >= 3 and 'href="https://iris.who.int/handle/10665/345329"' in bh and '>WHO global air quality guidelines (2021)</a>' in bh,
               "its comfort band in the KPI, the key and the notes as the climate data used it; its notes cite WHO's edition in force, by name and source")
            await safe("()=>window.__a3dStdClear('who.aqg','pm25_24h_it4')", pg=p3)
            # Analyze site again: the data fetched with the values as they are now
            await safe("()=>window.__a3dStdClear('leed.nd','radius')", pg=p3)
            await safe("()=>window.__a3dStdClear('app.context','storey')", pg=p3)
            await safe("()=>window.__a3dStdOverride('app.climate','comfort_t0',21,'A warmer band')", pg=p3)
            await safe("()=>window.__a3dStdOverride('crtn','range',400,'A wider range')", pg=p3)
            fin2 = await analyze(p3)
            ctx2 = {s_['id']: s_.get('text', '') for s_ in fin2.get('steps', [])}.get('context', '')
            ck('400 m around' in ctx2 or 'the context radius is 400 m now' in ctx2, "Analyze site fetches the context as far as CRTN's range, overridden to 400 m (%s)" % ctx2[:120])
            ck('21\u201327 \u00b0C' in (await safe("()=>window.__a3dClbHtml()", pg=p3) or ''), "and the climate board's comfort band is the one the new data used, 21 to 27 \u00b0C")
            dd2 = await finding('climate.degreedays', pg=p3)
            l3 = await safe("()=>window.__a3dSaStdText('climate.degreedays')", pg=p3) or ''
            ck(dd2 and '(base 20 \u00b0C)' in dd2 and 'Out of date' not in l3 and dd2 != dd, "Analyze site again: the degree days at 20 \u00b0C, current (%s)" % (dd2 or '')[:80])
            ct4 = await card('dgtransit', pg=p3)
            ck('Out of date' not in ct4.get('st', ''), "and Transit is current (%s)" % ct4.get('st', '')[-80:])
            # a project from before V167: its runs and data without stamps, taken as the editions' own values
            await safe("()=>{var o=window.__a3dStdState().ov;Object.keys(o).forEach(function(k){var j=k.indexOf('|');window.__a3dStdClear(k.slice(0,j),k.slice(j+1));});}", pg=p3)
            await p3.wait_for_timeout(900)
            rec = json.loads(await safe("()=>localStorage.getItem('acad3dV1')", pg=p3) or '{}')
            S_ = rec.get('site') or {}
            for r_ in (S_.get('diag') or {}).get('runs', {}).values():
                r_.pop('std', None)
            for path_ in (('access', 'std'), ('context', 'last', 'std'), ('climate', 'std'), ('climate', 'normals', 'used'), ('climate', 'hourly', 'used'),
                          ('risk', 'air', 'std'), ('risk', 'air', 'used'), ('std',)):
                o_ = S_
                for k_ in path_[:-1]:
                    o_ = o_.get(k_) or {}
                o_.pop(path_[-1], None)
            await c3.close()   # the app saves as a page unloads: the project from before V167 goes into a context of its own
            c3 = await browser.new_context(viewport={'width': 1440, 'height': 900})
            for hh in FX.HOSTS:
                await c3.route(hh, handler(ST3))
            for hh in BLOCKERS:
                await c3.route(hh, lambda r: r.abort())
            await c3.add_init_script("if(!sessionStorage.getItem('v167seed')){localStorage.setItem('acad3dV1',%s);sessionStorage.setItem('v167seed','1');}" % json.dumps(json.dumps(rec)))
            p3 = await c3.new_page()
            p3.on('pageerror', lambda x: e3_.append(str(x)))
            await within(p3.goto('file://' + str(HTML)), 'goto')
            await p3.wait_for_timeout(2000)
            await safe("()=>window.__a3dAnzView(true)", pg=p3)
            await p3.wait_for_timeout(200)
            old_ = await safe("()=>{var D=window.__a3dDgState();return {runs:Object.keys(D.runs).filter(function(k){return D.runs[k].std;}),acc:!!window.__a3dAcc().access.std,std:window.__a3dStdState()};}", pg=p3) or {}
            ch0 = await safe("()=>['transit','frame','views','wind'].map(function(a){var c=window.__a3dDgStdChanged(a);return c.run.length+c.data.length;})", pg=p3)
            ck(old_.get('runs') == [] and old_.get('acc') is False and old_.get('std') is None and ch0 == [0, 0, 0, 0] and 'Out of date' not in (await card('dgtransit', pg=p3)).get('st', 'Out of date'),
               "a project from before V167, no stamps: its runs and data taken as worked out with the editions' own values, current (%s, %s)" % (old_, ch0))
            await safe("()=>window.__a3dStdOverride('tfl.ptal','walk_bus',9,'Slower')", pg=p3)
            await safe("()=>window.__a3dStdOverride('app.climate','calm',1,'A breezier calm')", pg=p3)
            await p3.wait_for_timeout(150)
            ck('Public Transport Accessibility Level (PTAL): walk_bus overridden since it ran: Run again' in (await card('dgtransit', pg=p3)).get('st', '') and
               (await safe("()=>window.__a3dSaStdText('climate.wind')", pg=p3) or '').endswith('Out of date: Climate readings: calm overridden since the climate data was fetched: Analyze site again'),
               "and once a value is overridden, out of date as any other")
            ck((await safe("()=>window.__a3dSa().findings.filter(function(f){return f.auto==='climate.degreedays';})[0].value", pg=p3) or '').find('(base 18 \u00b0C)') >= 0,
               "its degree days said at the edition's own base, 18 \u00b0C")
            ck(not e3_, "no page error (%s)" % e3_[:2])

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Packs")
            txt = pack()
            sha = hashlib.sha256(txt.encode('utf-8')).hexdigest()
            await safe("()=>window.__a3dStdSetPlace({cc:'us',r:'us-pa',city:'Philadelphia'},'hand')")
            s0 = await safe("()=>window.__a3dStdState()")
            D = await safe("(t)=>window.__a3dStdPackDiff(t)", txt) or {}
            ck(D.get('ok') and D.get('sha') == sha and await safe("(t)=>window.__a3dSha256(t)", txt) == sha, "its SHA-256 is Python's (%s)" % (D.get('sha') or '')[:16])
            ck(D.get('pub') == 'Example Planning Office' and D.get('name') == 'Example walking standard' and D.get('signed') is False and D.get('date') == '2026-09-01', "its publisher, name and date, unsigned")
            tw = {t['t']: t for t in D.get('topics', [])}
            w_ = tw.get('walk.speed', {})
            ck(w_.get('before') == 'walk.speed.1' and w_.get('beforeHow') == 'assumption' and w_.get('after') == 'walk.speed.pa2026' and w_.get('afterHow') == 'adopted' and
               w_.get('changes') == [{'n': 'm_min', 'say': 'the walking speed', 'from': 80, 'to': 70, 'u': 'm/min'}] and w_.get('applied') is True,
               "what it changes, first: the walking speed's edition in force, 80 to 70 m a minute (%s)" % w_)
            ex = tw.get('ex.parking', {})
            ck(ex.get('before') is None and ex.get('after') == 'ex.parking.1' and ex.get('applied') is False, "a topic the app does not apply: listed, not applied (%s)" % ex)
            ck(await safe("()=>window.__a3dStdState()") == s0 and await safe("()=>window.__a3dStd('walk.speed','m_min')") == 80, "nothing changes before Apply")
            sha2 = await safe("(t)=>window.__a3dSha256(t)", '\u00e9\U0001F600 abc') or ''
            ck(sha2 == hashlib.sha256('\u00e9\U0001F600 abc'.encode('utf-8')).hexdigest(), "the app's SHA-256 reads UTF-8, a character outside the BMP too")
            REF = [('not json', 'The file is not JSON'), (json.dumps({'format': 'x'}), 'its format is not bim-standards-pack'),
                   (pack(version=2), 'A pack of version 2'), (pack(publisher=''), 'names no publisher'), (pack(topics=[]), 'has no topics'),
                   (pack(eds_walk=[{'id': 'walk.speed.1', 'adopt': [], 'v': [{'n': 'm_min', 'v': 70}]}]), 'is already in the registry; a revision is a new edition'),
                   (pack(eds_walk=[{'id': 'walk.speed.x', 'adopt': [], 'v': []}]), 'lacks m_min (the walking speed), which the app reads'),
                   (pack(eds_walk=[{'id': 'walk.speed.x', 'adopt': [], 'v': [{'n': 'm_min', 'v': '70'}]}]), 'm_min must be a number'),
                   (pack(eds_walk=[{'id': 'walk.speed.x', 'adopt': [{'at': 'Pennsylvania'}], 'v': [{'n': 'm_min', 'v': 70}]}]), 'is not a place key'),
                   (pack(eds_walk=[{'id': 'walk.speed.x', 'v': [{'n': 'm_min', 'v': 70}]}]), 'says nothing of where it is in force'),
                   ('{"format":"bim-standards-pack","version":1,"publisher":"x","name":"x","topics":[{"id":"x","eds":[]}],"pad":"' + 'x' * 1048600 + '"}', 'larger than 1 MB')]
            for t_, msg in REF:
                d_ = await safe("(t)=>window.__a3dStdPackDiff(t)", t_) or {}
                ck(d_.get('ok') is False and msg in (d_.get('err') or ''), "refused: %s (%s)" % (msg, (d_.get('err') or '')[:90]))
            tb = pack(eds_walk=[{'id': 'walk.speed.x', 'adopt': [], 'v': [{'n': 'm_min', 'v': 70}]}],
                      extra=[{'id': 'tfl.ptal', 'eds': [{'id': 'tfl.ptal.x', 'adopt': [], 'v': [{'n': 'walk_bus', 'v': 8}, {'n': 'walk_rail', 'v': 12}, {'n': 'walk_tram', 'v': 12}, {'n': 'k_bus', 'v': 2},
                                                                                                  {'n': 'k_rail', 'v': 0.75}, {'n': 'bands', 'v': 5}]}]}])
            ck('bands must be a table' in ((await safe("(t)=>window.__a3dStdPackDiff(t)", tb) or {}).get('err') or ''), "a table must be a table")
            await safe("()=>window.__a3dTestClearUndo()")
            d0 = await safe("()=>window.__a3dUndoDepth()")
            A_ = await safe("(t)=>window.__a3dStdPackApply(t)", txt) or {}
            st1 = await safe("()=>window.__a3dStdState()") or {}
            ck(A_.get('ok') and [p_['sha'] for p_ in st1.get('packs', [])] == [sha] and st1['packs'][0]['pub'] == 'Example Planning Office' and st1['packs'][0]['at'] == TODAY and
               await safe("()=>window.__a3dUndoDepth()") == d0 + 1, "Apply: kept with the project, its SHA-256, publisher and date; one undo step")
            ck('(Example Planning Office, unsigned) is applied: 2 topics. Its SHA-256: ' + sha[:16] in await toast(), "and says so (%s)" % await toast())
            e_ = await ed('walk.speed')
            ck(e_.get('id') == 'walk.speed.pa2026' and e_.get('how') == 'adopted' and e_.get('pack') == sha and await safe("()=>window.__a3dStd('walk.speed','m_min')") == 70,
               "the edition in force in Pennsylvania is the pack's: 70 m a minute (%s)" % e_.get('id'))
            ck((await safe("(t)=>window.__a3dStdPackDiff(t)", txt) or {}).get('err') == 'This pack is already applied to the project', "the same pack twice is refused")
            await safe("()=>window.__a3dStdSetPlace({cc:'us',r:'us-ny'},'hand')")
            ck((await ed('walk.speed')).get('id') == 'walk.speed.1', "in New York the app's own walking speed")
            await safe("()=>window.__a3dUndo()")
            ck(await safe("()=>window.__a3dStdPick('walk.speed','walk.speed.pa2026')") is True, "the pack's edition can be chosen")
            ck(await safe("(s)=>window.__a3dStdPackRemove(s)", sha) is True and await safe("()=>window.__a3dStdState().packs") == [] and
               await safe("()=>window.__a3dStdState().pick") == {} and await safe("()=>window.__a3dStd('walk.speed','m_min')") == 80,
               "Remove: the pack gone, the edition chosen from it with it, the app's own value back")
            ck(await safe("()=>window.__a3dStdPackRemove('abc')") is False and 'No pack abc' in await toast(), "a pack not in the project")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dUndo()")
            ck([p_['sha'] for p_ in (await safe("()=>window.__a3dStdState()") or {}).get('packs', [])] == [sha], "undo brings the pack back")
            await safe("()=>window.__a3dUndo()")
            ck((await safe("()=>window.__a3dStdState()") or {}).get('packs') == [], "and undo again takes it away")
            tw2 = pack(eds_walk=[{'id': 'walk.speed.pa2025', 'name': 'From 2025', 'pub': '2025-01-01', 'adopt': [{'at': 'us-pa', 'from': '2025-01-01'}], 'v': [{'n': 'm_min', 'v': 75}]},
                                 {'id': 'walk.speed.pa2026b', 'name': 'June to August 2026', 'pub': '2026-05-01', 'adopt': [{'at': 'us-pa', 'from': '2026-06-01', 'to': '2026-09-01'}], 'v': [{'n': 'm_min', 'v': 72}]}],
                       name='Two walks')
            await safe("(t)=>window.__a3dStdPackApply(t)", tw2)
            got_w = []
            for d_ in ('2026-05-31', '2026-06-01', '2026-08-31', '2026-09-01'):
                await safe("(d)=>window.__a3dStdSetDate(d)", d_)
                got_w.append(await safe("()=>window.__a3dStd('walk.speed','m_min')"))
            ck(got_w == [75, 72, 72, 75], "two editions in force for one place: the one adopted latest; its window from its first day to the day before its end (%s)" % got_w)
            await safe("()=>window.__a3dStdSetDate('')")
            await safe("(s)=>window.__a3dStdPackRemove(s)", hashlib.sha256(tw2.encode('utf-8')).hexdigest())

            # ---------------------------------------------------------------------------------
            print("\n-- 10. The Standards group")
            await safe("()=>window.__a3dStdSetPlace(null)")
            await safe("()=>window.__a3dStdCommand()")
            await page.wait_for_timeout(200)
            G = await std_group()
            ck(G.get('tab') == 'site' and G.get('open') and G.get('prev') == 'Data Layers', "STANDARDS: Properties, Site, the Standards group open after Data Layers (%s, %s)" % (G.get('tab'), G.get('prev')))
            ck("no place set, so each is applied as the app's default and says so" in await toast(), "and says where it is (%s)" % await toast())
            # AMENDED FOR V168: Land and green, before Climate, and its four topics
            want_t = [t for a_ in ['Transit and walking', 'Roads and noise', 'Cycling', 'Air', 'Flood and ground', 'Buildings', 'Structure', 'Site context', 'Land and green', 'Climate']
                      for t in R.TOPICS if not R.TOPICS[t]['cat'] and RECS[t]['area'] == a_]
            ck(G.get('topics') == want_t and len(want_t) == 22, "the 22 topics the app applies, by area (%s)" % G.get('topics'))
            ck(G.get('areas', [])[:10] == ['Transit and walking', 'Roads and noise', 'Cycling', 'Air', 'Flood and ground', 'Buildings', 'Structure', 'Site context', 'Land and green', 'Climate'] and
               'In force here, not applied by the app yet' in G.get('areas', []) and 'Standards packs' in G.get('areas', []), "under their areas, the catalogue and the packs (%s)" % G.get('areas'))
            ck("Not set: each standard is applied as the app's default, and says so" in G.get('text', '') and 'Set the place to list the codes in force there' in G.get('text', ''), "no place: said, and no catalogue")
            for cmd in ('STANDARDS', 'STANDARDSREGISTRY', 'CODES', 'STDS'):
                reg = await safe("(n)=>window.__wsRegistry.filter(function(c){return c.name===n||(c.aliases||[]).indexOf(n)>=0;}).map(function(c){return c.name;})", cmd)
                ck(reg == ['STANDARDS'], "%s is the STANDARDS command" % cmd)
            # the place by hand
            ck(await click('[data-propstdact="place"]'), "Set the place")
            await fill('[data-propstd="cc"]', 'us')
            await fill('[data-propstd="r"]', 'us-pa')
            await fill('[data-propstd="city"]', 'Philadelphia')
            await click('[data-propstdact="placesave"]')
            P4 = await safe("()=>window.__a3dStdPlace()") or {}
            G = await std_group()
            ck(P4.get('cc') == 'us' and P4.get('r') == 'us-pa' and P4.get('city') == 'Philadelphia' and P4.get('src') == 'hand' and 'Philadelphia, US (US, US-PA)' in G.get('text', '') and
               'Set by hand, ' + TODAY in G.get('text', ''), "saved: the place, said in the group (%s)" % P4)
            ck(G.get('cat') == ['pa.ucc', 'ibc', 'ada.2010', 'mutcd', 'aashto.lrfd', 'penndot.dm4', 'faa.ac150_5300_13'],
               "the codes in force in Pennsylvania, not applied by the app yet: the UCC, the 2021 IBC, ADA, MUTCD, LRFD 8 through DM-4, DM-4, the FAA's circular; DM-2 not, its edition unread (%s)" % G.get('cat'))
            catrow = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdcat=\"aashto.lrfd\"]');return e&&e.textContent;}") or ''
            ck('AASHTO LRFD Bridge Design Specifications, 8th Edition (2017), as DM-4 adopts it' in catrow and 'in force here: US-PA' in catrow and 'AASHTO; sold' in catrow,
               "a catalogue row: the edition in force, where, its publisher and how it is had (%s)" % catrow[:160])
            lk = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody [data-stdcat] .a3d-stdsrc a'),function(a){return [a.href,a.target,a.rel];})") or []
            ck(lk and all(a_[0].startswith('https://') and a_[1] == '_blank' and a_[2] == 'noopener' for a_ in lk), "its source linked, opened apart (%d)" % len(lk))
            # the date
            await page.fill('#a3d-propsbody [data-propstd="date"]', '2025-12-31')
            await page.dispatch_event('#a3d-propsbody [data-propstd="date"]', 'change')
            await page.wait_for_timeout(150)
            G = await std_group()
            ck((await safe("()=>window.__a3dStdState()") or {}).get('date') == '2025-12-31' and 'pa.ucc' not in G.get('cat', []) and 'ibc' not in G.get('cat', []),
               "In force on 31 December 2025: the UCC's 2021 codes not yet (%s)" % G.get('cat'))
            await page.fill('#a3d-propsbody [data-propstd="date"]', '')
            await page.dispatch_event('#a3d-propsbody [data-propstd="date"]', 'change')
            await page.wait_for_timeout(150)
            # a topic's values, an override
            row = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic=\"tfl.ptal\"]');return e&&e.textContent;}") or ''
            ck('Assessing transport connectivity in London (2015)' in row and 'applied outside its place' in row and 'Used by: Transit layer' in row and row.startswith('Public Transport Accessibility Level (PTAL)'),
               "a topic: its title, the edition, its level and how it applies here, what uses it (%s)" % row[:160])
            ck(await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic=\"tfl.ptal\"] .a3d-stdlv');return e&&[e.textContent,e.title,e.className];}") == ['P', 'read at its source', 'a3d-stdlv lv-P'] and
               await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic=\"tfl.ptal\"] .a3d-stdhow');return e&&e.className;}") == 'a3d-stdhow h-outside',
               "its level, said, and coloured by its class; applied outside its place, coloured too")
            await click('[data-propstdact="open:tfl.ptal"]')
            V = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdvals=\"tfl.ptal\"]');return e?{t:e.textContent,ov:[].map.call(e.querySelectorAll('[data-propstdact^=\"ov:\"]'),function(b){return b.getAttribute('data-propstdact');})}:null;}") or {}
            vr = await safe("""()=>[].map.call(document.querySelectorAll('#a3d-propsbody [data-stdvals="tfl.ptal"] .a3d-prow'),function(r){var l=r.querySelector('.a3d-plabel'),v=r.querySelector('[data-stdval]');
              return [l?l.textContent:'',v?v.textContent:''];}).filter(function(x){return x[1];})""") or []
            ck('Applied outside its place (Greater London)' in V.get('t', '') and vr == [['The walk to a bus stop', '8 minutes'], ['The walk to a rail, Tube or DLR station', '12 minutes'],
               ['The walk to a tram stop', '12 minutes'], ['The reliability allowance for buses', '2 minutes'], ['The reliability allowance for rail, Tube and tram', '0.75 minutes']],
               "Values: each in words with its unit (%s)" % vr[:3])
            ck(V.get('ov') == ['ov:tfl.ptal|walk_bus', 'ov:tfl.ptal|walk_rail', 'ov:tfl.ptal|walk_tram', 'ov:tfl.ptal|k_bus', 'ov:tfl.ptal|k_rail'] and 'a table: a pack changes it' in V.get('t', ''),
               "an Override for each number; the bands a table, changed by a pack (%s)" % V.get('ov'))
            ck('Source: Transport for London, Assessing transport connectivity in London; section 2.5' in V.get('t', '') and '(read at its source, read 2026-10-18)' in V.get('t', ''), "and its source, to the section")
            await click('[data-propstdact="ov:tfl.ptal|walk_bus"]')
            ck(await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propstd')") == 'ovv', "Override: the value's field, focused")
            await fill('[data-propstd="ovv"]', '9')
            await click('[data-propstdact="ovsave:tfl.ptal|walk_bus"]')
            ck('Say why' in await toast() and await safe("()=>window.__a3dStdUi().edit") == 'tfl.ptal|walk_bus' and await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 8,
               "Save without a reason: refused, still editing")
            await fill('[data-propstd="ovv"]', '9')
            await fill('[data-propstd="ovwhy"]', 'Older residents')
            await click('[data-propstdact="ovsave:tfl.ptal|walk_bus"]')
            vt = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdval=\"tfl.ptal|walk_bus\"]');return e&&[e.textContent,e.className];}") or ['', '']
            ck(await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 9 and vt[0] == '9 minutes (overridden: Older residents; the standard has 8 minutes)' and 'a3d-stdovd' in vt[1],
               "with a reason: saved, shown overridden, the standard beside it (%s)" % vt[0])
            row = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic=\"tfl.ptal\"]');return e&&e.textContent;}") or ''
            ck('(1 overridden)' in row, "the topic says one value is overridden")
            await click('[data-propstdact="ovreset:tfl.ptal|walk_bus"]')
            ck(await safe("()=>window.__a3dStd('tfl.ptal','walk_bus')") == 8 and await safe("()=>!!document.querySelector('#a3d-propsbody [data-propstdact=\"ov:tfl.ptal|walk_bus\"]')") is True, "Reset: the standard's again")
            await click('[data-propstdact="open:tfl.ptal"]')
            ck(not await safe("()=>document.querySelector('#a3d-propsbody [data-stdvals=\"tfl.ptal\"]')"), "Hide closes the values")
            # an edition chosen
            opts = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody [data-propstd=\"pick:ibc.occupant_load\"] option'),function(o){return o.value;})")
            ck(opts == ['', 'ibc.2021.1004.5', 'ibc.2018.1004.5'], "a topic of two editions: chosen by place and date, or either (%s)" % opts)
            await page.select_option('#a3d-propsbody [data-propstd="pick:ibc.occupant_load"]', 'ibc.2018.1004.5')
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dStdState().pick") or {}) == {'ibc.occupant_load': 'ibc.2018.1004.5'} and 'chosen for this project' in
               (await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic=\"ibc.occupant_load\"]');return e&&e.textContent;}") or ''), "chosen in the list, said in the row")
            await page.select_option('#a3d-propsbody [data-propstd="pick:ibc.occupant_load"]', '')
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dStdState().pick") or {}) == {}, "back to place and date")
            # a pack looked at, then applied, then removed
            await safe("(t)=>window.__a3dStdPackLook(t,'walk-pa.json')", txt)
            await page.wait_for_timeout(150)
            pk = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdpack]');return e?{sha:e.getAttribute('data-stdpack'),t:e.textContent,b:[].map.call(e.querySelectorAll('[data-propstdact]'),function(b){return b.textContent;})}:null;}") or {}
            ck(pk.get('sha') == sha and sha in pk.get('t', '') and 'Example Planning Office, 2026-09-01; unsigned: its origin is the file you chose' in pk.get('t', '') and pk.get('b') == ['Apply', 'Cancel'],
               "a pack looked at: its SHA-256 in full, its publisher, unsigned; Apply or Cancel (%s)" % pk.get('t', '')[:160])
            ck('The edition in force becomes walk.speed.pa2026 (in force here), was walk.speed.1. Changes: the walking speed: 80 to 70 m/min.' in pk.get('t', '') and
               'Not applied by the app yet.' in pk.get('t', ''), "what it changes shown first")
            ck((await safe("()=>window.__a3dStdState()") or {}).get('packs') == [], "nothing applied yet")
            await click('[data-propstdact="packcancel"]')
            ck(not await safe("()=>document.querySelector('#a3d-propsbody [data-stdpack]')"), "Cancel: gone, nothing applied")
            await safe("(t)=>window.__a3dStdPackLook(t,'walk-pa.json')", txt)
            await page.wait_for_timeout(100)
            await click('[data-propstdact="packapply"]')
            G = await std_group()
            ck([p_['sha'] for p_ in (await safe("()=>window.__a3dStdState()") or {}).get('packs', [])] == [sha] and 'Example walking standard' in G.get('text', '') and
               'Example Planning Office, unsigned; SHA-256 ' + sha[:16] in G.get('text', '') and 'ex.parking' in G.get('cat', []),
               "Apply: listed with its publisher and hash; its catalogue topic in force here listed too (%s)" % G.get('cat'))
            wr = await safe("""()=>{var e=document.querySelector('#a3d-propsbody [data-stdtopic="walk.speed"]');return e&&[e.querySelector('.a3d-pstatic').textContent,e.querySelector('.a3d-stdhow').textContent,
              [].map.call(e.querySelectorAll('option'),function(o){return o.value;})];}""") or ['', '', []]
            ck(wr[0] == 'A slower walk for Pennsylvania (2026) \u2013 an example' and wr[1] == 'in force here: US-PA' and wr[2] == ['', 'walk.speed.1', 'walk.speed.pa2026'],
               "the walking speed's row shows the pack's edition, in force here, and both editions to choose from (%s)" % wr)
            await safe("(t)=>window.__a3dStdPackLook(t,'bad.json')", 'not json')
            await page.wait_for_timeout(100)
            ck('bad.json: The file is not JSON' in (await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-stdpackerr]');return e&&e.textContent;}") or ''), "a file that is not a pack: said, by name")
            await click('[data-propstdact="packcancel"]')
            await click('[data-propstdact="packremove:%s"]' % sha)
            ck((await safe("()=>window.__a3dStdState()") or {}).get('packs') == [], "Remove")
            await click('[data-propstdact="placeclear"]')
            ck(await safe("()=>window.__a3dStdPlace()") is None, "Clear the place")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. Kept")
            await safe("()=>window.__a3dStdSetPlace({cc:'gb',r:'gb-eng',d8:'gb-wsm',city:'London'},'hand')")
            await safe("()=>window.__a3dStdSetDate('2026-03-01')")
            await safe("()=>window.__a3dStdOverride('walk.speed','m_min',75,'Measured on site')")
            await safe("(t)=>window.__a3dStdPackApply(t)", txt)
            before = await safe("()=>window.__a3dStdState()")
            await page.wait_for_timeout(1500)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2000)
            after = await safe("()=>window.__a3dStdState()")
            ck(after == before and after and after.get('place', {}).get('d8') == 'gb-wsm' and await safe("()=>window.__a3dStd('walk.speed','m_min')") == 75 and
               (await ed('tfl.ptal')).get('how') == 'adopted', "a reload keeps the place, the date, the override and the pack")

            # ---------------------------------------------------------------------------------
            print("\n-- 12. A phone, a tablet, a desktop")
            for vw, nm, mob in (((390, 844), 'phone', True), ((820, 1180), 'tablet', True), ((1440, 900), 'desktop', False)):
                c6, p6, e6, w6 = await fresh({}, vw=vw, mobile=mob, lot=False)
                await safe("()=>window.__a3dStdSetPlace({cc:'us',r:'us-pa',city:'Philadelphia'},'hand')", pg=p6)
                await safe("()=>window.__a3dStdCommand()", pg=p6)
                await p6.wait_for_timeout(250)
                await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-propstdact=\"open:tfl.ptal\"]');if(b)b.click();}", pg=p6)
                await p6.wait_for_timeout(150)
                await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-propstdact=\"ov:tfl.ptal|walk_bus\"]');if(b)b.click();}", pg=p6)
                await p6.wait_for_timeout(150)
                gm = await safe("""()=>{var b=document.getElementById('a3d-propsbody'),g=b.querySelector('[data-a3dpgrp="Standards"]'),body=g&&g.nextElementSibling;
                  if(!body)return null;var r=b.getBoundingClientRect(),over=[],small=[];
                  [].forEach.call(body.querySelectorAll('.a3d-prow,.a3d-stdarea,button,select,input'),function(e){var q=e.getBoundingClientRect();if(q.width&&(q.right>r.right+1||q.left<r.left-1))over.push(e.className||e.tagName);});
                  [].forEach.call(body.querySelectorAll('[data-propstdact],select,input'),function(e){var q=e.getBoundingClientRect();if(q.width&&q.height<34)small.push((e.getAttribute('data-propstdact')||e.tagName)+':'+Math.round(q.height));});
                  return {over:over.slice(0,4),small:small.slice(0,4),sw:b.scrollWidth,cw:b.clientWidth,doc:document.documentElement.scrollWidth,vis:r.width>0};}""", pg=p6) or {}
                ck(gm.get('vis') and not gm.get('over') and gm.get('sw', 9) <= gm.get('cw', 0) + 1 and gm.get('doc', 9999) <= vw[0] + 1,
                   "on a %s: the Standards group inside the panel, nothing spilling (%s)" % (nm, {k: gm.get(k) for k in ('over', 'sw', 'cw', 'doc')}))
                if mob:
                    ck(not gm.get('small'), "on a %s its buttons, lists and fields finger-sized (%s)" % (nm, gm.get('small')))
                ck(not e6, "no page error on a %s (%s)" % (nm, e6[:2]))
                await c6.close()
            ck(not errs, "no page error (%s)" % errs[:3])
            ck(not [w_ for w_ in warns if 'standards' in w_.lower() or 'findings could not' in w_], "no warning from the registry (%s)" % warns[:3])
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
