// Point-to-segment distance (used for sketch line picking)
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

// Segment from (0,0) to (10,0). Point (5,2) should be distance 2 (perpendicular to midpoint).
assert('perpendicular distance to segment midpoint', bimPointSegDist(5,2,0,0,10,0)===2);
// Point beyond the segment end (15,0) should clamp to distance from (10,0) = 5
assert('distance clamps to nearest endpoint beyond segment', bimPointSegDist(15,0,0,0,10,0)===5);
// Point exactly on the segment = 0
assert('point exactly on segment has zero distance', bimPointSegDist(5,0,0,0,10,0)===0);
// Degenerate zero-length segment (a===b) falls back to point distance, no NaN/divide-by-zero
var d=bimPointSegDist(3,4,0,0,0,0);
assert('degenerate zero-length segment does not produce NaN', !isNaN(d) && d===5, 'd='+d);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
