import { A3D } from '../core/state.js';
import { camVecs } from '../core/mesh-primitives.js';
import { bimMaterialCards } from '../bim/type-instance-params.js';
import { toScreen } from '../io/import-entry.js';
import { A3D_PC, bimPcData, bimPcIsCloud } from '../map/pointcloud-view.js';
import { bimSheet } from '../views/spreadsheet.js';
import { cvH, cvW } from '../ui/canvas-size.js';

  /* __acad3dV266-V273: what the FreeCAD-gap browser check (tests/e2e/bim_phase266_273_check.mjs) reads */
  window.__a3dEdgePick=function(){
    var sk=A3D.sk;
    if(!sk||sk.tool!=='occtedge')return null;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    return {picked:sk.picked.slice(),edges:sk.edges.map(function(e){var m=e.pts[Math.floor(e.pts.length/2)],s=toScreen(m,V,W,H);
      return {a:e.pts[0],b:e.pts[e.pts.length-1],mid:m,screen:[s[0],s[1]]};})};
  };
  window.__a3dMatCards=function(){return JSON.parse(JSON.stringify(bimMaterialCards()));};
  window.__a3dSheetState=function(){return JSON.parse(JSON.stringify(bimSheet()));};
  window.__a3dPcState=function(){
    return {drewGl:!!A3D_PC.drewGl,budget:A3D_PC.budget,preview:A3D_PC.preview?A3D_PC.preview.pts.length:0,
      clouds:A3D.objs.filter(bimPcIsCloud).map(function(o){var D=bimPcData(o);return {id:o.id,name:o.name,n:o.pc.n,count:o.pc.count,origin:o.pc.origin,
        mode:o.pc.mode,classes:o.pc.classes,hidden:o.pc.hidden,loaded:!!D};})};
  };
  window.__a3dWorldToScreen=function(p){var s=toScreen(p,camVecs(A3D.cam),cvW(),cvH());return [s[0],s[1]];};
