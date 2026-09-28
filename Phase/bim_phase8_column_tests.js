  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }

  function earClip(P){
    var idx=[],i,n=P.length,tris=[],guard=0;
    for(i=0;i<n;i++)idx.push(i);
    function cross2(o,a2,b2){return (a2[0]-o[0])*(b2[1]-o[1])-(a2[1]-o[1])*(b2[0]-o[0]);}
    function inTri(p,a2,b2,c2){
      var d1=cross2(p,a2,b2),d2=cross2(p,b2,c2),d3=cross2(p,c2,a2);
      var neg=(d1<0)||(d2<0)||(d3<0),pos=(d1>0)||(d2>0)||(d3>0);
      return !(neg&&pos);
    }
    while(idx.length>3&&guard++<3000){
      var cut=false;
      for(i=0;i<idx.length;i++){
        var i0=idx[(i+idx.length-1)%idx.length],i1=idx[i],i2=idx[(i+1)%idx.length];
        if(cross2(P[i0],P[i1],P[i2])<=1e-9)continue;
        var ok=true,k;
        for(k=0;k<idx.length;k++){
          var ix=idx[k];
          if(ix===i0||ix===i1||ix===i2)continue;
          if(inTri(P[ix],P[i0],P[i1],P[i2])){ok=false;break;}
        }
        if(!ok)continue;
        tris.push([i0,i1,i2]);
        idx.splice(i,1);
        cut=true;
        break;
      }
      if(!cut)break;
    }
    if(idx.length===3)tris.push([idx[0],idx[1],idx[2]]);
    return tris;
  }

  function padMesh(P,y0,h){
    var n=P.length,v=[],f=[],i,j;
    for(i=0;i<n;i++)v.push([P[i][0],y0,P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],y0+h,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][0],tris[i][1],tris[i][2]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][2]+n,tris[i][1]+n,tris[i][0]+n]);
    for(i=0;i<n;i++){
      j=(i+1)%n;
      f.push([j,i,i+n,j+n]);
    }
    return {v:v,f:f};
  }

  function bimBuildColumnGeometry(center,y0,w,dep,h){
    var hw=w/2,hd=dep/2;
    var quad=[[center[0]-hw,center[1]-hd],[center[0]+hw,center[1]-hd],[center[0]+hw,center[1]+hd],[center[0]-hw,center[1]+hd]];
    var mesh;
    try{mesh=padMesh(sketchCCW(quad),y0,h);}
    catch(eC){return {error:'Column build failed: '+(eC&&eC.message?eC.message:eC)};}
    if(!mesh||!mesh.f||mesh.f.length<4)return {error:'Column produced an empty solid'};
    return {mesh:mesh};
  }

  function bimPointSegDist(px,py,x1,y1,x2,y2){
    var dx=x2-x1,dy=y2-y1;
    var len2=dx*dx+dy*dy;
    var t=len2>1e-9?((px-x1)*dx+(py-y1)*dy)/len2:0;
    t=Math.max(0,Math.min(1,t));
    var cx=x1+t*dx,cy=y1+t*dy;
    var ex=px-cx,ey=py-cy;
    return Math.sqrt(ex*ex+ey*ey);
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function near(a,b){return Math.abs(a-b)<1e-9;}

var g1=bimBuildColumnGeometry([5,5],2,0.4,0.6,3);
assert('column geometry builds successfully', !g1.error, JSON.stringify(g1.error));
var xs=g1.mesh.v.map(function(v){return v[0];}),zs=g1.mesh.v.map(function(v){return v[2];}),ys=g1.mesh.v.map(function(v){return v[1];});
assert('column footprint width matches (0.4) centered at x=5', near(Math.max.apply(null,xs)-Math.min.apply(null,xs),0.4) && near((Math.max.apply(null,xs)+Math.min.apply(null,xs))/2,5));
assert('column footprint depth matches (0.6) centered at z=5', near(Math.max.apply(null,zs)-Math.min.apply(null,zs),0.6) && near((Math.max.apply(null,zs)+Math.min.apply(null,zs))/2,5));
assert('column base sits at y=2, top at y=5 (height 3)', ys.every(function(y){return near(y,2)||near(y,5);}) && Math.min.apply(null,ys)===2 && Math.max.apply(null,ys)===5);

var g2=bimBuildColumnGeometry([0,0],0,-1,0.4,3);
assert('degenerate (negative width) column still returns an object without throwing', typeof g2==='object');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
