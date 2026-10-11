"""land_fixture.py -- the ground and the flood map the V165 suite analyses.

The ground, in metres above sea level, as a function of model x (east) and z (south), the site at 0,0:
  a fall to the north-east of 3 cm a metre each way, from 100 m at the site's origin;
  a hill 15 m high to the south-west, at (-90, 70), its flanks steeper than 25%;
  a valley 4 m deep along a line through (45, 0) running north-east, the site on its south-west flank;
  a hollow 1.6 m deep at (-60, -60), which ponds where the fall would carry its water away.
Served as AWS Terrain Tiles (Terrarium PNG, zoom 15), decoded by the app as the real ones are.

FEMA's flood zones (the NFHL layer 28 answer, GeoJSON in longitude and latitude): strips along the
valley's line -- the regulatory floodway within 6 m of it, zone AE (base flood elevation 315 ft,
NAVD88) out to 18 m, shaded zone X (0.2% annual chance) out to 34 m, unshaded zone X (minimal) beyond
to the south-west. The site's centre, 31.8 m from the line, is in shaded X."""
import math, pathlib, struct, sys, zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import m2g, radii, LAT0, LON0   # noqa: E402

TZ = 15
U = (math.sqrt(0.5), -math.sqrt(0.5))   # the valley's direction, north-east in the model's plan
N = (math.sqrt(0.5), math.sqrt(0.5))    # across it, to the south-east
P0 = (45.0, 0.0)


def land_height(x, z):
    h = 100.0 - 0.03 * x + 0.03 * z
    h += 15.0 * math.exp(-((x + 90.0) ** 2 + (z - 70.0) ** 2) / (2 * 30.0 ** 2))
    d = (x - P0[0]) * N[0] + (z - P0[1]) * N[1]
    h -= 4.0 * math.exp(-d * d / (2 * 15.0 ** 2))
    h -= 1.6 * math.exp(-((x + 60.0) ** 2 + (z + 60.0) ** 2) / (2 * 10.0 ** 2))
    return h


def g2m(lon, lat):
    """longitude and latitude to model x, z, true north up (the app's bimGeoToModel at true north 0)"""
    M, Nr = radii(LAT0)
    E = math.radians(lon - LON0) * Nr * math.cos(math.radians(LAT0))
    Nn = math.radians(lat - LAT0) * M
    return E, -Nn


def land_px(gx, gy):
    n = 256 * 2 ** TZ
    lon = gx / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / n))))
    x, z = g2m(lon, lat)
    return land_height(x, z)


_PNG = {}


def land_png(z, x, y):
    key = (z, x, y)
    if key in _PNG:
        return _PNG[key]
    s = 2 ** (TZ - z) if z <= TZ else 1
    rows = []
    for j in range(256):
        row = bytearray(b'\x00')
        for i in range(256):
            v = land_px((x * 256 + i + 0.5) * s, (y * 256 + j + 0.5) * s) + 32768
            fl = math.floor(v)
            b = min(255, int(round((v - fl) * 256)))
            row += bytes((int(fl) // 256, int(fl) % 256, b))
        rows.append(bytes(row))

    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    _PNG[key] = b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', 256, 256, 8, 2, 0, 0, 0)) + \
        ch(b'IDAT', zlib.compress(b''.join(rows))) + ch(b'IEND', b'')
    return _PNG[key]


def strip(d0, d1, s0=-260.0, s1=260.0):
    """the strip d0..d1 from the valley's line, s0..s1 along it, as a closed ring of [lon, lat]"""
    pts = []
    for s, d in ((s0, d0), (s1, d0), (s1, d1), (s0, d1), (s0, d0)):
        x = P0[0] + s * U[0] + d * N[0]
        zz = P0[1] + s * U[1] + d * N[1]
        lon, lat = m2g(x, zz)
        pts.append([lon, lat])
    return pts


def feature(fid, zone, sub, sfha, rings, bfe=-9999.0):
    return {'type': 'Feature', 'id': fid, 'geometry': {'type': 'Polygon' if len(rings) == 1 else 'MultiPolygon',
            'coordinates': rings[0:1] if len(rings) == 1 else [[r] for r in rings]},
            'properties': {'FLD_AR_ID': 'FIX_%d' % fid, 'FLD_ZONE': zone, 'ZONE_SUBTY': sub, 'SFHA_TF': sfha,
                           'STATIC_BFE': bfe, 'LEN_UNIT': 'Feet', 'V_DATUM': 'NAVD88'}}


ZONES = [
    feature(1, 'AE', 'FLOODWAY', 'T', [strip(-6, 6)], 315.0),
    feature(2, 'AE', ' ', 'T', [strip(-18, -6), strip(6, 18)], 315.0),
    feature(3, 'X', '0.2 PCT ANNUAL CHANCE FLOOD HAZARD', 'F', [strip(-34, -18), strip(18, 34)]),
    feature(4, 'X', 'AREA OF MINIMAL FLOOD HAZARD', 'F', [strip(-200, -34)]),
]


def fema_body(kind='zones'):
    return {'type': 'FeatureCollection', 'features': ZONES if kind == 'zones' else []}
