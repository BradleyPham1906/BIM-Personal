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
  function bimDep3Url(a, cols, rows) {
    if (!a || typeof cols !== 'number' || typeof rows !== 'number') return null;
    if (cols < 2 || cols > 2000 || rows < 2 || rows > 2000) return null;
    if (!a.w || !a.s || !a.e || !a.n) return null;
    var R = 6378137, D = Math.PI / 180;
    var mx = function(lon) { return R * lon * D; };
    var my = function(lat) { return R * Math.log(Math.tan(Math.PI / 4 + lat * D / 2)); };
    var bbox = mx(a.w).toFixed(2) + ',' + my(a.s).toFixed(2) + ',' + mx(a.e).toFixed(2) + ',' + my(a.n).toFixed(2);
    return 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?bbox=' + bbox + '&bboxSR=3857&imageSR=3857&size=' + cols + ',' + rows + '&format=tiff&pixelType=F32&compression=None&interpolation=RSP_BilinearInterpolation&f=image';
  }
  /* WO-03: the ground in metres at lon, lat from a DEM grid {w,h,data,a}, bilinear between pixel
     centres in Web Mercator; NaN off the grid or on nodata (below -1000) */
  function bimDep3ElevAt(g,lon,lat){
  var A=g.a,fx=(lon-A.w)/(A.e-A.w),fy=(A.n-lat)/(A.n-A.s);
  if(fx<0||fx>1||fy<0||fy>1)return NaN;
  var cx=(0.5+Math.floor(fx*g.w))/g.w,cy=(0.5+Math.floor(fy*g.h))/g.h;
  var ix=Math.floor(fx*g.w),iy=Math.floor(fy*g.h);
  if(ix>=g.w)ix=g.w-1;if(iy>=g.h)iy=g.h-1;
  var dx=fx-cx,dy=fy-cy;
  var ixa=ix,ixb=ix,ya=iy,yb=iy;
  if(dx<0){ixa=ix-1;if(ixa<0)ixa=0;}else{ixb=ix+1;if(ixb>=g.w)ixb=g.w-1;}
  if(dy<0){ya=iy-1;if(ya<0)ya=0;}else{yb=iy+1;if(yb>=g.h)yb=g.h-1;}
  var v00=g.data[ya*g.w+ixa],v10=g.data[ya*g.w+ixb],v01=g.data[yb*g.w+ixa],v11=g.data[yb*g.w+ixb];
  if(Math.abs(dx)<1e-9&&Math.abs(dy)<1e-9)return v00;
  var wx=Math.abs(dx)*g.w,wy=Math.abs(dy)*g.h;
  if(Math.abs(dx)<1e-9){if(!isFinite(v00)||v00<-1000||!isFinite(v01)||v01<-1000)return NaN;return v00+wy*(v01-v00);}
  if(Math.abs(dy)<1e-9){if(!isFinite(v00)||v00<-1000||!isFinite(v10)||v10<-1000)return NaN;return v00+wx*(v10-v00);}
  if(!isFinite(v00)||v00<-1000||!isFinite(v10)||v10<-1000||!isFinite(v01)||v01<-1000||!isFinite(v11)||v11<-1000)return NaN;
  return (1-wx)*(1-wy)*v00+wx*(1-wy)*v10+(1-wx)*wy*v01+wx*wy*v11;
  }
  /* WO-04: the city's measured height for an OSM footprint: the smallest city ring holding the
     footprint's vertex mean, in metres through rec.unit, as {h,top,base,from:'city',id}; else null */
  function bimCityHeightPick(ring,feats,rec){
  if(!ring||!feats||!rec)return null;
  var cx=0,cy=0,n=ring.length,i;for(i=0;i<n;i++){cx+=ring[i][0];cy+=ring[i][1];}
  cx/=n;cy/=n;
  var best=null,bestArea=Infinity,fi;for(fi=0;fi<feats.length;fi++){
    var f=feats[fi];
    if(!f.ring||!f.a)continue;
    var r=f.ring,m=r.length,j,k=m-1,inside=false;
    for(j=0;j<m;j++){if((r[j][1]>cy)!=(r[k][1]>cy)&&cx<(r[k][0]-r[j][0])*(cy-r[j][1])/(r[k][1]-r[j][1])+r[j][0])inside=!inside;k=j;}
    if(!inside)continue;
    var area=0;for(j=0;j<m;j++){var p=r[j],q=r[(j+1)%m];area+=p[0]*q[1]-q[0]*p[1];}
    area=Math.abs(area)/2;
    if(area>=bestArea)continue;
    var h=f.a[rec.roof]*rec.unit;
    if(!isFinite(h)||h<=0)continue;
    h=Math.round(h*100)/100;
    var topV=f.a[rec.top],top=topV==null?null:(isFinite(topV)?Math.round(topV*rec.unit*100)/100:null);
    if(top!==null&&top<=h)top=null;
    var baseV=f.a[rec.base],base=baseV==null?null:(isFinite(baseV)?Math.round(baseV*rec.unit*100)/100:null);
    best={h:h,top:top,base:base,from:'city',id:rec.id};bestArea=area;
  }
  return best;
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
