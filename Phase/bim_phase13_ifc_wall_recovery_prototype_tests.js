function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
  if(a<0)P.reverse();
  return P;
}
function bimTryRecoverWallFromRectProfile(profXZ,baseY,height){
  if(!profXZ||profXZ.length!==4)return null;
  var P=sketchCCW(profXZ.slice());
  var i,edges=[];
  for(i=0;i<4;i++){
    var a=P[i],b=P[(i+1)%4];
    var dx=b[0]-a[0],dz=b[1]-a[1];
    edges.push({a:a,b:b,len:Math.sqrt(dx*dx+dz*dz),dx:dx,dz:dz});
  }
  var e0=edges[0],e1=edges[1],e2=edges[2],e3=edges[3];
  function closeLen(x,y){return Math.abs(x-y)<Math.max(0.02,0.02*Math.max(x,y));}
  if(!closeLen(e0.len,e2.len)||!closeLen(e1.len,e3.len))return null;
  function perp(u,v){var cosA=(u.dx*v.dx+u.dz*v.dz)/((u.len*v.len)||1);return Math.abs(cosA)<0.06;}
  if(!perp(e0,e1)||!perp(e1,e2))return null;
  var longEdges,shortEdges;
  if(e0.len>=e1.len){longEdges=[e0,e2];shortEdges=[e1,e3];}
  else{longEdges=[e1,e3];shortEdges=[e0,e2];}
  var thickness=shortEdges[0].len;
  if(thickness<1e-4)return null;
  var c1=[(shortEdges[0].a[0]+shortEdges[0].b[0])/2,(shortEdges[0].a[1]+shortEdges[0].b[1])/2];
  var c2=[(shortEdges[1].a[0]+shortEdges[1].b[0])/2,(shortEdges[1].a[1]+shortEdges[1].b[1])/2];
  var runLen=Math.sqrt(Math.pow(c2[0]-c1[0],2)+Math.pow(c2[1]-c1[1],2));
  if(runLen<1e-3)return null;
  return {centerline:[c1,c2],thickness:thickness,align:'center',closed:false,baseY:baseY,height:height};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- 1. Clean axis-aligned rectangular wall profile: 5m long, 0.3m thick, along X ----
var rectA=[[0,-0.15],[5,-0.15],[5,0.15],[0,0.15]];
var recA=bimTryRecoverWallFromRectProfile(rectA,0,3);
assert('clean rectangular profile recovers successfully', recA!==null);
assert('recovered thickness matches (0.3)', approx(recA.thickness,0.3,1e-3), recA&&recA.thickness);
var runLenA=Math.sqrt(Math.pow(recA.centerline[1][0]-recA.centerline[0][0],2)+Math.pow(recA.centerline[1][1]-recA.centerline[0][1],2));
assert('recovered centerline run length matches (5)', approx(runLenA,5,1e-3), runLenA);
assert('recovered centerline sits on the profile\'s long axis (z\u22480)',
  approx(recA.centerline[0][1],0,1e-3)&&approx(recA.centerline[1][1],0,1e-3));

// ---- 2. Rotated rectangular wall profile (not axis-aligned) -- must still recover correctly ----
function rotate(p,deg){var r=deg*Math.PI/180;return [p[0]*Math.cos(r)-p[1]*Math.sin(r),p[0]*Math.sin(r)+p[1]*Math.cos(r)];}
var rectB=rectA.map(function(p){return rotate(p,37);});
var recB=bimTryRecoverWallFromRectProfile(rectB,0,3);
assert('rotated rectangular profile still recovers', recB!==null);
assert('rotated profile recovers the same thickness', approx(recB.thickness,0.3,1e-3), recB&&recB.thickness);
var runLenB=Math.sqrt(Math.pow(recB.centerline[1][0]-recB.centerline[0][0],2)+Math.pow(recB.centerline[1][1]-recB.centerline[0][1],2));
assert('rotated profile recovers the same run length', approx(runLenB,5,1e-3), runLenB);

// ---- 3. Non-rectangular profile (arbitrary polygon) must be rejected, not misinterpreted ----
var lshapeProfile=[[0,0],[3,0],[3,1],[1,1],[1,3],[0,3]];
var recC=bimTryRecoverWallFromRectProfile(lshapeProfile,0,3);
assert('a 6-point L-shaped profile is rejected (wrong point count)', recC===null);

var nearRectButNot=[[0,0],[5,0],[5,0.3],[0,0.5]]; // not a true rectangle (one corner is off)
var recD=bimTryRecoverWallFromRectProfile(nearRectButNot,0,3);
assert('a quadrilateral that is not actually rectangular is rejected', recD===null);

// ---- 4. Degenerate/zero-thickness profile is rejected ----
var zeroThick=[[0,0],[5,0],[5,0],[0,0]];
var recE=bimTryRecoverWallFromRectProfile(zeroThick,0,3);
assert('a degenerate zero-thickness profile is rejected', recE===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
