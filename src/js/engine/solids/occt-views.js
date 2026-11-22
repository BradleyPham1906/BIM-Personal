import { A3D, el } from '../core/state.js';
import { pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimCreateTextLabel } from '../annotation/dimensions.js';
import { bimLayerByName, bimLayerChanged, bimLayerNew } from '../layers/select-change.js';
import { bimOcctIsSolid, bimOcctShapeAt } from './occt-adapter.js';
import { bimOcctRun, bimOcctSel } from './occt-tools.js';
import { paint } from '../map/terrain-3d.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV272: drawing views of solids (AutoCAD's VIEWBASE, FreeCAD's TechDraw) =================
     The selected OpenCASCADE solids projected with OpenCASCADE's exact hidden-line removal (HLRBRep, through
     replicad's makeProjectedEdges): front, top, right and an isometric view, each as plain 2D lines in the plan,
     visible edges on "Drawing - visible", hidden ones dashed on "Drawing - hidden", laid out in third-angle
     projection (top above front, right beside it, the isometric up and right) east of the solids. They are ordinary
     sketches: dimension them, put them on a sheet. Exact on the B-rep, unlike Make2D on meshes (v189), which stays
     for meshes. The camera and the layout are pure, tested without a page; a view's direction points at the viewer,
     its x along xAxis and its y along direction x xAxis, as OpenCASCADE's projector takes them (measured, 2026-11-22).
     The app's (x, y, z) is OpenCASCADE's (x, -z, y) (occt-adapter.js). */
  var BIM_VIEWBASE_VIEWS={
    front:{dir:[0,-1,0],x:[1,0,0],label:'Front'},
    top:{dir:[0,0,1],x:[1,0,0],label:'Top'},
    right:{dir:[1,0,0],x:[0,1,0],label:'Right'},
    iso:{dir:[1,-1,1],x:[1,1,0],label:'Isometric'}};
  function bimVbUnit(v){var l=Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);return [v[0]/l,v[1]/l,v[2]/l];}
  /* Polylines [u, v] from projected edges: a line by its ends, a curve sampled. Pure on replicad's edges. */
  function bimVbPolylines(edges,samples){
    var out=[],i,k;
    for(i=0;i<edges.length;i++){
      var e=edges[i],pts=[];
      if(e.geomType==='LINE')pts=[e.startPoint.toTuple(),e.endPoint.toTuple()];
      else for(k=0;k<=samples;k++)pts.push(e.pointAt(k/samples).toTuple());
      out.push(pts.map(function(p){return [p[0],p[1]];}));
    }
    return out;
  }
  function bimVbBox(lines){
    var b=[Infinity,Infinity,-Infinity,-Infinity];
    lines.forEach(function(L){L.forEach(function(p){b[0]=Math.min(b[0],p[0]);b[1]=Math.min(b[1],p[1]);b[2]=Math.max(b[2],p[0]);b[3]=Math.max(b[3],p[1]);});});
    return b[0]===Infinity?[0,0,0,0]:b;
  }
  /* Where each view goes: {name: [du, dv]} added to its own (u, v), third-angle, a gap between. Pure.
     boxes: {name: [umin, vmin, umax, vmax]}; the front view's lower left lands on (0, 0). */
  function bimVbLayout(boxes,gap){
    var F=boxes.front||[0,0,0,0],out={};
    var fw=F[2]-F[0],fh=F[3]-F[1];
    if(boxes.front)out.front=[-F[0],-F[1]];
    if(boxes.top){var T=boxes.top;out.top=[-T[0],fh+gap-T[1]];}
    if(boxes.right){var Rr=boxes.right;out.right=[fw+gap-Rr[0],-Rr[1]];}
    if(boxes.iso){var I=boxes.iso,rw=boxes.right?boxes.right[2]-boxes.right[0]+gap:0;out.iso=[fw+gap+rw-I[0],fh+gap-I[1]];}
    for(var k in out)out[k]=[out[k][0]+0,out[k][1]+0];   /* -0 read as 0 */
    return out;
  }
  function bimVbLayer(name,linetype){
    var L=bimLayerByName(name);
    if(!L){L=bimLayerNew({name:name});if(L&&linetype){L.linetype=linetype;bimLayerChanged();}}
    return L?L.id:A3D.activeLayer;
  }
  function openViewbaseDlg(){
    var S=bimOcctSel().filter(bimOcctIsSolid);
    if(!S.length){a3dToast('VIEWBASE: select solids made by the solid tools');return null;}
    closeDlg();
    var d=document.createElement('div');d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Drawing views</div><div class="a3d-dlgbody">'+
      ['front','top','right','iso'].map(function(k){return '<div class="a3d-dlgrow"><label>'+BIM_VIEWBASE_VIEWS[k].label+'</label><input type="checkbox" data-a3dvb="'+k+'" checked></div>';}).join('')+
      '<div class="a3d-dlgrow"><label>Hidden lines</label><input type="checkbox" data-a3dvb="hidden" checked></div>'+
      '<div class="a3d-dlgrow"><label>Gap between views, m</label><input type="number" min="0" step="any" data-a3dvb="gap" value="1"></div>'+
      '<div class="a3d-propnote">Exact hidden lines from OpenCASCADE, drawn east of the solids as 2D lines.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Draw</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;
      if(b.getAttribute('data-a3dlg')!=='ok'){closeDlg();return;}
      var views=['front','top','right','iso'].filter(function(k){return d.querySelector('[data-a3dvb="'+k+'"]').checked;});
      if(!views.length){d.querySelector('#a3d-dlgerr').textContent='Choose a view';return;}
      var hid=d.querySelector('[data-a3dvb="hidden"]').checked,gap=Math.max(0,+d.querySelector('[data-a3dvb="gap"]').value||0);
      closeDlg();
      bimViewbase(S.map(function(o){return o.id;}),views,hid,gap);
    });
    return d;
  }
  function bimViewbase(ids,views,hidden,gap){
    return bimOcctRun('VIEWBASE',function(R){
      var S=ids.map(objById).filter(bimOcctIsSolid),shape=null,i,v;
      if(!S.length)return null;
      for(i=0;i<S.length;i++){var s=bimOcctShapeAt(R,S[i],null);shape=shape?shape.fuse(s):s;}
      var got={},boxes={};
      for(i=0;i<views.length;i++){
        v=BIM_VIEWBASE_VIEWS[views[i]];
        var cam=new R.ProjectionCamera([0,0,0],bimVbUnit(v.dir),bimVbUnit(v.x));
        var r=R.makeProjectedEdges(shape,cam,hidden);
        got[views[i]]={vis:bimVbPolylines(r.visible,24),hid:hidden?bimVbPolylines(r.hidden,24):[]};
        boxes[views[i]]=bimVbBox(got[views[i]].vis.concat(got[views[i]].hid));
      }
      var place=bimVbLayout(boxes,gap);
      /* east of the solids, at the active level */
      var bb=shape.boundingBox.bounds,x0=bb[1][0]+Math.max(2,gap*2),z0=-bb[0][1],y=bimGetActiveLevel().elev;
      pushUndo();
      setUndoSuspend(true);   /* the layers and labels made here push their own steps: VIEWBASE is one */
      try{
      var layV=bimVbLayer('Drawing - visible',null),layH=hidden?bimVbLayer('Drawing - hidden','HIDDEN'):null,made=[];
      for(i=0;i<views.length;i++){
        var k=views[i],off=place[k]||[0,0],G=got[k];
        [[G.vis,layV],[G.hid,layH]].forEach(function(pair){
          pair[0].forEach(function(L){
            if(L.length<2)return;
            A3D.counts.sketch=(A3D.counts.sketch||0)+1;
            var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:BIM_VIEWBASE_VIEWS[k].label+' view '+A3D.counts.sketch,
              pts:L.map(function(p){return [x0+p[0]+off[0],z0-(p[1]+off[1])];}),closed:false,y:y,pos:[0,0,0],layer:pair[1],col:'#dfe4ea'};
            A3D.objs.push(o);made.push(o.id);
          });
        });
        var bx=boxes[k];
        var lab=bimCreateTextLabel([x0+off[0]+bx[0],z0-(off[1]+bx[1])+0.4],y,BIM_VIEWBASE_VIEWS[k].label.toUpperCase(),{height:0.25});
        if(lab){lab.layer=layV;made.push(lab.id);}
      }
      }finally{setUndoSuspend(false);}
      A3D.selSet=made;A3D.sel=made[0]||null;
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast('VIEWBASE: '+views.length+' view(s), '+made.length+' objects');
      return made;
    });
  }
export { openViewbaseDlg };
