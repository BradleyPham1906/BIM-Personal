  var LSK='acad3dV1';
  var SCALE=0.35;
  var DEFCAM={yaw:-0.7,pitch:0.42,dist:30,tx:0,ty:1,tz:0};
  /* __acad3dV120: the material library. One array, read through bimMaterialCards() by the
     inspector, the schedules' mass takeoff, the plan hatches and the Assets panel. Each card carries
     its engineering data -- density in kg/m3, Young's modulus, Poisson's ratio -- and a hatch. */
  var A3D_MATERIAL_LIBRARY=[
    {name:'Steel',kind:'Metal',density:7900,youngsModulus:'210 GPa',poissonRatio:0.30,color:'#9fb6c9',hatch:{angle:45,gap:9}},
    {name:'Aluminium',kind:'Metal',density:2700,youngsModulus:'70 GPa',poissonRatio:0.35,color:'#c9cdd2',hatch:{angle:45,gap:9,cross:true}},
    {name:'Concrete',kind:'Mineral',density:2400,youngsModulus:'32 GPa',poissonRatio:0.17,color:'#b7ab98',hatch:{angle:30,gap:12,cross:true}},
    {name:'Wood',kind:'Organic',density:700,youngsModulus:'12 GPa',poissonRatio:0.05,color:'#c8a06a',hatch:{angle:0,gap:10}},
    {name:'Glass',kind:'Mineral',density:2500,youngsModulus:'72 GPa',poissonRatio:0.22,color:'#8fd0d8',hatch:{angle:60,gap:14}}
  ];
  var A3D={
    on:false, sel:null, sel2:null, view:'Home', frames:0, seq:1, built:false,
    flat:false, navMode:'orbit', sk:null, prevCam:null, prevView:null,
    /* __acad3dV60: Phase 52a. A runtime view toggle, not a saved project field -- deliberately not
       part of bimSnapshotState/bimBuildProjectEnvelope, the same way camera orbit state (A3D.cam)
       and A3D.flat itself are ephemeral rather than persisted. Starts false so a freshly loaded
       project renders exactly as it always has. */
    presentMode:false,
    cam:{yaw:DEFCAM.yaw,pitch:DEFCAM.pitch,dist:DEFCAM.dist,tx:DEFCAM.tx,ty:DEFCAM.ty,tz:DEFCAM.tz},
    objs:[], counts:{}, lastPolys:[], cubePolys:[], homeRect:null, meshes:{}, grips:[], selSet:[], section:null,
    views:[], activeViewId:null, levelFilter:false, types:null, activeWallType:null, grids:[],
    levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3,buildingId:'bldg-0'}], activeLevel:'lvl-0',
    buildings:[{id:'bldg-0',name:'Building 1'}], activeBuilding:'bldg-0',
    site:{name:'Site'},
    roomScheme:'',   /* __acad3dV105: '' off, 'dept' or 'occupancy' -- the room colour fill */
    showTrib:false,   /* __acad3dV106: the TRIBAREA overlay, a view toggle */
    showSun:false,   /* __acad3dV107: shadows and the sun path, a view toggle */
    layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}], activeLayer:'layer-0',
    sheets:[], activeSheetId:null, sheetSelVp:null, sheetDrag:null,
    sheetActiveVp:null,   /* __acad3dV116: the viewport being worked in (model space), or null for paper space */
    titleBlock:{project:'',client:'',drawnBy:'',checkedBy:''}, sheetCapture:false,
    conPick:null, classifications:[]
  };
  var el={};
  /* __acad3dV115: the defaults are what save3d would write before anything stored is applied, so
     a new project is exactly a first boot. The loader was code that ran once; it is a function now
     because opening a project is the same act as booting into it. */
  var A3D_PROJECT_DEFAULTS=JSON.stringify(bimProjectRecord());
  var A3D_BOOT_DOC=null;
  var A3D_BOOT_IDB=null;   /* __acad3dV172d: the project on screen is in the browser's database (core/idb-store.js) */
  function bimApplyStoredState(st){
      if(st&&st.objs&&st.objs.length){A3D.objs=st.objs;}
      if(st&&st.cam&&typeof st.cam.dist==='number'){A3D.cam=st.cam;}
      if(st&&typeof st.seq==='number'){A3D.seq=st.seq;}
      if(st&&st.counts){A3D.counts=st.counts;}
      if(st&&st.levels){
        if(Array.isArray(st.levels)&&st.levels.length&&st.levels.every(function(L){return L&&typeof L.id==='string'&&isFinite(L.elev)&&isFinite(L.height);})){
          A3D.levels=st.levels;
        }else{
          console.warn('[BIM] Corrupted level data in '+LSK+' storage; falling back to default levels.');
        }
      }
      if(st&&typeof st.activeLevel==='string')A3D.activeLevel=st.activeLevel;
      if(st&&Array.isArray(st.grids)){
        A3D.grids=st.grids.filter(function(g){
          return g&&typeof g.id==='string'&&g.p1&&g.p2&&g.p1.length===2&&g.p2.length===2;
        });
        if(A3D.grids.length!==st.grids.length)console.warn('[BIM] Discarded malformed grid datums from '+LSK+' storage.');
      }
      if(st&&st.types&&typeof st.types==='object')A3D.types=st.types;
      if(st&&typeof st.activeWallType==='string')A3D.activeWallType=st.activeWallType;
      if(st&&Array.isArray(st.views))A3D.views=st.views;
      if(st&&typeof st.activeViewId==='string')A3D.activeViewId=st.activeViewId;
      if(st&&typeof st.levelFilter==='boolean')A3D.levelFilter=st.levelFilter;
      if(st&&st.layers){
        if(Array.isArray(st.layers)&&st.layers.length&&st.layers.every(function(L){return L&&typeof L.id==='string'&&typeof L.name==='string';})){
          A3D.layers=st.layers;
        }else{
          console.warn('[BIM] Corrupted layer data in '+LSK+' storage; falling back to default layers.');
        }
      }
      if(st&&typeof st.activeLayer==='string')A3D.activeLayer=st.activeLayer;
      if(st&&Array.isArray(st.sheets)){
        A3D.sheets=st.sheets.filter(function(s){
          return s&&typeof s.id==='string'&&isFinite(s.w)&&isFinite(s.h)&&Array.isArray(s.viewports);
        });
        if(A3D.sheets.length!==st.sheets.length)console.warn('[BIM] Discarded malformed sheet(s) from '+LSK+' storage.');
      }
      if(st&&st.titleBlock&&typeof st.titleBlock==='object')A3D.titleBlock=st.titleBlock;
      if(st&&Array.isArray(st.buildings)){
        var goodBldgs=st.buildings.filter(function(b){return b&&typeof b.id==='string'&&typeof b.name==='string';});
        if(goodBldgs.length){
          A3D.buildings=goodBldgs;
          if(goodBldgs.length!==st.buildings.length)console.warn('[BIM] Discarded malformed building(s) from '+LSK+' storage.');
        }else{
          console.warn('[BIM] Corrupted building data in '+LSK+' storage; falling back to default building.');
        }
      }
      if(st&&typeof st.activeBuilding==='string')A3D.activeBuilding=st.activeBuilding;
      if(st&&st.site&&typeof st.site==='object'&&typeof st.site.name==='string')A3D.site=st.site;
      A3D.dataFeatures={};   /* __acad3dV134: the features of the project's data layers, orphans dropped */
      if(st&&st.dataFeatures&&typeof st.dataFeatures==='object'&&A3D.site&&Array.isArray(A3D.site.dataLayers))
        A3D.site.dataLayers.forEach(function(L){if(L&&Array.isArray(st.dataFeatures[L.id]))A3D.dataFeatures[L.id]=st.dataFeatures[L.id];});
      if(st&&(st.roomScheme==='dept'||st.roomScheme==='occupancy'))A3D.roomScheme=st.roomScheme;   /* __acad3dV105 */
      A3D.history=bimHistValid(st&&st.history);   /* __acad3dV146: its history, or none */
      A3D.resultLayers=bimResValid(st&&st.resultLayers);   /* __acad3dV148: its result layers, or none */
      A3D.pres=bimPresValid(st&&st.pres);   /* __acad3dV162: its boards in the set, and the set's order */
      A3D_RES_IMG={};
      if(st&&Array.isArray(st.classifications)){
        A3D.classifications=st.classifications.filter(function(c){return c&&typeof c.id==='string'&&typeof c.code==='string';});
        if(A3D.classifications.length!==st.classifications.length)console.warn('[BIM] Discarded malformed classification(s) from '+LSK+' storage.');
      }
      /* __acad3dV121: an older project's layerless objects join the layer that was current when it
         was saved -- the one they were being drawn as, so nothing changes on screen */
      try{bimAdoptLayers();}
      catch(eAd){console.warn('[BIM] Objects could not be given their layers; they follow the current one until the next save.',eAd);}
  }
  try{
    var raw=localStorage.getItem(LSK);
    if(raw){
      var st=JSON.parse(raw);
      /* __acad3dV172d: a pointer in place of the record: its name now, the record once the database is read */
      if(st&&st.idb===1&&typeof st.docId==='string'&&!Array.isArray(st.objs)){
        A3D_BOOT_IDB=st.docId;
        if(st.titleBlock&&typeof st.titleBlock.project==='string')A3D.titleBlock.project=st.titleBlock.project;
      }else bimApplyStoredState(st);
      if(st&&typeof st.docId==='string'&&st.docId)A3D_BOOT_DOC=st.docId;   /* __acad3dV115 */
    }
  }catch(e0){
    console.warn('[BIM] Failed to restore 3D/BIM state from localStorage; starting from defaults.',e0);
  }
  /* __acad3dV115: the project list, reconciled with what is stored before anything can save */
  var A3D_DOCS_KEY='acad3dDocsV1',A3D_DOC_PREFIX='acad3dDocV1:';
  var A3D_DOCS=bimDocsBoot();
  var A3D_DOC_RT={};
