// V172c experiment: the app's own ray functions (bimRayBox, bimRayTri, bimRayBlocked, copied verbatim from
// src/js/engine/analysis/simulation.js at run time) build Ladybug's intersection matrix (cosine when seen, 0 when
// blocked; the ground as the sky reversed), checked entry by entry against geometry with exact answers.
var fs=require('fs'),SRC=process.argv[2],D=JSON.parse(fs.readFileSync(process.argv[3]));
var js=fs.readFileSync(SRC+'/src/js/engine/analysis/simulation.js','utf8');
function grab(name){var i=js.indexOf('  function '+name+'('),j=js.indexOf('\n  }\n',i);if(i<0||j<0)throw new Error(name);return js.slice(i,j+4);}
eval(grab('bimRayBox')+grab('bimRayTri')+grab('bimRayBlocked'));
function box(x0,y0,z0,x1,y1,z1){
  var P=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
  var Q=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],T=[];
  Q.forEach(function(q){T.push([P[q[0]],P[q[1]],P[q[2]]]);T.push([P[q[0]],P[q[2]],P[q[3]]]);});
  return {box:[x0,y0,z0,x1,y1,z1],tris:T};
}
function vecs(k){var v=D[k].v;return v.concat(v.map(function(a){return [-a[0],-a[1],-a[2]];}));}
function row(p,n,V,occ,off){
  var o=[p[0]+n[0]*off,p[1]+n[1]*off,p[2]+n[2]*off];
  return V.map(function(v){var c=n[0]*v[0]+n[1]*v[1]+n[2]*v[2];return c>0&&!bimRayBlocked(o,v,occ)?c:0;});
}
function check(name,k,p,n,occ,exact){
  var V=vecs(k),r=row(p,n,V,occ,0.001),bad=0,edge=0,svf=0,i,c,want;
  for(i=0;i<V.length;i++){
    c=n[0]*V[i][0]+n[1]*V[i][1]+n[2]*V[i][2];
    var e=exact(V[i]);               // true seen, false blocked, null on an edge (within 1e-6)
    if(e===null){edge++;continue;}
    want=c>0&&e?c:0;
    if(Math.abs(r[i]-want)>1e-12)bad++;
  }
  for(i=0;i<D[k].v.length;i++)svf+=r[i]*D[k].sr[i]/Math.PI;
  console.log(name,k+':',V.length,'entries,',bad,'differ from the exact answer,',edge,'on an edge; sky view factor',svf.toFixed(4));
  return svf;
}
var W=10,H=10,L=200,a=10,Hc=12;
['tregenza','reinhart'].forEach(function(k){
  // 1. open ground: nothing blocks; SVF is 1
  check('open ground   ',k,[0,0,0],[0,0,1],[],function(){return true;});
  // 2. a canyon W wide, H high, L long (along y), the point at its middle, on the ground
  var can=[box(-W/2-1,-L/2,0,-W/2,L/2,H),box(W/2,-L/2,0,W/2+1,L/2,H)];
  function inCanyon(p){return function(v){
    if(v[2]<=0)return false;                                     // the ground plane is not geometry; facing up, c<=0 anyway
    if(Math.abs(v[0])<1e-12)return Math.abs(p[1])<L/2?true:true;
    var x=v[0]>0?W/2:-W/2,t=(x-p[0])/v[0];if(t<=0)return true;
    var z=p[2]+v[2]*t,y=p[1]+v[1]*t;
    if(Math.abs(z-H)<1e-6||Math.abs(Math.abs(y)-L/2)<1e-6)return null;
    return !(z<H&&Math.abs(y)<L/2);
  };}
  var s=check('canyon floor  ',k,[0,0,0],[0,0,1],can,inCanyon([0,0,0]));
  console.log('               infinite canyon, analytic: cos(atan(2H/W)) =',Math.cos(Math.atan(2*H/W)).toFixed(4),'(this one is',L,'m long)');
  // 3. the canyon's west wall at 3 m, facing east
  check('canyon wall   ',k,[-W/2,0,3],[1,0,0],can,function(v){
    if(v[0]<=0)return false;var t=W/v[0],z=3+v[2]*t,y=v[1]*t;
    if(v[2]<0&&-3/v[2]<t)return true;                                // reaches the ground plane first: a ground direction, seen
    if(Math.abs(z-H)<1e-6||Math.abs(z)<1e-6||Math.abs(Math.abs(y)-L/2)<1e-6)return null;
    return !(z<H&&z>0&&Math.abs(y)<L/2);
  });
  // 4. a courtyard 2a square, Hc high, the point at its centre
  var ct=[box(-a-1,-a-1,0,a+1,-a,Hc),box(-a-1,a,0,a+1,a+1,Hc),box(-a-1,-a,0,-a,a,Hc),box(a,-a,0,a+1,a,Hc)];
  check('courtyard     ',k,[0,0,0],[0,0,1],ct,function(v){
    if(v[2]<=0)return false;var t=Hc/v[2],x=Math.abs(v[0]*t),y=Math.abs(v[1]*t);
    if(Math.abs(x-a)<1e-6||Math.abs(y-a)<1e-6)return null;
    return x<a&&y<a;
  });
  // the opening's view factor, closed form: a point under the corner of a parallel square, four of them, A = a/Hc
  // (the differential-area-to-parallel-rectangle factor; its source to be cited from a view factor catalogue)
  var A=a/Hc,f=(A/Math.sqrt(1+A*A)*Math.atan(A/Math.sqrt(1+A*A)))*2/(2*Math.PI)*4;
  console.log('               courtyard, closed form: 4 x F(point to rectangle) =',f.toFixed(4));
});
