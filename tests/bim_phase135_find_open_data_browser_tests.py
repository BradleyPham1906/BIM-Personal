#!/usr/bin/env python3
"""bim_phase135_find_open_data_browser_tests.py -- V135: find open data.

US open-data portals searched from the Data Layers group, their results added as V134 data layers.
The portal list and the two searches are ported from GeoLibre (MIT). Every server is routed inside
the browser: ArcGIS Online's search and Hub site items, the Socrata Discovery API, ArcGIS services,
a Socrata portal, and servers that fail.

  1. NOTHING UNTIL ASKED: the portal list (federal, each state, its cities and counties), the search
     in the Data Layers group, the credit to GeoLibre, no request; FINDDATA.
  2. WHICH PORTAL: guessed from the site's address (its city, else its state), then remembered.
  3. AN ARCGIS HUB PORTAL: the site's catalog groups read once; the search for the words, the
     types, the groups, near the site; Lucene syntax dropped; the organisation when there are no
     groups; the results in Properties, linked to their pages.
  4. ADDING: a layer, a service of one layer, a service of several (pick), a GeoJSON item, one
     without an address; each a V134 data layer, credited to the portal; one undo.
  5. A SOCRATA PORTAL: its spatial datasets only, its own; More; a dataset added and asked for the
     site's box by its geometry column.
  6. FAILURES, each named; a second search while one runs is refused.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, sys, traceback, urllib.parse
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


WA, WE2 = 6378137.0, 0.00669437999014
LAT0, LON0 = 39.9656683, -75.1687892
G1, G2 = 'a' * 32, 'b' * 31 + 'c'
PHL = 'data-phl.opendata.arcgis.com'
CHI = 'data.cityofchicago.org'


def m2g(x, z):
    s = math.sin(math.radians(LAT0))
    w = 1 - WE2 * s * s
    M, Nr = WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)
    return [LON0 + math.degrees(x / (Nr * math.cos(math.radians(LAT0)))), LAT0 + math.degrees(-z / M)]


def sq(x0, z0, w, d):
    p = [(x0, z0), (x0 + w, z0), (x0 + w, z0 + d), (x0, z0 + d), (x0, z0)]
    return [m2g(*q) for q in p]


def fc(n=2):
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'ID': i}, 'geometry': {'type': 'Polygon', 'coordinates': [sq(10 * i, -10, 8, 8)]}}
        for i in range(n)]}


def hub_items():
    return [
        {'id': '1' * 32, 'title': 'Parcels (PWD)', 'type': 'Feature Service', 'owner': 'phl_admin', 'snippet': 'Water Department parcels',
         'url': 'https://gis.example.org/arcgis/rest/services/PWD_PARCELS/FeatureServer/0'},
        {'id': '2' * 32, 'title': 'Street Trees', 'type': 'Feature Service', 'owner': 'phl_ppr',
         'url': 'https://gis.example.org/arcgis/rest/services/Trees/FeatureServer'},
        {'id': '3' * 32, 'title': 'Zoning', 'type': 'Map Service', 'owner': 'phl_plan',
         'url': 'https://gis.example.org/arcgis/rest/services/Zoning/MapServer'},
        {'id': '4' * 32, 'title': 'Bike Network', 'type': 'GeoJson', 'owner': 'phl_streets', 'url': None},
        {'id': '5' * 32, 'title': 'No Address', 'type': 'Feature Service', 'owner': 'x', 'url': ''},
        {'id': 'not-an-id', 'title': 'Bad item', 'type': 'Feature Service', 'url': 'https://gis.example.org/x/FeatureServer/0'},
    ]


def soc_entry(i, dom=CHI, spatial=True, col='the_geom'):
    return {'resource': {'id': 'ab%02d-cd%02d' % (i, i), 'name': 'Dataset %d' % i, 'description': 'about %d' % i,
                         'columns_datatype': ['text', 'number'] + (['multipolygon'] if spatial else []),
                         'columns_field_name': ['name', 'n'] + ([col] if spatial else [])},
            'metadata': {'domain': dom}, 'classification': {'domain_category': 'Buildings'}}


SRV = {'req': [], 'mode': 'ok', 'site': 'v2', 'socpages': 1, 'hold': None}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        ext = []
        page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:')) else None)

        async def answer(route, body, status=200, ctype='application/json'):
            await route.fulfill(status=status, body=body if isinstance(body, str) else json.dumps(body),
                                headers={'Content-Type': ctype, 'Access-Control-Allow-Origin': '*'})

        async def srv(route):
            u = route.request.url
            SRV['req'].append(u)
            p = urllib.parse.urlparse(u)
            qs = dict(urllib.parse.parse_qsl(p.query))
            m = SRV['mode']
            if SRV['hold'] is not None:
                await SRV['hold'].wait()
            if m == 'abort':
                return await route.abort('internetdisconnected')
            if m == '500':
                return await answer(route, 'busy', 500, 'text/plain')
            if m == 'junk':
                return await answer(route, '<html>oops</html>', 200, 'text/html')
            if m == 'arcerr':
                return await answer(route, {'error': {'code': 400, 'message': 'Unable to perform query', 'details': []}})
            if p.netloc == 'www.arcgis.com' and '/content/items/' in p.path and p.path.endswith('/data') and qs.get('f') == 'json':
                if SRV['site'] == 'v2':
                    return await answer(route, {'catalogV2': {'scopes': {'item': {'filters': [
                        {'predicates': [{'group': [G1, 'not-a-group']}, {'group': {'any': [G2, G1]}}]}]}}}})
                if SRV['site'] == 'v1':
                    return await answer(route, {'catalog': {'groups': [G2]}})
                return await answer(route, 'nope', 404, 'text/plain')
            if p.netloc == 'www.arcgis.com' and p.path == '/sharing/rest/search':
                start = int(qs.get('start', '1'))
                its = hub_items() if start == 1 else [{'id': '6' * 32, 'title': 'Page Two', 'type': 'GeoJson', 'owner': 'p'}]
                return await answer(route, {'total': 7, 'start': start, 'num': 20, 'nextStart': 7 if start == 1 else -1, 'results': its})
            if p.netloc == 'www.arcgis.com' and '/content/items/' in p.path and p.path.endswith('/data'):
                return await answer(route, fc(3))
            if p.netloc == 'api.us.socrata.com':
                off = int(qs.get('offset', '0'))
                if off == 0:
                    res = [soc_entry(1), soc_entry(2, spatial=False), soc_entry(3, dom='data.other.gov'), soc_entry(4, col='bad col')]
                    total = 6 if SRV['socpages'] > 1 else 4
                else:
                    res = [soc_entry(5), soc_entry(6)]
                    total = 6
                return await answer(route, {'resultSetSize': total, 'results': res})
            if p.netloc == 'gis.example.org' and qs.get('f') == 'json' and not p.path.endswith('/query'):
                if 'Trees' in p.path:
                    return await answer(route, {'layers': [{'id': 0, 'name': 'Trees', 'type': 'Feature Layer'}]})
                return await answer(route, {'layers': [{'id': 0, 'name': 'Zoning (group)', 'type': 'Group Layer', 'subLayerIds': [1, 2]},
                                                       {'id': 1, 'name': 'Base Districts', 'type': 'Feature Layer'},
                                                       {'id': 2, 'name': 'Overlays', 'type': 'Feature Layer'},
                                                       {'id': 3, 'name': 'Hillshade', 'type': 'Raster Layer'}]})
            return await answer(route, fc(2))
        for host in ('https://www.arcgis.com/**', 'https://api.us.socrata.com/**', 'https://gis.example.org/**', 'https://' + CHI + '/**'):
            await ctx.route(host, srv)

        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV135")
        ck(bool(has), "__acad3dV135 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(150)
            return ok

        async def click(sel):
            ok = await safe("(s)=>{var e=document.querySelector('#a3d-propsbody '+s);if(!e)return false;e.click();return true;}", sel)
            await page.wait_for_timeout(150)
            return ok

        async def settle():
            for _ in range(100):
                if not await safe("()=>window.__a3dFindState().busy"):
                    break
                await page.wait_for_timeout(50)
            await page.wait_for_timeout(100)

        async def state():
            return await safe("()=>window.__a3dFindState()") or {}

        async def layers():
            return await safe("()=>window.__a3dDataLayers()") or []

        async def find_add(ix, ly=None):
            return await safe("(a)=>window.__a3dFindAdd(a[0],a[1])", [ix, ly]) or {}

        def qs_of(u):
            return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(u).query))

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. nothing until asked")
            await safe("()=>{try{localStorage.removeItem('acad3dUIPrefs');}catch(e){}return window.__a3dFindReset();}")
            P = await safe("()=>window.__a3dFindPortals()") or []
            n = sum(len(g[1]) for g in P)
            ck(n == 238 and len(P) == 98, "238 portals in 98 groups (%d, %d)" % (n, len(P)))
            names = [g[0] for g in P]
            ck(names[0].startswith('Federal: ') and all(x.startswith('Federal: ') for x in names[:11]) and not names[11].startswith('Federal'),
               "the federal agencies first")
            i_pa = names.index('Pennsylvania: state') if 'Pennsylvania: state' in names else -1
            ck(i_pa > 0 and names[i_pa + 1] == 'Pennsylvania: cities and counties', "each state's portals, then its cities and counties")
            pa = dict((p[0], p) for p in P[i_pa + 1][1]) if i_pa > 0 else {}
            ck(pa.get('Philadelphia') == ['Philadelphia', PHL, '80ecb6974200435f8e4b5696b11ca2b8', 'fLeGjb7u4uXqeF9q', 0],
               "Philadelphia: its Hub site and the organisation the V134 presets use")
            chi = [p for g in P for p in g[1] if p[1] == CHI]
            ck(chi and chi[0][4] == 1 and chi[0][2] == '' and chi[0][3] == '', "Chicago is a Socrata portal")
            ck(all(p[4] or p[2] or p[3] for g in P for p in g[1]), "every portal has something to search by")
            await nosel()
            h = await props_html()
            ck('data-propfind="portal"' in h and h.count('<optgroup') == 98 and 'data-propfind="q"' in h and 'data-propfindact="search"' in h and
               'data-propfind="near"' in h, "the Data Layers group has the search: a portal, words, Search, Near the site only")
            ck(h.index('data-a3dpgrp="Data Layers"') < h.index('data-propfind="portal"') < h.index('data-a3dpgrp="View"'), "inside the Data Layers group")
            ck('GeoLibre (MIT licence)' in h, "the list and the searches are credited to GeoLibre")
            ck(ext == [], "no request on the way up, nor for the group")
            r = await safe("()=>window.__a3dRunCmd('finddata')")
            await page.wait_for_timeout(150)
            foc = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-propfind')")
            ck(foc == 'q' and 'Find data' in await toast(), "FINDDATA opens it at the words")
            ck(ext == [], "still nothing asked")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. which portal")
            await safe("()=>window.__a3dFindReset()")
            ck(await safe("()=>window.__a3dFindGuess()") == '', "no address, no guess")
            addr = '1400 John F Kennedy Blvd, Center City, Philadelphia, Philadelphia County, Pennsylvania, 19107, United States'
            await safe("(a)=>window.__a3dSetSiteAddress(a)", addr)
            g = await safe("()=>window.__a3dFindGuess()")
            ck(g == PHL, "an address in Philadelphia picks Philadelphia's portal (%s)" % g)
            await safe("(a)=>window.__a3dSetSiteAddress(a)", 'Market Square, Harrisburg, Dauphin County, Pennsylvania, 17101, United States')
            g = await safe("()=>window.__a3dFindGuess()")
            ck(g == 'data-pennshare.opendata.arcgis.com', "a town with no portal of its own picks its state's (%s)" % g)
            await safe("(a)=>window.__a3dSetSiteAddress(a)", 'Tri Ton, An Giang, Vietnam')
            ck(await safe("()=>window.__a3dFindGuess()") == '', "outside the US, none")
            p = await safe("()=>window.__a3dFindPortal()")
            ck(p is None, "and no portal is picked")
            await set_field('[data-propfind="portal"]', 'usgs.maps.arcgis.com')
            p = await safe("()=>window.__a3dFindPortal()") or {}
            ck(p.get('name') == 'U.S. Geological Survey' and p.get('org') == 'v01gqwM5QqNysAAi' and p.get('site') == '' and p.get('group') == 'Federal: Department of the Interior',
               "a portal picked in the list (%s)" % p.get('name'))
            await safe("()=>{var s=window.__a3dFindState();window.__a3dFindReset();return s;}")
            p = await safe("()=>window.__a3dFindPortal()") or {}
            ck(p.get('host') == 'usgs.maps.arcgis.com', "is remembered")
            await safe("(a)=>window.__a3dSetSiteAddress(a)", addr)
            await safe("()=>window.__a3dFindReset()")
            p = await safe("()=>window.__a3dFindPortal()") or {}
            ck(p.get('host') == PHL, "but a site with an address of its own picks its own")
            ck(await safe("()=>window.__a3dFindPortal('no.such.host')") and (await safe("()=>window.__a3dFindPortal()") or {}).get('host') == PHL,
               "a host not in the list is not picked")
            ck(ext == [], "no request while picking")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. an ArcGIS Hub portal")
            u = await safe("(a)=>window.__a3dFindHubUrl(a[0],a[1])", ['parcels: (2024) AND "zoning" OR x+y', {'groups': [G1, 'zz'], 'org': 'fLeGjb7u4uXqeF9q', 'start': 21}])
            q = qs_of(u or '')
            ck(urllib.parse.urlparse(u or '').netloc == 'www.arcgis.com' and q.get('q', '').startswith('(parcels 2024 zoning x y) AND ('),
               "the words with Lucene syntax dropped (%s)" % q.get('q', '')[:40])
            ck('type:"Feature Service" OR type:"Map Service" OR type:"GeoJson"' in q.get('q', '') and q.get('q', '').endswith(' AND access:public'),
               "the types read here, public items only")
            ck(' AND (group:' + G1 + ')' in q.get('q', '') and 'zz' not in q.get('q', '') and 'orgid' not in q.get('q', ''),
               "scoped to the catalog's groups, a malformed one dropped, no organisation then")
            ck(q.get('start') == '21' and q.get('num') == '20' and q.get('f') == 'json' and q.get('sortField') == 'relevance', "paged, by relevance")
            q = qs_of(await safe("(a)=>window.__a3dFindHubUrl(a[0],a[1])", ['', {'org': 'fLeGjb7u4uXqeF9q', 'bbox': [-75.2, 39.9, -75.1, 40.0]}]) or '')
            ck(q.get('q', '').startswith('(type:') and ' AND orgid:fLeGjb7u4uXqeF9q AND access:public' in q.get('q', '') and q.get('sortField') == 'title' and
               q.get('sortOrder') == 'asc' and q.get('bbox') == '-75.20000,39.90000,-75.10000,40.00000',
               "no words: the catalog by title; the organisation without groups; the box")
            q = qs_of(await safe("(a)=>window.__a3dFindHubUrl(a[0],a[1])", ['', {'org': 'bad org!'}]) or '')
            ck('orgid' not in q.get('q', ''), "a malformed organisation is dropped")
            # the search itself
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            await safe("()=>window.__a3dSetTrueNorth(0)")
            await set_field('[data-propfind="q"]', 'parcels')
            ck(ext == [], "typing the words asks nothing")
            n0 = len(ext)
            await click('[data-propfindact="search"]')
            await settle()
            reqs = ext[n0:]
            ck(len(reqs) == 2 and '/content/items/80ecb6974200435f8e4b5696b11ca2b8/data' in reqs[0] and '/sharing/rest/search' in reqs[1],
               "Search reads the Hub site's item, then searches: two requests (%d)" % len(reqs))
            q = qs_of(reqs[1]) if len(reqs) > 1 else {}
            a = await safe("()=>window.__a3dCtxArea()") or {}
            bb = [float(v) for v in q.get('bbox', '0,0,0,0').split(',')]
            ck(q.get('q', '').startswith('(parcels) AND') and '(group:' + G1 + ' OR group:' + G2 + ')' in q.get('q', '') and 'orgid' not in q.get('q', ''),
               "for the words, in the site's catalog groups, each once")
            ck(a and all(abs(bb[i] - v) < 1e-5 for i, v in enumerate((a['w'], a['s'], a['e'], a['n']))), "near the site: its area's box")
            s = await state()
            ck([x['title'] for x in s.get('res', [])] == ['Parcels (PWD)', 'Street Trees', 'Zoning', 'Bike Network', 'No Address'] and s.get('next') == 7,
               "5 results, the malformed item dropped, more to see")
            ck(s.get('groups', {}).get('80ecb6974200435f8e4b5696b11ca2b8') == [G1, G2], "the catalog groups kept")
            h = await props_html()
            ck('Parcels (PWD)' in h and 'Feature Service - phl_admin' in h and h.count('data-propfindact="add:') == 5 and 'data-propfindact="more"' in h and
               '5 found, more to see' in h, "each result with its kind and owner, Add, and More results")
            ck('href="https://www.arcgis.com/home/item.html?id=' + '1' * 32 + '" target="_blank" rel="noopener noreferrer"' in h, "linked to its page, in a new tab")
            n0 = len(ext)
            await safe("()=>window.__a3dFindNear(false)")
            await safe("()=>window.__a3dFindSearch('parcels')")
            await settle()
            reqs = ext[n0:]
            ck(len(reqs) == 1 and 'bbox' not in qs_of(reqs[0]), "a second search does not read the site again; not near: no box")
            await safe("()=>window.__a3dFindNear(true)")
            n0 = len(ext)
            await click('[data-propfindact="more"]')
            await settle()
            s = await state()
            ck(len(ext) == n0 + 1 and qs_of(ext[-1]).get('start') == '7' and s['res'][-1]['title'] == 'Page Two' and len(s['res']) == 6 and s['next'] == 0,
               "More continues from where it stopped, and there is no more")
            ck('data-propfindact="more"' not in await props_html(), "so More goes")
            # an older site, and a site that cannot be read
            await safe("()=>window.__a3dFindReset()")
            SRV['site'] = 'v1'
            await safe("()=>window.__a3dFindPortal('hub-cookcountyil.opendata.arcgis.com')")
            n0 = len(ext)
            await safe("()=>window.__a3dFindSearch('roads')")
            await settle()
            ck('(group:' + G2 + ')' in qs_of(ext[-1]).get('q', ''), "an older Hub site's catalog groups")
            SRV['site'] = 'gone'
            await safe("()=>window.__a3dFindPortal('gis-idot.opendata.arcgis.com')")
            await safe("()=>window.__a3dFindSearch('roads')")
            await settle()
            q = qs_of(ext[-1]).get('q', '')
            ck('orgid:aIrBD8yn1TDTEXoz' in q and 'group:' not in q and (await state()).get('err') == '', "a site that cannot be read: its organisation instead")
            SRV['site'] = 'v2'
            n0 = len(ext)
            await safe("()=>window.__a3dFindPortal('usgs.maps.arcgis.com')")
            await safe("()=>window.__a3dFindSearch('')")
            await settle()
            q = qs_of(ext[-1]).get('q', '')
            ck(len(ext) == n0 + 1 and 'orgid:v01gqwM5QqNysAAi' in q and q.startswith('(type:'), "an organisation with no Hub site: one request, by organisation")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. adding")
            await safe("()=>window.__a3dFindReset()")
            await safe("()=>window.__a3dFindPortal('" + PHL + "')")
            await safe("()=>window.__a3dFindSearch('parcels')")
            await settle()
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the add's undo is its own
            n0 = len(ext)
            r = await find_add(0)
            L = await layers()
            ck(r.get('id') and len(L) == 1 and L[0]['url'] == 'https://gis.example.org/arcgis/rest/services/PWD_PARCELS/FeatureServer/0' and L[0]['kind'] == 'arcgis' and
               L[0]['name'] == 'Parcels (PWD)', "a layer is added as a data layer, named as the portal names it")
            ck(L and L[0]['credit'] == 'Philadelphia open data (' + PHL + ')', "credited to the portal (%s)" % (L[0]['credit'] if L else None))
            ck((r.get('fetch') or {}).get('count') == 2 and len(ext) == n0 + 1 and '/FeatureServer/0/query' in ext[-1], "and fetched at once for the site")
            await nosel()
            h = await props_html()
            ck('Parcels (PWD)</a><span class="a3d-fdk">Feature Service - phl_admin</span></div><span class="a3d-fdk">added</span>' in h, "the result says added")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(await layers() == [] and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7, "one undo step, its own")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(100)
            n0 = len(ext)
            r = await find_add(1)
            L = await layers()
            ck(len(ext) == n0 + 2 and ext[n0].endswith('/Trees/FeatureServer?f=json') and L[-1]['url'].endswith('/Trees/FeatureServer/0') and L[-1]['name'] == 'Street Trees',
               "a whole service of one layer: its layers read, that one added")
            n0 = len(ext)
            r = await find_add(2)
            s = await state()
            ck(r.get('result') == {'pick': 2} and len(ext) == n0 + 1 and len(await layers()) == 2, "a service of several: nothing added yet")
            ck([x['name'] for x in (s.get('pick') or {}).get('layers', [])] == ['Base Districts', 'Overlays'], "the feature layers to pick: no group, no imagery")
            await nosel()
            h = await props_html()
            ck(h.count('a3d-fdsub') == 2 and 'data-propfindact="layer:2:1"' in h, "listed under the result, each with Add")
            await click('[data-propfindact="layer:2:1"]')
            await page.wait_for_timeout(300)
            L = await layers()
            ck(L[-1]['url'] == 'https://gis.example.org/arcgis/rest/services/Zoning/MapServer/2' and L[-1]['name'] == 'Zoning - Overlays', "a picked layer is added")
            h = await props_html()
            ck('data-propfindact="layer:2:1"' not in h and 'data-propfindact="layer:2:0"' in h, "and says added; the other is still there to add")
            n0 = len(ext)
            r = await find_add(3)
            L = await layers()
            ck(L[-1]['url'] == 'https://www.arcgis.com/sharing/rest/content/items/' + '4' * 32 + '/data' and L[-1]['kind'] == 'geojson' and
               (r.get('fetch') or {}).get('count') == 3, "a GeoJSON item: its data, as a file kept to the area")
            n0 = len(ext)
            r = await find_add(4)
            ck(not r.get('id') and len(ext) == n0 and 'no ArcGIS layer address' in await toast(), "one without an address is refused, nothing asked")
            r = await find_add(0)
            ck(not r.get('id') and 'here already' in await toast(), "one already added is refused")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. a Socrata portal")
            u = await safe("(a)=>window.__a3dFindSocrataUrl(a[0],a[1],a[2])", [CHI, ' building footprints ', 200])
            q = qs_of(u or '')
            ck((u or '').startswith('https://api.us.socrata.com/api/catalog/v1?') and q.get('search_context') == CHI and q.get('domains') == CHI and
               q.get('only') == 'dataset' and q.get('q') == 'building footprints' and q.get('offset') == '200' and q.get('limit') == '100',
               "the Discovery API, scoped to the portal's own catalog")
            ck(qs_of(await safe("(a)=>window.__a3dFindSocrataUrl(a)", CHI) or '').get('order') == 'name', "no words: by name")
            await safe("()=>window.__a3dFindReset()")
            await safe("()=>window.__a3dFindPortal('" + CHI + "')")
            n0 = len(ext)
            await safe("()=>window.__a3dFindSearch('buildings')")
            await settle()
            s = await state()
            ck(len(ext) == n0 + 1 and [x['id'] for x in s['res']] == ['ab01-cd01', 'ab04-cd04'] and s['next'] == 0,
               "its spatial datasets only, its own only: 2 of 4")
            r0 = s['res'][0] if s['res'] else {}
            ck(r0.get('data') == 'https://' + CHI + '/resource/ab01-cd01.geojson' and r0.get('geom') == 'the_geom' and r0.get('page') == 'https://' + CHI + '/d/ab01-cd01' and
               r0.get('type') == 'Socrata dataset' and r0.get('owner') == 'Buildings', "its addresses from the portal's host, its geometry column")
            ck(s['res'][1].get('geom') == '', "a geometry column that is not a plain name is not used")
            SRV['socpages'] = 2
            n0 = len(ext)
            await safe("()=>window.__a3dFindSearch('buildings')")
            await settle()
            s = await state()
            ck(len(ext) == n0 + 2 and qs_of(ext[-1]).get('offset') == '4' and [x['id'] for x in s['res']] == ['ab01-cd01', 'ab04-cd04', 'ab05-cd05', 'ab06-cd06'],
               "too few in a batch: it reads on until it has a page or the catalog ends")
            SRV['socpages'] = 1
            n0 = len(ext)
            r = await find_add(0)
            L = await layers()
            Ls = L[-1] if L else {}
            ck(Ls.get('kind') == 'socrata' and Ls.get('geom') == 'the_geom' and Ls.get('name') == 'Dataset 1' and Ls.get('credit') == 'Chicago open data (' + CHI + ')',
               "a dataset added as a Socrata data layer")
            a = await safe("()=>window.__a3dCtxArea()") or {}
            q = qs_of(ext[-1]) if len(ext) > n0 else {}
            want = 'within_box(the_geom,%.7f,%.7f,%.7f,%.7f)' % (a.get('n', 0), a.get('w', 0), a.get('s', 0), a.get('e', 0))
            ck(urllib.parse.urlparse(ext[-1]).path == '/resource/ab01-cd01.geojson' and q.get('$where') == want and q.get('$limit') == '2000',
               "asked for the site's box only: within_box(column, north, west, south, east), at most 2000")
            ck((r.get('fetch') or {}).get('count') == 2, "its features kept")
            ck(await safe("(u)=>window.__a3dDataKind(u)", 'https://' + CHI + '/resource/ab01-cd01.geojson?$limit=5') == {'kind': 'socrata'}, "a pasted Socrata address is that kind too")
            r = await find_add(1)
            ck('$where' not in ext[-1] and qs_of(ext[-1]).get('$limit') == '2000', "with no geometry column: the first 2000, kept to the area")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. failures, each named")
            await safe("()=>window.__a3dFindPortal('" + PHL + "')")
            for mode, want in (('500', 'www.arcgis.com answered HTTP 500'), ('abort', 'www.arcgis.com could not be reached'),
                               ('junk', 'www.arcgis.com sent an answer that does not read'), ('arcerr', 'www.arcgis.com said: Unable to perform query')):
                SRV['mode'] = mode
                await safe("()=>{window.__a3dFindReset();window.__a3dFindPortal('" + PHL + "');}")
                await safe("()=>window.__a3dFindSearch('x')")
                await settle()
                s = await state()
                await nosel()
                ck(want in s.get('err', '') and want in await props_html() and s['res'] == [], "%s: %s" % (mode, s.get('err')))
            SRV['mode'] = '500'
            await safe("()=>window.__a3dFindPortal('" + CHI + "')")
            await safe("()=>window.__a3dFindSearch('x')")
            await settle()
            ck('api.us.socrata.com answered HTTP 500' in (await state()).get('err', ''), "a Socrata failure names its host")
            SRV['mode'] = 'ok'
            await safe("()=>{window.__a3dFindReset();window.__a3dFindPortal('" + PHL + "');}")
            await safe("()=>window.__a3dFindSearch('trees')")
            await settle()
            SRV['mode'] = '500'
            r = await find_add(1)
            ck('Street Trees: gis.example.org answered HTTP 500' in await toast(), "a service whose layers cannot be read is named")
            SRV['mode'] = 'ok'
            SRV['hold'] = asyncio.Event()
            p1 = asyncio.ensure_future(safe("()=>window.__a3dFindSearch('roads')"))
            await page.wait_for_timeout(200)
            busy = (await state()).get('busy')
            await nosel()
            dis = 'data-propfindact="search" disabled' in await props_html()
            r2 = await safe("()=>window.__a3dFindSearch('roads').then(function(r){return r===null;})")
            ck(busy and dis and r2 is True and 'already on its way' in await toast(), "a second search while one runs is refused, Search off")
            SRV['hold'].set()
            SRV['hold'] = None
            await within(p1, 'held search')
            await settle()
            await safe("()=>window.__a3dSetSiteAddress('')")
            await safe("()=>window.__a3dFindReset()")
            await safe("()=>window.__a3dFindPortal('')")
            r = await safe("()=>window.__a3dFindSearch('x').then(function(r){return r===null;})")
            ck(r is True and 'Pick a portal' in await toast(), "no portal picked: asked to pick one")
            ck(not errs, "no page errors (%s)" % errs[:2])
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the harness crashed')
        await browser.close()
    print("\n%d/%d checks passed\nRESULT: %s" % (ck.n - len(ck.bad), ck.n, 'PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
