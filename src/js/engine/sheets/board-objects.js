import { A3D } from '../core/state.js';
import { bimLayerById, bimLayerZero } from '../layers/layer-rules.js';
import { bimLayerTree } from '../layers/layers-panel.js';


  /* ================= __acad3dV174a: a board's objects, on the one layer table =================
     docs/research/research-presentation-boards.md, 11a (R1 to R4, the owner, 2026-11-08: "everything should be one
     just like autocad layer system"). A board is paper space, as an AutoCAD layout is: its rectangles, ellipses,
     lines, polygons, stars, text and images are objects drawn on it (B.objs), and each is on a layer of the project's
     one layer table (A3D.layers), the model's. A V172b figure of the board is one object of the list too ('fig',
     naming its figure; its place stays in the board's columns), so an old board looks as it did (D19).
     Paint order is the layer order (R3): the Layers list read from the bottom up, a layer higher in it drawn over
     those below; within a layer, the list's order (Draw order: Bring to front, Send to back). A sub-layer is how
     objects are grouped (R4). Transparency and Blend are ByLayer unless an object has its own (R2), applied to each
     object as AutoCAD applies a layer's transparency, and drawn in the Presentation appearance and in Present.
     A mask clips the objects of its own layer drawn above it, up to the next mask of that layer (R4, D5).
     Millimetres are as printed: a board's 1408 CSS px are 372.5 mm on paper. Functions only, no tables made at
     load: a project is read before this file has run (bimPresValid). */
  function bimBobPxMm(){return 96/25.4;}
  function bimBobMax(){return 400;}
  /* the W3C 16 under Figma's names, in Figma's order (D2): [key, name, CSS and canvas keyword] */
  function bimBobBlends(){
    return [['normal','Normal','normal'],['darken','Darken','darken'],['multiply','Multiply','multiply'],['color-burn','Color burn','color-burn'],
      ['lighten','Lighten','lighten'],['screen','Screen','screen'],['color-dodge','Color dodge','color-dodge'],['overlay','Overlay','overlay'],
      ['soft-light','Soft light','soft-light'],['hard-light','Hard light','hard-light'],['difference','Difference','difference'],
      ['exclusion','Exclusion','exclusion'],['hue','Hue','hue'],['saturation','Saturation','saturation'],['color','Color','color'],['luminosity','Luminosity','luminosity']];
  }
  function bimBobBlend(k){var L=bimBobBlends(),i;for(i=0;i<L.length;i++)if(L[i][0]===k)return L[i];return null;}
  /* the kinds: [key, name, can be a mask] */
  function bimBobKinds(){
    return [['rect','Rectangle',1],['ellipse','Ellipse',1],['line','Line',1],['poly','Polygon',1],['star','Star',1],['text','Text',0],['image','Image',1],['fig','Figure',0]];
  }
  function bimBobKind(t){var L=bimBobKinds(),i;for(i=0;i<L.length;i++)if(L[i][0]===t)return L[i];return null;}
  function bimBobMaskTypes(){return [['alpha','Alpha'],['vector','Vector'],['lum','Luminance']];}
  /* ---- the record ---- */
  function bimBobNum(v,lo,hi,d){v=typeof v==='number'&&isFinite(v)?v:d;return Math.max(lo,Math.min(hi,Math.round(v*1000)/1000));}
  function bimBobCol(v,d){
    if(v==='none')return 'none';
    if(typeof v==='string'&&/^#[0-9a-fA-F]{6}$/.test(v))return v.toLowerCase();
    return d;
  }
  /* one object, good, or null */
  function bimBobOne(n,seen){
    var K,r;
    if(!n||typeof n!=='object'||typeof n.t!=='string')return null;
    K=bimBobKind(n.t);if(!K)return null;
    if(typeof n.id!=='string'||!/^e\d{1,6}$/.test(n.id)||seen[n.id])return null;
    seen[n.id]=1;
    r={id:n.id,t:n.t};
    if(typeof n.layer==='string'&&n.layer&&n.layer.length<=120)r.layer=n.layer;
    if(typeof n.nm==='string'&&n.nm.replace(/\s+/g,''))r.nm=n.nm.replace(/\s+/g,' ').trim().slice(0,80);
    if(typeof n.tr==='number'&&isFinite(n.tr))r.tr=Math.round(Math.max(0,Math.min(90,n.tr)));   /* absent: ByLayer */
    if(typeof n.bm==='string'&&bimBobBlend(n.bm))r.bm=n.bm;   /* absent: ByLayer */
    if(n.t==='fig'){
      if(typeof n.k!=='string'||!/^f\d{1,6}$/.test(n.k))return null;
      r.k=n.k;
      return r;
    }
    r.x=bimBobNum(n.x,-2000,20000,0);r.y=bimBobNum(n.y,-2000,20000,0);
    if(n.t==='line'){r.w=bimBobNum(n.w,-20000,20000,40);r.h=bimBobNum(n.h,-20000,20000,0);}
    else{r.w=bimBobNum(n.w,0.5,20000,40);r.h=bimBobNum(n.h,0.5,20000,30);}
    if(K[2]&&(n.mask==='alpha'||n.mask==='vector'||n.mask==='lum'))r.mask=n.mask;
    if(n.t==='rect'||n.t==='ellipse'||n.t==='poly'||n.t==='star'){r.fill=bimBobCol(n.fill,'#c3c2b7');r.fop=bimBobNum(n.fop,0,1,1);}
    if(n.t==='rect'||n.t==='ellipse'||n.t==='poly'||n.t==='star'||n.t==='line'){
      r.stroke=bimBobCol(n.stroke,n.t==='line'?'#0b0b0b':'none');
      r.sw=bimBobNum(n.sw,0,50,n.t==='line'?0.5:0.35);
    }
    if(n.t==='rect')r.r=bimBobNum(n.r,0,1000,0);
    if(n.t==='poly')r.n=Math.round(bimBobNum(n.n,3,60,6));
    if(n.t==='star'){r.n=Math.round(bimBobNum(n.n,3,60,5));r.ri=bimBobNum(n.ri,0.05,0.95,0.38);}
    if(n.t==='line'){if(n.a0===true)r.a0=true;if(n.a1===true)r.a1=true;}
    if(n.t==='text'){
      r.s=typeof n.s==='string'?n.s.slice(0,4000):'Text';
      r.fs=bimBobNum(n.fs,4,400,14);
      r.fw=n.fw===700?700:400;
      r.al=(n.al==='center'||n.al==='right')?n.al:'left';
      r.col=bimBobCol(n.col,'#0b0b0b');if(r.col==='none')r.col='#0b0b0b';
      r.fit=(n.fit==='auto-w'||n.fit==='fixed')?n.fit:'auto-h';
    }
    if(n.t==='image'){
      r.src=typeof n.src==='string'&&/^h[0-9a-f]{16}$/.test(n.src)?n.src:'';
      r.fit=(n.fit==='fit'||n.fit==='tile')?n.fit:'fill';
    }
    return r;
  }
  /* a board's objects as saved, good, agreeing with its figures; null when it has none */
  function bimBobValid(L,figs){
    if(!Array.isArray(L))return null;
    var seen={},out=[],i,n;
    for(i=0;i<L.length&&out.length<bimBobMax();i++){n=bimBobOne(L[i],seen);if(n)out.push(n);}
    return bimBobSync(out,figs||[]);
  }
  function bimBobNewId(L){
    var m=0;
    L.forEach(function(n){var r=/^e(\d+)$/.exec(n.id);if(r&&+r[1]>m)m=+r[1];});
    return 'e'+(m+1);
  }
  function bimBobFind(L,id){var i;for(i=0;i<L.length;i++)if(L[i].id===id)return {n:L[i],i:i};return null;}
  /* the list agrees with the figures: an object whose figure is gone is dropped, a figure with none gets one at the
     list's end (its layer the first layer's), in the order given (reading order); a figure named twice keeps its first */
  function bimBobSync(L,figs){
    var have={},seen={},i;
    (figs||[]).forEach(function(F){if(F&&F.k)have[F.k]=1;});
    for(i=L.length-1;i>=0;i--)if(L[i].t==='fig'&&!have[L[i].k])L.splice(i,1);
    L.forEach(function(n){if(n.t==='fig')seen[n.k]=(seen[n.k]||0)+1;});
    for(i=L.length-1;i>=0;i--)if(L[i].t==='fig'&&seen[L[i].k]>1){seen[L[i].k]--;L.splice(i,1);}
    (figs||[]).forEach(function(F){if(F&&F.k&&!seen[F.k]){seen[F.k]=1;L.push({id:bimBobNewId(L),t:'fig',k:F.k});}});
    return L;
  }
  /* ---- the layer an object is on, and what it takes from it ---- */
  function bimBobLayer(o){return (o&&o.layer&&bimLayerById(o.layer))||bimLayerZero();}
  /* transparency, 0 to 90 per cent, its own or its layer's */
  function bimBobTr(o){
    if(typeof o.tr==='number')return o.tr;
    var ly=bimBobLayer(o),t=ly?+ly.transparency:0;
    return isFinite(t)&&t>0?Math.min(90,t):0;
  }
  /* the blend mode, its own or its layer's */
  function bimBobBm(o){
    if(o.bm)return o.bm;
    var ly=bimBobLayer(o);
    return ly&&bimBobBlend(ly.blend)?ly.blend:'normal';
  }
  /* ---- paint order (R3): the layer tree read from the bottom up, then the list's order within a layer ---- */
  function bimBobRank(){
    var T=bimLayerTree(),R={},i;
    for(i=0;i<T.length;i++)R[T[i].ly.id]=T.length-1-i;
    return R;
  }
  function bimBobPaint(L){
    var R=bimBobRank(),z=bimLayerZero(),zid=z?z.id:'';
    return L.map(function(n,i){var ly=bimBobLayer(n),id=ly?ly.id:zid;return {n:n,i:i,ly:id,r:R.hasOwnProperty(id)?R[id]:-1};})
      .sort(function(a,b){return a.r-b.r||a.i-b.i;});
  }
  /* the paint list cut into runs: a mask masks the objects of its own layer above it, up to that layer's next mask;
     a mask whose layer is off masks nothing and its objects are not drawn either. [{mask, items:[objects]}] */
  function bimBobRuns(P){
    var runs=[],cur=null;
    P.forEach(function(p){
      var n=p.n;
      if(n.mask){cur={mask:n,ly:p.ly,items:[]};runs.push(cur);return;}
      if(cur&&cur.ly===p.ly){cur.items.push(n);return;}
      cur=null;
      runs.push({mask:null,ly:p.ly,items:[n]});
    });
    return runs;
  }
  /* Draw order within its layer (R3): 'forward', 'backward', 'front', 'back'; true when it moved */
  function bimBobReorder(L,id,how){
    var f=bimBobFind(L,id),ly,same=[],i,k,j;
    if(!f)return false;
    ly=bimBobLayer(f.n);
    for(i=0;i<L.length;i++)if(bimBobLayer(L[i])===ly)same.push(i);
    k=same.indexOf(f.i);
    j=how==='forward'?k+1:how==='backward'?k-1:how==='front'?same.length-1:how==='back'?0:k;
    j=Math.max(0,Math.min(same.length-1,j));
    if(j===k)return false;
    L.splice(same[j],0,L.splice(f.i,1)[0]);
    return true;
  }
  /* ---- geometry, in mm ---- */
  /* a figure's box in mm, from its columns (V172b: x*P, w*P-G px) */
  function bimBobFigBox(F,P,G){
    var k=bimBobPxMm();
    return {x:F.x*P/k,y:F.y*P/k,w:(F.w*P-G)/k,h:(F.h*P-G)/k};
  }
  /* a box in mm back to a figure's columns */
  function bimBobFigCols(b,P,G){
    var k=bimBobPxMm();
    return {x:b.x*k/P,y:b.y*k/P,w:(b.w*k+G)/P,h:(b.h*k+G)/P};
  }
  function bimBobBox(n,figBox){
    if(n.t==='fig')return figBox?figBox(n.k):null;
    if(n.t==='line')return {x:Math.min(n.x,n.x+n.w),y:Math.min(n.y,n.y+n.h),w:Math.abs(n.w),h:Math.abs(n.h)};
    return {x:n.x,y:n.y,w:n.w,h:n.h};
  }
  function bimBobUnion(a,b){
    var x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
    return {x:x,y:y,w:Math.max(a.x+a.w,b.x+b.w)-x,h:Math.max(a.y+a.h,b.y+b.h)-y};
  }
  /* moved by dx, dy mm; a figure through moveFig(k, dx, dy) */
  function bimBobShift(n,dx,dy,moveFig){
    if(n.t==='fig'){if(moveFig)moveFig(n.k,dx,dy);return;}
    n.x=Math.round((n.x+dx)*1000)/1000;n.y=Math.round((n.y+dy)*1000)/1000;
  }
  /* ---- the layer table's side ---- */
  /* how many objects of every board are on a layer (Delete Layer refuses a layer that holds any) */
  function bimBobOnLayer(id){
    var P=A3D.pres,n=0;
    if(!P||!Array.isArray(P.boards))return 0;
    P.boards.forEach(function(B){(B&&Array.isArray(B.objs)?B.objs:[]).forEach(function(o){var ly=bimBobLayer(o);if(ly&&ly.id===id)n++;});});
    return n;
  }
export {
  bimBobBlend, bimBobBlends, bimBobBm, bimBobBox, bimBobFigBox, bimBobFigCols, bimBobFind, bimBobKind,
  bimBobLayer, bimBobMaskTypes, bimBobMax, bimBobNewId, bimBobOnLayer, bimBobPaint, bimBobPxMm, bimBobReorder,
  bimBobRuns, bimBobShift, bimBobSync, bimBobTr, bimBobUnion, bimBobValid
};
