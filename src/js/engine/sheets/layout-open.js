import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimEscXml } from '../io/export-mappings.js';
import { bimLayerById, bimLayerZero } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimStd } from '../standards/registry.js';
import { A3D_CLB, bimClbClose, bimClbOpen } from '../site-analysis/climate-board.js';
import { bimShellSetTab } from '../ui/tool-palette.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { A3D_VIEW, bimActivateView } from '../views/saved-views.js';
import { bimSheetById, bimSheetLabel } from './sheets.js';
import { bimBuildSheetSVG } from './viewports.js';
import { bimRenderLayoutTabs } from './layout-tabs.js';
import { bimLyLabel } from './layouts.js';
import { bimLmDrawMenu, bimLmFrameToVp, bimLmN, bimLmSheetToLayout } from './layout-merge.js';
import { bimPresData, bimPresOpenBoard, bimPresSeq } from './boards.js';
import { bimBrdKeep } from './board-figures.js';
import { bimBobKind } from './board-objects.js';
import { bimPgBoardPage, bimPgDims, bimPgFamilies, bimPgSize } from './page-sizes.js';
import { bimBmapFit } from './board-map.js';
import { bimPresPanelRefresh, refreshBrowser } from './presentation-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV175c WO-18: one editor, one print, in the app =================
     docs/research/research-one-paper-space.md (the owner's D1 to D8) and docs/work-orders/v175c/SPEC-step2.md.
     A sheet opens as a layout in the board editor: Open as layout (the sheet bar, or SHEETLAYOUT) makes it a drawing
     layout (board.drawing) with the sheet's number, name, page and place in the set: the ISO 5457 frame and an ISO 7200
     title block, a map frame (bimLmVpToFrame, WO-11) for each plan, elevation and view at its scale and pan, and a
     schedule for each rooms or levels schedule; one undo step. A sheet a layout cannot hold yet is refused with the
     reason (a size outside the gallery, another schedule). Not done to every sheet at once: a sheet stays a sheet
     until its owner opens it as a layout.
     A drawing layout's Draw menu leaves out the live values and the charts (D4, bimLmDrawMenu, WO-14). Its map frames
     are its viewports: Work in viewport opens the frame's view in the model; the layout's tab brings it back.
     It prints as one vector page: its frames turned back into viewports (bimLmFrameToVp, WO-12) and drawn by the
     sheets' own SVG (each clipped inside its frame, plans as vectors), its shapes and text as SVG, at its page size in
     millimetres; a layout holding a kind the vector page does not draw prints as a board does, and says so. */
  /* the gallery's page of a sheet's size: {key, o}, or null */
  function bimLoPage(sh){
    var m=/^pg:([a-z]+-[A-Z0-9]+):([lp])$/.exec(String(sh&&sh.sizeKey||'')),F=bimPgFamilies(),i,j,o,k,d;
    if(m&&bimPgSize(m[1]))return {key:m[1],o:m[2]};
    for(i=0;i<F.length;i++)for(j=0;j<F[i][3].length;j++)for(o=0;o<2;o++){
      k=F[i][0]+'-'+F[i][3][j];d=bimPgDims(k,o?'p':'l');
      if(d&&Math.abs(d.w-sh.w)<0.5&&Math.abs(d.h-sh.h)<0.5)return {key:k,o:o?'p':'l'};
    }
    return null;
  }
  /* the Draw menu's kinds as bimLmDrawMenu reads them: a live value, a chart, or anything else */
  function bimLoDrawKind(k){return (k==='lvfield'||k==='lvnumber'||k==='lvkpi')?'live':(k==='lvchart'?'chart':'shape');}
  function bimLoDrawKinds(L,drawing){
    var out=bimLmDrawMenu(L.map(function(k){return {k:k,kind:k==='-'?'sep':bimLoDrawKind(k[0])};}),drawing).map(function(x){return x.k;});
    return out.filter(function(k,i){return !(k==='-'&&(i===0||i===out.length-1||out[i-1]==='-'));});
  }
  /* a sheet as a drawing layout's record: {rec} or {why}. fit(frame) gives a fitted frame's {den, px, py}; ly the layer */
  function bimLoFromSheet(sh,fit,ly){
    var page=bimLoPage(sh),L,objs=[],k=1,i,vp,fr,n,d,ml,m,sw,tw;
    if(!page)return {why:'its size ('+sh.w+' x '+sh.h+' mm) is not one of the page sizes a layout has'};
    d=bimPgDims(page.key,page.o);
    ml=bimStd('drawing.iso5457','margin_left');m=bimStd('drawing.iso5457','margin');sw=bimStd('drawing.iso5457','frame');
    tw=Math.min(bimStd('drawing.iso7200','width'),d.w-ml-m);
    objs.push({id:'e'+(k++),t:'border',layer:ly,x:ml,y:m,w:d.w-ml-m,h:d.h-2*m,sw:sw});
    objs.push({id:'e'+(k++),t:'tblock',st:'iso',layer:ly,x:d.w-m-tw,y:d.h-m-36,w:tw,h:36,num:String(sh.number||'')});
    L=bimLmSheetToLayout(sh);
    for(i=0;i<(sh.viewports||[]).length;i++){
      vp=sh.viewports[i];fr=L.objs[i+1];
      if(vp.kind==='schedule'){
        if(vp.refId!=='rooms'&&vp.refId!=='levels')return {why:'its '+(vp.label||vp.refId)+' schedule is not one a layout shows yet (rooms and levels are)'};
        objs.push({id:'e'+(k++),t:'sched',layer:ly,x:vp.x,y:vp.y,w:vp.w,h:vp.h,src:vp.refId,ttl:vp.label||''});
        continue;
      }
      n={id:'e'+(k++),t:'map',layer:ly,x:fr.x,y:fr.y,w:fr.w,h:fr.h,src:fr.src,nm:fr.label};
      if(fr.fit){var f=fit(n);n.den=f.den;n.px=f.px;n.py=f.py;}
      else{n.den=fr.den;n.px=vp.pan&&isFinite(vp.pan[0])?vp.pan[0]:0;n.py=vp.pan&&isFinite(vp.pan[1])?vp.pan[1]:0;}
      objs.push(n);
    }
    return {rec:{name:sh.name||'Untitled',num:String(sh.number||''),page:page,objs:objs,drawing:true}};
  }
  /* Open as layout: the sheet replaced by its drawing layout, in its place in the set, opened in the board editor */
  function bimLoOpenSheet(id){
    var sh=bimSheetById(id),P,ly,plan,bid,n=0,r,order,at;
    if(!sh){a3dToast('No sheet open');return null;}
    ly=(bimLayerById(A3D.activeLayer)||bimLayerZero()).id;
    plan=bimLoFromSheet(sh,bimBmapFit,ly);
    if(plan.why){a3dToast(bimSheetLabel(sh)+' cannot open as a layout yet: '+plan.why);return null;}
    P=bimPresData();
    P.boards.forEach(function(b){var mm=/^board-c(\d+)$/.exec(b.id);if(mm&&+mm[1]>n)n=+mm[1];});
    bid='board-c'+(n+1);
    r=bimBrdKeep({id:bid,kind:'custom'},{name:plan.rec.name,figs:[],objs:plan.rec.objs,page:plan.rec.page,num:plan.rec.num,drawing:true});
    if(!r.objs||r.objs.length!==plan.rec.objs.length){a3dToast(bimSheetLabel(sh)+' could not be opened as a layout -- see the console');
      console.warn('[BIM] Open as layout: the layout\'s objects were not all kept',plan.rec.objs,r.objs);return null;}
    pushUndo();
    order=bimPresSeq().map(function(e){return e.id;});at=order.indexOf(sh.id);
    if(A3D_VIEW.kind==='sheet')bimActivateView('3d',null,{anim:false});
    P.boards.push(r);
    A3D.sheets.splice(A3D.sheets.indexOf(sh),1);
    if(A3D.activeSheetId===sh.id)A3D.activeSheetId=null;
    if(at<0)order.push(bid);else order.splice(at,1,bid);
    P.order=order;
    saveSoon();refreshBrowser();bimPresPanelRefresh();bimRenderLayoutTabs();
    bimShellSetTab('presentation');
    if(bimPresOpenBoard(bid)){A3D_CLB.edit=true;bimClbOpen();}
    a3dToast(bimLyLabel(r.num,r.name)+' is a drawing layout: its viewports are map frames; Undo brings the sheet back');
    return bid;
  }
  /* Work in viewport: the frame's view opened in the model */
  function bimLoWorkIn(fr){
    var m=/^(plan|elevation|view):(.+)$/.exec(fr&&fr.src||''),ok;
    if(!m){a3dToast('This frame shows no view yet');return false;}
    bimClbClose();
    ok=bimActivateView(m[1]==='plan'?'plan':(m[1]==='elevation'?'elev':'saved'),m[2]);
    if(ok)a3dToast('Working in the model on '+(fr.nm||m[2])+': the layout\'s tab brings it back');
    return ok;
  }
  /* the kinds the vector page draws */
  var BIM_LO_VECTOR={border:1,tblock:1,map:1,sched:1,rect:1,ellipse:1,line:1,text:1};
  /* a drawing layout as the sheet the vector page is drawn from: its frames as viewports, its schedules as theirs */
  function bimLoAsSheet(B){
    var pg=bimPgBoardPage(B),vps=[],tb=null;
    if(!pg)return null;
    (B.objs||[]).forEach(function(n){
      var v;
      if(n.t==='map'){v=bimLmFrameToVp({id:n.id,src:n.src,label:n.nm||'',x:n.x,y:n.y,w:n.w,h:n.h,den:n.den,fit:false});v.pan=[n.px||0,n.py||0];v.scaleMode='ratio';vps.push(v);}
      else if(n.t==='sched')vps.push({id:n.id,kind:'schedule',refId:n.src,label:n.ttl||'',x:n.x,y:n.y,w:n.w,h:n.h,scaleMode:'fit',scaleDenom:100});
      else if(n.t==='tblock')tb=n;
    });
    return {id:B.id,number:tb&&tb.num?tb.num:(B.num||''),name:B.name||'',w:pg.w,h:pg.h,viewports:vps};
  }
  /* its shapes and text as SVG, millimetres, as the board draws them */
  function bimLoShapesSvg(B){
    var s='';
    (B.objs||[]).forEach(function(n){
      var st=' fill="'+(n.fill&&n.fill!=='none'?n.fill:'none')+'"'+(n.fop!=null&&n.fop<1?' fill-opacity="'+n.fop+'"':'')+
        ' stroke="'+(n.stroke&&n.stroke!=='none'?n.stroke:'none')+'" stroke-width="'+bimLmN(n.sw||0)+'"';
      if(n.t==='rect')s+='<rect x="'+bimLmN(n.x)+'" y="'+bimLmN(n.y)+'" width="'+bimLmN(n.w)+'" height="'+bimLmN(n.h)+'" rx="'+bimLmN(n.r||0)+'"'+st+'/>';
      else if(n.t==='ellipse')s+='<ellipse cx="'+bimLmN(n.x+n.w/2)+'" cy="'+bimLmN(n.y+n.h/2)+'" rx="'+bimLmN(n.w/2)+'" ry="'+bimLmN(n.h/2)+'"'+st+'/>';
      else if(n.t==='line')s+='<line x1="'+bimLmN(n.x)+'" y1="'+bimLmN(n.y)+'" x2="'+bimLmN(n.x+n.w)+'" y2="'+bimLmN(n.y+n.h)+'"'+st+'/>';
      else if(n.t==='text'){
        var fs=(n.fs||14)*25.4/96,x=n.al==='center'?n.x+n.w/2:(n.al==='right'?n.x+n.w:n.x),a=n.al==='center'?'middle':(n.al==='right'?'end':'start');
        String(n.s||'').split('\n').forEach(function(line,i){
          s+='<text x="'+bimLmN(x)+'" y="'+bimLmN(n.y+fs*(1.1+i*1.25))+'" font-size="'+bimLmN(fs)+'" font-weight="'+(n.fw===700?700:400)+'" text-anchor="'+a+'" fill="'+(n.col||'#0b0b0b')+'">'+bimEscXml(line)+'</text>';
        });
      }
    });
    return s;
  }
  /* the vector page of a drawing layout, or null (with why) when it holds a kind the vector page does not draw */
  function bimLoLayoutSvg(B,mode){
    var S,bad=[];
    if(!B||!B.drawing)return {why:'not a drawing layout'};
    (B.objs||[]).forEach(function(n){if(!BIM_LO_VECTOR[n.t]&&bad.indexOf(n.t)<0)bad.push(n.t);});
    if(bad.length)return {why:'it holds '+bad.map(function(t){return (bimBobKind(t)||['',t])[1].toLowerCase();}).join(', ')+', which the vector page does not draw yet'};
    S=bimLoAsSheet(B);
    if(!S)return {why:'it has no page'};
    return {svg:bimBuildSheetSVG(S,mode,bimLoShapesSvg(B)),w:S.w,h:S.h};
  }
  /* Print, from the board's bar: a drawing layout as one vector page; anything else as a board prints */
  function bimLoPrint(B){
    var r=bimLoLayoutSvg(B,A3D.presentMode?'presentation':'technical'),w;
    if(r.why){if(B&&B.drawing)a3dToast('Printed as a board prints: '+r.why);return false;}
    w=window.open('','_blank');
    if(!w){a3dToast('The print window was blocked -- allow pop-ups for this page and try again');return true;}
    w.document.write('<html><head><title>'+bimEsc(bimLyLabel(B.num||'',B.name||''))+'</title><style>@page{size:'+r.w+'mm '+r.h+'mm;margin:0}'+
      'body{margin:0}svg{width:'+r.w+'mm;height:'+r.h+'mm;display:block}</style></head><body>'+r.svg+
      '<script>window.onload=function(){window.focus();window.print();};<\/script></body></html>');
    w.document.close();
    a3dToast('Printing '+bimLyLabel(B.num||'',B.name||'')+' as one vector page -- Save as PDF in the print dialog makes a PDF');
    return true;
  }
export { bimLoDrawKinds, bimLoLayoutSvg, bimLoOpenSheet, bimLoPrint, bimLoWorkIn };
