import { bimSegNormal } from '../bim/section-profiles.js';
import { bimAlignOffsets } from '../bim/footings.js';
import { bimRectFootprint } from '../bim/columns-openings.js';
import { bimHasBulge } from '../drawing/arc-storage.js';

/* __acad3dV177: the model as the plain data IfcOpenShell's adapter writes as an IFC file (src/py/bim_ifcos.py,
   bim_ifcos_export; docs/work-orders/v177/SPEC.md part 3). Metres; IFC's axes are X east, Y north, Z up: the app's
   x, minus its z, its y. Straight walls, floors, rectangular columns, doors and windows go as IFC's own elements;
   every other element as its triangles with its IFC class. An element that came from an IFC file keeps its GlobalId
   (bim.guid). Nothing here reads the scene: each function is given what it works on, so the unit tests can call it.
   docs/research/research-ifcopenshell-app.md. */
  /* the functions of this file by name, for the tests (window.__a3dIfcSave): each is added below its definition */
  var BIM_IFC_SAVE={};
  /* the IFC class of an element sent as triangles, by its bim.type; anything else is a proxy */
  var BIM_IFC_SAVE_CLASS={wall:'IfcWall',floor:'IfcSlab',column:'IfcColumn',beam:'IfcBeam',roof:'IfcRoof',stair:'IfcStair',
    ceiling:'IfcCovering',footing:'IfcFooting',door:'IfcDoor',window:'IfcWindow'};
  /* a point of the plan ([x, z]) as IFC's [X, Y], and a point of a mesh ([x, y, z]) as IFC's [X, Y, Z]; to the
     millimetre's tenth, so the file's numbers are short */
  function bimIfcSaveNum(v){return Math.round((+v||0)*1e4)/1e4+0;}
  function bimIfcSavePt(p){return [bimIfcSaveNum(p[0]),bimIfcSaveNum(-p[1])];}
  function bimIfcSavePt3(p){return [bimIfcSaveNum(p[0]),bimIfcSaveNum(-p[2]),bimIfcSaveNum(p[1])];}
  /* the other files' functions this file's work orders use, named here so tools/engine_modules.cjs writes their
     imports once (a work order may not add an import): a segment's left normal, a wall's two side distances, whether
     a wall has arcs, a column's four corners */
  var BIM_IFC_SAVE_USES=[bimSegNormal,bimAlignOffsets,bimHasBulge,bimRectFootprint];
  BIM_IFC_SAVE.uses=BIM_IFC_SAVE_USES;BIM_IFC_SAVE.num=bimIfcSaveNum;BIM_IFC_SAVE.pt=bimIfcSavePt;BIM_IFC_SAVE.pt3=bimIfcSavePt3;BIM_IFC_SAVE.cls=BIM_IFC_SAVE_CLASS;
export { BIM_IFC_SAVE };
