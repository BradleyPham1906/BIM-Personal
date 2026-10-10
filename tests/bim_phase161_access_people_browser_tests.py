#!/usr/bin/env python3
"""bim_phase161_access_people_browser_tests.py -- V161: Site analysis SA4, access and people, and the board.

The free services (Overpass, TIGERweb, the Census Data API) are answered inside the browser by
tests/access_fixture.py, in their own shapes. Every number is worked out again in
tests/access_reference.py another way: a half-metre net beside the lot instead of the app's 5 m,
Python's heapq, numpy for the nearest edge, parks sampled every metre, and the Census Bureau's
formulas written out again.

  1. THE COMMANDS AND THE PANEL: ACCESSGET, ACCESS, WALKTIMES; Site analysis's new section.
  2. THE REQUESTS: one Overpass request (the network, places, parks, stops, routes, radii from the
     lot), TIGERweb and the ACS (the variables, estimates and margins; the year); refusals.
  3. THE WALK: every place's and stop's walk time against the reference; the rules (no motorway, no
     private road unless foot=yes, steps slower, a bridge is not the lot's ground); the bands' lengths;
     no lot, and a lot with no street near it.
  4. PLACES, PARKS, STOPS AND LINES: the kinds, counts, a park's edge and area, a private garden out,
     stops grouped with their lines, the nearest bus and rail.
  5. THE FRONTAGE AND CONNECTIVITY: three streets, their lengths and tags, sidewalks inferred; LEED
     ND's intersections (dead ends off, a divided road once); route directness.
  6. THE PEOPLE: the facts with their margins, the special values, shares by the derived-proportion
     formula (and its ratio fallback), sums, the pyramid, the year falling back, outside the US.
  7. FINDINGS: eight, classed by their references, each with its source and date; one undo step.
  8. THE WALK TIMES LAYER: added once, in Layers under Analysis, drawn on the plan, follows its data.
  9. FAILURES: a source down is named and the rest kept; all down changes nothing; busy; a stopped
     request.
 10. THE BOARD: header, two rows of indicators with states, eight figures with titles, sources and
     tables, the always-shown tables, hover, Esc, the theme, print, the SA panel's stale notes.
 11. A RELOAD, OFFLINE, AND A PHONE.

The harness never waits without a bound (V123).
"""
import asyncio, datetime, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within, near   # noqa: E402
import access_fixture as FX   # noqa: E402
import access_reference as AR   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
HOSTS = ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**',
         'https://tigerweb.geo.census.gov/**', 'https://api.census.gov/**')
TODAY = datetime.date.today()
YEAR = TODAY.year - (1 if TODAY.month == 12 else 2)
TOL = 0.02   # minutes: the app's 5 m net against the reference's half metre


async def run():
    ck = CK
    LOT = [list(p) for p in FX.LOT]
    REF = AR.Ref(AR.Lot(ring=LOT))
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        ST = {'year': YEAR}
        for h in HOSTS:
            await ctx.route(h, FX.route_handler(ST))
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

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

        async def set_site(lat, lon, pg=None):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in (('sunlat', lat), ('sunlon', lon)):
                await safe("""(a)=>{var L=document.querySelectorAll('#a3d-propsbody input'),e=null,i;for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')===a[0])e=L[i];
                  if(!e)return false;e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [k, v], pg=pg)
                await (pg or page).wait_for_timeout(80)

        async def lot(pts, pg=None):
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT';});
              if(a){o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});}
              window.__a3dTestSetObjs(o);if(a)window.__a3dPropertyFromSketch('LOT');}""", pts, pg=pg)

        async def acc(pg=None):
            return await safe("()=>window.__a3dAcc()", pg=pg) or {}

        async def fetch(pg=None):
            return await safe("()=>Promise.resolve(window.__a3dAccFetch())", pg=pg) or {}

        async def fnd(key):
            for f in ((await safe("()=>window.__a3dSa()")) or {}).get('findings', []):
                if f.get('auto') == key:
                    return f
            return None

        def place(A, name):
            for p in A.get('places', []):
                for q in p['near']:
                    if q['n'] == name:
                        return p['k'], q
            return None, None

        def stop(A, name):
            for s in A.get('stops', []):
                if s['n'] == name:
                    return s
            return None

        try:
            has = await safe("()=>window.__acad3dV161")
            ck(bool(has) and 'walktimes' in has and 'census' in has and 'walklayer' in has, "__acad3dV161 marker is present (%s)" % (has or '')[:80])
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 161, "the app says V161 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V161')
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. the commands and the panel")
            for q, want in (('walkability', 'ACCESS'), ('age pyramid', 'ACCESS'), ('census', 'ACCESSGET'), ('isochrone', 'WALKTIMES'),
                            ('transit stops', 'ACCESS'), ('demographics', 'ACCESS'), ('walk shed', 'WALKTIMES')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,6)", q) or [])]
                ck(want in nm[:3], "searching %r finds %s (%s)" % (q, want, nm[:4]))
            await safe("()=>window.__a3dAnzView('site')")
            await page.wait_for_timeout(150)
            sec = await safe("""()=>{var s=document.querySelector('.a3d-sa-wrap [data-accsec]');if(!s)return null;
              return {hd:s.querySelector('.a3d-sasechd').textContent,acts:[].map.call(s.querySelectorAll('[data-saact]'),function(b){return [b.getAttribute('data-saact'),b.textContent];})};}""") or {}
            ck(sec.get('hd') == 'Access and people' and sec.get('acts') == [['accget', 'Get access and people'], ['accboard', 'Open the board']],
               "Site analysis has an Access and people section: Get access and people, Open the board (%s)" % sec)
            order = await safe("()=>[].map.call(document.querySelectorAll('.a3d-sa-wrap .a3d-clsec .a3d-sasechd'),function(h){return h.textContent;})")
            ck(order == ['Climate and risk', 'Zoning and yield', 'Access and people'], "after Climate and risk and Zoning and yield (%s)" % order)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the requests")
            r = await fetch()
            ck(r == {} and 'Set the site latitude and longitude first' in await toast() and not ST.get('hits'), "no place: refused, saying why, nothing asked")
            q = await safe("()=>window.__a3dAccQuery(40,-75,1730,1680)") or ''
            ck(q.startswith('[out:json][timeout:120];') and 'way["highway"](around:1730,40.000000,-75.000000);out body geom qt;' in q,
               "one request: every highway way within the network radius, with its nodes and geometry")
            ck('nwr["shop"~"^(supermarket|greengrocer|bakery|butcher|deli|convenience)$"](around:1680' in q and 'nwr["amenity"~"^(marketplace|pharmacy' in q and
               'out tags center qt' in q and 'node.p;out body qt;' in q, "the places of daily need in the nearer radius, nodes with their points, ways and relations by their centres")
            ck('nwr["leisure"="park"](around:1680,40.000000,-75.000000);out geom qt;' in q, "parks with their outlines, to walk to their edge")
            ck('node["highway"="bus_stop"]' in q and 'node["railway"~"^(station|halt|tram_stop|subway_entrance)$"]' in q and 'node["amenity"="ferry_terminal"]' in q and
               'rel(bn.s)["type"="route"]["route"~"^(bus|trolleybus|tram|subway|light_rail|monorail|train|ferry)$"];out body qt;' in q, "the stops, and the routes that serve them with their members")
            await set_site('40', '-75')
            await lot(LOT)
            U = await safe("(y)=>window.__a3dCenUrls(40,-75,y,{st:'42',co:'101',tr:'007600'})", YEAR) or {}
            ck('/TIGERweb/Tracts_Blocks/MapServer/identify?' in U.get('tract', '') and 'layers=all' in U['tract'] and 'returnGeometry=false' in U['tract'] and 'f=json' in U['tract'] and
               '/TIGERweb/State_County/MapServer/identify?' in U.get('countyState', ''), "TIGERweb's identify at the site: the tract, and the county and state")
            kv = ','.join(v + s for v in FX.VARS.values() for s in ('E', 'M'))
            ck(U.get('acsTract', '').startswith('https://api.census.gov/data/%d/acs/acs5?get=NAME,' % YEAR) and kv in U['acsTract'] and
               U['acsTract'].endswith('&for=tract:007600&in=state:42%20county:101'), "the ACS 5-year for %d: each figure's estimate and margin, for the tract" % YEAR)
            ck(U.get('acsCounty', '').endswith('&for=county:101&in=state:42') and U.get('acsState', '').endswith('&for=state:42') and
               'B01001_003E' in U.get('pyrTract', '') and 'B01001_049E' in U['pyrTract'] and 'B01001_026E' not in U['pyrTract'], "its county and state; the age and sex cells, men 3 to 25, women 27 to 49")
            ck(len(U['acsTract'].split('get=')[1].split('&')[0].split(',')) <= 50 and len(U['pyrTract'].split('get=')[1].split('&')[0].split(',')) <= 50, "each within the API's 50 variables")
            ck(all('key=' not in u.lower() for u in U.values()), "no key in any of them")
            ck(await safe("()=>window.__a3dCenYear()") == YEAR, "the newest 5-year estimates: %d (%d to %d)" % (YEAR, YEAR - 4, YEAR))
            ST['hits'] = []
            r = await fetch()
            ck(r.get('access') and r.get('people') and r.get('errors') == [] and r.get('stops') == 5, "one press: the walk, the stops and the people (%s)" % r)
            H = ST.get('hits', [])
            osm = [h for h in H if '/api/interpreter' in h]
            ck(len(osm) == 1 and len([h for h in H if 'tigerweb' in h]) == 2 and len([h for h in H if 'api.census.gov' in h]) == 5,
               "one Overpass request, two TIGERweb, five ACS (%d, %d, %d)" % (len(osm), len([h for h in H if 'tigerweb' in h]), len([h for h in H if 'api.census.gov' in h])))
            from urllib.parse import unquote
            qq = unquote(osm[0].split('data=')[1]) if osm else ''
            reach = max(math.hypot(x, z) for x, z in FX.LOT)
            ck('(around:%d,40.000000,-75.000000)' % round(1600 + reach + 30 + 50) in qq and '(around:%d,40.000000,-75.000000)' % round(1600 + reach + 30) in qq,
               "its radii from the lot: 20 minutes at 80 m a minute, the lot's reach (%.1f m) and 30 m, and 50 m more for the network" % reach)
            A = (await acc()).get('access') or {}
            P = (await acc()).get('people') or {}

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the walk")
            worst, n = 0.0, 0
            for typ, k, v, name, (x, z) in FX.PLACES:
                rf = REF.point(x, z)
                kk, q2 = place(A, name)
                if rf['t'] <= 20:
                    n += 1
                    worst = max(worst, abs(q2['t'] - rf['t']) if q2 else 99)
                else:
                    ck(q2 is None, "%s, %.1f minutes away, is left out (beyond 20)" % (name, rf['t']))
            ck(n == 14 and worst <= TOL, "every one of the %d places within 20 minutes: its walk time as worked out here, to %.3f min (the worst)" % (n, worst))
            for nm in ('Fresh Market', 'Main Pharmacy', 'Bridge Cafe', 'Bistro'):
                rec = [p for p in FX.PLACES if p[3] == nm][0]
                rf = REF.point(*rec[4])
                ck(place(A, nm)[1] and near(place(A, nm)[1]['t'], rf['t'], TOL), "%s: %.2f min (here %.3f)" % (nm, place(A, nm)[1]['t'] if place(A, nm)[1] else -1, rf['t']))
            mot = AR.Ref(AR.Lot(ring=LOT), walk_motorways=True)
            cl = [p for p in FX.PLACES if p[3] == 'Riverside Clinic'][0][4]
            ck(mot.point(*cl)['t'] < REF.point(*cl)['t'] - 2 and place(A, 'Riverside Clinic')[1] and near(place(A, 'Riverside Clinic')[1]['t'], REF.point(*cl)['t'], TOL),
               "the expressway is no walk: the clinic where it comes down %.2f min away, not the %.2f it would make it" % (REF.point(*cl)['t'], mot.point(*cl)['t']))
            pri = AR.Ref(AR.Lot(ring=LOT), private_walkable=True)
            bis = [p for p in FX.PLACES if p[3] == 'Bistro'][0][4]
            ck(pri.point(*bis)['t'] < REF.point(*bis)['t'] - 0.3 and near(place(A, 'Bistro')[1]['t'], REF.point(*bis)['t'], TOL),
               "nor the private drive: the Bistro %.2f min, not %.2f" % (REF.point(*bis)['t'], pri.point(*bis)['t']))
            nofoot = AR.Ref(AR.Lot(ring=LOT), honour_foot=False)
            ph = [p for p in FX.PLACES if p[3] == 'Main Pharmacy'][0][4]
            ck(nofoot.point(*ph)['t'] > REF.point(*ph)['t'] + 0.3 and near(place(A, 'Main Pharmacy')[1]['t'], REF.point(*ph)['t'], TOL),
               "but Hospital Drive, private with foot=yes, is walked: the pharmacy %.2f min by it, %.2f without" % (REF.point(*ph)['t'], nofoot.point(*ph)['t']))
            fast = AR.Ref(AR.Lot(ring=LOT), steps_slow=False)
            pts = [(p[3], p[4]) for p in FX.PLACES] + [(str(s[0]), s[2]) for s in FX.STOPS]
            quick = [(nm, xz) for nm, xz in pts if fast.point(*xz)['t'] < REF.point(*xz)['t'] - 0.05 and REF.point(*xz)['t'] <= 20]
            app_t = {}
            for nm, xz in pts:
                q2 = place(A, nm)[1]
                if q2:
                    app_t[nm] = q2['t']
            sid = {str(s[0]): s for s in FX.STOPS}
            cs0 = stop(A, 'Central Station')
            if cs0:
                app_t['900006'] = cs0['t']
            hit = [nm for nm, xz in quick if nm in app_t and near(app_t[nm], REF.point(*xz)['t'], TOL)]
            ck(quick and len(hit) == len([nm for nm, xz in quick if nm in app_t]) and hit,
               "Hill Steps at half speed: %d walks they would shorten at a full pace are not shortened (%s)" % (len(quick), [(nm, round(fast.point(*xz)['t'], 2), round(REF.point(*xz)['t'], 2)) for nm, xz in quick][:2]))
            bri = AR.Ref(AR.Lot(ring=LOT), seed_bridges=True)
            bc = [p for p in FX.PLACES if p[3] == 'Bridge Cafe'][0][4]
            ck(bri.point(*bc)['t'] < REF.point(*bc)['t'] - 0.2 and near(place(A, 'Bridge Cafe')[1]['t'], REF.point(*bc)['t'], TOL),
               "the footbridge over the lot is not the ground it opens onto: the Bridge Cafe %.2f min, not %.2f" % (REF.point(*bc)['t'], bri.point(*bc)['t']))
            ck(A.get('start', {}).get('far') is False and A['start']['n'] > 20 and near(A['start']['d'], 5, 0.01),
               "the walk starts at the lot line: %d starts within 30 m, the nearest 5 m away (the sidewalk)" % A.get('start', {}).get('n', 0))
            RB = REF.band_lengths()
            got = [x * 1000 for x in A.get('reach', {}).get('len', [])]
            ck(len(got) == 4 and all(abs(g - r) <= 0.006 * r + 5 for g, r in zip(got, RB)),
               "streets and paths reached in each band, as worked out here: %s m (here %s)" % ([round(g) for g in got], [round(r) for r in RB]))
            cls = A.get('reach', {}).get('cls', {})
            ck('w' not in cls and set(cls) == {'a', 'c', 'l', 's', 'p'} and all(near(sum(cls[c][k] for c in cls), A['reach']['len'][k], 0.006) for k in range(4)),
               "by class, adding up to each band; the sidewalks and crossings walked but not counted (%s)" % sorted(cls))
            segs = A.get('segs', [])
            ck(segs and all(s[0] in 'aclsp' and (len(s) - 1) % 3 == 0 and len(s) >= 7 for s in segs) and max(t for s in segs for t in s[3::3]) <= 20.0001,
               "the network drawn as %d lines of [class, x, z, minutes ...], to 20 minutes and no further" % len(segs))
            ck(all(s[0] != 'w' for s in segs), "sidewalks and crossings not drawn")
            drawn = [0.0, 0.0, 0.0, 0.0]
            for g in segs:
                for j in range(4, len(g) - 2, 3):
                    x1, z1, t1, x2, z2, t2 = g[j - 3:j + 3]
                    cuts = sorted([0, 1] + [(T - t1) / (t2 - t1) for T in (5, 10, 15) if (t1 - T) * (t2 - T) < 0])
                    L = math.hypot(x2 - x1, z2 - z1)
                    for a, b in zip(cuts, cuts[1:]):
                        tm = t1 + (a + b) / 2 * (t2 - t1)
                        drawn[0 if tm <= 5 else (1 if tm <= 10 else (2 if tm <= 15 else 3))] += (b - a) * L
            ck(all(abs(d - r * 1000) <= 0.01 * r * 1000 + 5 for d, r in zip(drawn, A['reach']['len'])),
               "and the lines drawn, cut where they cross 5, 10 and 15 minutes, are the reach in each band: %s m" % [round(d) for d in drawn])
            sz = len(json.dumps(A))
            ck(sz < 60000, "kept small enough to save with the project: %d bytes" % sz)
            # no lot: the site's point
            await lot(None)
            W0 = await safe("(j)=>window.__a3dAccWork(j)", FX.overpass()) or {}
            R0 = AR.Ref(AR.Lot(ring=None, pt=(0.0, 0.0)))
            w0 = max(abs(place(W0, nm)[1]['t'] - R0.point(*p[4])['t']) for p in FX.PLACES for nm in [p[3]] if R0.point(*p[4])['t'] <= 20 and place(W0, nm)[1])
            ck(W0.get('lot', {}).get('ring') is None and W0.get('streets') == [] and worst <= TOL and w0 <= TOL,
               "with no property line, the walk starts at the site's point: every place as worked out here, to %.3f min; no frontage" % w0)
            mid = [[115, -156], [125, -156], [125, -146], [115, -146]]
            await lot(mid)
            W1 = await safe("(j)=>window.__a3dAccWork(j)", FX.overpass()) or {}
            R1 = AR.Ref(AR.Lot(ring=mid))
            w1 = max(abs(place(W1, p[3])[1]['t'] - R1.point(*p[4])['t']) for p in FX.PLACES if R1.point(*p[4])['t'] <= 20 and place(W1, p[3])[1])
            ck(W1.get('start', {}).get('far') is True and near(W1['start']['d'], 44, 0.01) and near(R1.far, 44, 0.01) and w1 <= TOL,
               "a lot in the middle of a block, no street within 30 m: the walk starts 44 m away where the nearest comes nearest (to %.3f min)" % w1)
            await lot(LOT)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. places, parks, stops and lines")
            K = {p['k']: p for p in A.get('places', [])}
            ck(list(K) == ['food', 'health', 'learn', 'parks', 'eat', 'services', 'community'], "seven kinds, in order (%s)" % list(K))
            ref_n = {}
            for typ, k, v, name, (x, z) in FX.PLACES:
                kd = {'supermarket': 'food', 'convenience': 'food', 'bakery': 'food', 'pharmacy': 'health', 'hospital': 'health', 'clinic': 'health', 'school': 'learn', 'library': 'learn',
                      'playground': 'parks', 'cafe': 'eat', 'restaurant': 'eat', 'fast_food': 'eat', 'bank': 'services', 'post_office': 'services', 'place_of_worship': 'community'}[v]
                t = REF.point(x, z)['t']
                ref_n.setdefault(kd, []).append(t)
            ref_n.setdefault('parks', []).extend([REF.ring_time(FX.PARK), REF.ring_time(FX.COMMONS_OUT)])
            cnt = {k: [sum(1 for t in L if t <= b) for b in (5, 10, 15, 20)] for k, L in ref_n.items()}
            cnt['community'] = cnt.get('community', [0, 0, 0, 0])
            ck(all(K[k]['n'] == cnt[k] for k in K), "how many of each within 5, 10, 15 and 20 minutes, as worked out here (%s)" % {k: K[k]['n'] for k in K})
            ck(K['community']['near'] == [] and K['community']['n'] == [0, 0, 0, 0], "no community or worship within 20 minutes: the chapel is %.1f away" % ref_n['community'][0])
            pk = place(A, 'Riverside Park')[1]
            cm = place(A, 'The Commons')[1]
            ck(pk and near(pk['t'], REF.ring_time(FX.PARK), TOL) and cm and near(cm['t'], REF.ring_time(FX.COMMONS_OUT), TOL),
               "a park's walk is to the nearest point of its edge: Riverside Park %.2f, the Commons %.2f min" % (REF.ring_time(FX.PARK), REF.ring_time(FX.COMMONS_OUT)))
            cen_t = REF.point(-480, 250)['t']
            ck(pk and pk['a'] == 1.0 and cm and cm['a'] == 0.8 and cm['t'] < cen_t - 0.5,
               "with their areas: 1.0 ha, and 0.8 ha for the Commons, its hole taken off; not to its centre (%.2f min)" % cen_t)
            ck(place(A, 'Private Garden')[1] is None, "a private garden is not a park to walk to")
            names = [s['n'] for s in A.get('stops', [])]
            ck(names == ['Market St & 5th St', 'Market St & 3rd St', 'Library Tram', 'Stop B7', 'Central Station'], "the stops by walk time, grouped (%s)" % names)
            ms = stop(A, 'Market St & 5th St')
            mt = min(REF.point(*s[2])['t'] for s in FX.STOPS[:3])
            ck(ms and ms['m'] == ['bus'] and ms['l'] == [['bus', '12'], ['bus', '42']] and near(ms['t'], mt, TOL),
               "the two sides of Market Street and its stop position, one stop: buses 12 and 42 (12 once, though it runs both ways), %.2f min" % mt)
            cs = stop(A, 'Central Station')
            ck(cs and cs['m'] == ['metro'] and cs['l'] == [['metro', 'A']] and near(cs['t'], REF.point(*FX.STOPS[5][2])['t'], TOL) and
               REF.point(*FX.STOPS[4][2])['t'] > cs['t'] + 1, "Central Station: line A, reached at its nearest entrance (%.2f min), not its platform (%.2f)" % (cs['t'], REF.point(*FX.STOPS[4][2])['t']))
            ck(stop(A, 'Stop B7') and stop(A, 'Stop B7')['l'] == [['bus', '7']] and stop(A, 'Library Tram')['m'] == ['tram'] and stop(A, 'Library Tram')['l'] == [['tram', 'T1']],
               "an unnamed stop by its ref; the tram stop with its line")
            ck(stop(A, 'Northside Halt') is None and REF.point(*FX.STOPS[9][2])['t'] > 20, "the halt %.1f minutes away is left out" % REF.point(*FX.STOPS[9][2])['t'])
            ck(A.get('bus') == 0 and A.get('rail') == 4 and A.get('lines10') == 4, "the nearest bus or tram: Market St & 5th St; the nearest rail or metro: Central Station; 4 lines within 10 minutes")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the frontage and connectivity")
            F = A.get('streets', [])
            ck([(f['n'], f['c'], f['len'], f['d']) for f in F] == [('Market Street', 'a', 40, 10), ('', 's', 40, 10), ('5th Street', 'c', 30, 10)],
               "the lot fronts Market Street (40 m), an alley behind (40 m) and 5th Street (30 m), each 10 m off; nothing on its fourth side (%s)" % [(f['n'], f['len']) for f in F])
            ck(F and F[0]['sp'] == '30 mph' and F[0]['ln'] == '4' and F[0]['sw'] == 'both' and F[0]['cy'] == 'lane' and F[1]['sv'] == 'alley',
               "with their tags: 30 mph, 4 lanes, sidewalks on both sides, a cycle lane; the alley known as one")
            ck(len(F) == 3 and F[2]['sw'] == 'separate', "5th Street's sidewalks, untagged on it, found mapped beside it")
            ck(all(len(f['pcs']) == 1 and abs(sum(math.hypot(p[2] - p[0], p[3] - p[1]) for p in f['pcs']) - f['len']) < 0.2 for f in F),
               "each frontage drawn along the lot line, as long as it says")
            IX = REF.intersections()
            C = A.get('conn', {})
            area = (AR.Lot(ring=LOT).area() + AR.Lot(ring=LOT).perim() * 400 + math.pi * 400 ** 2) / 1e6
            ck(C.get('ix') == len(IX) == 48 and near(C['area'], area, 0.001) and near(C['dens'], len(IX) / area, 0.06) and near(C['sqmi'], len(IX) / area * 2.589988, 0.06),
               "%d intersections within 400 m of the lot, as LEED ND counts them, in %.3f km² (the lot and 400 m round it): %.1f per km², %.1f per square mile" % (len(IX), area, len(IX) / area, len(IX) / area * 2.589988))
            ck(not any(abs(p[0] - 240) < 1 and abs(p[1] + 100) < 1 for p in C.get('pts', [])) and not any(abs(p[0] - 240) < 1 and abs(p[1] + 150) < 1 for p in C.get('pts', [])),
               "Elm Court's junctions, leading only to dead ends, are not counted")
            dv = [p for p in C.get('pts', []) if 290 < p[1] < 310]
            ck(len(dv) == 5 and all(abs(p[1] - 300) < 0.2 for p in dv) and sum(1 for p in IX if p[2] == 2) == 5,
               "Broad Avenue's two carriageways: each crossing counted once, at its middle (%d)" % len(dv))
            rats = []
            for typ, k, v, name, (x, z) in FX.PLACES:
                kd, q2 = place(A, name)
                if q2 and q2['d'] >= 150:
                    rats.append(q2['t'] * 80 / q2['d'])
            for p in ('Riverside Park', 'The Commons'):
                q2 = place(A, p)[1]
                if q2['d'] >= 150:
                    rats.append(q2['t'] * 80 / q2['d'])
            for s in A.get('stops', []):
                if s['d'] >= 150:
                    rats.append(s['t'] * 80 / s['d'])
            rats.sort()
            med = (rats[len(rats) // 2] if len(rats) % 2 else (rats[len(rats) // 2 - 1] + rats[len(rats) // 2]) / 2) if rats else None
            ck(C.get('ndir') == len(rats) and med and near(C['dir'], med, 0.011) and 1.0 < C['dir'] < 1.6 and len(C.get('rats', [])) == len(rats),
               "route directness: the median of %d walks over the straight line, %.2f (a grid's)" % (len(rats), med or 0))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the people")
            ck(P.get('year') == YEAR and P.get('src') == 'U.S. Census Bureau, American Community Survey 5-year estimates, %d–%d' % (YEAR - 4, YEAR),
               "the ACS 5-year, %d to %d, credited" % (YEAR - 4, YEAR))
            G = P.get('geo', {})
            ck(G.get('tract') == {'name': 'Census Tract 76', 'geoid': '42101007600', 'aland': 1207431} and G['county'] == {'name': 'Sample County', 'geoid': '42101', 'aland': 347520037} and
               G['state'] == {'name': 'Sample State', 'geoid': '42', 'aland': 115881784866}, "the tract, county and state named by TIGERweb, with their land areas (the blocks' layers passed over)")
            ok = all(P.get('v', {}).get(g) == AR.facts(g) for g in ('tract', 'county', 'state'))
            ck(ok, "every figure for the three, its estimate and margin, as sent")
            ck(P['v']['county']['pop'] == [1584000, 0] and P['v']['county']['hhs'] == [None, None],
               "the ACS's special values: a controlled total's margin is 0; an estimate it could not make, none")
            ck(P.get('pyr', {}).get('tract') == AR.pyramid('tract') and P['pyr'].get('county') == AR.pyramid('county'), "the age pyramid's 18 bands, men and women, from B01001's 46 cells, for the tract and the county")
            T = P['v']['tract']
            sh = await safe("(a)=>window.__a3dCenShare(a[0],a[1])", [T['rent'], T['ten']]) or [0, 0]
            p, m = AR.share(T['rent'], T['ten'])
            ck(near(sh[0], p, 1e-12) and near(sh[1], m, 1e-12) and near(sh[1], math.sqrt(160 ** 2 - (1305 / 2105) ** 2 * 150 ** 2) / 2105, 1e-12),
               "a share's margin by the Census Bureau's derived-proportion formula: renting %.1f%% ± %.1f" % (p * 100, m * 100))
            sh2 = await safe("(a)=>window.__a3dCenShare(a[0],a[1])", [[90, 40], [100, 60]]) or [0, 0]
            ck(near(sh2[1], math.sqrt(40 ** 2 + 0.9 ** 2 * 60 ** 2) / 100, 1e-12), "and where the term under the root is negative, the formula for a ratio (%.4f)" % sh2[1])
            sm = await safe("(a)=>window.__a3dCenSum(a)", [T['wlk'], T['bik']]) or [0, 0]
            ck(sm[0] == 322 and near(sm[1], math.hypot(70, 45), 1e-9), "a sum's margin: the root of the sum of the squares (walk and bike %d ± %.1f)" % (sm[0], sm[1]))
            ST['mode'] = {'acsnew': '404'}
            ST['years'] = []
            r = await fetch()
            P2 = (await acc()).get('people') or {}
            ck(r.get('people') and P2.get('year') == YEAR - 1 and ST['years'] and set(ST['years']) == {YEAR - 1},
               "%d's estimates not out yet (HTTP 404): the year before's, %d, asked for everything" % (YEAR, YEAR - 1))
            ST['mode'] = {}
            await fetch()
            # outside the US
            await set_site('51.5', '-0.12')
            ST['hits'] = []
            r = await fetch()
            ck(r.get('outside') and r.get('access') and not [h for h in ST['hits'] if 'census.gov' in h], "a site outside the US: the walk as ever, and no census request at all")
            ck((await acc()).get('people', {}).get('outside') is True, "the people's record says so")
            await set_site('40', '-75')
            ST['mode'] = {'tracts': 'none'}
            r = await fetch()
            ck(r.get('outside') and r.get('access'), "where TIGERweb finds no tract (offshore, say), the same")
            ST['mode'] = {}
            r = await fetch()
            ck(r.get('people') and r.get('errors') == [], "and back")
            A = (await acc()).get('access') or {}
            P = (await acc()).get('people') or {}

            # ---------------------------------------------------------------------------------
            print("\n-- 7. findings")
            keys = ['access.walk', 'access.transit', 'access.frontage', 'access.connectivity', 'people.daily', 'people.population', 'people.households', 'people.mobility']
            Fd = [await fnd(k) for k in keys]
            ck(all(Fd) and all(f['source'] and re.match(r'^\d{4}-\d{2}-\d{2}$', f['date']) for f in Fd), "eight findings, each with its source and date")
            ck([f['cat'] for f in Fd] == ['access'] * 4 + ['people'] * 4, "under Access and circulation, and People and place")
            ck(Fd[0]['value'].startswith('Along the streets from the lot at 4.8 km/h: 5 minutes reach %s km' % ('%.1f' % (A['reach']['len'][0]))) and 'ODbL' in Fd[0]['source'],
               "the walk, with its reach (%s)" % Fd[0]['value'][:90])
            ck(Fd[1]['cls'] == 'opportunity' and 'Market St & 5th St, under a minute (12, 42)' in Fd[1]['value'] and 'Central Station, 11 min (A)' in Fd[1]['value'] and 'GTFS' in Fd[1]['value'],
               "transit: an opportunity, a stop within 5 minutes; how often, the timetable's to say")
            ck(Fd[2]['cls'] == 'constraint' and Fd[2]['sev'] == 1 and Fd[2]['value'].startswith('The lot fronts Market Street (arterial, 30 mph, 4 lanes, sidewalks on both sides, cycleway lane) for 40 m; an unnamed alley for 40 m; 5th Street'),
               "the frontage: an arterial's, a constraint to plan for (%s)" % Fd[2]['value'][:120])
            ck(Fd[3]['cls'] == 'neutral' and 'LEED ND' in Fd[3]['value'] and '48 intersections within 400 m of the lot' in Fd[3]['value'], "connectivity, against LEED ND")
            ck(Fd[4]['cls'] == 'opportunity' and Fd[4]['value'].startswith('6 of 7 kinds within a 10-minute walk') and 'community and worship none within 20 min' in Fd[4]['value'],
               "daily needs: 6 of 7 within 10 minutes, an opportunity, the missing one named")
            ck('Census Tract 76, Sample County, Sample State: 4,512 (± 380) people, 3,737 per km²; median age 34.1 (± 2.3)' == Fd[5]['value'], "who lives here, with the margins (%s)" % Fd[5]['value'])
            ck('62% (± 6) rent' in Fd[6]['value'] and '$72,400 (± $8,100)' in Fd[6]['value'] and "county's $57,500" in Fd[6]['value'], "households, renting, income against the county")
            ck(Fd[7]['cls'] == 'opportunity' and Fd[7]['value'].startswith('38% (± 6) of households have no car; of 2,300 workers, 30% drove alone') and '45% transit' in Fd[7]['value'],
               "how people move: no car, and the commute, an opportunity for less parking")
            now = await acc()
            await safe("()=>window.__a3dUndo()")
            back = await acc()
            ck(back.get('people', {}).get('outside') is True and back.get('access') and await fnd('people.population') is None and await fnd('access.walk'),
               "one undo takes the last fetch back, whole: the people return to the record before it (no tract), and their findings go")
            await safe("()=>window.__a3dRedo()")
            ck(await acc() == now and await fnd('people.population'), "redo returns them")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. the walk times layer")
            L = [x for x in (await safe("()=>window.__a3dResultLayers()") or []) if x['kind'] == 'walk']
            ck(len(L) == 1 and L[0]['name'] == 'Walk times' and L[0]['src'] == 'access' and L[0]['visible'] and not L[0]['stale'] and not L[0]['gone'],
               "the walk times became one layer, though fetched again and again: Walk times, shown, never out of date (%s)" % L)
            wid = L[0]['id'] if L else None
            ck(wid in (await safe("()=>window.__a3dResultDrawn()") or []), "drawn on the plan")
            await safe("()=>window.__a3dResultLayerAdd('walk')")
            ck('a layer already' in await toast() and len([x for x in await safe("()=>window.__a3dResultLayers()") if x['kind'] == 'walk']) == 1, "a second is refused, saying where the first is")
            await safe("(i)=>window.__a3dResultLayerUpdate(i)", wid)
            ck('follows the access data' in await toast(), "Update: it follows the access data")
            await page.click('#a3d-rail [data-tab="layers"]')
            await page.wait_for_timeout(250)
            await safe("(k)=>{if(document.querySelector('#a3d-leftpanel [data-lyresd=\"'+k+'\"]'))return;var e=document.querySelector('#a3d-leftpanel [data-lyres=\"'+k+'\"]');if(e)e.click();}", 'res:' + wid)
            await page.wait_for_timeout(200)
            row = await safe("""(k)=>{var d=document.querySelector('#a3d-leftpanel [data-lyresd="'+k+'"]');if(!d)return null;
              return {leg:[].map.call(d.querySelectorAll('.a3d-lyleg span'),function(s){return s.textContent;}),meta:(d.querySelector('.a3d-lyresmeta')||{}).textContent,upd:!!d.querySelector('[data-lyresupd]'),
                sec:d.closest('[data-lysec]').getAttribute('data-lysec')};}""", 'res:' + wid) or {}
            ck(row.get('sec') == 'analysis' and row.get('leg') == ['5 min or less', '5 to 10 min', '10 to 15 min', 'Bus or tram stop', 'Rail or metro'] and not row.get('upd') and
               'from OpenStreetMap data of' in (row.get('meta') or ''), "in Layers under Analysis: its legend, what it shows, no Update button (%s)" % row)
            await safe("(i)=>window.__a3dResultLayerRemove(i)", wid)
            ck(not [x for x in await safe("()=>window.__a3dResultLayers()") if x['kind'] == 'walk'], "removed")
            await safe("()=>window.__a3dRunCmd('walktimes')")
            L = [x for x in (await safe("()=>window.__a3dResultLayers()") or []) if x['kind'] == 'walk']
            ck(len(L) == 1, "WALKTIMES puts it back")
            wid = L[0]['id'] if L else None
            v = await safe("(i)=>window.__a3dResultLayersValid([{id:i,name:'Walk times',kind:'walk',src:'access'},{id:'x',name:'x',kind:'walk',src:'other'}])", wid)
            ck(v == [wid], "a saved walk layer is read back; a bad one let go")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. failures")
            before = await acc()
            ST['mode'] = {'osm': 'abort'}
            r = await fetch()
            ck(r.get('access') is False and r.get('people') and all(any(h in e for e in r.get('errors', [])) for h in ('overpass-api.de', 'overpass.kumi.systems')),
               "Overpass down, every server tried and named; the people still come (%s)" % (r.get('errors') or [])[:2])
            ck((await acc()).get('access') == before.get('access'), "and the walk times got before are kept, not wiped")
            ck('Not available: overpass-api.de' in await toast(), "and said")
            ST['mode'] = {'osm': 'remark'}
            r = await fetch()
            ck(r.get('access') is False and any('stopped short' in e for e in r.get('errors', [])), "a request that stopped short (Overpass's remark) is not taken as an empty neighbourhood")
            ST['mode'] = {'osm': 'empty'}
            r = await fetch()
            ck(r.get('access') is False and any('no streets or paths came back' in e for e in r.get('errors', [])), "nor is an answer without streets")
            ST['mode'] = {'tracts': 'abort'}
            r = await fetch()
            ck(r.get('access') and r.get('people') is False and any('tigerweb.geo.census.gov could not be reached' in e for e in r.get('errors', [])), "TIGERweb down: named, the walk kept")
            ST['mode'] = {'pyr': 'abort'}
            r = await fetch()
            P3 = (await acc()).get('people') or {}
            ck(r.get('people') and P3.get('pyr') == {} and P3.get('v', {}).get('tract') and any('api.census.gov' in e for e in P3.get('errors', [])), "the age cells down: the facts kept, the pyramid left out, named")
            ST['mode'] = {'osm': '429', 'tracts': 'abort', 'counties': 'abort'}
            before = await acc()
            r = await fetch()
            ck(r.get('error') and 'busy (HTTP 429)' in r['error'] and await acc() == before, "all down: nothing changes, each failure named (%s)" % (r.get('error') or '')[:80])
            ST['mode'] = {}
            await safe("()=>{window.__a3dAccFetch();}")
            ck(await safe("()=>window.__a3dAccFetch()") is None and 'already on their way' in await toast(), "a second press while one runs: refused")
            for _ in range(60):
                if not await safe("()=>window.__a3dAccBusy()"):
                    break
                await page.wait_for_timeout(100)
            r = await fetch()
            ck(r.get('access') and r.get('people') and r.get('errors') == [], "and all well again")
            A = (await acc()).get('access') or {}
            P = (await acc()).get('people') or {}

            # ---------------------------------------------------------------------------------
            print("\n-- 10. the board")
            await safe("()=>window.__a3dAnzView('site')")
            await page.wait_for_timeout(150)
            sec = await safe("""()=>{var s=document.querySelector('.a3d-sa-wrap [data-accsec]');return s?{txt:s.querySelector('.a3d-clsum').textContent,acts:[].map.call(s.querySelectorAll('[data-saact]'),function(b){return [b.getAttribute('data-saact'),b.disabled];})}:null;}""") or {}
            ck(sec.get('txt', '').startswith('6 of 7 daily needs within 10 min · bus under a minute · rail 11 min · 86 intersections per km² · Census Tract 76: 4,512 people. Data of ') and
               sec.get('acts') == [['accboard', False], ['acclayer', True], ['accget', False]], "the section says what is known; the layer button off while the layer is there (%s)" % sec)
            await safe("()=>document.querySelector('.a3d-sa-wrap [data-saact=\"accboard\"]').click()")
            await page.wait_for_timeout(300)
            B = await safe("""()=>{var b=document.querySelector('.a3d-clb');if(!b)return null;
              return {h1:b.querySelector('.a3d-clb-h1').textContent,sub:b.querySelector('.a3d-clb-sub').textContent,kick:b.querySelector('.a3d-clb-kicker').textContent,label:b.getAttribute('aria-label'),
                kh:[].map.call(b.querySelectorAll('.a3d-acc-kh'),function(k){return k.textContent;}),
                kpis:[].map.call(b.querySelectorAll('.a3d-clb-kpi'),function(k){var s=k.querySelector('.a3d-clb-st');return [k.querySelector('.a3d-clb-kl').textContent,k.querySelector('.a3d-clb-kv').textContent,s?s.textContent:null,s?!!s.querySelector('svg'):null];}),
                figs:[].map.call(b.querySelectorAll('.a3d-clb-card[data-fig]'),function(c){return {no:c.getAttribute('data-fig'),t:c.querySelector('.a3d-clb-h2').textContent,svg:c.querySelectorAll('svg[role="img"]').length,
                  src:!!c.querySelector('.a3d-clb-src'),tbl:!!c.querySelector('.a3d-clb-table'),cls:c.className};}),
                secs:[].map.call(b.querySelectorAll('.a3d-acc-sec'),function(s){return s.textContent;}),cols:b.querySelectorAll('.a3d-acc-col').length,
                notes:b.querySelector('.a3d-clb-notes')?b.querySelector('.a3d-clb-notes').textContent:'',open:document.body.classList.contains('a3d-clb-open')};}""") or {}
            ck(B.get('open') and B.get('label') == 'Access and people board' and B.get('h1', '').endswith(': access and people') and B['kick'] == 'Site analysis · 8 Access and circulation · 10 People and place',
               "the Access and people board opens from Site analysis, in the Climate board's frame")
            ck('40.0000° N, 75.0000° W' in B.get('sub', '') and 'walking at 4.8 km/h from the lot' in B['sub'] and 'Census Tract 76, Sample County · ACS %d–%d' % (YEAR - 4, YEAR) in B['sub'],
               "its header: the place, the walk, the data's date, the tract and the ACS years (%s)" % B.get('sub'))
            ck(B.get('kh') == ['Access and circulation', 'People and place · Census Tract 76'], "two rows of indicators, access and the people")
            kl = [k[0] for k in B.get('kpis', [])]
            ck(kl == ['Daily needs', 'Nearest bus or tram', 'Nearest rail or metro', 'Lines within 10 min', 'Intersections', 'Population', 'Median age', 'Household income', 'Renting', 'No car'],
               "ten indicators, in reading order (%s)" % kl)
            kv = {k[0]: k[1:] for k in B.get('kpis', [])}
            ck(kv['Daily needs'][:2] == ['6 of 7', 'Good'] and kv['Nearest bus or tram'][:2] == ['<1min', 'Good'] and kv['Nearest rail or metro'][:2] == ['11min', 'Watch'] and
               kv['Intersections'][:2] == ['86per km²', 'Good'] and kv['Lines within 10 min'][1] is None, "states where a reference exists: daily needs, the stops, intersections against LEED ND (%s)" % kv)
            ck(all(v[2] for v in kv.values() if v[1]), "each state an icon and a word, never colour alone")
            ck(kv['Population'][0] == '4,512' and kv['Household income'][0] == '$72,400median' and kv['Renting'][0] == '62%' and kv['No car'][0] == '38%' and
               all(kv[k][1] is None for k in ('Population', 'Median age', 'Household income', 'Renting', 'No car')), "the people's, with no state: a fact is not good or bad")
            figs = B.get('figs', [])
            ck([f['no'] for f in figs] == [str(i) for i in range(1, 9)] and all(f['svg'] >= 1 and f['src'] and f['tbl'] for f in figs),
               "eight figures, numbered, each with its chart, its source and a table")
            ck(all(re.search(r'\d', f['t']) for f in figs), "every title states a finding with its number (%s)" % [f['t'][:40] for f in figs])
            ck(figs and figs[0]['t'] == 'A 10-minute walk reaches %.1f km of streets and 6 of 7 daily needs' % (A['reach']['len'][0] + A['reach']['len'][1]) and
               figs[2]['t'] == 'The lot fronts Market Street, an arterial; an alley; and 5th Street, a collector' and
               figs[3]['t'] == 'The nearest bus or tram stop is under a minute away; 4 lines within 10 minutes', "Fig. 1, 3 and 4 say it in words")
            ck(figs[4]['t'].startswith('86 intersections per km² (222 per square mile): meets LEED ND') and figs[5]['t'].startswith('Census Tract 76: to work by transit 45% against 25% in the county; 7 of 9 measures differ'),
               "Fig. 5 against LEED ND; Fig. 6 the tract's largest difference from its county, and how many differ beyond the margins (%s)" % figs[5]['t'][:70])
            ck(B.get('secs') == ['8 · Access and circulation', '10 · People and place'] and B.get('cols') == 2, "two sections, as in Site analysis; a wide figure beside a column of two, twice")
            ck('ODbL' in B.get('notes', '') and 'LEED ND v4' in B['notes'] and 'derived proportion' in B['notes'] and 'not a Walk Score' in B['notes'], "the notes: method and sources, credits")
            M = await safe("""()=>{var s=document.querySelector('[data-accmap="walk"]');if(!s)return null;
              return {bands:[].map.call(s.querySelectorAll('path[data-band]'),function(p){return p.getAttribute('data-band')+p.getAttribute('data-cls');}),
                crow:[].map.call(s.querySelectorAll('[data-crow]'),function(c){return c.getAttribute('data-crow');}),stops:s.querySelectorAll('[data-accstop]').length,
                places:[].map.call(s.querySelectorAll('[data-accplace]'),function(p){return p.getAttribute('data-accplace');}),lot:s.querySelectorAll('polygon').length,ov:s.style.overflow,
                north:s.textContent.indexOf('N')>=0};}""") or {}
            ck(set(b[0] for b in M.get('bands', [])) == {'0', '1', '2', '3'} and M.get('crow') == ['400', '800'] and M.get('lot') == 1,
               "Fig. 1, the walk-time map: the rings and the grey beyond, 400 and 800 m as the crow flies, the lot")
            ck(M.get('stops') == len([s for s in A['stops'] if s['t'] <= 15]) and M.get('places') == [p['k'] for p in A['places'] if p['near'] and p['near'][0]['t'] <= 15] and M.get('ov') == 'hidden',
               "the stops within 15 minutes and the nearest of each daily need, clipped to its frame")
            nt = await safe("()=>[].map.call(document.querySelectorAll('[data-accnearest] tr'),function(r){return [].map.call(r.children,function(c){return c.textContent;});})") or []
            tcs = REF.point(*[p for p in FX.PLACES if p[3] == 'Corner Shop'][0][4])['t']
            ck(len(nt) == 7 and nt[0] == ['Food shopping', 'Corner ShopConvenience store', '<1 min' if tcs < 0.5 else '%d min' % math.floor(tcs + 0.5)] and nt[6][2] == '—',
               "Fig. 2's nearest of each kind, shown without asking (%s)" % nt[:2])
            ft = await safe("()=>[].map.call(document.querySelectorAll('[data-accfronttable] tbody tr'),function(r){return [].map.call(r.children,function(c){return c.textContent;});})") or []
            ck(ft == [['Market Streetprimary', 'Arterial', '40 m', '30 mph', '4', 'Both sides', 'lane'], ['Unnamed alleyservice', 'Alley', '40 m', '—', '—', '—', '—'],
                      ['5th Streetsecondary', 'Collector', '30 m', '25 mph', '2', 'Mapped separately', '—']], "Fig. 3's frontage table, shown without asking (%s)" % ft)
            sm2 = await safe("""()=>{var s=document.querySelector('[data-accmap="streets"]');return s?{front:s.querySelectorAll('[data-accfront]').length,ix:s.querySelectorAll('[data-accix]').length,
              buf:!!s.querySelector('[data-buffer="400"]'),cls:[].map.call(s.querySelectorAll('path[data-cls]'),function(p){return [p.getAttribute('data-cls'),+p.getAttribute('stroke-width')];})}:null;}""") or {}
            wd = dict(sm2.get('cls', []))
            ck(sm2.get('front') == 3 and sm2.get('ix') == 48 and sm2.get('buf') and wd.get('a', 0) > wd.get('c', 0) > wd.get('l', 0) > wd.get('s', 9),
               "Fig. 3's map: the frontage, the 48 intersections counted, the 400 m line, line weight by class (%s)" % wd)
            facts = await safe("()=>[].map.call(document.querySelectorAll('[data-accfacts] tbody tr'),function(r){return [].map.call(r.children,function(c){return c.textContent;});})") or []
            ck(facts and facts[0] == ['People', '4,512± 380', '1,584,000', '12,990,000'] and facts[-1] == ['Land area, km²', '1.21', '348', '115,882'],
               "Fig. 6's key facts with their margins, shown without asking (%s)" % facts[:1])
            geo = await safe("()=>{var c=document.querySelector('.a3d-clb-card[data-fig=\"6\"]');return [c.querySelectorAll('[data-accgeo=\"tract\"]').length,c.querySelectorAll('[data-accgeo=\"county\"]').length,c.querySelectorAll('[data-accgeo=\"state\"]').length,c.querySelectorAll('[data-accmoe]').length];}")
            ck(geo == [10, 9, 10, 10], "Fig. 6: ten measures, the tract with its margin on each; the county's household size, which the ACS could not make, left out (%s)" % geo)
            com = await safe("()=>[].map.call(document.querySelectorAll('[data-acccom]'),function(r){return r.getAttribute('data-acccom');})") or []
            ck(len(com) == 21 and com[:7] == ['tract:%d' % j for j in range(7)], "Fig. 7: the seven means for the tract, its county and its state (%d bars)" % len(com))
            fill = await safe("()=>[].map.call(document.querySelectorAll('[data-acccom^=\"tract:\"]'),function(r){return r.getAttribute('fill');})")
            ck(fill == ['var(--s%d)' % (j + 1) for j in range(7)], "in the categorical order, slots 1 to 7, never cycled")
            py = await safe("()=>[document.querySelectorAll('[data-accpyr]').length,document.querySelectorAll('[data-acccounty]').length]")
            ck(py == [36, 2], "Fig. 8: 18 bands for men and women, the county's outline on each side")
            tips = await safe("()=>document.querySelectorAll('.a3d-clb [data-tip]').length") or 0
            ck(tips > 60, "a tooltip on every mark (%d)" % tips)
            box = await safe("()=>{var e=document.querySelector('[data-accnear=\"food\"]');e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}")
            await page.mouse.move(box[0], box[1])
            await page.wait_for_timeout(120)
            tip = await safe("()=>{var t=document.querySelector('.a3d-clb-tip');return t.hidden?null:t.textContent;}") or ''
            ck(tip.startswith('Corner Shop') and 'Nearest food shopping: Convenience store' in tip and 'min on foot' in tip, "hover the nearest food: its name, kind and walk (%s)" % tip)
            ck(await safe("()=>getComputedStyle(document.querySelector('.a3d-clb-card[data-fig=\"1\"] .a3d-clb-table')).display") == 'none', "tables hidden until asked")
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            ck(await safe("()=>getComputedStyle(document.querySelector('.a3d-clb-card[data-fig=\"1\"] .a3d-clb-table')).display") == 'table', "Tables: every chart's numbers")
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            s5 = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--s5').trim()")
            await safe("()=>document.body.classList.add('light-theme')")
            s5l = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--s5').trim()")
            await safe("()=>document.body.classList.remove('light-theme')")
            await page.emulate_media(media='print')
            s5p = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--s7').trim()")
            await page.emulate_media(media='screen')
            ck(s5 == '#d55181' and s5l == '#e87ba4' and s5p == '#6250d6', "the new slots follow the theme and print: dark %s, light %s; in print light (%s)" % (s5, s5l, s5p))
            ST['hits'] = []
            await safe("()=>document.querySelector('.a3d-clb [data-clb=\"refresh\"]').click()")
            for _ in range(60):
                if not await safe("()=>window.__a3dAccBusy()"):
                    break
                await page.wait_for_timeout(100)
            ck(any('/api/interpreter' in h for h in ST.get('hits', [])) and not any('open-meteo' in h for h in ST.get('hits', [])), "the board's Refresh data gets the access and people, not the climate")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            ck(await safe("()=>!document.querySelector('.a3d-clb')"), "Esc closes it")
            await safe("()=>window.__a3dRunCmd('access')")
            ck(await safe("()=>document.querySelector('.a3d-clb').getAttribute('aria-label')") == 'Access and people board', "ACCESS opens it")
            await safe("()=>window.__a3dClbClose()")
            await lot([[12, -40], [50, -40], [50, -10], [12, -10]])
            await safe("()=>window.__a3dAnzView('site')")
            await page.wait_for_timeout(100)
            ck('The lot has changed since: refresh to walk from it.' in (await safe("()=>document.querySelector('.a3d-sa-wrap [data-accsec] .a3d-clsum').textContent") or ''),
               "the lot changed: the section says to refresh")
            await safe("()=>window.__a3dClbOpen('access')")
            ck('The lot has changed since' in (await safe("()=>(document.querySelector('.a3d-acc-warn')||{}).textContent") or ''), "and so does the board")
            await safe("()=>window.__a3dClbClose()")
            await lot(LOT)
            await safe("()=>window.__a3dClbOpen('climate')")
            ck(await safe("()=>document.querySelector('.a3d-clb').getAttribute('aria-label')") == 'Climate and risk board', "the other boards are as they were")
            await safe("()=>window.__a3dClbClose()")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. a reload, offline, and a phone")
            before = await acc()
            await page.wait_for_timeout(700)
            ST['mode'] = {'osm': 'abort', 'tracts': 'abort', 'counties': 'abort', 'acs': 'abort'}
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(await acc() == before, "a reload keeps it all")
            ck([x['kind'] for x in (await safe("()=>window.__a3dResultLayers()") or [])].count('walk') == 1, "the walk times layer with it")
            await safe("()=>window.__a3dClbOpen('access')")
            ck(await safe("()=>document.querySelectorAll('.a3d-clb-card[data-fig]').length") == 8, "and the board opens offline, all eight figures")
            await safe("()=>window.__a3dClbClose()")
            ck(not errs, "no page errors (%s)" % errs[:3])
            await ctx.close()

            ctx2 = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
            ST2 = {'year': YEAR}
            for h in HOSTS:
                await ctx2.route(h, FX.route_handler(ST2))
            p2 = await ctx2.new_page()
            e2 = []
            p2.on('pageerror', lambda e: e2.append(str(e)))
            await within(p2.goto('file://' + str(HTML)), 'goto')
            await p2.wait_for_timeout(1800)
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}", pg=p2)
            await set_site('40', '-75', pg=p2)
            await lot(LOT, pg=p2)
            await fetch(pg=p2)
            await safe("()=>window.__a3dClbOpen('access')", pg=p2)
            await p2.wait_for_timeout(300)
            ph = await safe("""()=>{var b=document.querySelector('.a3d-clb');return {vb:[].map.call(b.querySelectorAll('.a3d-clb-card svg[role="img"]'),function(s){return +s.getAttribute('viewBox').split(' ')[2];}),
              sw:b.scrollWidth,cw:b.clientWidth,docw:document.documentElement.scrollWidth,cols:[].map.call(b.querySelectorAll('.a3d-acc-col,.a3d-clb-card[data-fig]'),function(c){return Math.round(c.getBoundingClientRect().width);})};}""", pg=p2) or {}
            ck(ph.get('vb') and all(v == 360 for v in ph['vb']), "on a phone every chart is drawn for its width, 360 (%s)" % ph.get('vb'))
            ck(ph.get('sw', 999) <= ph.get('cw', 0) + 1 and ph.get('docw', 999) <= 391, "and nothing spills across: the board %d of %d, the page %d" % (ph.get('sw', 0), ph.get('cw', 0), ph.get('docw', 0)))
            ck(ph.get('cols') and max(ph['cols']) - min(ph['cols']) <= 2, "one column of cards, all the same width (%s)" % sorted(set(ph.get('cols', [])))[:3])
            ck(not e2, "no page errors on the phone (%s)" % e2[:3])
            await ctx2.close()
        except Stalled as e:
            ck(False, 'the harness stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
        await browser.close()


def main():
    asyncio.run(run())
    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        for b in CK.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(main())
