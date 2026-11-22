#!/bin/sh
# V239 research (2026-11-21): can a browser read each surface source keyless? HEAD/range GET with an
# Origin header; prints the status, the CORS header and the content type. Run: sh probe_sources.sh
O='Origin: https://example.org'
probe(){ printf '%s\n  ' "$1"; curl -s -o /dev/null -r 0-1023 -H "$O" -D - --max-time 25 "$1" | tr -d '\r' | grep -iE '^HTTP/|^access-control-allow-origin|^content-type|^content-range' | tr '\n' ' '; echo; }
probe 'https://storage.googleapis.com/climate-and-sustainability/gem-15/stac/catalog.json'
probe 'https://storage.googleapis.com/storage/v1/b/climate-and-sustainability/o/gem-15%2Fstac%2Fcatalog.json?alt=media'
probe 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N39_00_W076_00_DEM/Copernicus_DSM_COG_10_N39_00_W076_00_DEM.tif'
probe 'https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/tiles.geojson'
probe 'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/PA_Philadelphia_2015/ept.json'
probe 'https://usgs-lidar-stac.s3-us-west-2.amazonaws.com/ept/catalog.json'
probe 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer?f=json'
probe 'https://geodesy.noaa.gov/GEOID/GEOID18/downloads.shtml'
probe 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/15/9532/12405.png'
# GEM-15's COGs for the cell holding Philadelphia (wm76s39, EPSG:32618), found through its STAC catalog
probe 'https://storage.googleapis.com/climate-and-sustainability/gem-15/p30_m80/wm76s39/dtm/zall/mosaic.tif'
probe 'https://storage.googleapis.com/climate-and-sustainability/gem-15/p30_m80/wm76s39/dsm/zall/mosaic.tif'
probe 'https://geodesy.noaa.gov/api/geoid/ght?lat=39.9557&lon=-75.1822'
