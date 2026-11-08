import { A3D_SNAP, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimClbEl, bimClbOpen } from '../site-analysis/climate-board.js';
import { saveSoon } from '../bim/region-regenerate.js';
import {
  BIM_BRD_P0, bimBrdBands, bimBrdEditing, bimBrdFigsValid, bimBrdPx, bimBrdRec, bimFigEntry
} from './board-figures.js';
import { bimBrdRedraw, bimBrdWorking } from './board-edit.js';
import {
  bimBtrBox, bimBtrCopy, bimBtrCount, bimBtrEff, bimBtrFind, bimBtrGroup, bimBtrIsBox, bimBtrKind, bimBtrMax,
  bimBtrMoveTo, bimBtrNewId, bimBtrOut, bimBtrPick, bimBtrPxMm, bimBtrRemove, bimBtrReorder, bimBtrShift,
  bimBtrSync, bimBtrUngroup, bimBtrUnion, bimBtrValid, bimBtrWalk
} from './board-tree.js';
import { bimBimgAdd } from './board-images.js';
import { bimBdsFigBoxer, bimBdsPos, bimBdsPx } from './board-design.js';
import { bimBdePanel, bimBdePanelClose } from './board-design-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV174a: designing a board, in Edit =================
     docs/research/research-presentation-boards.md, 4.1. A click selects the outermost unlocked, visible element
     within the group one has gone into (the board at first); Ctrl-click (Cmd on a Mac) selects deep; Shift adds.
     Enter goes into a group, Shift+Enter out. Locked and hidden elements are not picked on the board but are in the
     layer list. The arrows nudge 1 mm, 10 with Shift. Ctrl+G groups, Ctrl+Shift+G ungroups, Ctrl+] and Ctrl+[ bring
     forward and send backward, with Shift to the front and the back (Figma's keys, and QGIS's). On a touch screen the
     list's own buttons do what the keys do. Every change is one undo step, kept with the project. */
  var A3D_BDE={sel:[],scope:null,drag:null,pnl:null,fold:{},file:null};
  /* the board's tree and figures to change: copies, the tree made from the figures when there is none yet */
  function bimBdeWork(){
    var B=bimBrdRec(),figs,els,order=[];
    if(!B)return null;
    figs=bimBrdWorking(B);
    if(B.els)els=JSON.parse(JSON.stringify(B.els));
    else{els=[];bimBrdBands(figs).forEach(function(D){D.f.forEach(function(F){order.push(F);});});}
    bimBtrSync(els,order.length?order:figs);
    return {B:B,figs:figs,els:els,off:B.off?B.off.slice():null};
  }
  function bimBdeFigBox(W){return bimBdsFigBoxer(W.figs);}
  function bimBdeMoveFig(W){
    return function(k,dx,dy){
      var i,F,s=bimBtrPxMm()/BIM_BRD_P0;
      for(i=0;i<W.figs.length;i++)if(W.figs[i].k===k){
        F=W.figs[i];
        F.x=Math.max(0,Math.min(12-F.w,Math.round((F.x+dx*s)*10000)/10000));
        F.y=Math.max(0,Math.round((F.y+dy*s)*10000)/10000);
      }
    };
  }
  /* one undo step: the board's figures and tree as W has them */
  function bimBdeCommit(W,msg,sel){
    var F=bimBrdFigsValid(W.figs),T;
    if(!F){console.warn('[BIM] A board\'s new figures were not a list; nothing changed');return false;}
    T=bimBtrValid(W.els,F);
    pushUndo();
    W.B.figs=F;W.B.els=T||[];
    if(W.B.kind!=='custom'){if(W.off&&W.off.length)W.B.off=W.off;else delete W.B.off;}
    if(sel)A3D_BDE.sel=sel.slice();
    saveSoon();
    bimBrdRedraw();
    if(msg)a3dToast(msg);
    return true;
  }
  function bimBdeName(n,W){
    var K=bimBtrKind(n.t),F,E,i;
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
  /* the selected ids that are still there, with none under another selected one */
  function bimBdeSel(W){
    var S=A3D_BDE.sel.filter(function(id){return !!bimBtrFind(W.els,id);});
    return S.filter(function(id){var f=bimBtrFind(W.els,id);return !f.path.some(function(a){return S.indexOf(a.id)>=0;});});
  }
  /* ---- adding ---- */
  function bimBdeAddSpot(){
    var b=bimClbEl(),d=b&&b.querySelector('.a3d-clb-dsn'),k=bimBtrPxMm(),z,y=20,br,dr;
    if(d){
      z=parseFloat(d.style.getPropertyValue('--z'))||1;
      br=b.getBoundingClientRect();dr=d.getBoundingClientRect();
      y=Math.max(10,(br.top+90-dr.top)/z/k+10);
    }
    return {x:20,y:Math.round(y)};
  }
  /* a new element of a kind ('arrow' is a line with its head), at the top of the board's visible part, or of the
     group one is in */
  function bimBdeAdd(kind,extra){
    var W=bimBdeWork(),p=bimBdeAddSpot(),n,id,par=null,f;
    if(!W){a3dToast('Only a board in the set can be designed: Show in Presentation puts it there');return null;}
    if(bimBtrCount(W.els)>=bimBtrMax().nodes){a3dToast('A board holds '+bimBtrMax().nodes+' elements at most');return null;}
    id=bimBtrNewId(W.els);
    n={id:id,t:kind==='arrow'?'line':kind,x:p.x,y:p.y,op:1};
    if(kind==='rect'){n.w=60;n.h=40;}
    else if(kind==='ellipse'||kind==='poly'||kind==='star'){n.w=50;n.h=50;}
    else if(kind==='line'||kind==='arrow'){n.w=60;n.h=0;if(kind==='arrow')n.a1=true;}
    else if(kind==='text'){n.w=80;n.h=10;n.s='Text';}
    else if(kind==='frame'){n.w=120;n.h=80;n.fill='#ffffff';n.bm='pass';}
    else if(kind==='image'){n.w=100;n.h=75;}
    else return null;
    if(extra)for(f in extra)if(extra.hasOwnProperty(f))n[f]=extra[f];
    if(A3D_BDE.scope){f=bimBtrFind(W.els,A3D_BDE.scope);if(f&&bimBtrIsBox(f.n))par=f.n;}
    (par?par.ch:W.els).push(n);
    if(!bimBdeCommit(W,(bimBtrKind(n.t)||['',kind])[1]+' added: drag it into place',[id]))return null;
    return id;
  }
  function bimBdeAddImage(){
    var inp=A3D_BDE.file;
    if(!inp){
      inp=A3D_BDE.file=document.createElement('input');
      inp.type='file';inp.accept='image/png,image/jpeg,image/gif,image/webp';inp.style.display='none';
      inp.addEventListener('change',function(){
        var f=inp.files&&inp.files[0],swap=inp.__swap;
        inp.value='';inp.__swap=null;
        if(!f)return;
        bimBimgAdd(f,function(h,w,hh){
          if(swap){bimBdeSet(swap,{src:h});return;}
          var W0=100,H0=Math.max(1,Math.round(W0*hh/w));
          bimBdeAdd('image',{src:h,h:H0,nm:f.name.replace(/\.[^.]+$/,'').slice(0,80)});
        });
      });
      document.body.appendChild(inp);
    }
    inp.__swap=arguments[0]||null;
    inp.click();
    return true;
  }
  /* ---- changing what is selected ---- */
  /* fields onto one element; numbers in mm and fractions as given */
  function bimBdeSet(id,o){
    var W=bimBdeWork(),f=W&&bimBtrFind(W.els,id),k;
    if(!f)return false;
    for(k in o)if(o.hasOwnProperty(k)){if(o[k]===null)delete f.n[k];else f.n[k]=o[k];}
    return bimBdeCommit(W,null,[id]);
  }
  /* one action on the selection: forward, backward, front, back, group, frame, ungroup, out, dup, del, lock, hide */
  function bimBdeDo(a,ids){
    var W=bimBdeWork(),S,msg=null,sel=null,id,changed=false,f,lost=false;
    if(!W)return false;
    S=bimBdeSel({els:W.els}).filter(function(x){return !ids||ids.indexOf(x)>=0;});
    if(ids)S=ids.filter(function(x){return !!bimBtrFind(W.els,x);});
    if(!S.length)return false;
    if(a==='forward'||a==='front'){S.slice().reverse().forEach(function(x){if(bimBtrReorder(W.els,x,a))changed=true;});sel=S;}
    else if(a==='backward'||a==='back'){S.forEach(function(x){if(bimBtrReorder(W.els,x,a))changed=true;});sel=S;}
    else if(a==='group'||a==='frame'){
      id=bimBtrGroup(W.els,S,a==='frame',bimBdeFigBox(W));
      if(!id){a3dToast('Only elements side by side in one list can be grouped');return false;}
      changed=true;sel=[id];msg=a==='frame'?'Framed':'Grouped';
    }else if(a==='ungroup'){
      S.forEach(function(x){
        f=bimBtrFind(W.els,x);
        if(f&&bimBtrIsBox(f.n)){if(f.n.bm!=='pass')lost=true;sel=(sel||[]).concat(f.n.ch.map(function(c){return c.id;}));if(bimBtrUngroup(W.els,x))changed=true;}
      });
      if(lost)msg='Ungrouped: the group\'s blend mode is let go, its opacity is in its elements';
    }else if(a==='out'){S.forEach(function(x){if(bimBtrOut(W.els,x))changed=true;});sel=S;A3D_BDE.scope=null;}
    else if(a==='lock'||a==='hide'){
      var on=!S.every(function(x){return bimBtrFind(W.els,x).n[a];});
      S.forEach(function(x){f=bimBtrFind(W.els,x);if(on)f.n[a]=true;else delete f.n[a];});
      changed=true;sel=a==='hide'&&on?[]:S;
    }else if(a==='dup'){
      sel=[];
      S.forEach(function(x){
        f=bimBtrFind(W.els,x);
        var c=bimBtrCopy(W.els,f.n);
        if(!c)return;
        bimBtrShift(c,5,5,null);
        f.list.splice(f.i+1,0,c);sel.push(c.id);changed=true;
      });
      if(!changed){a3dToast('A figure is on a board once: Duplicate in its menu puts a copy below the others');return false;}
      msg='Duplicated';
    }else if(a==='del'){
      S.forEach(function(x){
        f=bimBtrFind(W.els,x);if(!f)return;
        bimBtrWalk([f.n],function(n){if(n.t==='fig')bimBdeDropFig(W,n.k);});
        bimBtrRemove(W.els,x);changed=true;
      });
      sel=[];msg='Deleted: Ctrl+Z brings it back';
    }
    if(!changed)return false;
    return bimBdeCommit(W,msg,sel||S);
  }
  /* a figure off the board, as its menu's Remove does it (the three boards keep the figures taken off) */
  function bimBdeDropFig(W,k){
    var F=null,E;
    W.figs=W.figs.filter(function(x){if(x.k===k){F=x;return false;}return true;});
    if(!F||W.B.kind==='custom')return;
    E=bimFigEntry(F.f);
    if(E&&E.kind===W.B.kind&&!E.kpis&&!W.figs.some(function(x){return x.f===F.f;})){W.off=W.off||[];if(W.off.indexOf(F.f)<0)W.off.push(F.f);}
  }
  /* into a group or a frame, at its top */
  function bimBdeInto(pid){
    var W=bimBdeWork(),S,ok=false;
    if(!W)return false;
    S=bimBdeSel(W);
    S.forEach(function(x){if(bimBtrMoveTo(W.els,x,pid))ok=true;});
    if(!ok){a3dToast('An element cannot go into itself');return false;}
    return bimBdeCommit(W,null,S);
  }
  /* Enter: into the group selected, its top element selected; Shift+Enter: out, the group selected */
  function bimBdeEnter(up){
    var W=bimBdeWork(),S,f,c;
    if(!W)return false;
    S=bimBdeSel(W);if(S.length!==1)return false;
    f=bimBtrFind(W.els,S[0]);
    if(up){if(!f.par)return false;A3D_BDE.scope=f.path.length>1?f.path[f.path.length-2].id:null;A3D_BDE.sel=[f.par.id];}
    else{if(!bimBtrIsBox(f.n)||!f.n.ch.length)return false;A3D_BDE.scope=f.n.id;c=f.n.ch[f.n.ch.length-1];A3D_BDE.sel=[c.id];}
    bimBdeSync();
    return true;
  }
  function bimBdeEsc(){
    if(!bimBrdEditing()||(!A3D_BDE.sel.length&&!A3D_BDE.scope))return false;
    if(A3D_BDE.sel.length)A3D_BDE.sel=[];else A3D_BDE.scope=null;
    bimBdeSync();
    return true;
  }
  /* ---- the board's pointer ---- */
  function bimBdeDsn(){var b=bimClbEl();return b&&b.querySelector('.a3d-clb-dsn');}
  function bimBdeZoom(d){return parseFloat(d.style.getPropertyValue('--z'))||1;}
  /* the elements on the page that draw an element (a group drawn straight has none of its own: its children's) */
  function bimBdeDom(d,W,id){
    var q=d.querySelectorAll('[data-bde="'+id+'"],[data-bdmask="'+id+'"]'),f,out=[];
    if(q.length)return [].slice.call(q);
    f=bimBtrFind(W.els,id);
    if(f&&f.n.ch)f.n.ch.forEach(function(c){out=out.concat(bimBdeDom(d,W,c.id));});
    return out;
  }
  function bimBdeDown(ev){
    if(!bimBrdEditing()||(ev.button!==undefined&&ev.button>0))return;
    var t=ev.target,d=t&&t.closest?t.closest('.a3d-clb-dsn'):null,W,e,id,hd,S,f,b;
    if(!d||t.closest('[data-brdmenu],[data-brdrsz]'))return;
    W=bimBdeWork();if(!W)return;
    try{d.focus({preventScroll:true});}catch(eF){}
    hd=t.closest('[data-bdh]');
    if(hd){
      S=bimBdeSel(W);if(S.length!==1)return;
      f=bimBtrFind(W.els,S[0]);
      bimBdeDragStart(ev,d,W,'size',[S[0]],{x:f.n.x,y:f.n.y,w:f.n.w,h:f.n.h});
      return;
    }
    e=t.closest('[data-bde]');
    if(!e){if(!ev.shiftKey&&(A3D_BDE.sel.length||A3D_BDE.scope)){A3D_BDE.sel=[];A3D_BDE.scope=null;bimBdeSync();}return;}
    id=bimBtrPick(W.els,e.getAttribute('data-bde'),A3D_BDE.scope,ev.ctrlKey||ev.metaKey);
    if(!id)return;
    if(ev.shiftKey){
      A3D_BDE.sel=A3D_BDE.sel.indexOf(id)>=0?A3D_BDE.sel.filter(function(x){return x!==id;}):A3D_BDE.sel.concat([id]);
      bimBdeSync();ev.preventDefault();return;
    }
    if(A3D_BDE.sel.indexOf(id)<0){A3D_BDE.sel=[id];bimBdeSync();}
    if(ev.pointerType==='touch'&&!t.closest('[data-brdgrip]'))return;   /* a finger scrolls the board; the fields place it */
    S=bimBdeSel(W).filter(function(x){return !bimBtrEff(W.els,x).lock;});
    if(!S.length)return;
    b=null;S.forEach(function(x){var q=bimBtrBox(bimBtrFind(W.els,x).n,bimBdeFigBox(W));if(q)b=b?bimBtrUnion(b,q):q;});
    bimBdeDragStart(ev,d,W,'move',S,b);
  }
  function bimBdeDragStart(ev,d,W,mode,ids,box){
    var b=bimClbEl(),dom=[];
    ids.forEach(function(x){dom=dom.concat(bimBdeDom(d,W,x));});
    A3D_BDE.drag={mode:mode,ids:ids,W:W,x0:ev.clientX,y0:ev.clientY,s0:b?b.scrollTop:0,z:bimBdeZoom(d),d:d,dom:dom,box:box,pid:ev.pointerId,moved:false,dx:0,dy:0};
    try{d.setPointerCapture(ev.pointerId);}catch(eP){}
    ev.preventDefault();
  }
  function bimBdeMoveEv(ev){
    var D=A3D_BDE.drag,b,k=bimBtrPxMm(),dx,dy,px,py,f;
    if(!D||ev.pointerId!==D.pid)return;
    if(!D.moved&&Math.abs(ev.clientX-D.x0)<3&&Math.abs(ev.clientY-D.y0)<3)return;
    b=bimClbEl();
    dx=(ev.clientX-D.x0)/D.z/k;dy=(ev.clientY-D.y0+((b?b.scrollTop:0)-D.s0))/D.z/k;
    if(A3D_SNAP.ortho){if(Math.abs(dx)>=Math.abs(dy))dy=0;else dx=0;}
    if(A3D_SNAP.grid){dx=Math.round(dx);dy=Math.round(dy);}   /* whole millimetres; V174b brings the board's snaps */
    D.moved=true;D.dx=dx;D.dy=dy;
    px=bimBrdPx(dx*k);py=bimBrdPx(dy*k);
    if(D.mode==='move')D.dom.forEach(function(el){el.style.transform='translate('+px+'px,'+py+'px)';});
    else{
      f=bimBtrFind(D.W.els,D.ids[0]).n;
      var w=f.t==='line'?D.box.w+dx:Math.max(0.5,D.box.w+dx),h=f.t==='line'?D.box.h+dy:Math.max(0.5,D.box.h+dy);
      if(ev.shiftKey&&f.t!=='line'&&D.box.w>0&&D.box.h>0){var s=Math.max(w/D.box.w,h/D.box.h);w=D.box.w*s;h=D.box.h*s;}
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
      D.ids.forEach(function(x){f=bimBtrFind(D.W.els,x);if(f)bimBtrShift(f.n,D.dx,D.dy,bimBdeMoveFig(D.W));});
    }else{
      f=bimBtrFind(D.W.els,D.ids[0]);
      if(!f)return;
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
  /* the app's key handler asks this first: Ctrl+G, Ctrl+[ and Ctrl+] belong to the board while one designs it */
  function bimBdeWantsKey(ev){
    var a=document.activeElement;
    if(!bimBrdEditing()||!a||!a.closest||!a.closest('.a3d-clb-dsn'))return false;
    return (ev.ctrlKey||ev.metaKey)&&/^(g|G|d|D|\[|\]|\{|\})$/.test(ev.key);
  }
  function bimBdeKey(ev){
    var t=ev.target,k=ev.key,c=ev.ctrlKey||ev.metaKey,W,S,m,f;
    if(!bimBrdEditing()||!t||!t.closest||!t.closest('.a3d-clb-dsn'))return;
    if(/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))return;
    if(!A3D_BDE.sel.length)return;
    if(c&&(k==='g'||k==='G')){bimBdeDo(ev.shiftKey?'ungroup':'group');}
    else if(c&&(k==='d'||k==='D'))bimBdeDo('dup');
    else if(c&&(k===']'||k==='}'))bimBdeDo(ev.shiftKey?'front':'forward');
    else if(c&&(k==='['||k==='{'))bimBdeDo(ev.shiftKey?'back':'backward');
    else if(k==='Delete'||k==='Backspace')bimBdeDo('del');
    else if(k==='Enter')bimBdeEnter(ev.shiftKey);
    else if(/^Arrow/.test(k)&&!c){
      W=bimBdeWork();if(!W)return;
      S=bimBdeSel(W).filter(function(x){return !bimBtrEff(W.els,x).lock;});
      if(!S.length)return;
      m=ev.shiftKey?10:1;
      S.forEach(function(x){f=bimBtrFind(W.els,x);bimBtrShift(f.n,k==='ArrowLeft'?-m:k==='ArrowRight'?m:0,k==='ArrowUp'?-m:k==='ArrowDown'?m:0,bimBdeMoveFig(W));});
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
  /* ---- after the board is drawn: the selection's outlines, and the panel ---- */
  function bimBdeOverlay(d,W,live){
    var o=d&&d.querySelector('.a3d-clb-dsel'),S,h='',fb;
    if(!o)return;
    S=bimBdeSel(W);fb=bimBdeFigBox(W);
    S.forEach(function(x,i){
      var f=bimBtrFind(W.els,x),b=bimBtrBox(f.n,fb),hd=false;
      if(!b)return;
      b={x:b.x,y:b.y,w:b.w,h:b.h};
      if(live&&live.dx!==undefined){b.x+=live.dx;b.y+=live.dy;}
      if(live&&live.w!==undefined&&f.n.t!=='line'){b.w=Math.max(0.5,live.w);b.h=Math.max(0.5,live.h);}
      hd=S.length===1&&f.n.t!=='group'&&f.n.t!=='fig'&&!bimBtrEff(W.els,x).lock;
      h+='<div class="a3d-clb-dbox'+(f.n.mask?' mk':'')+'" style="'+bimBdsPos(b,0,0)+'">'+
        (hd?'<div class="a3d-clb-dhdl" data-bdh="se" title="Drag to size; Shift keeps its proportions" style="'+(f.n.t==='line'?'left:'+bimBdsPx(f.n.x+f.n.w-b.x)+'px;top:'+bimBdsPx(f.n.y+f.n.h-b.y)+'px':'right:0;bottom:0')+'"></div>':'')+'</div>';
    });
    if(A3D_BDE.scope){var g=bimBtrFind(W.els,A3D_BDE.scope),gb=g&&bimBtrBox(g.n,fb);if(gb)h='<div class="a3d-clb-dscope" style="'+bimBdsPos(gb,0,0)+'"></div>'+h;}
    o.innerHTML=h;
  }
  /* the board was drawn: the selection kept to what is still there, outlined, and the panel brought up to date */
  function bimBdeAfterDraw(b){
    var W,d;
    if(!bimBrdEditing()){bimBdePanelClose();A3D_BDE.sel=[];A3D_BDE.scope=null;return;}
    W=bimBdeWork();
    if(!W){bimBdePanelClose();return;}
    A3D_BDE.sel=bimBdeSel(W);
    if(A3D_BDE.scope&&!bimBtrFind(W.els,A3D_BDE.scope))A3D_BDE.scope=null;
    d=b&&b.querySelector('.a3d-clb-dsn');
    if(d){d.setAttribute('tabindex','0');d.setAttribute('aria-label','The board: click an element to select it; the layer list beside it has every element');bimBdeOverlay(d,W,null);}
    bimBdePanel(W);
  }
  function bimBdeSync(){
    var W=bimBdeWork();
    if(!W)return;
    A3D_BDE.sel=bimBdeSel(W);
    bimBdeOverlay(bimBdeDsn(),W,null);
    bimBdePanel(W);
  }
export {
  A3D_BDE, bimBdeAdd, bimBdeAddImage, bimBdeAfterDraw, bimBdeCommit, bimBdeDo, bimBdeEnter, bimBdeEsc,
  bimBdeFigBox, bimBdeInto, bimBdeName, bimBdeSel, bimBdeSet, bimBdeSync, bimBdeWantsKey, bimBdeWire,
  bimBdeWork
};
