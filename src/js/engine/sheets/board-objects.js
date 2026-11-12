import { A3D } from '../core/state.js';
import { bimLayerById, bimLayerZero } from '../layers/layer-rules.js';
import { bimLayerTree } from '../layers/layers-panel.js';
import { BIM_BRD_P0 } from './board-figures.js';
import { bimBalLayout } from './board-arrange.js';
import { bimLvBindValid, bimLvOvValid } from './live-text.js';


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
    return [['rect','Rectangle',1],['ellipse','Ellipse',1],['line','Line',1],['poly','Polygon',1],['star','Star',1],['text','Text',0],['image','Image',1],['fig','Figure',0],
      ['tblock','Title block',0],['border','Sheet frame',0],   /* __acad3dV174c */
      ['map','Map frame',0],['legend','Legend',0],['north','North arrow',0],['sbar','Scale bar',0]];   /* __acad3dV174d */
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
    /* __acad3dV174b: in its layer's auto layout: Fill on an axis, or out of the flow ("ignore auto layout") */
    if(n.lw==='fill'&&n.t!=='fig')r.lw='fill';
    if(n.lh==='fill'&&n.t!=='fig')r.lh='fill';
    if(n.la===true)r.la=true;
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
      /* __acad3dV175a: a live text's binding, its overrides and the source's words when each was made; never its value (D8) */
      if(n.bind){
        r.bind=bimLvBindValid(n.bind);
        if(!r.bind)delete r.bind;
        else if((r.ov=bimLvOvValid(n.ov,null))){r.ovAt=bimLvOvValid(n.ovAt,r.ov);if(!r.ovAt)delete r.ovAt;}
        else delete r.ov;
      }
    }
    if(n.t==='image'){
      r.src=typeof n.src==='string'&&/^h[0-9a-f]{16}$/.test(n.src)?n.src:'';
      r.fit=(n.fit==='fit'||n.fit==='tile')?n.fit:'fill';
    }
    /* __acad3dV174c: a title block, ISO 7200's at the bottom right or a US strip at the right (D14); the sheet's frame line */
    if(n.t==='tblock'){
      r.st=n.st==='us'?'us':'iso';
      if(typeof n.num==='string')r.num=n.num.replace(/\s+/g,' ').trim().slice(0,40);   /* its identification number */
      if(typeof n.dt==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(n.dt))r.dt=n.dt;   /* its date of issue, kept */
    }
    if(n.t==='border')r.sw=bimBobNum(n.sw,0.1,5,0.7);
    /* __acad3dV174d: a map frame's view, scale and pan; the surround's frame, and their own settings */
    if(n.t==='map'){
      r.src=typeof n.src==='string'&&/^(plan|elevation|view):.{1,100}$/.test(n.src)?n.src:'';
      r.den=bimBobNum(n.den,1,1e8,500);r.px=bimBobNum(n.px,-1e7,1e7,0);r.py=bimBobNum(n.py,-1e7,1e7,0);
    }
    if(n.t==='legend'||n.t==='north'||n.t==='sbar'){if(typeof n.fr==='string'&&/^e\d{1,6}$/.test(n.fr))r.fr=n.fr;}
    if(n.t==='legend')r.ttl=typeof n.ttl==='string'?n.ttl.slice(0,80):'Legend';
    if(n.t==='north'){r.nk=n.nk==='plan'?'plan':'true';r.off=bimBobNum(n.off,-360,360,0);}
    if(n.t==='sbar')r.un=n.un==='ft'?'ft':'m';
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
  /* what moves a figure of a list by dx, dy mm: its columns, kept on the board's 12 */
  function bimBobFigMover(figs){
    return function(k,dx,dy){
      var i,F,s=bimBobPxMm()/BIM_BRD_P0;
      for(i=0;i<figs.length;i++)if(figs[i].k===k){
        F=figs[i];
        F.x=Math.max(0,Math.min(12-F.w,Math.round((F.x+dx*s)*10000)/10000));
        F.y=Math.max(0,Math.round((F.y+dy*s)*10000)/10000);
      }
    };
  }
  /* moved by dx, dy mm; a figure through moveFig(k, dx, dy) */
  function bimBobShift(n,dx,dy,moveFig){
    if(n.t==='fig'){if(moveFig)moveFig(n.k,dx,dy);return;}
    n.x=Math.round((n.x+dx)*1000)/1000;n.y=Math.round((n.y+dy)*1000)/1000;
  }
  /* ---- __acad3dV174b: a layer's auto layout on one board (D7, R4: the sub-layer is the group) ----
     B.lay = {layer id: {dir 'row'|'column'|'wrap', gap mm or 'auto', pad mm, am and ac 'start'|'center'|'end', x, y (the
     stack's corner, mm), sw and sh 'hug'|'fixed', w, h}}. Its objects are that layer's on the board, in Draw order, masks
     left out. */
  function bimBobLayOne(L){
    if(!L||typeof L!=='object'||(L.dir!=='row'&&L.dir!=='column'&&L.dir!=='wrap'))return null;
    var al=function(v){return v==='center'||v==='end'?v:'start';};
    return {dir:L.dir,gap:L.gap==='auto'?'auto':bimBobNum(L.gap,-1000,1000,5),pad:bimBobNum(L.pad,0,1000,0),am:al(L.am),ac:al(L.ac),
      x:bimBobNum(L.x,-2000,20000,0),y:bimBobNum(L.y,-2000,20000,0),sw:L.sw==='fixed'?'fixed':'hug',sh:L.sh==='fixed'?'fixed':'hug',
      w:bimBobNum(L.w,1,20000,100),h:bimBobNum(L.h,1,20000,60)};
  }
  function bimBobLayValid(m){
    var out={},k,n=0,L;
    if(!m||typeof m!=='object')return null;
    for(k in m)if(m.hasOwnProperty(k)&&typeof k==='string'&&k.length<=120&&n<100){L=bimBobLayOne(m[k]);if(L){out[k]=L;n++;}}
    return n?out:null;
  }
  /* the objects of a layer in a stack, in Draw order */
  function bimBobLayKids(objs,lyId){return objs.filter(function(o){var ly=bimBobLayer(o);return ly&&ly.id===lyId&&!o.mask;});}
  /* every stack of the board laid out: W {objs, figs, lay}; objects moved (a figure through moveFig) and Fill sized.
     narrow: a phone, where a row is shown as a column, in reading order (D11). {layer id: the stack's box} */
  function bimBobLayApply(W,figBox,moveFig,narrow){
    var boxes={},k,L,kids,F,res;
    if(!W.lay)return boxes;
    for(k in W.lay)if(W.lay.hasOwnProperty(k)){
      L=W.lay[k];
      if(!bimLayerById(k))continue;
      kids=bimBobLayKids(W.objs,k);
      F={dir:narrow||L.dir==='column'?'column':'row',wrap:!narrow&&L.dir==='wrap',gap:L.gap,pad:L.pad,alignMain:L.am,alignCross:L.ac,
        sizeW:L.sw,sizeH:L.sh,w:L.w,h:L.h,children:kids.map(function(o){
          var b=bimBobBox(o,figBox)||{x:0,y:0,w:0,h:0};
          return {w:b.w,h:b.h,x:b.x-L.x,y:b.y-L.y,sizeW:o.lw==='fill'?'fill':'fixed',sizeH:o.lh==='fill'?'fill':'fixed',absolute:!!o.la};
        })};
      res=bimBalLayout(F);
      kids.forEach(function(o,i){
        var r=res.kids[i],b=bimBobBox(o,figBox);
        if(!r||o.la||!b)return;
        if(o.t!=='line'&&o.t!=='fig'){if(o.lw==='fill')o.w=Math.max(0.5,Math.round(r.w*1000)/1000);if(o.lh==='fill')o.h=Math.max(0.5,Math.round(r.h*1000)/1000);}
        bimBobShift(o,Math.round((L.x+r.x-b.x)*1000)/1000,Math.round((L.y+r.y-b.y)*1000)/1000,moveFig);
      });
      boxes[k]={x:L.x,y:L.y,w:res.w,h:res.h};
    }
    return boxes;
  }
  /* after a drag in a stack: its objects put in Draw order by where they now are, so the next layout follows */
  function bimBobLayReorder(W,lyId,figBox){
    var L=W.lay&&W.lay[lyId],idx=[],kids=[],key;
    if(!L)return false;
    W.objs.forEach(function(o,i){var ly=bimBobLayer(o);if(ly&&ly.id===lyId&&!o.mask){idx.push(i);kids.push(o);}});
    key=function(o){var b=bimBobBox(o,figBox)||{x:0,y:0,w:0,h:0},cx=b.x+b.w/2,cy=b.y+b.h/2;
      return L.dir==='column'?cy:(L.dir==='wrap'?Math.round(cy/Math.max(1,b.h))*100000+cx:cx);};
    kids.sort(function(a,b){return key(a)-key(b);});
    idx.forEach(function(i,j){W.objs[i]=kids[j];});
    return true;
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
  bimBobBlend, bimBobBlends, bimBobBm, bimBobBox, bimBobFigBox, bimBobFigCols, bimBobFigMover, bimBobFind,
  bimBobKind, bimBobLayApply, bimBobLayKids, bimBobLayReorder, bimBobLayValid, bimBobLayer, bimBobMaskTypes,
  bimBobMax, bimBobNewId, bimBobOnLayer, bimBobPaint, bimBobPxMm, bimBobReorder, bimBobRuns, bimBobShift,
  bimBobSync, bimBobTr, bimBobUnion, bimBobValid
};
