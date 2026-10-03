"""patch_phase133f.py -- V133f: the street map is Esri's World Street Map.

CARTO's basemaps now answer a page opened as a file with "API KEY REQUIRED" tiles, as OSM's answer it
with "Access blocked". Esri's tile server, whose imagery the owner's file-opened page already shows,
also serves a street map, keyless; OpenStreetMap is among its credited sources."""
NAME = 'patch_phase133f.py'
BASE = 'c4d52859062256d8157b22fd71433915e40ed5b4081382f5b7cf38dd208fc5ed'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""    street:{name:'Street (CARTO, OpenStreetMap data)',url:'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',maxz:19,
      credit:'\\u00a9 OpenStreetMap contributors \\u00a9 CARTO',link:'https://www.openstreetmap.org/copyright'},""",
    """    /* __acad3dV133f: Esri's World Street Map. OSM's own servers answer a page opened as a file with
       "Access blocked" tiles, and CARTO's with "API KEY REQUIRED"; Esri's serve it, keyless. */
    street:{name:'Street (Esri World Street Map)',url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',maxz:19,
      credit:'Map: Esri, HERE, Garmin, USGS, \\u00a9 OpenStreetMap contributors, and the GIS User Community',link:'https://www.arcgis.com/home/item.html?id=3b93337983e9436f8db950e38a8629af'},""")
rep("""  window.__acad3dV133e='""", """  window.__acad3dV133f='esristreet';
  window.__acad3dV133e='""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
