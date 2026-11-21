/* V203 e04 (2026-11-21): why the walker climbed a 0.40 m curb in the app's browser check, and the fix.
   A floor that is a box (as the app's slabs are) beside a curb: the capsule walker (radius 0.23 m, step 0.206 m) is
   lifted by Jolt's stair step until the curb's edge is below its sphere's centre, then rides up the edge as a slope:
   it climbs any edge up to step + radius. A cylinder of the same size (convex radius 0.02 to 0.1) refuses a 0.25 m
   and a 0.40 m curb and still climbs a stair of 0.18 m risers and a 1:12 ramp, and refuses a 40 degree slope.
   Run from the repository's root:  node docs/research/experiments/w1-walk/e04-cylinder.mjs
   Its output on 2026-11-21 (x where the walker ended, top the highest the feet reached):
     base   curb0.40 top 0.401  curb0.25 top 0.251  stair top 1.261  ramp top 0.640  slope40 top 0.017
     cyl0.05 curb0.40 top 0.017 curb0.25 top 0.017  stair top 1.262  ramp top 0.654  slope40 top 0.017 */
import fs from 'node:fs'; import vm from 'node:vm'; import path from 'node:path';
const ROOT=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..','..','..','..');
const ctx=vm.createContext({console,setTimeout,clearTimeout,WebAssembly,TextDecoder,TextEncoder,performance,URL,process,Buffer,globalThis:{}});
vm.runInContext(fs.readFileSync(path.join(ROOT,'runtime/jolt/1.1.1/bim-jolt.min.js'),'utf8')+'\n;this.BIMJOLT=BIMJOLT;',ctx);
const J=await ctx.BIMJOLT.default();
let t=fs.readFileSync(path.join(ROOT,'src/js/engine/walk/walk-physics.js'),'utf8').replace(/^import \{[^}]*\} from '[^']+';\n/gm,'').replace(/\nexport \{[^}]*\};\n?$/,'\n');
const T0=t.replace('new J.CylinderShapeSettings(cap.half+cap.r,cap.r,0.05)','new J.CapsuleShapeSettings(cap.half,cap.r)');   /* base: the capsule walker as C-04 built it */let P=new Function(t+'\nreturn {bimWalkPhys,bimWalkPhysMesh,bimWalkPhysChar,bimWalkPhysStep,bimWalkPhysFree};')();
function box(out,x0,y0,z0,x1,y1,z1){const v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
 for(const f of [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])for(const k of f)out.push(...v[k]);}
const CAP={half:0.645,r:0.23,step:0.206,slope:35*Math.PI/180};
function quad(out,a,b,c,d){out.push(...a,...b,...c,...a,...c,...d);}
const FACES={bottom:[[0,2,1],[0,3,2]].concat([[4,5,6],[4,6,7]]).slice(0,0),};
function boxF(out,x0,y0,z0,x1,y1,z1,skip){const v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
 const F={zlo:[[0,2,1],[0,3,2]],zhi:[[4,5,6],[4,6,7]],bot:[[0,1,5],[0,5,4]],top:[[3,7,6],[3,6,2]],xlo:[[0,4,7],[0,7,3]],xhi:[[1,2,6],[1,6,5]]};
 for(const k in F){if(skip.includes(k))continue;for(const f of F[k])for(const q of f)out.push(...v[q]);}}
const variants={base:T0};
for (const cr of [0.02,0.05,0.1]) variants['cyl'+cr]=T0.replace('inner=new J.CapsuleShapeSettings(cap.half,cap.r)','inner=new J.CylinderShapeSettings(cap.half+cap.r,cap.r,'+cr+')');
function run(P,obs,v,sec){const W=P.bimWalkPhys(J);const g=[];boxF(g,-5,-0.3,-3,30,0,3,[]);P.bimWalkPhysMesh(W,'g',1,new Float32Array(g));P.bimWalkPhysMesh(W,'o',1,new Float32Array(obs));
 P.bimWalkPhysChar(W,CAP,[0,0.02,0]);let r,top=0;for(let i=0;i<Math.round(sec*60);i++){r=P.bimWalkPhysStep(W,v,1/60,'walk',false);top=Math.max(top,r.p[1]);}P.bimWalkPhysFree(W);return {x:r.p[0].toFixed(2),top:top.toFixed(3)};}
for (const vn in variants){
 const P=new Function(variants[vn]+'\nreturn {bimWalkPhys,bimWalkPhysMesh,bimWalkPhysChar,bimWalkPhysStep,bimWalkPhysFree};')();
 const curb=[];boxF(curb,3,0,-3,4,0.4,3,[]);const c25=[];boxF(c25,3,0,-3,4,0.25,3,[]);
 const st=[];for(let k=0;k<7;k++)boxF(st,3+k*0.28,0,-3,30,0.18*(k+1),3,[]);
 const ramp=[];quad(ramp,[3,0,-3],[3,0,3],[15,1,3],[15,1,-3]);
 const sl=[];const g=Math.tan(40*Math.PI/180);quad(sl,[3,0,-3],[3,0,3],[15,12*g,3],[15,12*g,-3]);
 console.log(vn,'curb0.40',JSON.stringify(run(P,curb,[1.34,0,0],5)),'curb0.25',JSON.stringify(run(P,c25,[1.34,0,0],5)),'stair7x0.18',JSON.stringify(run(P,st,[1.34,0,0],6)),'ramp1:12',JSON.stringify(run(P,ramp,[1.34,0,0],8)),'slope40',JSON.stringify(run(P,sl,[1.34,0,0],8)));}
