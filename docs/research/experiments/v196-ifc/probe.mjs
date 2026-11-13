import fs from 'node:fs'; import path from 'node:path'; import { pathToFileURL } from 'node:url'; import { createRequire } from 'node:module';
const req = createRequire(path.join(process.cwd(), 'x.js'));
const [ccDir, file] = process.argv.slice(2);
const bytes = new Uint8Array(fs.readFileSync(file));
const CC = await import(pathToFileURL(path.join(ccDir, 'api.js')).href);
const Module = (await import('manifold-3d')).default; const manifold = await Module(); manifold.setup();
const WebIFC = req('web-ifc'); const wi = new WebIFC.IfcAPI(); await wi.Init();
function per(api){ const mid=api.OpenModel(bytes,{}); const m=new Map(); api.StreamAllMeshes(mid,(mesh)=>{let t=0;const g=mesh.geometries;for(let i=0;i<g.size();i++){const geo=api.GetGeometry(mid,g.get(i).geometryExpressID);t+=geo.GetIndexDataSize()/3;if(geo.delete)geo.delete();} m.set(mesh.expressID,{t,type:api.GetNameFromTypeCode(api.GetLineType(mid,mesh.expressID))});}); return {mid,m}; }
const cc=new CC.IfcAPI(); await cc.Init({manifold});
const A=per(wi),B=per(cc);
const notes=cc.notes(B.mid); console.log('notes', notes.size, JSON.stringify(Array.from(notes.entries()).slice(0,8)).slice(0,1200));
const missing=[...A.m.keys()].filter(k=>!B.m.has(k)); console.log('missing in cc', missing.length, missing.slice(0,8).map(k=>k+':'+A.m.get(k).type));
for (const k of missing.slice(0,3)) { const l = cc.GetLine(B.mid,k); console.log(k, JSON.stringify(l).slice(0,300)); }
const byType={}; for(const [k,v] of B.m){const a=A.m.get(k);if(!a)continue;const r=byType[v.type]||(byType[v.type]={n:0,wi:0,cc:0});r.n++;r.wi+=a.t;r.cc+=v.t;}
console.log(Object.entries(byType).sort((a,b)=>b[1].cc-a[1].cc).slice(0,8).map(([k,v])=>`${k} n${v.n} wi${v.wi} cc${v.cc}`).join('\n'));
