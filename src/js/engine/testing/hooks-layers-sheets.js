  /* __acad3dV121b: what this start removed, and the names it removes */
  window.__a3dCanvasCleared=function(){return {removed:A3D_CANVAS_CLEARED.slice(),names:A3D_CANVAS_KEYS.slice()};};
  window.__a3dThemeAtStart=function(){return A3D_THEME_AT_START;};   /* __acad3dV121b */
  window.__a3dAddLayer=addLayer;
  window.__a3dSetLayer=setActiveLayer;
  /* __acad3dV121: the layer rules, the three questions and the tree, through the functions the panel,
     the manager and the commands call */
  window.__a3dLayerNew=function(opts){var l=bimLayerNew(opts||{});return l?l.id:null;};
  window.__a3dLayerSet=function(id,field,val){return bimLayerSet(id,field,val);};
  window.__a3dLayerDelete=function(id){return bimLayerDelete(id);};
  window.__a3dLayerCurrent=function(id){return bimLayerMakeCurrent(id);};
  window.__a3dObjSetLayer=function(objId,layerId){return bimObjSetLayer(objId,layerId);};
  window.__a3dLayerQ=function(objId){
    var o=objById(objId);
    if(!o)return null;
    var s=bimObjLayerState(o),ly=bimLayerOf(o);
    return {layer:ly?ly.id:null,on:s.on,frozen:s.frozen,locked:s.locked,plot:s.plot,
      shown:bimLayerShown(o),pickable:bimLayerPickable(o),selectable:bimLayerSelectable(o),alpha:bimLayerAlpha(o)};
  };
  window.__a3dLayerTree=function(){return bimLayerTree().map(function(t){return {id:t.ly.id,name:t.ly.name,depth:t.depth};});};
  window.__a3dLinetypes=function(){return JSON.parse(JSON.stringify(BIM_LINETYPES));};
  window.__a3dLineweights=function(){return BIM_LINEWEIGHTS.slice();};
  window.__a3dActiveLayer=function(){return A3D.activeLayer;};
  /* the look a sketch is drawn with on the open sheet's paper, when the sheet is plotted */
  window.__a3dPlotLook=function(objId,pxPerMM){
    var s=bimSheetById(A3D.activeSheetId);
    if(!s)return null;
    A3D.lastLook={};
    bimRenderSheet(s,pxPerMM||SHEET_EXPORT_PXMM,true);
    return window.__a3dLastLook(objId);
  };
  window.__a3dImportText=function(text,filename){
    var ext=(filename.split('.').pop()||'').toLowerCase();
    if(ext==='dxf')return bimImportDXF(text,filename);
    if(ext==='obj')return bimImportOBJ(text,filename);
    if(ext==='ifc')return bimImportIFC(text,filename);
    a3dToast('Unsupported text import type: .'+ext);
  };
  window.__a3dImportBinary=function(buf,filename){
    var ext=(filename.split('.').pop()||'').toLowerCase();
    if(ext==='stl')return bimImportSTL(buf,filename);
    a3dToast('Unsupported binary import type: .'+ext);
  };
  window.__a3dSheets=function(){return JSON.parse(JSON.stringify(A3D.sheets));};
  window.__a3dAddSheet=function(number,name,sizeKey){var s=bimAddSheet(number,name,sizeKey);return s?s.id:null;};
  window.__a3dDeleteSheet=bimDeleteSheet;
  window.__a3dOpenSheetView=function(id){return bimActivateView('sheet',id);};   /* __acad3dV116: the view path, not around it */
  window.__a3dCloseSheetView=function(){return bimShowModel();};   /* __acad3dV116 */
  window.__a3dActiveSheetId=function(){return A3D.activeSheetId;};
  /* __acad3dV122: the Pages display, as the engine holds it */
  window.__a3dPages=function(){
    var pages=A3D.sheets.map(function(s){
      var e=A3D_PAGES.els[s.id];
      return {id:s.id,label:bimSheetLabel(s),el:!!e,cssW:e?e.box.offsetWidth:0,cssH:e?e.box.offsetHeight:0,
        devW:e?e.cv.width:0,devH:e?e.cv.height:0,scale:e?e.scale:0,drawn:!!(e&&e.key&&e.key===bimPageKey(s,e))};
    });
    var dom=el.pagescol?Array.prototype.map.call(el.pagescol.children,function(b){return b.getAttribute('data-page');}):[];
    return {display:A3D_PAGES.display,on:bimPagesOn(),zoom:A3D_PAGES.zoom,pxmm:A3D_PAGES.pxmm,cur:A3D.activeSheetId,dom:dom,
      index:bimPagesIndex(),rev:A3D_REV,pages:pages,scrollTop:el.pageswrap?el.pageswrap.scrollTop:0,
      view:{kind:A3D_VIEW.kind,id:A3D_VIEW.id,name:A3D_VIEW.name},hint:bimStatusHintText(),
      keys:A3D_PAGEVIEW_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),say:k.say.slice(),label:k.label};}),
      zooms:A3D_PAGE_ZOOMS.map(function(z){return z.v;})};
  };
  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
  /* __acad3dV122: the Presentation panel as it is on screen, and the order */
  window.__a3dPresPanel=function(){
    var host=bimPresHost(),items=[];
    if(host)Array.prototype.forEach.call(host.querySelectorAll('[data-prpitem]'),function(it){
      var id=it.getAttribute('data-prpitem'),cv=it.querySelector('canvas[data-prpthumb]'),s=bimSheetById(id),nm=it.querySelector('.a3d-prpname'),no=it.querySelector('.a3d-prpno');
      var fr=it.querySelector('iframe[data-prpbframe]'),bd=bimBoardById(id),fd=fr&&fr.contentDocument;   /* __acad3dV162: a board's page */
      items.push({id:id,no:no?no.textContent:null,name:nm?nm.textContent:null,cur:it.classList.contains('cur'),w:cv?cv.width:0,h:cv?cv.height:0,
        drawn:bd?!!(fd&&fd.__prpKey==='brd|'+A3D_REV&&fd.querySelector('.a3d-clb.prt')):!!(cv&&s&&cv.__prpKey===bimPageSig(s)+'|'+cv.width+'x'+cv.height),
        board:bd?bd.kind:null,scale:fr?fr.style.transform:null,thumbTitle:fd&&fd.querySelector('.a3d-clb-h1')?fd.querySelector('.a3d-clb-h1').textContent:null});
    });
    return {open:!!host,count:bimPresSeq().length,items:items,edit:A3D_PRP.edit,
      head:host?(host.querySelector('.a3d-prpcount')||{}).textContent:null,cached:Object.keys(A3D_PRP.thumbs).length};
  };
  window.__a3dSheetMove=function(id,to){return bimSheetMove(id,to);};
  window.__a3dSheetMenuItems=function(id,where){return bimSheetMenuItems(id,where).map(function(x){return x==='-'?'-':x[0];});};
  /* __acad3dV122: Present, as the engine holds it */
  window.__a3dSlideshow=function(){
    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,Q=bimPresSeq(),e=Q[A3D_SLIDESHOW.idx]||null,s=e&&e.t==='sheet'?e.s:null,bd=ov?ov.querySelector('.a3d-ssboard'):null;   /* __acad3dV162 */
    return {on:A3D_SLIDESHOW.on,idx:A3D_SLIDESHOW.idx,id:e?e.id:null,n:Q.length,fs:A3D_SLIDESHOW.fs,board:e&&e.t==='board'?e.b.kind:null,
      boardShown:bd?bd.getAttribute('data-sspage'):null,boardTitle:bd&&bd.querySelector('.a3d-clb-h1')?bd.querySelector('.a3d-clb-h1').textContent:null,
      canvasShown:!!(cv&&cv.style.display!=='none'),
      fsEl:!!(document.fullscreenElement||document.webkitFullscreenElement),open:!!(ov&&ov.classList.contains('open')),
      idle:!!(ov&&ov.classList.contains('idle')),cssW:cv?cv.offsetWidth:0,cssH:cv?cv.offsetHeight:0,devW:cv?cv.width:0,devH:cv?cv.height:0,
      shown:cv?cv.getAttribute('data-sspage'):null,drawnKey:cv?cv.getAttribute('data-sskey'):null,scale:A3D_SLIDESHOW.scale,
      key:s?bimPageSig(s):null,pos:ov?ov.querySelector('.a3d-sspos').textContent:'',hint:ov?ov.querySelector('.a3d-sshint').textContent:'',
      ahead:A3D_SLIDESHOW.ahead?A3D_SLIDESHOW.ahead.id:null,
      keys:A3D_SHOW_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),say:k.say.slice(),label:k.label};})};
  };
  window.__a3dSlideshowStart=function(id){return bimSlideshowStart(id);};
  /* __acad3dV162: the boards as pages of the set */
  window.__a3dPresSeq=function(){return bimPresSeq().map(function(e){return {id:e.id,t:e.t,kind:e.t==='board'?e.b.kind:null};});};
  window.__a3dPresRecord=function(){return JSON.parse(JSON.stringify(bimPresData()));};
  window.__a3dBoardAdd=function(k){return bimBoardAdd(k);};
  window.__a3dBoardRemove=function(id){return bimBoardRemove(id);};
  window.__a3dBoardShow=function(k){return bimBoardShow(k);};
  window.__a3dPresOpen=function(id){return bimPresOpenPage(id);};
  window.__a3dPresMoveNear=function(id,t,after){return bimPresMoveNear(id,t,!!after);};
  window.__a3dPresStep=function(id,d){return bimPresStep(id,d);};
  window.__a3dBoardMenuItems=function(id){return bimBoardMenuItems(id).map(function(x){return x==='-'?'-':x[0];});};
  window.__a3dBoardMenuDo=function(a,id){return bimBoardMenuDo(a,id);};
  window.__a3dBoardPrintHtml=function(k){return bimBoardPrintHtml(k);};
  window.__a3dPrintSetHtml=function(){return bimPrintSetHtml();};
  window.__a3dClbCss=function(){return bimClbCss();};
  window.__a3dClbState=function(){var b=bimClbEl();return {open:A3D_CLB.open,kind:A3D_CLB.kind,board:A3D_CLB.board,narrow:A3D_CLB.narrow,inView:!!(b&&b.parentNode&&b.parentNode.classList&&b.parentNode.classList.contains('a3d-vp')),cls:b?b.className:null,w:b?bimClbW(b):0};};
  window.__a3dSlideshowEnd=function(){return bimSlideshowEnd();};
  window.__a3dPagesGo=function(i){return bimPagesGo(i);};
  window.__a3dPagesZoom=function(z){return bimPagesZoom(z);};
  /* the pixels of a page drawn afresh at a scale, to set beside the page on screen */
  window.__a3dPageFresh=function(id,scale){
    var s=bimSheetById(id);if(!s)return null;
    var cv=document.createElement('canvas');
    bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,cv,scale);
    return cv.toDataURL('image/png');
  };
  window.__a3dSheetIsOpen=function(){return !!(el.sheetview&&el.sheetview.classList.contains('open'));};
  /* __acad3dV116 */
  window.__a3dSheetSpace=function(){
    var sh=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sh,A3D.sheetActiveVp);
    return {onSheet:bimSheetOnScreen(),sheet:A3D.activeSheetId,activeVp:A3D.sheetActiveVp,selVp:A3D.sheetSelVp,
            view:A3D_VIEW.kind,viewId:A3D_VIEW.id,viewName:A3D_VIEW.name,
            vp:vp?{pan:vp.pan||null,scaleMode:vp.scaleMode,scaleDenom:vp.scaleDenom}:null};
  };
  window.__a3dSheetVpCamera=function(sheetId,vpId,pxPerMM){
    var vp=bimSheetVp(bimSheetById(sheetId),vpId);if(!vp)return null;
    var src=bimResolveViewportSource(vp);if(src.error)return null;
    return bimSheetSolveCamera(src,vp.w*(pxPerMM||1),vp.h*(pxPerMM||1),pxPerMM||1,vp.scaleMode,vp.scaleDenom,vp.pan);
  };
  window.__a3dSheetSourceOptions=bimSheetSourceOptions;
  window.__a3dAddViewport=function(sheetId,kind,refId,scaleMode,scaleDenom){
    var s=bimSheetById(sheetId);if(!s)return null;
    var vp=bimNewViewport(kind,refId);
    var src=bimResolveViewportSource(vp);
    if(!src.error)vp.label=src.label;
    vp.scaleMode=scaleMode||'fit';
    vp.scaleDenom=scaleDenom||100;
    s.viewports.push(vp);
    bimSheetViewRefresh();saveSoon();
    return vp.id;
  };
  window.__a3dSetViewportRect=function(sheetId,vpId,x,y,w,h){
    var s=bimSheetById(sheetId);if(!s)return false;
    var i;for(i=0;i<s.viewports.length;i++)if(s.viewports[i].id===vpId){
      var vp=s.viewports[i];vp.x=x;vp.y=y;vp.w=w;vp.h=h;bimSheetViewRefresh();return true;
    }
    return false;
  };
  window.__a3dDeleteViewport=function(sheetId,vpId){
    var s=bimSheetById(sheetId);if(!s)return false;
    var idx=-1,i;for(i=0;i<s.viewports.length;i++)if(s.viewports[i].id===vpId)idx=i;
    if(idx<0)return false;
    s.viewports.splice(idx,1);bimSheetViewRefresh();saveSoon();
    return true;
  };
  window.__a3dRenderSheetPNG=function(pxPerMM){
    var s=bimSheetById(A3D.activeSheetId);if(!s)return null;
    var cv=bimRenderSheet(s,pxPerMM||SHEET_PREVIEW_PXMM);
    return cv?cv.toDataURL('image/png'):null;
  };
  window.__a3dTitleBlockGet=function(){return JSON.parse(JSON.stringify(A3D.titleBlock));};
  /* __acad3dV115: the document tabs and the Start page read and drive the project list here */
  window.__a3dDocs={
    list:function(){
      return A3D_DOCS.docs.map(function(d){
        var loaded=(d.id===A3D_DOCS.active);
        return {id:d.id,name:bimDocName(d.id),objs:loaded?A3D.objs.length:(d.objs||0),saved:loaded?0:(d.saved||0),
                open:A3D_DOCS.open.indexOf(d.id)>=0,loaded:loaded};
      });
    },
    open:function(){return A3D_DOCS.open.slice();},
    active:function(){return A3D_DOCS.open.indexOf(A3D_DOCS.active)>=0?A3D_DOCS.active:null;},
    activate:bimDocsActivate,
    create:bimDocsCreate,
    close:bimDocsClose,
    remove:bimDocsRemove,
    undoDepth:function(){return {undo:UNDO_STACK.length,redo:REDO_STACK.length};}
  };
  window.__a3dTitleBlockSet=function(tb){A3D.titleBlock=tb;bimSheetViewRefresh();saveSoon();};
  window.__a3dSheetPointerDown=bimSheetPointerDown;
  window.__a3dSheetPointerMove=bimSheetPointerMove;
  window.__a3dSheetPointerUp=bimSheetPointerUp;
  window.__a3dSheetSelectedVp=function(){return A3D.sheetSelVp;};
  window.__a3dResolveViewportSource=bimResolveViewportSource;
  window.__a3dSheetSolveCamera=bimSheetSolveCamera;
  window.__a3dSolveSketchConstraints=bimSolveSketchConstraints;
  window.__a3dEstimateSketchDOF=bimEstimateSketchDOF;
  window.__a3dAddSketchConstraint=function(objId,type,refs,value){
    var o=objById(objId);if(!o)return null;
    var c=bimAddSketchConstraint(o,type,refs,value);
    return c?c.id:null;
  };
  window.__a3dDeleteSketchConstraint=function(objId,conId){
    var o=objById(objId);if(!o)return false;
    var before=(o.constraints||[]).length;
    bimDeleteSketchConstraint(o,conId);
    return (o.constraints||[]).length<before;
  };
  window.__a3dSketchConstraints=function(objId){
    var o=objById(objId);
    return (o&&o.constraints)?JSON.parse(JSON.stringify(o.constraints)):[];
  };
  window.__a3dSketchConstraintDesc=function(objId,conId){
    var o=objById(objId);if(!o||!o.constraints)return null;
    var i,c=null;
    for(i=0;i<o.constraints.length;i++)if(o.constraints[i].id===conId){c=o.constraints[i];break;}
    return c?bimSketchConstraintDesc(o,c):null;
  };
  window.__a3drIcon=a3drIcon;
  window.__a3drLabel=a3drLabel;
  window.__a3dResolveSketch=function(objId,pinIdx){
    var o=objById(objId);if(!o)return null;
    return bimResolveSketch(o,(pinIdx===undefined?null:pinIdx));
  };
  window.__a3dStartConstraintTool=startConstraintTool;
  window.__a3dGrips=function(){paint();return JSON.parse(JSON.stringify(A3D.grips));};
