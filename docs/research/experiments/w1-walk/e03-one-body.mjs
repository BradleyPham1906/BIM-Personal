// W1 walkthrough research, experiment e03 (2026-11-14, during C-04): the obstacle in its own Jolt body, or in one mesh
// with the ground. Data, never a suite. Run from the repository: node docs/research/experiments/w1-walk/e03-one-body.mjs
// It drives src/js/engine/walk/walk-physics.js's first version through bimWalkPhysMesh, which then made one body per
// element; the result is why the adapter now makes one body of every element (e03-results.txt).
// The committed runtime (runtime/jolt/1.1.1) runs in a context without `process`, the path a browser page takes.
// The walker: capsule half 0.645, radius 0.23, step 0.206 m, slope 35 deg; 1.4 m/s along +x for 6 s.
// Its "two" rows need the first version (one body per element), kept beside it: pass e03-walk-physics-v1.js as the argument.
import fs from 'node:fs'; import vm from 'node:vm';
const ctx = vm.createContext({ WebAssembly, console, setTimeout, clearTimeout, TextDecoder, TextEncoder, Uint8Array, atob, performance });
vm.runInContext(fs.readFileSync('runtime/jolt/1.1.1/bim-jolt.min.js', 'utf8') + '\n;this.BIMJOLT=BIMJOLT;', ctx);
const J = await ctx.BIMJOLT.default();
const P = new Function(fs.readFileSync(process.argv[2] || 'src/js/engine/walk/walk-physics.js', 'utf8') + '\nreturn {bimWalkPhys,bimWalkPhysMesh,bimWalkPhysChar,bimWalkPhysStep,bimWalkPhysFree};')();
function box(out, x0, y0, z0, x1, y1, z1) { const v = [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
  for (const f of [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]]) for (const k of f) out.push(...v[k]); }
const g=[-5,0,-3,-5,0,3,30,0,3,-5,0,-3,30,0,3,30,0,-3];
const ramp=(gr)=>[3,0,-3,3,0,3,15,12*gr,3,3,0,-3,15,12*gr,3,15,12*gr,-3];
const obs = { 'step 0.18':(c)=>box(c,3,0,-3,30,0.18,3), 'curb 0.30':(c)=>box(c,3,0,-3,30,0.30,3), 'curb 0.40':(c)=>box(c,3,0,-3,30,0.40,3), 'block 1m deep 0.4':(c)=>box(c,3,0,-3,4,0.4,3),
  'ramp 1:12':(c)=>c.push(...ramp(1/12)), 'slope 40':(c)=>c.push(...ramp(Math.tan(40*Math.PI/180))), 'wall 3m':(c)=>box(c,3,0,-3,3.2,3,3),
  'stair 7 risers':(c)=>{for(let i=0;i<7;i++) box(c,3+i*0.28,0,-3,30,0.178*(i+1),3);} };
for (const [name, mk] of Object.entries(obs)) for (const mode of ['one','two']) {
  const W = P.bimWalkPhys(J); const c=[]; mk(c);
  if (mode==='one') P.bimWalkPhysMesh(W,'all',1,new Float32Array([...g,...c])); else { P.bimWalkPhysMesh(W,'g',1,new Float32Array(g)); P.bimWalkPhysMesh(W,'c',1,new Float32Array(c)); }
  P.bimWalkPhysChar(W,{half:0.645,r:0.23,step:0.206,slope:35*Math.PI/180},[0,0.02,0]);
  let r; for (let i=0;i<360;i++) r=P.bimWalkPhysStep(W,[1.4,0,0],1/60,'walk',false);
  console.log(name.padEnd(20), mode, r.p[0].toFixed(2), r.p[1].toFixed(2)); P.bimWalkPhysFree(W);
}
