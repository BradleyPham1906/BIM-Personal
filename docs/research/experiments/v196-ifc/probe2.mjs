import fs from 'node:fs'; import path from 'node:path'; import { pathToFileURL } from 'node:url'; import { createRequire } from 'node:module';
const req = createRequire(path.join(process.cwd(), 'x.js'));
const [ccDir, file, mode] = process.argv.slice(2);
const bytes = new Uint8Array(fs.readFileSync(file));
const CC = await import(pathToFileURL(path.join(ccDir, 'api.js')).href);
const Module = (await import('manifold-3d')).default; const manifold = await Module(); manifold.setup();
const WebIFC = req('web-ifc'); const wi = new WebIFC.IfcAPI(); await wi.Init();
const cc=new CC.IfcAPI(); await cc.Init({manifold});
function per(api){ const mid=api.OpenModel(bytes,{}); const m=new Map(); api.StreamAllMeshes(mid,(mesh)=>{let t=0;const g=mesh.geometries;for(let i=0;i<g.size();i++){const geo=api.GetGeometry(mid,g.get(i).geometryExpressID);t+=geo.GetIndexDataSize()/3;if(geo.delete)geo.delete();} m.set(mesh.expressID,t);}); return {mid,m}; }
const A=per(wi),B=per(cc);
const nm=(id)=>cc.GetNameFromTypeCode(cc.GetLineType(B.mid,id));
// the Body items of an element, by type, walking mapped items
function items(id){const out={};const L=cc.GetLine(B.mid,id);const rep=L.Representation&&cc.GetLine(B.mid,L.Representation.value);if(!rep)return out;
 const walk=(r,d)=>{const it=cc.GetLine(B.mid,r);const t=nm(r);if(t.toUpperCase()==='IFCMAPPEDITEM'){const src=cc.GetLine(B.mid,it.MappingSource.value);const sr=cc.GetLine(B.mid,src.MappedRepresentation.value);for(const x of sr.Items)walk(x.value,d+1);}else out[t]=(out[t]||0)+1;};
 for(const r of rep.Representations){const sr=cc.GetLine(B.mid,r.value);for(const x of sr.Items)walk(x.value,0);}return out;}
if(mode==='ratio'){const rows=[...B.m].filter(([k])=>A.m.has(k)).map(([k,v])=>[k,A.m.get(k),v]).sort((a,b)=>b[2]-a[2]).slice(0,6);
 for(const [k,a,b] of rows)console.log(k,nm(k),'wi',a,'cc',b,JSON.stringify(items(k)));}
else { const ids=(mode||'').split(',').map(Number).filter(Boolean); const lower=[...A.m].filter(([k,a])=>B.m.has(k)&&a<B.m.get(k)*0.9).length; const higher=[...A.m].filter(([k,a])=>B.m.has(k)&&a>B.m.get(k)*1.1);
 console.log('elements where web-ifc has <90% of cc tris:',lower,' >110%:',higher.length, higher.slice(0,6).map(([k,a])=>k+' '+nm(k)+' wi'+a+' cc'+B.m.get(k)).join('; '));}
