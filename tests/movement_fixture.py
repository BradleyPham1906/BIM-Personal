"""movement_fixture.py -- the V166 suite's neighbourhood: V161's street grid (tests/access_fixture.py) with
what movement reads added, each piece there to test one rule.

Shaped as Overpass answers the app's one access request: the ways with their tags and geometry, the
places, the stops and the routes, then the crossings' nodes, the doors and garage entrances, and the car
parks with their outlines. Model metres (x east, z south, the site at 0,0); deterministic.

What is added to V161's grid:
- tags on its streets, by name: S1 Street a bike lane beside parking at 30 mph (LTS 2); N1 Street 35 mph
  (LTS 4); Avenue 18 a cycle track (LTS 1); Avenue 14 six lanes at 25 mph (LTS 4); North Boulevard 40 mph
  and 4 lanes (LTS 4, and its crossings LTS 4 where nothing controls them), and its surface, a tag
  movement leaves out; 5th Street parking on its left only;
- a signal at North Boulevard and Avenue 15, an all-way stop at North Boulevard and Avenue 17, a stop on
  the approach only at North Boulevard and Avenue 19 (not a control), a marked crossing with an island at
  Market Street and Avenue 18;
- a path joining two avenues; a driveway from Market Street into the lot (left out with 'nodrive');
- 5th Street mapped as two ways, split where N3 Street crosses it, as OpenStreetMap often splits a
  street: a street's own pieces do not cross each other;
- doors: one on the lot line, one inside it, one 20 m off it (not the lot's);
- a garage entrance, a surface car park with 40 spaces, a multi-storey with none mapped, a car park
  beyond 400 m;
- the routes' intervals (bus 12 every 10 and 12 minutes by direction, 42 every 15, line A every 5, bus 7
  every 20; tram T1 none; 'noiv' takes them all off, 'alliv' gives T1 8) and their ways (12 along Market
  Street, 42 along 5th Street);
- 'dense': a footway of 7,000 points zig-zagging 700 m away, past the 6,000-node budget."""
import copy, json, pathlib, sys
from urllib.parse import unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import access_fixture as AFX          # noqa: E402
import site_analysis_fixture as SFX   # noqa: E402
from access_fixture import NET, _g, _bounds   # noqa: E402

LOT = AFX.LOT
TAGS = {
    'S1 Street': {'cycleway:both': 'lane', 'parking:both': 'lane', 'maxspeed': '30 mph', 'lanes': '2'},
    'N1 Street': {'maxspeed': '35 mph'},
    'Avenue 18': {'cycleway': 'track'},
    'Avenue 14': {'lanes': '6', 'maxspeed': '25 mph'},
    'North Boulevard': {'maxspeed': '40 mph', 'lanes': '4', 'surface': 'asphalt'},   # surface: a tag movement does not keep
    '5th Street': {'parking:left': 'lane', 'parking:right': 'no'},
}
NODES = [   # (x, z, tags): on the grid's junctions, so the same nodes as the streets'
    (-60, -400, {'highway': 'traffic_signals'}),
    (180, -400, {'highway': 'stop', 'stop': 'all'}),
    (420, -400, {'highway': 'stop'}),
    (300, 0, {'highway': 'crossing', 'crossing': 'marked', 'crossing:island': 'yes'}),
]
DOORS = [(30, -10, {'entrance': 'main', 'name': 'Main door'}), (12, -38, {'entrance': 'service'}), (30, 10, {'entrance': 'yes'})]   # the last 20 m off the lot
GARAGE = (100, -60, {'amenity': 'parking_entrance', 'name': 'Garage A', 'access': 'customers'})
CARPARKS = [
    ([(100, -70), (160, -70), (160, -90), (100, -90)], {'amenity': 'parking', 'parking': 'surface', 'capacity': '40', 'access': 'yes', 'fee': 'yes', 'name': 'Lot P1'}),
    ([(-240, -130), (-200, -130), (-200, -170), (-240, -170)], {'amenity': 'parking', 'parking': 'multi-storey', 'access': 'customers', 'name': 'Deck P2'}),
    ([(900, -900), (960, -900), (960, -960), (900, -960)], {'amenity': 'parking', 'parking': 'surface', 'name': 'Far Lot'}),
]
PATH = [(540, -200), (600, -150), (660, -100)]   # joins Avenue 22 (x 540) and Avenue 23 (x 660) at grid junctions
DRIVE = [(40, 0), (40, -12)]
INTERVALS = {800001: '10', 800002: '00:12', 800003: '15', 800004: '5', 800006: '20'}
ROUTE_WAYS = {800001: 'Market Street', 800002: 'Market Street', 800003: '5th Street'}
_nid = [9100000]


def _node(x, z):
    k = (round(x, 4), round(z, 4))
    if k in NET.ids:
        return NET.ids[k]
    _nid[0] += 1
    return _nid[0]


def _way(wid, pts, tags):
    return {'type': 'way', 'id': wid, 'bounds': _bounds(pts), 'nodes': [_node(x, z) for x, z in pts], 'geometry': [_g(x, z) for x, z in pts], 'tags': dict(tags)}


def overpass_mv(modes=()):
    """V161's answer with movement's parts; modes: nodrive, noiv, alliv, dense"""
    body = copy.deepcopy(AFX.overpass())   # V161's answer shares its tags with its grid: a copy to change
    E = body['elements']
    by_name = {}
    for e in E:
        if e['type'] == 'way' and 'highway' in e.get('tags', {}):
            n = e['tags'].get('name')
            if n in TAGS:
                e['tags'].update(TAGS[n])
            by_name.setdefault(n, []).append(e)
    # a node on Market Street where the driveway meets it: on its line, so its geometry stays the same
    if 'nodrive' not in modes:
        ms = by_name['Market Street'][0]
        xs = [AFX.NET.xy[i][0] for i in ms['nodes']]
        k = next(j for j in range(1, len(xs)) if xs[j - 1] < 40 < xs[j])
        nid = 9000001
        NET.ids[(40.0, 0.0)] = nid
        ms['nodes'].insert(k, nid)
        ms['geometry'].insert(k, _g(40, 0))
        E.append(_way(9500001, DRIVE, {'highway': 'service', 'service': 'driveway'}))
    E.append(_way(9500002, PATH, {'highway': 'path', 'name': 'Park Path'}))
    st = by_name['5th Street'][0]   # two ways, split at N3 Street: its own pieces meet there
    k = st['nodes'].index(NET.ids[(60, -300)])
    st2 = dict(st, id=9500004, nodes=st['nodes'][k:], geometry=st['geometry'][k:], tags=dict(st['tags']))
    st['nodes'], st['geometry'] = st['nodes'][:k + 1], st['geometry'][:k + 1]
    for w in (st, st2):
        la, lo = [g['lat'] for g in w['geometry']], [g['lon'] for g in w['geometry']]
        w['bounds'] = {'minlat': min(la), 'minlon': min(lo), 'maxlat': max(la), 'maxlon': max(lo)}
    E.append(st2)
    by_name['5th Street'].append(st2)
    if 'dense' in modes:
        pts = [(600 + (i % 40), -480 + (i // 40) * 0.25 + (2 if i % 2 else 0)) for i in range(7000)]
        w = _way(9500003, pts, {'highway': 'footway', 'name': 'Maze Walk'})
        w['nodes'] = [9600000 + i for i in range(len(pts))]
        E.append(w)
    for e in E:
        if e['type'] == 'relation' and e['tags'].get('type') == 'route':
            rid = e['id']
            if 'noiv' not in modes and rid in INTERVALS:
                e['tags']['interval'] = INTERVALS[rid]
            if 'alliv' in modes and rid == 800005:
                e['tags']['interval'] = '8'
            if rid in ROUTE_WAYS:
                e['members'] = [m for m in e['members'] if m['type'] != 'way'] + \
                    [{'type': 'way', 'ref': w['id'], 'role': ''} for w in by_name[ROUTE_WAYS[rid]]]
    for x, z, tags in NODES:
        g = _g(x, z)
        E.append({'type': 'node', 'id': _node(x, z), 'lat': g['lat'], 'lon': g['lon'], 'tags': dict(tags)})
    for i, (x, z, tags) in enumerate(DOORS + [GARAGE]):
        g = _g(x, z)
        E.append({'type': 'node', 'id': 9700001 + i, 'lat': g['lat'], 'lon': g['lon'], 'tags': dict(tags)})
    for i, (ring, tags) in enumerate(CARPARKS):
        pts = ring + ring[:1]
        E.append({'type': 'way', 'id': 9800001 + i, 'bounds': _bounds(pts), 'nodes': [9810000 + 10 * i + j for j in range(len(ring))] + [9810000 + 10 * i],
                  'geometry': [_g(x, z) for x, z in pts], 'tags': dict(tags)})
    return body


def route_handler(store):
    """V164's handler for every host, the access request answered with movement's neighbourhood;
    store['mv'] the modes, store['mode']['acc'] 'abort' to take Overpass's access answer away"""
    base = SFX.route_handler(store)

    async def handle(route):
        u = route.request.url
        if '/api/interpreter' in u and '["building"]' not in unquote(u):
            store.setdefault('hits', []).append(('acc', u))
            if store.get('mode', {}).get('acc') == 'abort':
                await route.abort('internetdisconnected')
                return
            await route.fulfill(status=200, body=json.dumps(overpass_mv(store.get('mv', ()))), headers=SFX.HDR)
            return
        await base(route)
    return handle


HOSTS = SFX.HOSTS
