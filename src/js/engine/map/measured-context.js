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
    if(!(bytes instanceof Uint8Array)||bytes.length<8)return null;
    var le=bytes[0]===0x49&&bytes[1]===0x49,dv,n=bytes.length,ifd,cnt,p,tags={},i,id,ty,c,sz,at,j,a,w,h,data,offs,rps,tw,th,nx,ny,tx,tyi,rows,cols,off,x,y;
    if(!le&&!(bytes[0]===0x4D&&bytes[1]===0x4D))return null;
    dv=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
    if(dv.getUint16(2,le)!==42)return null;
    ifd=dv.getUint32(4,le);
    if(ifd<8||ifd>n-2)return null;
    cnt=dv.getUint16(ifd,le);
    if(ifd+2+cnt*12>n)return null;
    for(i=0;i<cnt;i++){
      p=ifd+2+i*12;id=dv.getUint16(p,le);ty=dv.getUint16(p+2,le);c=dv.getUint32(p+4,le);
      if((ty!==3&&ty!==4)||!c)continue;
      sz=ty===3?2:4;at=c*sz>4?dv.getUint32(p+8,le):p+8;
      if(c*sz>n||at>n-c*sz)return null;
      a=[];for(j=0;j<c;j++)a.push(ty===3?dv.getUint16(at+j*sz,le):dv.getUint32(at+j*sz,le));
      tags[id]=a;
    }
    function v(id,def){return tags[id]?tags[id][0]:def}
    w=v(256,0);h=v(257,0);
    if(!w||!h||w*h>16777216||v(258,0)!==32||v(259,1)!==1||v(277,1)!==1||v(339,0)!==3)return null;
    data=new Float32Array(w*h);
    tw=v(322,0);th=v(323,0);offs=tags[324]||[];
    if(tw||th||offs.length){
      if(!tw||!th)return null;
      nx=Math.ceil(w/tw);ny=Math.ceil(h/th);
      if(offs.length!==nx*ny)return null;
      for(i=0;i<offs.length;i++){
        tx=i%nx;tyi=Math.floor(i/nx);rows=Math.min(th,h-tyi*th);cols=Math.min(tw,w-tx*tw);off=offs[i];
        if(off+((rows-1)*tw+cols)*4>n)return null;
        for(y=0;y<rows;y++)for(x=0;x<cols;x++)data[(tyi*th+y)*w+tx*tw+x]=dv.getFloat32(off+(y*tw+x)*4,le);
      }
    }else{
      offs=tags[273]||[];rps=v(278,h);
      if(!rps||offs.length!==Math.ceil(h/rps))return null;
      for(i=0;i<offs.length;i++){
        rows=Math.min(rps,h-i*rps);off=offs[i];
        if(off+w*rows*4>n)return null;
        for(j=0;j<w*rows;j++)data[i*rps*w+j]=dv.getFloat32(off+j*4,le);
      }
    }
    return{w:w,h:h,data:data}
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
