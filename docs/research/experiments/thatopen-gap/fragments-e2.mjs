// e2: the app's pinned @thatopen/fragments 3.6.1 + web-ifc 0.0.79 (tools/thatopen/node_modules), run unchanged in Node:
// IfcImporter -> SingleThreadedFragmentsModel -> the calls WO-09 needs, with their return shapes.
import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const NM=process.argv[2], ifcPath=process.argv[3];
const req=createRequire(path.join(NM,'x.js'));
const FRAGS=req('@thatopen/fragments');
const wasmDir=path.join(NM,'web-ifc')+'/';
const imp=new FRAGS.IfcImporter(); imp.wasm={path:wasmDir,absolute:true};
const bytes=new Uint8Array(fs.readFileSync(ifcPath));
const t0=Date.now(); const frag=await imp.process({bytes,raw:true}); const t1=Date.now();
console.log('frag bytes',frag.length,'ms',t1-t0);
const M=new FRAGS.SingleThreadedFragmentsModel('m',frag,true); await M.ready;
const cats=await M.getCategories(); console.log('categories',JSON.stringify(cats));
const sp=await M.getSpatialStructure(); console.log('spatial',JSON.stringify(sp));
const geo=await M.getItemsIdsWithGeometry(); console.log('with geometry',JSON.stringify(geo));
console.log('coords',JSON.stringify(await M.getCoordinates()));
const st=await M.getItemsOfCategories([/IFCBUILDINGSTOREY/]); console.log('storeys',JSON.stringify(st));
const sid=Object.values(st)[0]||[]; if(sid.length){const d=await M.getItemsData(sid,{attributesDefault:true}); console.log('storey data',JSON.stringify(d).slice(0,500));}
const data=await M.getItemsData(geo,{attributesDefault:true,relations:{IsDefinedBy:{attributes:true,relations:true},DefinesOccurrence:{attributes:false,relations:false},ContainedInStructure:{attributes:true,relations:false},IsTypedBy:{attributes:true,relations:false}}});
console.log('item data',JSON.stringify(data).slice(0,1500));
const g=await M.getItemsGeometry(geo);
for(const arr of g){for(const m of arr){console.log('mesh localId',m.localId,'sampleId',m.sampleId,'pos',m.positions&&m.positions.constructor.name,m.positions&&m.positions.length,'idx',m.indices&&m.indices.constructor.name,m.indices&&m.indices.length,'nrm',m.normals&&m.normals.constructor.name,'T',JSON.stringify(Array.from(m.transform.elements).map(n=>+n.toFixed(3))));
  let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];const e=m.transform.elements,p=m.positions;
  for(let k=0;k<p.length;k+=3){const x=p[k],y=p[k+1],z=p[k+2];const q=[e[0]*x+e[4]*y+e[8]*z+e[12],e[1]*x+e[5]*y+e[9]*z+e[13],e[2]*x+e[6]*y+e[10]*z+e[14]];for(let j=0;j<3;j++){mn[j]=Math.min(mn[j],q[j]);mx[j]=Math.max(mx[j],q[j]);}}
  console.log('  world box',mn.map(n=>+n.toFixed(3)),mx.map(n=>+n.toFixed(3)));
  const s=await M.getSamples([m.sampleId]); const smp=s.get(m.sampleId); const mat=await M.getMaterials([smp.material]); console.log('  sample',JSON.stringify(smp),'material',JSON.stringify(mat.get(smp.material)));}}
console.log('guids',JSON.stringify(await M.getGuidsByLocalIds(geo)));
console.log('crs',JSON.stringify(await M.getCRS()));
console.log('meta',JSON.stringify(await M.getMetadata()).slice(0,300));
