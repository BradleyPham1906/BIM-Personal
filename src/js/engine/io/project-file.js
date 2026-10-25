  // ---- __acad3dV14: Project file save/load. Builds on bimSnapshotState/bimRestoreState (the
  // existing, already-tested undo/redo machinery) rather than a parallel serialization system --
  // a project file is just that same snapshot wrapped in a versioned envelope so a random or
  // foreign JSON file can be confidently rejected instead of silently corrupting the model. ----
  function bimBuildProjectEnvelope(){
    return JSON.stringify({app:'acad3d-project',formatVersion:1,savedAt:new Date().toISOString(),
      data:{objs:A3D.objs,levels:A3D.levels,grids:A3D.grids,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer,views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:A3D.levelFilter,types:A3D.types,activeWallType:A3D.activeWallType,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null,resultLayers:A3D.resultLayers||[],pres:A3D.pres||null}});   /* __acad3dV146, __acad3dV148 */
  }
  function bimParseProjectEnvelope(text){
    var parsed;
    try{parsed=JSON.parse(text);}catch(eP){return {error:'not valid JSON'};}
    if(!parsed||typeof parsed!=='object')return {error:'not a recognized project file'};
    if(parsed.app!=='acad3d-project'||!parsed.data)return {error:'not a recognized project file'};
    var warn=null;
    if(parsed.formatVersion>1)warn='this project file is from a newer version, some data may not load correctly';
    return {data:parsed.data,warn:warn};
  }
  /* __acad3dV115: with several projects open, "project.acad3d.json" and "plan.pdf" no longer say
     which project a file came from. Every download starts with the project's name, the way
     AutoCAD names a plot "<drawing>-Layout1.pdf". Characters no file system accepts become _. */
  function bimFileStem(){
    var s=bimProjectLabel().replace(/[\\\/:*?"<>|\u0000-\u001f]+/g,'_').replace(/^[\s.]+|[\s.]+$/g,'');
    return s.slice(0,80)||'project';
  }
  function bimExportProjectFile(){
    try{
      var json=bimBuildProjectEnvelope();
      bimTriggerDownload(json,bimFileStem()+'.acad3d.json','application/json');
      a3dToast('Project saved as '+bimFileStem()+'.acad3d.json ('+A3D.objs.length+' object(s))');
    }catch(eS){console.warn('[BIM] Project export failed: ',eS);a3dToast('Project export failed: '+(eS&&eS.message?eS.message:eS));}
  }
  /* __acad3dV115: a project file opens in a tab of its own, the way OPEN works in AutoCAD and in
     Revit. It used to replace the model on screen behind a confirm(), so the only way to look at a
     second project was to give up the first. Nothing is replaced now, so there is nothing to
     confirm; the project that was on screen stays in its own tab. */
  function bimImportProjectFile(text,filename){
    filename=filename||'project.acad3d.json';
    var res=bimParseProjectEnvelope(text);
    if(res.error){a3dToast(filename+': '+res.error);return false;}
    var id=bimDocsOpenData(res.data,filename);
    if(!id)return false;
    fitScene();
    var msg='Opened '+filename+' in a new tab: '+(res.data.objs?res.data.objs.length:0)+' object(s)';
    if(res.warn)msg+=' \u2014 '+res.warn;
    a3dToast(msg);
    return true;
  }
  function bimOpenProjectFileObj(file){
    if(!file)return;
    var name=file.name||'project.json',ext=(name.split('.').pop()||'').toLowerCase();
    if(ext!=='json'){
      a3dToast(name+' is not a project file. Open takes .json project files; use Import for DXF, IFC, OBJ or STL.');
      return;
    }
    var reader=new FileReader();
    reader.onerror=function(){console.warn('[BIM] A project file could not be read: '+name);a3dToast('Failed to read '+name);};
    reader.onload=function(ev){
      try{bimImportProjectFile(ev.target.result,name);}
      catch(eI){console.warn('[BIM] Opening a project file crashed:',eI);a3dToast('Opening '+name+' failed: '+(eI&&eI.message?eI.message:eI));}
    };
    reader.readAsText(file);
  }
  function bimOpenProjectPicker(){
    var fi=document.getElementById('a3d-projin');
    if(!fi){
      console.warn('[BIM] The project file picker is not built yet');
      a3dToast('The workspace is still loading; try Open again in a moment');
      return false;
    }
    fi.value='';fi.click();
    return true;
  }
