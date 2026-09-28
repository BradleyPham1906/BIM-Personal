function segIntersect(a1,a2,b1,b2){
  // returns {pt,t,u} where t is the parameter along segment a, u along segment b
  var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
  var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
  var den=d1x*d2z-d1z*d2x;
  if(Math.abs(den)<1e-12)return null;
  var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
  var t=(dx*d2z-dz*d2x)/den;
  var u=(dx*d1z-dz*d1x)/den;
  return {pt:[a1[0]+d1x*t,a1[1]+d1z*t],t:t,u:u};
}
function ptSegDist(p,a,b){
  var dx=b[0]-a[0],dz=b[1]-a[1];
  var L2=dx*dx+dz*dz;
  var t=L2?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
  t=Math.max(0,Math.min(1,t));
  var cx=a[0]+dx*t,cz=a[1]+dz*t;
  return Math.sqrt(Math.pow(p[0]-cx,2)+Math.pow(p[1]-cz,2));
}

// Trim a wall polyline against a cutter polyline. The clicked point decides which side goes away.
function bimTrimPolyline(pts,closed,cutterPts,cutterClosed,clickPt){
  if(closed)return {error:'Trim needs an open wall (a closed loop has no free end to remove)'};
  if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
  var n=pts.length,cn=cutterPts.length;
  var cSegs=cutterClosed?cn:cn-1;
  var best=null,i,j;
  for(i=0;i<n-1;i++){
    for(j=0;j<cSegs;j++){
      var r=segIntersect(pts[i],pts[i+1],cutterPts[j],cutterPts[(j+1)%cn]);
      if(!r)continue;
      // must land inside BOTH segments -- an intersection off the end of the cutter is not a cut
      if(r.t<-1e-9||r.t>1+1e-9)continue;
      if(r.u<-1e-9||r.u>1+1e-9)continue;
      if(!best)best={seg:i,t:r.t,pt:r.pt};
    }
  }
  if(!best)return {error:'Those two walls do not cross \u2014 nothing to trim'};
  // decide which side the click is on, measured along the polyline
  var distKeepStart=0,distKeepEnd=0,k;
  var clickSeg=-1,clickT=0,bestD=Infinity;
  for(k=0;k<n-1;k++){
    var d=ptSegDist(clickPt,pts[k],pts[k+1]);
    if(d<bestD){
      bestD=d;clickSeg=k;
      var dx=pts[k+1][0]-pts[k][0],dz=pts[k+1][1]-pts[k][1];
      var L2=dx*dx+dz*dz;
      clickT=L2?((clickPt[0]-pts[k][0])*dx+(clickPt[1]-pts[k][1])*dz)/L2:0;
      clickT=Math.max(0,Math.min(1,clickT));
    }
  }
  var clickPos=clickSeg+clickT, cutPos=best.seg+best.t;
  var out=[];
  if(clickPos>cutPos){
    // click is past the cut -> keep the START side
    for(k=0;k<=best.seg;k++)out.push([pts[k][0],pts[k][1]]);
    out.push([best.pt[0],best.pt[1]]);
  }else{
    // keep the END side
    out.push([best.pt[0],best.pt[1]]);
    for(k=best.seg+1;k<n;k++)out.push([pts[k][0],pts[k][1]]);
  }
  // drop a duplicated point if the cut landed exactly on a vertex
  var clean=[out[0]];
  for(k=1;k<out.length;k++){
    var p=clean[clean.length-1];
    if(Math.abs(p[0]-out[k][0])>1e-6||Math.abs(p[1]-out[k][1])>1e-6)clean.push(out[k]);
  }
  if(clean.length<2)return {error:'Trim would remove the whole wall'};
  return {pts:clean,cutAt:best.pt};
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}

// ---- horizontal wall crossed by a vertical cutter at x=6 ----
var wall=[[0,0],[10,0]];
var cutter=[[6,-5],[6,5]];

var rKeepStart=bimTrimPolyline(wall,false,cutter,false,[9,0]); // click on the far side
assert('trim succeeds when the walls genuinely cross', !rKeepStart.error, JSON.stringify(rKeepStart.error));
assert('clicking past the cut keeps the START side', approx(rKeepStart.pts[0][0],0)&&approx(rKeepStart.pts[1][0],6), JSON.stringify(rKeepStart.pts));
assert('cut point is reported at the true intersection', approx(rKeepStart.cutAt[0],6)&&approx(rKeepStart.cutAt[1],0));

var rKeepEnd=bimTrimPolyline(wall,false,cutter,false,[1,0]); // click on the near side
assert('clicking before the cut keeps the END side', approx(rKeepEnd.pts[0][0],6)&&approx(rKeepEnd.pts[1][0],10), JSON.stringify(rKeepEnd.pts));

// ---- non-crossing walls are refused, not silently mangled ----
var farCutter=[[50,-5],[50,5]];
assert('walls that do not cross are refused with a clear message', !!bimTrimPolyline(wall,false,farCutter,false,[5,0]).error);

// ---- cutter that stops short (intersection beyond the cutter's own extent) is NOT a cut ----
var shortCutter=[[6,2],[6,5]];  // vertical but sitting above the wall, never actually touching
assert('a cutter whose span does not reach the wall is refused', !!bimTrimPolyline(wall,false,shortCutter,false,[9,0]).error);

// ---- multi-segment L wall trimmed on its second leg ----
var Lwall=[[0,0],[10,0],[10,10]];
var cutL=[[5,5],[15,5]];   // horizontal cutter crossing the vertical leg at (10,5)
var rL=bimTrimPolyline(Lwall,false,cutL,false,[10,9]);
assert('L-shaped wall trims on the correct segment', !rL.error, JSON.stringify(rL.error));
assert('L trim keeps the start side up to the intersection (0,0)-(10,0)-(10,5)',
  rL.pts.length===3&&approx(rL.pts[2][0],10)&&approx(rL.pts[2][1],5), JSON.stringify(rL.pts));

var rL2=bimTrimPolyline(Lwall,false,cutL,false,[1,0]);
assert('clicking the other side of an L keeps the end portion', approx(rL2.pts[0][0],10)&&approx(rL2.pts[0][1],5), JSON.stringify(rL2.pts));

// ---- closed loops rejected ----
assert('a closed wall loop is refused (no free end to trim)', !!bimTrimPolyline([[0,0],[4,0],[4,4],[0,4]],true,cutter,false,[2,0]).error);

// ---- degenerate ----
assert('a wall with fewer than 2 points is refused', !!bimTrimPolyline([[0,0]],false,cutter,false,[0,0]).error);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
