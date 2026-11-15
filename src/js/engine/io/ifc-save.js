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
function bimIfcSaveBase(o, layerName){
  var b=o.bim||{},r={id:o.id,name:String(o.name||o.id),psets:[]},sets=b.psets||[],i,j,ps,props,row,hasProps;
  if(typeof b.guid==='string'&&b.guid.length===22)r.guid=b.guid;
  r.psets.push({name:'BIM_Personal',props:{Type:String(b.type||o.t||''),Layer:String(layerName||'')}});
  for(i=0;i<sets.length;i++){
    ps=sets[i];if(!ps.name||ps.name==='BIM_Personal')continue;
    props={};hasProps=false;
    for(j=0;j<(ps.rows||[]).length;j++){
      row=ps.rows[j];
      if(row&&row[0]!==undefined&&row[0]!==''){props[String(row[0])]=String(row[1]==null?'':row[1]);hasProps=true;}
    }
    if(hasProps)r.psets.push({name:String(ps.name),props:props});
  }
  return r;
}
BIM_IFC_SAVE.base = bimIfcSaveBase;

function bimIfcSaveLevels(lv){
  var list=[],at={},i,l;
  if(Array.isArray(lv))for(i=0;i<lv.length;i++){
    l=lv[i];list.push({name:String(l.name||'Level '+i),elev:bimIfcSaveNum(l.elev)});at[l.id||'lvl-'+i]=i;
  }
  return {list:list,at:at};
}
BIM_IFC_SAVE.levels = bimIfcSaveLevels;

function bimIfcSaveLevel(o, lv, y){
  var at=lv&&lv.at,id=o&&o.bim&&o.bim.levelId,best=-Infinity,index=0,i;
  if(id!==undefined&&id!==null&&at&&Object.prototype.hasOwnProperty.call(at,id))return at[id];
  if(lv&&lv.list)for(i=0;i<lv.list.length;i++){
    if(lv.list[i].elev<=y+1e-6&&lv.list[i].elev>best){best=lv.list[i].elev;index=i;}
  }
  return index;
}
BIM_IFC_SAVE.level = bimIfcSaveLevel;

function bimIfcSaveMoved(o){
  return !!(o&&o.pos&&(Math.abs(o.pos[0]||0)>1e-9||Math.abs(o.pos[1]||0)>1e-9||Math.abs(o.pos[2]||0)>1e-9));
}

function bimIfcSaveWalls(o, lv, base){
  var b=o&&o.bim,p,off,n,i,a,q,dx,dz,len,nr,s,item,k,walls=[];
  if(!b||b.type!=='wall'||!b.centerline||b.centerline.length<2||bimHasBulge(b.bulges)||bimIfcSaveMoved(o)||!(b.thickness>0)||!(b.height>0))return null;
  p=b.centerline;off=bimAlignOffsets(b.thickness,b.align);n=p.length-1+(b.closed&&p.length>2?1:0);
  for(i=0;i<n;i++){
    a=p[i%p.length];q=p[(i+1)%p.length];dx=q[0]-a[0];dz=q[1]-a[1];len=Math.sqrt(dx*dx+dz*dz);
    if(len<1e-6)continue;
    nr=bimSegNormal(a,q);s=(nr[0]*dz-nr[1]*dx)/len;var oZ=Math.min(s*off.dLeft,-s*off.dRight);item={};
    for(k in base)if(base.hasOwnProperty(k))item[k]=base[k];
    q=bimIfcSavePt(q);a=bimIfcSavePt(a);
    item.level=bimIfcSaveLevel(o,lv,b.baseY);item.x0=a[0];item.y0=a[1];item.x1=q[0];item.y1=q[1];
    item.base=bimIfcSaveNum(b.baseY);item.height=bimIfcSaveNum(b.height);
    item.thickness=bimIfcSaveNum(off.dLeft+off.dRight);item.offset=bimIfcSaveNum(oZ);
    if(walls.length){item.id=o.id+'#'+i;delete item.guid;}
    walls.push(item);
  }
  if(!walls.length)return null;
  if(walls.length>1)for(i=0;i<walls.length;i++)walls[i].name=String(base.name)+' '+(i+1);
  return walls;
}
BIM_IFC_SAVE.walls = bimIfcSaveWalls;
export { BIM_IFC_SAVE };
