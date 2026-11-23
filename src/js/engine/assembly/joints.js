import { A3D, el } from '../core/state.js';
import { bimEnterDraftingMode, pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimObjMass, bimObjVolume } from '../bim/type-instance-params.js';
import { bimTriggerDownload } from '../annotation/annotation-pick.js';
import { bimFileStem } from '../io/project-file.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow, bimPropText } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { paint } from '../map/terrain-3d.js';
import { bimRotateObjectInPlace } from '../editing/precision-editing.js';
import { bimPropagateFrom } from '../bim/region-dependents.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV273: FreeCAD's Assembly workbench: parts, joints, a bill of materials =================
     JOINT joins two selected objects, the first the base and the second the part that moves: Fixed (it follows the
     base), Revolute (it turns about a vertical hinge, clicked in the plan, as a door or a gate does) or Slider (it
     slides along a direction, as a sliding door or a drawer). A part has one joint to its base, so an assembly is a
     tree from a grounded part, which moves only when it is moved itself. A joint's value (degrees, or metres) is set
     in Properties, within its limits: the part and everything joined below it moves by the change, their own hinges
     and directions with them (forward kinematics, the joints of a tree solved in order; closed loops are refused).
     BOM lists an assembly's parts, counted by name and material, with volume and mass, and exports them as CSV, as
     FreeCAD's BOM does. Movement goes through the app's own ROTATE and MOVE, so an OpenCASCADE solid stays one
     (V266). The tree and the arithmetic are pure, tested without a page. */
  var BIM_JOINT_TYPES=[['fixed','Fixed'],['revolute','Revolute (vertical hinge)'],['slider','Slider']];
  /* ---------- pure: the tree ---------- */
  function bimJointChildren(objs,id){return objs.filter(function(o){return o.joint&&o.joint.parent===id;}).map(function(o){return o.id;});}
  /* The part and everything joined below it, each once. */
  function bimJointSubtree(objs,id){
    var out=[id],seen={},i;seen[id]=1;
    for(i=0;i<out.length;i++)bimJointChildren(objs,out[i]).forEach(function(c){if(!seen[c]){seen[c]=1;out.push(c);}});
    return out;
  }
  /* Joining child under parent would close a loop (the parent is the child or below it). */
  function bimJointWouldLoop(objs,parentId,childId){return bimJointSubtree(objs,childId).indexOf(parentId)>=0;}
  /* The whole assembly a part is in: up to its root, then down. */
  function bimJointRoot(objs,id){
    var by={},cur=id,guard=0;
    objs.forEach(function(o){by[o.id]=o;});
    while(by[cur]&&by[cur].joint&&by[cur].joint.parent&&by[by[cur].joint.parent]&&guard++<1000)cur=by[cur].joint.parent;
    return cur;
  }
  function bimJointClamp(j,v){
    if(isFinite(j.min)&&v<j.min)v=j.min;
    if(isFinite(j.max)&&v>j.max)v=j.max;
    return v;
  }
  /* A plan point turned counter-clockwise (north up) by deg about a centre; the app's z runs south. Pure. */
  function bimJointTurnPt(p,c,deg){
    var a=-deg*Math.PI/180,vx=p[0]-c[0],vz=p[1]-c[1],co=Math.cos(a),s=Math.sin(a);
    return [c[0]+vx*co-vz*s,c[1]+vx*s+vz*co];
  }
  /* A direction turned the same way (its plan part). Pure. */
  function bimJointTurnDir(d,deg){var p=bimJointTurnPt([d[0],d[2]],[0,0],deg);return [p[0],d[1],p[1]];}
  /* ---------- the model ---------- */
  function bimJointSet(o,value){
    var j=o&&o.joint;
    if(!j||j.type==='fixed')return false;
    var v=bimJointClamp(j,+value);
    if(!isFinite(v))return false;
    var delta=v-(j.value||0);
    if(Math.abs(delta)<1e-12)return false;
    var ids=bimJointSubtree(A3D.objs,o.id),i;
    pushUndo();
    setUndoSuspend(true);
    try{
      for(i=0;i<ids.length;i++){
        var s=objById(ids[i]);if(!s)continue;
        if(j.type==='revolute'){
          bimRotateObjectInPlace(s,[j.axis[0],j.axis[2]],-delta*Math.PI/180);
          if(s!==o&&s.joint){var ap=bimJointTurnPt([s.joint.axis[0],s.joint.axis[2]],[j.axis[0],j.axis[2]],delta);s.joint.axis=[ap[0],s.joint.axis[1],ap[1]];
            if(s.joint.dir)s.joint.dir=bimJointTurnDir(s.joint.dir,delta);}
        }else{
          var d=[j.dir[0]*delta,j.dir[1]*delta,j.dir[2]*delta];
          if(!s.pos)s.pos=[0,0,0];
          s.pos[0]+=d[0];s.pos[1]+=d[1];s.pos[2]+=d[2];
          bimPropagateFrom([s.id],'transform',d);
          if(s!==o&&s.joint)s.joint.axis=[s.joint.axis[0]+d[0],s.joint.axis[1]+d[1],s.joint.axis[2]+d[2]];
        }
      }
    }finally{setUndoSuspend(false);}
    j.value=v;
    A3D.meshes={};
    refreshTree();refreshProps();paint();saveSoon();
    return true;
  }
  function bimJointCreate(parent,child,spec){
    if(!parent||!child||parent===child)return {error:'Select the base, then the part that moves'};
    if(bimJointWouldLoop(A3D.objs,parent.id,child.id))return {error:child.name+' is already above '+parent.name+' in the assembly: a loop is not solved'};
    var j={id:'joint-'+Date.now().toString(36)+'-'+(A3D.seq++),type:spec.type,parent:parent.id,value:0};
    if(spec.type==='revolute'){j.axis=[spec.at[0],0,spec.at[1]];j.min=isFinite(spec.min)?spec.min:-180;j.max=isFinite(spec.max)?spec.max:180;}
    if(spec.type==='slider'){
      var d=spec.dir,l=Math.sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2]);
      if(!(l>0))return {error:'A slider needs a direction'};
      j.dir=[d[0]/l,d[1]/l,d[2]/l];j.axis=[0,0,0];j.min=isFinite(spec.min)?spec.min:0;j.max=isFinite(spec.max)?spec.max:1;
    }
    pushUndo();
    child.joint=j;
    var name=parent.asm||child.asm;
    if(!name){A3D.counts.asm=(A3D.counts.asm||0)+1;name='Assembly '+A3D.counts.asm;}
    bimJointSubtree(A3D.objs,bimJointRoot(A3D.objs,parent.id)).forEach(function(id){var x=objById(id);if(x)x.asm=name;});
    refreshTree();refreshProps();paint();saveSoon();
    return j;
  }
  function openJointDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():[];
    if(ids.length!==2){a3dToast('JOINT: select two objects, the base first, then the part that moves');return null;}
    var P=objById(ids[0]),C=objById(ids[1]);
    if(!P||!C)return null;
    closeDlg();
    var d=document.createElement('div');d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Joint: '+bimEsc(C.name)+' on '+bimEsc(P.name)+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Type</label><select data-a3djt="type">'+BIM_JOINT_TYPES.map(function(t){return '<option value="'+t[0]+'">'+t[1]+'</option>';}).join('')+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Revolute: limits, degrees</label><span><input type="number" step="any" data-a3djt="rmin" value="-90" style="width:60px"> to <input type="number" step="any" data-a3djt="rmax" value="90" style="width:60px"></span></div>'+
      '<div class="a3d-dlgrow"><label>Slider: direction east, north, up</label><span><input type="number" step="any" data-a3djt="dx" value="1" style="width:44px"><input type="number" step="any" data-a3djt="dn" value="0" style="width:44px"><input type="number" step="any" data-a3djt="du" value="0" style="width:44px"></span></div>'+
      '<div class="a3d-dlgrow"><label>Slider: limits, m</label><span><input type="number" step="any" data-a3djt="smin" value="0" style="width:60px"> to <input type="number" step="any" data-a3djt="smax" value="1" style="width:60px"></span></div>'+
      '<div class="a3d-propnote">A revolute joint asks for its hinge next: click it in the plan. Set the joint’s value in Properties.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function val(k){return parseFloat(d.querySelector('[data-a3djt="'+k+'"]').value);}
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')!=='ok'){closeDlg();return;}
      var type=d.querySelector('[data-a3djt="type"]').value,spec={type:type};
      if(type==='revolute'){
        spec.min=val('rmin');spec.max=val('rmax');
        if(!(spec.min<=0&&spec.max>=0)){d.querySelector('#a3d-dlgerr').textContent='The limits must take in 0, where it is now';return;}
        closeDlg();bimEnterDraftingMode();
        A3D.sk={tool:'jointaxis',pts:[],y:bimGetActiveLevel().elev,on:null,jP:P.id,jC:C.id,spec:spec};
        a3dToast('JOINT: click the hinge');paint();return;
      }
      if(type==='slider'){spec.dir=[val('dx'),val('du'),-val('dn')];spec.min=val('smin');spec.max=val('smax');
        if(!(spec.min<=0&&spec.max>=0)){d.querySelector('#a3d-dlgerr').textContent='The limits must take in 0, where it is now';return;}}
      var r=bimJointCreate(P,C,spec);
      if(r.error){d.querySelector('#a3d-dlgerr').textContent=r.error;return;}
      closeDlg();a3dToast('Joint: '+C.name+' on '+P.name+' ('+type+')');
    });
    return d;
  }
  function bimJointAxisPoint(sk,p){
    A3D.sk=null;paint();
    var P=objById(sk.jP),C=objById(sk.jC);
    var spec=sk.spec;spec.at=[p[0],p[1]];
    var r=bimJointCreate(P,C,spec);
    if(r.error){a3dToast(r.error);return null;}
    a3dToast('Joint: '+C.name+' turns on '+P.name+' about ('+p[0].toFixed(2)+', '+(-p[1]).toFixed(2)+'). Set its angle in Properties.');
    return r;
  }
  /* ---------- Properties ---------- */
  function bimJointPropsHtml(o){
    var j=o.joint,P=objById(j.parent),h='';
    h+=bimPropText('Assembly',o.asm||'');
    h+=bimPropText('Joint',(BIM_JOINT_TYPES.filter(function(t){return t[0]===j.type;})[0]||[0,j.type])[1]+' on '+(P?P.name:'(gone)'));
    if(j.type!=='fixed')h+=bimPropRow(j.type==='revolute'?'Angle, degrees ('+j.min+' to '+j.max+')':'Distance, m ('+j.min+' to '+j.max+')',
      '<input type="number" step="any" data-propf="jointval" value="'+(+(+j.value||0).toFixed(6))+'">');
    h+=bimPropRow('','<button data-propf="jointdel">Remove joint</button>');
    return h;
  }
  function bimJointPropField(o,f,inp){
    if(f!=='jointval'||!o||!o.joint)return false;
    var v=parseFloat(inp.value);
    if(!isFinite(v)){a3dToast('Must be a number');refreshProps();return true;}
    var c=bimJointClamp(o.joint,v);
    bimJointSet(o,c);
    if(c!==v)a3dToast('Held at its limit: '+c);
    refreshProps();
    return true;
  }
  function bimJointRemove(o){
    if(!o||!o.joint)return;
    pushUndo();delete o.joint;
    refreshProps();saveSoon();a3dToast(o.name+' is free of its joint');
  }
  /* ---------- BOM ---------- */
  /* A part's name for counting: its own without a trailing count or "copy". Pure. */
  function bimBomName(n){return String(n||'Part').replace(/(\s+(copy|mirror))+$/i,'').replace(/[\s_]*\d+$/,'')||String(n||'Part');}
  /* The rows: {part, material, count, volume, mass} each, sorted by part. Pure on its reader. */
  function bimBomRows(objs,info){
    var by={},out=[],k;
    objs.forEach(function(o){
      var m=info(o),key=bimBomName(o.name)+'|'+(m.material||'');
      if(!by[key]){by[key]={part:bimBomName(o.name),material:m.material||'',count:0,volume:m.volume,mass:m.mass};out.push(by[key]);}
      by[key].count++;
    });
    return out.sort(function(a,b){return a.part<b.part?-1:a.part>b.part?1:0;});
  }
  function bimBomCsv(rows){
    var q=function(s){s=String(s==null?'':s);return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
    return ['Part,Material,Count,Volume each (m3),Mass each (kg)'].concat(rows.map(function(r){
      return [q(r.part),q(r.material),r.count,r.volume==null?'':(+r.volume.toFixed(6)),r.mass==null?'':(+r.mass.toFixed(3))].join(',');})).join('\n')+'\n';
  }
  function bimBomObjects(){
    var sel=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.map(objById).filter(Boolean):(A3D.sel?[objById(A3D.sel)].filter(Boolean):[]);
    var names={};sel.forEach(function(o){if(o.asm)names[o.asm]=1;});
    var L=A3D.objs.filter(function(o){return o.asm&&(!sel.length||names[o.asm]);});
    return L.length?L:sel;
  }
  function openBomDlg(){
    var L=bimBomObjects();
    if(!L.length){a3dToast('BOM: no assembly (JOINT makes one); or select the parts to list');return null;}
    var rows=bimBomRows(L,function(o){return {material:o.materialName||'',volume:bimObjVolume(o),mass:bimObjMass(o)};});
    closeDlg();
    var d=document.createElement('div');d.className='a3d-dlg a3d-matb';
    d.innerHTML='<div class="a3d-dlghd">Bill of materials</div><div class="a3d-dlgbody"><table class="a3d-sheetgrid" style="width:100%"><tr><th>Part</th><th>Material</th><th>Count</th><th>Mass each, kg</th></tr>'+
      rows.map(function(r){return '<tr><td>'+bimEsc(r.part)+'</td><td>'+bimEsc(r.material||'—')+'</td><td>'+r.count+'</td><td>'+(r.mass==null?'—':r.mass.toFixed(1))+'</td></tr>';}).join('')+
      '</table></div><div class="a3d-dlgft"><button data-a3dbom="csv">Export CSV</button><button data-a3dlg="cancel">Close</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dbom],[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')){closeDlg();return;}
      bimTriggerDownload(bimBomCsv(rows),bimFileStem()+'-bom.csv','text/csv');a3dToast('BOM exported');});
    return d;
  }
export { bimJointAxisPoint, bimJointPropField, bimJointPropsHtml, bimJointRemove, openBomDlg, openJointDlg };
