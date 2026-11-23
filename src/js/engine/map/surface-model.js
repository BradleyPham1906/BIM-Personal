
  /* ===== __acad3dV202c: the surface model (docs/work-orders/v202/SPEC.md, part C) =====
     GEM-15's 15 m DSM (with its 5th, 50th, 95th percentiles and spread) and DTM, levelled to the local ground,
     and the heights of buildings and trees from them where nothing better gives one. */
  /* WO-24: the GEM-15 cell holding lon, lat: {group, cell, dsm, dtm}, the two COGs' addresses; null outside
     61 S to 84 N or off the globe */
  function bimGemCell(lon,lat){
  if(!isFinite(lon)||!isFinite(lat)||lat<-61||lat>=84||lon<-180||lon>=180)return null;
  var x=Math.floor(lon),y=Math.floor(lat),gx=Math.floor(lon/10)*10,gy=Math.floor(lat/10)*10;
  var s=function(v){return v<0?'m'+(-v):'p'+v;};
  var c=function(v){return v<0?'m'+(-v):''+v;};
  var group=s(gy)+'_'+s(gx),cell='w'+c(x)+'s'+c(y);
  return{group:group,cell:cell,dsm:'https://storage.googleapis.com/climate-and-sustainability/gem-15/'+group+'/'+cell+'/dsm/zall/mosaic.tif',dtm:'https://storage.googleapis.com/climate-and-sustainability/gem-15/'+group+'/'+cell+'/dtm/zall/mosaic.tif'};
  }
  /* WO-25: GEM-15's DTM levelled to a local ground: the median of ref - dtm over open cells (|dsm - dtm| <= 1 m
     and std <= 1 m), as {offset, n, mad}; null under five open cells */
  function bimSurfaceOffset(pairs){
  if(!pairs)return null;
  var ok=function(v){return v!=null&&isFinite(v);},kept=[],i,p;for(i=0;i<pairs.length;i++){p=pairs[i];if(!p)continue;
    if(!ok(p.ref)||!ok(p.dtm)||!ok(p.dsm)||!ok(p.std))continue;
    if(Math.abs(p.dsm-p.dtm)>1||p.std>1)continue;
    kept.push(p.ref-p.dtm);
  }
  if(kept.length<5)return null;
  kept.sort(function(a,b){return a-b;});
  var n=kept.length,m=Math.floor(n/2);
  var offset=n%2?kept[m]:(kept[m-1]+kept[m])/2;
  var devs=[];for(i=0;i<n;i++)devs.push(Math.abs(kept[i]-offset));
  devs.sort(function(a,b){return a-b;});
  var mad=n%2?devs[m]:(devs[m-1]+devs[m])/2;
  return{offset:Math.round(offset*100)/100,n:n,mad:Math.round(mad*100)/100};
  }
  /* WO-26: a footprint's height from GEM-15: the median of its cells' p95 less the ground, as {h, n, spread,
     from:'gem15'}; null under three cells, under 2 m, or without ground */
  function bimFootprintHeight(cells,ground){
  if(!cells||!isFinite(ground))return null;
  var vals=[],i;for(i=0;i<cells.length;i++){if(cells[i]&&isFinite(cells[i].p95))vals.push(cells[i].p95);}
  if(vals.length<3)return null;
  vals.sort(function(a,b){return a-b;});
  var n=vals.length,m=Math.floor(n/2);
  var med=n%2?vals[m]:(vals[m-1]+vals[m])/2;
  var h=Math.round((med-ground)*10)/10;
  if(h<2)return null;
  var devs=[];for(i=0;i<n;i++)devs.push(Math.abs(vals[i]-med));
  devs.sort(function(a,b){return a-b;});
  var spread=n%2?devs[m]:(devs[m-1]+devs[m])/2;
  return{h:h,n:n,spread:Math.round(spread*10)/10,from:'gem15'};
  }
export { bimFootprintHeight, bimGemCell, bimSurfaceOffset };
