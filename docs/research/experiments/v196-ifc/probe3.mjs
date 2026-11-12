import fs from 'node:fs'; import path from 'node:path'; import { pathToFileURL } from 'node:url'; import { createRequire } from 'node:module';
const req = createRequire(path.join(process.cwd(), 'x.js'));
const [ccDir, file, idsArg] = process.argv.slice(2); const want=new Set(idsArg.split(',').map(Number));
const bytes = new Uint8Array(fs.readFileSync(file));
const CC = await import(pathToFileURL(path.join(ccDir, 'api.js')).href);
const Module = (await import('manifold-3d')).default; const manifold = await Module(); manifold.setup();
const WebIFC = req('web-ifc'); const wi = new WebIFC.IfcAPI(); await wi.Init();
const cc=new CC.IfcAPI(); await cc.Init({manifold});
function area(api){const mid=api.OpenModel(bytes,{});const out={};api.StreamAllMeshes(mid,(mesh)=>{if(!want.has(mesh.expressID))return;let A=0;const g=mesh.geometries;for(let i=0;i<g.size();i++){const pg=g.get(i);const geo=api.GetGeometry(mid,pg.geometryExpressID);const v=api.GetVertexArray(geo.GetVertexData(),geo.GetVertexDataSize());const ix=api.GetIndexArray(geo.GetIndexData(),geo.GetIndexDataSize());const s=Math.cbrt(Math.abs(pg.flatTransformation[0]*pg.flatTransformation[5]*pg.flatTransformation[10]))||1;
for(let k=0;k<ix.length;k+=3){const a=ix[k]*6,b=ix[k+1]*6,c=ix[k+2]*6;const u=[v[b]-v[a],v[b+1]-v[a+1],v[b+2]-v[a+2]],w=[v[c]-v[a],v[c+1]-v[a+1],v[c+2]-v[a+2]];A+=0.5*Math.hypot(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])*s*s;}if(geo.delete)geo.delete();}out[mesh.expressID]=+A.toFixed(3);});return out;}
console.log('web-ifc m2',JSON.stringify(area(wi)));console.log('cc-ifc  m2',JSON.stringify(area(cc)));
