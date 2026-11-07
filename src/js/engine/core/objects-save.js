import { A3D, A3D_DOCS, A3D_NO_STORAGE, LSK } from './state.js';
import { TYPES, mergePrm, meshMinY, meshOf, validatePrm } from './mesh-primitives.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { paint } from '../map/terrain-3d.js';
import { A3D_SPILL, A3D_STORE, bimSpillSave } from './idb-store.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { A3D_TAB, bimTabReadOnlyEdit } from './tab-lock.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';

  function add3d(t,prm){
    var tp=TYPES[t];if(!tp)return null;
    var p=mergePrm(t,prm);
    if(validatePrm(t,p))return null;
    pushUndo();
    A3D.counts[t]=(A3D.counts[t]||0)+1;
    var k=A3D.objs.length;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:t,name:tp.n+' '+A3D.counts[t],prm:p,
      pos:[-6+(k%3)*6,0,-6+Math.floor(k/3)*6]
    };
    o.pos[1]=-meshMinY(meshOf(o));
    A3D.objs.push(o);
    A3D.sel=o.id;
    refreshTree();refreshHud();paint();saveSoon();
    return o;
  }
  function del3d(id){
    if(!id)return false;
    var i;
    for(i=A3D.objs.length-1;i>=0;i--){
      if(A3D.objs[i].id===id){
        pushUndo();
        A3D.objs.splice(i,1);
        if(A3D.sel===id)A3D.sel=null;
        if(A3D.sel2===id)A3D.sel2=null;
        refreshTree();refreshHud();paint();saveSoon();
        return true;
      }
    }
    return false;
  }
  var saveT=null;
  /* __acad3dV122: the model's revision, moved by every change (saveSoon). What draws a page -- the
     pages, their thumbnails, the slideshow -- keeps the revision it drew at and draws again only when
     this has moved. */
  var A3D_REV=0;
  /* __acad3dV115: the one list of what a project is. save3d wrote it inline; the project tabs
     need the same list to park a project in its own key and to know what a fresh project is,
     and two copies of one field list are two lists that will eventually disagree. */
  function bimProjectRecord(){
    return {objs:A3D.objs,cam:A3D.cam,seq:A3D.seq,counts:A3D.counts,levels:A3D.levels,grids:A3D.grids,activeLevel:A3D.activeLevel,layers:A3D.layers,activeLayer:A3D.activeLayer,types:A3D.types,activeWallType:A3D.activeWallType,views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:A3D.levelFilter,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null,resultLayers:A3D.resultLayers||[],pres:A3D.pres||null};   /* __acad3dV146, __acad3dV148; __acad3dV162 */
  }
  /* __acad3dV115: a save that failed went into an empty catch, so a full browser store lost every
     later edit without a word. It says so now -- once per run of failures, not once per edit. */
  var A3D_SAVE_FAILED=false;
  /* __acad3dV172d, __acad3dV172f: every project is kept in the browser's database (core/idb-store.js); localStorage only
     while the database has not answered for a browser that never had it, or when the browser refuses it. Nothing is
     saved while the record on screen is still being read or copied (the edit is saved once it is), while this tab
     shows a project another tab holds (D7), or when the database cannot be opened by this copy. */
  function save3d(){
    if(A3D_STORE.mode==='refused'||A3D_NO_STORAGE)return;   /* __acad3dV172g: D5, the file is the only save there */
    if((A3D_SPILL&&A3D_SPILL.loading)||A3D_STORE.mode==='migrating'||(A3D_STORE.mode==='boot'&&A3D_STORE.v2)){A3D_SPILL.dirty=true;return;}
    if(A3D_TAB.readOnly){bimTabReadOnlyEdit();return;}
    var rec=bimProjectRecord();
    rec.docId=A3D_DOCS.active;
    var s=JSON.stringify(rec);
    if(A3D_STORE.mode==='idb'){bimSpillSave(rec.docId,s,rec);return;}
    try{
      localStorage.setItem(LSK,s);
      if(A3D_SAVE_FAILED){A3D_SAVE_FAILED=false;a3dToast('Saving to browser storage works again');}
    }catch(e1){
      if(!A3D_SAVE_FAILED){
        A3D_SAVE_FAILED=true;
        console.warn('[BIM] The project could not be saved: browser storage is full.',e1);
        a3dToast('This project could not be saved: browser storage is full. Use Save to keep a copy as a file.');
      }
    }
  }
  /* setters: other files assign these through them (an ES module cannot assign to an import) */
  function setA3D_REV(v){A3D_REV=v;return v;}
  function setA3D_SAVE_FAILED(v){A3D_SAVE_FAILED=v;return v;}
  function setSaveT(v){saveT=v;return v;}
export {
  A3D_REV, A3D_SAVE_FAILED, add3d, bimProjectRecord, del3d, save3d, saveT, setA3D_REV, setA3D_SAVE_FAILED,
  setSaveT
};
