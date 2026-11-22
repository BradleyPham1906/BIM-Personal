"""V239 research (2026-11-21): how far apart the vertical datums are at 30th Street Station.
EGM96 and EGM2008 geoid heights from PROJ's grids (cdn.proj.org, read by rasterio); GEOID18 from NGS's
geoid API (no CORS, so not usable from the browser; read here once). H(EGM96) - H(NAVD88) = N(GEOID18) - N(EGM96).
Run: python3 -I geoid_offsets.py"""
import json, urllib.request
import rasterio
lat, lon = 39.9557, -75.1822
def n(grid):   # PROJ's geoid grids, read in place by range requests
    with rasterio.open('/vsicurl/https://cdn.proj.org/' + grid) as r:
        return float(next(r.sample([(lon, lat)]))[0])
n96, n08 = n('us_nga_egm96_15.tif'), n('us_nga_egm08_25.tif')
g18 = json.load(urllib.request.urlopen('https://geodesy.noaa.gov/api/geoid/ght?lat=%s&lon=%s' % (lat, lon), timeout=30))['geoidHeight']
print('N EGM96 %.3f m, N EGM2008 %.3f m, N GEOID18 %.3f m' % (n96, n08, g18))
print('H(EGM96) - H(NAVD88) = %.3f m; H(EGM2008) - H(NAVD88) = %.3f m' % (g18 - n96, g18 - n08))
