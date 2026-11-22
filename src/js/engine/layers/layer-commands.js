import { A3D } from '../core/state.js';
import { UNDO_STACK, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayerById, bimLayerOf } from './layer-rules.js';
import { bimLayerChanged, bimLayerMakeCurrent, bimLayerUnder } from './select-change.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV256: AutoCAD's layer commands (docs/research/research-cadcraft-gap.md) =================
     LAYISO and LAYUNISO, LAYOFF, LAYFRZ, LAYLCK, LAYON, LAYTHW, LAYMCUR and LAYERP, by AutoCAD's names: each acts on
     the layers of the selected objects, or on every layer, in one undo step. LAYERP (LAYP) steps back through the
     layer settings as they were before each change, whether it came from these commands or from the Layer
     Properties Manager (bimLayerSet records it), as AutoCAD's does; LAYUNISO puts back what the last LAYISO changed.
     The arithmetic is pure (bimLayerSnap, bimLayIsoPlan), tested without a canvas. */
  var BIM_LAY_FIELDS=['visible','frozen','locked','plot','color','linetype','lineweight','transparency'];
  var A3D_LAYP={stack:[],max:50,iso:null};
  /* Every layer's settings and the current layer, as LAYERP and LAYUNISO put them back. */
  function bimLayerSnap(layers,current){
    return {cur:current,ls:layers.map(function(l){
      var o={id:l.id},k;
      for(k=0;k<BIM_LAY_FIELDS.length;k++)o[BIM_LAY_FIELDS[k]]=l[BIM_LAY_FIELDS[k]];
      return o;
    })};
  }
  function bimLayerRecordPrev(){
    A3D_LAYP.stack.push(bimLayerSnap(A3D.layers,A3D.activeLayer));
    if(A3D_LAYP.stack.length>A3D_LAYP.max)A3D_LAYP.stack.shift();
  }
  function bimLayerRestore(snap,fields){
    var i,k,l,s;
    fields=fields||BIM_LAY_FIELDS;
    for(i=0;i<snap.ls.length;i++){
      s=snap.ls[i];l=bimLayerById(s.id);
      if(!l)continue;
      for(k=0;k<fields.length;k++){
        if(s[fields[k]]===undefined)delete l[fields[k]];else l[fields[k]]=s[fields[k]];
      }
    }
    if(snap.cur&&bimLayerById(snap.cur))A3D.activeLayer=snap.cur;
  }
  /* The layers the selected objects are on (ids, in the list's order). */
  function bimSelLayerIds(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]),seen={},out=[],i,o,ly;
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);ly=o?bimLayerOf(o):null;
      if(ly&&!seen[ly.id]){seen[ly.id]=1;out.push(ly.id);}
    }
    return out;
  }
  /* LAYISO's plan: the kept layers and the layers above them stay on; every other layer goes off. A layer that
     holds a kept layer is not turned off, or the kept one would vanish with it. */
  function bimLayIsoPlan(layers,keepIds){
    var keep={},i,j,off=[];
    for(i=0;i<keepIds.length;i++){
      var c=null;
      for(j=0;j<layers.length;j++)if(layers[j].id===keepIds[i])c=layers[j];
      while(c&&!keep[c.id]){
        keep[c.id]=1;
        var p=c.parent,n=null;
        for(j=0;p&&j<layers.length;j++)if(layers[j].id===p)n=layers[j];
        c=n;
      }
    }
    for(i=0;i<layers.length;i++)if(!keep[layers[i].id]&&layers[i].visible!==false)off.push(layers[i].id);
    return {keep:Object.keys(keep),off:off};
  }
  function bimLayCmdApply(ids,field,val,msg){
    if(!ids.length){a3dToast(msg.none);return 0;}
    var cur=bimLayerById(A3D.activeLayer),n=0,skipped=0,i,l;
    pushUndo();bimLayerRecordPrev();
    for(i=0;i<ids.length;i++){
      l=bimLayerById(ids[i]);if(!l)continue;
      if(field==='frozen'&&val&&cur&&bimLayerUnder(cur,l.id)){skipped++;continue;}
      var was=field==='visible'?l.visible!==false:!!l[field];
      if(was===val)continue;
      l[field]=val;n++;
    }
    if(!n){A3D_LAYP.stack.pop();UNDO_STACK.pop();}
    bimLayerChanged();
    a3dToast(msg.done.replace('#',n)+(skipped?' (the current layer cannot be frozen)':''));
    return n;
  }
  function bimLayIso(){
    var keep=bimSelLayerIds();
    if(!keep.length){a3dToast('LAYISO: select objects on the layers to keep');return null;}
    var plan=bimLayIsoPlan(A3D.layers,keep);
    pushUndo();bimLayerRecordPrev();
    A3D_LAYP.iso=bimLayerSnap(A3D.layers,A3D.activeLayer);
    for(var i=0;i<plan.off.length;i++)bimLayerById(plan.off[i]).visible=false;
    /* AutoCAD makes an isolated layer current when the current one went off */
    if(plan.off.indexOf(A3D.activeLayer)>=0)A3D.activeLayer=keep[0];
    bimLayerChanged();
    a3dToast('LAYISO: '+keep.length+' layer(s) isolated, '+plan.off.length+' turned off');
    return plan;
  }
  function bimLayUniso(){
    if(!A3D_LAYP.iso){a3dToast('LAYUNISO: no layers were isolated with LAYISO');return false;}
    pushUndo();bimLayerRecordPrev();
    bimLayerRestore(A3D_LAYP.iso,['visible','locked']);
    A3D_LAYP.iso=null;
    bimLayerChanged();
    a3dToast('LAYUNISO: the layers are back as they were before LAYISO');
    return true;
  }
  function bimLayerPrevious(){
    var s=A3D_LAYP.stack.pop();
    if(!s){a3dToast('LAYERP: no layer changes to undo');return false;}
    pushUndo();
    bimLayerRestore(s);
    bimLayerChanged();
    a3dToast('LAYERP: the layer settings are back as they were before the last change');
    return true;
  }
  function bimLayMcur(){
    var ids=bimSelLayerIds();
    if(ids.length!==1){a3dToast(ids.length?'LAYMCUR: select objects on one layer':'LAYMCUR: select an object first');return false;}
    return bimLayerMakeCurrent(ids[0]);
  }
  function bimLayAll(field,val,label){
    return bimLayCmdApply(A3D.layers.map(function(l){return l.id;}),field,val,{none:label+': no layers',done:label+': # layer(s) changed'});
  }
export {
  bimLayAll, bimLayCmdApply, bimLayIso, bimLayMcur, bimLayUniso, bimLayerPrevious, bimLayerRecordPrev,
  bimSelLayerIds
};
