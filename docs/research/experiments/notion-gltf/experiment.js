// Isolated reproduction of exporter fan indices from io/gltf.js; no app/viewer invoked.
const p=[[0,0],[3,0],[3,3],[2,3],[2,1],[1,1],[1,3],[0,3]];
const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
const tris=[];for(let j=2;j<p.length;j++)tris.push([0,j-1,j]);
let shoelace=0;for(let i=0;i<p.length;i++)shoelace+=p[i][0]*p[(i+1)%p.length][1]-p[(i+1)%p.length][0]*p[i][1];
const r={case:'concave-u-fan',polygonArea:Math.abs(shoelace)/2,fanAbsoluteArea:tris.reduce((s,t)=>s+Math.abs(cross(...t.map(i=>p[i])))/2,0),fanSignedArea:tris.reduce((s,t)=>s+cross(...t.map(i=>p[i]))/2,0),triangleCount:tris.length,triangles:tris,points:p,scope:'isolated index and area reproduction; not a browser/export integration test'};
require('fs').writeFileSync(__dirname+'/results.json',JSON.stringify(r,null,2)); console.log(JSON.stringify(r));
