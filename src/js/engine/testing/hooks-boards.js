import { bimApplyUnitState, bimUnitState } from '../properties/palette.js';
import { bimResLayers } from '../analysis/results-layers.js';
import { A3D_CLB, bimClbEl, bimClbOpen } from '../site-analysis/climate-board.js';
import { A3D_REV, setA3D_REV } from '../core/objects-save.js';
import { bimLtMenuClose } from '../sheets/layout-tabs.js';
import { bimBoardById, bimBoardHtmlFor } from '../sheets/boards.js';
import {
  bimBrdBands, bimBrdFigsValid, bimBrdMeasureDefault, bimBrdNatH, bimBrdRec, bimFigCapture, bimFigCat,
  bimFigSrc
} from '../sheets/board-figures.js';
import {
  A3D_BRD, bimBrdAddFig, bimBrdCatalogue, bimBrdDlgClose, bimBrdDup, bimBrdDupBoard, bimBrdEdit, bimBrdFit,
  bimBrdMenu, bimBrdNewUi, bimBrdNudge, bimBrdOptsDlg, bimBrdOptsSet, bimBrdRedraw, bimBrdRemove,
  bimBrdRename, bimBrdReset, bimBrdSnap, bimBrdSwap, bimBrdWorking
} from '../sheets/board-edit.js';
import {
  bimLvBindValid, bimLvFormat, bimLvGroup, bimLvKind, bimLvMenuItems, bimLvOvKeep, bimLvOvReset, bimLvOvSet,
  bimLvOvState, bimLvOvValid, bimLvPrintNote, bimLvSubst, bimLvTokens
} from '../sheets/live-text.js';
import {
  bimLiveGet, bimLiveKey, bimLiveKeys, bimLiveMarks, bimLiveShow, bimLiveStaleItems
} from '../sheets/live-sources.js';
import {
  bimLbdChartMenu, bimLbdCols, bimLbdKpiMenu, bimLbdRows, bimLbdRun, bimLbdSchedMenu, bimLbdState
} from '../sheets/live-board-draw.js';
import {
  bimLvAct, bimLvAddNumber, bimLvInsertField, bimLvOverride, bimLvPropsHtml, bimLvSetDp, bimLvTextPatch
} from '../sheets/live-edit.js';

  /* __acad3dV172b: a board's figures and Edit, for the suite */
  function bimBrdHookErr(e){return {error:String(e&&e.message||e)};}
  window.__a3dBrdCat=function(){
    var ctx={edit:false,narrow:false,caps:{},no:0};
    return bimFigCat().map(function(E){return {f:E.f,kind:E.kind,cat:E.cat,name:E.name,kpis:E.kpis,has:E.f==='text'||!!bimFigSrc(ctx,E.f,null)};});
  };
  window.__a3dBrdCapture=function(kind,narrow){var c=bimFigCapture(kind,!!narrow);return {order:c.order,notes:!!c.notes,cls:c.order.map(function(f){return c.figs[f].cls||null;})};};
  window.__a3dBrdRecord=function(id){var b=bimBoardById(id);return b?JSON.parse(JSON.stringify(b)):null;};
  window.__a3dBrdEdit=function(on){return bimBrdEdit(!!on);};
  /* the board on screen: its figures where they are drawn, in reading order */
  window.__a3dBrdState=function(){
    var b=bimClbEl(),A=b?b.querySelector('.a3d-clb-arr'):null,ar=A?A.getBoundingClientRect():null,figs=[],x=[],B=bimBrdRec();
    if(A)[].forEach.call(A.querySelectorAll('.a3d-clb-fig'),function(f){
      var r=f.getBoundingClientRect(),n=f.querySelector('.a3d-clb-fno'),c=f.querySelector('.a3d-clb-card,.a3d-clb-tcard');
      figs.push({k:f.getAttribute('data-brdk'),f:f.getAttribute('data-brdf'),no:n?n.textContent:'',l:r.left-ar.left,t:r.top-ar.top,w:r.width,h:r.height,
        cls:f.className,over:c?c.scrollHeight>c.clientHeight+2:false,title:(f.querySelector('.a3d-clb-h2,.a3d-clb-texth')||{}).textContent||''});
    });
    if(b)[].forEach.call(b.querySelectorAll('.a3d-clb-extra [data-brdx]'),function(e){x.push(e.getAttribute('data-brdx'));});
    return {open:A3D_CLB.open,kind:A3D_CLB.kind,cid:A3D_CLB.cid,board:A3D_CLB.board,edit:A3D_CLB.edit,narrow:A3D_CLB.narrow,dlg:A3D_BRD.dlg?A3D_BRD.dlg.getAttribute('aria-label'):null,
      arranged:!!A,z:A?parseFloat(A.style.getPropertyValue('--z'))||1:null,zoomed:A?getComputedStyle(A).zoom:null,figs:figs,extra:x,bands:A?A.querySelectorAll('.a3d-clb-band').length:0,
      rec:B?JSON.parse(JSON.stringify(B)):null,editBar:!!(b&&b.querySelector('.a3d-clb-ebar')),editBtn:!!(b&&b.querySelector('.a3d-clb-bar [data-brd="edit"]')),
      label:b?b.getAttribute('aria-label'):null,h1:b&&b.querySelector('.a3d-clb-h1')?b.querySelector('.a3d-clb-h1').textContent:null};
  };
  window.__a3dBrdWorking=function(){var B=bimBrdRec();return B?bimBrdWorking(B):null;};
  window.__a3dBrdMeasure=function(kind){return bimBrdMeasureDefault(kind);};
  window.__a3dBrdNatH=function(f,w,o){try{return bimBrdNatH({k:'f1',f:f,o:o||undefined},w);}catch(e){return bimBrdHookErr(e);}};
  window.__a3dBrdSnap=function(mode,F0,dx,dy,others,z){return bimBrdSnap(mode,F0,dx,dy,others||[],z||1);};
  window.__a3dBrdBands=function(L){return bimBrdBands(L).map(function(D){return {t:D.t,b:D.b,k:D.f.map(function(F){return F.k;})};});};
  window.__a3dBrdValid=function(L){return bimBrdFigsValid(L);};
  window.__a3dBrdAdd=function(f,o){try{return bimBrdAddFig(f,o);}catch(e){return bimBrdHookErr(e);}};
  window.__a3dBrdRemove=function(k){return bimBrdRemove(k);};
  window.__a3dBrdDup=function(k){return bimBrdDup(k);};
  window.__a3dBrdFit=function(k){return bimBrdFit(k);};
  window.__a3dBrdSwap=function(k,d){return bimBrdSwap(k,d);};
  window.__a3dBrdOpts=function(k,o){return bimBrdOptsSet(k,o);};
  window.__a3dBrdNudge=function(k,dx,dy,size){return bimBrdNudge(k,dx,dy,!!size);};
  window.__a3dBrdReset=function(){return bimBrdReset();};
  window.__a3dBrdNew=function(name){try{return bimBrdNewUi(name);}catch(e){return bimBrdHookErr(e);}};
  window.__a3dBrdDupBoard=function(id){try{return bimBrdDupBoard(id);}catch(e){return bimBrdHookErr(e);}};
  window.__a3dBrdRename=function(n){return bimBrdRename(n);};
  window.__a3dBrdCatalogue=function(){return bimBrdCatalogue();};
  window.__a3dBrdOptsDlg=function(k){return bimBrdOptsDlg(k);};
  window.__a3dBrdDlgClose=function(){bimBrdDlgClose();return true;};
  window.__a3dBrdMenu=function(k){var ok=bimBrdMenu(k,40,40),m=document.getElementById('a3d-ltmenu'),it=m?[].map.call(m.querySelectorAll('[data-ltm]'),function(b){return [b.textContent,b.getAttribute('data-ltm')];}):[];bimLtMenuClose();return ok?it:null;};
  window.__a3dBrdOpen=function(key){return bimClbOpen(key);};
  window.__a3dBrdHtmlFor=function(key,narrow){return bimBoardHtmlFor(key,!!narrow);};
  /* __acad3dV175a: live text on a board: fields, numbers, overrides, Reset, Unlink; the units kept with the project */
  window.__acad3dV175a='fields,numbers,override,reset,keep,unlink,marks,printnote,unitsaved,loadrev';
  window.__a3dLive={tokens:bimLvTokens,group:bimLvGroup,format:bimLvFormat,subst:bimLvSubst,ovSet:bimLvOvSet,ovReset:bimLvOvReset,ovState:bimLvOvState,ovKeep:bimLvOvKeep,
    printNote:bimLvPrintNote,menuItems:bimLvMenuItems,kind:bimLvKind,keys:bimLiveKeys,key:bimLiveKey,get:function(k,id,nm,B){return bimLiveGet(k,id,nm,B||null);},
    show:function(n,B,edit){return bimLiveShow(n,B||null,!!edit);},marks:bimLiveMarks,stale:bimLiveStaleItems,textPatch:bimLvTextPatch,
    insertField:function(k){return bimLvInsertField(k);},addNumber:function(k,id){return bimLvAddNumber(k,id);},override:function(v){return bimLvOverride(v);},
    setDp:function(v){return bimLvSetDp(v);},act:function(a){return bimLvAct(a,40,40);},propsHtml:bimLvPropsHtml,unitState:bimUnitState,applyUnits:bimApplyUnitState,
    bindValid:bimLvBindValid,ovValid:bimLvOvValid,rev:function(){return A3D_REV;},bump:function(){setA3D_REV(A3D_REV+1);return A3D_REV;}};
  /* __acad3dV175b: schedules, single indicators and result charts on a board */
  window.__acad3dV175b='sched,kpi,rchart,hist,sunsix,solarkwh,printlist';
  window.__a3dLiveBoard={state:function(n){return bimLbdState(n,null);},cols:bimLbdCols,rows:function(s){return bimLbdRows(s);},
    schedMenu:function(){return bimLbdSchedMenu(40,40);},kpiMenu:function(){return bimLbdKpiMenu(40,40);},chartMenu:function(){return bimLbdChartMenu(40,40);},
    run:function(id){return bimLbdRun(id);},addLayer:function(R){bimResLayers().unshift(R);setA3D_REV(A3D_REV+1);return R.id;},redraw:function(){bimBrdRedraw();return true;}};
