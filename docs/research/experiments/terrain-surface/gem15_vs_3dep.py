"""V239 research (2026-11-21): GEM-15 at 30th Street Station, Philadelphia, against USGS 3DEP 1 m.
Reads GEM-15's public COGs (wm76s39, EPSG:32618) by HTTP range requests and 3DEP's ImageServer
getSamples, both keyless. Prints the DTM offset (GEM-15 EGM96 minus 3DEP NAVD88) on a grid of points,
and GEM-15's surface statistics (p95 - dtm) at named buildings. Run: python3 -I gem15_vs_3dep.py"""
import json, statistics, urllib.parse, urllib.request
import rasterio
from pyproj import Transformer

G = 'https://storage.googleapis.com/climate-and-sustainability/gem-15/p30_m80/wm76s39/'
DEP = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples'
to_utm = Transformer.from_crs(4326, 32618, always_xy=True)

def dep3(pts):
    geom = json.dumps({'points': [[lon, lat] for lon, lat in pts], 'spatialReference': {'wkid': 4326}})
    q = urllib.parse.urlencode({'geometry': geom, 'geometryType': 'esriGeometryMultipoint', 'returnFirstValueOnly': 'true', 'f': 'json'})
    js = json.load(urllib.request.urlopen(DEP + '?' + q, timeout=60))
    out = {}
    for s in js.get('samples', []):
        out[s['locationId']] = float(s['value']) if s['value'] not in ('NoData', None) else None
    return [out.get(i) for i in range(len(pts))]

def gem(path, pts, bands):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with rasterio.open('/vsicurl/' + G + path) as r:
            xy = [to_utm.transform(lon, lat) for lon, lat in pts]
            return [list(v) for v in r.sample(xy, indexes=bands)], r.descriptions

# a 9 x 9 grid, 120 m apart, centred on the station (39.9557, -75.1822)
grid = [(-75.1822 + (i - 4) * 0.0014, 39.9557 + (j - 4) * 0.00108) for i in range(9) for j in range(9)]
d = dep3(grid)
t, _ = gem('dtm/zall/mosaic.tif', grid, [1])
diffs = [g[0] - e for g, e in zip(t, d) if e is not None and g[0] == g[0]]
print('DTM points compared:', len(diffs), 'of', len(grid))
if diffs:
    print('GEM-15 DTM minus 3DEP: median %.2f m, mean %.2f m, stdev %.2f m, min %.2f, max %.2f' % (
        statistics.median(diffs), statistics.mean(diffs), statistics.pstdev(diffs), min(diffs), max(diffs)))
named = {'30th Street Station': (-75.18205, 39.95570), 'Cira Centre (about 132 m)': (-75.18323, 39.95745),
         'FMC Tower (about 223 m)': (-75.18715, 39.95530), 'Schuylkill River Park, open grass': (-75.18120, 39.94930)}
pts = list(named.values())
s, desc = gem('dsm/zall/mosaic.tif', pts, [1, 2, 3, 4, 5])
t2, _ = gem('dtm/zall/mosaic.tif', pts, [1])
print('DSM bands:', desc)
for (k, _), b, tt in zip(named.items(), s, t2):
    print('%-36s dsm %.1f p5 %.1f p50 %.1f p95 %.1f std %.1f | dtm %.1f | p95-dtm %.1f m' % ((k,) + tuple(b) + (tt[0], b[3] - tt[0])))
