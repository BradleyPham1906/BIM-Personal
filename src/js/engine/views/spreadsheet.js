import { A3D, el } from '../core/state.js';
import { UNDO_STACK, bimObjOffset, pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { bimObjMass, bimObjVolume, bimRebuildWall } from '../bim/type-instance-params.js';
import { bimEsc } from '../layers/layer-manager.js';
import { refreshProps } from '../site-analysis/panel.js';
import { paint } from '../map/terrain-3d.js';
import { bimResolveSketch, bimSketchConstraintDesc } from '../drawing/sketch-constraints.js';
import { bimAfterSketchEdit, bimPropagateFrom } from '../bim/region-dependents.js';
import { bimBulgedArea, bimBulgedLength } from '../drawing/arc-storage.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import {
  BIM_SHEET_COLS, BIM_SHEET_FN, BIM_SHEET_ROWS, bimSheetColName, bimSheetEvaluate, bimSheetParseRef,
  bimSheetRefName
} from './spreadsheet-eval.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV269: SPREADSHEET, cells that read and drive the model =================
     FreeCAD's Spreadsheet: a project sheet (A3D.sheet, saved with it) of cells (spreadsheet-eval.js), each with an
     optional alias, and bindings that push a cell's value into the model, as FreeCAD's expressions bound to a property
     do: every recalculation sets each bound property to its cell, as one undo step. What can be bound, per object:
       x, y, z           where it sits (its offset, as MOVE sets it)
       height, thickness a wall's (it is rebuilt)
       text              a text's words (any cell's value)
       con:<id>          a sketch constraint's value (a distance, a radius or diameter in m; an angle in degrees), the
                         sketch solved again, as FreeCAD's spreadsheet drives a Sketcher dimension
     and what obj("name", "property") reads: x, y, z, height, thickness, volume, mass, area, length. */
  function bimSheetValid(s){
    var out={cells:{},aliases:{},binds:[]},k;
    if(!s||typeof s!=='object')return out;
    for(k in (s.cells||{}))if(bimSheetParseRef(k)&&s.cells[k]!=null&&String(s.cells[k])!=='')out.cells[k]=String(s.cells[k]).slice(0,400);
    for(k in (s.aliases||{}))if(bimSheetParseRef(k)&&/^[A-Za-z_][A-Za-z0-9_]{0,30}$/.test(String(s.aliases[k]))&&!bimSheetParseRef(s.aliases[k]))out.aliases[k]=String(s.aliases[k]);
    if(Array.isArray(s.binds))s.binds.forEach(function(b){if(b&&bimSheetParseRef(b.cell)&&typeof b.obj==='string'&&typeof b.prop==='string')out.binds.push({cell:b.cell,obj:b.obj,prop:b.prop});});
    return out;
  }
  function bimSheet(){if(!A3D.sheet)A3D.sheet=bimSheetValid(null);return A3D.sheet;}
  function bimSheetObjByName(name){
    var i;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].name===name)return A3D.objs[i];
    return objById(name);
  }
  /* The properties an object can have bound, [key, label]. */
  function bimSheetTargets(o){
    var out=[['x','Position x'],['y','Position y (elevation)'],['z','Position z']];
    if(!o)return [];
    if(o.bim&&o.bim.type==='wall')out.push(['height','Wall height'],['thickness','Wall thickness']);
    if(o.t==='text')out.push(['text','Text']);
    (o.constraints||[]).forEach(function(c){
      if(c.type==='distance'||c.type==='angle'||c.type==='radius'||c.type==='diameter')out.push(['con:'+c.id,bimSketchConstraintDesc(o,c)]);
    });
    return out;
  }
  function bimSheetRead(name,prop){
    var o=bimSheetObjByName(name);
    if(!o)throw new Error('No object named '+name);
    var q=bimObjOffset(o);
    if(prop==='x')return q[0];if(prop==='y')return q[1];if(prop==='z')return q[2];
    if((prop==='height'||prop==='thickness')&&o.bim&&isFinite(o.bim[prop]))return o.bim[prop];
    if(prop==='volume'){var v=bimObjVolume(o);if(v!=null)return v;}
    if(prop==='mass'){var m=bimObjMass(o);if(m!=null)return m;}
    if(o.t==='sketch'&&o.pts){
      if(prop==='area'&&o.closed!==false)return bimBulgedArea(o.pts,o.bulges,true);
      if(prop==='length')return bimBulgedLength(o.pts,o.bulges,o.closed!==false);
    }
    throw new Error(name+' has no '+prop);
  }
  /* One bound property set; true when it changed. */
  function bimSheetApplyOne(o,prop,v){
    var q=bimObjOffset(o);
    if(prop==='text'){if(o.t!=='text')return false;var t=typeof v==='number'?String(+v.toPrecision(10)):String(v);if(o.text===t)return false;o.text=t;return true;}
    if(typeof v!=='number'||!isFinite(v))return false;
    if(prop==='x'||prop==='y'||prop==='z'){
      var k=prop==='x'?0:prop==='y'?1:2;
      if(Math.abs(q[k]-v)<1e-12)return false;
      if(!o.pos)o.pos=[0,0,0];
      var d=[0,0,0];d[k]=v-q[k];o.pos[k]=v;
      bimPropagateFrom([o.id],'transform',d);
      return true;
    }
    if((prop==='height'||prop==='thickness')&&o.bim&&o.bim.type==='wall'){
      if(!(v>0)||Math.abs(o.bim[prop]-v)<1e-12)return false;
      bimRebuildWall(o,prop==='thickness'?v:o.bim.thickness,prop==='height'?v:o.bim.height,o.bim.align);
      return true;
    }
    if(prop.indexOf('con:')===0&&o.constraints){
      var c=null,i;for(i=0;i<o.constraints.length;i++)if('con:'+o.constraints[i].id===prop)c=o.constraints[i];
      if(!c)return false;
      var nv=c.type==='angle'?v*Math.PI/180:v;
      if(!(c.type==='angle'||nv>0)||Math.abs(c.value-nv)<1e-12)return false;
      var old=c.value;c.value=nv;
      if(!bimResolveSketch(o,null,{silent:true}).ok){c.value=old;throw new Error('the sketch cannot take '+v);}
      bimAfterSketchEdit(o);
      return true;
    }
    return false;
  }
  /* Evaluate, then push the bound cells into the model: one undo step, nothing when nothing changes. */
  function bimSheetRecalc(){
    var S=bimSheet(),vals=bimSheetEvaluate(S.cells,S.aliases,bimSheetRead),n=0,errs=[],i;
    pushUndo();
    setUndoSuspend(true);   /* a wall's rebuild pushes its own step: the recalculation is one */
    try{
    for(i=0;i<S.binds.length;i++){
      var b=S.binds[i],o=objById(b.obj),v=vals[b.cell];
      if(!o){errs.push(b.cell+': its object is gone');continue;}
      if(v&&typeof v==='object'){errs.push(b.cell+': '+v.error);continue;}
      try{if(bimSheetApplyOne(o,b.prop,v===''?0:v))n++;}catch(e){errs.push(b.cell+': '+e.message);}
    }
    }finally{setUndoSuspend(false);}
    if(!n)UNDO_STACK.pop();
    else{refreshTree();refreshHud();paint();refreshProps();}
    saveSoon();
    return {values:vals,changed:n,errors:errs};
  }
  function bimSheetFmt(v){
    if(v&&typeof v==='object')return '#ERR';
    if(typeof v==='number')return String(+v.toPrecision(10));
    return v==null?'':String(v);
  }
  function openSheetDlg(){
    closeDlg();
    var d=document.createElement('div'),S=bimSheet(),focus='A1';
    d.className='a3d-dlg a3d-sheet';
    el.root.appendChild(d);el.dlg=d;
    function render(res){
      var vals=res?res.values:bimSheetEvaluate(S.cells,S.aliases,bimSheetRead),r,c,h='<table class="a3d-sheetgrid"><tr><th></th>';
      for(c=0;c<BIM_SHEET_COLS;c++)h+='<th>'+bimSheetColName(c)+'</th>';
      h+='</tr>';
      for(r=0;r<BIM_SHEET_ROWS;r++){
        h+='<tr><th>'+(r+1)+'</th>';
        for(c=0;c<BIM_SHEET_COLS;c++){
          var ref=bimSheetRefName(c,r),v=vals[ref],err=v&&typeof v==='object';
          var bound=S.binds.some(function(b){return b.cell===ref;});
          h+='<td><input type="text" data-a3dsc="'+ref+'" value="'+bimEsc(bimSheetFmt(v))+'"'+(err?' title="'+bimEsc(v.error)+'" class="a3d-sheeterr"':'')+
            (bound?' data-bound="1"':'')+' aria-label="'+ref+(S.aliases[ref]?' ('+bimEsc(S.aliases[ref])+')':'')+'"></td>';
        }
        h+='</tr>';
      }
      h+='</table>';
      var binds=S.binds.map(function(b,i){var o=objById(b.obj);
        return '<div class="a3d-dlgrow"><label>'+bimEsc(b.cell)+' → '+bimEsc(o?o.name:'(gone)')+' · '+bimEsc(b.prop)+'</label><button data-a3dsb="del" data-i="'+i+'">Remove</button></div>';}).join('');
      var sel=objById(A3D.sel),tg=bimSheetTargets(sel);
      d.innerHTML='<div class="a3d-dlghd">Spreadsheet</div><div class="a3d-dlgbody">'+
        '<div class="a3d-dlgrow"><label>Cell <b data-a3dsf="ref">'+focus+'</b></label><input type="text" data-a3dsf="f" maxlength="400" value="'+bimEsc(S.cells[focus]||'')+'" placeholder="=A1*2, 3.5, or text"></div>'+
        '<div class="a3d-dlgrow"><label>Alias</label><input type="text" data-a3dsf="alias" maxlength="31" value="'+bimEsc(S.aliases[focus]||'')+'" placeholder="width"></div>'+
        '<div class="a3d-sheetwrap">'+h+'</div>'+
        '<div class="a3d-dlghd" style="font-size:12px">Bound to the model</div>'+(binds||'<div class="a3d-propnote">Nothing bound yet.</div>')+
        (sel&&tg.length?'<div class="a3d-dlgrow"><label>Bind '+focus+' to '+bimEsc(sel.name)+'</label><select data-a3dsf="prop">'+
          tg.map(function(t){return '<option value="'+bimEsc(t[0])+'">'+bimEsc(t[1])+'</option>';}).join('')+'</select> <button data-a3dsb="bind">Bind</button></div>'
          :'<div class="a3d-propnote">Select an object in the model to bind a cell to one of its properties.</div>')+
        '<div class="a3d-propnote">Formulas: + - * / ^, cells (A1), aliases, sum(A1:A4), min, max, average, round, sqrt, sin and cos in degrees, if(test, a, b), obj("Name", "volume").</div>'+
        '<div id="a3d-dlgerr" class="a3d-dlgerr">'+bimEsc(res&&res.errors.length?res.errors.join('; '):'')+'</div></div>'+
        '<div class="a3d-dlgft"><button data-a3dsb="recalc">Recalculate</button><button data-a3dlg="cancel">Close</button></div>';
    }
    function setCell(ref,raw){
      if(raw==null||raw==='')delete S.cells[ref];else S.cells[ref]=String(raw).slice(0,400);
      var res=bimSheetRecalc();render(res);
      if(res.changed)a3dToast('Spreadsheet: '+res.changed+' propert'+(res.changed===1?'y':'ies')+' of the model set');
      return res;
    }
    render(null);
    d.addEventListener('focusin',function(ev){
      var t=ev.target,ref=t&&t.getAttribute&&t.getAttribute('data-a3dsc');
      if(!ref)return;
      focus=ref;t.value=S.cells[ref]||'';
      var fr=d.querySelector('[data-a3dsf="ref"]');if(fr)fr.textContent=ref;
      var ff=d.querySelector('[data-a3dsf="f"]');if(ff)ff.value=S.cells[ref]||'';
      var fa=d.querySelector('[data-a3dsf="alias"]');if(fa)fa.value=S.aliases[ref]||'';
    });
    d.addEventListener('change',function(ev){
      var t=ev.target;if(!t||!t.getAttribute)return;
      var ref=t.getAttribute('data-a3dsc');
      if(ref){setCell(ref,t.value);return;}
      var f=t.getAttribute('data-a3dsf');
      if(f==='f')setCell(focus,t.value);
      else if(f==='alias'){
        var a=String(t.value||'').replace(/^\s+|\s+$/g,'');
        if(a&&(!/^[A-Za-z_][A-Za-z0-9_]{0,30}$/.test(a)||bimSheetParseRef(a)||BIM_SHEET_FN.hasOwnProperty(a.toLowerCase())||a.toLowerCase()==='pi'||a.toLowerCase()==='obj')){
          d.querySelector('#a3d-dlgerr').textContent='An alias is a name of letters, digits and _, not a cell or a function';return;}
        var k;for(k in S.aliases)if(k!==focus&&String(S.aliases[k]).toLowerCase()===a.toLowerCase()){d.querySelector('#a3d-dlgerr').textContent=k+' already has that alias';return;}
        if(a)S.aliases[focus]=a;else delete S.aliases[focus];
        render(bimSheetRecalc());
      }
    });
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dsb],[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')){closeDlg();return;}
      var a=b.getAttribute('data-a3dsb');
      if(a==='recalc')render(bimSheetRecalc());
      else if(a==='del'){S.binds.splice(+b.getAttribute('data-i'),1);saveSoon();render(null);}
      else if(a==='bind'){
        var sel=objById(A3D.sel),p=d.querySelector('[data-a3dsf="prop"]');
        if(!sel||!p)return;
        S.binds=S.binds.filter(function(x){return !(x.obj===sel.id&&x.prop===p.value);});   /* one cell per property */
        S.binds.push({cell:focus,obj:sel.id,prop:p.value});
        var res=bimSheetRecalc();render(res);
        a3dToast(focus+' now drives '+sel.name+' · '+p.value);
      }
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();return;}
      if(ev.key==='Enter'&&ev.target&&ev.target.getAttribute&&ev.target.getAttribute('data-a3dsc')){ev.preventDefault();ev.target.blur();}
      ev.stopPropagation();
    });
    return d;
  }
export { bimSheetValid, openSheetDlg };
