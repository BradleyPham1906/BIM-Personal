#!/usr/bin/env python3
"""bim_phase134_data_layers_browser_tests.py -- V134: data layers.

Parcels, zoning and flood zones from the GIS servers councils and agencies publish
(reference/research-data-layers.md). Every server is routed inside the browser: an ArcGIS
FeatureServer, FEMA's MapServer (the preset), a WFS, a GeoJSON file, and servers that fail.

  1. NOTHING UNTIL ASKED: the Data Layers group, the presets, no request.
  2. WHAT AN ADDRESS IS: ArcGIS layer, WFS, GeoJSON; a whole service, a WFS without its layer and
     not-an-address refused with the reason.
  3. AN ARCGIS LAYER: its query for the area, one request, the features in the area kept, the name
     from the address; one undo; redo; a duplicate refused.
  4. ON THE PLAN: drawn in its colour; a click reads a feature (a point before an area, the smallest
     area); its attributes in Properties; hidden is neither drawn nor read; not on paper.
  5. A PARCEL BECOMES A PROPERTY LINE, where the parcel is, in one undo step.
  6. WFS AND GEOJSON: GetFeature in CRS:84; a file kept to the area.
  7. FAILURES, each named, the features kept; more on the server said.
  8. CREDITS, REMOVE AND UNDO, A RELOAD (offline), THE PRESET, THE COMMAND.

The harness never waits without a bound (V123).
"""
import asyncio, io, json, math, pathlib, re, sys, traceback, urllib.parse
from playwright.async_api import async_playwright
from PIL import Image

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


def radii(lat):
    s = math.sin(math.radians(lat))
    w = 1 - WE2 * s * s
    return WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)


def m2g(x, z, tn=0.0):
    t = math.radians(tn)
    E, N = x * math.cos(t) + z * math.sin(t), x * math.sin(t) - z * math.cos(t)
    M, Nr = radii(LAT0)
    return [LON0 + math.degrees(E / (Nr * math.cos(math.radians(LAT0)))), LAT0 + math.degrees(N / M)]


def ring(pts):
    return [m2g(*p) for p in pts + [pts[0]]]


def sq(x0, z0, w, d):
    return [(x0, z0), (x0 + w, z0), (x0 + w, z0 + d), (x0, z0 + d)]


PARCEL_A = sq(10, -30, 20, 25)       # 500 m2
PARCEL_B = sq(40, -30, 15, 25)
PARCEL_C = sq(-60, 10, 30, 30)       # with a courtyard
HOLE_C = sq(-50, 20, 10, 10)
FAR = sq(2000, 2000, 10, 10)         # outside the area


def parcels(more=False):
    fc = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'PARCELID': '001S07-0123', 'ADDRESS': '1500 SPRING GARDEN ST', 'GROSS_AREA': 500},
         'geometry': {'type': 'Polygon', 'coordinates': [ring(PARCEL_A)]}},
        {'type': 'Feature', 'properties': {'PARCELID': '001S07-0124', 'ADDRESS': '1520 SPRING GARDEN ST', 'GROSS_AREA': 375},
         'geometry': {'type': 'Polygon', 'coordinates': [ring(PARCEL_B)]}},
        {'type': 'Feature', 'properties': {'PARCELID': '001S07-0200', 'ADDRESS': 'COURTYARD BLOCK'},
         'geometry': {'type': 'Polygon', 'coordinates': [ring(PARCEL_C), ring(HOLE_C)]}},
        {'type': 'Feature', 'properties': {'PARCELID': 'FAR-AWAY'}, 'geometry': {'type': 'Polygon', 'coordinates': [ring(FAR)]}},
    ]}
    if more:
        fc['properties'] = {'exceededTransferLimit': True}
    return fc


def zoning():
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'LONG_CODE': 'CMX-3', 'ZONINGGROUP': 'Commercial/Commercial Mixed-Use'},
         'geometry': {'type': 'Polygon', 'coordinates': [ring(sq(-100, -100, 200, 200))]}}]}


def trees():
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'species': 'London plane'}, 'geometry': {'type': 'Point', 'coordinates': m2g(20, -20)}},
        {'type': 'Feature', 'properties': {'species': 'Far oak'}, 'geometry': {'type': 'Point', 'coordinates': m2g(3000, 0)}},
        {'type': 'Feature', 'properties': {'name': 'Spring Garden St'}, 'geometry': {'type': 'LineString', 'coordinates': [m2g(-90, 5), m2g(90, 5)]}}]}


def flood():
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'FLD_ZONE': 'AE', 'ZONE_SUBTY': None},
         'geometry': {'type': 'Polygon', 'coordinates': [ring(sq(-140, 60, 80, 60))]}}]}


SRV = {'req': [], 'mode': 'ok', 'more': False}


def near(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        ext = []
        page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:', 'blob:')) else None)

        async def answer(route, body, status=200, ctype='application/json'):
            await route.fulfill(status=status, body=body if isinstance(body, str) else json.dumps(body),
                                headers={'Content-Type': ctype, 'Access-Control-Allow-Origin': '*'})

        async def gis(route):
            u = route.request.url
            SRV['req'].append(u)
            m = SRV['mode']
            if m == 'abort':
                await route.abort('internetdisconnected')
            elif m == '500':
                await answer(route, 'busy', 500, 'text/plain')
            elif m == 'arcerr':
                await answer(route, {'error': {'code': 400, 'message': 'Invalid query parameters', 'details': []}})
            elif m == 'junk':
                await answer(route, '<html>oops</html>', 200, 'text/html')
            elif m == 'projected':
                await answer(route, {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {},
                                     'geometry': {'type': 'Point', 'coordinates': [2694000.5, 240000.25]}}]})
            elif 'Zoning' in u or 'typeNames=city:zoning' in u:
                await answer(route, zoning())
            elif 'trees.geojson' in u:
                await answer(route, trees())
            elif 'NFHL' in u:
                await answer(route, flood())
            else:
                await answer(route, parcels(SRV['more']))
        for host in ('https://gis.example.org/**', 'https://geo.example.org/**', 'https://data.example.org/**', 'https://hazards.fema.gov/**'):
            await ctx.route(host, gis)

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

        has = await safe("()=>!!window.__acad3dV134")
        ck(bool(has), "__acad3dV134 marker is present")
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

        async def layers():
            return await safe("()=>window.__a3dDataLayers()") or []

        async def add(u, *rest):
            return await safe("(a)=>window.__a3dDataAdd(a[0],a[1],a[2],a[3])", [u] + list(rest) + [None] * (3 - len(rest))) or {}

        async def screen_of(x, z):
            return await safe("""(p)=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect(),q=window.__a3dProject([p[0],0,p[1]]);
              return [r.left+q.x,r.top+q.y];}""", [x, z])

        async def click_at(x, z):
            s = await screen_of(x, z)
            await page.mouse.click(s[0], s[1])
            await page.wait_for_timeout(150)
            return await safe("()=>window.__a3dDataSel()")

        ARC = 'https://gis.example.org/arcgis/rest/services/Parcels_Public/FeatureServer/0'
        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. nothing until asked")
            await nosel()
            h = await props_html()
            ck('data-a3dpgrp="Data Layers"' in h and h.index('data-a3dpgrp="Site Context"') < h.index('data-a3dpgrp="Data Layers"') < h.index('data-a3dpgrp="View"'),
               "a Data Layers group after the Site Context")
            pres = await safe("()=>window.__a3dDataPresets()") or []
            ck([p['name'] for p in pres] == ['Flood zones (FEMA NFHL, US)', 'Parcels (Philadelphia Water Dept.)', 'Zoning base districts (Philadelphia)'] and
               all(p['name'] in h for p in pres), "three presets: FEMA's flood zones, Philadelphia's parcels and zoning")
            ck('None yet' in h and 'data-propdataact="add"' in h, "none yet, an address and Add")
            ck(ext == [], "no request on the way up")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. what an address is")
            for u, want in ((ARC, {'kind': 'arcgis'}), (ARC + '/', {'kind': 'arcgis'}),
                            ('https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28', {'kind': 'arcgis'}),
                            ('https://geo.example.org/geoserver/wfs?service=WFS&typeNames=city:zoning', {'kind': 'wfs'}),
                            ('https://data.example.org/trees.geojson', {'kind': 'geojson'})):
                ck(await safe("(u)=>window.__a3dDataKind(u)", u) == want, "%s is %s" % (u[:60], want['kind']))
            for u, why in (('https://gis.example.org/arcgis/rest/services/Parcels_Public/FeatureServer', "add the layer's number"),
                           ('https://geo.example.org/geoserver/wfs?service=WFS&request=GetCapabilities', 'add typeNames'),
                           ('parcels please', 'a web address')):
                r = await safe("(u)=>window.__a3dDataKind(u)", u) or {}
                ck(why in r.get('error', ''), "%r refused: %s" % (u[:50], r.get('error')))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. an ArcGIS layer")
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            await safe("()=>window.__a3dSetTrueNorth(0)")
            n0 = len(ext)
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the add's undo must be its own
            n0 = len(ext)
            r = await add(ARC)
            lid = r.get('id')
            ck(r.get('result', {}).get('count') == 3 and len(ext) == n0 + 1, "added and fetched at once: one request, 3 parcels (%s)" % r.get('result'))
            a = await safe("()=>window.__a3dCtxArea()")
            q = urllib.parse.urlparse(SRV['req'][-1]) if SRV['req'] else None
            qs = dict(urllib.parse.parse_qsl(q.query)) if q else {}
            ck(q and q.path.endswith('/FeatureServer/0/query') and qs.get('where') == '1=1' and qs.get('f') == 'geojson' and qs.get('outFields') == '*' and
               qs.get('inSR') == '4326' and qs.get('outSR') == '4326' and qs.get('geometryType') == 'esriGeometryEnvelope' and qs.get('resultRecordCount') == '2000',
               "ArcGIS's query: everything, as GeoJSON in longitude and latitude, at most 2000")
            box = [float(v) for v in qs.get('geometry', '0,0,0,0').split(',')]
            ck(a and all(near(box[i], v, 1e-7) for i, v in enumerate((a['w'], a['s'], a['e'], a['n']))), "on the site's area, west, south, east, north")
            L = (await layers() or [{}])[0]
            ck(L.get('name') == 'Parcels Public' and L.get('kind') == 'arcgis' and L.get('visible') is True and L.get('credit') == 'gis.example.org' and
               L.get('status', {}).get('count') == 3, "named from its address, shown, credited to its host, holding 3 (%s)" % L)
            F = await safe("(i)=>window.__a3dDataFeatures(i)", lid) or []
            ck([f['p'].get('PARCELID') for f in F] == ['001S07-0123', '001S07-0124', '001S07-0200'], "the one far from the site is left out")
            ck(F and F[0]['p'] == {'PARCELID': '001S07-0123', 'ADDRESS': '1500 SPRING GARDEN ST', 'GROSS_AREA': 500}, "each with its attributes")
            await nosel()
            ck('3 features' in await props_html(), "the group says what the layer holds")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(await layers() == [] and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7, "adding is one undo step, its own")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(100)
            ck(len(await layers()) == 1 and len(await safe("(i)=>window.__a3dDataFeatures(i)", lid) or []) == 3, "and a redo brings it back with its features, no request")
            n0 = len(ext)
            r = await add(ARC)
            ck(not r.get('id') and 'here already' in await toast() and len(ext) == n0, "the same address twice is refused, nothing asked")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. on the plan")
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:160})")
            await safe("(i)=>window.__a3dDataSet(i,'color','#ff00ff')", lid)
            await safe("()=>window.__a3dTestPaint()")
            ck(await safe("()=>window.__a3dDataDrawn()") == 3, "its 3 features are drawn")
            img = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
            s = await screen_of(15, -25)
            px = img.getpixel((int(s[0]), int(s[1])))
            bg = (29, 32, 36)
            want = tuple(round(bg[i] + ((255, 0, 255)[i] - bg[i]) * 0.16) for i in range(3))
            ck(all(abs(px[i] - want[i]) <= 8 for i in range(3)), "an area is filled faintly in its colour (%s, %s)" % (px, want))
            s2 = await screen_of(-45, 25)
            px2 = img.getpixel((int(s2[0]), int(s2[1])))
            ck(all(abs(px2[i] - bg[i]) <= 6 for i in range(3)), "and its courtyard is not filled (%s)" % (px2,))
            sel = await click_at(15, -20)
            ck(sel and sel['layer'] == lid and sel['fi'] == 0, "a click on a parcel reads it (%s)" % sel)
            h = await props_html()
            ck('data-a3dpgrp="Data Feature"' in h and '1500 SPRING GARDEN ST' in h and 'PARCELID' in h and 'Make Property Line' in h and
               h.index('data-a3dpgrp="Data Feature"') < h.index('data-a3dpgrp="Identity Data"'), "its attributes head Properties, with Make Property Line")
            ck('500 m' in h, "and its area")
            sel = await click_at(-45, 25)
            ck(sel is None, "a click in its courtyard reads nothing")
            sel = await click_at(150, 150)
            ck(sel is None and 'data-a3dpgrp="Data Feature"' not in await props_html(), "nor a click on nothing, and the page goes")
            # a point before an area, the smallest area
            r2 = await add('https://data.example.org/trees.geojson', 'Street trees', '#00ff00', 'City of Philadelphia, PPR')
            r3 = await add('https://gis.example.org/arcgis/rest/services/Zoning_BaseDistricts/FeatureServer/0', None, '#ffaa00')
            tid, zid = r2.get('id'), r3.get('id')
            ck(r2.get('result', {}).get('count') == 2 and r3.get('result', {}).get('count') == 1, "a tree, a street and a zoning district added")
            sel = await click_at(20, -20)
            ck(sel and sel['layer'] == tid, "where a tree stands in a parcel in a district, the tree is read (%s)" % sel)
            sel = await click_at(25, -10)
            ck(sel and sel['layer'] == lid and sel['fi'] == 0, "elsewhere in the parcel, the parcel: the smaller area (%s)" % sel)
            sel = await click_at(-80, -40)
            ck(sel and sel['layer'] == zid, "outside every parcel, the district")
            sel = await click_at(0, 5)
            ck(sel and sel['layer'] == tid and sel['fi'] == 1, "a click on the street reads the line")
            await safe("(i)=>window.__a3dDataSet(i,'visible',false)", zid)
            sel = await click_at(-80, -40)
            ck(sel is None, "a hidden layer is not read")
            await safe("()=>window.__a3dTestPaint()")
            ck(await safe("()=>window.__a3dDataDrawn()") == 3 + 2, "nor drawn")
            await nosel()
            await set_field('[data-propdata="vis:%s"]' % zid, True)
            ck((await layers())[2]['visible'] is True, "the box in the group shows it again")
            await set_field('[data-propdata="vis:%s"]' % zid, False)
            ck((await layers())[2]['visible'] is False, "and unticked, hides it")
            await set_field('[data-propdata="vis:%s"]' % zid, True)
            # not on paper
            pngb = b''
            try:
                async with page.expect_download() as dl:
                    await safe("()=>window.__a3dRunAct('m:exportpng')")
                pngb = pathlib.Path(await (await dl.value).path()).read_bytes()
            except Exception as e:
                print('      (download failed: %s)' % str(e)[:120])
            im = Image.open(io.BytesIO(pngb)).convert('RGB') if pngb else None
            mag = 0
            if im:
                for yy in range(0, im.height, 2):
                    for xx in range(0, im.width, 2):
                        p = im.getpixel((xx, yy))
                        if p[0] > 200 and p[1] < 60 and p[2] > 200:
                            mag += 1
            img = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
            mag_s = sum(1 for yy in range(0, img.height, 2) for xx in range(0, img.width, 2)
                        if (lambda p: p[0] > 200 and p[1] < 60 and p[2] > 200)(img.getpixel((xx, yy))))
            ck(im is not None and mag == 0 and mag_s > 0, "on screen the parcels' outlines show (%d), the PNG export has none (%d)" % (mag_s, mag))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. a parcel becomes a property line")
            await safe("()=>window.__a3dMapSet('opacity',60)")   # the step before
            await safe("(i)=>window.__a3dDataSelect(i,0)", lid)
            pid = await safe("()=>window.__a3dDataToProperty()")
            g = await safe("(i)=>window.__a3dPropertyGeometry(i)", pid) or {}
            rg = sorted((round(p[0], 3), round(p[1], 3)) for p in g.get('ring', []))
            ck(pid and rg == sorted((float(x), float(z)) for x, z in PARCEL_A), "Make Property Line: the parcel's corners, to the millimetre (%s)" % rg)
            st = await safe("()=>window.__a3dState()")
            po = [o for o in st['objs'] if o['id'] == pid]
            ck(po and po[0].get('dataSource', {}).get('layer') == 'Parcels Public' and po[0]['dataSource']['props']['PARCELID'] == '001S07-0123' and st['sel'] == pid,
               "it keeps where it came from, and is selected")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(not [o for o in (await safe("()=>window.__a3dState().objs") or []) if o['id'] == pid] and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.6,
               "in one undo step, its own")
            await safe("(i)=>window.__a3dDataSelect(i,0)", tid)
            ck(await safe("()=>window.__a3dDataToProperty()") is None and 'Pick an area' in await toast(), "a tree is not a parcel: said")
            await safe("(i)=>window.__a3dDataSelect(i,2)", lid)
            pid2 = await safe("()=>window.__a3dDataToProperty()")
            g2 = await safe("(i)=>window.__a3dPropertyGeometry(i)", pid2) or {}
            ck(pid2 and sorted((round(p[0], 3), round(p[1], 3)) for p in g2.get('ring', [])) == sorted((float(x), float(z)) for x, z in PARCEL_C),
               "a parcel with a courtyard gives its outer ring")
            await safe("()=>window.__a3dUndo()")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. WFS and GeoJSON")
            W = 'https://geo.example.org/geoserver/wfs?service=WFS&typeNames=city:zoning'
            r = await add(W, 'Zoning (WFS)')
            q = urllib.parse.urlparse(SRV['req'][-1])
            qs = dict(urllib.parse.parse_qsl(q.query))
            ck(r.get('result', {}).get('count') == 1 and q.path == '/geoserver/wfs' and qs.get('service') == 'WFS' and qs.get('version') == '2.0.0' and
               qs.get('request') == 'GetFeature' and qs.get('typeNames') == 'city:zoning' and qs.get('outputFormat') == 'application/json' and
               qs.get('srsName') == 'CRS:84' and qs.get('count') == '2000', "WFS: GetFeature 2.0.0 for its typeNames, as JSON in CRS:84 (%s)" % qs)
            bb = qs.get('bbox', '').split(',')
            ck(len(bb) == 5 and bb[4] == 'CRS:84' and near(float(bb[0]), a['w'], 1e-7) and near(float(bb[3]), a['n'], 1e-7), "on the area, longitude first")
            ck(SRV['req'][-2].endswith('trees.geojson') or any(u == 'https://data.example.org/trees.geojson' for u in SRV['req']), "a GeoJSON file is read as it is")
            F = await safe("(i)=>window.__a3dDataFeatures(i)", tid) or []
            ck([f['p'] for f in F] == [{'species': 'London plane'}, {'name': 'Spring Garden St'}], "and kept to the area: the far oak left out")
            wid = r.get('id')
            await safe("(i)=>window.__a3dDataRemove(i)", wid)

            # ---------------------------------------------------------------------------------
            print("\n-- 7. failures")
            for mode, words in (('arcerr', 'gis.example.org said: Invalid query parameters'), ('500', 'gis.example.org answered HTTP 500'),
                                ('junk', 'gis.example.org sent an answer that does not read'),
                                ('abort', 'gis.example.org could not be reached (offline, or it does not allow browser access)'),
                                ('projected', 'gis.example.org answered in a projected grid (2694000.5, 240000.25), not longitude and latitude')):
                SRV['mode'] = mode
                r = await safe("(i)=>window.__a3dDataFetch(i)", lid) or {}
                L = [x for x in await layers() if x['id'] == lid][0]
                ck(r.get('error') == words and L['status'].get('error') == words and words in await toast() and
                   len(await safe("(i)=>window.__a3dDataFeatures(i)", lid) or []) == 3, "%s: %r, the features kept" % (mode, words))
            await nosel()
            ck('gis.example.org could not be reached' in await props_html() or 'projected grid' in await props_html(), "the group shows why")
            SRV['mode'] = 'ok'
            SRV['more'] = True
            r = await safe("(i)=>window.__a3dDataFetch(i)", lid) or {}
            ck(r.get('more') is True and 'there are more' in await toast(), "more on the server than came: said")
            SRV['more'] = False
            await safe("(i)=>window.__a3dDataFetch(i)", lid)

            # ---------------------------------------------------------------------------------
            print("\n-- 8. credits, remove, a reload, the preset, the command")
            ft = await safe("()=>document.getElementById('a3d-mapattr').innerHTML") or ''
            ck('Data: gis.example.org; City of Philadelphia, PPR' in ft, "the credit line names each shown layer's source (%s)" % ft[:120])
            await safe("(i)=>window.__a3dDataSet(i,'visible',false)", tid)
            await safe("()=>window.__a3dTestPaint()")
            ft = await safe("()=>document.getElementById('a3d-mapattr').innerHTML") or ''
            ck('PPR' not in ft and 'gis.example.org' in ft, "a hidden layer's credit goes with it")
            await safe("(i)=>window.__a3dDataSet(i,'visible',true)", tid)
            await safe("(i)=>window.__a3dDataRemove(i)", zid)
            ck([x['id'] for x in await layers()] == [lid, tid], "Remove takes a layer away")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(len(await layers()) == 3 and len(await safe("(i)=>window.__a3dDataFeatures(i)", zid) or []) == 1, "and an undo brings it back whole, without asking again")
            await page.wait_for_timeout(600)
            n0 = len(ext)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dTestPaint()")
            ck(len(await layers()) == 3 and len(await safe("(i)=>window.__a3dDataFeatures(i)", lid) or []) == 3 and await safe("()=>window.__a3dDataDrawn()") == 6,
               "a reload keeps the layers and their features, and draws them")
            ck(not [u for u in ext[n0:] if 'example.org' in u], "with no request: the project opens offline")
            n0 = len(SRV['req'])
            await nosel()
            await set_field('[data-propdata="preset"]', '0')
            for _ in range(30):
                if not await safe("()=>window.__a3dDataLayers().some(function(l){return window.__a3dDataBusy(l.id);})"):
                    break
                await page.wait_for_timeout(100)
            fl = [x for x in await layers() if 'FEMA' in x['name']]
            ck(fl and fl[0]['url'] == 'https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28' and fl[0]['credit'] == 'FEMA National Flood Hazard Layer' and
               any('/NFHL/MapServer/28/query?' in u for u in SRV['req'][n0:]) and fl[0].get('status', {}).get('count') == 1, "the FEMA preset adds and reads the flood zones")
            await safe("(i)=>window.__a3dDataSelect(i,0)", fl[0]['id'] if fl else '')
            ck('FLD_ZONE' in await props_html() and 'AE' in await props_html(), "a flood zone reads as AE")
            await safe("()=>window.__a3dRunCmd('datalayers')")
            await page.wait_for_timeout(150)
            ck('Data layers are in Properties' in await toast() and await safe("()=>window.__a3dState().sel") is None, "DATALAYERS opens the group")
            cat = await safe("()=>window.__a3dCommandCatalog().filter(c=>c.name==='DATALAYERS').map(c=>c.where.join(' '))") or []
            ck(cat and 'Site' in cat[0], "on the ribbon's Site panel")
            for q_ in ('parcels', 'zoning', 'flood', 'arcgis'):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck('DATALAYERS' in nm[:3], "searching %r finds DATALAYERS (%s)" % (q_, nm))
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
