import { A3D } from '../core/state.js';
import { bimTrueNorthDeg } from '../survey/survey-arithmetic.js';
import { A3D_PLOT } from '../layers/layer-rules.js';
import { bimAwLook } from '../site-analysis/analysis-workspace.js';
import {
  A3D_MAP, BIM_MAP_STYLES, bimMapEvict, bimMapOrigin, bimMapPlan, bimMapRecord, bimMapSource,
  bimMapTileCorners
} from '../map/map-tiles.js';
import { BIM_DRAPE_ZREF, bimDrapeTiles, bimTerrainMeshData } from '../map/terrain-3d.js';

  /* ================= __acad3dV198: the map in the rendered view =================
     docs/research/research-rendered-map.md. The basemap the shaded view draws (V132), on the ground and draped on a
     terrain (V137), drawn by the rendered view too: lit by the site's sun and sky, the model's shadows on it. The tiles
     are the shaded view's own (the same plan, zoom, store and credit), so turning the rendered view on asks the tile
     server for nothing more. Each surface takes one picture: its tiles drawn side by side on a canvas (an atlas), the
     opacity mixed in against the colour under it, grey in the Analyze workspace's look; the surface's points know where
     on that canvas they are. Here are the plain numbers, with nothing of three.js, so Node tests them; the canvas and
     its texture are made in rendered-core.js. */
  var BIM_RV_MAP_CELL=256,BIM_RV_MAP_CELL_MAX=512;
  /* the tiles' places on the canvas: a rectangle of whole tiles (x0..x0+cols-1, y0..y0+rows-1 at zoom z), each drawn
     from its source (the tile, or the part of a parent standing in while it loads) into its own cell */
  function bimRvMapLayout(tiles,srcs){
    var x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity,i,t,s,iw,ih,cell=BIM_RV_MAP_CELL,draws=[];
    for(i=0;i<tiles.length;i++){t=tiles[i];if(t.x<x0)x0=t.x;if(t.y<y0)y0=t.y;if(t.x>x1)x1=t.x;if(t.y>y1)y1=t.y;}
    if(!tiles.length)return null;
    for(i=0;i<srcs.length;i++){s=srcs[i];if(!s)continue;iw=(s.e.img&&(s.e.img.naturalWidth||s.e.img.width))||256;if(iw>cell)cell=Math.min(BIM_RV_MAP_CELL_MAX,iw);}
    for(i=0;i<tiles.length;i++){
      s=srcs[i];if(!s)continue;t=tiles[i];
      iw=(s.e.img&&(s.e.img.naturalWidth||s.e.img.width))||256;ih=(s.e.img&&(s.e.img.naturalHeight||s.e.img.height))||256;
      draws.push({img:s.e.img,sx:s.u0*iw,sy:s.v0*ih,sw:(s.u1-s.u0)*iw,sh:(s.v1-s.v0)*ih,cx:t.x-x0,cy:t.y-y0});
    }
    return {z:tiles[0].z,x0:x0,y0:y0,cols:x1-x0+1,rows:y1-y0+1,cell:cell,draws:draws};
  }
  /* a point given in tiles at zoom z, as the canvas's u and v (v down the canvas, as the texture is not flipped) */
  function bimRvMapUV(L,tx,ty){return [(tx-L.x0)/L.cols,(ty-L.y0)/L.rows];}
  /* what a set of tiles looks like now, in a few characters: each tile and what stands for it (0 itself, d a parent d
     zooms up, - nothing yet) */
  function bimRvMapTilesSig(tiles,srcs){
    var s=[],i;
    for(i=0;i<tiles.length;i++)s.push(tiles[i].z+'/'+tiles[i].x+'/'+tiles[i].y+(srcs[i]?'='+srcs[i].up:'-'));
    return s.join(',');
  }
  /* where the site is and how it is turned, in a few characters: a change moves every tile */
  function bimRvMapPlaceSig(org){return org.lat+','+org.lon+','+bimTrueNorthDeg();}
  /* the frame's map, when it has one: the shaded view's plan, its tiles asked for and kept as that view keeps them,
     and what the rendered view draws of it. bg is the colour of the ground the opacity mixes toward. Under plot by
     layer there is none, as in the shaded view. */
  function bimRvMapFrame(V,W,H,bg){
    if(A3D_PLOT.on&&!A3D.mapFrame)return null;
    A3D_MAP.frame++;
    var plan=bimMapPlan(V,W,H),srcs=[],i,drawn=0,look=bimAwLook();
    for(i=0;i<plan.tiles.length;i++){srcs.push(bimMapSource(plan.tiles[i],plan.tpl));if(srcs[i])drawn++;}
    bimMapRecord('rendered',plan,drawn,srcs);
    bimMapEvict();
    if(!plan.tiles.length)return null;
    return {plan:plan,srcs:srcs,drawn:drawn,bg:bg,grey:look?look.grey:0,look:!!look};
  }
  /* the map on the ground: a square for each tile with something to show, on the lowest level, its corners where the
     shaded view puts them (the site's place and true north), each to its cell on the canvas */
  function bimRvMapFlatItem(M){
    var plan=M.plan,L=bimRvMapLayout(plan.tiles,M.srcs),pos=[],uv=[],i,t,k,a,b,c,d,y=plan.ground;
    if(!L||!L.draws.length)return null;
    for(i=0;i<plan.tiles.length;i++){
      if(!M.srcs[i])continue;
      t=plan.tiles[i];k=bimMapTileCorners(t,plan.org,y);
      a=bimRvMapUV(L,t.x,t.y);b=bimRvMapUV(L,t.x+1,t.y);c=bimRvMapUV(L,t.x+1,t.y+1);d=bimRvMapUV(L,t.x,t.y+1);
      pos.push(k.nw[0],k.nw[1],k.nw[2],k.ne[0],k.ne[1],k.ne[2],k.se[0],k.se[1],k.se[2],
        k.nw[0],k.nw[1],k.nw[2],k.se[0],k.se[1],k.se[2],k.sw[0],k.sw[1],k.sw[2]);
      uv.push(a[0],a[1],b[0],b[1],c[0],c[1],a[0],a[1],c[0],c[1],d[0],d[1]);
    }
    return {key:'mflat',
      sig:bimRvMapTilesSig(plan.tiles,M.srcs)+'|'+plan.opacity+'|'+M.grey+'|'+M.bg+'|'+y+'|'+bimRvMapPlaceSig(plan.org),
      map:{flat:true,pos:new Float32Array(pos),uv:new Float32Array(uv),n:pos.length/3,
        atlas:{layout:L,bg:M.bg,alpha:plan.opacity,grey:M.grey}}};
  }
  /* the map draped on a terrain: the tiles over its area (as the shaded view picks them), and each of its triangles'
     corners on the canvas from its Web Mercator place, in the order bimRvTerrainArrays writes them. Not in the Analyze
     workspace's look, where the shaded view leaves the surface plain. */
  function bimRvMapDrape(o,M,col){
    if(!M||M.look)return null;
    var org=bimMapOrigin(),D=org?bimTerrainMeshData(o,org):null,tiles,srcs=[],i,L,sc,uv;
    if(!D||!D.ext)return null;
    tiles=bimDrapeTiles(D.ext,M.plan.z,BIM_MAP_STYLES[M.plan.style].maxz);
    for(i=0;i<tiles.length;i++)srcs.push(bimMapSource(tiles[i],M.plan.tpl));
    L=bimRvMapLayout(tiles,srcs);
    if(!L||!L.draws.length)return null;
    sc=Math.pow(2,BIM_DRAPE_ZREF-L.z);
    uv=new Float32Array(D.count*2);
    for(i=0;i<D.count;i++){
      uv[i*2]=((D.mer[i*2]+D.ox)/sc-L.x0)/L.cols;
      uv[i*2+1]=((D.mer[i*2+1]+D.oy)/sc-L.y0)/L.rows;
    }
    return {sig:bimRvMapTilesSig(tiles,srcs)+'|'+M.plan.opacity+'|'+D.key,uv:uv,
      atlas:{layout:L,bg:col,alpha:M.plan.opacity,grey:0}};
  }
  /* the canvas of an atlas, no wider or taller than max pixels: the colour under the map, then each tile at the
     opacity, then grey toward its brightness by the look's amount */
  function bimRvMapCanvas(A,max){
    var L=A.layout,cell=L.cell,w=L.cols*cell,h=L.rows*cell,k=Math.min(1,max/w,max/h),cv=document.createElement('canvas'),ctx,i,d,cs,im,px,g,n;
    cv.width=Math.max(1,Math.floor(w*k));cv.height=Math.max(1,Math.floor(h*k));
    ctx=cv.getContext('2d');
    ctx.fillStyle=A.bg||'#cbc6bb';ctx.fillRect(0,0,cv.width,cv.height);
    ctx.globalAlpha=A.alpha;
    cs=cell*k;
    for(i=0;i<L.draws.length;i++){
      d=L.draws[i];
      try{ctx.drawImage(d.img,d.sx,d.sy,d.sw,d.sh,d.cx*cs,d.cy*cs,cs,cs);}
      catch(eI){console.warn('[BIM] Rendered view: a map tile could not be drawn',eI);}
    }
    ctx.globalAlpha=1;
    if(A.grey>0){
      try{
        im=ctx.getImageData(0,0,cv.width,cv.height);px=im.data;n=px.length;
        for(i=0;i<n;i+=4){g=px[i]*0.299+px[i+1]*0.587+px[i+2]*0.114;px[i]+=(g-px[i])*A.grey;px[i+1]+=(g-px[i+1])*A.grey;px[i+2]+=(g-px[i+2])*A.grey;}
        ctx.putImageData(im,0,0);
      }catch(eG){console.warn('[BIM] Rendered view: the map could not be greyed',eG);}
    }
    return cv;
  }
export {
  bimRvMapCanvas, bimRvMapDrape, bimRvMapFlatItem, bimRvMapFrame, bimRvMapLayout, bimRvMapTilesSig, bimRvMapUV
};
