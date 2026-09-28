function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
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
  for(i=0;i<n;i++){j=(i+1)%n;f.push([j,i,i+n,j+n]);}
  return {v:v,f:f};
}
// ---- verbatim copies of the real kernel helpers, to prototype against before embedding ----
function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
function faceNormal(pts){
  var n=[0,0,0],i;
  for(i=0;i<pts.length;i++){
    var a=pts[i],b=pts[(i+1)%pts.length];
    n[0]+=(a[1]-b[1])*(a[2]+b[2]);
    n[1]+=(a[2]-b[2])*(a[0]+b[0]);
    n[2]+=(a[0]-b[0])*(a[1]+b[1]);
  }
  return vnorm(n);
}
function triOk(a,b,c){var n=faceNormal([a,b,c]);return isFinite(n[0])&&isFinite(n[1])&&isFinite(n[2])&&(Math.abs(n[0])+Math.abs(n[1])+Math.abs(n[2])>1e-9);}
function cpoly(v,shared){var p={v:v,shared:shared};return p;}
function planeOf(v){var n=faceNormal(v);return {n:n,w:vdot(n,v[0])};}
var CSG_EPS=1e-5;
function cflip(p){p.v.reverse();}
function csplit(pl,poly,cf,cb,f,b){
  var COPLANAR=0,FRONT=1,BACK=2,SPANNING=3;
  var types=[],type=0,i;
  for(i=0;i<poly.v.length;i++){var t=vdot(pl.n,poly.v[i])-pl.w;var ty=(t<-CSG_EPS)?BACK:(t>CSG_EPS?FRONT:COPLANAR);type|=ty;types.push(ty);}
  switch(type){
    case COPLANAR:(vdot(pl.n,faceNormal(poly.v))>0?cf:cb).push(poly);break;
    case FRONT:f.push(poly);break;
    case BACK:b.push(poly);break;
    case SPANNING:
      var fv=[],bv=[];
      for(i=0;i<poly.v.length;i++){
        var j=(i+1)%poly.v.length;
        var ti=types[i],tj=types[j];
        var vi=poly.v[i],vj=poly.v[j];
        if(ti!==BACK)fv.push(vi);
        if(ti!==FRONT)bv.push(vi);
        if((ti|tj)===SPANNING){
          var t=(pl.w-vdot(pl.n,vi))/vdot(pl.n,vsub(vj,vi));
          var v2=[vi[0]+(vj[0]-vi[0])*t,vi[1]+(vj[1]-vi[1])*t,vi[2]+(vj[2]-vi[2])*t];
          fv.push(v2);bv.push(v2);
        }
      }
      if(fv.length>=3)f.push(cpoly(fv,poly.shared));
      if(bv.length>=3)b.push(cpoly(bv,poly.shared));
      break;
  }
}
function CNode(polys){
  this.plane=null;this.front=null;this.back=null;this.polys=[];
  if(polys)this.build(polys);
}
CNode.prototype.invert=function(){
  var i;
  for(i=0;i<this.polys.length;i++)cflip(this.polys[i]);
  if(this.plane){this.plane.n=[-this.plane.n[0],-this.plane.n[1],-this.plane.n[2]];this.plane.w=-this.plane.w;}
  if(this.front)this.front.invert();
  if(this.back)this.back.invert();
  var t=this.front;this.front=this.back;this.back=t;
};
CNode.prototype.clipPolys=function(polys){
  if(!this.plane)return polys.slice();
  var f=[],b=[],i;
  for(i=0;i<polys.length;i++)csplit(this.plane,polys[i],f,f,f,b);
  if(this.front)f=this.front.clipPolys(f);
  if(this.back)b=this.back.clipPolys(b);else b=[];
  return f.concat(b);
};
CNode.prototype.clipTo=function(bsp){this.polys=bsp.clipPolys(this.polys);if(this.front)this.front.clipTo(bsp);if(this.back)this.back.clipTo(bsp);};
CNode.prototype.all=function(){var polys=this.polys.slice();if(this.front)polys=polys.concat(this.front.all());if(this.back)polys=polys.concat(this.back.all());return polys;};
CNode.prototype.build=function(polys){
  if(!polys.length)return;
  if(!this.plane)this.plane=planeOf(polys[0].v);
  var f=[],b=[],i;
  for(i=0;i<polys.length;i++)csplit(this.plane,polys[i],this.polys,this.polys,f,b);
  if(f.length){if(!this.front)this.front=new CNode();this.front.build(f);}
  if(b.length){if(!this.back)this.back=new CNode();this.back.build(b);}
};
function csgUnion(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());return a.all();}
function csgSubtract(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());a.invert();return a.all();}
function csgIntersect(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();b.clipTo(a);b.invert();a.clipTo(b);b.clipTo(a);a.build(b.all());a.invert();return a.all();}
function meshPolys(o){
  var m=o.mesh,i,j;
  if(!m||!m.f||!m.f.length)return [];
  var tris=[];
  for(i=0;i<m.f.length;i++){
    var fc=m.f[i];
    for(j=2;j<fc.length;j++){
      var a=fc[0],b=fc[j-1],c=fc[j];
      if(a===b||b===c||a===c)continue;
      tris.push([a,b,c]);
    }
  }
  function ek(x,y){return x<y?x+'_'+y:y+'_'+x;}
  var em={};
  function addE(t,x,y){var kk=ek(x,y);if(!em[kk])em[kk]=[];em[kk].push({t:t,s:x<y?1:-1});}
  for(i=0;i<tris.length;i++){addE(i,tris[i][0],tris[i][1]);addE(i,tris[i][1],tris[i][2]);addE(i,tris[i][2],tris[i][0]);}
  var flip=[],comp=[],nc=0;
  for(i=0;i<tris.length;i++){flip.push(false);comp.push(-1);}
  var s0,e2,q;
  for(s0=0;s0<tris.length;s0++){
    if(comp[s0]!==-1)continue;
    comp[s0]=nc;
    var Q=[s0];
    while(Q.length){
      var cur=Q.pop(),T3=tris[cur];
      var te=[[T3[0],T3[1]],[T3[1],T3[2]],[T3[2],T3[0]]];
      for(e2=0;e2<3;e2++){
        var ex=te[e2][0],ey=te[e2][1];
        var cs=(ex<ey?1:-1)*(flip[cur]?-1:1);
        var lst=em[ek(ex,ey)]||[];
        for(q=0;q<lst.length;q++){
          var nb=lst[q];
          if(nb.t===cur||comp[nb.t]!==-1)continue;
          comp[nb.t]=nc;
          if(nb.s===cs)flip[nb.t]=true;
          Q.push(nb.t);
        }
      }
    }
    nc++;
  }
  var wv=[];
  for(i=0;i<m.v.length;i++)wv.push([m.v[i][0]+o.pos[0],m.v[i][1]+o.pos[1],m.v[i][2]+o.pos[2]]);
  var vol=[];
  for(i=0;i<nc;i++)vol.push(0);
  for(i=0;i<tris.length;i++){
    var t2=flip[i]?[tris[i][0],tris[i][2],tris[i][1]]:tris[i];
    vol[comp[i]]+=vdot(wv[t2[0]],vcross(wv[t2[1]],wv[t2[2]]));
  }
  var out=[];
  for(i=0;i<tris.length;i++){
    var t3=flip[i]?[tris[i][0],tris[i][2],tris[i][1]]:tris[i];
    if(vol[comp[i]]<0)t3=[t3[0],t3[2],t3[1]];
    var A=wv[t3[0]],B=wv[t3[1]],C=wv[t3[2]];
    if(!triOk(A,B,C))continue;
    out.push(cpoly([A,B,C],null));
  }
  return out;
}
function polysToMesh(polys){
  var vm={},verts=[],faces=[],fseen={},i,j;
  function vid(p){
    var k=p[0].toFixed(4)+','+p[1].toFixed(4)+','+p[2].toFixed(4);
    if(vm[k]===undefined){vm[k]=verts.length;verts.push([p[0],p[1],p[2]]);}
    return vm[k];
  }
  for(i=0;i<polys.length;i++){
    var f=[],ok=true;
    for(j=0;j<polys[i].v.length;j++){
      var id2=vid(polys[i].v[j]);
      if(f.indexOf(id2)>=0){ok=false;break;}
      f.push(id2);
    }
    if(!ok||f.length<3)continue;
    var fk=f.slice().sort(function(a,b){return a-b;}).join('_');
    if(fseen[fk])continue;
    fseen[fk]=1;
    faces.push(f);
  }
  return {v:verts,f:faces};
}
function bimBuildHalfSpaceBox(P,dir,keepSign,size){
  var perp=[-dir[1],dir[0]];
  function pt(u,v){return [P[0]+dir[0]*u+perp[0]*v,P[1]+dir[1]*u+perp[1]*v];}
  var footprint=[pt(-size,0),pt(size,0),pt(size,keepSign*size),pt(-size,keepSign*size)];
  return padMesh(sketchCCW(footprint),-size,size*2);
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- Test 1: cut a simple 10x10 box in half with a vertical section plane through the middle ----
var bigBox=padMesh(sketchCCW([[0,0],[10,0],[10,10],[0,10]]),0,4);
var bigBoxPolys=meshPolys({mesh:bigBox,pos:[0,0,0]});

// section line through x=5, running along +Z. perp = 90deg CCW rotation of dir, so keepSign=+1
// keeps the CCW side (toward -X, "left" here); keepSign=-1 keeps the CW side (toward +X, "right").
var halfBoxLeft=bimBuildHalfSpaceBox([5,0],[0,1],1,100);
var halfBoxLeftPolys=meshPolys({mesh:halfBoxLeft,pos:[0,0,0]});
var cutPolys=csgIntersect(bigBoxPolys,halfBoxLeftPolys);
var cutMesh=polysToMesh(cutPolys);

var i,minX=Infinity,maxX=-Infinity;
for(i=0;i<cutMesh.v.length;i++){if(cutMesh.v[i][0]<minX)minX=cutMesh.v[i][0];if(cutMesh.v[i][0]>maxX)maxX=cutMesh.v[i][0];}
assert('section cut of a 10x10 box at x=5 (keep left) has correct X range [0,5]',
  Math.abs(minX-0)<1e-6 && Math.abs(maxX-5)<1e-6, minX+'..'+maxX);
assert('cut result is non-empty (real geometry, not degenerate)', cutMesh.f.length>0);

// keep the RIGHT side instead
var halfBoxRight=bimBuildHalfSpaceBox([5,0],[0,1],-1,100);
var halfBoxRightPolys=meshPolys({mesh:halfBoxRight,pos:[0,0,0]});
var cutPolys2=csgIntersect(meshPolys({mesh:bigBox,pos:[0,0,0]}),halfBoxRightPolys);
var cutMesh2=polysToMesh(cutPolys2);
var minX2=Infinity,maxX2=-Infinity;
for(i=0;i<cutMesh2.v.length;i++){if(cutMesh2.v[i][0]<minX2)minX2=cutMesh2.v[i][0];if(cutMesh2.v[i][0]>maxX2)maxX2=cutMesh2.v[i][0];}
assert('keeping the RIGHT side instead gives the correct opposite X range [5,10]',
  Math.abs(minX2-5)<1e-6 && Math.abs(maxX2-10)<1e-6, minX2+'..'+maxX2);

// ---- Test 2: an object entirely on the REMOVED side produces an empty result, not a crash ----
var smallBoxFarLeft=padMesh(sketchCCW([[-20,-20],[-15,-20],[-15,-15],[-20,-15]]),0,3);
var smallBoxPolys=meshPolys({mesh:smallBoxFarLeft,pos:[0,0,0]});
var emptyResult=csgIntersect(smallBoxPolys,halfBoxRightPolys); // box is at x=-20, keeping x>5: nothing should remain
var emptyMesh=polysToMesh(emptyResult);
assert('an object entirely outside the kept half-space produces an empty (not crashed) result', emptyMesh.f.length===0, emptyMesh.f.length);

// ---- Test 3: an object entirely INSIDE the kept side is returned essentially whole ----
var smallBoxInside=padMesh(sketchCCW([[6,4],[8,4],[8,6],[6,6]]),0,3);
var smallBoxInsidePolys=meshPolys({mesh:smallBoxInside,pos:[0,0,0]});
var wholeResult=csgIntersect(smallBoxInsidePolys,halfBoxRightPolys);
var wholeMesh=polysToMesh(wholeResult);
assert('an object entirely inside the kept half-space survives essentially intact', wholeMesh.f.length>0);
var wv=wholeMesh.v.map(function(p){return p[0];});
assert('surviving object keeps its original X extent (not clipped, since fully inside)', Math.min.apply(null,wv)>=5.99 && Math.max.apply(null,wv)<=8.01);

// ---- Test 4: cutting a mitered WALL (realistic BIM case) shows correct wall thickness at the cut ----
// (using a simple thick box as a stand-in wall cross-section: 0.3 thick, 6 long, 3 tall)
var wallStandin=padMesh(sketchCCW([[0,-0.15],[6,-0.15],[6,0.15],[0,0.15]]),0,3);
var wallPolys=meshPolys({mesh:wallStandin,pos:[0,0,0]});
var wallCutBox=bimBuildHalfSpaceBox([3,0],[0,1],1,100); // cut at the wall's midpoint, keep the left half
var wallCutBoxPolys=meshPolys({mesh:wallCutBox,pos:[0,0,0]});
var wallCutResult=csgIntersect(wallPolys,wallCutBoxPolys);
var wallCutMesh=polysToMesh(wallCutResult);
var wcMinZ=Infinity,wcMaxZ=-Infinity;
for(i=0;i<wallCutMesh.v.length;i++){if(wallCutMesh.v[i][2]<wcMinZ)wcMinZ=wallCutMesh.v[i][2];if(wallCutMesh.v[i][2]>wcMaxZ)wcMaxZ=wallCutMesh.v[i][2];}
assert('cutting a wall standin preserves its full thickness at the cut face (Z range still -0.15..0.15)',
  Math.abs(wcMinZ-(-0.15))<1e-6 && Math.abs(wcMaxZ-0.15)<1e-6, wcMinZ+'..'+wcMaxZ);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
