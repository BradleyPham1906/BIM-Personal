import { A3D_DOCS } from '../core/state.js';
import { bimFileDownload, bimFileRead } from './file-save.js';
import { BIM_APP_VERSION } from '../ui/guide-versions.js';
import { fitScene } from '../ui/tool-palette.js';
import { bimProjectRecord } from '../core/objects-save.js';
import { bimProjectLabel } from '../ui/project-tabs.js';
import { bimDocsOpenData } from '../assets/templates.js';
import { bimBimgForFile, bimBimgFromFile } from '../sheets/board-images.js';
import { a3dToast } from '../bim/csg-booleans.js';

  // ---- __acad3dV14: Project file save/load. Builds on bimSnapshotState/bimRestoreState (the
  // existing, already-tested undo/redo machinery) rather than a parallel serialization system --
  // a project file is just that same snapshot wrapped in a versioned envelope so a random or
  // foreign JSON file can be confidently rejected instead of silently corrupting the model. ----
  /* __acad3dV172g: envelope version 2 (D4). Its data is bimProjectRecord() itself -- the one list of what a project is,
     with the view (cam) and the id counter (seq) that version 1 left out -- and the app's version; the record's docId
     belongs to this browser and is not written. V172f and older read a version-2 file with their "newer version" warning
     and take every field they know (part 14.7). */
  function bimBuildProjectEnvelope(){
    var env={app:'acad3d-project',formatVersion:2,savedAt:new Date().toISOString(),appVersion:BIM_APP_VERSION.v,
      data:bimProjectRecord()},im=bimBimgForFile();
    if(im)env.imgs=im;   /* __acad3dV174a: the boards' images, each once by its hash; an older version leaves the field */
    return JSON.stringify(env);
  }
  function bimParseProjectEnvelope(text){
    var parsed;
    try{parsed=JSON.parse(text);}catch(eP){return {error:'not valid JSON'};}
    if(!parsed||typeof parsed!=='object')return {error:'not a recognized project file'};
    if(parsed.app!=='acad3d-project'||!parsed.data)return {error:'not a recognized project file'};
    var warn=null;
    if(parsed.formatVersion>2)warn=   /* __acad3dV172g: version 2 is this build's */
      'this project file is from a newer version, some data may not load correctly';
    return {data:parsed.data,warn:warn,imgs:parsed.imgs||null};
  }
  /* __acad3dV115: with several projects open, "project.acad3d.json" and "plan.pdf" no longer say
     which project a file came from. Every download starts with the project's name, the way
     AutoCAD names a plot "<drawing>-Layout1.pdf". Characters no file system accepts become _. */
  function bimFileStem(){
    var s=bimProjectLabel().replace(/[\\\/:*?"<>|\u0000-\u001f]+/g,'_').replace(/^[\s.]+|[\s.]+$/g,'');
    return s.slice(0,80)||'project';
  }
  /* __acad3dV172g: a download of the plain file, whatever the browser (the test hooks' export); Save itself is
     bimFileSave in io/file-save.js */
  function bimExportProjectFile(){
    try{bimFileDownload(A3D_DOCS.active,'json');}
    catch(eS){console.warn('[BIM] Project export failed: ',eS);a3dToast('Project export failed: '+(eS&&eS.message?eS.message:eS));}
  }
  /* __acad3dV172e: decision D3. The browser keeps best-effort storage only while it has room; persist() asks it to
     keep this app's. Asked once, at the first Save -- a gesture, never on load (web.dev); Firefox shows a prompt,
     Chrome and Safari answer silently, and false is the usual answer in a Safari tab, so it is not an error. */
  var A3D_PERSIST={asked:false,granted:null};
  function bimAskPersist(){
    if(A3D_PERSIST.asked)return;
    A3D_PERSIST.asked=true;
    try{
      if(!navigator.storage||typeof navigator.storage.persist!=='function')return;
      navigator.storage.persisted().then(function(p){
        if(p){A3D_PERSIST.granted=true;return null;}
        return navigator.storage.persist().then(function(g){A3D_PERSIST.granted=!!g;});
      })['catch'](function(eQ){console.warn('[BIM] The browser could not be asked to keep this app\'s storage.',eQ);});
    }catch(eP){console.warn('[BIM] The browser could not be asked to keep this app\'s storage.',eP);}
  }
  /* __acad3dV115: a project file opens in a tab of its own, the way OPEN works in AutoCAD and in
     Revit. It used to replace the model on screen behind a confirm(), so the only way to look at a
     second project was to give up the first. Nothing is replaced now, so there is nothing to
     confirm; the project that was on screen stays in its own tab. */
  function bimImportProjectFile(text,filename){
    filename=filename||'project.acad3d.json';
    var res=bimParseProjectEnvelope(text);
    if(res.error){a3dToast(filename+': '+res.error);return false;}
    if(res.imgs)bimBimgFromFile(res.imgs);   /* __acad3dV174a */
    var id=bimDocsOpenData(res.data,filename);
    if(!id)return false;   /* __acad3dV172g: the new project's id, for its file */
    fitScene();
    var msg='Opened '+filename+' in a new tab: '+(res.data.objs?res.data.objs.length:0)+' object(s)';
    if(res.warn)msg+=' \u2014 '+res.warn;
    a3dToast(msg);
    return id;
  }
  /* __acad3dV172g: .json and .gz (D4); the bytes decide, in bimFileRead */
  function bimOpenProjectFileObj(file){
    if(!file)return;
    var name=file.name||'project.json',ext=(name.split('.').pop()||'').toLowerCase();
    if(ext!=='json'&&ext!=='gz'){
      a3dToast(name+' is not a project file. Open takes .acad3d.json and .acad3d.json.gz project files; use Import for DXF, IFC, OBJ or STL.');
      return;
    }
    bimFileRead(file,null);
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
export {
  A3D_PERSIST, bimAskPersist, bimBuildProjectEnvelope, bimExportProjectFile, bimFileStem,
  bimImportProjectFile, bimOpenProjectFileObj, bimOpenProjectPicker, bimParseProjectEnvelope
};
