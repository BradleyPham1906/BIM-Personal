import { A3D } from '../core/state.js';
import { camVecs } from '../core/mesh-primitives.js';
import { bimTrueNorthDeg } from '../survey/survey-arithmetic.js';
import { bimPresentGraphics } from '../layers/plot-by-layers.js';
import { A3D_PLOT } from '../layers/layer-rules.js';
import { bimResSwatch } from '../layers/analysis-data-rows.js';
import { bimResGone } from '../analysis/results-layers.js';
import { bimClbE } from '../site-analysis/climate-board.js';
import { bimDataLensScale, bimLensRows } from '../map/colour-lens.js';
import { A3D_MAP, bimMapCredit, bimMapSettings } from '../map/map-tiles.js';
import { bimDataList } from '../map/data-layers.js';
import { A3D_REV } from '../core/objects-save.js';
import {
  SHEET_SCALES, bimRenderSourceToCanvas, bimResolveViewportSource, bimSheetSolveCamera, bimSheetSourceOptions
} from './sheets.js';
import { bimBrdPx } from './board-figures.js';
import { bimBobBox } from './board-objects.js';
import { bimBdsAttr, bimBdsComp, bimBdsPos, bimBdsPx } from './board-design.js';


  /* ================= __acad3dV174d: map frames on a board, and their surround =================
     docs/research/research-presentation-boards.md, 4.6, 5.5 (D15 to D18). A map frame is a board object that shows a
     plan, an elevation or a saved view of the model at a scale, drawn by the sheets' viewport machinery
     (bimRenderSourceToCanvas), so it cannot disagree with a sheet. Inside a frame the site's data layers and the
     basemap reach paper (D18): V173 kept them off sheets, and a frame is where they belong; the basemap's credit is
     printed in the frame's corner, always. A legend, a north arrow and a scale bar are each bound to one frame:
     - the legend follows the shown data and result layers, in the Layers tab's order, and is empty when none is (D17);
     - the north arrow points to true north (the site's trueNorth) or plan north, plus a typed offset, for magnetic
       declination (D16): no magnetic model;
     - the scale bar is a 1-2-5 number, the largest whose two divisions fit between 15 and 40 per cent of the frame's
       width; metres to kilometres at 1000 m, feet to miles at a quarter mile (D15; the research's chooser, 240 of 240
       cases from 1:1 to 1:50,000,000). */
  var A3D_BMAP={img:{},busy:false};
  function bimBmapPxMm(){return 96/25.4*2;}   /* drawn at twice the page's pixels, so print is crisp */
  /* the sources a frame can show: the sheets' own, schedules aside */
  function bimBmapSources(){return bimSheetSourceOptions().filter(function(s){return s.kind!=='schedule';});}
  function bimBmapSrc(n){
    var m=/^(plan|elevation|view):(.+)$/.exec(n.src||''),r;
    if(!m)return {error:'No view is chosen'};
    r=bimResolveViewportSource({kind:m[1],refId:m[2]});
    return r;
  }
  /* a nice scale near a denominator, from the sheets' scales or, beyond them, 1, 2, 2.5 or 5 times a power of ten */
  function bimBmapNiceDen(v){
    var L=SHEET_SCALES.map(function(s){return s.denom;}),i,e,st=[1,2,2.5,5];
    for(i=0;i<L.length;i++)if(L[i]>=v-1e-9)return L[i];
    for(e=Math.floor(Math.log(v)/Math.LN10);e<12;e++)for(i=0;i<st.length;i++)if(st[i]*Math.pow(10,e)>=v-1e-9)return st[i]*Math.pow(10,e);
    return Math.round(v);
  }
  /* the scale that shows the whole source in a frame of w x h mm, and the pan that centres it: {den, px, py} */
  function bimBmapFit(n){
    var src=bimBmapSrc(n),k=bimBmapPxMm(),W=n.w*k,H=n.h*k,cam,b,V,d;
    if(src.error)return {den:100,px:0,py:0};
    cam=bimSheetSolveCamera(src,W,H,k,'fit',100,null);b=src.cam;
    V=camVecs({yaw:b.yaw,pitch:b.pitch,dist:1,tx:b.tx,ty:b.ty,tz:b.tz});
    d=[cam.tx-b.tx,cam.ty-b.ty,cam.tz-b.tz];
    return {den:bimBmapNiceDen(Math.max(1,1000*k*cam.dist/(1.2*H))),
      px:Math.round((d[0]*V.r[0]+d[1]*V.r[1]+d[2]*V.r[2])*1000)/1000,py:Math.round((d[0]*V.u[0]+d[1]*V.u[1]+d[2]*V.u[2])*1000)/1000};
  }
  function bimBmapFitDen(n){return bimBmapFit(n).den;}
  /* the frame's picture, as a data URL, drawn when the model, the frame or the basemap's tiles have changed */
  function bimBmapUrl(n,bid){
    var src=bimBmapSrc(n),k=bimBmapPxMm(),key,cv,u,tiles=0,t,ck=(bid||'')+'|'+n.id;   /* ids repeat across boards: the board's id too */
    if(src.error)return {error:src.error};
    for(t in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(t)&&A3D_MAP.cache[t].state==='ok')tiles++;
    key=A3D_REV+'|'+n.src+'|'+n.w+'|'+n.h+'|'+n.den+'|'+n.px+'|'+n.py+'|'+tiles+'|'+(A3D_PLOT.on?'p':'s')+'|'+(bimPresentGraphics()?1:0);
    if(A3D_BMAP.img[ck]&&A3D_BMAP.img[ck].key===key)return {url:A3D_BMAP.img[ck].url};
    if(A3D_BMAP.busy)return {error:'A frame inside a frame is not drawn'};
    A3D_BMAP.busy=true;A3D.mapFrame=true;
    try{
      cv=bimRenderSourceToCanvas(src,n.w*k,n.h*k,k,'ratio',n.den,[n.px||0,n.py||0],1);
      u=cv.toDataURL('image/png');
    }catch(eM){console.warn('[BIM] A map frame could not be drawn',eM);return {error:'The view could not be drawn: see the console'};}
    finally{A3D.mapFrame=false;A3D_BMAP.busy=false;}
    A3D_BMAP.img[ck]={key:key,url:u};
    return {url:u};
  }
  /* what the frame's corner credits: the basemap's, and every shown data layer's source, always (free data, credited) */
  function bimBmapCreditText(){
    var st=bimMapSettings(),out=[],d=[];
    if(st.style!=='off'&&bimMapCredit(st))out.push(bimMapCredit(st));
    bimDataList().forEach(function(L){if(L.visible&&L.credit&&d.indexOf(L.credit)<0)d.push(L.credit);});
    if(d.length)out.push('Data: '+d.join('; '));
    return out.join(' | ');
  }
  /* the frame's view, looked at from above? and where north points on it, in degrees clockwise from up, through the
     view's own camera, as the plan's north arrow is drawn (site/property.js, drawNorthArrow); null in an elevation */
  function bimBmapNorthDeg(F,nk){
    var src=bimBmapSrc(F),c,V,tn,n,sx,sy;
    if(src.error||!src.cam)return null;
    c=src.cam;
    if(Math.abs(Math.sin(c.pitch))<0.9)return null;   /* not a plan: an elevation or a section has no north on it */
    V=camVecs({yaw:c.yaw,pitch:c.pitch,dist:1,tx:0,ty:0,tz:0});
    tn=(nk==='plan'?0:bimTrueNorthDeg())*Math.PI/180;
    n=[Math.sin(tn),0,-Math.cos(tn)];
    sx=n[0]*V.r[0]+n[1]*V.r[1]+n[2]*V.r[2];sy=n[0]*V.u[0]+n[1]*V.u[1]+n[2]*V.u[2];
    if(!(Math.abs(sx)+Math.abs(sy)>1e-9))return null;
    return Math.atan2(sx,sy)*180/Math.PI;
  }
  /* ---- the surround ---- */
  /* the legend's rows: the shown data layers (their classes, or their colour) and result layers */
  function bimBmapLegendRows(){
    var out=[],credits=[];
    bimDataList().forEach(function(L){
      var ds,rows;
      if(!L.visible)return;
      if(L.by){try{ds=bimDataLensScale(L);rows=ds?bimLensRows(ds.scale,ds.none):[];}catch(e){rows=[];}}
      if(rows&&rows.length){out.push({h:L.name});rows.slice(0,12).forEach(function(r){out.push({c:r.col,t:r.name});});}
      else out.push({c:/^#[0-9a-fA-F]{6}$/.test(L.color||'')?L.color:'#7f9db8',t:L.name});
      if(L.credit&&credits.indexOf(L.credit)<0)credits.push(L.credit);
    });
    (A3D.resultLayers||[]).forEach(function(R){if(R.visible!==false&&!bimResGone(R))out.push({c:bimResSwatch(R),t:R.name});});
    return {rows:out,credits:credits};
  }
  /* the scale bar's numbers: frame width mm, scale denominator, 'm' or 'ft' -> {seg, label, segs, barMm} */
  function bimBmapBar(frameMm,denom,unit){
    var FT=0.3048,MI=5280*FT,segs=2,minMm=Math.max(20,frameMm*0.15),maxMm=Math.max(minMm,frameMm*0.4),mPerMm=denom/1000;
    var uM=unit==='ft'?FT:1,big=unit==='ft'?MI:1000,r,r2,label=unit==='ft'?'ft':'m';
    function ladder(lo,hi){var out=[],e,i,st=[1,2,5];for(e=Math.floor(Math.log(lo)/Math.LN10)-1;e<=Math.ceil(Math.log(hi)/Math.LN10)+1;e++)for(i=0;i<3;i++)out.push(st[i]*Math.pow(10,e));return out;}
    function pick(u){
      var lo=minMm*mPerMm/segs/u,hi=maxMm*mPerMm/segs/u,L=ladder(lo,hi),best=null,near=null,i,w,d;
      for(i=0;i<L.length;i++){
        w=L[i]*u/mPerMm*segs;
        if(w>=minMm-1e-9&&w<=maxMm+1e-9)best=L[i];
        d=w<minMm?minMm-w:(w>maxMm?w-maxMm:0);
        if(near===null||d<near.d)near={v:L[i],d:d};
      }
      return best!==null?{v:best,fit:true}:{v:near.v,fit:false};
    }
    r=pick(uM);
    if(r.v*uM*segs>=(unit==='ft'?big/4:big)){r2=pick(big);if(r2.fit||!r.fit){r=r2;label=unit==='ft'?'mi':'km';}}
    var segM=r.v*(label==='km'?1000:label==='mi'?MI:uM);
    return {seg:r.v,label:label,segs:segs,barMm:segM/mPerMm*segs};
  }
  function bimBmapFmt(v){return String(+v.toPrecision(6));}
  /* the frame an object is bound to, on the same board: its id, or the first frame */
  function bimBmapFrameOf(n,objs){
    var i,first=null;
    for(i=0;i<objs.length;i++)if(objs[i].t==='map'){if(objs[i].id===n.fr)return objs[i];if(!first)first=objs[i];}
    return n.fr?null:first;
  }
  /* ---- drawn ---- */
  function bimBmapHtml(n,ox,oy,ctx){
    var b=bimBobBox(n),pos=bimBdsPos(b,ox,oy)+bimBdsComp(n,ctx),attr,F,r,h,a,bar,W,s,i,x,cr;
    attr=function(cls){return bimBdsAttr(n,cls,ctx);};
    if(n.t==='map'){
      r=bimBmapUrl(n,ctx.B?ctx.B.id:'');cr=bimBmapCreditText();
      if(r.error)return '<div'+attr('a3d-clb-dmap ph')+' style="'+pos+'"><span>'+bimClbE(r.error)+'</span></div>';
      return '<div'+attr('a3d-clb-dmap')+' style="'+pos+'"><img alt="'+bimClbE(n.nm||'Map frame')+'" src="'+r.url+'">'+
        (cr?'<span class="a3d-clb-dmapcr" style="font-size:'+bimBdsPx(1.8)+'px">'+bimClbE(cr)+'</span>':'')+'</div>';
    }
    F=bimBmapFrameOf(n,ctx.allObjs||[]);
    if(n.t==='legend'){
      r=bimBmapLegendRows();
      if(!r.rows.length)return ctx.edit?'<div'+attr('a3d-clb-dleg ph')+' style="'+pos+'"><span>Legend: no data or result layer is shown</span></div>':'';   /* hidden when empty (D17) */
      h='<div class="a3d-clb-dlegt" style="font-size:'+bimBdsPx(3)+'px">'+bimClbE(n.ttl||'Legend')+'</div>';
      r.rows.forEach(function(q){h+=q.h?'<div class="a3d-clb-dlegh" style="font-size:'+bimBdsPx(2.4)+'px">'+bimClbE(q.h)+'</div>':
        '<div class="a3d-clb-dlegr" style="font-size:'+bimBdsPx(2.2)+'px"><i style="background:'+bimClbE(q.c)+'"></i>'+bimClbE(q.t)+'</div>';});
      if(r.credits.length)h+='<div class="a3d-clb-dlegc" style="font-size:'+bimBdsPx(1.7)+'px">Data: '+bimClbE(r.credits.join('; '))+'</div>';
      return '<div'+attr('a3d-clb-dleg')+' style="'+pos+'">'+h+'</div>';
    }
    if(n.t==='north'){
      if(!F)return ctx.edit?'<div'+attr('a3d-clb-dleg ph')+' style="'+pos+'"><span>North arrow: no map frame</span></div>':'';
      a=bimBmapNorthDeg(F,n.nk);
      if(a===null)return ctx.edit?'<div'+attr('a3d-clb-dleg ph')+' style="'+pos+'"><span>The frame\'s view is not a plan: it has no north</span></div>':'';
      a+=(n.off||0);
      W=Math.min(b.w,b.h);
      return '<svg'+attr('a3d-clb-dshp')+' xmlns="http://www.w3.org/2000/svg" style="'+pos+'" viewBox="-50 -50 100 100" aria-label="'+(n.nk==='plan'?'Plan north':'True north')+'">'+
        '<g transform="rotate('+Math.round(a*100)/100+')"><polygon points="0,-40 14,22 0,12 -14,22" fill="#0b0b0b"/><polygon points="0,-40 0,12 -14,22" fill="#ffffff" stroke="#0b0b0b" stroke-width="1.5"/>'+
        '<text x="0" y="-44" text-anchor="middle" font-size="16" font-family="Inter,system-ui,sans-serif" font-weight="700" fill="#0b0b0b">N</text></g></svg>';
    }
    if(n.t==='sbar'){
      if(!F)return ctx.edit?'<div'+attr('a3d-clb-dleg ph')+' style="'+pos+'"><span>Scale bar: no map frame</span></div>':'';
      bar=bimBmapBar(F.w,F.den,n.un==='ft'?'ft':'m');
      W=bimBdsPx(bar.barMm);s=W/bar.segs;x=bimBdsPx(2);
      h='<svg'+attr('a3d-clb-dshp')+' xmlns="http://www.w3.org/2000/svg" style="'+pos+'" viewBox="0 0 '+bimBdsPx(b.w)+' '+bimBdsPx(b.h)+'" aria-label="Scale bar, 1:'+F.den+'">';
      for(i=0;i<bar.segs;i++)h+='<rect x="'+bimBrdPx(x+i*s)+'" y="'+bimBdsPx(1)+'" width="'+bimBrdPx(s)+'" height="'+bimBdsPx(2)+'" fill="'+(i%2?'#ffffff':'#0b0b0b')+'" stroke="#0b0b0b" stroke-width="1"/>';
      for(i=0;i<=bar.segs;i++)h+='<text x="'+bimBrdPx(x+i*s)+'" y="'+bimBdsPx(6)+'" text-anchor="middle" font-size="'+bimBdsPx(2.4)+'" font-family="Inter,system-ui,sans-serif" fill="#0b0b0b">'+bimBmapFmt(bar.seg*i)+(i===bar.segs?' '+bar.label:'')+'</text>';
      h+='<text x="'+bimBrdPx(x)+'" y="'+bimBdsPx(9.5)+'" font-size="'+bimBdsPx(2)+'" font-family="Inter,system-ui,sans-serif" fill="#52514e">1:'+F.den+'</text>';
      return h+'</svg>';
    }
    return '';
  }
export { bimBmapBar, bimBmapFit, bimBmapHtml, bimBmapNiceDen, bimBmapSources };
