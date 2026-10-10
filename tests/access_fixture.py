"""access_fixture.py -- a made-up but realistic neighbourhood for the V161 suite: a street grid with its
places, parks, stops and routes, and a census tract in its county and state.

Shaped exactly as the real services answer: Overpass's JSON (ways out body geom, places out center,
parks out geom, route relations with their members), TIGERweb's identify, and the Census Data API's
arrays of strings. Everything is laid out in model metres (x east, z south, the site at 0,0) and
turned into latitude and longitude with the app's own local projection, so the suite can work out
every walk time exactly. Deterministic: no randomness at all.

What the grid holds, each to be tested:
- avenues every 120 m (x = 60 + 120k), streets every 100 m (z = 100k), out to 1,800 m;
- Market Street (z = 0, primary, 30 mph, 4 lanes, sidewalks both) in front of the lot, 5th Street
  (x = 60, secondary) beside it with its sidewalks mapped separately, and an unnamed alley behind;
- Broad Avenue (z = 300) divided: two one-way carriageways 8 m apart;
- Elm Court, a Y-shaped cul-de-sac (its junctions lead only to dead ends);
- Hill Steps, slower to walk than the grid around them;
- an expressway and a private drive, each a shortcut were it walkable (neither is), and Hospital
  Drive (private, but foot=yes: walkable);
- a footbridge over the lot (a bridge is not the ground the lot opens onto);
- no place or stop as near to two streets at once (its walk would be either's);
- places of every kind, a park whose walk is to its edge, a park with a hole as a relation, a
  private garden, places too far away; bus stops on both sides of a street, a metro station with its
  entrances, a tram stop, a stop known by its ref, routes in both directions."""
import json, math, re
from urllib.parse import urlparse, parse_qs, unquote

LAT0, LON0 = 40.0, -75.0
A_WGS, E2, D2R = 6378137.0, 0.00669437999014, math.pi / 180


def _radii(lat):
    s = math.sin(lat * D2R)
    w = 1 - E2 * s * s
    return A_WGS * (1 - E2) / w ** 1.5, A_WGS / math.sqrt(w)


M_R, N_R = _radii(LAT0)


def to_ll(x, z):
    """model (x east, z south) to (lat, lon), as the app's bimModelToGeo with true north 0"""
    return LAT0 + (-z) / M_R / D2R, LON0 + x / (N_R * math.cos(LAT0 * D2R)) / D2R


AVES = [60 + 120 * k for k in range(-15, 15)]          # -1740 .. 1740
STREETS = [100 * k for k in range(-17, 18) if k != 3]   # z = 300 is Broad Avenue, divided
EXT = 1800
LOT = [(10, -40), (50, -40), (50, -10), (10, -10)]      # the lot: 40 m along Market Street, 30 m deep


class Net:
    def __init__(self):
        self.ids, self.xy, self.ways, self.n, self.w = {}, {}, [], 100000, 500000

    def node(self, x, z):
        k = (round(x, 4), round(z, 4))
        if k not in self.ids:
            self.n += 1
            self.ids[k] = self.n
            self.xy[self.n] = (float(x), float(z))
        return self.ids[k]

    def way(self, pts, tags):
        self.w += 1
        self.ways.append({'id': self.w, 'tags': dict(tags), 'ids': [self.node(x, z) for x, z in pts]})
        return self.w


def build():
    N = Net()
    # streets east-west
    extra_ew = {0: [55, 65], -100: [55, 65, 240]}
    for z in STREETS:
        xs = sorted(set([-EXT, EXT] + AVES + extra_ew.get(z, [])))
        if z == 0:
            tags = {'highway': 'primary', 'name': 'Market Street', 'maxspeed': '30 mph', 'lanes': '4', 'sidewalk': 'both', 'cycleway': 'lane'}
        elif z in (-400, 400):
            tags = {'highway': 'secondary', 'name': ('North' if z < 0 else 'South') + ' Boulevard'}
        else:
            tags = {'highway': 'residential', 'name': '%s%d Street' % ('N' if z < 0 else 'S', abs(z) // 100)}
        N.way([(x, z) for x in xs], tags)
    for z in (296, 304):   # Broad Avenue, divided
        xs = sorted(set([-EXT, EXT] + AVES))
        N.way([(x, z) for x in (xs if z == 296 else xs[::-1])], {'highway': 'secondary', 'name': 'Broad Avenue', 'oneway': 'yes'})
    # avenues north-south
    extra_ns = {-60: [-25, -50], 60: [-25, -50]}
    for k, x in enumerate(AVES):
        zs = sorted(set([-EXT, EXT] + STREETS + [296, 304] + extra_ns.get(x, [])))
        if x == 60:
            tags = {'highway': 'secondary', 'name': '5th Street', 'maxspeed': '25 mph', 'lanes': '2'}
        else:
            tags = {'highway': 'tertiary' if k % 2 else 'residential', 'name': 'Avenue %d' % (k + 1)}
        N.way([(x, z) for z in zs], tags)
    N.way([(-60, -50), (60, -50)], {'highway': 'service', 'service': 'alley'})
    N.way([(240, -100), (240, -150)], {'highway': 'residential', 'name': 'Elm Court'})
    N.way([(240, -150), (220, -180)], {'highway': 'residential', 'name': 'Elm Court'})
    N.way([(240, -150), (260, -180)], {'highway': 'residential', 'name': 'Elm Court'})
    N.way([(300, -300), (420, -400)], {'highway': 'steps', 'name': 'Hill Steps'})
    N.way([(60, 0), (660, -600)], {'highway': 'motorway', 'name': 'Expressway', 'oneway': 'yes'})   # a shortcut, were it walkable
    N.way([(60, -100), (180, -200)], {'highway': 'service', 'access': 'private'})                   # likewise
    N.way([(300, 0), (420, -100)], {'highway': 'service', 'access': 'private', 'foot': 'yes', 'name': 'Hospital Drive'})
    N.way([(-60, -25), (60, -25)], {'highway': 'footway', 'bridge': 'yes', 'layer': '1', 'name': 'Skybridge'})
    N.way([(55, 0), (55, -100)], {'highway': 'footway', 'footway': 'sidewalk'})
    N.way([(65, 0), (65, -100)], {'highway': 'footway', 'footway': 'sidewalk'})
    return N


NET = build()

# the places: (osm type, key, value, name, (x, z)); a way's point is its centre
PLACES = [
    ('node', 'shop', 'supermarket', 'Fresh Market', (200, 30)),
    ('way', 'shop', 'convenience', 'Corner Shop', (-95, -60)),
    ('node', 'shop', 'bakery', 'Far Bakery', (1500, 1500)),
    ('node', 'amenity', 'pharmacy', 'Main Pharmacy', (365, -52)),     # beside Hospital Drive
    ('node', 'amenity', 'clinic', 'Riverside Clinic', (665, -600)),   # where the expressway comes down
    ('way', 'amenity', 'hospital', 'General Hospital', (-700, 290)),
    ('way', 'amenity', 'school', 'Hill School', (-300, -400)),
    ('node', 'amenity', 'library', 'Public Library', (500, 100)),
    ('node', 'leisure', 'playground', 'Little Playground', (100, -150)),
    ('node', 'amenity', 'cafe', 'Corner Cafe', (32.5, 10)),   # across Market Street, between two of the app's 5 m cuts
    ('node', 'amenity', 'cafe', 'Bridge Cafe', (-70, -25)),   # where the footbridge lands: nearer, were a bridge the lot's ground
    ('node', 'amenity', 'restaurant', 'Bistro', (300, -250)),
    ('node', 'amenity', 'fast_food', 'Burger Bar', (-420, 80)),
    ('node', 'amenity', 'bank', 'Savings Bank', (0, 60)),
    ('node', 'amenity', 'post_office', 'Post Office', (-180, -180)),
    ('node', 'amenity', 'place_of_worship', 'Far Chapel', (2000, 0)),
]
PARK = [(545, -395), (655, -395), (655, -305), (545, -305)]            # Riverside Park, a way
GARDEN = [(-170, -190), (-70, -190), (-70, -110), (-170, -110)]         # a private garden
COMMONS_OUT = [(-535, 205), (-425, 205), (-425, 295), (-535, 295)]      # the Commons, a relation
COMMONS_IN = [(-500, 230), (-460, 230), (-460, 270), (-500, 270)]
# the stops: id, tags, (x, z)
STOPS = [
    (900001, {'highway': 'bus_stop', 'public_transport': 'platform', 'bus': 'yes', 'name': 'Market St & 5th St'}, (70, -8)),
    (900002, {'highway': 'bus_stop', 'public_transport': 'platform', 'bus': 'yes', 'name': 'Market St & 5th St'}, (70, 8)),
    (900003, {'public_transport': 'stop_position', 'bus': 'yes'}, (70, 0)),
    (900004, {'highway': 'bus_stop', 'public_transport': 'platform', 'name': 'Market St & 3rd St'}, (-170, 8)),
    (900005, {'railway': 'station', 'station': 'subway', 'public_transport': 'station', 'subway': 'yes', 'name': 'Central Station'}, (480, -640)),
    (900006, {'railway': 'subway_entrance'}, (420, -560)),
    (900007, {'railway': 'subway_entrance'}, (560, -640)),
    (900008, {'railway': 'tram_stop', 'public_transport': 'platform', 'tram': 'yes', 'name': 'Library Tram'}, (500, 110)),
    (900009, {'highway': 'bus_stop', 'ref': 'B7'}, (-420, -300)),
    (900010, {'railway': 'halt', 'name': 'Northside Halt'}, (-900, -900)),
]
ROUTES = [
    (800001, {'type': 'route', 'route': 'bus', 'ref': '12', 'name': 'Bus 12: eastbound'}, [900001, 900003, 900004]),
    (800002, {'type': 'route', 'route': 'bus', 'ref': '12', 'name': 'Bus 12: westbound'}, [900002, 900004]),
    (800003, {'type': 'route', 'route': 'bus', 'ref': '42', 'name': 'Bus 42'}, [900001, 900002]),
    (800004, {'type': 'route', 'route': 'subway', 'ref': 'A', 'name': 'Line A'}, [900005]),
    (800005, {'type': 'route', 'route': 'tram', 'ref': 'T1', 'name': 'Tram T1'}, [900008]),
    (800006, {'type': 'route', 'route': 'bus', 'ref': '7', 'name': 'Bus 7'}, [900009]),
    (800007, {'type': 'route', 'route': 'train', 'ref': 'R', 'name': 'Northside line'}, [900010]),
]


def _g(x, z):
    la, lo = to_ll(x, z)
    return {'lat': round(la, 9), 'lon': round(lo, 9)}


def _bounds(pts):
    L = [to_ll(x, z) for x, z in pts]
    return {'minlat': min(p[0] for p in L), 'minlon': min(p[1] for p in L), 'maxlat': max(p[0] for p in L), 'maxlon': max(p[1] for p in L)}


def overpass(drop_ways=False, remark=None):
    """the answer to the app's one request, in the order its out statements print"""
    E = []
    if not drop_ways:
        for w in NET.ways:
            pts = [NET.xy[i] for i in w['ids']]
            E.append({'type': 'way', 'id': w['id'], 'bounds': _bounds(pts), 'nodes': list(w['ids']),
                      'geometry': [_g(x, z) for x, z in pts], 'tags': w['tags']})
    pid = 700000
    for typ, k, v, name, (x, z) in PLACES:
        pid += 1
        if typ == 'node':
            g = _g(x, z)
            E.append({'type': 'node', 'id': pid, 'lat': g['lat'], 'lon': g['lon'], 'tags': {k: v, 'name': name}})
    for typ, k, v, name, (x, z) in PLACES:
        if typ == 'way':
            pid += 1
            E.append({'type': 'way', 'id': pid, 'center': _g(x, z), 'tags': {k: v, 'name': name, 'building': 'yes'}})
    ring = PARK + PARK[:1]
    E.append({'type': 'way', 'id': 710001, 'bounds': _bounds(ring), 'nodes': [720000 + i for i in range(4)] + [720000],
              'geometry': [_g(x, z) for x, z in ring], 'tags': {'leisure': 'park', 'name': 'Riverside Park'}})
    ring = GARDEN + GARDEN[:1]
    E.append({'type': 'way', 'id': 710002, 'bounds': _bounds(ring), 'nodes': [721000 + i for i in range(4)] + [721000],
              'geometry': [_g(x, z) for x, z in ring], 'tags': {'leisure': 'park', 'access': 'private', 'name': 'Private Garden'}})
    E.append({'type': 'relation', 'id': 710003, 'bounds': _bounds(COMMONS_OUT),
              'members': [{'type': 'way', 'ref': 730001, 'role': 'outer', 'geometry': [_g(x, z) for x, z in COMMONS_OUT + COMMONS_OUT[:1]]},
                          {'type': 'way', 'ref': 730002, 'role': 'inner', 'geometry': [_g(x, z) for x, z in COMMONS_IN + COMMONS_IN[:1]]}],
              'tags': {'type': 'multipolygon', 'leisure': 'park', 'name': 'The Commons'}})
    for sid, tags, (x, z) in STOPS:
        g = _g(x, z)
        E.append({'type': 'node', 'id': sid, 'lat': g['lat'], 'lon': g['lon'], 'tags': tags})
    for rid, tags, mem in ROUTES:
        E.append({'type': 'relation', 'id': rid, 'members': [{'type': 'node', 'ref': m, 'role': 'platform'} for m in mem] +
                  [{'type': 'way', 'ref': 500001, 'role': ''}], 'tags': tags})
    out = {'version': 0.6, 'generator': 'Overpass API 0.7.62 (fixture)', 'osm3s': {'timestamp_osm_base': '2026-10-01T00:00:00Z',
           'copyright': 'The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.'}, 'elements': E}
    if remark:
        out['remark'] = remark
    return out


# ---------------- the census ----------------
TRACT = {'GEOID': '42101007600', 'STATE': '42', 'COUNTY': '101', 'TRACT': '007600', 'BASENAME': '76', 'NAME': 'Census Tract 76', 'AREALAND': '1207431', 'AREAWATER': '0'}
COUNTY = {'GEOID': '42101', 'STATE': '42', 'COUNTY': '101', 'BASENAME': 'Sample', 'NAME': 'Sample County', 'AREALAND': '347520037'}
STATE = {'GEOID': '42', 'STATE': '42', 'STUSAB': 'SS', 'BASENAME': 'Sample State', 'NAME': 'Sample State', 'AREALAND': '115881784866'}
VARS = {'pop': 'B01003_001', 'age': 'B01002_001', 'inc': 'B19013_001', 'hhs': 'B25010_001', 'hh': 'B11001_001',
        'ten': 'B25003_001', 'own': 'B25003_002', 'rent': 'B25003_003',
        'wrk': 'B08301_001', 'drv': 'B08301_003', 'cpl': 'B08301_004', 'trn': 'B08301_010', 'txi': 'B08301_016', 'mcy': 'B08301_017',
        'bik': 'B08301_018', 'wlk': 'B08301_019', 'oth': 'B08301_020', 'wfh': 'B08301_021',
        'vht': 'B08201_001', 'vh0': 'B08201_002', 'hu': 'B25001_001', 'vac': 'B25002_003'}
# estimate, margin of error; the ACS's special values as it sends them
FACTS = {
    'tract': {'pop': (4512, 380), 'age': (34.1, 2.3), 'inc': (72400, 8100), 'hhs': (2.1, 0.12), 'hh': (2105, 150), 'ten': (2105, 150), 'own': (800, 120),
              'rent': (1305, 160), 'wrk': (2300, 210), 'drv': (690, 110), 'cpl': (115, 50), 'trn': (1035, 160), 'txi': (23, 20), 'mcy': (0, 16),
              'bik': (92, 45), 'wlk': (230, 70), 'oth': (25, 18), 'wfh': (90, 40), 'vht': (2105, 150), 'vh0': (800, 130), 'hu': (2300, 140), 'vac': (195, 60)},
    'county': {'pop': (1584000, -555555555), 'age': (35.0, 0.2), 'inc': (57500, 900), 'hhs': (-666666666, -222222222), 'hh': (610000, 3000),
               'ten': (610000, 3000), 'own': (320000, 2500), 'rent': (290000, 2800), 'wrk': (720000, 4000), 'drv': (360000, 3500), 'cpl': (58000, 1800),
               'trn': (180000, 2500), 'txi': (7000, 600), 'mcy': (1000, 300), 'bik': (14000, 900), 'wlk': (58000, 1700), 'oth': (7000, 700),
               'wfh': (35000, 1200), 'vht': (610000, 3000), 'vh0': (180000, 2200), 'hu': (690000, 900), 'vac': (80000, 1900)},
    'state': {'pop': (12990000, -555555555), 'age': (40.9, 0.1), 'inc': (73170, 300), 'hhs': (2.39, 0.01), 'hh': (5190000, 9000),
              'ten': (5190000, 9000), 'own': (3570000, 10000), 'rent': (1620000, 8000), 'wrk': (6350000, 10000), 'drv': (4700000, 9000),
              'cpl': (500000, 4000), 'trn': (310000, 3000), 'txi': (20000, 900), 'mcy': (10000, 500), 'bik': (30000, 1000), 'wlk': (220000, 2500),
              'oth': (60000, 1500), 'wfh': (500000, 4000), 'vht': (5190000, 9000), 'vh0': (560000, 4000), 'hu': (5750000, 2000), 'vac': (560000, 5000)},
}
NAMES = {'tract': 'Census Tract 76; Sample County; Sample State', 'county': 'Sample County, Sample State', 'state': 'Sample State'}


def pyramid_cells(geo):
    """B01001's 23 men's and 23 women's cells, deterministic: a young-adult tract, an older county"""
    widths = [5, 5, 5, 3, 2, 1, 1, 3, 5, 5, 5, 5, 5, 5, 5, 2, 3, 2, 3, 5, 5, 5, 6]   # the cells' age spans
    mids = [2.5, 7.5, 12.5, 16, 18.5, 20, 21, 23, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 61, 63.5, 65.5, 68, 72.5, 77.5, 82.5, 88]
    peak, base = (29, 30) if geo == 'tract' else (45, 18000)
    out = {}
    for sex, off, f in (('m', 3, 1.0), ('f', 27, 1.04)):
        for j in range(23):
            per_year = base * f * math.exp(-((mids[j] - peak) / (26 if geo == 'tract' else 34)) ** 2) * (0.55 if mids[j] > 80 else 1)
            out['B01001_%03dE' % (off + j)] = int(round(per_year * widths[j]))
    return out


def acs_answer(url):
    """the Census Data API's answer to the app's URL: [header, row], strings"""
    u = urlparse(url)
    q = parse_qs(u.query)
    get = q['get'][0].split(',')
    fr = q['for'][0]
    lev = fr.split(':')[0]
    geo = 'tract' if lev == 'tract' else ('county' if lev == 'county' else 'state')
    vals = {}
    for k, v in VARS.items():
        e, m = FACTS[geo][k]
        vals[v + 'E'] = e
        vals[v + 'M'] = m
    vals.update(pyramid_cells(geo))
    head = list(get) + (['state', 'county', 'tract'] if geo == 'tract' else (['state', 'county'] if geo == 'county' else ['state']))
    row = []
    for h in get:
        row.append(NAMES[geo] if h == 'NAME' else str(vals[h]))
    row += ['42', '101', '007600'][:len(head) - len(get)]
    return [head, row]


def identify(svc):
    if svc == 'tracts':
        # the blocks first: the tract must be picked by its layer's name, not its place in the list
        return {'results': [{'layerId': 1, 'layerName': 'Census Block Groups', 'value': '1', 'displayFieldName': 'BASENAME',
                             'attributes': {'GEOID': '421010076001', 'NAME': 'Block Group 1', 'AREALAND': '400000'}},
                            {'layerId': 2, 'layerName': 'Census Blocks', 'value': '1003', 'displayFieldName': 'BASENAME',
                             'attributes': {'GEOID': '421010076001003', 'NAME': 'Block 1003', 'AREALAND': '20000'}},
                            {'layerId': 0, 'layerName': 'Census Tracts', 'value': '76', 'displayFieldName': 'BASENAME', 'attributes': dict(TRACT)}]}
    return {'results': [{'layerId': 0, 'layerName': 'States', 'value': 'Sample State', 'displayFieldName': 'BASENAME', 'attributes': dict(STATE)},
                        {'layerId': 1, 'layerName': 'Counties', 'value': 'Sample', 'displayFieldName': 'BASENAME', 'attributes': dict(COUNTY)}]}


def route_handler(store):
    """a Playwright route handler for Overpass, TIGERweb and the Census Data API; store['hits'] the urls,
    store['mode'] what to break: osm abort|429|remark|empty, tracts abort|none, counties abort,
    acsnew 404 (this year's 5-year estimates not out), acs abort, pyr abort"""
    async def handle(route):
        u = route.request.url
        store.setdefault('hits', []).append(u)
        mode = store.get('mode', {})
        hdr = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
        if '/api/interpreter' in u:
            m = mode.get('osm')
            if m == 'abort':
                await route.abort('internetdisconnected'); return
            if m == '429':
                await route.fulfill(status=429, body='busy', headers=hdr); return
            body = overpass(drop_ways=(m == 'empty'), remark=('runtime error: Query timed out in "query" at line 1 after 121 seconds.' if m == 'remark' else None))
        elif 'tigerweb.geo.census.gov' in u:
            key = 'tracts' if 'Tracts_Blocks' in u else 'counties'
            m = mode.get(key)
            if m == 'abort':
                await route.abort('internetdisconnected'); return
            body = {'results': []} if m == 'none' else identify(key)
        elif 'api.census.gov' in u:
            y = int(re.search(r'/data/(\d{4})/', u).group(1))
            pyr = 'B01001_003E' in unquote(u)
            if mode.get('acs') == 'abort' or (pyr and mode.get('pyr') == 'abort'):
                await route.abort('internetdisconnected'); return
            if mode.get('acsnew') == '404' and y == store.get('year'):
                await route.fulfill(status=404, body='<html><body>error: unknown/unsupported geography hierarchy</body></html>', headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/html'}); return
            store.setdefault('years', []).append(y)
            body = acs_answer(u)
        else:
            await route.abort('addressunreachable'); return
        await route.fulfill(status=200, body=json.dumps(body), headers=hdr)
    return handle
