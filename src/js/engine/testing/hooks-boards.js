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
