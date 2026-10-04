#!/usr/bin/env python3
"""bim_phase157_site_context_infra_browser_tests.py -- V157: the whole surroundings, in 3D.

The owner (V156): "i want more context from the site than the current one. and the trees and roads and
tunnels, bridges railway and airports. currently we only have buildings." V133 fetched roads, water,
green and trees but drew them flat, as lines and points. Now each comes with a surface: roads as
strips of their width, coloured by use; bridges as decks on piers; tunnels as their line only;
railways, platforms, runways, taxiways and aprons; trees as trunks and crowns, a row as a tree every
8 m; pylons and power lines; land use as a tint. On the terrain, each surface follows the ground.
Overpass and the terrain tiles are answered inside the browser, as in V133 (its fixture helpers are
reused: the ground is linear in the tile pixels, so it is known exactly everywhere).

  1. THE KINDS: four new kinds in the settings, Properties and the query; unticked, gone.
  2. READING THE TAGS: kinds, road use, widths (tag, lanes, class), metres, points along a line.
  3. ONE PRESS: counts, bridges, tunnels, surfaces; the message; the layers.
  4. THE SURFACES: widths, the ground under each point, a bridge's deck and piers, a tunnel with no
     surface, rail and runway, the platform, apron, land use; trees and rows; pylons and the line.
  5. PROPERTIES, THE 3D SCENE, OFF THE GROUND, UNDO.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import (   # noqa: E402  the V133 harness: its ground, its tiles
    Checks, Stalled, within, m2g, G, ring, ground_xz, terrarium_png, LAT0, LON0, near)
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

CK = Checks()
BASE = 120.0   # the ground at model 0,0: the datum
TG = 0.011     # the app keeps the ground to the centimetre, rounded its way

ROAD = [(-100, 5), (0, 5), (100, 5)]
BRIDGE = [(-60, -50), (60, -50)]
TUNNEL = [(-60, -70), (60, -70)]
RAIL = [(-140, 80), (140, 80)]
TRAM = [(-140, 90), (140, 90)]
PLATFORM = [(-20, 84), (20, 84), (20, 86.5), (-20, 86.5)]
RUNWAY = [(-140, -120), (140, -120)]
TAXIWAY = [(-140, -100), (140, -100)]
APRON = [(100, -95), (130, -95), (130, -85), (100, -85)]
FIELD = [(-145, -130), (145, -130), (145, -80), (-145, -80)]
ROW = [(-20, 120), (20, 120)]
LANDUSE = [(60, 40), (120, 40), (120, 70), (60, 70)]


def fixture():
    def way(i, tags, pts):
        return {'type': 'way', 'id': i, 'tags': tags, 'geometry': G(pts)}

    def node(i, tags, x, z):
        lon, lat = m2g(x, z)
        return {'type': 'node', 'id': i, 'lat': lat, 'lon': lon, 'tags': tags}
    return {'version': 0.6, 'generator': 'Overpass API (fixture)', 'elements': [
        way(1001, {'highway': 'residential', 'lanes': '2', 'name': 'Elm Street'}, ROAD),
        way(1002, {'highway': 'footway'}, [(-50, 20), (50, 20)]),
        way(1003, {'highway': 'cycleway', 'width': '2.5'}, [(-50, 30), (50, 30)]),
        way(1004, {'highway': 'secondary', 'bridge': 'yes', 'layer': '2', 'name': 'High Bridge'}, BRIDGE),
        way(1005, {'highway': 'tertiary', 'tunnel': 'yes', 'name': 'Low Road'}, TUNNEL),
        way(1006, {'highway': 'pedestrian'}, [(0, 40), (0, 60)]),
        way(2001, {'railway': 'rail', 'name': 'Main Line'}, RAIL),
        way(2002, {'railway': 'tram'}, TRAM),
        way(2003, {'railway': 'platform'}, ring(PLATFORM)),
        way(2004, {'railway': 'abandoned'}, [(-10, 0), (10, 0)]),
        way(3001, {'aeroway': 'runway', 'ref': '09/27'}, RUNWAY),
        way(3002, {'aeroway': 'taxiway'}, TAXIWAY),
        way(3003, {'aeroway': 'apron'}, ring(APRON)),
        way(3004, {'aeroway': 'aerodrome', 'name': 'Field Airport'}, ring(FIELD)),
        node(4001, {'natural': 'tree', 'species': 'Acer', 'height': '12'}, 10, 10),
        way(4002, {'natural': 'tree_row'}, ROW),
        node(5001, {'power': 'tower'}, -100, 140),
        node(5002, {'power': 'tower', 'height': '30'}, 100, 140),
        way(5003, {'power': 'line'}, [(-100, 140), (100, 140)]),
        way(6001, {'landuse': 'residential'}, ring(LANDUSE)),
        way(6002, {'landuse': 'farmland'}, ring([(-140, 40), (-120, 40), (-120, 60), (-140, 60)])),
    ]}


SRV = {'ovp': [], 'ter': [], 'ext': []}


def gy(x, z):
    """the model height of the ground under x, z, as the app rounds it (cm)"""
    return round((ground_xz(x, z) - BASE) * 100) / 100


def pairs(m):
    """a strip's vertex pairs: (left, right, centre)"""
    v = m['v']
    out = []
    for i in range(0, len(v) - 1, 2):
        a, b = v[i], v[i + 1]
        out.append((a, b, ((a[0] + b[0]) / 2, (a[2] + b[2]) / 2)))
    return out


def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2)


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        def on_req(r):
            u = r.url
            if not (u.startswith('file:') or u.startswith('data:') or u.startswith('blob:')):
                SRV['ext'].append(u)
        page.on('request', on_req)

        async def ovp_route(route):
            SRV['ovp'].append(route.request.url)
            await route.fulfill(status=200, body=json.dumps(fixture()),
                                headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
        for host in ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**',
                     'https://overpass.kumi.systems/**'):
            await ctx.route(host, ovp_route)

        async def ter_route(route):
            u = route.request.url
            SRV['ter'].append(u)
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', u)
            if not m:
                await route.abort('internetdisconnected')
                return
            await route.fulfill(status=200, body=terrarium_png(int(m.group(1)), int(m.group(2)), int(m.group(3))), headers={
                'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*',
                'Access-Control-Expose-Headers': 'x-amz-meta-x-imagery-sources', 'x-amz-meta-x-imagery-sources': 'srtm/N39W076.tif'})
        await ctx.route('https://s3.amazonaws.com/**', ter_route)

        await within(page.goto('file://' + str(HTML)), 'goto')
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

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def props_of(i):
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", i)
            await page.wait_for_timeout(60)
            return await props_html()

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(120)
            return ok

        async def objs():
            return await safe("()=>window.__a3dState().objs") or []

        async def ctx_objs(kind=None):
            return [o for o in await objs() if o.get('context') and (kind is None or o['context']['kind'] == kind)]

        async def by_osm(i):
            for o in await ctx_objs():
                if o['context'].get('id') == i:
                    return o
            return None

        async def fetch():
            return await safe("()=>Promise.resolve(window.__a3dCtxFetch())")

        try:
            has = await safe("()=>window.__acad3dV157")
            ck(bool(has) and 'bridgedeck' in has and 'trees3d' in has, "__acad3dV157 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 157, "the app says V157 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V157')

            # ---------------------------------------------------------------------------------
            print("\n-- 1. the kinds")
            NEW = ('rail', 'airports', 'power', 'landuse')
            st = await safe("()=>window.__a3dCtxSettings()") or {}
            ck(all(st.get('kinds', {}).get(k) is True for k in NEW) and len(st.get('kinds', {})) == 10,
               "four new kinds, ticked by default: rail, airports, power, land use (%s)" % st.get('kinds'))
            await nosel()
            h = await props_html()
            ck(all('data-propctx="kind:%s"' % k in h for k in NEW), "a box for each in the Site Context group")
            ck(SRV['ext'] == [], "nothing asked of any server on the way up")
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            q = await safe("()=>window.__a3dCtxQuery()") or ''
            for w, what in (('way["natural"="tree_row"]', 'tree rows'),
                            ('way["railway"~"^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$"]', 'railways, trams, subways, platforms'),
                            ('way["aeroway"~"^(runway|taxiway|apron|aerodrome|helipad)$"]', 'runways, taxiways, aprons, aerodromes'),
                            ('relation["aeroway"="aerodrome"]', 'an aerodrome as a relation'),
                            ('way["power"="line"]', 'power lines'), ('node["power"="tower"]', 'pylons'),
                            ('way["landuse"~"^(residential|commercial|retail|industrial|railway|construction)$"]', 'land use')):
                ck(w in q, "the query asks for %s" % what)
            for k in NEW:
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,false)", k)
            q2 = await safe("()=>window.__a3dCtxQuery()") or ''
            ck('railway' not in q2 and 'aeroway' not in q2 and 'power' not in q2 and 'residential|commercial' not in q2 and 'way["highway"]' in q2,
               "unticked, each leaves the query; the rest stay")
            for k in NEW:
                await safe("(k)=>window.__a3dCtxSet('kind:'+k,true)", k)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. reading the tags")
            for el, want in ((('way', {'railway': 'rail'}), 'rail'), (('way', {'railway': 'subway', 'tunnel': 'yes'}), 'rail'),
                             (('way', {'railway': 'abandoned'}), ''), (('way', {'aeroway': 'runway'}), 'airports'),
                             (('way', {'aeroway': 'gate'}), ''), (('node', {'power': 'tower'}), 'power'),
                             (('way', {'power': 'line'}), 'power'), (('way', {'power': 'cable'}), ''),
                             (('way', {'natural': 'tree_row'}), 'trees'), (('way', {'landuse': 'industrial'}), 'landuse'),
                             (('way', {'landuse': 'farmland'}), ''), (('way', {'landuse': 'grass'}), 'green'),
                             (('way', {'highway': 'primary', 'bridge': 'yes'}), 'roads')):
                got = await safe("(e)=>window.__a3dOsmKind({type:e[0],tags:e[1]})", list(el))
                ck(got == want, "%s %s: %r (%r)" % (el[0], el[1], want, got))
            for tags, use in (({'highway': 'primary'}, 'car'), ({'highway': 'residential'}, 'car'), ({'highway': 'pedestrian'}, 'pedestrian'),
                              ({'highway': 'living_street'}, 'pedestrian'), ({'highway': 'footway'}, 'footway'), ({'highway': 'steps'}, 'footway'),
                              ({'highway': 'cycleway'}, 'cycleway'), ({'highway': 'track'}, 'path'), ({'highway': 'path'}, 'path')):
                ck(await safe("(t)=>window.__a3dRoadUse(t)", tags) == use, "a %s is a %s" % (tags['highway'], use))
            for v, m in (('7', 7), ('7 m', 7), ('7.5m', 7.5), ("23'", 7.0104), ('20 ft', 6.096), ('3,5', 3.5),
                         ('wide', None), ('', None), ('0', None), ('-4', None), ('900', None)):
                got = await safe("(v)=>window.__a3dTagMetres(v)", v)
                ck((got is None and m is None) or near(got, m, 1e-9), "width %r: %s (%s)" % (v, m, got))
            for kind, tags, w in (('roads', {'highway': 'primary', 'width': '9.5', 'lanes': '4'}, 9.5),
                                  ('roads', {'highway': 'primary', 'lanes': '4'}, 13.2), ('roads', {'highway': 'residential', 'lanes': '1'}, 3.3),
                                  ('roads', {'highway': 'footway', 'lanes': '0'}, 2), ('roads', {'highway': 'primary'}, 11),
                                  ('roads', {'highway': 'motorway'}, 14), ('roads', {'highway': 'service'}, 4),
                                  ('roads', {'highway': 'mystery'}, 5), ('rail', {'railway': 'rail'}, 3.2), ('rail', {'railway': 'tram'}, 2.6),
                                  ('airports', {'aeroway': 'runway'}, 45), ('airports', {'aeroway': 'runway', 'width': '30'}, 30),
                                  ('airports', {'aeroway': 'taxiway'}, 18)):
                got = await safe("(a)=>window.__a3dCtxWidth(a[0],a[1])", [kind, tags])
                ck(near(got, w, 1e-9), "%s %s: %g m wide (%s)" % (kind, tags, w, got))
            al = await safe("()=>window.__a3dCtxAlong([[0,0],[10,0],[10,30]],8)") or []
            ck([tuple(round(c, 9) for c in p) for p in al] == [(0, 0), (8, 0), (10, 6), (10, 14), (10, 22), (10, 30)],
               "points every 8 m along a line, round its corner, its end included (%s)" % al)
            al = await safe("()=>window.__a3dCtxAlong([[0,0],[39.9999,0]],8)") or []
            ck(len(al) == 6 and near(al[-1][0], 39.9999, 1e-9) and near(al[1][0], 39.9999 / 5, 1e-9),
               "a row a hair short of 40 m: still six, evenly, its last at its end (%s)" % [round(p[0], 4) for p in al])
            al = await safe("()=>window.__a3dCtxAlong([[0,0],[3,0]],8)") or []
            ck(len(al) == 2, "a row shorter than the step: a tree at each end")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. one press")
            await safe("()=>window.__a3dTestSetObjs([])")
            r = await fetch() or {}
            want = {'buildings': 0, 'roads': 6, 'water': 0, 'green': 0, 'trees': 7, 'rail': 3, 'airports': 4, 'power': 3, 'landuse': 1, 'terrain': 1}
            ck(r.get('counts') == want and not r.get('errors'),
               "6 roads, 7 trees (one and a row of six), 3 railways, 4 airport parts, 3 power, 1 land use, the terrain (%s)" % r.get('counts'))
            ck(r.get('bridges') == 1 and r.get('tunnels') == 1 and r.get('surfaces') == 12,
               "1 bridge, 1 tunnel, 12 surfaces (%s, %s, %s)" % (r.get('bridges'), r.get('tunnels'), r.get('surfaces')))
            tt = await toast()
            ck('3 railways' in tt and '4 airports' in tt and '3 power' in tt and '1 land use' in tt and '7 trees' in tt,
               "the message counts each kind (%r)" % tt)
            ck('1 bridge raised' in tt and '1 tunnel below ground' in tt, "and says a bridge was raised and a tunnel is below ground")
            ck(await safe("()=>window.__a3dCtxDatum()") == BASE, "the datum: the ground at model 0,0 (120 m)")
            L = await safe("()=>window.__a3dLayers()") or []
            byid = {l['id']: l for l in L}
            par = [l for l in L if l['name'] == 'Context']
            kids = {l['name'] for l in L if par and l.get('parent') == par[0]['id']}
            ck(all('Context ' + k in kids for k in NEW), "a sub-layer for each new kind (%s)" % sorted(kids))
            co = await ctx_objs()
            ck(co and all(byid.get(o['layer'], {}).get('name') == 'Context ' + o['context']['kind'] for o in co) and all(o.get('locked') for o in co),
               "every object on its kind's layer, pinned")
            ck(await by_osm(2004) is None and await by_osm(6002) is None, "an abandoned railway and farmland are not brought")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the surfaces")
            rd = await by_osm(1001)
            m = (rd or {}).get('mesh') or {'v': [], 'f': []}
            P = pairs(m)
            ck(rd and rd['t'] == 'sketch' and len(rd['pts']) == 3 and len(m['v']) == 6 and len(m['f']) == 2,
               "a road keeps its centre line, the element, and carries its surface: two quads along three points")
            ck(P and all(near(dist(a, b), 6.6, 1e-6) for a, b, _ in P), "6.6 m wide: its two lanes at 3.3 m (%s)" % [round(dist(a, b), 4) for a, b, _ in P])
            ck(P and all(near(c[0], p[0], 1e-6) and near(c[1], p[1], 1e-6) for (_, _, c), p in zip(P, ROAD)), "centred on its line")
            ys = [(a[1], gy(c[0], c[1]) + 0.05) for a, _, c in P] + [(b[1], gy(c[0], c[1]) + 0.05) for _, b, c in P]
            ck(ys and all(near(y, w, TG) for y, w in ys), "each point 5 cm over the ground under it, so the road follows the terrain (%s)" % ys)
            ck(len(set(round(y, 3) for y, _ in ys)) > 1, "(the ground here is not flat: the heights differ)")
            ck(rd['col'] == '#6e737a' and rd['context'].get('use') == 'car' and near(rd['context'].get('width'), 6.6, 1e-9),
               "a car road, in the car road's grey")
            for i, col, use, w in ((1002, '#8cbf86', 'footway', 2), (1003, '#5fa8d3', 'cycleway', 2.5), (1006, '#cdb98d', 'pedestrian', 6)):
                o = await by_osm(i) or {}
                pp = pairs(o.get('mesh') or {'v': []})
                ck(o.get('col') == col and o.get('context', {}).get('use') == use and pp and near(dist(pp[0][0], pp[0][1]), w, 1e-6),
                   "a %s: its colour, %g m wide (%s, %s)" % (use, w, o.get('col'), pp and round(dist(pp[0][0], pp[0][1]), 4)))
            # the bridge
            br = await by_osm(1004) or {}
            bm = br.get('mesh') or {'v': [], 'f': []}
            bc = br.get('context', {})
            ck(br.get('name') == 'Bridge: High Bridge' and bc.get('bridge') is True and bc.get('deck') == 12,
               "a bridge on layer 2: named so, its deck 12 m up (%s, %s)" % (br.get('name'), bc.get('deck')))
            top = bm['v'][:4]
            bot = bm['v'][4:8]
            ck(len(top) == 4 and all(near(v[1], gy(c[0], c[1]) + 12, TG) for v, c in zip(top, (BRIDGE[0], BRIDGE[0], BRIDGE[1], BRIDGE[1]))),
               "its deck 12 m over the ground at each end (%s)" % [round(v[1], 3) for v in top])
            ck(len(bot) == 4 and all(near(t[1] - b[1], 0.8, 1e-9) for t, b in zip(top, bot)), "a slab 0.8 m thick")
            npier = (len(bm['v']) - 8) // 8
            ck(npier == 4 and (len(bm['v']) - 8) % 8 == 0, "piers every 30 m from 15 m: four along 120 m (%s)" % npier)
            pv = bm['v'][8:]
            pier_ok = True
            for k in range(npier):
                b8 = pv[k * 8:k * 8 + 8]
                cx = sum(v[0] for v in b8) / 8
                cz = sum(v[2] for v in b8) / 8
                lo = min(v[1] for v in b8)
                hi = max(v[1] for v in b8)
                pier_ok = pier_ok and near(cx, -60 + 15 + 30 * k, 1e-6) and near(cz, -50, 1e-6) and near(lo, gy(cx, cz), TG) and near(hi, gy(cx, cz) + 12 - 0.8, TG)
            ck(npier and pier_ok, "each pier from the ground up to the deck's underside, at 15, 45, 75 and 105 m")
            ck(len(bm['f']) == 1 + 1 + 2 + 2 + 6 * npier, "deck faces: top, bottom, two sides, two ends; six to a pier (%s)" % len(bm['f']))
            tn = await by_osm(1005) or {}
            ck(tn.get('name') == 'Tunnel: Low Road' and tn.get('context', {}).get('tunnel') is True and not tn.get('mesh'),
               "a tunnel: named so, its centre line only, no surface on the ground")
            # rail, platform
            rl = await by_osm(2001) or {}
            rp = pairs(rl.get('mesh') or {'v': []})
            ck(rp and near(dist(rp[0][0], rp[0][1]), 3.2, 1e-6) and near(rp[0][0][1], gy(*RAIL[0]) + 0.08, TG) and rl.get('col') == '#8d7b68',
               "a railway: 3.2 m, 8 cm over the ground, in rail brown")
            tr = await by_osm(2002) or {}
            tp = pairs(tr.get('mesh') or {'v': []})
            ck(tp and near(dist(tp[0][0], tp[0][1]), 2.6, 1e-6), "a tram: 2.6 m")
            pf = await by_osm(2003) or {}
            pm = pf.get('mesh') or {'v': []}
            ck(pf.get('t') == 'sketch' and pf.get('closed') is not False and pm['v'] and
               near(max(v[1] for v in pm['v']) - min(v[1] for v in pm['v']), 1, 1e-6),
               "a platform: its outline, standing 1 m high")
            # airports
            rw = await by_osm(3001) or {}
            rwp = pairs(rw.get('mesh') or {'v': []})
            ck(rw.get('name') == '09/27' and rwp and near(dist(rwp[0][0], rwp[0][1]), 45, 1e-6) and near(rwp[0][0][1], gy(*RUNWAY[0]) + 0.03, TG),
               "a runway: named by its ref, 45 m wide, on the ground")
            tw = await by_osm(3002) or {}
            twp = pairs(tw.get('mesh') or {'v': []})
            ck(twp and near(dist(twp[0][0], twp[0][1]), 18, 1e-6), "a taxiway: 18 m")
            ap = await by_osm(3003) or {}
            ck((ap.get('mesh') or {}).get('v'), "an apron: a surface")
            fd = await by_osm(3004) or {}
            ck(fd.get('name') == 'Field Airport' and fd.get('closed') is not False and not fd.get('mesh'),
               "an aerodrome: its boundary, no surface over the whole field")
            # land use
            lu = await by_osm(6001) or {}
            lm = lu.get('mesh') or {'v': []}
            lc = (sum(p[0] for p in LANDUSE) / 4, sum(p[1] for p in LANDUSE) / 4)
            ck(lu.get('col') == '#d9cfb4' and lm['v'] and near(max(v[1] for v in lm['v']), gy(*lc) + 0.02, TG),
               "residential land: a tint at the ground, under the roads")
            # trees
            trees = await ctx_objs('trees')
            ac = [o for o in trees if o['context'].get('id') == 4001]
            rows = sorted([o for o in trees if o['context'].get('id') == 4002], key=lambda o: o['pts'][0][0])
            ck(len(ac) == 1 and len(rows) == 6 and all(o['context'].get('row') for o in rows),
               "one tree, and a row of six along 40 m")
            ck([round(o['pts'][0][0], 6) for o in rows] == [-20, -12, -4, 4, 12, 20], "a tree every 8 m, from end to end")
            a1 = ac[0] if ac else {}
            am = a1.get('mesh') or {'v': [], 'f': []}
            base = gy(10, 10)
            ck(len(am['v']) == 24 and len(am['f']) == 26, "a trunk of six sides and a crown of twenty faces")
            ck(am['v'] and near(min(v[1] for v in am['v']), base, TG) and 11 < max(v[1] for v in am['v']) - base <= 12,
               "standing on the ground, up to its height tag, 12 m (%s)" % (am['v'] and round(max(v[1] for v in am['v']) - base, 3)))
            ck(a1.get('name') == 'Acer 1' and a1.get('kind') == 'point' and a1.get('context', {}).get('height') == 12, "named by its species, still a point")
            rm = rows[0].get('mesh') if rows else None
            ck(rm and 7 < max(v[1] for v in rm['v']) - min(v[1] for v in rm['v']) <= 8, "a tree with no height: 8 m")
            # power
            py = sorted(await ctx_objs('power'), key=lambda o: (o['pts'][0][0] if o.get('kind') == 'point' else 1e9))
            pyl = [o for o in py if o.get('kind') == 'point']
            ln = [o for o in py if o.get('kind') != 'point']
            hts = [round(max(v[1] for v in o['mesh']['v']) - min(v[1] for v in o['mesh']['v']), 6) for o in pyl if o.get('mesh')]
            ck(len(pyl) == 2 and hts == [25, 30], "two pylons: 25 m, or as tall as tagged (%s)" % hts)
            ck(pyl and pyl[0].get('name') == 'Pylon 1' and near(min(v[1] for v in pyl[0]['mesh']['v']), gy(-100, 140), TG), "on the ground")
            ck(len(ln) == 1 and ln[0].get('y') == 20 and not ln[0].get('mesh'), "the line strung 20 m up between them, a line")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Properties, the 3D scene, off the ground, undo")
            h = await props_of(rd['id'])
            ck('car road' in h and '6.6 m' in h, "a road's page: its use and width")
            h = await props_of(br.get('id'))
            ck('its deck 12 m above the ground, on piers every 30 m' in h, "a bridge's page: its deck and piers")
            ck('below ground: its centre line only' in await props_of(tn.get('id')), "a tunnel's page says it is below ground")
            h = await props_of(a1.get('id'))
            ck('12 m, crown 7.2 m across' in h, "a tree's page: its height and crown")
            ck('in a row, a tree every 8 m' in await props_of(rows[0]['id'] if rows else ''), "a row tree's page says so")
            await nosel()
            await safe("()=>{window.__a3dRunCmd('3d');window.__a3dRunCmd('zoomextents');}")
            await page.wait_for_timeout(500)
            t1 = await safe("(i)=>window.__a3dGlTableOf(i)", rd['id'])
            ck(t1 and t1[3] == 1 and near(t1[4], 0x6e / 255, TG) and near(t1[5], 0x73 / 255, TG) and near(t1[6], 0x7a / 255, TG),
               "in the 3D scene: the road is drawn, opaque, in its colour (%s)" % t1)
            t2 = await safe("(i)=>window.__a3dGlTableOf(i)", a1.get('id'))
            ck(t2 and t2[3] == 1, "and the tree")
            ck(not await safe("(i)=>window.__a3dGlTableOf(i)", tn.get('id')), "the tunnel has no surface to draw")
            # off the ground: flat
            await safe("()=>window.__a3dRunCmd('2d')")
            await nosel()
            await safe("()=>window.__a3dCtxSet('onGround',false)")
            r2 = await fetch() or {}
            rd2 = await by_osm(1001) or {}
            ys2 = [v[1] for v in (rd2.get('mesh') or {'v': []})['v']]
            ck(r2.get('counts', {}).get('roads') == 6 and ys2 and all(near(y, 0.05, 1e-9) for y in ys2),
               "not on the ground: the road flat, 5 cm over the level (%s)" % sorted(set(ys2)))
            br2 = await by_osm(1004) or {}
            ck(br2.get('mesh') and all(near(v[1], 12, 1e-9) for v in br2['mesh']['v'][:4]), "the bridge deck 12 m over the level")
            ck(len(await ctx_objs()) == len(co), "a fresh fetch replaces what the last one brought, nothing doubled (%s, %s)" % (len(await ctx_objs()), len(co)))
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            rd3 = await by_osm(1001) or {}
            ck(rd3.get('mesh') and len(set(round(v[1], 3) for v in rd3['mesh']['v'])) > 1, "one undo brings the draped road back")
            await safe("()=>{window.__a3dUndo();window.__a3dUndo();}")
            await page.wait_for_timeout(100)
            ck(len(await ctx_objs()) == 0, "and, the setting undone, one more takes the whole context away")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(100)
            ck(len(await ctx_objs()) == len(co), "redo brings it back, surfaces and all")
            ck(await safe("()=>window.__a3dCtxRemove()") == len(co) and len(await ctx_objs()) == 0, "CONTEXTREMOVE takes every kind")
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'railway') or [])]
            ck('CONTEXT' in nm[:2], "searching 'railway' finds CONTEXT (%s)" % nm)
            nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", 'bridges') or [])]
            ck('CONTEXT' in nm[:2], "searching 'bridges' finds CONTEXT (%s)" % nm)
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the harness raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
