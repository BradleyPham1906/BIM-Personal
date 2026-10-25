  /* __acad3dV51: opening-propagation surface for the Phase 55b tests. */
  window.__a3dDoorAt=function(wallId,xz,w,h){
    var wall=objById(wallId);
    if(!wall)return null;
    var m=buildDoorOpening(wall,xz,w||0.9,h||2.1);
    return m?m.id:null;
  };
  window.__a3dWindowAt=function(wallId,xz,w,h,sill){
    var wall=objById(wallId);
    if(!wall)return null;
    var m=buildWindowOpening(wall,xz,w||1.2,h||1.2,sill===undefined?0.9:sill);
    return m?m.id:null;
  };
  window.__a3dOpeningsOf=function(wallId){
    return A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.hostWallId===wallId;})
      .map(function(o){return {id:o.id,name:o.name,center:o.bim.center,width:o.bim.width,height:o.bim.height,sill:o.bim.sillHeight};});
  };
  window.__a3dMeshStats=function(id){
    var o=objById(id);
    if(!o||!o.mesh)return null;
    return {verts:o.mesh.v?o.mesh.v.length:0,faces:o.mesh.f?o.mesh.f.length:0};
  };
  window.__a3dRebuildWall=function(id,thk,hgt,align){
    var o=objById(id);
    if(!o)return false;
    return bimRebuildWall(o,thk===undefined?o.bim.thickness:thk,hgt===undefined?o.bim.height:hgt,align||o.bim.align);
  };
  window.__a3dPropagateFrom=function(ids,reason,delta){return bimPropagateFrom(ids,reason,delta);};
  window.__acad3dV51='dependencyvisitors,openingrecut,wallrebuildpropagation,reasonflag';
  /* __acad3dV52: room-remeasurement + related-path test surface. */
  window.__a3dCreateRoomAt=function(pt,y0){
    var b=bimFindRoomBoundaryAt(pt,y0===undefined?0:y0);
    if(!b)return null;
    var o=bimCreateRoom(b);
    return o?o.id:null;
  };
  window.__a3dObjSnapshot=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(o)):null;};
  window.__a3dDragWallGripTo=function(wallId,idx,x,z){
    var o=objById(wallId);
    if(!o)return null;
    bimDragWallPoint(o,idx,[x,z]);
    bimPropagateFrom([o.id],'rebuild');
    return JSON.parse(JSON.stringify(o.bim.centerline));
  };
  window.__a3dApplyWallJoin=function(idA,idB){
    A3D.sel=idA;A3D.sel2=idB;
    applyWallJoin();
    return A3D.objs.map(function(o){return o.id;});
  };
  window.__a3dApplyTrim=function(cutterId,clickPt){bimApplyTrim(cutterId,clickPt);};
  window.__a3dRotateSelection=function(ids,center,angleRad){return bimRotateSelection(ids,center,angleRad);};
  window.__a3dAfterSketchEdit=function(id){var o=objById(id);return o?bimAfterSketchEdit(o):null;};
  window.__acad3dV52='roomremeasure,livesourcetracking,walljointrimmergepropagation,sketcheditpropagation,detachonmanualedit';
  window.__a3dSelectFor=function(ids){A3D.sel=(ids&&ids[0])||null;A3D.selSet=(ids||[]).slice();A3D.sel2=null;};
  /* __acad3dV87: the pair selection Chamfer, Fillet, Join and Merge all take. */
  window.__a3dSelectPair=function(a,b){A3D.sel=a||null;A3D.sel2=b||null;A3D.selSet=[a,b].filter(Boolean);};
  window.__a3dMirrorSelection=function(ids,P1,P2){bimMirrorSelection(ids,P1,P2);return A3D.selSet.slice();};
  window.__a3dBuildPolarArray=function(ids,center,n,totalAngleDeg){bimBuildPolarArray(ids,center,n,totalAngleDeg*Math.PI/180);return A3D.selSet.slice();};
  window.__a3dDeleteWallForTest=function(id){
    var idx=-1,i;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id){idx=i;break;}
    if(idx>=0)A3D.objs.splice(idx,1);
  };
  window.__a3dUnits=function(){return {key:A3D_UNITS.key,dp:bimUnitDp(),label:bimUnitLabel()};};
  window.__a3dSetUnits=bimSetUnits;
  window.__a3dDispLen=bimDispLen;
  /* Drives a length field through the REAL path -- the same input element and the same change
     event a user produces -- rather than calling the converter directly, so a suite cannot pass
     while the wiring is broken. */
  window.__a3dSetPropLen=function(field,displayValue){
    if(!el.propsbody)return false;
    var inp=el.propsbody.querySelector('[data-propf="'+field+'"][data-proplen]');
    if(!inp)return false;
    inp.value=String(displayValue);
    inp.dispatchEvent(new Event('change',{bubbles:true}));
    return true;
  };
  window.__a3dPropRows=function(){
    if(!el.propsbody)return null;
    var rows=el.propsbody.querySelectorAll('.a3d-prow'),out=[],i;
    for(i=0;i<rows.length;i++){
      var lab=rows[i].querySelector('.a3d-plabel');
      var stat=rows[i].querySelector('.a3d-pstatic');
      var inpEl=rows[i].querySelector('input,select');
      out.push({label:lab?lab.textContent.trim():'',
                value:stat?stat.textContent.trim():(inpEl?String(inpEl.value):''),
                ro:rows[i].classList.contains('ro'),
                len:!!(inpEl&&inpEl.getAttribute&&inpEl.getAttribute('data-proplen')),
                group:bimPropRowGroup(rows[i])});
    }
    return out;
  };
  function bimPropRowGroup(row){
    var n=row.parentNode;
    if(!n)return null;
    var p=n.previousElementSibling;
    return (p&&p.getAttribute)?p.getAttribute('data-a3dpgrp'):null;
  }
  window.__acad3dV77='projectdisplayunits,onenumberformat,unitsinlabels,lengthinputconversion,locationlineinconstraints,readonlyrowstyling';
  window.__a3dRefreshProps=function(){refreshProps();};
  window.__a3dRemeasureRoomFromSource=function(roomId){
    var o=objById(roomId);
    if(!o)return null;
    var ctx={roomsUpdated:0,roomsFailed:0};
    var ok=bimRemeasureRoomFromSource(o,ctx);
    return {ok:ok,roomsUpdated:ctx.roomsUpdated,roomsFailed:ctx.roomsFailed,snapshot:JSON.parse(JSON.stringify(o))};
  };
  /* __acad3dV53: linked-clone auto-sync test surface. */
  window.__a3dFloorAt=function(pts,y,thk,mat){
    var o=buildFloorSolid({pts:pts,y:y===undefined?0:y},thk||0.2,mat||'Concrete Slab',bimGetActiveLevel());
    return o?o.id:null;
  };
  window.__a3dColumnAt=function(pt,y,w,dep,h){
    var o=buildColumnSolid(pt,y===undefined?0:y,w||0.4,dep||0.4,h||3);
    return o?o.id:null;
  };
  window.__a3dRebuildFloor=function(id,thk,mat){
    var o=objById(id);if(!o)return false;
    return bimRebuildFloor(o,thk===undefined?o.bim.thickness:thk,mat||o.bim.material);
  };
  window.__a3dRebuildColumn=function(id,w,dep,h){
    var o=objById(id);if(!o)return false;
    return bimRebuildColumn(o,w===undefined?o.bim.width:w,dep===undefined?o.bim.depth:dep,h===undefined?o.bim.height:h);
  };
  window.__a3dSyncOneClone=function(cloneId){
    var o=objById(cloneId);
    if(!o)return null;
    var ctx={clonesUpdated:0,clonesFailed:0};
    var ok=bimSyncOneClone(o,ctx);
    return {ok:ok,clonesUpdated:ctx.clonesUpdated,clonesFailed:ctx.clonesFailed,snapshot:JSON.parse(JSON.stringify(o))};
  };
  window.__acad3dV53='cloneautosync,onesyncimplementation,detachondirectedit,floorcolumnrebuildpropagation';
  /* __acad3dV55: transform-propagation test surface -- exercises the drag-move gesture's
     deferred single-propagation path without simulating real mouse events, the same way
     __a3dDragWallGripTo exercises grip-drag. */
  window.__a3dMoveObjects=function(ids,dx,dy,dz){
    dx=dx||0;dy=dy||0;dz=dz||0;
    var i,touched=[];
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o){continue;}
      if(!o.pos)o.pos=[0,0,0];
      o.pos[0]+=dx;o.pos[1]+=dy;o.pos[2]+=dz;
      touched.push(ids[i]);
    }
    var rep=bimPropagateFrom(touched,'transform',[dx,dy,dz]);
    paint();saveSoon();
    return rep;
  };
  window.__a3dNudgeObject=function(id,key){
    var o=objById(id);
    if(!o)return null;
    var d=bimNudgeObject(o,key);
    if(d){paint();saveSoon();}
    return d;
  };
  window.__acad3dV55='transformpropagation,posawareroomclonesync,relationshipawaredetach,dragmovedeferredpropagation,alignnudgeimmediatepropagation,levelshiftpropagation,openingtranslateoncenter';
  /* __acad3dV56: vector plan export test surface. */
  window.__a3dBuildSVG=function(mode){return bimBuildSVG(mode);};
  // Text/dim objects have no UI-tool test hook of their own (unlike wall/room/sketch) since they
  // are normally placed by direct click in the drafting overlay -- this appends a hand-built raw
  // object literal directly, the same trick __a3dTestSetObjs already relies on wholesale, just
  // additive instead of replacing the scene.
  window.__a3dPushTestObj=function(o){A3D.objs.push(o);return o.id;};
  window.__acad3dV56='svgexport,modelspacevectoroutput,perlayergroups,dataobjids';
  /* __acad3dV57: vector sheet print/export test surface. */
  window.__a3dBuildSheetSVG=function(sheetId,mode){
    var s=bimSheetById(sheetId||A3D.activeSheetId);
    return s?bimBuildSheetSVG(s,mode):null;
  };
  window.__a3dBuildPlanViewportSVG=function(sheetId,vpId,mode){
    var s=bimSheetById(sheetId||A3D.activeSheetId);if(!s)return null;
    var vp=null,i;for(i=0;i<s.viewports.length;i++)if(s.viewports[i].id===vpId){vp=s.viewports[i];break;}
    if(!vp)return null;
    var src=bimResolveViewportSource(vp);
    if(src.error)return {error:src.error};
    return bimBuildPlanViewportSVG(vp,src,vp.x,vp.y,vp.w,vp.h,mode);
  };
  window.__acad3dV57='vectorsheetprint,planviewportvector,rasterfallbackforelevationschedule,vectortitleblock,exportsheetsvg';
  /* __acad3dV61: Phase 52b -- presentation mode wired into the vector SVG export sinks (bimBuildSVG,
     bimBuildPlanViewportSVG, and by extension bimBuildSheetSVG). Optional mode param, defaults to
     'technical' (byte-identical to pre-Phase-52b output). Presentation resolves each object's
     graphics via bimResolveGraphics and applies fill/line-color/line-weight/opacity per element;
     wall poche uses an evenodd outer-minus-inner path so a filled wall never covers its interior
     room. Drop shadow is NOT emitted in vector output (no per-path SVG equivalent to Canvas2D
     shadowBlur without a <filter>/feDropShadow defs system -- deliberately out of scope here, same
     "small tested sub-phase" reasoning Phase 52a used to defer pattern). */
  window.__acad3dV61='svgpresentationmode,vectorwallpoche,evenoddfillrule,mmcalibratedlineweight,exportsvgfollowspresentmode,sheetexportprintfollowpresentmode,shadowdeferredtonextphase';
  /* __acad3dV62: maintenance fixes -- multi-opening walls, T-junction-aware Check Model, and the
     removal of the remote webfont bundle. Test surface for the first two. */
  window.__acad3dV62='multiopeningwallcut,singlebooleanfromregeneratedbase,volumemustdecreasefailsafe,tjunctionclosurecheck,checkmodelnofalsepositive,nolocalfirstviolationwebfont';
  /* __acad3dV63: Phase 53 pattern library. Test surface deliberately exposes the definition table
     and both sinks' calibration, so the suite can assert the tile geometry it claims to draw
     rather than sampling rendered pixels. */
  window.__a3dPatternDefs=function(){return JSON.parse(JSON.stringify(BIM_PATTERN_DEFS));};
  window.__a3dPatternNames=function(){return BIM_HATCH_PATTERNS.slice();};
  window.__a3dPatternDraws=function(n){return bimPatternDraws(n);};
  window.__a3dPatternLabel=function(n){return bimPatternLabel(n);};
  window.__a3dPatternTileSize=function(n,scale){return bimPatternTileSize(n,scale);};
  /* __acad3dV96: forwards its arguments instead of re-listing them. The six-parameter version
     of this wrapper silently dropped the angle bimPatternSvgDef gained in V96, and shadowed the
     second export that did pass it. */
  window.__a3dPatternSvgDef=function(){
    return bimPatternSvgDef.apply(null,arguments);
  };
  window.__a3dLwToPx=function(){return BIM_LW_TO_PX;};
  window.__acad3dV63='patternlibrary,proceduralhatchtiles,patterncolor,patternscale,canvas2dpatternsink,svgpatterndefs,wallpochehatch,roomfillhatch,screenalignednotsurfacealigned';
  /* __acad3dV64: the shell's measured geometry -- one work surface, and where it starts -- so a
     suite can assert the invariant rather than re-deriving it. */
  window.__a3dShellGeom=function(){
    function box(id){
      var e=document.getElementById(id);
      if(!e)return null;
      var r=e.getBoundingClientRect(),cs=getComputedStyle(e);
      return {w:Math.round(r.width),h:Math.round(r.height),x:Math.round(r.x),y:Math.round(r.y),
              display:cs.display,visible:cs.display!=='none'&&r.width>0&&r.height>0};
    }
    var sh=box('acad3d');
    return {
      mode:(window.__a3dOn?(window.__a3dFlat&&window.__a3dFlat()?'da':'3d'):null),   /* __acad3dV120 */
      wsCur:window.ACAD_WS_CUR||null,
      a3dOn:!!window.__a3dOn,
      acad3d:sh,
      dock:box('a3d-shell'),ribbon:box('acad-shell'),
      workSurfaces:[sh].filter(function(b){return b&&b.visible;}).length,
      work:(sh&&sh.visible)?sh:null
    };
  };
  window.__acad3dV64='shellunification,modesswitchnotstack,canvasboardhiddeninbim,onework-areacontract,dockwidthbinding,roundtripsafe';
  /* __acad3dV65: shell unification step 3 -- ONE left column. The Properties/Project Browser tree
     is re-parented into the dock panel on entry and restored on exit, so the rail selects a
     subject and its sections stack beneath it, instead of a second navigator opening beside the
     first. Also fixes the stale --a3d-left-w that let the two panels land on the same x. */
  window.__a3dTreeDocked=function(){
    var t=document.querySelector('.a3d-tree');
    return {
      docked:!!(t&&t.parentElement&&t.parentElement.id==='a3d-leftpanel'),
      parent:t?(t.parentElement.id||t.parentElement.className||null):null,
      propsAlive:!!document.getElementById('a3d-propsbody'),
      browserAlive:!!document.getElementById('a3d-browser'),
      dockVar:getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim(),
      tab:(document.getElementById('a3d-shell')||{dataset:{}}).dataset.tab||null
    };
  };
  window.__acad3dV65='oneleftcolumn,treenestedindockpanel,railselectssubject,sectionsstack,docksyncfix,restoredonexit';
  window.__acad3dV66='sectionpanesnotonescroll,propscappedat46pct,browseralwaysonscreen,graphicsoverridegroupscollapsed,palettebuttonswrap';
  window.__acad3dV67='bimstatusbar,livecoordreadout,activelevelselect,snaptogglesinbar,snappillretired,canvasbannerretired';
  window.__acad3dV68='navigatorleft,inspectorright,propssectionmoves,v66capretired,rightdraweroncompact,restoredonexit';
  window.__acad3dV69='sharedmateriallibrary,samearraynotacopy,materialcutpattern,closedvolumeonly,massinschedules,firstmodelbridge';
  window.__acad3dV70='rayontooldock,generatedfromribbonregistry,ribbonhiddeninbim,nocommandlost,caretpopovers,ribbonheightrecalculated';
  /* __acad3dV70: __a3dRibbonActions is every action the tool registry (A3DR_TABS) can reach;
     __a3dDockActions is every action the rendered dock can reach.
     The suite asserts they are the SAME SET -- which is the only way to know a rebuilt tool
     surface did not quietly drop a command. */
  /* __acad3dV70: which sketch/placement tool is armed right now, or null. Needed because the
     nearest existing hook, __a3dSketch(tool,pts), is a BUILDER -- calling it with no arguments
     starts a tool named undefined and returns null, which reads exactly like "no tool active"
     and made the first Phase 70 dock-click check fail against working code. */
  window.__a3dActiveSketchTool=function(){return (A3D.sk&&A3D.sk.tool)||null;};
  window.__acad3dV72='devicepixelratio,logicalcanvasunits,ctxscaledperframe,resizeobserveronviewport,capturescratchunaffected';
  window.__acad3dV73='canvasworkspaceretired,bootsintodraftingshell,modelpropsonnoselection,biggerhittargets,wsmigration';
  /* __acad3dV73: the hit sizes a user has to click. (__a3dWorkspaces, which read the view dropdown's
     menu, went with the dropdown in V119.) */
  window.__a3dHitSizes=function(){
    function box(sel){
      var e=document.querySelector(sel);
      if(!e)return null;
      var r=e.getBoundingClientRect();
      return [Math.round(r.width),Math.round(r.height)];
    }
    return {dockButton:box('#a3d-dock .a3d-dbtn'),
      dockAll:box('#a3d-dock .a3d-dall'),   /* __acad3dV130: the control that opens the rest */
      propGroupCaret:box('#a3d-propsbody .a3d-pgcar'),
      paletteButton:box('.a3d-palbtn')};
  };
  window.__a3dModelProps=function(){
    var b=el.propsbody;
    if(!b)return null;
    var fields={},f=b.querySelectorAll('[data-propmodel]'),i;
    for(i=0;i<f.length;i++)fields[f[i].getAttribute('data-propmodel')]=f[i].value;
    var texts=[],rows=b.querySelectorAll('.a3d-prow'),j;
    for(j=0;j<rows.length;j++){
      var lab=rows[j].querySelector('.a3d-plabel'),val=rows[j].querySelector('.a3d-pstatic');
      if(lab&&val)texts.push([lab.textContent.trim(),val.textContent.trim()]);
    }
    var grps=b.querySelectorAll('.a3d-pgrp'),g=[],k;
    for(k=0;k<grps.length;k++)g.push(grps[k].getAttribute('data-a3dpgrp'));
    return {editable:fields,readonly:texts,groups:g,
      isEmptyMessage:!!b.querySelector('.a3d-propempty')};
  };
  window.__a3dSetModelField=function(key,value){
    var f=el.propsbody?el.propsbody.querySelector('[data-propmodel="'+key+'"]'):null;
    if(!f)return false;
    f.value=value;
    f.dispatchEvent(new Event('change',{bubbles:true}));
    return true;
  };
  /* __acad3dV72: the three sizes that have to agree, exposed together because the bug was that
     they silently disagreed. backing = device pixels the canvas actually allocates; units = the
     coordinate space the drawing and hit-testing code works in; cssBox = the on-screen size the
     browser stretches the backing store to. A click at CSS x lands at x*(units/cssBox) in model
     space, so units must equal cssBox or every click is off by that ratio -- and backing must be
     cssBox*dpr or the result is upscaled and blurry. */
  window.__a3dCanvasMetrics=function(){
    if(!el.cv)return null;
    var r=el.cv.getBoundingClientRect();
    return {backing:[el.cv.width,el.cv.height],
      units:[cvW(),cvH()],
      cssBox:[Math.round(r.width*100)/100,Math.round(r.height*100)/100],
      scale:cvScale(el.cv),
      dpr:window.devicePixelRatio||1,
      ctxTransform:(function(){try{var t=el.ctx.getTransform();return [t.a,t.d];}catch(e){return null;}})()};
  };
  /* Where a model point actually appears ON SCREEN, in CSS pixels: the drawing code's own
     projection, mapped through the stretch the browser applies to the backing store. This is the
     number a user compares against their cursor, and the one the in-canvas round trip could not
     see because projection and un-projection share the same (possibly wrong) units. */
  window.__a3dProjectCss=function(pos){
    var p=window.__a3dProject(pos);
    var r=el.cv.getBoundingClientRect();
    var uw=cvW(),uh=cvH();
    if(!uw||!uh)return null;
    return {x:p.x*(r.width/uw),y:p.y*(r.height/uh)};
  };
  window.__acad3dV71='disciplines,computeddockrows,commandsearch,oneCallRegistration,domainpluggable,extbeforebuiltin';
  /* __acad3dV71: the extension API, exposed so a domain pack (bridge, mechanical, MEP) can be
     added without editing this file's registries by hand -- and so the scalability claim can be
     TESTED by actually adding a discipline at runtime rather than asserted in a comment. */
  window.__a3dRegisterCommand=a3drRegisterCommand;
  window.__a3dRegisterDiscipline=a3drRegisterDiscipline;
  window.__a3dRegisterTab=a3drRegisterTab;
  window.__a3dDisciplines=function(){return A3D_DISCIPLINES.map(function(d){
    return {id:d.id,name:d.name};});};
  window.__a3dDiscipline=function(){return A3D_DISC_CUR;};
  window.__a3dSetDiscipline=function(id){
    var i;
    for(i=0;i<A3D_DISCIPLINES.length;i++)if(A3D_DISCIPLINES[i].id===id){
      A3D_DISC_CUR=id;bimBuildDock();return true;
    }
    return false;
  };
  /* __acad3dV128: the dock's search is the command search -- what it matches, and the ribbon
     actions among the matches */
  window.__a3dDockSearch=function(q){
    var r=bimCmdSearch(q,0),acts=[],i;
    for(i=0;i<r.length;i++)if(r[i].act)acts.push(r[i].act);
    return {matches:r.length,shown:acts};
  };
  /* Coverage audit: every action any tab can reach must have a real label (not its own raw id)
     and a real icon. Those are two of the four places a command has to be defined, and the two a
     rebuild silently gets wrong -- a command with no label renders as 'bim:girder'. */
  window.__a3dCommandAudit=function(){
    var all=a3drAllCommands(),noLabel=[],noIcon=[],i,c;
    for(i=0;i<all.length;i++){
      c=all[i];
      if(a3drLabel(c.act)===c.act)noLabel.push(c.act);
      if(!a3drIcon(c.act))noIcon.push(c.act);
    }
    return {total:all.length,noLabel:noLabel,noIcon:noIcon};
  };
  window.__a3dRibbonActions=function(){
    var out={},i,j,k,t,p,a;
    for(i=0;i<A3DR_TABS.length;i++){
      t=A3DR_TABS[i];
      for(j=0;j<t.panels.length;j++){
        p=t.panels[j];
        if(p.big)for(k=0;k<p.big.length;k++){
          a=a3drActOf(p.big[k]);out[a]=1;
          if(p.big[k].menu){var m;for(m=0;m<p.big[k].menu.length;m++)out[p.big[k].menu[m][0]]=1;}
        }
        if(p.small)for(k=0;k<p.small.length;k++)out[p.small[k]]=1;
      }
    }
    return Object.keys(out).sort();
  };
  window.__a3dDockActions=function(){
    var els=document.querySelectorAll('#a3d-dock [data-a3dr]'),out={},i;
    for(i=0;i<els.length;i++)out[els[i].getAttribute('data-a3dr')]=1;
    return Object.keys(out).sort();
  };
  window.__a3dDockInfo=function(){
    var d=document.getElementById('a3d-dock');
    if(!d)return null;
    var rows=d.querySelectorAll('.a3d-dockrow'),grps=d.querySelectorAll('.a3d-dockgrp');
    var r=d.getBoundingClientRect(),i,g=[];
    for(i=0;i<grps.length;i++)g.push({id:grps[i].getAttribute('data-dockgrp'),
      buttons:grps[i].querySelectorAll('.a3d-dbtn').length});
    return {rows:rows.length,groups:g,
      visible:!!(d.offsetParent!==null),
      insideViewport:(function(){
        var vp=el.root?el.root.querySelector('.a3d-vp'):null;
        var bodyEl=d.querySelector('.a3d-dockbody');
        if(!vp||!bodyEl)return false;
        var v=vp.getBoundingClientRect(),br=bodyEl.getBoundingClientRect();
        return br.left>=v.left-1&&br.right<=v.right+1&&br.bottom<=v.bottom+1;
      })(),
      unimplementedOnFace:(function(){
        var b=d.querySelectorAll('.a3d-dbtn'),n=0,q;
        for(q=0;q<b.length;q++)if(A3DR_UNIMPL[b[q].getAttribute('data-a3dr')])n++;
        return n;
      })()};
  };
  window.__a3dDockOpenGroup=function(id){   /* __acad3dV130: the group, in the tools panel */
    if(!bimOpenToolsPanel())return false;
    var p=document.getElementById('a3d-rupop'),c=p&&p.querySelector('.a3d-rkcat[data-rkcat="tool:'+id+'"]');
    if(!c)return false;
    c.click();
    return p.classList.contains('open');
  };
  /* __acad3dV69: material test surface. __a3dMaterialCards returns the library itself, not a copy,
     so a test can prove every reader shares one list. */
  window.__a3dMaterialCards=function(){return bimMaterialCards().map(function(c){
    return {name:c.name,kind:c.kind,density:c.density,color:c.color,
            hatch:c.hatch?JSON.parse(JSON.stringify(c.hatch)):null};});};
  window.__a3dMaterialPattern=function(name){return bimMaterialPattern(bimMaterialByName(name));};
  window.__a3dSetMaterial=function(id,name){
    var o=objById(id);if(!o)return false;
    var ok=bimSetMaterial(o,name);
    if(ok){refreshProps();paint();}
    return ok;
  };
  window.__a3dMaterialOf=function(id){var o=objById(id);return (o&&o.materialName)||null;};
  window.__a3dObjVolume=function(id){return bimObjVolume(objById(id));};
  window.__a3dObjMass=function(id){return bimObjMass(objById(id));};
  window.__acad3dV74='scheduleregistry,beamschedulereachable,derivedbrowserlist,derivedsheetsources,registerschedule,matcolspublished';
  /* __acad3dV74: the schedule extension API. A domain pack registers a takeoff and it appears in
     the Project Browser, opens, exports to CSV and can be placed on a sheet -- with no edit to any
     of the three lists that used to have to be kept in step by hand. */
  window.__a3dRegisterSchedule=bimRegisterSchedule;
  /* __acad3dV74: a registered schedule's build() has to be able to ENUMERATE the model, and
     nothing exposed it -- only __a3dObjSnapshot(id), which needs an id you do not have yet. The
     first build of this phase discovered that by writing a bridge girder takeoff and finding it
     had nothing to iterate. Returns snapshots rather than live objects: a schedule is a read, and
     handing out live references would let a takeoff quietly mutate the model it is measuring. */
  window.__a3dObjects=function(){
    return A3D.objs.map(function(o){
      return {id:o.id,name:o.name,t:o.t,materialName:o.materialName||null,
        levelId:(o.bim&&o.bim.levelId)||null,
        bim:o.bim?JSON.parse(JSON.stringify(o.bim)):null};
    });
  };
  window.__a3dScheduleKeys=function(){return bimScheduleKeys();};
  /* Published so a domain reuses the same Material / Volume / Mass columns V69 defined rather than
     inventing a parallel set that rounds differently. Copied, so a caller cannot mutate ours. */
  window.__a3dMaterialCols=function(){return BIM_MAT_COLS.map(function(c){
    return {key:c.key,label:c.label,fmt:c.fmt};});};
  window.__a3dMaterialRowFor=function(id){var o=objById(id);return o?bimMatRow(o):null;};
  /* What the Project Browser actually offers, read from the rendered tree rather than from the
     registry -- the bug this phase fixed was a registry and a rendered list disagreeing. */
  window.__a3dBrowserSchedules=function(){
    var els=document.querySelectorAll('#a3d-browser [data-a3dbsched]'),out=[],i;
    for(i=0;i<els.length;i++)out.push({key:els[i].getAttribute('data-a3dbsched'),
      label:els[i].textContent.trim()});
    return out;
  };
  window.__a3dOpenSchedule=function(cat){
    if(!SCHEDULE_DEFS[cat]||!el.schedcat)return false;
    el.schedcat.value=cat;
    if(el.schedcat.value!==cat)return false;   // the option was never added
    refreshSchedule();
    return true;
  };
  window.__a3dScheduleRows=function(cat){
    var def=SCHEDULE_DEFS[cat];
    if(!def)return null;
    return {cols:def.cols.map(function(c){return c.key;}),rows:def.build()};
  };
  /* __acad3dV68: which side each panel is on, measured from the rendered boxes rather than from
     the class names -- the defect this phase fixes is that both panels were on the same side,
     which every state-level probe would have reported as "both present, both correct". */
  window.__a3dPanelSides=function(){
    function box(e){if(!e)return null;var r=e.getBoundingClientRect();
      return {x:Math.round(r.left),w:Math.round(r.width),h:Math.round(r.height),
              shown:!!(e.offsetParent!==null)&&r.width>0};}
    var props=document.getElementById('a3d-propssec');
    var browser=document.getElementById('a3d-browser');
    var right=document.getElementById('a3d-right');
    var vp=el.root?el.root.querySelector('.a3d-vp'):null;
    var vpR=vp?vp.getBoundingClientRect():null;
    return {
      props:box(props), browser:box(browser), right:box(right), vp:box(vp),
      propsInRight:!!(props&&right&&right.contains(props)),
      browserInDock:!!(browser&&document.getElementById('a3d-leftpanel')&&
        document.getElementById('a3d-leftpanel').contains(browser)),
      propsRightOfViewport:!!(props&&vpR&&props.getBoundingClientRect().left>=vpR.right-1),
      browserLeftOfViewport:!!(browser&&vpR&&browser.getBoundingClientRect().right<=vpR.left+1)
    };
  };
  /* __acad3dV67: status bar test surface. Reads the RENDERED bar rather than the state behind
     it, because the defect this phase fixes is a display one -- state that exists but is not
     shown anywhere in this mode. A probe of A3D_SNAP would pass on the pre-change file. */
  window.__a3dStatusBar=function(){
    var bar=document.getElementById('a3d-statusbar');
    if(!bar)return null;
    var snaps={},btns=bar.querySelectorAll('[data-a3dsnap]'),i;
    for(i=0;i<btns.length;i++)snaps[btns[i].getAttribute('data-a3dsnap')]=btns[i].classList.contains('on');
    var lvlSel=bar.querySelector('#a3d-stlevel');
    var r=bar.getBoundingClientRect(),rootR=el.root?el.root.getBoundingClientRect():null;
    return {
      hint:(bar.querySelector('#a3d-sthint')||{}).textContent||'',
      coords:(bar.querySelector('#a3d-stcoords')||{}).textContent||'',
      levelValue:lvlSel?lvlSel.value:null,
      levelOptions:lvlSel?Array.prototype.map.call(lvlSel.options,function(o){return o.value;}):[],
      snaps:snaps,
      visible:!!(bar.offsetParent!==null),
      height:Math.round(r.height),
      atBottomOfShell:!!(rootR&&Math.abs(r.bottom-rootR.bottom)<1.5),
      spansShellWidth:!!(rootR&&Math.abs(r.width-rootR.width)<1.5)
    };
  };
  window.__a3dStatusHoverAt=function(sx,sy){
    if(!el.cv)return null;
    var r=el.cv.getBoundingClientRect();
    el.cv.dispatchEvent(new MouseEvent('mousemove',{clientX:r.left+sx,clientY:r.top+sy,bubbles:true}));
    return (document.getElementById('a3d-stcoords')||{}).textContent||'';
  };
  /* __acad3dV58: opening-cut-aware vector plan outlines (DXF + SVG + sheet vector), test surface. */
  window.__a3dWallOpeningBreaks=function(wallId){
    var o=objById(wallId);
    return o?bimWallOpeningBreaks(o):null;
  };
  window.__acad3dV58='openingcutsindxf,openingcutsinsvg,openingcutsinsheetvector,windowglazingline,noDoorSwingSymbolNoDataForIt';
  /* __acad3dV59: Phase 51 graphic override data model, test surface. Data and UI only -- no
     render path reads any of this yet (that's Phase 52). Accepts an id, matching the rest of this
     hook block's own convention, so tests never have to reach into A3D.objs by hand. */
  window.__a3dResolveGraphics=function(oOrId,mode){
    var o=(typeof oOrId==='string')?objById(oOrId):oOrId;
    return o?bimResolveGraphics(o,mode):null;
  };
  window.__a3dSetGraphicsOverride=function(oOrId,mode,key,value){
    var o=(typeof oOrId==='string')?objById(oOrId):oOrId;
    return o?bimSetGraphicsOverride(o,mode,key,value):false;
  };
  window.__a3dClearGraphicsOverride=function(oOrId,mode){
    var o=(typeof oOrId==='string')?objById(oOrId):oOrId;
    return o?bimClearGraphicsOverride(o,mode):false;
  };
  window.__a3dSetTypeGraphics=function(cat,typeId,mode,key,value){
    return bimSetTypeGraphics(cat,typeId,mode,key,value);
  };
  window.__a3dTypeGraphics=function(cat,typeId){
    var t=bimFindType(cat,typeId);
    return t?t.graphics:null;
  };
  window.__acad3dV59='graphicoverrides,typegraphics,instancegraphicsoverride,technicalpresentationmodes,resettotype,dataandUIonlyNoRenderYet';
  /* __acad3dV60: Phase 52a presentation render mode, test surface. */
  window.__a3dSetPresentMode=function(v){A3D.presentMode=!!v;bimSyncPresentPill();paint();};
  window.__a3dPresentMode=function(){return !!A3D.presentMode;};
  /* __acad3dV121: the look a sketch was drawn with; the GL alpha each solid was drawn with; and the
     alpha of the drawing canvas at a point on the page, for everything else on a layer */
  window.__a3dLastLook=function(id){return (A3D.lastLook&&A3D.lastLook[id])?JSON.parse(JSON.stringify(A3D.lastLook[id])):null;};
  window.__a3dLastGlAlpha=function(id){return (A3D.lastGlAlpha&&A3D.lastGlAlpha.hasOwnProperty(id))?A3D.lastGlAlpha[id]:null;};
  window.__a3dPixelAlpha=function(px,py){
    try{
      var r=el.cv.getBoundingClientRect(),sx=Math.round((px-r.left)*el.cv.width/r.width),sy=Math.round((py-r.top)*el.cv.height/r.height);
      return el.cv.getContext('2d').getImageData(sx,sy,1,1).data[3];
    }catch(eP){console.warn('[BIM] The canvas could not be read',eP);return null;}
  };
  window.__a3dLastDrawStyle=function(objId){
    var i;
    for(i=0;i<(A3D.lastPolys||[]).length;i++){
      var p=A3D.lastPolys[i];
      if(p.o&&p.o.id===objId&&p.rBaseFill!==undefined)
        // __acad3dV63: pattern fields added; they read 'none'/null for every object that carries
        // no hatch, so a Phase 52a-era assertion on this object still sees what it expects.
        return {fill:p.rBaseFill,stroke:p.rStroke,lineWidth:p.rLineWidth,opacity:p.rOpacity,shadow:p.rShadow,layerAlpha:p.rLayerAlpha,   /* __acad3dV121 */
                pattern:p.rPattern||'none',patternColor:p.rPatternColor||null,patternScale:p.rPatternScale||null};
    }
    return null;
  };
  window.__a3dLastRoomStyle=function(roomId){
    return (A3D.lastRoomStyle&&A3D.lastRoomStyle[roomId])?A3D.lastRoomStyle[roomId]:null;
  };
  /* __acad3dV105: occupant load and the room colour fill, read from the same functions the
     schedule, the Properties panel and every sink read. */
  window.__a3dOccLoads=function(){return bimOccLoads().map(function(r){return {name:r[0],ft2:r[1],basis:r[2]};});};
  window.__a3dRoomLoad=function(id){
    var o=objById(id);
    if(!o||o.t!=='room')return null;
    return {area:o.area,factor:bimRoomLoadFactor(o),occupants:bimRoomOccupants(o),text:bimRoomOccupantsText(o),hint:bimRoomLoadFactorHint(o)};
  };
  window.__a3dRoomScheme=function(by){if(by!==undefined)bimSetRoomScheme(by);return A3D.roomScheme||'';};
  window.__a3dRoomLegend=function(){return A3D.lastRoomLegend||null;};
  window.__acad3dV105='occupantload,ibc1004_5,roomloadfactor,roomcopyfields,roomcolourfill,roomlegend,schemesinks';
  /* __acad3dV106: the takedown, read from the one function the schedule and the overlay use. */
  window.__a3dColumnLoads=function(){var r=bimColumnLoads();return {rows:r.rows,levels:r.levels,cells:r.cells};};
  window.__a3dTribShown=function(){return A3D.lastTribDrawn||null;};
  window.__a3dGridMark=function(x,z){return bimGridMark(x,z);};
  window.__acad3dV106='levelloads,tributaryvoronoi,loadtakedown,colloadschedule,tribareaoverlay,gridmark';
  /* __acad3dV107: the sun and its shadows, read from the functions the renderer uses. */
  window.__a3dSunCalc=function(lat,lon,tz,d,t){return bimSunCalc(lat,lon,tz,d,t);};
  window.__a3dSunSettings=function(){return bimSunSettings();};
  window.__a3dSunNow=function(){return bimSunNow();};
  window.__a3dShadowInfo=function(){return A3D.lastShadows||null;};
  window.__a3dShadowPoints=function(id){
    var sun=bimSunNow(),g,s,list,i;
    if(sun.missing||!(sun.elevation>0))return null;
    g=bimShadowGround();s=bimSunVector(sun);list=bimShadowCasters(g);
    for(i=0;i<list.length;i++)if(list[i].id===id)return list[i].w.map(function(w){var p=bimShadowPoint(w,s,g);return {x:p[0],z:p[1],y:w[1]};});
    return [];
  };
  window.__a3dSunPath=function(){return A3D.lastSunPath||null;};
  /* __acad3dV105b: area plans, through the same functions the schedule and the overlay read. */
  window.__a3dLevelAreas=function(levelId){return bimLevelAreas(levelId||A3D.activeLevel);};
  window.__a3dGrossRings=function(levelId){
    var r=bimLevelGrossRings(levelId||A3D.activeLevel);
    return {error:r.error||null,rings:(r.rings||[]).map(function(x){return {pts:x.pts,area:x.area,srcIds:x.srcIds};})};
  };
  window.__a3dAreaDrawn=function(){return A3D.lastAreaDrawn||null;};
  window.__a3dWallFaceRings=function(id){var o=objById(id);return o?bimWallFaceRings(o):null;};
  window.__a3dRayPolyDepth=function(poly,closed,p,n,lim){return bimRayPolyDepth(poly,!!closed,p,n,lim);};
  window.__a3dWallInsetAt=function(id,p,n){var o=objById(id),r=o?bimWallFaceRings(o):null;return r?bimWallInsetAt(r,p,n):null;};
  window.__acad3dV105b='wallbasepts,wallfacerings,grossrings,levelareas,arealevel,areaplan';
  window.__acad3dV107='noaasun,sunsettings,groundshadows,sunpath,sunstudy';
  /* __acad3dV108: terrain, read from the functions the drawing, Properties and the schedule use. */
  window.__a3dDelaunay=function(P){return bimDelaunay(P);};
  window.__a3dTerrainTin=function(id){var o=objById(id),t=o?bimTerrainTin(o):null;   /* __acad3dV144: and its breaklines, boundary, own faces */
    return t?{P:t.P,H:t.H,tris:t.tris,constraints:t.constraints,unforced:t.unforced,outside:t.outside?Object.keys(t.outside).map(Number):[],ownFaces:t.ownFaces}:null;};
  window.__a3dContours=function(id,step){var o=objById(id),t=o?bimTerrainTin(o):null;return t?bimContours(t,step||bimTerrainInterval(o,t)):null;};
  window.__a3dParseSurvey=function(text,fmt){return bimParseSurvey(text,fmt);};
  window.__a3dSurveyToModel=function(pts,units,base,tn){return bimSurveyToModel(pts,units,base,tn);};
  window.__a3dMakeTerrain=function(model){var o=bimCreateTerrain(model,null,false);return o?o.id:null;};
  window.__a3dCutFill=function(id,pad,y){var o=objById(id);return o?bimCutFill(bimTerrainTin(o),pad,y):null;};
  window.__a3dEarthwork=function(){return bimEarthwork();};
  window.__a3dTerrainShown=function(){return A3D.lastTerrainDrawn||null;};
  window.__acad3dV108='delaunay,surveyimport,terrain,contours,earthworkprism,buildingpads';
  window.__acad3dV60='presentationrendertoggle,livecanvaspoche,lineweighthierarchy,dropshadow,roomfillpresentation,offbydefaultnorenderchange,patterndeferredtophase53';
