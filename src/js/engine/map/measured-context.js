import { bimStd, bimStdCopy } from '../standards/registry.js';

  /* ===== __acad3dV202: site context C3, measured (docs/work-orders/v202/SPEC.md) =====
     Measured public data in place of OpenStreetMap's guesses, where it exists: the USGS 3DEP 1 m
     ground, a city's LiDAR building heights (the registry's ctx.heights), and the National Bridge
     Inventory's decks. Each function below is pure; the fetches that use them follow in WO-07 to WO-09. */
  var BIM_3DEP_URL='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer';
  var BIM_NBI_URL='https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Bridge_Inventory/FeatureServer/0';

  /* WO-01: a single-band, uncompressed, float32 TIFF (strips or tiles, either byte order) as
     {w,h,data:Float32Array}, rows from the top; null for anything it cannot read exactly */
  function bimTiffF32(bytes){
    return null;
  }
  /* WO-02: the 3DEP exportImage address for an area {w,s,e,n} and a grid of cols x rows (2 to 2000),
     the bbox in Web Mercator (R 6378137, toFixed(2)); null for a missing area or a bad size */
  function bimDep3Url(a,cols,rows){
    return null;
  }
  /* WO-03: the ground in metres at lon, lat from a DEM grid {w,h,data,a}, bilinear between pixel
     centres in Web Mercator; NaN off the grid or on nodata (below -1000) */
  function bimDep3ElevAt(g,lon,lat){
    return NaN;
  }
  /* WO-04: the city's measured height for an OSM footprint: the smallest city ring holding the
     footprint's vertex mean, in metres through rec.unit, as {h,top,base,from:'city',id}; else null */
  function bimCityHeightPick(ring,feats,rec){
    return null;
  }
  /* WO-05: the nearest NBI structure within maxD (30 m by default) of a bridge's centreline, as
     {id,carried,year,width,length,spans,clear,clearRef,dist}; measured numbers only; else null */
  function bimNbiPick(pts,bridges,maxD){
    return null;
  }
  /* the city records whose bbox holds a longitude and latitude (D2: the registry's ctx.heights) */
  function bimCityRecs(lon,lat){
    var all=bimStd('ctx.heights','sources')||{},out=[],k,r,b;
    for(k in all)if(all.hasOwnProperty(k)){
      r=all[k];b=r&&r.bbox;
      if(b&&lon>=b[0]&&lon<=b[2]&&lat>=b[1]&&lat<=b[3]){r=bimStdCopy(r);r.id=k;out.push(r);}
    }
    return out;
  }
export {
  BIM_3DEP_URL, BIM_NBI_URL, bimCityHeightPick, bimCityRecs, bimDep3ElevAt, bimDep3Url, bimNbiPick, bimTiffF32
};
