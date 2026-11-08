import { A3D } from '../core/state.js';
import { bimLayerById, bimLayerZero } from '../layers/layer-rules.js';
import { bimStd } from '../standards/registry.js';
import { bimBrdRec } from './board-figures.js';
import { bimBrdDlgClose, bimBrdDlgOpen } from './board-edit.js';
import {
  bimBobBox, bimBobFind, bimBobLayKids, bimBobNewId, bimBobPxMm, bimBobShift
} from './board-objects.js';
import { bimBalAlign, bimBalDistribute, bimBalTidy, bimBalUnion } from './board-arrange.js';
import {
  bimPgBoardPage, bimPgDims, bimPgGalleryHtml, bimPgGalleryWire, bimPgIso5457Ok, bimPgLabel
} from './page-sizes.js';
import {
  A3D_BDE, bimBdeCommit, bimBdeFigBox, bimBdeMoveFig, bimBdePickable, bimBdeSel, bimBdeWork
} from './board-design-edit.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV174b, __acad3dV174c: a board's arranging tools and its page =================
     Align, distribute and tidy the selection (board-arrange.js); a layer's stack on this board; the board's page from
     the gallery (page-sizes.js) and its ISO 5457 frame and ISO 7200 title block, or a US title strip. Each change is
     one undo step, through bimBdeCommit. */
  /* ---- __acad3dV174b: align, distribute, tidy; a layer's stack on this board ---- */
  /* the page an object aligns to on its own: the board's page when it has one, else the board's width and height */
  function bimBdePage(W){
    var pg=bimPgBoardPage(W.B),k=bimBobPxMm(),H=0;
    if(pg)return {x:0,y:0,w:pg.w,h:pg.h};
    W.objs.forEach(function(n){var b=bimBobBox(n,bimBdeFigBox(W));if(b&&b.y+b.h>H)H=b.y+b.h;});
    return {x:0,y:0,w:1408/k,h:H};
  }
  /* a: 'al-left' (and the other five edges), 'dist-x', 'dist-y', 'tidy-x', 'tidy-y' */
  function bimBdeArrange(a){
    var W=bimBdeWork(),S,fb,B,R,mv;
    if(!W)return false;
    S=bimBdeSel(W).filter(function(x){return bimBdePickable(W,x);});
    if(!S.length)return false;
    fb=bimBdeFigBox(W);
    B=S.map(function(x){return bimBobBox(bimBobFind(W.objs,x).n,fb);});
    if(/^al-/.test(a))R=bimBalAlign(B,a.slice(3),bimBdePage(W));
    else if(/^dist-/.test(a)){if(S.length<3){a3dToast('Distribute takes three or more objects');return false;}R=bimBalDistribute(B,a.slice(5)).pos;}
    else if(/^tidy-/.test(a)){if(S.length<2)return false;R=bimBalTidy(B,a.slice(5)).pos;}
    else return false;
    mv=bimBdeMoveFig(W);
    S.forEach(function(x,i){bimBobShift(bimBobFind(W.objs,x).n,Math.round((R[i].x-B[i].x)*1000)/1000,Math.round((R[i].y-B[i].y)*1000)/1000,mv);});
    return bimBdeCommit(W,null,S);
  }
  /* a layer's stack on this board: its settings (o), on (dir) or off (dir null) */
  function bimBdeLaySet(lyId,o){
    var W=bimBdeWork(),L,k,kids,b;
    if(!W||!bimLayerById(lyId))return false;
    L=W.lay[lyId];
    if(o.dir===null){delete W.lay[lyId];return bimBdeCommit(W,'The layer\'s objects are free again',A3D_BDE.sel);}
    if(!L){
      kids=bimBobLayKids(W.objs,lyId);
      b=kids.length?bimBalUnion(kids.map(function(n){return bimBobBox(n,bimBdeFigBox(W));}).filter(function(q){return !!q;})):{x:20,y:20,w:100,h:60};
      L=W.lay[lyId]={dir:'row',gap:5,pad:0,am:'start',ac:'start',x:b.x,y:b.y,sw:'hug',sh:'hug',w:b.w,h:b.h};
    }
    for(k in o)if(o.hasOwnProperty(k))L[k]=o[k];
    return bimBdeCommit(W,null,A3D_BDE.sel);
  }
  /* ---- __acad3dV174c: the board's page and its title block ---- */
  function bimBdePageDlg(){
    var B=bimBrdRec(),cur,o,tb='none',d,st;
    if(!B){a3dToast('Only a board in the set can have a page');return false;}
    cur=B.page?B.page.key:'iso-A3';o=B.page?B.page.o:'l';
    (B.objs||[]).forEach(function(n){if(n.t==='tblock')tb=n.st;});
    d=bimBrdDlgOpen('<div class="a3d-clb-dlghd"><h2 class="a3d-clb-h2">The board\'s page</h2><p class="a3d-clb-dek">A size from the standards (ISO 216, ASME Y14.1, the Architectural sizes). The board becomes that page: on screen, in Present and on paper, one page at its own size.</p></div>'+
      '<div data-pggal="1">'+bimPgGalleryHtml(cur,o)+'</div>'+
      '<form class="a3d-clb-dlgf" data-bdpgform="1"><label>Title block<select name="tb">'+
        '<option value="none"'+(tb==='none'?' selected':'')+'>None</option><option value="iso"'+(tb==='iso'?' selected':'')+'>ISO 5457 frame and ISO 7200 title block, at the bottom right</option>'+
        '<option value="us"'+(tb==='us'?' selected':'')+'>A frame and a title strip at the right (US practice)</option></select></label>'+
      '<div class="a3d-clb-dlgb">'+(B.page?'<button type="button" class="a3d-clb-btn" data-bdpg="none">No page</button>':'')+'<button type="button" class="a3d-clb-btn" data-brddlg="cancel">Cancel</button><button type="submit" class="a3d-clb-btn pri">Apply</button></div></form>','The board\'s page',true);
    st=bimPgGalleryWire(d,cur,o,null);
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-bdpg]'):null;if(b){bimBrdDlgClose();bimBdePageSet(null,null,'none');}});
    d.addEventListener('submit',function(ev){
      var f=ev.target,v;
      if(!f||!f.getAttribute||!f.getAttribute('data-bdpgform'))return;
      ev.preventDefault();ev.stopPropagation();
      v=f.querySelector('[name="tb"]').value;
      bimBrdDlgClose();
      bimBdePageSet(st.key,st.o,v);
    },true);
    return true;
  }
  /* a page (key null: none) and a title block ('none', 'iso', 'us'), the frame and block put on the current layer */
  function bimBdePageSet(key,o,tb){
    var W=bimBdeWork(),d,ly=bimLayerById(A3D.activeLayer)||bimLayerZero(),ml,m,sw,id,msg;
    if(!W)return false;
    W.objs=W.objs.filter(function(n){return n.t!=='tblock'&&n.t!=='border';});
    if(!key){W.page=null;return bimBdeCommit(W,'The board flows again, with no page',[]);}
    W.page={key:key,o:o==='p'?'p':'l'};
    d=bimPgDims(key,W.page.o);
    msg=bimPgLabel(key,W.page.o);
    if(tb==='iso'){
      ml=bimStd('drawing.iso5457','margin_left');m=bimStd('drawing.iso5457','margin');sw=bimStd('drawing.iso5457','frame');
      id=bimBobNewId(W.objs);W.objs.push({id:id,t:'border',layer:ly.id,x:ml,y:m,w:d.w-ml-m,h:d.h-2*m,sw:sw});
      var tw=Math.min(bimStd('drawing.iso7200','width'),d.w-ml-m);
      W.objs.push({id:bimBobNewId(W.objs),t:'tblock',st:'iso',layer:ly.id,x:d.w-m-tw,y:d.h-m-36,w:tw,h:36});
      if(!bimPgIso5457Ok(key,W.page.o))msg+=': not to ISO 5457, which draws A0 to A3 landscape and A4 portrait';
    }else if(tb==='us'){
      m=12.7;
      W.objs.push({id:bimBobNewId(W.objs),t:'border',layer:ly.id,x:m,y:m,w:d.w-2*m,h:d.h-2*m,sw:0.7});
      W.objs.push({id:bimBobNewId(W.objs),t:'tblock',st:'us',layer:ly.id,x:d.w-m-38,y:m,w:38,h:d.h-2*m});
    }
    return bimBdeCommit(W,'The board is a page: '+msg,[]);
  }
export { bimBdeArrange, bimBdeLaySet, bimBdePage, bimBdePageDlg, bimBdePageSet };
