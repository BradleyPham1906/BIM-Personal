import { A3D } from '../core/state.js';
import { A3D_SNAP, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayerById, bimLayerEff, bimLayerZero } from '../layers/layer-rules.js';
import { refreshLayers } from '../layers/analysis-data-rows.js';
import { A3D_UNITS } from '../properties/palette.js';
import { A3D_CLB, bimClbEl, bimClbOpen } from '../site-analysis/climate-board.js';
import { refreshProps } from '../site-analysis/panel.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { bimLtMenuOpen } from './layout-tabs.js';
import {
  bimBrdBands, bimBrdEditing, bimBrdFigsValid, bimBrdPx, bimBrdRec, bimFigEntry
} from './board-figures.js';
import { bimBrdRedraw, bimBrdWorking } from './board-edit.js';
import {
  bimBobBox, bimBobFigMover, bimBobFind, bimBobKind, bimBobLayApply, bimBobLayReorder, bimBobLayValid,
  bimBobLayer, bimBobMax, bimBobNewId, bimBobPxMm, bimBobReorder, bimBobShift, bimBobSync, bimBobUnion,
  bimBobValid
} from './board-objects.js';
import { bimBalGaps, bimBalSnap } from './board-arrange.js';
import { bimPgFit, bimPgLabel, bimPgValid } from './page-sizes.js';
import { bimBimgAdd } from './board-images.js';
import { bimBdsFigBoxer, bimBdsPos, bimBdsPres, bimBdsPx } from './board-design.js';
import { bimBmapFit, bimBmapSources } from './board-map.js';
import { bimBdePage } from './board-design-tools.js';
import { bimLvFieldMenu, bimLvNumberMenu } from './live-edit.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV174a: drawing on a board, in Edit =================
     docs/research/research-presentation-boards.md, 11a. The board's Draw menu puts a rectangle, an ellipse, a line, an
     arrow, a polygon, a star, text or an image on the board, on the current layer, as AutoCAD draws on the current
     layer. A click selects an object (Shift or Ctrl adds); its properties are in the Properties panel and its row is
     under its layer in the Layers tab, where it is selected too. The arrows nudge 1 mm, 10 with Shift; Delete
     removes; Ctrl+] and Ctrl+[ bring forward and send backward within its layer, with Shift to the front and the
     back. A locked layer's objects are not picked. Every change is one undo step, kept with the project. */
  var A3D_BDE={sel:[],drag:null,file:null,hinted:false,was:false};
  /* the board's objects and figures to change: copies, the objects made from the figures when there are none yet
     (each figure on the first layer, in reading order) */
  function bimBdeWork(){
    var B=bimBrdRec(),figs,objs,order=[];
    if(!B)return null;
    figs=bimBrdWorking(B);
    if(B.objs)objs=JSON.parse(JSON.stringify(B.objs));
    else{objs=[];bimBrdBands(figs).forEach(function(D){D.f.forEach(function(F){order.push(F);});});}
    bimBobSync(objs,order.length?order:figs);
    return {B:B,figs:figs,objs:objs,off:B.off?B.off.slice():null,lay:B.lay?JSON.parse(JSON.stringify(B.lay)):{},page:B.page?{key:B.page.key,o:B.page.o}:null};
  }
  function bimBdeFigBox(W){return bimBdsFigBoxer(W.figs);}
  function bimBdeMoveFig(W){return bimBobFigMover(W.figs);}
  /* one undo step: the board's figures and objects as W has them */
  function bimBdeCommit(W,msg,sel){
    var F,T,Ly;
    bimBobLayApply(W,bimBdeFigBox(W),bimBdeMoveFig(W),false);   /* __acad3dV174b: the stacks laid out again */
    F=bimBrdFigsValid(W.figs);
    if(!F){console.warn('[BIM] A board\'s new figures were not a list; nothing changed');return false;}
    T=bimBobValid(W.objs,F);Ly=bimBobLayValid(W.lay);
    pushUndo();
    W.B.figs=F;W.B.objs=T||[];
    if(Ly)W.B.lay=Ly;else delete W.B.lay;
    /* __acad3dV174c: a board one draws on is a page (the owner, 2026-11-08): the first drawing gives it the smallest
       standard page that holds what is on it, unless No page was chosen */
    var auto=null;
    if(!W.page&&!W.B.pageOff&&W.objs.some(function(n){return n.t!=='fig';})){
      var fb0=bimBdeFigBox(W),mx=0,my=0;
      W.objs.forEach(function(n){var q=bimBobBox(n,fb0);if(q){mx=Math.max(mx,q.x+q.w);my=Math.max(my,q.y+q.h);}});
      auto=bimPgFit(mx,my,/^(ft|in|ftin)$/.test(A3D_UNITS.key));
      W.page={key:auto.key,o:auto.o};
    }
    if(W.page&&bimPgValid(W.page)){W.B.page=bimPgValid(W.page);delete W.B.pageOff;}else delete W.B.page;
    if(W.pageOff&&!W.B.page)W.B.pageOff=true;
    if(W.B.kind!=='custom'){if(W.off&&W.off.length)W.B.off=W.off;else delete W.B.off;}
    if(sel)A3D_BDE.sel=sel.slice();
    saveSoon();
    bimBrdRedraw();
    refreshLayers();refreshProps();
    if(msg)a3dToast(msg);
    if(auto)a3dToast('The board is now a page, '+bimPgLabel(auto.key,auto.o)+(auto.fits?'':', and some of it runs past the page')+': Page changes it');
    return true;
  }
  function bimBdeName(n,W){
    var K=bimBobKind(n.t),F,E,i;
    if(n.nm)return n.nm;
    if(n.t==='fig'){
      for(i=0;i<W.figs.length;i++)if(W.figs[i].k===n.k)F=W.figs[i];
      if(!F)return 'Figure';
      if(F.f==='text')return (F.o&&F.o.t)||'A heading';
      E=bimFigEntry(F.f);return E?E.name:F.f;
    }
    if(n.t==='text')return n.s.replace(/\s+/g,' ').slice(0,40)||'Text';
    return K?K[1]:n.t;
  }
  /* the selected ids that are still there */
  function bimBdeSel(W){return A3D_BDE.sel.filter(function(id){return !!bimBobFind(W.objs,id);});}
  /* a board's objects selected: the model's selection is let go, so the two never stand together */
  function bimBdeSelect(ids){
    A3D_BDE.sel=ids.slice();
    if(ids.length&&(A3D.sel||(A3D.selSet&&A3D.selSet.length))){A3D.sel=null;A3D.sel2=null;A3D.selSet=[];}
    bimBdeSync();
  }
  /* the Properties panel shows the board's selection while a board is designed */
  function bimBdeOwnsProps(){return bimBrdEditing()&&A3D_BDE.sel.length>0&&!!bimBrdRec();}
  /* ---- drawing ---- */
  function bimBdeAddSpot(){
    var b=bimClbEl(),d=b&&b.querySelector('.a3d-clb-dsn'),k=bimBobPxMm(),z,y=20,br,dr;
    if(d){
      z=parseFloat(d.style.getPropertyValue('--z'))||1;
      br=b.getBoundingClientRect();dr=d.getBoundingClientRect();
      y=Math.max(10,(br.top+90-dr.top)/z/k+10);
    }
    return {x:20,y:Math.round(y)};
  }
  function bimBdeDrawKinds(){return [['rect','Rectangle'],['ellipse','Ellipse'],['line','Line'],['arrow','Arrow'],['poly','Polygon'],['star','Star'],['text','Text'],['image','Image…'],
    '-',['map','Map frame'],['legend','Legend'],['north','North arrow'],['sbar','Scale bar'],   /* __acad3dV174d */
    '-',['lvfield','Field\u2026'],['lvnumber','Number\u2026']];}   /* __acad3dV175a: a value of the project, kept up to date */
  function bimBdeDrawMenu(x,y){
    bimLtMenuOpen(x,y,bimBdeDrawKinds().map(function(k){return k==='-'?k:[k[1],k[0]];}),function(k){
      if(k==='image')bimBdeAddImage();
      else if(k==='lvfield'||k==='lvnumber')setTimeout(function(){if(k==='lvfield')bimLvFieldMenu(x,y);else bimLvNumberMenu(x,y);},0);   /* after this menu has closed */
      else bimBdeAdd(k);
    });
    return true;
  }
  /* a new object of a kind ('arrow' is a line with its head) on the current layer, at the top of the board's visible part */
  function bimBdeAdd(kind,extra){
    var W=bimBdeWork(),p=bimBdeAddSpot(),n,id,f,ly=bimLayerById(A3D.activeLayer)||bimLayerZero();
    if(!W){a3dToast('Only a board in the set can be drawn on: Show in Presentation puts it there');return null;}
    if(W.objs.length>=bimBobMax()){a3dToast('A board holds '+bimBobMax()+' objects at most');return null;}
    id=bimBobNewId(W.objs);
    n={id:id,t:kind==='arrow'?'line':kind,x:p.x,y:p.y,layer:ly?ly.id:undefined};
    if(kind==='rect'){n.w=60;n.h=40;}
    else if(kind==='ellipse'||kind==='poly'||kind==='star'){n.w=50;n.h=50;}
    else if(kind==='line'||kind==='arrow'){n.w=60;n.h=0;if(kind==='arrow')n.a1=true;}
    else if(kind==='text'){n.w=80;n.h=10;n.s='Text';}
    else if(kind==='image'){n.w=100;n.h=75;}
    else if(kind==='map'){   /* __acad3dV174d: the first plan, at a scale that shows it whole */
      var srcs=bimBmapSources();
      if(!srcs.length){a3dToast('There is no plan or view to show: add a level first');return null;}
      n.w=160;n.h=110;n.src=srcs[0].kind+':'+srcs[0].refId;var fit=bimBmapFit(n);n.den=fit.den;n.px=fit.px;n.py=fit.py;
    }else if(kind==='legend'||kind==='north'||kind==='sbar'){
      var fr=null;
      A3D_BDE.sel.forEach(function(x){var q=bimBobFind(W.objs,x);if(q&&q.n.t==='map')fr=q.n;});
      if(!fr)W.objs.forEach(function(q){if(!fr&&q.t==='map')fr=q;});
      if(!fr){a3dToast('Draw a map frame first: the '+(kind==='legend'?'legend':kind==='north'?'north arrow':'scale bar')+' is bound to one');return null;}
      n.fr=fr.id;
      if(kind==='legend'){n.w=60;n.h=40;n.x=fr.x+fr.w+5;n.y=fr.y;}
      else if(kind==='north'){n.w=14;n.h=18;n.x=fr.x+fr.w-18;n.y=fr.y+4;}
      else{n.w=Math.max(40,fr.w*0.45);n.h=11;n.x=fr.x;n.y=fr.y+fr.h+3;n.un=/^(ft|in|ftin)$/.test(A3D_UNITS.key)?'ft':'m';}
    }
    else return null;
    if(extra)for(f in extra)if(extra.hasOwnProperty(f))n[f]=extra[f];
    W.objs.push(n);
    if(!bimBdeCommit(W,(bimBobKind(n.t)||['',kind])[1]+' drawn on layer '+(bimBobLayer(n)?bimBobLayer(n).name:'')+': drag it into place',[id]))return null;
    return id;
  }
  /* an image picked from the device: a new one, or (swap) the image of an image object */
  function bimBdeAddImage(swap){
    var inp=A3D_BDE.file;
    if(!inp){
      inp=A3D_BDE.file=document.createElement('input');
      inp.type='file';inp.accept='image/png,image/jpeg,image/gif,image/webp';inp.style.display='none';
      inp.addEventListener('change',function(){
        var f=inp.files&&inp.files[0],sw=inp.__swap;
        inp.value='';inp.__swap=null;
        if(!f)return;
        bimBimgAdd(f,function(h,w,hh){
          if(sw){bimBdeSet(sw,{src:h});return;}
          bimBdeAdd('image',{src:h,h:Math.max(1,Math.round(100*hh/w)),nm:f.name.replace(/\.[^.]+$/,'').slice(0,80)});
        });
      });
      document.body.appendChild(inp);
    }
    inp.__swap=swap||null;
    inp.click();
    return true;
  }
  /* ---- changing the selection ---- */
  /* fields onto objects (ids, or the selection); a null field goes back to its default (ByLayer for tr and bm) */
  function bimBdeSet(ids,o){
    var W=bimBdeWork(),S,k,done=0;
    if(!W)return false;
    S=typeof ids==='string'?[ids]:(ids||bimBdeSel(W));
    S.forEach(function(id){
      var f=bimBobFind(W.objs,id);if(!f)return;
      for(k in o)if(o.hasOwnProperty(k)){
        if(f.n.t==='fig'&&k!=='layer'&&k!=='tr'&&k!=='bm'&&k!=='nm'&&k!=='la')continue;   /* a figure keeps its place in its columns */
        if(o[k]===null)delete f.n[k];else f.n[k]=o[k];
      }
      done++;
    });
    if(!done)return false;
    if((o.tr!==undefined||o.bm!==undefined)&&!bimBdsPres()&&!A3D_BDE.hinted){A3D_BDE.hinted=true;a3dToast('Transparency and blend modes show in the Presentation appearance (Pres in the status bar) and in Present');}
    return bimBdeCommit(W,null,S);
  }
  /* one action on the selection: forward, backward, front, back, dup, del */
  function bimBdeDo(a,ids){
    var W=bimBdeWork(),S,sel=null,changed=false;
    if(!W)return false;
    S=(ids||bimBdeSel(W)).filter(function(x){return !!bimBobFind(W.objs,x);});
    if(!S.length)return false;
    if(a==='forward'||a==='front'){S.slice().reverse().forEach(function(x){if(bimBobReorder(W.objs,x,a))changed=true;});}
    else if(a==='backward'||a==='back'){S.forEach(function(x){if(bimBobReorder(W.objs,x,a))changed=true;});}
    else if(a==='dup'){
      sel=[];
      S.forEach(function(x){
        var f=bimBobFind(W.objs,x),c;
        if(!f||f.n.t==='fig')return;
        c=JSON.parse(JSON.stringify(f.n));c.id=bimBobNewId(W.objs);bimBobShift(c,5,5,null);
        W.objs.splice(f.i+1,0,c);sel.push(c.id);changed=true;
      });
      if(!changed){a3dToast('A figure is on a board once: Duplicate in its menu puts a copy below the others');return false;}
    }else if(a==='del'){
      S.forEach(function(x){
        var f=bimBobFind(W.objs,x);if(!f)return;
        if(f.n.t==='fig')bimBdeDropFig(W,f.n.k);
        W.objs.splice(f.i,1);changed=true;
      });
      sel=[];
    }
    if(!changed)return false;
    return bimBdeCommit(W,a==='del'?'Deleted: Ctrl+Z brings it back':a==='dup'?'Duplicated':null,sel||S);
  }
  /* a figure off the board, as its menu's Remove does it (the three boards keep the figures taken off) */
  function bimBdeDropFig(W,k){
    var F=null,E;
    W.figs=W.figs.filter(function(x){if(x.k===k){F=x;return false;}return true;});
    if(!F||W.B.kind==='custom')return;
    E=bimFigEntry(F.f);
    if(E&&E.kind===W.B.kind&&!E.kpis&&!W.figs.some(function(x){return x.f===F.f;})){W.off=W.off||[];if(W.off.indexOf(F.f)<0)W.off.push(F.f);}
  }
  function bimBdeEsc(){
    if(!bimBrdEditing()||!A3D_BDE.sel.length)return false;
    bimBdeSelect([]);
    return true;
  }
  /* ---- the board's pointer ---- */
  function bimBdeDsn(){var b=bimClbEl();return b&&b.querySelector('.a3d-clb-dsn');}
  function bimBdeZoom(d){return parseFloat(d.style.getPropertyValue('--z'))||1;}
  function bimBdeDom(d,id){return [].slice.call(d.querySelectorAll('[data-bde="'+id+'"],[data-bdmask="'+id+'"]'));}
  function bimBdePickable(W,id){
    var f=bimBobFind(W.objs,id),ly=f&&bimBobLayer(f.n),s=ly?bimLayerEff(ly):null;
    return !!f&&(!s||(s.on&&!s.frozen&&!s.locked));
  }
  function bimBdeDown(ev){
    if(!bimBrdEditing()||(ev.button!==undefined&&ev.button>0))return;
    var t=ev.target,d=t&&t.closest?t.closest('.a3d-clb-dsn'):null,W,e,id,S,f,b;
    if(!d||t.closest('[data-brdmenu],[data-brdrsz]'))return;
    W=bimBdeWork();if(!W)return;
    try{d.focus({preventScroll:true});}catch(eF){}
    if(t.closest('[data-bdh]')){
      S=bimBdeSel(W);if(S.length!==1)return;
      f=bimBobFind(W.objs,S[0]);
      if(f.n.t==='fig'||!bimBdePickable(W,S[0]))return;
      bimBdeDragStart(ev,d,W,'size',[S[0]],{x:f.n.x,y:f.n.y,w:f.n.w,h:f.n.h});
      return;
    }
    e=t.closest('[data-bde]');
    if(!e){if(!ev.shiftKey&&A3D_BDE.sel.length)bimBdeSelect([]);return;}
    id=e.getAttribute('data-bde');
    if(!bimBdePickable(W,id))return;
    if(ev.shiftKey||ev.ctrlKey||ev.metaKey){
      bimBdeSelect(A3D_BDE.sel.indexOf(id)>=0?A3D_BDE.sel.filter(function(x){return x!==id;}):A3D_BDE.sel.concat([id]));
      ev.preventDefault();return;
    }
    if(A3D_BDE.sel.indexOf(id)<0)bimBdeSelect([id]);
    if(ev.pointerType==='touch'&&!t.closest('[data-brdgrip]'))return;   /* a finger scrolls the board; Properties places it */
    S=bimBdeSel(W).filter(function(x){return bimBdePickable(W,x);});
    if(!S.length)return;
    b=null;S.forEach(function(x){var q=bimBobBox(bimBobFind(W.objs,x).n,bimBdeFigBox(W));if(q)b=b?bimBobUnion(b,q):q;});
    bimBdeDragStart(ev,d,W,'move',S,b);
  }
  function bimBdeDragStart(ev,d,W,mode,ids,box){
    var b=bimClbEl(),dom=[];
    ids.forEach(function(x){dom=dom.concat(bimBdeDom(d,x));});
    A3D_BDE.drag={mode:mode,ids:ids,W:W,x0:ev.clientX,y0:ev.clientY,s0:b?b.scrollTop:0,z:bimBdeZoom(d),d:d,dom:dom,box:box,pid:ev.pointerId,moved:false,dx:0,dy:0,
      G:mode==='move'?bimBdeSnapIndex(W,ids):null};   /* __acad3dV174b: the others' edges and gaps, found once */
    try{d.setPointerCapture(ev.pointerId);}catch(eP){}
    ev.preventDefault();
  }
  function bimBdeMoveEv(ev){
    var D=A3D_BDE.drag,b,k=bimBobPxMm(),dx,dy,px,py,f,w,h,s;
    if(!D||ev.pointerId!==D.pid)return;
    if(!D.moved&&Math.abs(ev.clientX-D.x0)<3&&Math.abs(ev.clientY-D.y0)<3)return;
    b=bimClbEl();
    dx=(ev.clientX-D.x0)/D.z/k;dy=(ev.clientY-D.y0+((b?b.scrollTop:0)-D.s0))/D.z/k;
    if(A3D_SNAP.ortho){if(Math.abs(dx)>=Math.abs(dy))dy=0;else dx=0;}
    D.guides=[];
    if(D.mode==='move'&&A3D_SNAP.point&&D.G&&D.box){   /* __acad3dV174b: smart spacing, within the drawing's 12 px (D10) */
      var cand={x:D.box.x+dx,y:D.box.y+dy,w:D.box.w,h:D.box.h},sn=bimBalSnap(cand,D.G,A3D_SNAP.pxThreshold/(D.z*k)),gx=null,gy=null;
      if(sn.x&&(dx!==0||!A3D_SNAP.ortho)){dx+=sn.x.d;gx=sn.x;}
      if(sn.y&&(dy!==0||!A3D_SNAP.ortho)){dy+=sn.y.d;gy=sn.y;}
      if(gx)D.guides.push(['x',gx.kind==='point'?gx.at:(gx.kind==='before'?D.box.x+dx+D.box.w:(gx.kind==='centre'?D.box.x+dx+D.box.w/2:D.box.x+dx)),gx.kind]);
      if(gy)D.guides.push(['y',gy.kind==='point'?gy.at:(gy.kind==='before'?D.box.y+dy+D.box.h:(gy.kind==='centre'?D.box.y+dy+D.box.h/2:D.box.y+dy)),gy.kind]);
      if(A3D_SNAP.grid){if(!gx)dx=Math.round(dx);if(!gy)dy=Math.round(dy);}
    }else if(A3D_SNAP.grid){dx=Math.round(dx);dy=Math.round(dy);}   /* whole millimetres */
    D.moved=true;D.dx=dx;D.dy=dy;
    px=bimBrdPx(dx*k);py=bimBrdPx(dy*k);
    if(D.mode==='move')D.dom.forEach(function(el){el.style.transform='translate('+px+'px,'+py+'px)';});
    else{
      f=bimBobFind(D.W.objs,D.ids[0]).n;
      w=f.t==='line'?D.box.w+dx:Math.max(0.5,D.box.w+dx);h=f.t==='line'?D.box.h+dy:Math.max(0.5,D.box.h+dy);
      if(ev.shiftKey&&f.t!=='line'&&D.box.w>0&&D.box.h>0){s=Math.max(w/D.box.w,h/D.box.h);w=D.box.w*s;h=D.box.h*s;}
      D.w=Math.round(w*10)/10;D.h=Math.round(h*10)/10;
      D.dom.forEach(function(el){if(f.t!=='line'){el.style.width=bimBdsPx(D.w)+'px';if(f.t!=='text'||f.fit==='fixed')el.style.height=bimBdsPx(D.h)+'px';}});
    }
    bimBdeOverlay(D.d,D.W,D.mode==='move'?{dx:dx,dy:dy}:{w:D.w,h:D.h});
    ev.preventDefault();
  }
  function bimBdeUp(ev){
    var D=A3D_BDE.drag,f;
    if(!D||ev.pointerId!==D.pid)return;
    A3D_BDE.drag=null;
    try{D.d.releasePointerCapture(D.pid);}catch(eR){}
    if(!D.moved||(D.mode==='move'&&!D.dx&&!D.dy)){D.dom.forEach(function(el){el.style.transform='';});return;}
    if(D.mode==='move'){
      D.ids.forEach(function(x){f=bimBobFind(D.W.objs,x);if(f)bimBobShift(f.n,D.dx,D.dy,bimBdeMoveFig(D.W));});
      /* __acad3dV174b: an object dropped in its layer's stack takes the place it was dropped at */
      D.ids.forEach(function(x){var q=bimBobFind(D.W.objs,x),ly=q&&bimBobLayer(q.n);if(ly&&D.W.lay[ly.id]&&!q.n.la)bimBobLayReorder(D.W,ly.id,bimBdeFigBox(D.W));});
    }
    else{
      f=bimBobFind(D.W.objs,D.ids[0]);if(!f)return;
      f.n.w=D.w;f.n.h=D.h;
      if(f.n.t==='text'&&f.n.fit==='auto-w')f.n.fit='auto-h';
    }
    bimBdeCommit(D.W,null,D.ids);
  }
  function bimBdeCancel(ev){
    var D=A3D_BDE.drag;
    if(!D||(ev&&ev.pointerId!==D.pid))return;
    A3D_BDE.drag=null;
    bimClbOpen();
  }
  /* ---- the keys on the board ---- */
  /* the app's key handler asks this first: Ctrl+D, Ctrl+[ and Ctrl+] belong to the board while one draws on it */
  function bimBdeWantsKey(ev){
    var a=document.activeElement;
    if(!bimBrdEditing()||!a||!a.closest||!a.closest('.a3d-clb-dsn'))return false;
    return (ev.ctrlKey||ev.metaKey)&&/^(d|D|\[|\]|\{|\})$/.test(ev.key);
  }
  function bimBdeKey(ev){
    var t=ev.target,k=ev.key,c=ev.ctrlKey||ev.metaKey,W,S,m;
    if(!bimBrdEditing()||!t||!t.closest||!t.closest('.a3d-clb-dsn'))return;
    if(/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))return;
    if(!A3D_BDE.sel.length)return;
    if(c&&(k==='d'||k==='D'))bimBdeDo('dup');
    else if(c&&(k===']'||k==='}'))bimBdeDo(ev.shiftKey?'front':'forward');
    else if(c&&(k==='['||k==='{'))bimBdeDo(ev.shiftKey?'back':'backward');
    else if(k==='Delete'||k==='Backspace')bimBdeDo('del');
    else if(/^Arrow/.test(k)&&!c){
      W=bimBdeWork();if(!W)return;
      S=bimBdeSel(W).filter(function(x){return bimBdePickable(W,x);});
      if(!S.length)return;
      m=ev.shiftKey?10:1;
      S.forEach(function(x){bimBobShift(bimBobFind(W.objs,x).n,k==='ArrowLeft'?-m:k==='ArrowRight'?m:0,k==='ArrowUp'?-m:k==='ArrowDown'?m:0,bimBdeMoveFig(W));});
      bimBdeCommit(W,null,S);
    }else return;
    ev.preventDefault();ev.stopPropagation();
  }
  function bimBdeWire(b){
    b.addEventListener('pointerdown',bimBdeDown);
    b.addEventListener('pointermove',bimBdeMoveEv);
    b.addEventListener('pointerup',bimBdeUp);
    b.addEventListener('pointercancel',bimBdeCancel);
    b.addEventListener('keydown',bimBdeKey);
  }
  /* the other shown objects' boxes and the page's edges and centre, for the snaps */
  function bimBdeSnapIndex(W,ids){
    var fb=bimBdeFigBox(W),R=[],pg=bimBdePage(W),G;
    W.objs.forEach(function(n){if(ids.indexOf(n.id)>=0||!bimBdePickableOrLocked(n))return;var b=bimBobBox(n,fb);if(b&&b.w>=0&&b.h>=0)R.push(b);});
    G=bimBalGaps(R);
    G.xs.push(pg.x,pg.x+pg.w/2,pg.x+pg.w);G.ys.push(pg.y);if(pg.h)G.ys.push(pg.y+pg.h/2,pg.y+pg.h);
    return G;
  }
  function bimBdePickableOrLocked(n){var ly=bimBobLayer(n),s=ly?bimLayerEff(ly):null;return !s||(s.on&&!s.frozen);}
  /* ---- after the board is drawn: the selection's outlines ---- */
  function bimBdeOverlay(d,W,live){
    var o=d&&d.querySelector('.a3d-clb-dsel'),S,h='',fb;
    if(!o)return;
    if(A3D_CLB.narrow&&W.lay){   /* a phone shows a stack's row as a column: the outlines follow what is shown */
      W={B:W.B,objs:JSON.parse(JSON.stringify(W.objs)),figs:JSON.parse(JSON.stringify(W.figs)),lay:W.lay};
      bimBobLayApply(W,bimBdeFigBox(W),bimBobFigMover(W.figs),true);
    }
    S=bimBdeSel(W);fb=bimBdeFigBox(W);
    S.forEach(function(x){
      var f=bimBobFind(W.objs,x),b=bimBobBox(f.n,fb),hd;
      if(!b)return;
      b={x:b.x,y:b.y,w:b.w,h:b.h};
      if(live&&live.dx!==undefined){b.x+=live.dx;b.y+=live.dy;}
      if(live&&live.w!==undefined&&f.n.t!=='line'){b.w=Math.max(0.5,live.w);b.h=Math.max(0.5,live.h);}
      hd=S.length===1&&f.n.t!=='fig'&&bimBdePickable(W,x);
      h+='<div class="a3d-clb-dbox'+(f.n.mask?' mk':'')+'" style="'+bimBdsPos(b,0,0)+'">'+
        (hd?'<div class="a3d-clb-dhdl" data-bdh="se" title="Drag to size; Shift keeps its proportions" style="'+(f.n.t==='line'?'left:'+bimBdsPx(f.n.x+f.n.w-b.x)+'px;top:'+bimBdsPx(f.n.y+f.n.h-b.y)+'px':'right:0;bottom:0')+'"></div>':'')+'</div>';
    });
    /* __acad3dV174b: the stacks of the selection's layers, and the snaps caught */
    var seen={},bx=bimBobLayApply({objs:JSON.parse(JSON.stringify(W.objs)),figs:W.figs,lay:W.lay},fb,null,!!A3D_CLB.narrow);
    S.forEach(function(x){var ly=bimBobLayer(bimBobFind(W.objs,x).n);if(ly&&bx[ly.id]&&!seen[ly.id]){seen[ly.id]=1;h='<div class="a3d-clb-dstack" style="'+bimBdsPos(bx[ly.id],0,0)+'"></div>'+h;}});
    if(A3D_BDE.drag&&A3D_BDE.drag.guides)A3D_BDE.drag.guides.forEach(function(g){
      h+='<div class="a3d-clb-guide '+g[0]+(g[2]==='point'?'':' gap')+'" style="'+(g[0]==='x'?'left:'+bimBdsPx(g[1]):'top:'+bimBdsPx(g[1]))+'px"></div>';
    });
    o.innerHTML=h;
  }
  /* the board was drawn: the selection kept to what is still there and outlined */
  function bimBdeAfterDraw(b){
    var W,d,n,ed=bimBrdEditing(),turned=ed!==A3D_BDE.was;
    A3D_BDE.was=ed;
    if(!ed){if(A3D_BDE.sel.length||turned){A3D_BDE.sel=[];refreshProps();refreshLayers();}return;}   /* the board's rows leave the Layers tab */
    W=bimBdeWork();if(!W)return;
    n=A3D_BDE.sel.length;
    A3D_BDE.sel=bimBdeSel(W);
    d=b&&b.querySelector('.a3d-clb-dsn');
    if(d){d.setAttribute('tabindex','0');d.setAttribute('aria-label','The board: click an object to select it; its properties are in the Properties panel and its row under its layer in Layers');bimBdeOverlay(d,W,null);}
    if(n!==A3D_BDE.sel.length||turned){refreshProps();refreshLayers();}   /* Edit on: the board's objects under their layers */
  }
  function bimBdeSync(){
    var W=bimBdeWork();
    if(W){A3D_BDE.sel=bimBdeSel(W);bimBdeOverlay(bimBdeDsn(),W,null);}
    refreshProps();refreshLayers();
  }
export {
  A3D_BDE, bimBdeAdd, bimBdeAddImage, bimBdeAfterDraw, bimBdeCommit, bimBdeDo, bimBdeDrawMenu, bimBdeEsc,
  bimBdeFigBox, bimBdeMoveFig, bimBdeName, bimBdeOwnsProps, bimBdePickable, bimBdeSel, bimBdeSelect,
  bimBdeSet, bimBdeWantsKey, bimBdeWire, bimBdeWork
};
