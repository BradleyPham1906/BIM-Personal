import { A3D, el } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimEsc } from '../layers/layer-manager.js';
import { dxfTextFromBytes } from './dxf-entities.js';
import { bimImportDXF } from './import-dxf.js';
import { bimImportDWG } from './dwg-io.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV265: external references (XATTACH, XREF) =================
     AutoCAD's XATTACH: another drawing shown in this one for reference, not merged into it. Here a DXF or DWG is read by
     the same importers (import-dxf.js, dwg-io.js), and every object it brings is marked o.xref {id, name} and locked,
     so it can be seen, snapped to and measured, but not edited. XREF lists the attached drawings: Detach takes one out;
     Reload reads a new copy of it, which a browser can only do from a file picked again (a page cannot read a path on
     the disk by itself). The bookkeeping is pure (bimXrefList), tested without a canvas. */
  function bimXrefList(objs){
    var by={},out=[],i,o;
    for(i=0;i<objs.length;i++){
      o=objs[i];if(!o.xref)continue;
      var r=by[o.xref.id];
      if(!r){r=by[o.xref.id]={id:o.xref.id,name:o.xref.name,count:0};out.push(r);}
      r.count++;
    }
    return out;
  }
  function bimXrefPick(cb){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.dxf,.dwg';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)cb(f);};
    inp.click();
  }
  /* Read a file as a reference: what the importer adds is marked as the reference's. */
  function bimXattachFile(file,reuseId){
    var name=file.name||'reference',ext=(name.split('.').pop()||'').toLowerCase();
    var before={},i,id=reuseId||'xref-'+Date.now().toString(36)+'-'+(A3D.seq++);
    for(i=0;i<A3D.objs.length;i++)before[A3D.objs[i].id]=1;
    function mark(){
      var n=0;
      for(var k=0;k<A3D.objs.length;k++){var o=A3D.objs[k];if(!before[o.id]){o.xref={id:id,name:name};o.locked=true;n++;}}
      refreshTree();paint();saveSoon();
      a3dToast(n?'XATTACH: '+name+' attached as a reference ('+n+' objects, locked)':'XATTACH: nothing came from '+name);
      return n;
    }
    return new Promise(function(res){
      var rd=new FileReader();
      rd.onerror=function(){a3dToast('XATTACH: could not read '+name);res(0);};
      rd.onload=function(ev){
        try{
          if(ext==='dwg')bimImportDWG(ev.target.result,name).then(function(){res(mark());});
          else{bimImportDXF(dxfTextFromBytes(ev.target.result),name);res(mark());}
        }catch(e){console.warn('[BIM] XATTACH failed:',e);a3dToast('XATTACH failed: '+(e&&e.message||e));res(0);}
      };
      rd.readAsArrayBuffer(file);
    });
  }
  function bimXattach(){bimXrefPick(function(f){bimXattachFile(f,null);});}
  function bimXrefDetach(id){
    var n=0;
    pushUndo();
    A3D.objs=A3D.objs.filter(function(o){if(o.xref&&o.xref.id===id){n++;return false;}return true;});
    A3D.sel=null;A3D.selSet=[];
    refreshTree();paint();saveSoon();
    return n;
  }
  function openXrefDlg(){
    var L=bimXrefList(A3D.objs);
    if(!L.length){a3dToast('XREF: no drawings are attached (XATTACH attaches one)');return null;}
    closeDlg();
    var d=document.createElement('div'),h='',i;
    d.className='a3d-dlg';
    for(i=0;i<L.length;i++)h+='<div class="a3d-dlgrow"><label>'+bimEsc(L[i].name)+' <span style="opacity:.6">('+L[i].count+' objects)</span></label>'+
      '<span><button data-a3dxr="reload" data-id="'+bimEsc(L[i].id)+'">Reload</button> <button data-a3dxr="detach" data-id="'+bimEsc(L[i].id)+'">Detach</button></span></div>';
    d.innerHTML='<div class="a3d-dlghd">External references</div><div class="a3d-dlgbody">'+h+
      '<div class="a3d-propnote">Reload asks for the file again: a page cannot read a path on the disk by itself.</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Close</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dxr],[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')){closeDlg();return;}
      var id=b.getAttribute('data-id'),what=b.getAttribute('data-a3dxr');
      closeDlg();
      if(what==='detach'){var n=bimXrefDetach(id);a3dToast('XREF: detached ('+n+' objects)');}
      else bimXrefPick(function(f){bimXrefDetach(id);bimXattachFile(f,id);});
    });
    return d;
  }
export { bimXattach, bimXrefList, openXrefDlg };
