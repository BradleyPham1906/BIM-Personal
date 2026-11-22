import { A3D } from '../core/state.js';
import { camVecs } from '../core/mesh-primitives.js';
import { UNDO_STACK, bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import {
  bimOcctAddSolid, bimOcctDrawing, bimOcctIsSolid, bimOcctOffsetXYZ, bimOcctPt, bimOcctReplace,
  bimOcctShapeAt, bimOcctShapeOf
} from './occt-adapter.js';
import { bimOcctClosedSketch, bimOcctNumDlg, bimOcctRun, bimOcctSel } from './occt-tools.js';
import { toScreen } from '../io/import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { BIM_BULGE_EPS, bimBulgeAt } from '../drawing/arc-storage.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';
import { cvH, cvW } from '../ui/canvas-size.js';

  /* ================= __acad3dV266: more of FreeCAD's PartDesign on OpenCASCADE =================
     What V264 left open (docs/research/research-occt-library.md, section 6):
     - FILLETEDGE and CHAMFEREDGE on edges picked with the mouse: the solid's edges are drawn over it, a click takes the
       one nearest the cursor on the screen (in any view), Enter applies. An edge is known again by its midpoint.
     - DRAFTANGLE (TAPER): FreeCAD's Draft feature, AutoCAD's SOLIDEDIT taper: the side faces of a solid tilted by an
       angle about its bottom plane, inward for a positive angle, as a mould needs.
     - SWEEP: a closed sketch (the section) swept along an open sketch (the path), as AutoCAD's SWEEP and FreeCAD's
       Sweep: the section is set square to the path at its start, centred on it.
     - SOLIDPATTERN: FreeCAD's LinearPattern, PolarPattern and Mirrored: copies of a solid, joined into it.
     - THICKNESS: FreeCAD's Thickness: SHELL with the open face chosen (the top, the bottom, or both).
     Each loads OpenCASCADE the first time and is one undo step. The pure parts (the edge nearest a click, the pattern's
     placements) are tested without a canvas. */
  /* ---------- edges picked with the mouse ---------- */
  var BIM_OCCT_EDGE_SAMPLES=12;
  /* An OpenCASCADE point (X, Y, Z) where the app shows it: (x, y, z) = (X, Z, -Y), plus the object's offset. */
  function bimOcctToApp(P,q){return [P[0]+q[0],P[2]+q[1],-P[1]+q[2]];}
  /* The edges of a shape as polylines in the app's frame, each with its midpoint in OpenCASCADE's. */
  function bimOcctEdgeLines(shape,q){
    var out=[],E=shape.edges,i,k;
    for(i=0;i<E.length;i++){
      var pts=[];
      for(k=0;k<=BIM_OCCT_EDGE_SAMPLES;k++)pts.push(bimOcctToApp(E[i].pointAt(k/BIM_OCCT_EDGE_SAMPLES).toTuple(),q));
      out.push({pts:pts,mid:E[i].pointAt(0.5).toTuple()});
    }
    return out;
  }
  /* The edge nearest a screen point, within tol pixels, from edges already projected to the screen. Pure. */
  function bimOcctNearestEdge(screenEdges,xy,tol){
    var best=-1,bd=tol,i,k;
    for(i=0;i<screenEdges.length;i++){
      var S=screenEdges[i];
      for(k=0;k+1<S.length;k++){
        var a=S[k],b=S[k+1],dx=b[0]-a[0],dy=b[1]-a[1],L=dx*dx+dy*dy,t=L>0?((xy[0]-a[0])*dx+(xy[1]-a[1])*dy)/L:0;
        t=Math.max(0,Math.min(1,t));
        var ex=a[0]+dx*t-xy[0],ey=a[1]+dy*t-xy[1],d=Math.sqrt(ex*ex+ey*ey);
        if(d<bd){bd=d;best=i;}
      }
    }
    return best;
  }
  function bimOcctSameMid(a,b){return Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])<1e-6;}
  function startOcctEdgePick(op,id,r){
    var label=op==='fillet'?'FILLETEDGE':'CHAMFEREDGE';
    return bimOcctRun(label,function(R){
      var o=objById(id);if(!o)return null;
      var edges=bimOcctEdgeLines(bimOcctShapeOf(R,o),bimObjOffset(o));
      if(A3D.sk)A3D.sk=null;
      A3D.sk={tool:'occtedge',pts:[],y:0,on:null,op:op,r:r,id:id,edges:edges,picked:[]};
      a3dToast(label+': click the edges ('+edges.length+' on this solid), then Enter');
      paint();
      return A3D.sk;
    });
  }
  function bimOcctEdgeScreen(sk){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    return sk.edges.map(function(e){return e.pts.map(function(p){return toScreen(p,V,W,H);});});
  }
  function bimOcctEdgeClick(sk,xy){
    var i=bimOcctNearestEdge(bimOcctEdgeScreen(sk),xy,14);
    if(i<0){a3dToast('No edge there: click on one of the drawn edges');return;}
    var at=sk.picked.indexOf(i);
    if(at>=0)sk.picked.splice(at,1);else sk.picked.push(i);
    a3dToast(sk.picked.length+' edge(s) picked; Enter applies, Esc cancels');
    paint();
  }
  function bimOcctEdgeDraw(ctx,V,W,H){
    var sk=A3D.sk,i,k;
    if(!sk||sk.tool!=='occtedge')return;
    ctx.save();
    for(i=0;i<sk.edges.length;i++){
      var on=sk.picked.indexOf(i)>=0,P=sk.edges[i].pts;
      ctx.strokeStyle=on?'#ff9f1a':'rgba(78,161,255,0.85)';ctx.lineWidth=on?3:1.5;
      ctx.beginPath();
      for(k=0;k<P.length;k++){var s=toScreen(P[k],V,W,H);if(k)ctx.lineTo(s[0],s[1]);else ctx.moveTo(s[0],s[1]);}
      ctx.stroke();
    }
    ctx.restore();
  }
  function bimOcctEdgeFinish(sk){
    A3D.sk=null;paint();
    if(!sk.picked.length){a3dToast('No edges picked');return null;}
    var mids=sk.picked.map(function(i){return sk.edges[i].mid;}),label=sk.op==='fillet'?'FILLETEDGE':'CHAMFEREDGE';
    return bimOcctRun(label,function(R){
      var o=objById(sk.id);if(!o)return null;
      var s=bimOcctShapeOf(R,o);
      var f=function(e){var m=e.pointAt(0.5).toTuple(),j;for(j=0;j<mids.length;j++)if(bimOcctSameMid(m,mids[j]))return sk.r;return null;};
      var out=sk.op==='fillet'?s.fillet(f):s.chamfer(f);
      pushUndo();
      if(!bimOcctReplace(o,out)){UNDO_STACK.pop();a3dToast(label+' made nothing');return null;}
      refreshTree();paint();saveSoon();
      a3dToast((sk.op==='fillet'?'Filleted ':'Chamfered ')+mids.length+' edge(s), '+bimFmtLen(sk.r));
      return o;
    });
  }
  /* ---------- DRAFTANGLE ---------- */
  function bimOcctDraft(ids,deg){
    return bimOcctRun('DRAFTANGLE',function(R){
      var n=0,i;
      pushUndo();
      for(i=0;i<ids.length;i++){
        var o=objById(ids[i]);if(!bimOcctIsSolid(o))continue;
        var s=bimOcctShapeOf(R,o),b=s.boundingBox.bounds;
        /* the side faces: their normals square to the vertical; the neutral plane is the bottom */
        var out=s.draft(deg,function(fc){return fc.atAngleWith('Z',90);},R.makePlane('XY',[0,0,b[0][2]]));
        if(bimOcctReplace(o,out))n++;
      }
      if(!n){UNDO_STACK.pop();a3dToast('DRAFTANGLE: select solids made by the solid tools');return null;}
      refreshTree();paint();saveSoon();
      a3dToast('Drafted the sides of '+n+' solid(s) by '+deg+'°');
      return n;
    });
  }
  function startOcctDraft(){
    var ids=bimOcctSel().filter(bimOcctIsSolid).map(function(o){return o.id;});
    if(!ids.length){a3dToast('DRAFTANGLE: select solids made by the solid tools');return;}
    bimOcctNumDlg('Draft angle',[{k:'deg',label:'Angle of the sides, degrees (positive leans in)',v:3}],function(v){
      if(!(Math.abs(v.deg)>0&&Math.abs(v.deg)<45))return 'The angle is between -45 and 45, not 0';
      bimOcctDraft(ids,v.deg);return '';
    });
  }
  /* ---------- SWEEP ---------- */
  function bimOcctOpenSketch(o){return !!(o&&o.t==='sketch'&&o.closed===false&&o.pts&&o.pts.length>=2);}
  /* A section's outline centred on its own middle (its box's centre), as the sweep sets it on the path. */
  function bimOcctCentred(pts){
    var x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity,i;
    for(i=0;i<pts.length;i++){x0=Math.min(x0,pts[i][0]);x1=Math.max(x1,pts[i][0]);z0=Math.min(z0,pts[i][1]);z1=Math.max(z1,pts[i][1]);}
    var cx=(x0+x1)/2,cz=(z0+z1)/2;
    return pts.map(function(p){return [p[0]-cx,p[1]-cz];});
  }
  function bimOcctPathDrawing(R,o){
    var q=bimObjOffset(o),P=o.pts.map(function(p){return bimOcctPt([p[0]+q[0],p[1]+q[2]]);}),d=R.draw(P[0]),i;
    for(i=1;i<P.length;i++){
      var b=-bimBulgeAt(o.bulges,i-1);
      d=Math.abs(b)>BIM_BULGE_EPS?d.bulgeArcTo(P[i],b):d.lineTo(P[i]);
    }
    return d.done().sketchOnPlane('XY',(o.y||0)+q[1]);
  }
  function bimOcctSweep(){
    var S=bimOcctSel(),sec=S.filter(bimOcctClosedSketch)[0],path=S.filter(bimOcctOpenSketch)[0];
    if(!sec||!path){a3dToast('SWEEP: select one closed sketch (the section) and one open sketch (the path)');return null;}
    return bimOcctRun('SWEEP',function(R){
      var prof=bimOcctCentred(sec.pts);
      var shape=bimOcctPathDrawing(R,path).sweepSketch(function(plane,origin){
        return bimOcctDrawing(R,prof,sec.bulges||null).sketchOnPlane(plane,origin);
      },{transitionMode:'round'});
      pushUndo();
      var s=bimOcctAddSolid(shape,'Sweep');
      if(!s){UNDO_STACK.pop();a3dToast('SWEEP made nothing');return null;}
      s.layer=sec.layer||s.layer;A3D.sel=s.id;A3D.selSet=[s.id];
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast('SWEEP: '+(sec.name||'the section')+' along '+(path.name||'the path'));
      return s;
    });
  }
  /* ---------- SOLIDPATTERN ---------- */
  /* The placements of a pattern's copies (the original not counted), in the app's frame. Pure.
     linear: {count, dx, dy, dz}; polar: {count, angle (the whole, degrees), cx, cz} about the vertical through (cx, cz),
     the copies spread over the angle (a full turn is shared out without a copy on the original); mirror: {axis 'x' or
     'z', at}, one copy reflected in the plane x = at or z = at. */
  function bimOcctPatternSteps(p){
    var out=[],i,n=Math.max(1,Math.round(p.count||1));
    if(p.type==='linear')for(i=1;i<n;i++)out.push({move:[p.dx*i,(p.dy||0)*i,p.dz*i]});
    else if(p.type==='polar'){
      var full=Math.abs(Math.abs(p.angle)-360)<1e-9,step=n>1?p.angle/(full?n:n-1):0;
      for(i=1;i<n;i++)out.push({turn:step*i,about:[p.cx||0,p.cz||0]});
    }
    else if(p.type==='mirror')out.push({mirror:p.axis==='z'?'z':'x',at:p.at||0});
    return out;
  }
  /* One placement on an OpenCASCADE shape: the app's (x, y, z) is OpenCASCADE's (x, -z, y), so OpenCASCADE's XY seen
     from above is the plan with north up: a turn about the app's vertical, counter-clockwise on the plan for a positive
     angle, is the same turn about Z; and the plane z = c is Y = -c. */
  function bimOcctPlace(s,st){
    if(st.move)return s.clone().translate(st.move[0],-st.move[2],st.move[1]);
    if(st.turn!=null)return s.clone().rotate(st.turn,[st.about[0],-st.about[1],0],[0,0,1]);
    return st.mirror==='x'?s.clone().mirror([1,0,0],[st.at,0,0]):s.clone().mirror([0,1,0],[0,-st.at,0]);
  }
  function bimOcctPattern(id,p){
    return bimOcctRun('SOLIDPATTERN',function(R){
      var o=objById(id);if(!bimOcctIsSolid(o))return null;
      var steps=bimOcctPatternSteps(p),q=bimObjOffset(o),off=bimOcctOffsetXYZ(q),i;
      if(!steps.length){a3dToast('SOLIDPATTERN: that pattern has no copies');return null;}
      /* in the model's frame (the offset applied), then back into the solid's own */
      var base=bimOcctShapeAt(R,o,null),shape=base;
      for(i=0;i<steps.length;i++)shape=shape.fuse(bimOcctPlace(base,steps[i]));
      if(off[0]||off[1]||off[2])shape=shape.translate(-off[0],-off[1],-off[2]);
      pushUndo();
      if(!bimOcctReplace(o,shape)){UNDO_STACK.pop();a3dToast('SOLIDPATTERN made nothing');return null;}
      refreshTree();paint();saveSoon();
      a3dToast('SOLIDPATTERN: '+(steps.length+1)+' copies joined into '+o.name);
      return o;
    });
  }
  function startOcctPattern(){
    var o=bimOcctSel().filter(bimOcctIsSolid)[0];
    if(!o){a3dToast('SOLIDPATTERN: select a solid made by the solid tools');return;}
    bimOcctNumDlg('Pattern',[{k:'type',label:'Pattern',options:[['linear','Linear'],['polar','Polar'],['mirror','Mirrored']],v:'linear'},
      {k:'count',label:'Count (linear, polar)',v:3},{k:'dx',label:'Linear: step east, m',v:2},{k:'dz',label:'Linear: step south, m',v:0},
      {k:'dy',label:'Linear: step up, m',v:0},{k:'angle',label:'Polar: angle, degrees',v:360},{k:'cx',label:'Polar: centre x, m',v:0},
      {k:'cz',label:'Polar: centre z, m',v:0},{k:'axis',label:'Mirrored: plane',options:[['x','x = (east-west mirror)'],['z','z = (north-south mirror)']],v:'x'},
      {k:'at',label:'Mirrored: at, m',v:0}],function(v){
      if(v.type!=='mirror'&&!(v.count>=2))return 'A pattern needs a count of 2 or more';
      if(v.type==='linear'&&!(v.dx||v.dz||v.dy))return 'A linear pattern needs a step';
      if(v.type==='polar'&&!(Math.abs(v.angle)>0&&Math.abs(v.angle)<=360))return 'The angle is more than 0 and at most 360';
      bimOcctPattern(o.id,v);return '';
    });
  }
  /* ---------- THICKNESS ---------- */
  function bimOcctThickness(ids,t,open){
    return bimOcctRun('THICKNESS',function(R){
      var n=0,i;
      pushUndo();
      for(i=0;i<ids.length;i++){
        var o=objById(ids[i]);if(!bimOcctIsSolid(o))continue;
        var s=bimOcctShapeOf(R,o),b=s.boundingBox.bounds,z0=b[0][2],z1=b[1][2];
        var out=s.shell(t,function(fc){
          if(open==='bottom')return fc.inPlane('XY',z0);
          if(open==='both')return fc.either([function(f){return f.inPlane('XY',z0);},function(f){return f.inPlane('XY',z1);}]);
          return fc.inPlane('XY',z1);
        });
        if(bimOcctReplace(o,out))n++;
      }
      if(!n){UNDO_STACK.pop();a3dToast('THICKNESS: select solids made by the solid tools');return null;}
      refreshTree();paint();saveSoon();
      a3dToast('THICKNESS: '+n+' solid(s), walls '+bimFmtLen(t)+', open at the '+(open==='both'?'top and bottom':open));
      return n;
    });
  }
  function startOcctThickness(){
    var ids=bimOcctSel().filter(bimOcctIsSolid).map(function(o){return o.id;});
    if(!ids.length){a3dToast('THICKNESS: select solids made by the solid tools');return;}
    bimOcctNumDlg('Thickness',[{k:'t',label:'Wall thickness, m',v:0.1},
      {k:'open',label:'Open face',options:[['top','The top'],['bottom','The bottom'],['both','Top and bottom']],v:'top'}],function(v){
      if(!(v.t>0))return 'The thickness must be more than zero';
      bimOcctThickness(ids,v.t,v.open);return '';
    });
  }
export {
  bimOcctEdgeClick, bimOcctEdgeDraw, bimOcctEdgeFinish, bimOcctSweep, startOcctDraft, startOcctEdgePick,
  startOcctPattern, startOcctThickness
};
