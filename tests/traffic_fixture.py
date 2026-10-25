"""traffic_fixture.py -- the V171 suite's neighbourhood: V166's (tests/movement_fixture.py) with what the
traffic simulation reads near the lot, each piece there to test one rule.

V166's grid maps its only signal 400 m north of the lot, beyond the simulation's 300 m reach. Added here, all
within the reach (model metres, x east, z south, the lot at x 10..50, z -40..-10):
- signals at Market Street and 5th Street (60, 0), beside the lot, and at Market Street and Avenue 14
  (-180, 0), where Avenue 14's six lanes are capped by a mapped width;
- an all-way stop at Avenue 17 and N1 Street (180, -100);
- a stop on one approach: Avenue 15's from Market Street, 8 m short of N1 Street (-60, -92);
- a mapped width of 10 m on Avenue 14 (its six lanes are three at the app's lane width: 2 one way, 1 the other).

Modes, besides V166's (nodrive, noiv, alliv, dense): 'nosig' leaves the signals out, 'nostop' the stops."""
import json, pathlib, sys
from urllib.parse import unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import movement_fixture as MFX       # noqa: E402
import site_analysis_fixture as SFX  # noqa: E402
from access_fixture import _g        # noqa: E402

LOT = MFX.LOT
SIGNALS = [(60, 0), (-180, 0)]
ALLSTOP = (180, -100)
STOP = (-60, -92)
WIDTH = {'Avenue 14': '10'}
_nid = [9900000]


def _node(x, z, tags):
    _nid[0] += 1
    g = _g(x, z)
    return {'type': 'node', 'id': _nid[0], 'lat': g['lat'], 'lon': g['lon'], 'tags': dict(tags)}


def overpass_tr(modes=()):
    """V166's answer with the traffic simulation's parts"""
    body = MFX.overpass_mv(tuple(m for m in modes if m in ('nodrive', 'noiv', 'alliv', 'dense')))
    E = body['elements']
    for e in E:
        if e['type'] == 'way' and e.get('tags', {}).get('name') in WIDTH:
            e['tags']['width'] = WIDTH[e['tags']['name']]
    if 'nosig' not in modes:
        for x, z in SIGNALS:
            E.append(_node(x, z, {'highway': 'traffic_signals'}))
    if 'nostop' not in modes:
        E.append(_node(ALLSTOP[0], ALLSTOP[1], {'highway': 'stop', 'stop': 'all'}))
        E.append(_node(STOP[0], STOP[1], {'highway': 'stop'}))
    return body


def route_handler(store):
    """V164's handler for every host, the access request answered with the traffic neighbourhood; store['tr'] the
    modes, store['mode']['acc'] 'abort' to take Overpass's access answer away"""
    base = SFX.route_handler(store)

    async def handle(route):
        u = route.request.url
        if '/api/interpreter' in u and '["building"]' not in unquote(u):
            store.setdefault('hits', []).append(('acc', u))
            if store.get('mode', {}).get('acc') == 'abort':
                await route.abort('internetdisconnected')
                return
            await route.fulfill(status=200, body=json.dumps(overpass_tr(store.get('tr', ()))), headers=SFX.HDR)
            return
        await base(route)
    return handle


HOSTS = SFX.HOSTS
