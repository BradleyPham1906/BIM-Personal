  /* __acad3dV72: the canvas has TWO sizes and the code had been using one of them for both
     jobs. el.cv.width/height is the BACKING STORE in device pixels; cvW()/cvH() are the
     LOGICAL size in CSS pixels, which is the space cvXY() -- and therefore every mouse event --
     lives in. Mixing them is what put the first click off the cursor.

     The divisor is stored on the canvas ELEMENT rather than read from A3D, because sheet
     capture swaps el.cv for a scratch canvas that is already 1:1 (see bimRenderViewportTo).
     A scratch canvas carries no __a3dScale, so it divides by 1 and behaves exactly as it did
     before this phase -- no capture path has to know that screen rendering is now scaled. */
  function cvScale(c){return (c&&c.__a3dScale)||1;}
  function cvW(){return el.cv?el.cv.width/cvScale(el.cv):0;}
  function cvH(){return el.cv?el.cv.height/cvScale(el.cv):0;}
  function bimDevicePixelRatio(){
    var d=window.devicePixelRatio||1;
    if(!isFinite(d)||d<=0)d=1;
    /* Capped at 3. Past that the backing store grows as the square for no visible gain, and a
     * 4x phone would be allocating ~50MB for one viewport. */
    return Math.min(3,Math.max(1,d));
  }
  function size(){
    var vp=el.root.querySelector('.a3d-vp');
    if(!vp||!el.cv)return;
    var dpr=bimDevicePixelRatio();
    var wCss=vp.clientWidth,hCss=vp.clientHeight;
    var wDev=Math.max(1,Math.round(wCss*dpr)),hDev=Math.max(1,Math.round(hCss*dpr));
    /* Assigning width/height clears the canvas even when the value is unchanged, so both are
       guarded -- a ResizeObserver that fires on every layout pass would otherwise blank the
       drawing between frames. */
    if(el.cv.width!==wDev)el.cv.width=wDev;
    if(el.cv.height!==hDev)el.cv.height=hDev;
    el.cv.__a3dScale=dpr;
    bimSyncGlCanvasSize();
    paint();
  }
  /* __acad3dV72: size() used to be called from exactly two places -- a window resize and once
     on entering the workspace. Every other thing that resizes the viewport (collapsing the file
     dock, opening the inspector, the status bar appearing, a discipline change reflowing the
     shell) left the backing store stale and the cursor mapping wrong. Observing the element is
     the fix for the CLASS of bug; chasing each layout change individually is not. */
  var A3D_VP_OBS=null;
  function bimObserveViewport(){
    if(A3D_VP_OBS||typeof ResizeObserver==='undefined')return;
    var vp=el.root&&el.root.querySelector('.a3d-vp');
    if(!vp)return;
    A3D_VP_OBS=new ResizeObserver(function(){if(A3D.on)size();});
    A3D_VP_OBS.observe(vp);
  }
  function enter3d(){
    buildUI();
    if(A3D.on)return;
    A3D.on=true;
    window.__a3dOn=true;
    el.root.classList.add('on');
    /* __acad3dV65: ONE left column, not two. The Project Browser tree is NESTED INSIDE the left
       panel, so the rail's sections and the BIM navigator stack in a single column -- the shape
       every comparable tool uses (a narrow rail selecting a panel; stacked sections within it).

       Moving the node is safe here, and that was verified rather than assumed before doing it:
         - every tree child is resolved ONCE at buildUI() time into el.* (el.propsbody, el.browser,
           ...), and a JS element reference stays valid when the node is re-parented;
         - all five tree listeners are bound DIRECTLY to those nodes, not delegated from #acad3d,
           so they travel with the node (a delegated listener on the old ancestor would not);
         - no CSS rule scopes the tree's classes under #acad3d -- they are all bare .a3d-tree /
           .a3d-palhd / .a3d-prow selectors -- so its styling is unaffected by the new parent.
       If any of those three had been false this would have had to be done a different way. */
    try{
      bimBuildShell();   /* __acad3dV113b */
      var shellEl=document.getElementById('a3d-shell');
      var panelEl=document.getElementById('a3d-leftpanel');
      var tree=el.root&&el.root.querySelector('.a3d-tree');
      if(panelEl&&tree&&tree.parentNode!==panelEl){
        panelEl.appendChild(tree);
        document.body.classList.add('a3d-tree-docked');
      }
      setTimeout(function(){try{bimTPalPlace();bimTPalSync();}catch(eTP){}},0);   /* __acad3dV150: the palette over the drawing */
      if(shellEl&&shellEl.classList.contains('collapsed')&&!bimShellOverlay()){   /* __acad3dV149: a drawer stays shut */
        // the panel hosts the BIM navigator, so it opens on entry
        shellEl.classList.remove('collapsed');
      }
      bimShellDockW();
    }catch(eDock){console.warn('[BIM] Could not nest the Project Browser into the left panel; it stays in the shell\'s own pane.',eDock);}
    /* the class the rest of the stylesheet keys this workspace on */
    try{
      document.body.classList.add('a3d-mode');
    }catch(eDp){console.warn('[BIM] Could not mark the page as the BIM workspace.',eDp);}
    /* __acad3dV68: Properties moves to the right inspector. Deliberately its OWN try block,
       not folded into the nesting one above: if the left panel is missing the navigator
       falls back to the shell's own left pane, and the inspector should still be on the right
       -- one failure should not drag the other layout back to the pre-V68 shape. */
    try{
      /* NOT el.root.querySelector: the dock-nesting block above has already moved the whole
         .a3d-tree (and this section inside it) OUT of el.root and into #a3d-leftpanel, so
         a shell-scoped lookup returns null here and the move silently does nothing. */
      var propsSec=document.getElementById('a3d-propssec');
      var rightPane=el.root&&el.root.querySelector('#a3d-right');
      if(propsSec&&rightPane&&propsSec.parentNode!==rightPane){
        rightPane.appendChild(propsSec);
        document.body.classList.add('a3d-props-right');
      }
      try{bimRightWire(rightPane,propsSec);}catch(eRw){console.warn('[BIM] The Properties panel could not be made resizable.',eRw);}   /* __acad3dV147 */
    }catch(eRight){console.warn('[BIM] Could not move Properties to the right inspector; it stays in the left column.',eRight);a3dToast('Properties panel could not be docked right');}
    /* __acad3dV70: the dock is the tool surface in this workspace now. Built on entry rather
       than at buildUI time so it always reflects the current A3DR_TABS, and bound once. */
    try{
      bimBuildDock();bimBindDock();
    }catch(eDock2){console.warn('[BIM] Could not build the tool dock.',eDock2);a3dToast('The tool dock could not be built; the command palette (Ctrl+K) still runs every command');}   /* __acad3dV120 */
    size();
    bimObserveViewport();
    bimWireOcclusionNotice();   // __acad3dV79
    bimWatchShell();            // __acad3dV80
    bimSyncActiveGlobal();
    refreshTree();refreshHud();refreshLevels();refreshLayers();paint();
    /* __acad3dV67: populate the status bar on entry. refreshLevels/refreshTree above already
       feed it, but syncSnapPill is only called on a toggle, so without this the three snap
       buttons would render in their markup default state rather than A3D_SNAP's real state --
       a bar that lies on the first frame is worse than no bar. */
    bimSyncStatusBar();syncSnapPill();
  }

  window.__a3dEnter=enter3d;
  window.__a3dAdd=add3d;
  window.__a3dDel=del3d;
  window.__a3dPick=function(x,y){var o=pick(x,y);return o?o.id:null;};
  window.__a3dFit=fitScene;
  window.__a3dOpenDlg=openDlg;
  window.__a3dSetView=function(n,anim){setView(n,anim===undefined?false:anim);};
  /* __acad3dV119: where the ViewCube's faces and its Home button are on the page, for a suite to
     click with the mouse. Empty while the cube is not drawn. */
  window.__a3dCubeFaces=function(){
    var r=el.cv?el.cv.getBoundingClientRect():null,out=[],i,j,p,sx,sy;
    if(!r)return out;
    for(i=0;i<A3D.cubePolys.length;i++){
      p=A3D.cubePolys[i].pts;sx=0;sy=0;
      for(j=0;j<p.length;j++){sx+=p[j][0];sy+=p[j][1];}
      out.push({n:A3D.cubePolys[i].n,x:r.left+sx/p.length,y:r.top+sy/p.length});
    }
    if(A3D.homeRect)out.push({n:'home',x:r.left+A3D.homeRect[0]+A3D.homeRect[2]/2,y:r.top+A3D.homeRect[1]+A3D.homeRect[3]/2});
    return out;
  };
  window.__a3dProject=function(pos){
    var V=camVecs(A3D.cam);
    var p=toScreen(pos,V,cvW(),cvH());
    /* __acad3dV111: w is the depth toScreen already computes -- distance along the view direction
       in a perspective view, and the same measure flattened in an orthographic one. Published so a
       suite can say which of two points is nearer the camera without being told. */
    return {x:p[0],y:p[1],w:p[2]};
  };
  window.__a3dBool=function(kind,ida,idb){if(ida)A3D.sel=ida;if(idb)A3D.sel2=idb;return doBool(kind);};
  window.__a3dSetPos=function(id,x,y,z){var o=objById(id);if(!o)return false;o.pos=[x,y,z];paint();saveSoon();return true;};
  window.__a3dFlat=function(on){
    /* __acad3dV119: with no argument this is a question, and a question changes nothing. It read as
       "flat: false" and turned a plan into 3D -- which __a3dShellGeom did on every call, to find out
       which mode it was in. */
    if(on!==undefined&&!!on!==A3D.flat)toggleFlat();
    return A3D.flat;
  };
  window.__a3dSketch=function(tool,pts){
    startSketch(tool);
    if(!A3D.sk)return null;
    A3D.sk.pts=(pts||[]).slice();
    var o=null;
    if(tool==='rect')o=finishRect();
    else if(tool==='circle')o=finishCircle();
    else o=finishPoly();
    return o?A3D.sel:null;
  };
  window.__a3dPad=function(h){
    var s=selSketch();if(!s)return null;
    var o=doPad(s,h);
    return o?o.id:null;
  };
  window.__a3dPocket=function(dp){
    var s=selSketch();if(!s)return null;
    var o=doPocket(s,dp);
    return o?o.id:null;
  };
  window.__a3dState=function(){
    return JSON.parse(JSON.stringify({on:A3D.on,sel:A3D.sel,sel2:A3D.sel2,view:A3D.view,frames:A3D.frames,cam:A3D.cam,objs:A3D.objs,flat:A3D.flat,nav:A3D.navMode,sk:A3D.sk?{tool:A3D.sk.tool,y:A3D.sk.y,on:A3D.sk.on,pts:A3D.sk.pts.length}:null,sheets:A3D.sheets,activeLevel:A3D.activeLevel,activeViewId:A3D.activeViewId,section:!!A3D.section,viewKind:A3D_VIEW.kind,viewName:A3D_VIEW.name}));
  };
  window.__acad3dV1='viewport,orbit,pan,zoom,viewcube,primitives,tree,persist';
  window.__acad3dV2='ribbon,params,tube,prism,wedge,ellipsoid,integrated';
  window.__acad3dV3='csg,union,cut,intersect,sel2,dragmove';
  window.__acad3dV4='plan2d,pill,shiftgt,sketch,rect,circle,poly,pad,pocket,ortho';
  window.__acad3dV5='bimlevels,activelevel,parametricwall,wallalign,structuralfloor,walluniontocsg,persistlevels';
  window.__acad3dV42='leveldatum,gridsnap,beamengine,gridbubbles,beamschedule';
  window.__acad3dV43='stairpath,multiflight,stairlandings,turnmiter,steppedguardrail,csgrailingunion';
  window.__acad3dV44='sheets,sheetviewports,titleblock,printsheet,schedulesviewport,sheetfit,sheetscale';
  window.__acad3dV45='sketchconstraints,coincident,horizontal,vertical,parallel,perpendicular,equal,distance,angle,constraintsolver,dofestimate';
  window.__a3dGrids=function(){return JSON.parse(JSON.stringify(A3D.grids));};
  window.__a3dAddGrid=function(p1,p2){var g=bimAddGrid(p1,p2);return g?g.id:null;};
  window.__a3dRemoveGrid=bimRemoveGrid;
  window.__a3dGridSnapPoints=bimGridSnapPoints;
  window.__a3dSegIntersect=bimSegIntersect;
  window.__a3dGridNextName=bimGridNextName;
  window.__a3dBeamGeometry=bimBuildBeamGeometry;
  window.__a3dBeam=function(p1,p2,w,dep,just){
    var lvl=bimGetActiveLevel(),top=lvl.elev;
    dep=dep||0.5;
    if(just==='center')top=lvl.elev+dep/2;else if(just==='bottom')top=lvl.elev+dep;
    var o=buildBeamSolid(p1,p2,top,w||0.25,dep);
    return o?o.id:null;
  };
  window.__a3dBeamSchedule=bimBuildBeamSchedule;
  window.__a3dObjectsOnLevel=function(id){return bimObjectsOnLevel(id).map(function(o){return o.id;});};
  window.__a3dShiftLevelContents=bimShiftLevelContents;
  window.__a3dUndo=doUndo;
  window.__a3dRedo=doRedo;
  /* __acad3dV50: dependency graph surface, for the Phase 55 browser tests and for any later
     phase that needs to reason about relationships without reaching into module internals. */
  window.__bimGraph={
    build:function(){
      var g=bimGraphBuild();
      if(!g)return null;
      var outPlain={},inPlain={},k;
      for(k in g.out){if(g.out.hasOwnProperty(k))outPlain[k]=g.out[k].slice();}
      for(k in g.in){if(g.in.hasOwnProperty(k))inPlain[k]=g.in[k].slice();}
      var kinds={};
      for(k in g.nodes){if(g.nodes.hasOwnProperty(k))kinds[k]=g.nodes[k].kind;}
      return {keys:Object.keys(g.nodes),kinds:kinds,out:outPlain,in:inPlain,edgeCount:g.edgeCount};
    },
    downstream:function(startKeys){
      var g=bimGraphBuild();
      if(!g)return null;
      return Object.keys(bimGraphDownstream(g,startKeys));
    },
    order:function(startKeys){
      var g=bimGraphBuild();
      if(!g)return null;
      var res=bimGraphTopoOrder(g,bimGraphDownstream(g,startKeys));
      return {order:res.order,cycle:res.cycle};
    },
    propagate:function(startKeys){
      var seen=[];
      var r=bimGraphPropagate(startKeys,function(node){seen.push(node.key);});
      r.seen=seen;
      return r;
    },
    relations:bimGraphRelationsOf,
    keyObj:bimGraphObjKey,
    keyLevel:bimGraphLevelKey,
    keyType:bimGraphTypeKey
  };
  window.__a3dAddLevel=addLevel;
  window.__a3dSetLevel=setActiveLevel;
  window.__a3dLevels=function(){return JSON.parse(JSON.stringify(A3D.levels));};
  window.__a3dActiveLevel=function(){return JSON.parse(JSON.stringify(bimGetActiveLevel()));};
  window.__a3dWall=function(pts,thk,hgt,align,closed){
    var lvl=bimGetActiveLevel();
    var o=buildWallSolid(pts,lvl.elev,hgt||lvl.height,thk||0.3,align||'center',!!closed);
    return o?o.id:null;
  };
  window.__a3dFloor=function(thk,mat){
    var prof=bimGetFloorProfile();
    if(!prof)return null;
    var o=buildFloorSolid(prof,thk||0.2,mat||'Concrete Slab',bimGetActiveLevel());
    return o?o.id:null;
  };
  window.__acad3dV6='layers,layervisibility,layerlock,importdxf,importobj,importstl,importifc,ifcstoreys,ifcwalls,ifcslabs';
  window.__acad3dV7='marqueeselect,windowcrossing,groupmove,groupdelete,duplicate,lineararray';
  window.__acad3dV8='touchinput,pinchzoom,touchpan,longpressmarquee,touchaimsketch,touchlenoverlay,elevationprop,responsivedrawer,scrollableribbon';
  window.__acad3dV9='miteredwallcorners,wallribbonmesh';
  window.__acad3dV10='roomtool,roomboundarydetect,roomarea,roomtag,nestedloopdetect';
  window.__acad3dV11='objectlockpin,importdefaultlocked,ifcwallparametricrecovery,crashfixwallcentline';
  window.__acad3dV12='rooftool,pitchedroof,stairtool,straightrunstair,weldedmeshconstruction';
  window.__acad3dV13='lineardimension,textlabel,pngexport,pdfexport,handrolledpdf';
  window.__acad3dV14='projectfilesave,projectfileload,jsonenvelopevalidation,ctrlSsave,countspersisted';
  window.__acad3dV15='orthographicelevations,groundpointfix';
  window.__acad3dV16='sectiontool,planeclipsectioncut,nondestructivecut,loopcapping,multiloopsupport';
  window.__acad3dV17='mirror,rotate,polararray,walljoin,generictransform';
  window.__acad3dV18='draftingmodehardening,sectioncamerarestorefix,annotateribbontab';
  window.__acad3dV19='schedules,roomschedule,doorschedule,windowschedule,wallschedule,columnschedule,csvexport';
  window.__acad3dV20='uipaneldropdown,panelvisibilitytoggle,uiprefspersistence';
  window.__acad3dV21='familylibrary,familyimport,familysaveas,familyplace,independentinstances';
  window.__acad3dV22='multiwallloopdetect,planarfacetracing,wallgroupboundary';
  window.__acad3dV23='savedviews,viewspecificannotations,levelfilter';
  window.__acad3dV24='dxfexport,ceilingtool';
  window.__acad3dV25='angulardim,radiusdim,diameterdim,leaders,dimkinddiscriminator';
  window.__acad3dV26='closepathkey,floorclickinside,browserverified';
  window.__acad3dV27='webglrenderer,gpusolids,perobjectbuffers,ondemandpicking';
  window.__acad3dV28='projectbrowser,collapsibletree,inlinelocktoggle,propertiespalette';
  window.__acad3dV29='canvasworkspace,threeworkspaces,tabfiltering';
  window.__acad3dV30='disciplinetabs,splitbuttondropdowns,unimplementedmarking';
  window.__acad3dV31='workspacetoolsetcleanup,canvasarrange,revitannotate,slimtoolbar';
  window.__acad3dV32='bimoffset,bimalign,objbounds2d';
  window.__acad3dV33='bimtrim,segintersect,polylinetruncate';
  window.__acad3dV34='navbarcleanup,caretalignment,dropdownzfix,fullicons';
  window.__acad3dV35='daisplanviewofmodel,singlenavbar,draftingtab,workspaceswitchfix';
  window.__acad3dV36='revitpropertiespalette,parametergroups,typeheader,browsersearch';
  window.__acad3dV37='revitviewcube,compassring,homeicon,topfacewindingfix';
  window.__acad3dV38='typesextendedtofloorceilingcolumn,generictypedialog,typemigration';
  window.__acad3dV39='straightskeletonroof,hipgable,tjunctionrepair,shedsidewindingfix';
  window.__a3dEnsureObjType=bimEnsureObjType;
  window.__a3dApplyTypeToInstances=bimApplyTypeToInstances;
  window.__a3dTypeCats=function(){return TYPE_CATS;};
  window.__acad3dV38='walltypes,typeinstanceparams,typepropagation,duplicatetype';
  window.__a3dWallTypes=function(){bimEnsureTypes();return A3D.types.wall;};
  window.__a3dApplyWallType=bimApplyWallTypeToInstances;
  /* Accepts an object or an object id, so callers and tests can use the same id-based style as
     every other hook here (bimSetWallTypeOf itself takes the object). */
  window.__a3dSetWallType=function(oOrId,typeId){
    var o=(typeof oOrId==='string')?objById(oOrId):oOrId;
    return bimSetWallTypeOf(o,typeId);
  };
  window.__a3dLiveWalls=function(){return A3D.objs.filter(function(o){return o.bim&&o.bim.type==='wall';}).map(function(o){return {name:o.name,thickness:o.bim.thickness,height:o.bim.height,typeId:o.bim.typeId};});};
  /* __acad3dV84: both of these open a view, so both go through the one activation path
     rather than keeping a second, slightly different copy of the camera logic. They are used
     by startup, where an animated camera would be wrong, so neither animates. */
  window.__a3dSetPlanView=function(){
    if(!bimActivateView('plan',A3D.activeLevel,{anim:false}))
      console.warn('[BIM] plan view switch failed');
  };
  window.__a3dSet3DView=function(){
    if(!bimActivateView('3d',null,{anim:false}))
      console.warn('[BIM] 3D view switch failed');
  };
  window.__a3dActiveView=function(){
    return {kind:A3D_VIEW.kind,id:A3D_VIEW.id,name:A3D_VIEW.name};
  };
  window.__a3dOpenView=function(kind,id,opts){return bimActivateView(kind,id,opts);};

