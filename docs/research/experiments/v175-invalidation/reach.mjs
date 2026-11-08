// V175 research: does a function reach saveSoon (or setA3D_REV) through its callees, by name? (data script, not a test)
// Name-based and over-approximate: a conditional call counts, so 'true' is not 'always'. Measured counter-example:
// paint() reaches by name but did not move A3D_REV when run (rev-on-paths.mjs).
//   node docs/research/experiments/v175-invalidation/reach.mjs bimLoadProjectRecord paint ...
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const ENG = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..', 'src', 'js', 'engine');
function walk(d,o){for(const f of fs.readdirSync(d)){const p=path.join(d,f);fs.statSync(p).isDirectory()?walk(p,o):f.endsWith('.js')&&o.push(p);}return o;}
const src=walk(ENG,[]).map(f=>fs.readFileSync(f,'utf8')).join('\n');
const re=/function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{/g;const B={};let m;
while((m=re.exec(src))){let i=re.lastIndex,d=1;for(;i<src.length&&d;i++){const c=src[i];if(c==='{')d++;else if(c==='}')d--;}B[m[1]]=(B[m[1]]||'')+src.slice(re.lastIndex,i);}
const reach=new Set(['saveSoon','setA3D_REV']);let ch=true;while(ch){ch=false;for(const n in B){if(reach.has(n))continue;const c=B[n].match(/\b[A-Za-z_$][\w$]*(?=\()/g)||[];if(c.some(x=>x!==n&&reach.has(x))){reach.add(n);ch=true;}}}
for(const n of process.argv.slice(2))console.log(n,reach.has(n));
