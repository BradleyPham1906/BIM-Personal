"""site_analysis_fixture.py -- the neighbourhood the V164 suite analyses, and every service Analyze site asks.

A made-up block at 40 N, 75 W, the site at model 0,0 (x east, z south), answered as the real services
answer, so the app reads it as it would them:
  Overpass, the context query (it asks for buildings): a ring of buildings round the site with tagged
    heights -- a 45 m tower to the north-east, a low block to the south-east that the top floor sees
    over -- and the south-west open over a park and a lake; forty small buildings further east, so the
    area reads as urban; a motorway 150 m north, Market Street (primary, 30 mph, four lanes) 40 m
    south, Elm Street and an unnamed street (residential), a footway, a road in a tunnel; a railway
    220 m east; trees; a meadow;
  Overpass, the access query (it asks around a point): the V161 neighbourhood (access_fixture);
  Open-Meteo's archive and air quality, and USGS: climate_fixture, with the zone's UTC offset as
    Open-Meteo gives it (timezone=auto);
  TIGERweb and the Census Data API: access_fixture;
  AWS Terrain Tiles: the V133 ground; AMENDED FOR V165: store['ground'] = 'land', the V165 ground
    (land_fixture);
  Nominatim: one place, the site;
  AMENDED FOR V165: FEMA's flood map: no zone, unless store['flood'] = 'zones' (land_fixture's).
store['mode'] breaks a service: ctx abort|429, clim abort, acc abort, ter abort, geo none|abort, flood abort.
Deterministic: no randomness but the climate fixture's fixed seeds."""
import json, pathlib, re, sys
from urllib.parse import unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import access_fixture as AFX    # noqa: E402
import climate_fixture as CFX   # noqa: E402
from bim_phase133_site_context_browser_tests import m2g, G, ring, terrarium_png, LAT0, LON0   # noqa: E402

UTC_OFFSET = -18000   # America/New_York in winter, as Open-Meteo answers for 40 N, 75 W

# the buildings: (id, name, x0, z0, x1, z1, height, extra tags)
BUILDINGS = [
    (101, 'North Block', -60, -80, -10, -50, 18, {}),
    (102, 'Sample Tower', 30, -90, 60, -60, 45, {}),
    (103, 'East Hall', 50, -20, 80, 20, 12, {}),
    (104, 'West House', -80, -20, -50, 20, 15, {}),
    (105, 'Low Shed', 30, 50, 60, 80, 9, {}),
]
FAR = [(200 + 11 * (k % 8), -60 + 11 * (k // 8)) for k in range(40)]   # forty 6 m sheds, 200..283 m east
LAKE = [(-260, 140), (-150, 140), (-150, 250), (-260, 250)]
PARK = [(-150, 110), (-80, 110), (-80, 200), (-150, 200)]
MEADOW = [(100, 200), (300, 200), (300, 300), (100, 300)]
MOTORWAY = [(-400, -150), (400, -150)]
MARKET = [(-400, 40), (400, 40)]
ELM = [(-100, -300), (-100, 300)]
ALLEY = [(100, -100), (100, 100)]
TUNNEL = [(-200, -20), (-200, 20)]
RAIL = [(220, -300), (220, 300)]
TREES = [(-20, 30), (0, 30), (20, 30)]


def box(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def context():
    def way(i, tags, pts):
        return {'type': 'way', 'id': i, 'tags': tags, 'geometry': G(pts)}

    def node(i, tags, x, z):
        lon, lat = m2g(x, z)
        return {'type': 'node', 'id': i, 'lat': lat, 'lon': lon, 'tags': tags}
    E = []
    for i, nm, x0, z0, x1, z1, h, extra in BUILDINGS:
        t = {'building': 'yes', 'name': nm, 'height': str(h)}
        t.update(extra)
        E.append(way(i, t, ring(box(x0, z0, x1, z1))))
    for k, (x, z) in enumerate(FAR):
        E.append(way(300 + k, {'building': 'shed', 'height': '4'}, ring(box(x, z, x + 6, z + 6))))
    E += [
        way(1001, {'highway': 'motorway', 'ref': 'I 99'}, MOTORWAY),
        way(1002, {'highway': 'primary', 'name': 'Market Street', 'maxspeed': '30 mph', 'lanes': '4'}, MARKET),
        way(1003, {'highway': 'residential', 'name': 'Elm Street'}, ELM),
        way(1004, {'highway': 'residential'}, ALLEY),
        way(1005, {'highway': 'footway'}, [(-40, 0), (40, 0)]),
        way(1006, {'highway': 'secondary', 'tunnel': 'yes', 'name': 'Under Road'}, TUNNEL),
        way(2001, {'railway': 'rail', 'name': 'Main Line'}, RAIL),
        way(4001, {'natural': 'water', 'name': 'Sample Lake'}, ring(LAKE)),
        way(5001, {'leisure': 'park', 'name': 'Mill Park'}, ring(PARK)),
        way(6001, {'landuse': 'meadow'}, ring(MEADOW)),
    ]
    for k, (x, z) in enumerate(TREES):
        E.append(node(7001 + k, {'natural': 'tree', 'height': '8'}, x, z))
    return {'version': 0.6, 'generator': 'Overpass API (fixture)', 'elements': E}


def with_offset(body):
    body = dict(body)
    body['utc_offset_seconds'] = UTC_OFFSET
    body['timezone'] = 'America/New_York'
    return body


HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
OVERPASS = ('https://overpass-api.de/**', 'https://overpass.private.coffee/**', 'https://maps.mail.ru/**', 'https://overpass.kumi.systems/**')
HOSTS = OVERPASS + ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**',
                    'https://tigerweb.geo.census.gov/**', 'https://api.census.gov/**', 'https://s3.amazonaws.com/**',
                    'https://nominatim.openstreetmap.org/**', 'https://hazards.fema.gov/**')   # AMENDED FOR V165: FEMA


def route_handler(store):
    """one handler for every host in HOSTS; store['hits'] keeps (service, url), store['mode'] what to break"""
    acc = AFX.route_handler(store.setdefault('afx', {}))

    async def handle(route):
        u = route.request.url
        mode = store.get('mode', {})
        if '/api/interpreter' in u:
            q = unquote(u)
            svc = 'ctx' if '["building"]' in q else 'acc'
            store.setdefault('hits', []).append((svc, u))
            if mode.get(svc) == 'abort':
                await route.abort('internetdisconnected'); return
            if mode.get(svc) == '429':
                await route.fulfill(status=429, body='busy', headers=HDR); return
            if svc == 'acc':
                await acc(route); return
            await route.fulfill(status=200, body=json.dumps(context()), headers=HDR); return
        if 'tigerweb.geo.census.gov' in u or 'api.census.gov' in u:
            store.setdefault('hits', []).append(('acc', u))
            if mode.get('acc') == 'abort':
                await route.abort('internetdisconnected'); return
            await acc(route); return
        if 'open-meteo.com' in u or 'earthquake.usgs.gov' in u:
            store.setdefault('hits', []).append(('clim', u))
            if mode.get('clim') == 'abort':
                await route.abort('internetdisconnected'); return
            if 'air-quality-api.open-meteo.com' in u:
                body = CFX.air()
            elif 'earthquake.usgs.gov' in u:
                body = CFX.quakes()
            elif 'hourly=' in u:
                body = with_offset(CFX.hourly(int(u.split('start_date=')[1][:4])))
            else:
                body = with_offset(CFX.daily(int(u.split('start_date=')[1][:4]), int(u.split('end_date=')[1][:4])))
            await route.fulfill(status=200, body=json.dumps(body), headers=HDR); return
        if 's3.amazonaws.com' in u:
            store.setdefault('hits', []).append(('ter', u))
            m = re.search(r'/terrarium/(\d+)/(\d+)/(\d+)\.png$', u)
            if mode.get('ter') == 'abort' or not m:
                await route.abort('internetdisconnected'); return
            png = terrarium_png
            if store.get('ground') == 'land':   # AMENDED FOR V165: the V165 ground
                import land_fixture as LFX
                png = LFX.land_png
            await route.fulfill(status=200, body=png(int(m.group(1)), int(m.group(2)), int(m.group(3))), headers={
                'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*',
                'Access-Control-Expose-Headers': 'x-amz-meta-x-imagery-sources', 'x-amz-meta-x-imagery-sources': 'srtm/N39W076.tif'})
            return
        if 'nominatim.openstreetmap.org' in u:
            store.setdefault('hits', []).append(('geo', u))
            if mode.get('geo') == 'abort':
                await route.abort('internetdisconnected'); return
            body = [] if mode.get('geo') == 'none' else [{'lat': str(LAT0), 'lon': str(LON0), 'display_name': '1 Market Street, Sample Town'}]
            await route.fulfill(status=200, body=json.dumps(body), headers=HDR); return
        if 'hazards.fema.gov' in u:   # AMENDED FOR V165: FEMA's National Flood Hazard Layer
            import land_fixture as LFX
            store.setdefault('hits', []).append(('flood', u))
            if mode.get('flood') == 'abort':
                await route.abort('internetdisconnected'); return
            await route.fulfill(status=200, body=json.dumps(LFX.fema_body(store.get('flood', 'none'))), headers=HDR); return
        await route.abort('addressunreachable')
    return handle
