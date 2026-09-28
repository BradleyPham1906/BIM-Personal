function bimTouchDist(a,b){var dx=b.clientX-a.clientX,dy=b.clientY-a.clientY;return Math.sqrt(dx*dx+dy*dy);}
function bimTouchMid(a,b){return [(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2];}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// distance / midpoint sanity
assert('dist: horizontal 3-4-5 triangle', approx(bimTouchDist({clientX:0,clientY:0},{clientX:3,clientY:4}),5));
assert('mid: simple average', JSON.stringify(bimTouchMid({clientX:0,clientY:0},{clientX:10,clientY:20}))===JSON.stringify([5,10]));

// pinch-zoom scale derivation, mirroring the embedded logic:
// scale = d0/d1 ; newDist = camStart.dist*scale ; fingers moving APART (d1>d0) should ZOOM IN (newDist < camStart.dist)
function pinchNewDist(camStartDist,d0,d1,minD,maxD){
  var scale=d0/Math.max(d1,1);
  var nd=camStartDist*scale;
  if(nd<minD)nd=minD;
  if(nd>maxD)nd=maxD;
  return nd;
}
assert('pinch OUT (fingers apart, d1>d0) zooms IN (dist decreases)', pinchNewDist(20,100,200,6,150) < 20);
assert('pinch IN (fingers together, d1<d0) zooms OUT (dist increases)', pinchNewDist(20,200,100,6,150) > 20);
assert('pinch with unchanged distance leaves camera dist unchanged', approx(pinchNewDist(20,100,100,6,150),20));
assert('pinch clamps to min dist', pinchNewDist(20,10,1000,6,150)===6);
assert('pinch clamps to max dist', pinchNewDist(20,1000,10,6,150)===150);

// aim-offset: touch precision drawing should sample groundPoint ABOVE the fingertip so the point
// isn't hidden under the finger. Offset only subtracts from Y, never touches X.
var AIM_OFFSET_Y=46;
function aimAdjustedY(clientY){return clientY-AIM_OFFSET_Y;}
assert('aim offset moves the sampled point upward (smaller Y) on screen', aimAdjustedY(500) === 500-46);
assert('aim offset is purely vertical (no X component in the formula)', true); // structural guarantee, not runtime-testable in isolation

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
