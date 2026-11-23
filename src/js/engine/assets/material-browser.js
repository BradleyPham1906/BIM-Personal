import { A3D, el } from '../core/state.js';
import { UNDO_STACK, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimMaterialCards, bimSetMaterial } from '../bim/type-instance-params.js';
import { bimTriggerDownload } from '../annotation/annotation-pick.js';
import { bimEsc } from '../layers/layer-manager.js';
import { refreshProps } from '../site-analysis/panel.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import {
  BIM_MAT_FIELDS, bimFcmatParse, bimFcmatWrite, bimMatCardValid, bimMatQty
} from './material-cards.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV268: MATERIALS, the material library's browser and editor =================
     AutoCAD's MATBROWSEROPEN, FreeCAD's material editor: the cards (material-cards.js) in a list, the chosen one in a
     form. A built-in card is read only (Duplicate makes an editable copy, or a project card of its name, which then
     stands in for it); a project card is edited in place. Assign gives the selected solids the card (their material,
     and the card's colour); Import and Export read and write FreeCAD's .FCMat. Each change is one undo step. */
  var A3D_MATB={sel:null};
  function bimMatProjectCards(){if(!Array.isArray(A3D.matCards))A3D.matCards=[];return A3D.matCards;}
  function bimMatFind(name){var L=bimMaterialCards(),i;for(i=0;i<L.length;i++)if(L[i].name===name)return L[i];return null;}
  function bimMatIsProject(name){return bimMatProjectCards().some(function(c){return c.name===name;});}
  function bimMatPut(card,oldName){
    var L=bimMatProjectCards(),i,at=-1;
    for(i=0;i<L.length;i++)if(L[i].name===(oldName||card.name))at=i;
    pushUndo();
    if(at>=0)L[at]=card;else L.push(card);
    if(oldName&&oldName!==card.name)for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].materialName===oldName)A3D.objs[i].materialName=card.name;   /* a rename follows */
    saveSoon();refreshProps();
  }
  function bimMatUniqueName(base){var n=base,k=2;while(bimMatFind(n))n=base+' '+(k++);return n;}
  function bimMatAssign(name){
    var c=bimMatFind(name),ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]),n=0,i;
    if(!c)return 0;
    pushUndo();
    for(i=0;i<ids.length;i++){var o=objById(ids[i]);if(o&&o.t==='solid'&&bimSetMaterial(o,name)){if(c.color)o.col=c.color;n++;}}
    if(!n)UNDO_STACK.pop();
    paint();saveSoon();refreshProps();
    return n;
  }
  function bimMatDelete(name){
    var L=bimMatProjectCards(),i;
    for(i=0;i<L.length;i++)if(L[i].name===name){pushUndo();L.splice(i,1);
      if(!bimMatFind(name))for(var k=0;k<A3D.objs.length;k++)if(A3D.objs[k].materialName===name)delete A3D.objs[k].materialName;
      saveSoon();refreshProps();return true;}
    return false;
  }
  function bimMatImportText(text){
    var c=bimFcmatParse(text);
    if(c.error)return c;
    var v=bimMatCardValid(c);
    if(v.error)return v;
    bimMatPut(v,null);
    return v;
  }
  function bimMatExport(name){
    var c=bimMatFind(name);if(!c)return null;
    var u=(window.crypto&&crypto.randomUUID)?crypto.randomUUID():'00000000-0000-4000-8000-'+Date.now().toString(16).slice(-12);
    var text=bimFcmatWrite(c,u);
    bimTriggerDownload(text,c.name.replace(/[^A-Za-z0-9_.-]+/g,'-')+'.FCMat','text/yaml');
    return text;
  }
  function openMaterialsDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg a3d-matb';
    el.root.appendChild(d);el.dlg=d;
    function render(){
      var L=bimMaterialCards(),cur=bimMatFind(A3D_MATB.sel)||L[0],i,k;
      A3D_MATB.sel=cur?cur.name:null;
      var list=L.map(function(c){return '<option value="'+bimEsc(c.name)+'"'+(cur&&c.name===cur.name?' selected':'')+'>'+bimEsc(c.name)+
        (bimMatIsProject(c.name)?' (project)':'')+' · '+bimEsc(c.kind||'')+'</option>';}).join('');
      var ro=!(cur&&bimMatIsProject(cur.name)),f='';
      f+='<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dmb="name" maxlength="80" value="'+bimEsc(cur?cur.name:'')+'"'+(ro?' disabled':'')+'></div>';
      f+='<div class="a3d-dlgrow"><label>Kind</label><input type="text" data-a3dmb="kind" maxlength="40" value="'+bimEsc(cur?cur.kind||'':'')+'"'+(ro?' disabled':'')+'></div>';
      for(k=0;k<BIM_MAT_FIELDS.length;k++){
        var F=BIM_MAT_FIELDS[k],v=cur?cur[F[0]]:null;
        if(F[0]==='youngsModulus')v=v==null?null:bimMatQty('youngsModulus',v);
        f+='<div class="a3d-dlgrow"><label>'+bimEsc(F[1])+(F[2]?', '+F[2]:'')+'</label><input type="number" step="any" min="0" data-a3dmb="'+F[0]+'" value="'+(v==null?'':v)+'"'+(ro?' disabled':'')+'></div>';
      }
      f+='<div class="a3d-dlgrow"><label>Colour</label><input type="color" data-a3dmb="color" value="'+bimEsc(cur&&cur.color||'#cccccc')+'"'+(ro?' disabled':'')+'></div>';
      f+='<div class="a3d-dlgrow"><label>Transparency, 0 to 1</label><input type="number" step="0.05" min="0" max="1" data-a3dmb="transparency" value="'+(cur&&cur.transparency!=null?cur.transparency:0)+'"'+(ro?' disabled':'')+'></div>';
      d.innerHTML='<div class="a3d-dlghd">Materials</div><div class="a3d-dlgbody">'+
        '<div class="a3d-dlgrow"><label>Card</label><select data-a3dmb="pick">'+list+'</select></div>'+
        '<div class="a3d-propnote">'+(ro?'A built-in card: Duplicate it to change it.':'A card of this project, saved with it.')+'</div>'+f+
        '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
        '<div class="a3d-dlgft"><button data-a3dmbact="new">New</button><button data-a3dmbact="dup">Duplicate</button>'+
        (ro?'':'<button data-a3dmbact="save">Save</button><button data-a3dmbact="del">Delete</button>')+
        '<button data-a3dmbact="import">Import .FCMat</button><button data-a3dmbact="export">Export .FCMat</button>'+
        '<button data-a3dmbact="assign">Assign to selection</button><button data-a3dlg="cancel">Close</button></div>';
    }
    function err(t){var e=d.querySelector('#a3d-dlgerr');if(e)e.textContent=t||'';}
    function formCard(){
      var c={},f=d.querySelectorAll('[data-a3dmb]'),j;
      for(j=0;j<f.length;j++){var k=f[j].getAttribute('data-a3dmb');if(k!=='pick')c[k]=f[j].value;}
      var cur=bimMatFind(A3D_MATB.sel);if(cur&&cur.hatch)c.hatch=cur.hatch;
      return c;
    }
    render();
    d.addEventListener('change',function(ev){var t=ev.target;if(t&&t.getAttribute('data-a3dmb')==='pick'){A3D_MATB.sel=t.value;render();}});
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dmbact],[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')){closeDlg();return;}
      var a=b.getAttribute('data-a3dmbact'),cur=bimMatFind(A3D_MATB.sel);
      if(a==='new'){var nm=bimMatUniqueName('New material');bimMatPut({name:nm,kind:'Custom',custom:true,color:'#cccccc'},null);A3D_MATB.sel=nm;render();}
      else if(a==='dup'&&cur){var c=JSON.parse(JSON.stringify(cur));c.name=bimMatUniqueName(cur.name+' copy');c.custom=true;bimMatPut(bimMatCardValid(c),null);A3D_MATB.sel=c.name;render();}
      else if(a==='save'&&cur){var v=bimMatCardValid(formCard());if(v.error){err(v.error);return;}
        if(v.name!==cur.name&&bimMatFind(v.name)&&bimMatIsProject(v.name)){err('Another project card has that name');return;}
        bimMatPut(v,cur.name);A3D_MATB.sel=v.name;render();a3dToast('Material "'+v.name+'" saved');}
      else if(a==='del'&&cur){bimMatDelete(cur.name);A3D_MATB.sel=null;render();}
      else if(a==='export'&&cur){bimMatExport(cur.name);}
      else if(a==='assign'&&cur){var n=bimMatAssign(cur.name);a3dToast(n?cur.name+' assigned to '+n+' solid(s)':'Select solids first, then Assign');}
      else if(a==='import'){
        var inp=document.createElement('input');inp.type='file';inp.accept='.FCMat,.fcmat';
        inp.onchange=function(){var file=inp.files&&inp.files[0];if(!file)return;var rd=new FileReader();
          rd.onload=function(){var r=bimMatImportText(String(rd.result||''));if(r.error){err(r.error);return;}A3D_MATB.sel=r.name;render();a3dToast('Imported material "'+r.name+'"');};
          rd.readAsText(file);};
        inp.click();
      }
    });
    d.addEventListener('keydown',function(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    return d;
  }
export { openMaterialsDlg };
