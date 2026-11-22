import { A3D, el } from '../core/state.js';
import { UNDO_STACK, bimEnterDraftingMode, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimCreateTextLabel } from '../annotation/dimensions.js';
import { bimTextStyle } from '../annotation/dim-tools.js';
import { bimEsc } from '../layers/layer-manager.js';
import { refreshProps } from '../site-analysis/panel.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV260: block attributes (ATTDEF, ATTEDIT) =================
     AutoCAD's attributes: data a block carries in text, asked for when it is inserted (a title block's sheet number,
     a door tag's mark). ATTDEF places a definition: a text object with o.attdef {tag, prompt, def}, drawn as its tag.
     A block saved with definitions in it asks for their values when inserted; each copy becomes a text with
     o.attrib {tag} and the value typed. Every object an insert makes carries o.blockRef {name, ins}, the one insert
     it belongs to, so ATTEDIT finds all of an insert's attributes from any of its members. A DXF or DWG insert's
     attributes come in with their tags (import-dxf.js, dwg-io.js). The value logic is pure (bimAttribFill), tested
     without a canvas. */
  function bimAttdefValid(a){
    var tag=String(a&&a.tag||'').replace(/^\s+|\s+$/g,'').toUpperCase().replace(/\s+/g,'_');
    if(!tag)return {error:'An attribute needs a tag'};
    if(/[^A-Z0-9_\-.]/.test(tag))return {error:'A tag is letters, digits, _ - and .'};
    return {tag:tag,prompt:String(a.prompt||'').slice(0,120)||tag,def:String(a.def==null?'':a.def).slice(0,500)};
  }
  /* The values an insert's attributes take: the typed one, else the definition's default. */
  function bimAttribFill(defs,values){
    var out=[],i,d,v;
    for(i=0;i<defs.length;i++){
      d=defs[i];v=values&&Object.prototype.hasOwnProperty.call(values,d.tag)?String(values[d.tag]):d.def;
      out.push({tag:d.tag,value:v});
    }
    return out;
  }
  function openAttdefDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var ts=bimTextStyle();
    d.innerHTML='<div class="a3d-dlghd">Attribute definition</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Tag</label><input type="text" data-a3dad="tag" maxlength="60"></div>'+
      '<div class="a3d-dlgrow"><label>Prompt</label><input type="text" data-a3dad="prompt" maxlength="120"></div>'+
      '<div class="a3d-dlgrow"><label>Default</label><input type="text" data-a3dad="def" maxlength="500"></div>'+
      '<div class="a3d-dlgrow"><label>Height on the plan, m</label><input type="number" min="0" step="any" data-a3dad="h" value="'+(ts.height||0.25)+'"></div>'+
      '<div class="a3d-propnote">Then click where it goes. Save it in a block (BLOCK) with the drawing it describes: each insert of the block asks for its value.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var a=bimAttdefValid({tag:d.querySelector('[data-a3dad="tag"]').value,prompt:d.querySelector('[data-a3dad="prompt"]').value,
        def:d.querySelector('[data-a3dad="def"]').value});
      if(a.error){d.querySelector('#a3d-dlgerr').textContent=a.error;return;}
      var h=parseFloat(d.querySelector('[data-a3dad="h"]').value);
      closeDlg();
      bimEnterDraftingMode();
      A3D.sk={tool:'attdef',pts:[],y:bimGetActiveLevel().elev,on:null,attdef:a,attH:h>0?h:0};
      a3dToast('ATTDEF: specify the start point of '+a.tag);
      paint();
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    d.querySelector('[data-a3dad="tag"]').focus();
  }
  function bimAttdefPlace(sk,p){
    A3D.sk=null;
    var o=bimCreateTextLabel([p[0],p[1]],sk.y,sk.attdef.tag,{height:sk.attH});
    if(o){o.attdef=sk.attdef;o.name='Attribute '+sk.attdef.tag;paint();}
    return o;
  }
  /* After an insert: its copies of attribute definitions become attributes, with the values asked for. */
  function bimAttribsAfterInsert(made,name){
    var ins='ins-'+Date.now().toString(36)+'-'+(A3D.seq++),defs=[],objs=[],i;
    for(i=0;i<made.length;i++){
      made[i].blockRef={name:name,ins:ins};
      if(made[i].t==='text'&&made[i].attdef){defs.push(made[i].attdef);objs.push(made[i]);}
    }
    if(!defs.length)return null;
    var vals=bimAttribFill(defs,null);
    for(i=0;i<objs.length;i++){
      objs[i].attrib={tag:defs[i].tag,prompt:defs[i].prompt};
      objs[i].text=vals[i].value||'';
      objs[i].name=name+' '+defs[i].tag;
      delete objs[i].attdef;
    }
    openAttribDlg(objs,'Enter attributes: '+name);
    return objs;
  }
  /* The attributes of the insert(s) the selection belongs to. */
  function bimAttribsOfSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]),ins={},out=[],i,o;
    for(i=0;i<ids.length;i++){o=objById(ids[i]);if(o&&o.blockRef)ins[o.blockRef.ins]=1;else if(o&&o.attrib)out.push(o);}
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.attrib&&o.blockRef&&ins[o.blockRef.ins]&&out.indexOf(o)<0)out.push(o);}
    return out;
  }
  function bimAttedit(){
    var at=bimAttribsOfSelection();
    if(!at.length){a3dToast('ATTEDIT: select a block insert that has attributes');return null;}
    return openAttribDlg(at,'Edit attributes'+(at[0].blockRef?': '+at[0].blockRef.name:''));
  }
  function openAttribDlg(objs,title){
    closeDlg();
    var d=document.createElement('div'),h='',i;
    d.className='a3d-dlg';
    for(i=0;i<objs.length;i++){
      var a=objs[i].attrib||{tag:'?'};
      h+='<div class="a3d-dlgrow"><label>'+bimEsc(a.prompt||a.tag)+' <span style="opacity:.6">('+bimEsc(a.tag)+')</span></label>'+
        '<input type="text" data-a3dav="'+i+'" value="'+bimEsc(objs[i].text)+'" maxlength="500"></div>';
    }
    d.innerHTML='<div class="a3d-dlghd">'+bimEsc(title)+'</div><div class="a3d-dlgbody">'+h+'</div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var f=d.querySelectorAll('[data-a3dav]'),k,changed=0;
      pushUndo();
      for(k=0;k<f.length;k++){var o=objs[+f[k].getAttribute('data-a3dav')];if(o&&o.text!==f[k].value){o.text=f[k].value;changed++;}}
      if(!changed)UNDO_STACK.pop();
      closeDlg();paint();saveSoon();refreshProps();
      if(changed)a3dToast(changed+' attribute(s) changed');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    var first=d.querySelector('[data-a3dav]');if(first)first.focus();
    return d;
  }
export { bimAttdefPlace, bimAttedit, bimAttribsAfterInsert, openAttdefDlg };
