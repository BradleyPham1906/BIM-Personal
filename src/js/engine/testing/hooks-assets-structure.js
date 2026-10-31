  /* __acad3dV124: the library, read and driven */
  window.__a3dLibrary=function(){
    var all=A3D_FAMLIB.concat(A3D_ASSET_BUILTINS);
    return all.map(function(e){
      return {id:e.id,kind:bimAssetKind(e),name:e.name,category:e.category,builtin:!!e.builtin,
        count:e.count||0,unit:e.unit||null,source:e.source||null,size:e.mesh&&e.mesh.size?e.mesh.size.slice():null,
        thumb:typeof e.thumb==='string'&&e.thumb.indexOf('data:image/png')===0};
    });
  };
  window.__a3dBlockSave=function(name,ids){
    var e=bimBlockSave(name,ids||bimAssetSelIds());
    if(e)refreshFamilyPanel();
    return e?e.id:null;
  };
  window.__a3dBlockInsert=function(id,x,z){return bimInsertBlock(bimFamilyLibraryGet(id),[x,z]);};
  window.__a3dTemplateSave=function(name){var e=bimTemplateSave(name);if(e)refreshFamilyPanel();return e?e.id:null;};
  window.__a3dTemplateUse=function(id){return bimTemplateUse(bimFamilyLibraryGet(id));};
  window.__a3dAssetDropAt=function(spec,cx,cy){return bimAssetDropAt(spec,cx,cy);};
  window.__a3dViewCentrePlan=function(){return bimViewCentrePlan();};
  window.__a3dImportGuess=function(mesh){return bimGuessImportUnit(mesh);};
  window.__a3dImportMesh=function(mesh,unit,zUp){return bimImportModelMesh(mesh,unit,!!zUp);};
  window.__a3dAssetsUI=function(){return {q:A3D_ASSETS_UI.q,closed:JSON.parse(JSON.stringify(A3D_ASSETS_UI.closed)),dragging:!!(A3D_ASDRAG&&A3D_ASDRAG.on)};};
  /* __acad3dV125: the analysis, read as data */
  window.__a3dStructModel=function(){
    var m=bimAnalyticalModel();
    return {nodes:m.nodes.map(function(n){return {p:n.p.slice(),sup:n.sup,why:n.supWhy};}),
      els:m.els.map(function(e){return {member:e.memberId,name:e.name,kind:e.kind,n1:e.n1,n2:e.n2,L:e.L,rel:e.rel.slice(),
        E:e.E,G:e.G,A:e.sec.A,Iy:e.sec.Iy,Iz:e.sec.Iz,J:e.sec.J,rho:e.rho,ey:e.ax.ey.slice()};}),
      notAnalysed:JSON.parse(JSON.stringify(m.notAnalysed)),skipped:JSON.parse(JSON.stringify(m.skipped))};
  };
  window.__a3dStructSolve=function(combo,selfWeight){
    var c=bimCombo(combo||A3D_STRUCT.combo);
    if(!c)return {error:'no such combination'};
    var r=bimFrameSolve(bimAnalyticalModel(),c,selfWeight===undefined?A3D_STRUCT.selfWeight:!!selfWeight);
    if(r.error)return {error:r.error,node:r.node,dof:r.dof};
    return JSON.parse(JSON.stringify({combo:r.combo,disp:r.disp,reactions:r.reactions,equilibrium:r.equilibrium,
      members:r.members.map(function(m){return {id:m.id,name:m.name,kind:m.kind,L:m.L,N:m.N,V:m.V,Mz:m.Mz,My:m.My,T:m.T,dmax:m.dmax,drel:m.drel,
        samples:m.samples.map(function(s){return {s:s.s,N:s.N,Mz:s.Mz,My:s.My,Vy:s.Vy};})};})}));
  };
  window.__a3dStructSettings=function(patch){
    var k;if(patch)for(k in patch)if(patch.hasOwnProperty(k)&&k!=='res')A3D_STRUCT[k]=patch[k];
    return {combo:A3D_STRUCT.combo,selfWeight:A3D_STRUCT.selfWeight,show:A3D_STRUCT.show,diagram:A3D_STRUCT.diagram,
      deflected:A3D_STRUCT.deflected,current:!!bimStructCurrent(),error:A3D_STRUCT.res&&A3D_STRUCT.res.error||null};
  };
  window.__a3dStructEditFor=function(id,st){
    var o=objById(id);if(!bimIsFrameMember(o))return false;
    bimStructEdit(o,function(s){var k;for(k in s)if(s.hasOwnProperty(k))delete s[k];for(k in st)if(st.hasOwnProperty(k))s[k]=JSON.parse(JSON.stringify(st[k]));});
    return true;
  };
  window.__a3dStructOf=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(bimStructOf(o))):null;};
  window.__a3dStructDrawn=function(){paint();return A3D.lastStructDrawn?JSON.parse(JSON.stringify(A3D.lastStructDrawn)):null;};
  window.__a3dCombos=function(){return bimCombos().map(function(c){return c.name;});};
  /* __acad3dV127: the alignment */
  function bimJ(x){return x===null||x===undefined?null:JSON.parse(JSON.stringify(x));}
  window.__a3dAlignFromPts=function(pts,radii,sta0){
    var al=bimNewAlignment(pts,[0,0,0],0);
    if(radii)al.radii=radii.slice();
    if(isFinite(sta0))al.sta0=sta0;
    pushUndo();A3D.objs.push(al);refreshTree();paint();saveSoon();
    return al.id;
  };
  /* an OPEN polyline, as the polyline tool ends one on Enter */
  window.__a3dOpenPolyline=function(pts,bulges){
    startSketch('poly');if(!A3D.sk)return null;
    A3D.sk.pts=(pts||[]).slice();
    if(bulges)A3D.sk.bulges=bulges.slice();
    var o=finishPoly(true);
    return o?A3D.sel:null;
  };
  window.__a3dAlignEditFor=function(id,patch){
    var o=objById(id);if(!bimIsAlignment(o))return false;
    return bimAlignEdit(o,function(c){for(var k in patch)if(patch.hasOwnProperty(k))c[k]=bimJ(patch[k]);});
  };
  window.__a3dAlignGeom=function(id){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignGeom(o)):null;};
  window.__a3dAlignPointAt=function(id,s){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignPointAt(bimAlignGeom(o),s)):null;};
  window.__a3dStationOffset=function(id,p){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignStationOffset(bimAlignGeom(o),p)):null;};
  window.__a3dProfileGeom=function(id){var o=objById(id);return bimIsAlignment(o)&&o.profile?bimJ(bimProfileGeom(o.profile,bimAlignGeom(o))):null;};
  window.__a3dProfileElevAt=function(id,s){var o=objById(id);if(!bimIsAlignment(o)||!o.profile)return null;return bimJ(bimProfileElevAt(bimProfileGeom(o.profile,bimAlignGeom(o)),s));};
  window.__a3dTerrainBands=function(id,mode){var o=objById(id);if(!o||o.t!=='terrain')return null;var b=bimBandsOf(o,mode);   /* __acad3dV145: and cutfill */
    return b?{bands:b.bands.map(function(x){return {label:x.label,col:x.col,area:x.area,share:x.share};}),tri:b.tri,total:b.total}:null;};
  window.__a3dLandXmlDoc=function(ids){return bimLandXmlDoc(ids||null);};
  window.__a3dLandXmlImport=function(text,name){return bimLandXmlImport(text,name||'test.xml');};
  window.__a3dBreakline=function(){return bimBreaklineCommand();};
  window.__a3dTerrainBoundary=function(){return bimBoundaryCommand();};
  window.__a3dTerrainSetView=function(id,mode){return bimTerrainSetView(objById(id),mode);};
  window.__a3dTerrainEdit=function(id,what){return bimTerrainEdit(objById(id),what);};
  window.__a3dTerrainView=function(mode){return bimTerrainViewCommand(mode);};
  window.__a3dModelToSurvey=function(id,x,z,y){return bimModelToSurvey(objById(id),x,z,y);};
  window.__a3dGrade=function(padIds,terId){   /* __acad3dV145 */
    var pads=(padIds||[]).map(objById).filter(bimIsPad);if(!pads.length)pads=A3D.objs.filter(bimIsPad);
    var ter=bimGradeExistingFor(pads,terId?objById(terId):null);if(!ter)return {error:'no existing surface under the pads'};
    return JSON.parse(JSON.stringify(bimGrade(pads,ter)));
  };
  window.__a3dGradeInfo=function(id){var o=objById(id);return o&&o.grading?{grading:JSON.parse(JSON.stringify(o.grading)),stale:bimGradeStale(o),name:o.name}:null;};
  window.__a3dGradeSpokes=function(padId,terId){
    var pad=objById(padId),ter=objById(terId);if(!bimIsPad(pad)||!ter)return null;var r=bimGradePad(pad,bimTinIndexOf(ter));if(r.error)return r;
    return {P:r.P,Z:r.Z,slopes:r.slopes,ring:r.ring,spokes:r.spokes.map(function(s){return {p:s.p,u:s.u,k:s.k,valley:!!s.valley,corner:s.corner===undefined?null:s.corner,
      r:s.r.off?{off:true}:{t:s.r.t,end:s.r.end,h:s.r.h,kind:s.r.kind,dir:s.r.dir}};})};
  };
  window.__a3dTinVolume=function(a,b){var A=objById(a),B=objById(b);return A&&B?bimTinVolume(bimTerrainTin(A),bimTerrainTin(B)):null;};
  window.__a3dSetPadSlope=function(id,which,v){return bimSetPadSlope(objById(id),which,v);};
  window.__a3dSpotsShown=function(){return A3D.lastSpotsDrawn||null;};
  window.__a3dSpotElev=function(id){var o=objById(id);return bimIsPoint(o)?bimSpotElev(o):null;};
  window.__a3dHistCommit=function(msg){return bimHistCommit(msg);};   /* __acad3dV146 */
  window.__a3dHistory=function(){var H=bimHist();return {head:H.head,commits:JSON.parse(JSON.stringify(H.commits)),size:bimHistSize()};};
  window.__a3dHistChanges=function(){return JSON.parse(JSON.stringify(bimHistChanges()));};
  window.__a3dHistCommitDiff=function(id){var c=bimHistCommitById(id);return c?JSON.parse(JSON.stringify(bimHistCommitDiff(c))):null;};
  window.__a3dHistRestore=function(id){return bimHistRestore(id);};
  window.__a3dHistOf=function(id){return JSON.parse(JSON.stringify(bimHistOf('o:'+id)));};
  window.__a3dHash=function(s){return bimHash(String(s));};
  window.__a3dCanon=function(v){return bimCanon(v);};
  window.__a3dRightPanel=function(){var r=bimRightApply();return r;};   /* __acad3dV147 */
  window.__a3dLeftPanel=function(){return bimLeftState();};   /* __acad3dV166b */
  window.__a3dSetLeftWidth=function(w){return bimLeftSetWidth(w);};
  window.__a3dRightSetWidth=function(w){return bimRightSetWidth(w);};
  window.__a3dRightToggleMin=function(on){return bimRightToggleMin(on);};
  window.__a3dTerrainLegend=function(){return A3D.lastTerrainLegend||null;};
  window.__a3dTinHeightAt=function(tid,x,z){var o=objById(tid);return o&&o.t==='terrain'?bimTinHeightAt(bimTerrainTin(o),x,z):null;};
  window.__a3dAlignGround=function(id){var o=objById(id);return bimIsAlignment(o)?bimJ(bimAlignGround(o,bimAlignGeom(o))):null;};
  window.__a3dAlignDrawn=function(){paint();return bimJ(A3D.lastAlignDrawn||{});};
  window.__a3dFmtStation=function(s){return bimFmtStation(s);};
  window.__a3dStationMark=function(){return bimJ(A3D.stationMark||null);};
  window.__acad3dV127='alignmentobject,pidesign,circularcurves,overlaprefused,stationing,stationoffset,profile,verticalcurves,'+
    'highlowpoint,kvalue,tinheight,groundprofile,alignmentdrawing,stationticks,profileview,alignmentprops,profileprops,'+
    'alignmentcommand,profileviewcommand,stationcommand,alignmentbutton,alignmentschedule,profileschedule,alignmentexport,alignmenttransform';
  /* __acad3dV126: section profiles */
  window.__a3dProfileProps=function(p){return bimProfileProblem(p)?null:bimProfileProps(p);};
  window.__a3dProfileProblem=function(p){return bimProfileProblem(p);};
  window.__a3dProfileLoops=function(p){return bimProfileProblem(p)?null:bimProfileLoops(p);};
  window.__a3dSweepVolume=function(p,len){return bimMeshSignedVolume(bimSweepMesh(p,len,function(y,z,s){return [s,y,z];}));};
  window.__a3dMeshVolume=function(id){var o=objById(id);return o&&o.mesh?bimMeshSignedVolume(o.mesh):null;};
  window.__a3dMemberSection=function(id){
    var o=objById(id);if(!bimIsFrameMember(o))return null;
    var pf=bimMemberSection(o);
    return {section:JSON.parse(JSON.stringify(pf)),props:bimProfileProblem(pf)?null:bimProfileProps(pf),problem:bimProfileProblem(pf)};
  };
  window.__a3dSectionTypes=function(){
    bimEnsureTypes();var out=[];
    ['column','beam'].forEach(function(c){(A3D.types[c]||[]).forEach(function(ty){
      if(ty.params&&ty.params.profile)out.push({cat:c,id:ty.id,name:ty.name,material:ty.params.material||'',shape:ty.params.profile.shape});});});
    return out;
  };
  window.__a3dTypeParams=function(cat,id){var ty=bimFindType(cat,id);return ty?JSON.parse(JSON.stringify(ty.params)):null;};
  window.__acad3dV126='profileshapes,profileprops,profileloops,sweepmesh,sectioncatalogue,typeseeding,typegroups,'+
    'edittypelocked,beamsection,columnsection,sectionrebuilds,sizelocked,sectionanalysis,sectionprops,assetsections';
  window.__acad3dV125='analyticalmodel,nodemerge,membersplit,rectsection,materialmodulus,supports,pinnedends,'+
    'loadcases,selfweight,lineload,pointload,lateralload,combinations,directstiffness,rcmband,cholesky,'+
    'unstablerefused,equilibrium,memberforces,shearzero,deflection,analysisdisplay,stale,analyzeoff,'+
    'structuralprops,analysisprops,supportcommand,loadcommand,analyzebutton,memberforceschedule,reactionschedule';
  window.__acad3dV124b='libsavetoast,libtoastonce,libsaveworksagain,libsavereturns';
  window.__acad3dV124='librarykinds,starterset,thumbnails,importunit,importupaxis,blocks,blocklinks,blocklevel,'+
    'selectionmodel,templates,librarypanel,librarysearch,folds,removeasks,clickatviewcentre,dragdrop,dropsnap,'+
    'droponobject,blockcommand,insertcommand,assetscommand,componentopenslibrary';
  window.__acad3dV123='projectunits,valuekinds,clicktotype,valuebox,noundoonclick,copyonfirstmove,bodydragisgizmomove,'+
    'carrybim,copyatoffset,flooroutlineturns,padatsketch,faces,facekeys,presspull,pushpull,pushsnap,pushrange,'+
    'sketchpull,primitivedimensions,primitivebase,openingfaces';
  window.__a3dGripAt=function(x,y){
    var g=bimPickGrip(x,y);
    return g?{x:g.x,y:g.y,idx:g.idx,objId:g.objId,kind:g.kind,elev:g.elev}:null;
  };
  window.__a3dCanvasRect=function(){
    if(!el.cv)return null;
    var r=el.cv.getBoundingClientRect();
    return {left:r.left,top:r.top,width:r.width,height:r.height};
  };
  window.__a3dSnapSet=function(o){
    if(o&&o.hasOwnProperty('point'))A3D_SNAP.point=!!o.point;
    if(o&&o.hasOwnProperty('grid'))A3D_SNAP.grid=!!o.grid;
    if(o&&o.hasOwnProperty('ortho'))A3D_SNAP.ortho=!!o.ortho;
    return {point:A3D_SNAP.point,grid:A3D_SNAP.grid,ortho:A3D_SNAP.ortho};
  };
  window.__a3dPlanScreenPoints=function(id){
    var o=objById(id);if(!o)return null;
    var ep=bimGetEditablePoints(o);
    var pts=ep?ep.pts:o.pts,y=ep?ep.y:o.y;
    if(!pts)return null;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    return pts.map(function(p){var s=toScreen(bimWorldPt(o,p,y),V,W,H);return [s[0],s[1]];});
  };
  window.__acad3dV75='worldoffsetinvariant,gripsfollowmove,sketchdrawpickmarqueeoffset,roommarquee,snapcandidatesworld,gripdraginverse';
  window.__a3dSetLockedById=function(objId,val){var o=objById(objId);return o?bimSetLocked(o,val):false;};
  window.__a3dSketchPts=function(objId){var o=objById(objId);return (o&&o.pts)?JSON.parse(JSON.stringify(o.pts)):null;};
  window.__a3dConPickState=function(){return A3D.conPick?JSON.parse(JSON.stringify(A3D.conPick)):null;};
  window.__a3dCancelConstraintPick=cancelConstraintPick;
  window.__a3dDragGripTo=function(objId,idx,x,z){
    var o=objById(objId);if(!o)return null;
    bimDragSketchPoint(o,idx,[x,z]);
    if(o.constraints&&o.constraints.length)bimResolveSketch(o,idx,{silent:true});
    bimPropagateFrom([o.id],'rebuild');
    return JSON.parse(JSON.stringify(o.pts));
  };
  window.__acad3dV46='buildings,activebuilding,site,buildinglevelhierarchy,buildingrehostonlete,buildingpersistence';
  window.__a3dBuildings=function(){bimEnsureBuildings();return JSON.parse(JSON.stringify(A3D.buildings));};
  window.__a3dAddBuilding=function(){addBuilding();return A3D.activeBuilding;};
  window.__a3dDeleteBuilding=function(id){removeBuilding(id);return JSON.parse(JSON.stringify(A3D.buildings));};
  window.__a3dRenameBuilding=function(id,name){updateBuilding(id,'name',name);return JSON.parse(JSON.stringify(A3D.buildings));};
  window.__a3dSite=function(){bimEnsureBuildings();return JSON.parse(JSON.stringify(A3D.site));};
  window.__a3dSetSite=function(name){updateSite('name',name);return JSON.parse(JSON.stringify(A3D.site));};
  window.__a3dActiveBuilding=function(){bimEnsureBuildings();return A3D.activeBuilding;};
  window.__a3dSetActiveBuilding=function(id){setActiveBuilding(id);return A3D.activeBuilding;};
  window.__a3dLevelBuilding=function(levelId){
    var i;for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId)return A3D.levels[i].buildingId||null;
    return null;
  };
  window.__acad3dV47='classifications,classificationcrud,classifyobject,classdeletefailsafe,classificationbrowsergroup';
  window.__a3dClassifications=function(){return JSON.parse(JSON.stringify(A3D.classifications));};
  window.__a3dAddClassification=function(code,desc){var c=addClassification(code,desc);return c?c.id:null;};
  window.__a3dUpdateClassification=function(id,field,val){updateClassification(id,field,val);return JSON.parse(JSON.stringify(A3D.classifications));};
  window.__a3dDeleteClassification=function(id){removeClassification(id);return JSON.parse(JSON.stringify(A3D.classifications));};
  window.__a3dSetObjClass=function(objId,classId){return setObjectClassification(objId,classId);};
  window.__a3dObjClass=function(objId){var o=objById(objId);return o?(o.classId||null):null;};
  window.__a3dClassificationUseCount=bimClassificationInUseCount;
  window.__a3dOpenClassificationDlg=openClassificationDlg;
  window.__acad3dV48='mergewalls,checkmodel,linkedclone,syncclones,meshsanitydiagnostic';
  window.__a3dMergeWalls=function(idA,idB){
    var a=objById(idA),b=objById(idB);
    if(!a||!b)return {error:'object not found'};
    return bimMergeWalls(a,b);
  };
  window.__a3dApplyMergeWalls=function(idA,idB){
    A3D.sel=idA;A3D.sel2=idB;
    applyMergeWalls();
    return A3D.objs.map(function(o){return o.id;});
  };
  window.__a3dCheckModel=bimCheckModel;
  window.__a3dOpenCheckModelDlg=openCheckModelDlg;
  window.__a3dMeshSanityCheck=bimMeshSanityCheck;
  window.__a3dMeshClosureCheck=bimMeshClosureCheck;
  window.__a3dCloneLinked=cloneLinked;
  window.__a3dSyncLinkedClones=syncLinkedClones;
  window.__a3dLinkedClonesOf=function(id){return bimLinkedClonesOf(id).map(function(o){return o.id;});};
  window.__a3dObjLinkSource=function(id){var o=objById(id);return o?(o.linkSourceId||null):null;};
  window.__acad3dV49='sketchconstraints,pointonline,midpoint,symmetric_pt,symmetric_line';
  window.__acad3dV50='dependencygraph,derivededges,topologicalorder,dirtymarking,cycledetection,dependenciespanel';
