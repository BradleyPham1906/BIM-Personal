
  /* ===== __acad3dV202c: heights on one datum (docs/work-orders/v202/SPEC.md, part C) =====
     Cloud-optimised GeoTIFFs (GEM-15, PROJ's geoid grids) are read by geotiff.js 3.0.5 (MIT, runtime/geotiff,
     loaded only when a fetch needs it; the owner, 2026-11-21) through bimCogRead (WO-28). The geoids put every
     source's heights on the project's datum: NAVD88 in CONUS, EGM96 elsewhere, by the project's location. */
  /* WO-22: a geoid grid {w,h,x0,y0,dx,dy,data} bilinear at lon, lat (x0, y0 the first node; longitudes taken round
     by 360 to the grid); NaN off the grid, at a NaN node, or for bad input */
  function bimGeoidAt(g,lon,lat){
  if(!g||!isFinite(lon)||!isFinite(lat))return NaN;
  while(lon<g.x0)lon+=360;while(lon>=g.x0+360)lon-=360;
  var fx=(lon-g.x0)/g.dx,fy=(lat-g.y0)/g.dy,i=Math.floor(fx),j=Math.floor(fy);
  if(i<0||i>=g.w||j<0||j>=g.h)return NaN;
  var tx=fx-i,ty=fy-j;
  var i2=i+1>=g.w&&tx===0?i:i+1;if(i+1>=g.w&&tx!==0)return NaN;
  var j2=j+1>=g.h&&ty===0?j:j+1;if(j+1>=g.h&&ty!==0)return NaN;
  var v00=g.data[j*g.w+i],v10=g.data[j*g.w+i2],v01=g.data[j2*g.w+i],v11=g.data[j2*g.w+i2];
  if(!isFinite(v00)||!isFinite(v10)||!isFinite(v01)||!isFinite(v11))return NaN;
  return (1-tx)*(1-ty)*v00+tx*(1-ty)*v10+(1-tx)*ty*v01+tx*ty*v11;
  }
  /* WO-23: a height moved from one datum to another, h + N[from] - N[to], N the geoid heights at the point
     ('ellipsoid' is 0); NaN for an unknown datum or a bad height */
  function bimDatumShift(h,from,to,N){
  if(!isFinite(h)||!N)return NaN;
  var nf=from==='ellipsoid'?0:N[from],nt=to==='ellipsoid'?0:N[to];
  if(!isFinite(nf)||!isFinite(nt))return NaN;
  return h+nf-nt;
  }
export { bimDatumShift, bimGeoidAt };
