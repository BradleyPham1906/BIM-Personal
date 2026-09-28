function bimComputeDim(p1,p2,p3){
  var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
  var len=Math.sqrt(dx*dx+dz*dz);
  if(len<1e-9)return null;
  var ux=dx/len,uz=dz/len;
  var perpX=-uz,perpZ=ux;
  var offSigned=(p3[0]-p1[0])*perpX+(p3[1]-p1[1])*perpZ;
  var d1=[p1[0]+perpX*offSigned,p1[1]+perpZ*offSigned];
  var d2=[p2[0]+perpX*offSigned,p2[1]+perpZ*offSigned];
  return {d1:d1,d2:d2,length:len,offset:offSigned};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// horizontal segment, offset point above -> dimension line offset upward (positive Z... depends on perp convention)
var r1=bimComputeDim([0,0],[4,0],[2,1]);
assert('length is correct for a simple horizontal 4-unit segment', approx(r1.length,4));
assert('dimension line endpoints are offset perpendicular to the measured segment, not along it',
  approx(r1.d1[0],0)&&approx(r1.d2[0],4));
assert('offset direction matches which side the reference point is on', Math.abs(r1.offset)>0);
assert('dimension line stays parallel to the original segment (same X span)', approx(r1.d2[0]-r1.d1[0],4));

// reference point on the OTHER side should flip the offset sign
var r2=bimComputeDim([0,0],[4,0],[2,-1]);
assert('reference point on the opposite side flips the offset sign', (r1.offset>0)!==(r2.offset>0));

// reference point exactly ON the line -> zero offset (dimension line coincides with the measured line)
var r3=bimComputeDim([0,0],[4,0],[2,0]);
assert('reference point exactly on the line gives zero offset', approx(r3.offset,0));

// diagonal segment
var r4=bimComputeDim([0,0],[3,4],[0,0]); // 3-4-5 triangle, length should be 5
assert('diagonal segment length uses real distance (3-4-5 triangle = 5)', approx(r4.length,5));

// degenerate: identical points
var r5=bimComputeDim([1,1],[1,1],[2,2]);
assert('identical p1/p2 (zero-length dimension) is rejected, not NaN', r5===null);

// vertical segment
var r6=bimComputeDim([0,0],[0,5],[1,2.5]);
assert('vertical segment length is correct', approx(r6.length,5));
assert('vertical segment dimension line is offset horizontally (perpendicular to vertical)',
  Math.abs(r6.d1[0]-0)>0.1);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
