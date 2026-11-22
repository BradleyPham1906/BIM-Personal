import { A3D, el } from '../core/state.js';
import { UNDO_STACK, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimEsc } from '../layers/layer-manager.js';
import { paint } from '../map/terrain-3d.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { A3D_FAMLIB, bimAssetKind, bimFamilyLibraryGet, bimSaveFamilyLibrary } from './family-library.js';
import { bimRecsThumb } from './scale-assets.js';
import { bimInsertBlock, refreshFamilyPanel } from './blocks.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV265: the block editor (BEDIT, BCLOSE) =================
     AutoCAD's BEDIT: a block's definition opened for editing, and BCLOSE saving it, which redefines every insert of it.
     Here BEDIT puts the block's objects in the model where they were drawn when the block was saved (its own frame),
     marked o.bedit; anything drawn before BCLOSE joins it. BCLOSE saves them as the block's new definition (same name,
     same base point), takes them out of the model, and replaces each insert's objects with the new definition at the
     insert's point, keeping its attribute values by tag, as AutoCAD's ATTSYNC does. Discard puts nothing back.
     The plan of a redefinition is pure (bimBlockInserts), tested without a canvas. */
  var A3D_BEDIT={id:null,before:null};
  /* The inserts of a block in the model: {ins, at, level, values by tag, ids}, one per insert that knows its point. */
  function bimBlockInserts(objs,blockId,name){
    var by={},out=[],i,o;
    for(i=0;i<objs.length;i++){
      o=objs[i];
      if(!o.blockRef||(o.blockRef.id?o.blockRef.id!==blockId:o.blockRef.name!==name)||!o.blockRef.at)continue;
      var r=by[o.blockRef.ins];
      if(!r){r=by[o.blockRef.ins]={ins:o.blockRef.ins,at:o.blockRef.at.slice(),level:o.blockRef.level||null,values:{},ids:[]};out.push(r);}
      r.ids.push(o.id);
      if(o.attrib&&o.attrib.tag)r.values[o.attrib.tag]=o.text;
    }
    return out;
  }
  function bimBlockList(){return A3D_FAMLIB.filter(function(e){return bimAssetKind(e)==='block'&&e.recs&&e.recs.length;});}
  function openBeditDlg(){
    if(A3D_BEDIT.id){a3dToast('BEDIT: a block is already open: BCLOSE it first');return;}
    var L=bimBlockList();
    if(!L.length){a3dToast('BEDIT: the library has no blocks (BLOCK makes one)');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Edit block definition</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Block</label><select data-a3dbe="id">'+L.map(function(e){
        return '<option value="'+bimEsc(e.id)+'">'+bimEsc(e.name)+' ('+e.recs.length+')</option>';}).join('')+'</select></div>'+
      '<div class="a3d-propnote">Its objects open where they were drawn. Edit them, draw more, then BCLOSE to save: every insert is redefined.</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Open</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok'){var id=d.querySelector('[data-a3dbe="id"]').value;closeDlg();bimBeditOpen(id);}else closeDlg();});
  }
  function bimBeditOpen(id){
    var e=bimFamilyLibraryGet(id);
    if(!e){a3dToast('BEDIT: that block is gone');return null;}
    var i,ids=bimInsertBlock(e,[e.base[0],e.base[1]],{values:{},quiet:true});
    if(!ids)return null;
    for(i=0;i<ids.length;i++){var o=objById(ids[i]);if(o){o.bedit=id;delete o.blockRef;if(o.attrib){o.attdef={tag:o.attrib.tag,prompt:o.attrib.prompt||o.attrib.tag,def:''};o.text=o.attdef.tag;delete o.attrib;}}}
    A3D_BEDIT.id=id;
    A3D_BEDIT.before={};
    for(i=0;i<A3D.objs.length;i++)A3D_BEDIT.before[A3D.objs[i].id]=1;
    paint();
    a3dToast('Block editor: "'+e.name+'" ('+ids.length+' objects). BCLOSE to save or discard.');
    return ids;
  }
  /* The block's objects now: those it opened with, and anything drawn since. */
  function bimBeditMembers(){
    return A3D.objs.filter(function(o){return o.bedit===A3D_BEDIT.id||!A3D_BEDIT.before[o.id];});
  }
  function openBcloseDlg(){
    if(!A3D_BEDIT.id){a3dToast('BCLOSE: no block is open (BEDIT opens one)');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Close the block editor</div><div class="a3d-dlgbody">'+
      '<div class="a3d-propnote">Save the changes to the block, and redefine every insert of it?</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="discard">Discard</button><button data-a3dlg="ok">Save</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;
      var w=b.getAttribute('data-a3dlg');closeDlg();if(w==='ok')bimBclose(true);else if(w==='discard')bimBclose(false);});
  }
  function bimBclose(save){
    var e=bimFamilyLibraryGet(A3D_BEDIT.id),mem=bimBeditMembers(),i,k,n=0;
    pushUndo();
    if(save&&e&&mem.length){
      var recs=mem.map(function(o){var r=JSON.parse(JSON.stringify(o));delete r.bedit;return r;});
      e.recs=recs;e.count=recs.length;e.thumb=bimRecsThumb(recs);e.editedAt=new Date().toISOString();
      bimSaveFamilyLibrary();
    }
    for(i=0;i<mem.length;i++)A3D.objs.splice(A3D.objs.indexOf(mem[i]),1);
    if(save&&e){
      var inserts=bimBlockInserts(A3D.objs,e.id,e.name),lvl=A3D.activeLevel;
      for(i=0;i<inserts.length;i++){
        for(k=0;k<inserts[i].ids.length;k++){var o=objById(inserts[i].ids[k]);if(o)A3D.objs.splice(A3D.objs.indexOf(o),1);}
        if(inserts[i].level)A3D.activeLevel=inserts[i].level;
        if(bimInsertBlock(e,inserts[i].at,{values:inserts[i].values,quiet:true}))n++;
      }
      A3D.activeLevel=lvl;
      /* bimInsertBlock pushes its own undo step each time: one BCLOSE is one undo, so they are folded back into this one */
      if(UNDO_STACK.length>1)UNDO_STACK.length=UNDO_STACK.length-n;
    }
    A3D_BEDIT.id=null;A3D_BEDIT.before=null;
    A3D.sel=null;A3D.selSet=[];
    refreshTree();refreshHud();paint();saveSoon();refreshFamilyPanel();
    a3dToast(save?'Block "'+(e?e.name:'')+'" saved; '+n+' insert(s) redefined':'Block editor closed; nothing saved');
    return n;
  }
export { openBcloseDlg, openBeditDlg };
