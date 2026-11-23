import { A3D, el } from '../core/state.js';
import { UNDO_STACK, bimEnterDraftingMode, bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimTriggerDownload } from '../annotation/annotation-pick.js';
import { bimFileStem } from '../io/project-file.js';
import { bimEsc } from '../layers/layer-manager.js';
import {
  A3D_OCCT, bimOcctAddSolid, bimOcctDrawing, bimOcctIsSolid, bimOcctLoad, bimOcctPt, bimOcctReplace,
  bimOcctShapeAt, bimOcctShapeOf
} from './occt-adapter.js';
import { startOcctEdgePick } from './occt-features.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { bimHasBulge } from '../drawing/arc-storage.js';
import { fitScene } from '../ui/tool-palette.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV264: the solid tools on OpenCASCADE =================
     AutoCAD's names for FreeCAD's Part and PartDesign operations: EXTRUDE (EXT) a closed sketch into a solid; FILLETEDGE
     and CHAMFEREDGE on a solid's edges (all, the vertical ones, the top or the bottom ones); SHELL (a solid hollowed,
     its top face open); REVOLVE (REV) a closed sketch about an axis picked in the plan; LOFT between closed sketches at
     different heights; SOLIDUNION, SOLIDSUBTRACT and SOLIDINTERSECT on B-rep solids; EXPORTSTEP; and .step and .stp
     files through Import. Each loads OpenCASCADE the first time (occt-adapter.js) and is one undo step.
     Edges in sets (all, vertical, top, bottom), or picked one by one with the mouse (V266, occt-features.js). */
  function bimOcctSel(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    return ids.map(objById).filter(Boolean);
  }
  function bimOcctClosedSketch(o){return !!(o&&o.t==='sketch'&&o.closed!==false&&o.pts&&(o.pts.length>2||bimHasBulge(o.bulges)));}
  /* Load, then act; a failure is said, not thrown into the page. */
  function bimOcctRun(label,fn){
    if(A3D_OCCT.st!=='ready')a3dToast(label+': loading the solid modeller (about 7 MB, the first time only)...');
    return bimOcctLoad().then(function(R){
      try{return fn(R);}
      catch(e){console.warn('[BIM] '+label+' failed:',e);a3dToast(label+' failed: '+bimOcctErr(e));return null;}
    },function(e){a3dToast(label+': '+(e&&e.message||e));return null;});
  }
  /* OpenCASCADE throws numbers (its own exception pointers) as well as Errors */
  function bimOcctErr(e){return (e&&e.message)?e.message:(typeof e==='number'?'the geometry could not be built (try a smaller radius or thickness)':String(e));}
  function bimOcctNumDlg(title,fields,onOk){
    closeDlg();
    var d=document.createElement('div'),h='',i;
    d.className='a3d-dlg';
    for(i=0;i<fields.length;i++){
      var F=fields[i];
      if(F.options)h+='<div class="a3d-dlgrow"><label>'+bimEsc(F.label)+'</label><select data-a3doc="'+F.k+'">'+
        F.options.map(function(op){return '<option value="'+op[0]+'"'+(op[0]===F.v?' selected':'')+'>'+bimEsc(op[1])+'</option>';}).join('')+'</select></div>';
      else h+='<div class="a3d-dlgrow"><label>'+bimEsc(F.label)+'</label><input type="number" step="any" data-a3doc="'+F.k+'" value="'+F.v+'"></div>';
    }
    d.innerHTML='<div class="a3d-dlghd">'+bimEsc(title)+'</div><div class="a3d-dlgbody">'+h+'<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var v={},f=d.querySelectorAll('[data-a3doc]'),j;
      for(j=0;j<f.length;j++){var k=f[j].getAttribute('data-a3doc');v[k]=f[j].tagName==='SELECT'?f[j].value:parseFloat(f[j].value);}
      var err=onOk(v);
      if(err){d.querySelector('#a3d-dlgerr').textContent=err;return;}
      closeDlg();
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    return d;
  }
  /* ---------- EXTRUDE ---------- */
  function bimOcctExtrudeShape(R,o,h){
    var q=bimObjOffset(o),pts=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
    return bimOcctDrawing(R,pts,o.bulges||null).sketchOnPlane('XY',(o.y||0)+q[1]).extrude(h);
  }
  function bimOcctExtrude(ids,h){
    return bimOcctRun('EXTRUDE',function(R){
      var made=[],i;
      pushUndo();
      for(i=0;i<ids.length;i++){
        var o=objById(ids[i]);if(!bimOcctClosedSketch(o))continue;
        var s=bimOcctAddSolid(bimOcctExtrudeShape(R,o,h),'Extrusion');
        if(s){s.layer=o.layer||s.layer;made.push(s.id);}
      }
      if(!made.length){UNDO_STACK.pop();a3dToast('EXTRUDE: select closed sketches');return null;}
      A3D.selSet=made;A3D.sel=made[0];A3D.sel2=null;
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast('EXTRUDE: '+made.length+' solid(s), '+bimFmtLen(h)+' high');
      return made;
    });
  }
  function startOcctExtrude(){
    var ids=bimOcctSel().filter(bimOcctClosedSketch).map(function(o){return o.id;});
    if(!ids.length){a3dToast('EXTRUDE: select one or more closed sketches first');return;}
    bimOcctNumDlg('Extrude',[{k:'h',label:'Height, m',v:3}],function(v){
      if(!(v.h>0))return 'The height must be more than zero';
      bimOcctExtrude(ids,v.h);return '';
    });
  }
  /* ---------- FILLETEDGE, CHAMFEREDGE, SHELL ---------- */
  var BIM_OCCT_EDGESETS=[['all','All edges'],['vertical','Vertical edges'],['top','Top edges'],['bottom','Bottom edges'],['pick','Pick them (click edges)']];
  /* replicad's edge finder for one of the sets, the shape's height range given */
  function bimOcctEdgeFilter(set,zmin,zmax){
    if(set==='vertical')return function(e){return e.inDirection('Z');};
    if(set==='top')return function(e){return e.inPlane('XY',zmax);};
    if(set==='bottom')return function(e){return e.inPlane('XY',zmin);};
    return null;
  }
  function bimOcctZRange(shape){var b=shape.boundingBox.bounds;return [b[0][2],b[1][2]];}
  function bimOcctEdges(op,ids,r,set){
    return bimOcctRun(op==='fillet'?'FILLETEDGE':'CHAMFEREDGE',function(R){
      var n=0,i;
      pushUndo();
      for(i=0;i<ids.length;i++){
        var o=objById(ids[i]);if(!bimOcctIsSolid(o))continue;
        var s=bimOcctShapeOf(R,o),z=bimOcctZRange(s),f=bimOcctEdgeFilter(set,z[0],z[1]);
        var out=op==='fillet'?(f?s.fillet(r,f):s.fillet(r)):(f?s.chamfer(r,f):s.chamfer(r));
        if(bimOcctReplace(o,out))n++;
      }
      if(!n){UNDO_STACK.pop();a3dToast('Select solids made by EXTRUDE, REVOLVE, LOFT or STEP import');return null;}
      refreshTree();paint();saveSoon();
      a3dToast((op==='fillet'?'Filleted ':'Chamfered ')+n+' solid(s), '+bimFmtLen(r));
      return n;
    });
  }
  function startOcctEdges(op){
    var ids=bimOcctSel().filter(bimOcctIsSolid).map(function(o){return o.id;});
    if(!ids.length){a3dToast((op==='fillet'?'FILLETEDGE':'CHAMFEREDGE')+': select solids made by EXTRUDE, REVOLVE, LOFT or STEP import');return;}
    bimOcctNumDlg(op==='fillet'?'Fillet edges':'Chamfer edges',[{k:'r',label:(op==='fillet'?'Radius':'Distance')+', m',v:0.1},
      {k:'set',label:'Edges',options:BIM_OCCT_EDGESETS,v:'all'}],function(v){
      if(!(v.r>0))return 'It must be more than zero';
      if(v.set==='pick'){startOcctEdgePick(op,ids[0],v.r);return '';}   /* __acad3dV266: the first selected solid */
      bimOcctEdges(op,ids,v.r,v.set);return '';
    });
  }
  function bimOcctShell(ids,t){
    return bimOcctRun('SHELL',function(R){
      var n=0,i;
      pushUndo();
      for(i=0;i<ids.length;i++){
        var o=objById(ids[i]);if(!bimOcctIsSolid(o))continue;
        var s=bimOcctShapeOf(R,o),z=bimOcctZRange(s);
        if(bimOcctReplace(o,s.shell(t,function(fc){return fc.inPlane('XY',z[1]);})))n++;
      }
      if(!n){UNDO_STACK.pop();a3dToast('SHELL: select solids made by the solid tools');return null;}
      refreshTree();paint();saveSoon();
      a3dToast('Shelled '+n+' solid(s): walls '+bimFmtLen(t)+', the top open');
      return n;
    });
  }
  function startOcctShell(){
    var ids=bimOcctSel().filter(bimOcctIsSolid).map(function(o){return o.id;});
    if(!ids.length){a3dToast('SHELL: select solids made by the solid tools');return;}
    bimOcctNumDlg('Shell',[{k:'t',label:'Wall thickness, m',v:0.1}],function(v){
      if(!(v.t>0))return 'The thickness must be more than zero';
      bimOcctShell(ids,v.t);return '';
    });
  }
  /* ---------- REVOLVE ---------- */
  function startOcctRevolve(){
    var o=bimOcctSel().filter(bimOcctClosedSketch)[0];
    if(!o){a3dToast('REVOLVE: select a closed sketch first');return;}
    closeDlg();bimEnterDraftingMode();
    A3D.sk={tool:'revolveaxis',pts:[],y:(o.y||0)+bimObjOffset(o)[1],on:null,revId:o.id};
    a3dToast('REVOLVE: specify the start point of the axis');
    paint();
  }
  function bimOcctRevolveShape(R,o,a,b,deg){
    var q=bimObjOffset(o),pts=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),y=(o.y||0)+q[1];
    var A=bimOcctPt(a),B=bimOcctPt(b);
    return bimOcctDrawing(R,pts,o.bulges||null).sketchOnPlane('XY',y)
      .revolve([B[0]-A[0],B[1]-A[1],0],{origin:[A[0],A[1],y],angle:deg});
  }
  function bimOcctRevolvePoint(sk,p){
    sk.pts.push([p[0],p[1]]);
    if(sk.pts.length<2){a3dToast('REVOLVE: specify the end point of the axis');paint();return;}
    var id=sk.revId,a=sk.pts[0],b=sk.pts[1];
    A3D.sk=null;paint();
    if(Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])<1e-9){a3dToast('REVOLVE: the axis needs two different points');return;}
    bimOcctNumDlg('Revolve',[{k:'deg',label:'Angle, degrees',v:360}],function(v){
      if(!(v.deg>0&&v.deg<=360))return 'The angle is more than 0 and at most 360';
      bimOcctRun('REVOLVE',function(R){
        var o=objById(id);if(!o)return null;
        pushUndo();
        var s=bimOcctAddSolid(bimOcctRevolveShape(R,o,a,b,v.deg),'Revolution');
        if(!s){UNDO_STACK.pop();a3dToast('REVOLVE made nothing');return null;}
        s.layer=o.layer||s.layer;A3D.sel=s.id;A3D.selSet=[s.id];
        refreshTree();refreshHud();paint();saveSoon();
        a3dToast('REVOLVE: a solid of revolution, '+v.deg+'°');
        return s;
      });
      return '';
    });
  }
  /* ---------- LOFT ---------- */
  /* the selected closed sketches, lowest first: LOFT runs through them in height */
  function bimOcctLoftOrder(objs){
    return objs.filter(bimOcctClosedSketch).sort(function(a,b){return ((a.y||0)+bimObjOffset(a)[1])-((b.y||0)+bimObjOffset(b)[1]);});
  }
  function bimOcctLoft(){
    var L=bimOcctLoftOrder(bimOcctSel());
    if(L.length<2){a3dToast('LOFT: select two or more closed sketches at different heights');return null;}
    var h0=(L[0].y||0)+bimObjOffset(L[0])[1],h1=(L[L.length-1].y||0)+bimObjOffset(L[L.length-1])[1];
    if(Math.abs(h1-h0)<1e-6){a3dToast('LOFT: the sketches are at one height; put them on different levels or offsets');return null;}
    return bimOcctRun('LOFT',function(R){
      var sk=L.map(function(o){var q=bimObjOffset(o);
        return bimOcctDrawing(R,o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),o.bulges||null).sketchOnPlane('XY',(o.y||0)+q[1]);});
      pushUndo();
      var s=bimOcctAddSolid(sk[0].loftWith(sk.slice(1),{ruled:false}),'Loft');
      if(!s){UNDO_STACK.pop();a3dToast('LOFT made nothing');return null;}
      A3D.sel=s.id;A3D.selSet=[s.id];
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast('LOFT: a solid through '+L.length+' sections');
      return s;
    });
  }
  /* ---------- booleans ---------- */
  function bimOcctBoolean(op){
    var S=bimOcctSel().filter(bimOcctIsSolid);
    if(S.length<2){a3dToast('Select two or more solids made by the solid tools (the first is kept)');return null;}
    return bimOcctRun(op==='fuse'?'SOLIDUNION':op==='cut'?'SOLIDSUBTRACT':'SOLIDINTERSECT',function(R){
      var base=S[0],shape=bimOcctShapeOf(R,base),i;
      for(i=1;i<S.length;i++){
        var t=bimOcctShapeAt(R,S[i],base);   /* in the first solid's frame, its offset kept */
        shape=op==='fuse'?shape.fuse(t):op==='cut'?shape.cut(t):shape.intersect(t);
      }
      pushUndo();
      if(!bimOcctReplace(base,shape)){UNDO_STACK.pop();a3dToast('Nothing is left of that operation');return null;}
      for(i=1;i<S.length;i++)A3D.objs.splice(A3D.objs.indexOf(S[i]),1);
      A3D.sel=base.id;A3D.selSet=[base.id];
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast((op==='fuse'?'Joined ':op==='cut'?'Subtracted from ':'Intersected ')+base.name);
      return base;
    });
  }
  /* ---------- STEP ---------- */
  function bimOcctExportStep(){
    var S=bimOcctSel().filter(bimOcctIsSolid);
    if(!S.length)S=A3D.objs.filter(bimOcctIsSolid);
    if(!S.length){a3dToast('EXPORTSTEP: no solids made by the solid tools to export');return null;}
    return bimOcctRun('EXPORTSTEP',function(R){
      var blob=R.exportSTEP(S.map(function(o){return {shape:bimOcctShapeAt(R,o,null),name:o.name||o.id};}),{unit:'M',modelUnit:'M'});   /* where the model shows them */
      var nm=bimFileStem()+'.step';
      bimTriggerDownload(blob,nm,'model/step');
      a3dToast('Exported '+nm+' ('+S.length+' solid(s))');
      return blob;
    });
  }
  function bimOcctImportStep(buf,name){
    return bimOcctRun('STEP import',function(R){
      return R.importSTEP(new Blob([buf])).then(function(shape){
        pushUndo();
        var s=bimOcctAddSolid(shape,String(name||'STEP').replace(/\.[^.]+$/,''));
        if(!s){UNDO_STACK.pop();a3dToast('STEP import: nothing with faces in '+name);return null;}
        A3D.sel=s.id;A3D.selSet=[s.id];
        refreshTree();refreshHud();fitScene();paint();saveSoon();
        a3dToast('STEP import: '+name+' ('+s.mesh.f.length+' triangles)');
        return s;
      },function(e){a3dToast('STEP import failed: '+bimOcctErr(e));return null;});
    });
  }
export {
  bimOcctBoolean, bimOcctClosedSketch, bimOcctExportStep, bimOcctImportStep, bimOcctLoft, bimOcctNumDlg,
  bimOcctRevolvePoint, bimOcctRun, bimOcctSel, startOcctEdges, startOcctExtrude, startOcctRevolve,
  startOcctShell
};
