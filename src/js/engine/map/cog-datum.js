
  /* ===== __acad3dV202c: heights on one datum (docs/work-orders/v202/SPEC.md, part C) =====
     Cloud-optimised GeoTIFFs (GEM-15, PROJ's geoid grids) are read by geotiff.js 3.0.5 (MIT, runtime/geotiff,
     loaded only when a fetch needs it; the owner, 2026-11-21) through bimCogRead (WO-28). The geoids put every
     source's heights on the project's datum: NAVD88 in CONUS, EGM96 elsewhere, by the project's location. */
  /* WO-22: a geoid grid {w,h,x0,y0,dx,dy,data} bilinear at lon, lat (x0, y0 the first node; longitudes taken round
     by 360 to the grid); NaN off the grid, at a NaN node, or for bad input */
  function bimGeoidAt(g,lon,lat){
    return NaN;
  }
  /* WO-23: a height moved from one datum to another, h + N[from] - N[to], N the geoid heights at the point
     ('ellipsoid' is 0); NaN for an unknown datum or a bad height */
  function bimDatumShift(h,from,to,N){
    return NaN;
  }
export { bimDatumShift, bimGeoidAt };
