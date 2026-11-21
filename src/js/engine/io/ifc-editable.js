import { A3D } from '../core/state.js';
import { pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { buildWallSolid } from '../bim/import-compliance.js';
import { buildFloorSolid } from '../bim/ceiling-floor-profile.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV177: Make editable, an imported IFC wall or floor as one of the app's own =================
     docs/work-orders/v177/SPEC.md part 1 (the owner's D3, 2026-11-13: editing imported walls and slabs in V177). The
     full import keeps each IfcWall's and IfcSlab's walls-and-slabs parameters (import-ifc.js, bimIfcEditParams) in
     bim.edit. Make editable rebuilds the element from them as an app wall or floor, under the same GlobalId, so Save as
     IFC writes it back as the element it was. The rebuilt shape must lie where the imported one does: the reader's
     plan is tried in IFC's axes and turned to the app's (z = -north), each moved by the import's shift to the origin
     (bim.edit.shift, the engine's coordination matrix), and the one whose box matches the imported mesh's is taken; neither matching, or a wall voided by an opening (the cut is not rebuilt), it is refused and says why. */
  /* a mesh's box [minX, minY, minZ, maxX, maxY, maxZ], or null */
  function bimIfcEdBox(m){
    var v=m&&m.v,i,b=null,p;
    if(!v||!v.length)return null;
    for(i=0;i<v.length;i++){
      p=v[i];
      if(!b){b=[p[0],p[1],p[2],p[0],p[1],p[2]];continue;}
      if(p[0]<b[0])b[0]=p[0];if(p[1]<b[1])b[1]=p[1];if(p[2]<b[2])b[2]=p[2];
      if(p[0]>b[3])b[3]=p[0];if(p[1]>b[4])b[4]=p[1];if(p[2]>b[5])b[5]=p[2];
    }
    return b;
  }
  /* whether two boxes agree to 2 cm, or 1% of the larger's size */
  function bimIfcEdSame(a,b){
    var i,t;
    if(!a||!b)return false;
    t=Math.max(0.02,0.01*Math.max(a[3]-a[0],a[4]-a[1],a[5]-a[2]));
    for(i=0;i<6;i++)if(Math.abs(a[i]-b[i])>t)return false;
    return true;
  }
  /* the plan of the rebuild, pure: {kind:'wall', pts, y0, height, thickness} or {kind:'floor', pts, top, thickness};
     {why} when it cannot be made editable */
  function bimIfcEditPlan(o){
    var b=o&&o.bim,e=b&&b.edit,k,turn,pts,box,want,i,S,mv;
    if(!b||!b.imported)return {why:'it was not imported from an IFC file'};
    if(b.type!=='wall'&&b.type!=='floor')return {why:'only imported walls and floors can be made editable'};
    if(!e||!e.profile||!(e.height>0))return {why:'its shape is not a vertical extrusion the walls-and-slabs reader can follow'};
    if(b.type==='wall'&&e.voided)return {why:'an opening cuts it, and Make editable does not rebuild the cut yet'};
    if(b.type==='wall'&&!e.wall)return {why:'its plan is not a rectangle, so it has no single centreline'};
    box=bimIfcEdBox(o.mesh);
    if(!box)return {why:'it has no shape'};
    S=(e.shift&&e.shift.length===3)?e.shift:[0,0,0];
    for(k=0;k<2;k++){
      turn=k===1;
      mv=function(p){return [p[0]+S[0],(turn?-p[1]:p[1])+S[2]];};
      pts=e.profile.map(mv);
      want=[Infinity,e.baseY+S[1],Infinity,-Infinity,e.baseY+e.height+S[1],-Infinity];
      for(i=0;i<pts.length;i++){
        if(pts[i][0]<want[0])want[0]=pts[i][0];if(pts[i][1]<want[2])want[2]=pts[i][1];
        if(pts[i][0]>want[3])want[3]=pts[i][0];if(pts[i][1]>want[5])want[5]=pts[i][1];
      }
      if(!bimIfcEdSame(box,want))continue;
      if(b.type==='floor')return {kind:'floor',pts:pts,top:e.baseY+e.height+S[1],thickness:e.height};
      return {kind:'wall',pts:e.wall.centerline.map(mv),y0:e.wall.baseY+S[1],height:e.wall.height,thickness:e.wall.thickness};
    }
    return {why:'the walls-and-slabs reader places it elsewhere than the imported shape'};
  }
  /* Make editable: the element rebuilt as the app's own, in its place on the list, keeping its name, layer, GlobalId,
     IFC class, storey and property sets; one undo step. The new element, or null (a toast says why). */
  function bimIfcMakeEditable(id){
    var o=objById(id),P,n=null,b,k,at;
    if(!o){a3dToast('Nothing to make editable');return null;}
    P=bimIfcEditPlan(o);
    if(P.why){a3dToast(o.name+' cannot be made editable: '+P.why);return null;}
    b=o.bim;
    pushUndo();
    setUndoSuspend(true);
    try{
      if(P.kind==='wall')n=buildWallSolid(P.pts,P.y0,P.height,P.thickness,'center',false);
      else n=buildFloorSolid({pts:P.pts,y:P.top},P.thickness,'Concrete',bimGetActiveLevel());
      if(n){
        n.name=o.name;n.layer=o.layer;
        for(k in {guid:1,ifcType:1,storey:1,file:1,psets:1})if(b[k]!==undefined)n.bim[k]=b[k];
        at=A3D.objs.indexOf(o);
        A3D.objs.splice(A3D.objs.indexOf(n),1);
        A3D.objs.splice(at,1,n);
        A3D.sel=n.id;A3D.sel2=null;A3D.selSet=[n.id];
      }
    }catch(eM){
      console.warn('[BIM] Make editable failed for '+o.name,eM);
      n=null;
    }finally{setUndoSuspend(false);}
    if(!n){a3dToast(o.name+' could not be made editable - see the console');return null;}
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(o.name+' is now an editable '+P.kind+', saved under its GlobalId');
    return n;
  }
  /* Properties: the button, for an imported wall or floor */
  function bimIfcEditButtonHtml(o){
    var b=o&&o.bim;
    if(!b||!b.imported||(b.type!=='wall'&&b.type!=='floor'))return '';
    var P=bimIfcEditPlan(o);
    return bimPropRow('Editing',P.why?'<span title="'+bimEsc(P.why)+'">Not editable: '+bimEsc(P.why)+'</span>':
      '<button type="button" class="a3d-pedit" data-ifcedit="'+bimEsc(o.id)+'">Make editable</button>');
  }
export { bimIfcEdBox, bimIfcEdSame, bimIfcEditButtonHtml, bimIfcEditPlan, bimIfcMakeEditable };
