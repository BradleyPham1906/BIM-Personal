
  /* ===== __acad3dV202c: the surface model (docs/work-orders/v202/SPEC.md, part C) =====
     GEM-15's 15 m DSM (with its 5th, 50th, 95th percentiles and spread) and DTM, levelled to the local ground,
     and the heights of buildings and trees from them where nothing better gives one. */
  /* WO-24: the GEM-15 cell holding lon, lat: {group, cell, dsm, dtm}, the two COGs' addresses; null outside
     61 S to 84 N or off the globe */
  function bimGemCell(lon,lat){
    return null;
  }
  /* WO-25: GEM-15's DTM levelled to a local ground: the median of ref - dtm over open cells (|dsm - dtm| <= 1 m
     and std <= 1 m), as {offset, n, mad}; null under five open cells */
  function bimSurfaceOffset(pairs){
    return null;
  }
  /* WO-26: a footprint's height from GEM-15: the median of its cells' p95 less the ground, as {h, n, spread,
     from:'gem15'}; null under three cells, under 2 m, or without ground */
  function bimFootprintHeight(cells,ground){
    return null;
  }
export { bimFootprintHeight, bimGemCell, bimSurfaceOffset };
