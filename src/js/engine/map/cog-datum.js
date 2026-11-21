
  /* ===== __acad3dV239: heights on one datum (docs/work-orders/v239/SPEC.md) =====
     A cloud-optimised GeoTIFF read by HTTP ranges (tiled, DEFLATE through the browser's DecompressionStream,
     TIFF's floating-point predictor), and the geoid grids that put every source's heights on one datum. */
  /* WO-01: the first IFD of a tiled TIFF, classic or BigTIFF, either byte order, as {big, le, w, h, tw, th, spp, bps,
     fmt, comp, pred, planar, offsets, counts, nodata, scale, tie, epsg}; null for anything else or an array past the bytes */
  function bimTiffIfd(bytes){
    return null;
  }
  /* WO-02: the tiles a pixel window [x0,x1) x [y0,y1) touches, clipped to the image, row by row, as
     {t, col, row, off, len}; [] for an empty window */
  function bimCogTiles(ifd,x0,y0,x1,y1){
    return [];
  }
  /* WO-03: a decompressed tile's bytes as a Float32Array of tw x th x spp samples: predictor 1 as little-endian
     float32, predictor 3 (floating point) undone row by row; null for a short buffer or another predictor */
  function bimTiffUnpredict(u8,tw,th,spp,pred){
    return null;
  }
  /* WO-04: a geoid grid {w,h,x0,y0,dx,dy,data} bilinear at lon, lat (x0, y0 the first node; longitudes taken round
     by 360 to the grid); NaN off the grid, at a NaN node, or for bad input */
  function bimGeoidAt(g,lon,lat){
    return NaN;
  }
  /* WO-05: a height moved from one datum to another, h + N[from] - N[to], N the geoid heights at the point
     ('ellipsoid' is 0); NaN for an unknown datum or a bad height */
  function bimDatumShift(h,from,to,N){
    return NaN;
  }
export { bimCogTiles, bimDatumShift, bimGeoidAt, bimTiffIfd, bimTiffUnpredict };
