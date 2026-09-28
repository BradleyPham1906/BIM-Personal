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
function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
  if(a<0)P.reverse();
  return P;
}
function bimSegNormal(a,b){
  var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
  return [-dz/len,dx/len];
}
function bimOffsetRing(pts,dist,closed){
  var n=pts.length,out=[],i;
  for(i=0;i<n;i++){
    if(!closed&&(i===0||i===n-1)){
      var a=i===0?pts[0]:pts[n-2],b=i===0?pts[1]:pts[n-1];
      var nrm=bimSegNormal(a,b);
      out.push([pts[i][0]+nrm[0]*dist,pts[i][1]+nrm[1]*dist]);
      continue;
    }
    var prev=pts[(i-1+n)%n],cur=pts[i],next=pts[(i+1)%n];
    var n1=bimSegNormal(prev,cur),n2=bimSegNormal(cur,next);
    var mx=n1[0]+n2[0],mz=n1[1]+n2[1];
    var mlen=Math.sqrt(mx*mx+mz*mz)||1;mx/=mlen;mz/=mlen;
    var cosH=(n1[0]*mx+n1[1]*mz);
    var scale=cosH>0.15?1/cosH:1;scale=Math.min(scale,4);
    out.push([cur[0]+mx*dist*scale,cur[1]+mz*dist*scale]);
  }
  return out;
}
function bimAlignOffsets(thickness,align){
  if(align==='left')return {dLeft:0,dRight:thickness};
  if(align==='right')return {dLeft:thickness,dRight:0};
  return {dLeft:thickness/2,dRight:thickness/2};
}

// ---- NEW: mitered wall ribbon mesh builder (the thing being verified) ----
function bimBuildWallRibbonMesh(outer,inner,y0,height,closed){
  var n=outer.length;
  if(n!==inner.length||n<2)return null;
  var v=[],f=[],i;
  var segCount=closed?n:n-1;
  for(i=0;i<n;i++)v.push([outer[i][0],y0,outer[i][1]]);
  for(i=0;i<n;i++)v.push([outer[i][0],y0+height,outer[i][1]]);
  for(i=0;i<n;i++)v.push([inner[i][0],y0,inner[i][1]]);
  for(i=0;i<n;i++)v.push([inner[i][0],y0+height,inner[i][1]]);
  var OB=0,OT=n,IB=2*n,IT=3*n;
  for(i=0;i<segCount;i++){
    var j=(i+1)%n;
    f.push([OB+j,OB+i,OT+i,OT+j]);
    f.push([IB+i,IB+j,IT+j,IT+i]);
    f.push([OT+i,OT+j,IT+j,IT+i]);
    f.push([OB+j,OB+i,IB+i,IB+j]);
  }
  if(!closed){
    f.push([OB+0,IB+0,IT+0,OT+0]);
    var last=n-1;
    f.push([IB+last,OB+last,OT+last,IT+last]);
  }
  return {v:v,f:f};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- Test 1: closed square wall loop, corners should be sharp single points (no double-corner overlap) ----
var square=[[0,0],[6,0],[6,4],[0,4]];
var ccw=sketchCCW(square);
var off=bimAlignOffsets(0.3,'center');
var inner=bimOffsetRing(ccw,off.dLeft,true);
var outer=bimOffsetRing(ccw,-off.dRight,true);
assert('offset rings have same point count as centerline', inner.length===4 && outer.length===4);
// at a 90-degree corner with thickness 0.3 (offset 0.15 each side), miter point should be at distance 0.15*sqrt(2) from the corner
var cornerDist=Math.sqrt(Math.pow(inner[0][0]-ccw[0][0],2)+Math.pow(inner[0][1]-ccw[0][1],2));
assert('mitered corner point sits at the correct diagonal miter distance (0.15*sqrt2)', Math.abs(cornerDist-0.15*Math.sqrt(2))<1e-6, cornerDist);

var mesh=bimBuildWallRibbonMesh(outer,inner,0,3,true);
assert('ribbon mesh for closed wall has 4*4=16 vertices', mesh.v.length===16);
assert('ribbon mesh for closed wall has 4 segments * 4 faces = 16 quad faces', mesh.f.length===16);

// watertightness: every undirected edge must be used by exactly 2 triangle-halves once triangulated
function checkWatertight(mesh){
  var edgeCount={};
  var i,j;
  for(i=0;i<mesh.f.length;i++){
    var fc=mesh.f[i];
    for(j=0;j<fc.length;j++){
      var a=fc[j],b=fc[(j+1)%fc.length];
      var k=a<b?a+'_'+b:b+'_'+a;
      edgeCount[k]=(edgeCount[k]||0)+1;
    }
  }
  var bad=0,k2;
  for(k2 in edgeCount)if(edgeCount[k2]!==2)bad++;
  return bad;
}
assert('closed wall ribbon mesh is watertight (every edge shared by exactly 2 faces)', checkWatertight(mesh)===0, 'bad edges: '+checkWatertight(mesh));

// ---- Test 2: open L-shaped wall (3 points, 2 segments), should have end caps ----
var Lshape=[[0,0],[5,0],[5,3]];
var innerL=bimOffsetRing(Lshape,off.dLeft,false);
var outerL=bimOffsetRing(Lshape,-off.dRight,false);
var meshL=bimBuildWallRibbonMesh(outerL,innerL,0,3,false);
assert('open wall ribbon mesh vertex count is 4*n', meshL.v.length===12);
// 2 segments * 4 faces + 2 end caps = 10
assert('open wall ribbon mesh face count includes end caps', meshL.f.length===10, meshL.f.length);
assert('open wall ribbon mesh is watertight', checkWatertight(meshL)===0, 'bad edges: '+checkWatertight(meshL));

// ---- Test 3: run the closed-wall mesh through the REAL meshPolys + CSG subtract pipeline (door-opening simulation) ----
var wallObj={mesh:mesh,pos:[0,0,0]};
var wallPolys=meshPolys(wallObj);
assert('meshPolys produces a non-empty poly list for the mitered wall', wallPolys.length>0);
assert('meshPolys triangle count matches expected 2 tris per quad face (32 total)', wallPolys.length===32, wallPolys.length);

// simulate a door-opening cut: a box roughly centered on one wall segment, spanning the full thickness
var doorBox={mesh:{
  v:[[2.5,0,-0.3],[3.5,0,-0.3],[3.5,0,0.3],[2.5,0,0.3],[2.5,2.1,-0.3],[3.5,2.1,-0.3],[3.5,2.1,0.3],[2.5,2.1,0.3]],
  f:[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]
},pos:[0,0,0]};
var doorPolys=meshPolys(doorBox);
var cutResult=csgSubtract(wallPolys,doorPolys);
assert('CSG subtract of a door-shaped box from the mitered wall produces a non-empty result', cutResult.length>0, cutResult.length);
var cutMesh=polysToMesh(cutResult);
assert('resulting cut mesh has a sane vertex count (opening actually cut something)', cutMesh.v.length>mesh.v.length, 'cutMesh verts='+cutMesh.v.length+' original='+mesh.v.length);
assert('resulting cut mesh has a sane face count (not degenerate/empty)', cutMesh.f.length>=20, cutMesh.f.length);

// ---- Test 4: compare corner sharpness vs the OLD per-segment CSG-union approach (regression proof the miter fix matters) ----
function bimWallSegQuad(a,b,dLeft,dRight){
  var n=bimSegNormal(a,b);
  var lx=n[0]*dLeft,lz=n[1]*dLeft,rx=-n[0]*dRight,rz=-n[1]*dRight;
  return [[a[0]+lx,a[1]+lz],[b[0]+lx,b[1]+lz],[b[0]+rx,b[1]+rz],[a[0]+rx,a[1]+rz]];
}
// old approach's per-segment quads at a corner leave two SEPARATE corner points instead of one shared miter point
var segA=bimWallSegQuad(ccw[0],ccw[1],off.dLeft,off.dRight); // segment 0->1
var segB=bimWallSegQuad(ccw[3],ccw[0],off.dLeft,off.dRight); // segment 3->0 (the one ending at corner 0)
// segA's start-inner-corner and segB's end-inner-corner both approximate corner 0, but from DIFFERENT (non-miter) offsets
var segAInnerAtCorner0=segA[0], segBInnerAtCorner0=segB[1];
var oldGap=Math.sqrt(Math.pow(segAInnerAtCorner0[0]-segBInnerAtCorner0[0],2)+Math.pow(segAInnerAtCorner0[1]-segBInnerAtCorner0[1],2));
assert('OLD per-segment approach leaves a real gap/overlap at the corner (proves the bug existed)', oldGap>1e-6, 'oldGap='+oldGap);
assert('NEW miter approach: inner ring has exactly ONE point per corner (no gap by construction)', inner.length===4);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
