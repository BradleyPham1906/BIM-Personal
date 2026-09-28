function groundPointFlatBranch(V, sx, sy, y0, W, H, camDist){
  var f=H*1.2;
  var k=f/Math.max(camDist,0.5);
  var xc=(sx-W/2)/k,yc=(H/2-sy)/k;
  var px=V.eye[0]+V.r[0]*xc+V.u[0]*yc,pz=V.eye[2]+V.r[2]*xc+V.u[2]*yc;
  var dn=V.d[1];
  // FIX: only apply the vertical-plane correction when the camera has a meaningful vertical
  // component (near-top-down). For a near-horizontal camera (elevation view), dn is close to
  // zero and dividing by it blows up to numerically unstable coordinates -- decline instead.
  var MIN_DN=0.15; // camera must be tilted at least ~8.6 degrees from horizontal
  if(Math.abs(dn)<MIN_DN)return null;
  var py=V.eye[1]+V.r[1]*xc+V.u[1]*yc;
  var t2=(y0-py)/(-dn);
  px+=-V.d[0]*t2;pz+=-V.d[2]*t2;
  return [px,y0,pz];
}

function camVecs(yaw,pitch){
  var cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
  var d=[cp*sy,sp,cp*cy];
  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vnorm(a){var l=Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var r=vnorm(vcross([0,1,0],d));
  var u=vcross(d,r);
  return {d:d,r:r,u:u,eye:[d[0]*20,d[1]*20,d[2]*20]};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- Near-top-down camera (normal plan-mode use): should work fine, produce stable coordinates ----
var Vtop=camVecs(0, 1.52); // pitch ~87 degrees, near-vertical looking down
var pTop=groundPointFlatBranch(Vtop, 400, 300, 0, 800, 600, 20);
assert('near-top-down camera produces a valid, finite ground point', pTop!==null && isFinite(pTop[0]) && isFinite(pTup=pTop[2]));

// ---- Near-horizontal camera (elevation view): should decline gracefully, not blow up ----
var Vfront=camVecs(0, 0.02); // matches the existing "front" view preset's pitch
var pFront=groundPointFlatBranch(Vfront, 400, 300, 0, 800, 600, 20);
assert('near-horizontal (elevation-like) camera declines instead of returning numerically unstable coordinates', pFront===null);

// ---- Exactly horizontal camera (pitch=0): must also decline cleanly, not divide by zero ----
var Vhoriz=camVecs(0, 0);
var pHoriz=groundPointFlatBranch(Vhoriz, 400, 300, 0, 800, 600, 20);
assert('exactly horizontal camera (pitch=0) declines cleanly, no NaN/Infinity', pHoriz===null);

// ---- Moderate pitch (somewhere between plan and elevation): should still work if steep enough ----
var Vmid=camVecs(0, 0.6); // ~34 degrees, a fairly steep 3D perspective angle
var pMid=groundPointFlatBranch(Vmid, 400, 300, 0, 800, 600, 20);
assert('a moderately steep camera angle still produces a valid point', pMid!==null && isFinite(pMid[0]));

// ---- Regression: verify old behavior (no threshold) WOULD have produced huge/unstable values here ----
// (demonstrates the fix actually addresses a real problem, not a hypothetical one)
function oldUnsafeVersion(V,sx,sy,y0,W,H,camDist){
  var f=H*1.2,k=f/Math.max(camDist,0.5);
  var xc=(sx-W/2)/k,yc=(H/2-sy)/k;
  var px=V.eye[0]+V.r[0]*xc+V.u[0]*yc,pz=V.eye[2]+V.r[2]*xc+V.u[2]*yc;
  var dn=V.d[1];
  if(Math.abs(dn)>1e-6){
    var py=V.eye[1]+V.r[1]*xc+V.u[1]*yc;
    var t2=(y0-py)/(-dn);
    px+=-V.d[0]*t2;pz+=-V.d[2]*t2;
  }
  return [px,y0,pz];
}
var oldResultOffCenter=oldUnsafeVersion(Vfront,650,150,0,800,600,20); // off-center click, not the degenerate symmetric center case
assert('regression proof: the OLD threshold (1e-6) let this near-horizontal case through and produced a result far outside any reasonable model extent',
  Math.abs(oldResultOffCenter[0])>50 || Math.abs(oldResultOffCenter[2])>50, JSON.stringify(oldResultOffCenter));

var Vexact=camVecs(0,0);
var oldResultExact=oldUnsafeVersion(Vexact,650,150,0,800,600,20);
assert('at exactly pitch=0, the old 1e-6 threshold correctly skips the correction (dn=0 fails the check), so it was already crash-safe there -- confirms the fix is about semantic correctness for near-horizontal cameras, not crash prevention',
  isFinite(oldResultExact[0])&&isFinite(oldResultExact[2]));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
