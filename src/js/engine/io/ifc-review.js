/* ================= __acad3dV206: That Open: the Review view and IFC import (with Hub H3's identity), the pure part ================
   docs/research/research-thatopen.md, research-notion-hub-h3-ifc.md and docs/work-orders/v206/SPEC.md. That Open's
   geometry as the app's meshes (Z-up to Y-up), IFC GlobalIds (valid, from and to hex), imports compared class by class,
   measuring and clipping. Each function is a work order, added below as it is built; none uses another file's names.
*/
function bimTorMesh(pos,idx,scale){if(pos.length%3!==0)return null;scale=scale!==undefined&&scale>0?scale:1;var v=[];for(var i=0;i<pos.length;i+=3){var x=pos[i],y=pos[i+1],z=pos[i+2];v.push([x*scale,z*scale,(0-y)*scale])}var f=[];for(var i=0;i<idx.length;i+=3)f.push([idx[i]||0,idx[i+1]||0,idx[i+2]||0]);return{v:v,f:f}}
function bimTorGuidValid(g){if(typeof g!=='string'||g.length!==22)return false;var A='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$',c=g.charAt(0);if(c<'0'||c>'3')return false;for(var i=1;i<22;i++){if(A.indexOf(g.charAt(i))===-1)return false}return true}
/* __acad3dV206 (Claude, the audit): WO-03 and WO-04 without BigInt, which is not ES5 and would stop the whole engine
   from parsing in a browser without it: the 128 bits are handled as 0s and 1s, the same characters out */
var BIM_TOR_B64='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$';
function bimTorGuidFromHex(hex){
  if(typeof hex!=='string')return null;
  var c=hex.replace(/-/g,''),bits='',i,k,n,s='';
  if(c.length!==32||!/^[0-9a-fA-F]+$/.test(c))return null;
  for(i=0;i<32;i++){n=parseInt(c.charAt(i),16);for(k=3;k>=0;k--)bits+=(n>>k)&1;}
  s=BIM_TOR_B64.charAt(parseInt(bits.slice(0,2),2));
  for(i=2;i<128;i+=6)s+=BIM_TOR_B64.charAt(parseInt(bits.slice(i,i+6),2));
  return s;
}
function bimTorGuidToHex(g){
  if(!bimTorGuidValid(g))return null;
  var bits='',i,k,n,v,out='';
  for(i=0;i<22;i++){
    v=BIM_TOR_B64.indexOf(g.charAt(i));
    for(k=(i===0?1:5);k>=0;k--)bits+=(v>>k)&1;
  }
  for(i=0;i<128;i+=4){n=parseInt(bits.slice(i,i+4),2);out+=n.toString(16);}
  return out;
}
function bimTorCompare(a,b){var C={};for(var cls in a)C[cls]=true;for(var cls in b)C[cls]=true;var S=[];for(var cls in C)S.push(cls);S.sort();var same=[],diff=[];for(var i=0;i<S.length;i++){var cls=S[i],ca=a[cls]||0,cb=b[cls]||0;if(ca===cb)same.push(cls);else diff.push({cls:cls,a:ca,b:cb})}return{same:same,diff:diff}}
function bimTorArea(pts){if(pts.length===0)return 0;var Nx=0,Ny=0,Nz=0,n=pts.length;for(var i=0;i<n;i++){var j=(i+1)%n,xi=pts[i][0],yi=pts[i][1],zi=pts[i][2],xj=pts[j][0],yj=pts[j][1],zj=pts[j][2];Nx+=yi*zj-zi*yj;Ny+=zi*xj-xi*zj;Nz+=xi*yj-yi*xj}return 0.5*Math.sqrt(Nx*Nx+Ny*Ny+Nz*Nz)}
function bimTorClip(p,plane){var dp=(p[0]-plane.p[0])*plane.n[0]+(p[1]-plane.p[1])*plane.n[1]+(p[2]-plane.p[2])*plane.n[2];return dp>1e-9}

/* ---- __acad3dV206 WO-09 (Claude): That Open's data as the import's (docs/research/experiments/thatopen/e02) ----
   That Open's values come as {value, type}; its geometry as parts already +Y up in metres, each with a 4x4 transform
   (column-major); its spatial tree alternates category nodes ({category, localId null}) and item nodes ({localId}). */
var BIM_TOE_MAX={sets:40,props:80,text:200};
/* a value of That Open's as text: {value, type} unwrapped, numbers to 6 figures, lists joined */
function bimToeVal(v){
  if(v==null)return '';
  if(Object.prototype.toString.call(v)==='[object Array]'){var a=[],i;for(i=0;i<v.length;i++)a.push(bimToeVal(v[i]));return a.join(', ');}
  if(typeof v==='object'&&v.hasOwnProperty('value'))return bimToeVal(v.value);
  if(typeof v==='number')return isFinite(v)?String(Math.abs(v)>=1e-4||v===0?+v.toPrecision(6):v):'';
  if(typeof v==='boolean')return v?'Yes':'No';
  if(typeof v==='object')return '';
  return String(v).replace(/\s+/g,' ').slice(0,BIM_TOE_MAX.text);
}
/* a value of That Open's as it is ({value, type} unwrapped), for ids: never formatted, so 1007971 stays 1007971 */
function bimToeRaw(v){return v!=null&&typeof v==='object'&&v.hasOwnProperty('value')?v.value:v;}
/* the project's length unit in metres, from the file's text (ISO 10303-21): the length unit of the unit assignment
   IfcProject names (else the first one), an SI unit with its prefix or a conversion-based foot, inch, yard or mile;
   1 when none is found */
var BIM_TOE_SI={EXA:1e18,PETA:1e15,TERA:1e12,GIGA:1e9,MEGA:1e6,KILO:1e3,HECTO:1e2,DECA:1e1,DECI:1e-1,CENTI:1e-2,MILLI:1e-3,
  MICRO:1e-6,NANO:1e-9,PICO:1e-12,FEMTO:1e-15,ATTO:1e-18};
var BIM_TOE_FT={FOOT:0.3048,FEET:0.3048,INCH:0.0254,YARD:0.9144,MILE:1609.344};
function bimToeUnit(text){
  var t=String(text||''),re=/#(\d+)\s*=\s*(IFC[A-Z0-9]+)\s*\(([^;]*)\)\s*;/gi,m,lines={},project=null,assigns=[],i,refs,u,k;
  while((m=re.exec(t))){
    var ty=m[2].toUpperCase();
    if(ty==='IFCPROJECT')project=m[3];
    else if(ty==='IFCUNITASSIGNMENT'){lines[m[1]]={ty:ty,a:m[3]};assigns.push(m[1]);}
    else if(ty==='IFCSIUNIT'||ty==='IFCCONVERSIONBASEDUNIT')lines[m[1]]={ty:ty,a:m[3]};
  }
  if(!assigns.length)return 1;
  var pick=assigns[0];
  if(project){refs=project.match(/#\d+/g)||[];for(i=0;i<refs.length;i++)if(assigns.indexOf(refs[i].slice(1))>=0){pick=refs[i].slice(1);break;}}
  refs=lines[pick].a.match(/#\d+/g)||[];
  for(i=0;i<refs.length;i++){
    u=lines[refs[i].slice(1)];
    if(!u||!/\.LENGTHUNIT\./i.test(u.a))continue;
    if(u.ty==='IFCSIUNIT'){var p=/\.LENGTHUNIT\.\s*,\s*(?:\.([A-Z]+)\.|\$)/i.exec(u.a);return p&&p[1]&&BIM_TOE_SI[p[1].toUpperCase()]||1;}
    var nm=/'([^']*)'/.exec(u.a);
    if(nm)for(k in BIM_TOE_FT)if(BIM_TOE_FT.hasOwnProperty(k)&&nm[1].toUpperCase().indexOf(k)>=0)return BIM_TOE_FT[k];
    return 1;
  }
  return 1;
}
/* That Open's spatial tree as {holder: {item: the storey (or a space outside storeys) that holds it}, storeys: [ids],
   cats: {item: its IFC class}} */
function bimToeTree(root){
  var holder={},storeys=[],cats={};
  (function walk(n,cat,hold){
    if(!n)return;
    var kids=n.children||[],i,here=hold;
    if(n.localId!=null){
      cats[n.localId]=cat||'';
      if(hold!=null&&holder[n.localId]==null)holder[n.localId]=hold;
      if(cat==='IFCBUILDINGSTOREY'){storeys.push(n.localId);here=n.localId;}
      else if(cat==='IFCSPACE'&&hold==null)here=n.localId;
      for(i=0;i<kids.length;i++)walk(kids[i],null,here);
    }else for(i=0;i<kids.length;i++)walk(kids[i],n.category||cat,hold);
  })(root,null,null);
  return {holder:holder,storeys:storeys,cats:cats};
}
/* an item's property and quantity sets (getItemsData with IsDefinedBy) as [{name, rows: [[name, value]]}] */
function bimToeSets(item){
  var out=[],defs=(item&&item.IsDefinedBy)||[],i,j,k,d,list,q,val,rows;
  for(i=0;i<defs.length&&out.length<BIM_TOE_MAX.sets;i++){
    d=defs[i];if(!d)continue;
    list=d.HasProperties||d.Quantities||[];rows=[];
    for(j=0;j<list.length&&rows.length<BIM_TOE_MAX.props;j++){
      q=list[j];if(!q||!q.Name)continue;
      val='';
      for(k in q)if(q.hasOwnProperty(k)&&/Value$/.test(k)&&q[k]!=null){val=bimToeVal(q[k]);break;}
      if(!val&&q.EnumerationValues)val=bimToeVal(q.EnumerationValues);
      if(!val&&q.ListValues)val=bimToeVal(q.ListValues);
      rows.push([bimToeVal(q.Name),val]);
    }
    if(rows.length)out.push({name:bimToeVal(d.Name)||'Properties',rows:rows});
  }
  return out;
}
/* an item's parts ([{positions, indices, transform}], transform a 16-number column-major matrix or {elements}) as one
   {pos, idx}, flat, each part moved by its transform; parts without triangles are left out */
function bimToeMesh(parts){
  var pos=[],idx=[],i,k,base,p,m,v,ix,x,y,z;
  for(i=0;i<(parts||[]).length;i++){
    p=parts[i];v=p&&p.positions;ix=p&&p.indices;
    if(!v||!ix||ix.length<3)continue;
    m=p.transform&&p.transform.elements?p.transform.elements:(p.transform||[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
    base=pos.length/3;
    for(k=0;k+2<v.length;k+=3){
      x=v[k];y=v[k+1];z=v[k+2];
      pos.push(m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]);
    }
    for(k=0;k+2<ix.length;k++)idx.push(base+ix[k]);
    for(;k<ix.length;k++)idx.push(base+ix[k]);
  }
  return {pos:pos,idx:idx};
}
/* That Open's colour ({r, g, b} from 0 to 1, linear, as three.js holds colours) as the app's #rrggbb (sRGB, as the
   file wrote it and as cc-ifc gives it): each channel through the sRGB transfer function (IEC 61966-2-1). Without it
   every colour came out darker (measured 2026-11-28: cc-ifc #939393, That Open #4a4a4a); grey for none */
function bimToeHex(c){
  if(!c||typeof c!=='object')return '#b8b8b0';
  var a=[c.r,c.g,c.b],s='#',i,h,v;
  for(i=0;i<3;i++){
    v=Math.max(0,Math.min(1,+a[i]||0));
    v=v<=0.0031308?12.92*v:1.055*Math.pow(v,1/2.4)-0.055;
    h=Math.max(0,Math.min(255,Math.round(v*255))).toString(16);s+=h.length<2?'0'+h:h;
  }
  return s;
}
/* one item's colour and opacity by cc-ifc's rule (io/ifc-full.js bimIfcMeshParts): of its parts' materials, the
   opaque one (alpha at least 0.99) covering the most triangles, else the one covering the most; opacity the triangle-
   weighted mean of alpha. parts: getItemsGeometry's [{sampleId, indices}]; sampleMat: {sampleId: materialId} (from
   getSamples); mats: {materialId: {r, g, b, a}}, 0 to 255 (getMaterials, the file's own values). null when no part
   has a known material (e03, 2026-11-28: the first-opaque rule matched cc-ifc on 69.5% of dental_clinic's elements) */
function bimToePartsLook(parts,sampleMat,mats){
  var by={},i,p,m,t,k,h,best='',bestN=-1,any='',anyN=-1,op=0,n=0;
  for(i=0;i<(parts||[]).length;i++){
    p=parts[i];if(!p||p.sampleId==null||!p.indices)continue;
    m=(mats||{})[(sampleMat||{})[p.sampleId]];if(!m)continue;
    t=Math.floor(p.indices.length/3);if(!t)continue;
    h='#';
    for(k=0;k<3;k++){var c=Math.max(0,Math.min(255,Math.round(+[m.r,m.g,m.b][k]||0))).toString(16);h+=c.length<2?'0'+c:c;}
    var a=typeof m.a==='number'&&isFinite(m.a)?Math.max(0,Math.min(1,m.a/255)):1;
    if(!by[h])by[h]={n:0,o:0};
    by[h].n+=t;if(a>=0.99)by[h].o+=t;
    op+=a*t;n+=t;
  }
  if(!n)return null;
  for(h in by)if(by.hasOwnProperty(h)){
    if(by[h].o>bestN&&by[h].o>0){best=h;bestN=by[h].o;}
    if(by[h].n>anyN){any=h;anyN=by[h].n;}
  }
  return {col:best||any,opacity:op/n};
}
/* the colour and opacity of each item, from getItemsMaterialDefinition's [{localIds, definition}]: the first opaque
   colour that covers it, and the mean of its materials' opacities */
function bimToeLook(defs){
  var out={},i,j,d,id,o;
  for(i=0;i<(defs||[]).length;i++){
    d=defs[i]&&defs[i].definition;if(!d)continue;
    var op=typeof d.opacity==='number'&&isFinite(d.opacity)?Math.max(0,Math.min(1,d.opacity)):1;
    for(j=0;j<(defs[i].localIds||[]).length;j++){
      id=defs[i].localIds[j];o=out[id]||(out[id]={col:'',sum:0,n:0,opacity:1});
      if(!o.col&&op>=0.99)o.col=bimToeHex(d.color);
      if(!o.first)o.first=bimToeHex(d.color);
      o.sum+=op;o.n++;o.opacity=o.sum/o.n;
    }
  }
  for(id in out)if(out.hasOwnProperty(id)){if(!out[id].col)out[id].col=out[id].first;delete out[id].first;delete out[id].sum;delete out[id].n;}
  return out;
}
/* the Review view's tree: [{storey: id or null, classes: {CLASS: [ids]}}], one row per storey in the file's order and
   a last one (storey null) for what no storey holds; spatial elements themselves are not listed */
var BIM_TOE_SPATIAL={IFCPROJECT:1,IFCSITE:1,IFCBUILDING:1,IFCBUILDINGSTOREY:1,IFCFACILITY:1,IFCFACILITYPART:1,IFCBRIDGE:1,
  IFCROAD:1,IFCRAILWAY:1,IFCMARINEFACILITY:1};
function bimToeStoreyClasses(root){
  var T=bimToeTree(root),rows=[],at={},id,c,r,i;
  for(i=0;i<T.storeys.length;i++){at[T.storeys[i]]=rows.length;rows.push({storey:T.storeys[i],classes:{}});}
  var rest={storey:null,classes:{}};
  for(id in T.cats){
    if(!T.cats.hasOwnProperty(id))continue;
    c=T.cats[id];if(!c||BIM_TOE_SPATIAL[c])continue;
    r=T.holder[id]!=null&&at.hasOwnProperty(T.holder[id])?rows[at[T.holder[id]]]:rest;
    (r.classes[c]||(r.classes[c]=[])).push(+id);
  }
  for(i=0;i<rows.length;i++)for(c in rows[i].classes)if(rows[i].classes.hasOwnProperty(c))rows[i].classes[c].sort(function(a,b){return a-b;});
  for(c in rest.classes)if(rest.classes.hasOwnProperty(c))rest.classes[c].sort(function(a,b){return a-b;});
  for(c in rest.classes)if(rest.classes.hasOwnProperty(c)){rows.push(rest);break;}
  return rows;
}
/* the schema's spelling of a class That Open names in capitals (IFCWALLSTANDARDCASE -> IfcWallStandardCase), from lists
   of class names (web-ifc's IFC4X3, IFC4 and IFC2X3 namespaces, newest first); a guess from the capitals if none has it */
function bimToeClassName(up,lists){
  var u=String(up||'').toUpperCase(),i,k,L;
  if(!u)return 'IfcProduct';
  for(i=0;i<(lists||[]).length;i++){L=lists[i]||[];for(k=0;k<L.length;k++)if(String(L[k]).toUpperCase()===u)return L[k];}
  return 'Ifc'+u.slice(3).charAt(0)+u.slice(4).toLowerCase();
}
export {
  bimToeClassName, bimToeLook, bimToeMesh, bimToePartsLook, bimToeRaw, bimToeSets, bimToeStoreyClasses,
  bimToeTree, bimToeUnit, bimToeVal, bimTorArea, bimTorClip, bimTorCompare, bimTorGuidValid
};
