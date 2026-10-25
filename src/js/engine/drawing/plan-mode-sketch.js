  // ---- __acad3dV4: Snaptrude-style 2D plan mode + sketch + Pad/Pocket ----
  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',xline:'Construction line',boundary:'Boundary',hatch:'Hatch',poly:'Polyline',wall:'Wall',column:'Column',door:'Door',window:'Window',room:'Room',roof:'Roof',stair:'Stair',dim:'Dimension',text:'Text',section:'Section',mirror:'Mirror',rotate:'Rotate',polararray:'Polar Array',familyplace:'Place Family',ceiling:'Ceiling',dimangular:'Angular Dim',dimradius:'Radius Dim',dimdiameter:'Diameter Dim',leader:'Leader',roomtag:'Tag Room',footing:'Isolated Footing',wallfoundation:'Wall Foundation',foundslab:'Foundation Slab'};
  var A3D_SNAP={point:true,grid:false,gridSize:0.5,ortho:false,pxThreshold:12};
  /* __acad3dV67: BIM status bar read-outs. Every field here reflects state the BIM engine
     actually owns -- A3D.sk, A3D.sel/selSet, A3D.levels/activeLevel, A3D_SNAP -- which is the
     whole reason the 2D bar could not simply be shown in this mode. */
  function bimStatusHintText(){
    var sk=A3D.sk,o,n;
    if(bimSheetOnScreen()){   /* __acad3dV116 */
      if(A3D_PAGES.display==='pages')   /* __acad3dV122: from the table the keys are read from */
        return 'Pages: scroll, or '+bimPageKeyWords('next')+' and '+bimPageKeyWords('prev')+' to turn a page; double-click a page to edit its layout';
      if(A3D.sheetActiveVp){
        var avs=bimSheetVp(bimSheetById(A3D.activeSheetId),A3D.sheetActiveVp);
        return 'Model space in '+((avs&&avs.label)||'the viewport')+': drag to pan, wheel for the next scale, double-click outside or Escape for paper space';
      }
      return 'Paper space: drag a viewport to move it, its corner to size it, double-click it to work in it';
    }
    if(sk){
      /* __acad3dV86: the AutoCAD prompt, plus whatever is being typed -- the command line is
         where a drafter looks to find out what the tool will accept next. */
      var pr=bimPromptFor(sk);
      if(A3D_TYPING.active)pr+='  '+A3D_TYPING.buf;
      return pr;
    }
    /* __acad3dV123: PRESSPULL waiting for its click; a held face and what it takes */
    if(A3D.facePick)return 'PRESSPULL: click a face to push or pull it, or Esc to cancel';
    var fcur=A3D.face?bimFaceCurrent():null;
    if(fcur)return bimFaceHint(fcur);
    /* __acad3dV123: the handle under the cursor, and what it does -- set by onHover, cleared the
       moment the cursor leaves it */
    if(A3D.gizHover&&A3D.gizHoverHint&&!drag&&A3D.gizmo)return A3D.gizHoverHint;
    n=(A3D.selSet&&A3D.selSet.length)||0;
    if(n>1)return n+' objects selected';
    if(A3D.sel){
      o=objById(A3D.sel);
      /* bimObjTypeLabel is the Revit-shaped "Family : Type" string the Properties palette
         header already uses ("Walls : Generic - 300mm"). o.t is the internal primitive kind
         ('solid'), which is true but tells the user nothing about what they selected. */
      if(o)return o.name+'  \u00b7  '+bimObjTypeLabel(o)+
        (bimFaceObjKind(o)?'  \u00b7  drag to move it, double-click a face to push or pull':'');   /* __acad3dV123 */
    }
    var sgH=bimSelectedGrid();   /* __acad3dV98 */
    if(sgH)return 'Grid '+sgH.name+'  \u00b7  Grids : Grid';
    return 'Ready';
  }
  function bimSyncStatusHint(){
    if(!el.sthint)return;
    el.sthint.textContent=bimStatusHintText();
  }
  function bimSyncStatusLevel(){
    if(!el.stlevel)return;
    var h='',i,lv;
    for(i=0;i<A3D.levels.length;i++){
      lv=A3D.levels[i];
      h+='<option value="'+bimEsc(lv.id)+'"'+(lv.id===A3D.activeLevel?' selected':'')+'>'+
        bimEsc(lv.name)+'</option>';
    }
    if(el.stlevel.innerHTML!==h)el.stlevel.innerHTML=h;
    el.stlevel.value=A3D.activeLevel;
  }
  function bimStatusCoordText(g){
    if(!g)return '\u2014';
    /* World axes here are X / Z on the ground plane with Y up; the bar reports them as the
       plan X / Y a drafter expects, and the third figure is the ACTIVE LEVEL's elevation,
       which is the plane the point was actually solved on -- not the cursor's own height. */
    return 'X '+g[0].toFixed(3)+'   Y '+g[2].toFixed(3)+'   Z '+(bimGetActiveLevel().elev).toFixed(3);
  }
  function bimStatusHover(ev){
    if(!el.stcoords)return;
    var xy=cvXY(ev);
    var g=groundPoint(xy[0],xy[1],bimGetActiveLevel().elev);
    el.stcoords.textContent=bimStatusCoordText(g);
  }
  function bimStatusHoverOut(){
    if(el.stcoords)el.stcoords.textContent='\u2014';
  }
  function bimSyncStatusBar(){
    bimSyncStatusHint();
    bimSyncStatusLevel();
    bimRenderLayoutTabs();   /* __acad3dV116 */
  }
  function syncSnapPill(){
    bimSyncStatusHint();
    if(!el.snappill)return;
    var btns=el.snappill.querySelectorAll('[data-a3dsnap]'),i;
    for(i=0;i<btns.length;i++){
      var s=btns[i].getAttribute('data-a3dsnap');
      var on=(s==='point'&&A3D_SNAP.point)||(s==='ortho'&&A3D_SNAP.ortho)||(s==='grid'&&A3D_SNAP.grid);
      btns[i].classList.toggle('on',!!on);
    }
  }
  /* __acad3dV60: Phase 52a pill button label/state, same idiom as el.flip's own 2D/3D label. */
  function bimSyncPresentPill(){
    bimPagesStale();   /* __acad3dV122: every change of appearance passes here, and a page is drawn in it */
    if(!el.present)return;
    el.present.textContent=A3D.presentMode?'Pres':'Tech';
    el.present.classList.toggle('on',!!A3D.presentMode);
    el.present.setAttribute('title',A3D.presentMode?
      'Presentation appearance is ON — click for Technical (Phase 51 graphic overrides)':
      'Technical appearance — click for Presentation (Phase 51 graphic overrides)');
  }
  var A3D_TYPING={active:false,buf:''};
  /* __acad3dV75: THE WORLD-OFFSET INVARIANT, in one place.

     An object's world geometry is its LOCAL geometry plus o.pos. That was already true of the
     solid renderer and of rooms, and quietly false everywhere else -- grips, sketch drawing,
     sketch picking, marquee and snapping each read local points and drew them as if they were
     world points. A wall moved 4m by 3m left its grips 135px from the wall; a sketch moved 5m
     did not move on screen at all, still picked at its old position and not at its new one.

     Both helpers are deliberately tolerant of a missing or short pos array: objects created
     before pos existed, and objects restored from an older saved project, must not throw here --
     this runs inside paint(), and an exception in paint() takes the whole viewport down. */
  function bimObjOffset(o){
    if(!o||!o.pos)return [0,0,0];
    return [o.pos[0]||0,o.pos[1]||0,o.pos[2]||0];
  }
  /* A local PLAN point [x,z] at local elevation y, as a world [x,y,z] triple ready for
     toScreen(). Plan points and world triples are shaped differently, which is exactly why the
     offset kept being dropped when one was converted to the other by hand. */
  function bimWorldPt(o,p,y){
    var q=bimObjOffset(o);
    return [p[0]+q[0],(y||0)+q[1],p[1]+q[2]];
  }
  /* The world elevation of an object's own plan plane -- what groundPoint() has to be given to
     un-project a cursor onto that plane. */
  function bimWorldElev(o,y){return (y||0)+bimObjOffset(o)[1];}
  function bimSnapCandidates(y0,skip){
    /* __acad3dV112: skip is a list of object ids to leave out -- what is being dragged cannot be
       its own snap target, or a drag would lock onto the position it started from. */
    var pts=[],i,o,j;
    /* Grid datums span every level, so their nodes are snap targets at any elevation. */
    try{
      var gp=bimGridSnapPoints();
      for(i=0;i<gp.length;i++)pts.push(gp[i]);
    }catch(eG){console.warn('[BIM] Grid snap candidates unavailable',eG);}
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(skip&&skip.indexOf(o.id)>=0)continue;   /* __acad3dV112 */
      if(!bimLayerShown(o))continue;   /* __acad3dV121: a hidden layer's corners were snap targets */
      /* __acad3dV75: candidates are WORLD plan points, and the elevation they are filtered by is
         the object's world elevation. Before this, a moved wall went on offering snap points at
         the position it no longer occupied -- so the snap actively pulled new geometry to the
         wrong place, which is worse than no snap at all. */
      var q=bimObjOffset(o);
      if(o.t==='sketch'&&Math.abs((o.y||0)+q[1]-y0)<0.05){
        for(j=0;j<o.pts.length;j++)pts.push([o.pts[j][0]+q[0],o.pts[j][1]+q[2]]);
      }else if(o.t==='solid'&&o.bim&&o.bim.centerline&&Math.abs((o.bim.baseY||0)+q[1]-y0)<0.05){
        for(j=0;j<o.bim.centerline.length;j++)
          pts.push([o.bim.centerline[j][0]+q[0],o.bim.centerline[j][1]+q[2]]);
      }else if(bimIsCline(o)&&Math.abs((o.y||0)+q[1]-y0)<0.05){
        /* __acad3dV94: the root. It is the one point on an infinite line that means anything,
           and it is the one a drafter comes back to. */
        pts.push([o.p[0]+q[0],o.p[1]+q[2]]);
      }
    }
    /* __acad3dV94: and where the construction lines CROSS things, which is the whole reason to
       draw one. Gathered after the vertices so a crossing never displaces a real corner that
       sits at the same distance. */
    try{
      var cl=bimClinesOnPlane(y0),ci,cj,hits,hk;
      for(ci=0;ci<cl.length;ci++){
        var C=cl[ci];
        for(j=0;j<A3D.objs.length;j++){
          var t=A3D.objs[j];
          if(bimIsCline(t)||!bimLayerShown(t))continue;   /* __acad3dV121 */
          var tq=bimObjOffset(t),src=null;
          if(t.t==='sketch'&&t.pts&&t.pts.length>=2&&Math.abs((t.y||0)+tq[1]-y0)<0.05)
            src={pts:t.pts,bulges:t.bulges||null,closed:t.closed!==false};
          else if(t.t==='solid'&&t.bim&&t.bim.centerline&&t.bim.centerline.length>=2&&
                  Math.abs((t.bim.baseY||0)+tq[1]-y0)<0.05)
            src={pts:t.bim.centerline,bulges:t.bim.bulges||null,closed:!!t.bim.closed};
          if(!src)continue;
          var moved=src.pts.map(function(p){return [p[0]+tq[0],p[1]+tq[2]];});
          hits=bimClineCrossings(C.p,C.dir,C.ray,moved,src.bulges,src.closed);
          for(hk=0;hk<hits.length;hk++)pts.push(hits[hk]);
        }
        /* Two construction lines crossing is the classic setup-out point. */
        for(cj=ci+1;cj<cl.length;cj++){
          var D=cl[cj];
          var seg=bimClipInfinite(D.p,D.dir,false,bimDrawingExtent2D());
          if(!seg)continue;
          var x2=bimClineSegIntersect(C.p,C.dir,C.ray,seg[0],seg[1]);
          if(x2&&(!D.ray||bimClinePointAhead(D,x2)))pts.push(x2);
        }
      }
    }catch(eX){console.warn('[BIM] Construction-line snap candidates unavailable',eX);}
    return pts;
  }
  /* __acad3dV94: the construction lines sitting on one plan elevation, already offset into
     world coordinates so every caller works in the same space. */
  function bimClinesOnPlane(y0){
    var out=[],i,o,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      q=bimObjOffset(o);
      if(Math.abs((o.y||0)+q[1]-y0)>0.05)continue;
      out.push({id:o.id,p:[o.p[0]+q[0],o.p[1]+q[2]],dir:[o.dir[0],o.dir[1]],ray:!!o.ray});
    }
    return out;
  }
  function bimClinePointAhead(C,pt){
    if(!C.ray)return true;
    return (pt[0]-C.p[0])*C.dir[0]+(pt[1]-C.p[1])*C.dir[1]>=-1e-9;
  }
  function bimSnapPoint(xy,gRaw,sk){
    var px=gRaw[0],pz=gRaw[2],snapped=false;
    if(A3D_SNAP.point){
      var V=camVecs(A3D.cam),W=cvW(),H=cvH();
      var cands=bimSnapCandidates(sk.y),k;
      for(k=0;k<sk.pts.length;k++)cands.push(sk.pts[k]);
      var best=null,bestD=A3D_SNAP.pxThreshold;
      for(k=0;k<cands.length;k++){
        var c=cands[k];
        var sp=toScreen([c[0],sk.y,c[1]],V,W,H);
        var dx=sp[0]-xy[0],dy=sp[1]-xy[1],d=Math.sqrt(dx*dx+dy*dy);
        if(d<bestD){bestD=d;best=c;}
      }
      if(best){px=best[0];pz=best[1];snapped=true;}
    }
    if(!snapped&&A3D_SNAP.grid&&A3D_SNAP.gridSize>0){
      px=Math.round(px/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
      pz=Math.round(pz/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
    }
    if(A3D_SNAP.ortho&&sk.pts.length&&!snapped){
      var last=sk.pts[sk.pts.length-1];
      var ddx=px-last[0],ddz=pz-last[1];
      if(Math.abs(ddx)>=Math.abs(ddz))pz=last[1];else px=last[0];
    }
    return [px,pz,snapped];
  }
  function bimCommitTypedLength(len){
    var sk=A3D.sk;
    if(!sk||!sk.pts.length){a3dToast('Click a start point first, then type a length');return;}
    var dir=sk.liveDir||[1,0];
    var last=sk.pts[sk.pts.length-1];
    var nx=last[0]+dir[0]*len,nz=last[1]+dir[1]*len;
    if(sk.pts.length>=3){
      var d0x=nx-sk.pts[0][0],d0z=nz-sk.pts[0][1];
      if(Math.sqrt(d0x*d0x+d0z*d0z)<0.09){
        if(sk.tool==='wall')finishWall(true);else finishPoly();
        return;
      }
    }
    sk.pts.push([nx,nz]);
    paint();
  }
  var UNDO_STACK=[],REDO_STACK=[],UNDO_MAX=50,undoSuspend=false;
  function bimSnapshotState(){
    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,grids:A3D.grids,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer,views:A3D.views,levelFilter:A3D.levelFilter,types:A3D.types,activeWallType:A3D.activeWallType,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,resultLayers:A3D.resultLayers||[],pres:A3D.pres||null});   /* __acad3dV148; __acad3dV162 */
  }
  /* __acad3dV164: held while a run of many steps is under way, after the one snapshot it takes */
  var bimUndoHold=false;
  function pushUndo(){
    if(undoSuspend||bimUndoHold)return;
    UNDO_STACK.push(bimSnapshotState());
    if(UNDO_STACK.length>UNDO_MAX)UNDO_STACK.shift();
    REDO_STACK.length=0;
  }
  function bimRestoreState(json){
    var st;
    try{st=JSON.parse(json);}catch(eR){console.warn('[BIM] Corrupted undo snapshot, ignoring.',eR);return false;}
    undoSuspend=true;
    A3D.objs=st.objs||[];
    A3D.levels=(st.levels&&st.levels.length)?st.levels:A3D.levels;
    A3D.grids=Array.isArray(st.grids)?st.grids:[];
    A3D.layers=(st.layers&&st.layers.length)?st.layers:A3D.layers;
    A3D.counts=st.counts||A3D.counts;
    A3D.activeLevel=st.activeLevel||A3D.activeLevel;
    A3D.activeLayer=st.activeLayer||A3D.activeLayer;
    A3D.views=st.views||[];
    /* __acad3dV119: the saved-view mark is not restored -- it follows the view on screen, which an
       undo does not change; a saved view the undo removed is let go of by bimViewSync */
    A3D.levelFilter=!!st.levelFilter;
    A3D.types=st.types||null;
    A3D.activeWallType=st.activeWallType||null;
    A3D.sheets=Array.isArray(st.sheets)?st.sheets:[];
    A3D.titleBlock=(st.titleBlock&&typeof st.titleBlock==='object')?st.titleBlock:{project:'',client:'',drawnBy:'',checkedBy:''};
    A3D.buildings=(Array.isArray(st.buildings)&&st.buildings.length)?st.buildings:A3D.buildings;
    A3D.activeBuilding=st.activeBuilding||A3D.activeBuilding;
    A3D.site=(st.site&&typeof st.site==='object')?st.site:A3D.site;
    A3D.roomScheme=(st.roomScheme==='dept'||st.roomScheme==='occupancy')?st.roomScheme:'';   /* __acad3dV105 */
    A3D.classifications=Array.isArray(st.classifications)?st.classifications:[];
    if(Array.isArray(st.resultLayers))A3D.resultLayers=st.resultLayers;   /* __acad3dV148: a version from History has none, and keeps today's */
    A3D.pres=bimPresValid(st.pres);   /* __acad3dV162: the set as it was */
    bimEnsureTypes();
    bimEnsureBuildings();
    A3D.sel=null;A3D.sel2=null;A3D.meshes={};
    if(A3D.sheetActiveVp&&!bimSheetVp(bimSheetById(A3D.activeSheetId),A3D.sheetActiveVp))A3D.sheetActiveVp=null;   /* __acad3dV116 */
    bimSyncActiveGlobal();
    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();bimSheetViewRefresh();paint();
    bimPresPanelRefresh();   /* __acad3dV162 */
    undoSuspend=false;
    return true;
  }
  function doUndo(){
    if(!UNDO_STACK.length){a3dToast('Nothing to undo');return;}
    REDO_STACK.push(bimSnapshotState());
    var st=UNDO_STACK.pop();
    if(bimRestoreState(st)){saveSoon();a3dToast('Undo');}
  }
  function doRedo(){
    if(!REDO_STACK.length){a3dToast('Nothing to redo');return;}
    UNDO_STACK.push(bimSnapshotState());
    var st=REDO_STACK.pop();
    if(bimRestoreState(st)){saveSoon();a3dToast('Redo');}
  }
  var PILL_PAN='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M7 11.5V7a1.4 1.4 0 0 1 2.8 0v3.2M9.8 10V5.4a1.4 1.4 0 0 1 2.8 0V10M12.6 10.2V6.4a1.4 1.4 0 0 1 2.8 0v5c0 3.6-2.1 5.8-5.2 5.8-2.3 0-3.7-1-4.8-3l-1.8-3.2c-.5-.9.6-1.8 1.4-1.1l2 1.8"/></svg>';
  var PILL_ORBIT='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3.4"/><ellipse cx="12" cy="12" rx="9.5" ry="4.2" transform="rotate(-25 12 12)"/></svg>';
  var PILL_SNAP='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 3v7a4 4 0 0 0 8 0V3"/><path d="M8 3H5v7a7 7 0 0 0 14 0V3h-3"/></svg>';
  var PILL_ORTHO='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 4v15h15"/><rect x="5" y="14" width="5" height="5"/></svg>';
  var PILL_PLAY='<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg>';   /* __acad3dV170 */
  var PILL_PAUSE='<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4.5" width="4.2" height="15" rx="0.8"/><rect x="13.8" y="4.5" width="4.2" height="15" rx="0.8"/></svg>';
  var PILL_STOP='<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><rect x="5.5" y="5.5" width="13" height="13" rx="1.2"/></svg>';
  var PILL_GRID='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/></svg>';
  var PILL_UNDO='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 10h9a5 5 0 0 1 0 10h-2"/><path d="M8 5 4 10l4 5"/></svg>';
  var PILL_REDO='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 10h-9a5 5 0 0 0 0 10h2"/><path d="M16 5l4 5-4 5"/></svg>';
  function objBBox(o){
    var m=meshOf(o);if(!m)return null;
    var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],j,k;
    for(j=0;j<m.v.length;j++)for(k=0;k<3;k++){
      var vv=m.v[j][k]+o.pos[k];
      if(vv<mn[k])mn[k]=vv;
      if(vv>mx[k])mx[k]=vv;
    }
    return {mn:mn,mx:mx};
  }
  function setNav(mode){
    A3D.navMode=mode;
    if(el.pill){
      var bs=el.pill.querySelectorAll('[data-a3dnav]'),i;
      for(i=0;i<bs.length;i++){
        var a=bs[i].getAttribute('data-a3dnav');
        if(a==='pan'||a==='orbit')bs[i].classList.toggle('on',a===mode);
      }
    }
  }
  function toggleFlat(){
    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a view change used to discard the drawing */
    if(A3D.flat){
      A3D.flat=false;
      var c=A3D.cam;
      if(A3D.prevCam){c.yaw=A3D.prevCam.yaw;c.pitch=A3D.prevCam.pitch;}
      A3D.view=A3D.prevView||'Home';
    }else{
      A3D.prevCam={yaw:A3D.cam.yaw,pitch:A3D.cam.pitch};
      A3D.prevView=A3D.view;
      A3D.flat=true;
      A3D.cam.yaw=0;A3D.cam.pitch=1.52;
      A3D.view='Plan';
    }
    if(el.flip){
      el.flip.textContent=A3D.flat?'3D':'2D';
      el.flip.setAttribute('title',A3D.flat?'Go to 3D (>)':'Go to 2D (>)');
    }
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    /* __acad3dV119: the switch is a view switch like any other, and records one. The status bar's
       3D / 2D, the '>' key and every drafting tool that drops a 3D view to the plan went around the
       record, so the HUD went on naming the view before -- as the Project Browser's mark and the
       Properties View row had since V84. A saved view is left, as any view switch leaves it. On a
       sheet the switch turns the model's camera behind the paper, and the sheet is still the view. */
    if(A3D_VIEW.kind!=='sheet')bimSetActiveView(A3D.flat?'plan':'3d',A3D.flat?A3D.activeLevel:null,null);
    else refreshHud();
    paint();saveSoon();
  }
  // ---- __acad3dV18: drafting-mode entry hardening. Drafting/annotation is fundamentally a
  // 2D-plane operation -- every tool that draws by clicking points needs to be on a flat
  // (orthographic) plane, not in 3D perspective. Every such tool used to call
  // "if(!A3D.flat)toggleFlat();" directly, which had a real gap: if a Section view was active
  // (which is ALSO flat=true, but a vertical cut view, not a top-down plan), starting another
  // drafting tool would silently skip toggleFlat (since A3D.flat was already true) and try to
  // place points against the section's horizontal camera -- groundPoint's near-horizontal guard
  // (see the Elevations/groundPoint fix) would then just silently decline every click, a
  // confusing "nothing happens" experience. This routes every drafting tool through one place. ----
  function bimEnterDraftingMode(){
    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a new command ends the old one, keeping it */
    if(A3D.section)bimExitSection();
    if(!A3D.flat)toggleFlat();
    else if(!bimCameraIsPlan())bimActivateView('plan',null,{anim:false});   /* __acad3dV119: an elevation is flat too */
  }
  /* __acad3dV93: a point is a sketch by storage and not by nature. Pad, Pocket and the
     sketch-constraint panel all reach the selection through here, so excluding it once keeps
     every one of them from offering an operation a node cannot carry. */
  function selSketch(){
    var o=objById(A3D.sel);
    return (o&&o.t==='sketch'&&!bimIsPoint(o))?o:null;
  }
  function cancelSketch(){A3D.sk=null;paint();}
