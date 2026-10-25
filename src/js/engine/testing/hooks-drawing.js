  /* __acad3dV87: the geometry core is exposed directly so the suite asserts on the POINTS a
     modify command produces, not on the picture drawn from them. */
  /* __acad3dV88: the arc core, exposed so the suite asserts on the stored bulge and the
     geometry it describes rather than on a rendered picture. */
  /* __acad3dV97 */
  window.__a3dSourceBoundaryWorld=function(id){var b=bimSourceBoundaryWorld(objById(id));return b;};
  window.__a3dFollowSource=function(id){var ctx={};var ok=bimFollowSource(objById(id),ctx);return {ok:ok,ctx:ctx};};
  window.__a3dSourceOf=function(id){var o=objById(id);return o?{id:bimGraphRoomSourceId(o),type:bimSourceTypeOf(o)}:null;};
  window.__a3dInsertSketchVertex=function(id,seg,pt){
    var o=objById(id);
    var r=bimInsertSketchVertex(o,seg,pt||(o?bimSketchSegMid(o,seg):null));
    if(!r.error)bimPropagateFrom([id],'rebuild');
    return r;
  };
  window.__a3dSketchSegMid=function(id,seg){var o=objById(id);return o?bimSketchSegMid(o,seg):null;};
  window.__acad3dV97='sourcecontract,everydependentfollows,dependentframe,cutsaysso,addvertex,constraintindexshift,chainedsources';
  /* __acad3dV98: annotations and grids can be touched and edited. */
  window.__a3dCreateAngularDim=bimCreateAngularDim;
  window.__a3dCreateRadialDim=bimCreateRadialDim;
  window.__a3dCreateLeader=bimCreateLeader;
  window.__a3dAnnotGripPoints=function(id){
    var o=objById(id),p=o?bimAnnotGripPoints(o):null;
    return p?JSON.parse(JSON.stringify(p)):null;
  };
  window.__a3dSelectedGrid=function(){var g=bimSelectedGrid();return g?g.id:null;};
  window.__a3dSelectGrid=bimSelectGrid;
  window.__a3dRenameGrid=bimRenameGrid;
  window.__a3dSetGridEnds=bimSetGridEnds;
  window.__a3dPickGrid=function(x,y){var g=bimPickGrid(x,y);return g?g.id:null;};
  window.__acad3dV98='edgesource,annotpickfirst,annotallkinds,annotgrips,gridselect,gridgrips,griddrag,griddelete,gridprops';
  /* __acad3dV99: region dependents. */
  window.__a3dRegenerateRegions=bimRegenerateRegions;
  window.__a3dIsRegionDep=function(id){return bimIsRegionDep(objById(id));};
  window.__a3dRegionOf=function(id){var o=objById(id);return (o&&o.region)?JSON.parse(JSON.stringify(o.region)):null;};
  window.__a3dFollowsText=function(id){return bimFollowsText(objById(id));};
  window.__a3dGraphRelationsOf=function(id){return bimGraphRelationsOf(id);};
  window.__a3dFloorOnRegionAt=function(pt,y,thk){
    var b=bimFindRoomBoundaryAt(pt,y||0);
    if(!b)return null;
    var o=buildFloorSolid(bimFloorProfileFrom(b),thk||0.2,'Concrete Slab',bimGetActiveLevel());
    return o?o.id:null;
  };
  window.__acad3dV99='regiondependent,regiontrace,regiongraph,regionregen,regionopen,legacywallgroup,deletedsource,followstext';
  window.__acad3dV100='escapekeeps,viewchangekeeps,newcommandkeeps,plineenteropen,plinetwopoints';
  /* __acad3dV101: room data and room tags. */
  window.__a3dTagRoomAt=function(pt){var t=bimTagRoomAt(pt);return t?t.id:null;};
  window.__a3dTagAllRooms=bimTagAllRooms;
  window.__a3dSetRoomField=function(id,k,v){return bimSetRoomField(objById(id),k,v);};
  window.__a3dNextRoomNumber=bimNextRoomNumber;
  window.__a3dRoomTagText=function(id){var o=objById(id);return o?bimRoomTagText(o):null;};
  window.__a3dRoomTagged=bimRoomTagged;
  window.__a3dRoomLabelPoint=function(id){var o=objById(id);return o?bimRoomLabelPoint(o):null;};
  window.__acad3dV101='roomdata,roomnumbering,roomtag,tagall,taglayout,tagfollowsmove,tagdeletedwithroom,orphansweep,exportlabels';
  /* __acad3dV102: structural foundations and the type catalogue. */
  window.__a3dAddFootingUnder=function(hostId){var f=bimAddFootingUnder(objById(hostId));return f?f.id:null;};
  window.__a3dFootingsUnderAll=bimFootingsUnderAllColumns;
  window.__a3dFootingOf=function(hostId){var f=bimFootingOf(hostId);return f?f.id:null;};
  window.__a3dFootingVolume=function(id){return bimFootingVolume(objById(id));};
  window.__a3dTypesOf=function(cat){bimEnsureTypes();return JSON.parse(JSON.stringify(A3D.types[cat]||[]));};
  window.__a3dAssignType=function(id,typeId){var o=objById(id);if(!o||!o.bim)return false;pushUndo();var ok=bimAssignTypeTo(o,o.bim.type,typeId);saveSoon();return ok;};
  window.__a3dApplyTypeParams=function(cat,typeId,params){
    var t=bimFindType(cat,typeId),k;if(!t)return null;pushUndo();
    for(k in params)if(params.hasOwnProperty(k))t.params[k]=params[k];
    var r=bimApplyTypeToInstances(cat,typeId);saveSoon();return r;};
  window.__a3dFoundationSlabAt=function(pt,y){var o=bimFoundationSlabAt(pt,y||0);return o?o.id:null;};
  window.__a3dRectFootprint=bimRectFootprint;
  /* __acad3dV103: site -- property lines, setbacks, true north. */
  window.__a3dParseBearing=bimParseBearing;
  window.__a3dFormatBearing=bimFormatBearing;
  window.__a3dParseLegs=bimParseLegs;
  window.__a3dTraverse=bimTraverse;
  window.__a3dLegsFromRing=bimLegsFromRing;
  window.__a3dSetbackRing=bimSetbackRing;
  window.__a3dPropertyGeometry=function(id){var o=objById(id);return bimIsProperty(o)?JSON.parse(JSON.stringify(bimPropertyGeometry(o))):null;};
  window.__a3dSetbackViolations=function(id){var o=objById(id);return bimIsProperty(o)?bimSetbackViolations(o).list:null;};
  window.__a3dPropertyFromSketch=function(id){var p=bimPropertyFromSketch(objById(id));return p?p.id:null;};
  window.__a3dSetTrueNorth=bimSetTrueNorth;
  window.__acad3dV104='exportoffset,dxfnorthup,dxfbulgeflip,dxfimportinverse,svgnorthup,viewportframing';
  window.__a3dNorthArrow=function(){return A3D.lastNorth?JSON.parse(JSON.stringify(A3D.lastNorth)):null;};
  window.__acad3dV103='bearings,traverse,closure,propertyline,propertyfromshape,setbacks,setbackviolations,truenorth,northarrow,propertyexport';
  window.__acad3dV102='typecatalogue,beamtypes,footingtypes,isolatedfooting,wallfoundation,foundationslab,footingfollowshost,footingschedules,rotatedfootprintexport';
  /* __acad3dV96 */
  window.__a3dPatternRotation=bimPatternRotation;
  window.__a3dIsHatch=function(id){return bimIsHatch(objById(id));};
  window.__a3dHatchGraphics=function(id){var o=objById(id);return o?bimHatchGraphics(o):null;};
  window.__a3dHatchArea=function(id){var o=objById(id);return o?bimHatchArea(o):null;};
  window.__a3dAddHatch=function(pts,bulges,y,opts){
    var o=bimAddHatch(pts,bulges,y,opts);
    if(o){refreshTree();paint();}
    return o?o.id:null;
  };
  window.__a3dApplyHatchAt=function(pt,y,opts){
    var o=bimApplyHatchAt(pt,y,opts||bimHatchDefaults());
    return o?o.id:null;
  };
  window.__a3dApplyHatchEdit=function(id,opts){
    var o=bimApplyHatchEdit(id,opts);
    return o?o.id:null;
  };
  window.__a3dHatchPatternNames=function(){
    return BIM_HATCH_PATTERNS.filter(function(n){return n!=='none';});
  };
  window.__acad3dV96='hatchobject,patternangle,onegraphicsfieldvalidator,materialangleheeded,hatchcommand,hatchedit,bothmodes';
  /* __acad3dV95 */
  window.__a3dBulgedSignedArea=bimBulgedSignedArea;
  window.__a3dEdgeDirAt=bimEdgeDirAt;
  window.__a3dSplitEdge=bimSplitEdge;
  window.__a3dArrangeEdges=bimArrangeEdges;
  window.__a3dTraceBoundary=bimTraceBoundary;
  window.__a3dBoundaryEdges=bimBoundaryEdges;
  window.__a3dApplyBoundary=bimApplyBoundary;
  window.__acad3dV95='planararrangement,edgesplitatcrossings,tangentangularkey,signedbulgedarea,boundarycommand,islandreported,wallfacetracerreplaced';
  /* __acad3dV94: whether the drawing will consume a plain letter -- true only when it will. The
     V94 suite asks it. */
  window.__a3dWantsKey=function(ev){
    try{
      if(!A3D.on||!ev)return false;
      if(bimKeyForControl(ev))return false;   /* __acad3dV117 */
      if(el.dlg||A3D_TYPING.active)return false;
      if(bimGizmoWantsKey(ev))return true;               /* __acad3dV112 */
      if(A3D.face&&!drag&&!ev.ctrlKey&&!ev.metaKey&&!ev.altKey&&bimFaceKeyFor(ev)&&bimFaceCurrent())return true;   /* __acad3dV123 */
      return !!(A3D.sk&&bimSketchKeyFor(A3D.sk,ev));
    }catch(eW){console.warn('[BIM] Key claim check failed',eW);return false;}
  };
  window.__a3dSketchKeyNames=function(){
    return BIM_SKETCH_KEYS.map(function(k){return k.name;});
  };
  /* __acad3dV94 */
  window.__a3dClipInfinite=bimClipInfinite;
  window.__a3dClineSegIntersect=bimClineSegIntersect;
  window.__a3dClineArcIntersect=bimClineArcIntersect;
  window.__a3dClineCrossings=bimClineCrossings;
  window.__a3dClineDir=bimClineDir;
  window.__a3dClineModeLabels=bimClineModeLabels;
  window.__a3dClineModeForKey=bimClineModeForKey;
  window.__a3dDrawingExtent2D=bimDrawingExtent2D;
  window.__a3dIsCline=function(id){return bimIsCline(objById(id));};
  window.__a3dClineVisibleSeg=function(id){var o=objById(id);return o?bimClineVisibleSeg(o,null):null;};
  window.__a3dClinesOnPlane=bimClinesOnPlane;
  window.__a3dAddCline=function(p,dir,ray,y){
    var o=bimAddCline(p,dir,ray,y);
    if(o){refreshTree();paint();}
    return o?o.id:null;
  };
  window.__a3dSkCline=function(){
    var sk=A3D.sk;
    if(!sk||sk.tool!=='xline')return null;
    return {mode:sk.mode||null,angle:(typeof sk.angle==='number')?sk.angle:null,
            ray:!!sk.ray,pts:sk.pts.length,readyDir:bimClineReadyDir(sk)};
  };
  window.__a3dPickAt=function(x,y){var o=pick(x,y);return o?o.id:null;};
  window.__acad3dV94='xline,ray,liangbarskyclip,derivedextent,clinecrossingsnap,clinepick,pointpickfix';
  /* __acad3dV93 */
  window.__a3dPointAtLength=bimPointAtLength;
  window.__a3dDividePoints=bimDividePoints;
  window.__a3dMeasurePoints=bimMeasurePoints;
  window.__a3dCircleSketch=bimCircleSketch;
  window.__a3dPolygonSketch=bimPolygonSketch;
  window.__a3dSketchOutline=function(id){var o=objById(id);return o?bimSketchOutline(o):null;};
  window.__a3dIsPoint=function(id){return bimIsPoint(objById(id));};
  window.__a3dPointMarkerSegs=bimPointMarkerSegs;
  window.__a3dAddPoint=function(x,z,y){var o=bimAddPoint(x,z,y);refreshTree();paint();return o.id;};
  window.__a3dStartPolygon=startPolygonTool;
  window.__a3dApplyDivide=bimApplyDivide;
  window.__a3dApplyMeasure=bimApplyMeasure;
  window.__a3dDivideSource=function(id){var o=objById(id);var s=bimDivideSource(o);
    return s?{pts:s.pts.map(function(p){return [p[0],p[1]];}),bulges:s.bulges?s.bulges.slice():null,closed:s.closed}:null;};
  window.__acad3dV93='realcircle,polygon,pointnode,divide,measure,arclengthwalk,viewportflattens';
  /* __acad3dV92 */
  window.__a3dGrowEnd=bimGrowEnd;
  window.__a3dLengthenBulged=bimLengthenBulged;
  window.__a3dExtendBulged=bimExtendBulged;
  window.__acad3dV92='arcextend,arclengthen,growendsweep,startendasymmetry,straightonlyversionsdeleted';
  /* __acad3dV91 */
  window.__a3dProjectOntoBulged=bimProjectOntoBulged;
  window.__a3dPtDistToBulgedSeg=bimPtDistToBulgedSeg;
  window.__a3dIntersectBulgedSegs=bimIntersectBulgedSegs;
  window.__a3dSplitBulgedAt=bimSplitBulgedAt;
  window.__a3dTrimBulged=bimTrimBulged;
  window.__a3dBreakBulged=bimBreakBulged;
  window.__a3dArcPointAt=bimArcPointAt;
  window.__acad3dV91='arcawaretrim,arcawarebreak,sweepparameter,arcarcintersection,curvepicking';
  /* __acad3dV90 */
  window.__a3dTangentBulge=bimTangentBulge;
  window.__a3dSegEndDir=bimSegEndDir;
  window.__a3dOffsetBulged=bimOffsetBulged;
  window.__a3dCircleLineIntersect=bimCircleLineIntersect;
  window.__a3dSetArcMode=function(on){return bimSetArcMode(A3D.sk,on);};
  window.__a3dSkBulges=function(){return A3D.sk&&A3D.sk.bulges?A3D.sk.bulges.slice():null;};
  window.__a3dSkArcMode=function(){return !!(A3D.sk&&A3D.sk.arcMode);};
  window.__acad3dV90='arcmodeonwallandpline,tangentcontinuation,arcawareoffset,curvedpreview,offsetrefusalremoved';
  /* __acad3dV89 */
  window.__a3dFilletCorner=bimFilletCorner;
  window.__a3dApplyFillet=bimApplyFillet;
  window.__a3dWallIsCurved=function(id){var o=objById(id);return bimWallIsCurved(o);};
  window.__a3dWallLength=function(id){
    var o=objById(id);
    return (o&&o.bim&&o.bim.centerline)?bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges):null;
  };
  window.__a3dCurvedWall=function(pts,bulges,thk,hgt,align,closed){
    var lvl=bimGetActiveLevel();
    var o=buildWallSolid(pts,lvl.elev,hgt||lvl.height,thk||0.3,align||'center',!!closed,bulges);
    return o?o.id:null;
  };
  window.__acad3dV89='curvedwalls,filletradius,arclengthinschedules,mirrornegatesbulge,curverefusals';
  window.__a3dBulgeArc=bimBulgeArc;
  window.__a3dBulgeFrom3Pts=bimBulgeFrom3Pts;
  window.__a3dFlattenPoly=bimFlattenPoly;
  window.__a3dFlattenSketch=function(id){var o=objById(id);return o?bimFlattenSketch(o):null;};
  window.__a3dBulgedLength=bimBulgedLength;
  window.__a3dBulgedArea=bimBulgedArea;
  window.__a3dPointOnSweptArc=bimPointOnSweptArc;
  window.__a3dArcSegments=bimArcSegments;
  window.__acad3dV88='bulgestorage,arc3point,flattenonce,arcpicking,arcprompts';
  window.__a3dChamferPolylines=bimChamferPolylines;
  window.__a3dScalePoint=bimScalePoint;
  window.__a3dPolyLength=bimPolyLength;
  window.__a3dProjectOntoPolyline=bimProjectOntoPolyline;
  window.__a3dPlacePoint=function(gx,gz){skPlacePoint(gx,gz,null);};
  window.__a3dApplyExtend=bimApplyExtend;
  window.__a3dApplyBreak=bimApplyBreak;
  window.__a3dApplyLengthen=bimApplyLengthen;
  window.__a3dApplyChamfer=bimApplyChamfer;
  window.__a3dScaleSelection=bimScaleSelection;
  window.__a3dTypedPoint=bimCommitTypedPoint;
  window.__acad3dV87='extend,break,breakatpoint,lengthen,chamfer,scale,typedpointroutedthroughplace,filletradius0,rotateandarraycommandsreachable';
  window.__acad3dV86='palettewired,linetool,autocadcoords,autocadprompts,closeundo,repeatlast';
  window.__a3dShortcuts=function(){return JSON.parse(JSON.stringify(bimShortcutGroups()));};   /* __acad3dV122 */
  window.__acad3dV85='shortcutsheet,deadhelpremoved,railstackhelp,unearnedclaimdropped';
  window.__acad3dV84='viewactivation,planisnotflat,viewfollowsribbon,viewlabel,browserviewrows';
  window.__a3dOffsetObject=bimOffsetObject;
  window.__a3dAlignSelection=bimAlignSelection;
  window.__a3dObjBounds=bimObjBounds2D;
  window.__a3dRefreshBrowser=function(){refreshBrowser();};
  window.__a3dGlRender=function(){return !!A3D_GL;};
  window.__a3dGlFaces=function(){return A3D.glFaces||0;};
  window.__a3dGpu=function(){var P=A3D_GPU;return {state:P.state,why:P.why,engine:P.engine,fallback:P.fallback,pref:bimGpuPref(),label:bimGraphicsLabel(),bundleDraws:P.bdraws,format:P.format};};   /* __acad3dV153 */
  window.__a3dGraphics=function(pref){return bimGraphicsSet(pref);};
  window.__a3dGpuCompare=function(){return bimGpuCompare();};
  window.__a3dGpuRestart=function(){if(A3D_GPU.state==='starting'||A3D_GPU.state==='ready')return A3D_GPU.state;A3D_GPU.state='off';A3D_GPU.why='';bimGpuStart();return A3D_GPU.state;};
  window.__a3dGpuTiles=function(){var k,e,n=0,lv=[];for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)){e=A3D_MAP.cache[k];if(e.gtx&&e.gtx.dev===A3D_GPU.device){n++;lv.push(e.gtx.tex.mipLevelCount);}}return {textures:n,levels:lv,live:A3D_GPU.tileLive||0};};   /* __acad3dV154 */
  window.__a3dMapDropAll=function(){var k,L=[];for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k))L.push(A3D_MAP.cache[k]);L.forEach(bimMapDrop);return L.length;};
  window.__a3dGpuBreakNext=function(){A3D_GPU.breakNext=true;return true;};
  window.__a3dGpuLose=function(){if(!A3D_GPU.device)return false;A3D_GPU.device.destroy();return true;};   /* as a driver reset would */
  window.__a3dGpuWait=function(ms){var t0=Date.now();return new Promise(function(res){(function w(){if(A3D_GPU.state!=='starting'||Date.now()-t0>(ms||8000))res(A3D_GPU.state);else setTimeout(w,50);})();});};
  window.__a3dGlBatch=function(on){if(on!==undefined){A3D_GL_BATCH=!!on;paint();}return A3D_GL_BATCH;};   /* __acad3dV152 */
  window.__a3dGlStats=function(){return A3D.glStats?JSON.parse(JSON.stringify(A3D.glStats)):null;};
  window.__a3dGlBatchInfo=function(){var B=A3D_SCENE;if(!B)return (A3D_GL&&A3D_GL.gb)||A3D_GPU.state==='ready'?{chunks:[],slots:0,cap:0,free:0}:null;
    return {chunks:B.chunks.map(function(c){return {objects:c.ids.length,verts:c.count,edges:c.ecount};}),slots:Object.keys(B.slots).length,cap:B.cap,free:B.free.length};};
  window.__a3dGlTotals=function(){var B=A3D_SCENE;return B&&B.tot?JSON.parse(JSON.stringify(B.tot)):{frames:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0};};
  window.__a3dGlTableOf=function(id){var B=A3D_SCENE;if(!B||!B.slots.hasOwnProperty(id))return null;var s=B.slots[id];return [].slice.call(B.data.subarray(s*8,s*8+8));};
  /* a grid of n boxes, each its own element, for measuring; the mesh is shared, as a family's is */
  window.__a3dStressModel=function(n,size){var r=bimStressModel(n,size);paint();return r;};   /* __acad3dV155: the app's own */
  window.__a3dRenderBench=function(frames){return bimRenderBench(frames).then(function(r){paint();return r;});};
  window.__a3dBenchmark=function(){return bimBenchmark().then(function(r){return JSON.parse(JSON.stringify(r));});};
  window.__a3dPickMode=function(m){if(m==='on'||m==='off'||m==='auto')A3D_PICK_GPU=m;return A3D_PICK_GPU;};   /* __acad3dV156 */
  window.__a3dPickInfo=function(x,y){var t=performance.now(),o=pick(x,y);return {id:o&&o.id?o.id:null,path:A3D.lastPickPath||null,ms:performance.now()-t};};
  window.__a3dCull=function(on){if(on!==undefined){A3D_CULL=!!on;paint();}return A3D_CULL;};
  window.__a3dChunkCells=function(){var B=A3D_SCENE;return B?B.chunks.map(function(c){return {cell:c.cell,objects:c.ids.length,cull:c.cull,box:c.wb?c.wb.slice(0,6):null};}):[];};
  window.__a3dTestSetObjs=function(list){A3D.objs=list;A3D.sel=null;A3D.sel2=null;A3D.selSet=[];};
  window.__a3dTestPaint=function(){paint();};
  window.__a3dTestRotate=function(d){A3D.cam.yaw+=d;};
  window.__a3dTestForceCpu=function(on){A3D_GL_FAILED=!!on;A3D_GPU.forceOff=!!on;if(on){bimSceneRelease();A3D_GL=null;}};
  window.__a3dAngularDim=bimComputeAngularDim;
  window.__a3dCircleFrom3=bimCircleFrom3Points;
  window.__a3dBuildDXF=bimBuildDXF;
  /* __acad3dV88: the DXF round trip, and a projection the suite can aim a click with. */
  window.__a3dImportDXF=function(text){return bimImportDXF(text,'test.dxf');};
  window.__a3dToScreen=function(p,y){
    return toScreen([p[0],(typeof y==='number')?y:0,p[1]],camVecs(A3D.cam),cvW(),cvH());
  };
  window.__a3dExportDXF=bimExportDXF;
  window.__a3dCaptureView=bimCaptureView;
  window.__a3dApplyView=function(id){return bimActivateView('saved',id);};   /* __acad3dV119: through the record */
  window.__a3dToggleLevelFilter=bimToggleLevelFilter;
  window.__a3dFindEnclosingWallFace=bimFindEnclosingWallFace;
  window.__a3dFamilyAdd=bimFamilyLibraryAdd;
  window.__a3dFamilyGet=bimFamilyLibraryGet;
  window.__a3dFamilyRemove=bimFamilyLibraryRemove;
  window.__a3dPlaceFamily=bimPlaceFamilyInstance;
  window.__a3dSetUIPanelVisible=bimSetUIPanelVisible;
  window.__a3dLoadUIPanelPrefs=bimLoadUIPanelPrefs;
  window.__a3dRoomSchedule=bimBuildRoomSchedule;
  window.__a3dDoorSchedule=bimBuildDoorSchedule;
  window.__a3dWallSchedule=bimBuildWallSchedule;
  window.__a3dScheduleCSV=bimScheduleToCSV;
  window.__a3dEnterDraftingMode=bimEnterDraftingMode;
  window.__a3dMirrorObject=bimMirrorObject;
  window.__a3dRotatePoint=bimRotatePoint;
  window.__a3dJoinWalls=bimJoinWalls;
  window.__a3dComputeTransformedGeometry=bimComputeTransformedGeometry;
  window.__a3dEnterSection=bimEnterSection;
  window.__a3dExitSection=bimExitSection;
  window.__a3dFlipSection=bimFlipSection;
  window.__a3dComputeSectionCuts=bimComputeSectionCuts;
  window.__a3dClipMeshToPlane=bimClipMeshToPlane;
  window.__a3dExportProject=bimExportProjectFile;
  window.__a3dProjectEnvelope=bimBuildProjectEnvelope;
  window.__a3dImportProject=bimImportProjectFile;
  window.__a3dParseProjectEnvelope=bimParseProjectEnvelope;
  window.__a3dCreateDim=bimCreateDim;
  window.__a3dCreateText=bimCreateTextLabel;
  window.__a3dBuildPdf=bimBuildSimplePdf;
  window.__a3dBuildRoof=buildRoofSolid;
  window.__a3dBuildStair=buildStairSolid;
  window.__a3dBuildStairPathGeometry=bimBuildStairPathGeometry;
  window.__a3dStairLayout=bimBuildStairLayout;
  window.__a3dStairGuardMesh=bimBuildStairGuardMesh;
  window.__a3dFinishStair=finishStair;
  window.__a3dStairToolStart=startStairTool;
  window.__a3dSkPush=function(pt){if(A3D.sk)A3D.sk.pts.push([pt[0],pt[1]]);return A3D.sk?A3D.sk.pts.length:null;};
  window.__a3dFindRoofBoundary=bimFindRoofBoundaryAt;
  window.__a3dIsLocked=bimIsLocked;
  window.__a3dSetLocked=bimSetLocked;
  window.__a3dRecoverWall=bimTryRecoverWallFromRectProfile;
  window.__a3dRoomBoundaryAt=bimFindRoomBoundaryAt;
  window.__a3dPolyArea=bimPolyArea;
  window.__a3dPointInPoly=bimPointInPoly;
  window.__a3dTouchFakeEvent=bimTouchFakeEvent;
  window.__a3dTouchDist=bimTouchDist;
  window.__a3dTouchMid=bimTouchMid;
  window.__a3dMarquee=bimApplyMarquee;
  window.__a3dDuplicate=duplicateSelection;
  window.__a3dSelSet=function(){return A3D.selSet.slice();};
  window.__a3dLayers=function(){return JSON.parse(JSON.stringify(A3D.layers));};
