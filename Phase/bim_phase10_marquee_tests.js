function bimRectContains(rx1,ry1,rx2,ry2,px,py){
  var minx=Math.min(rx1,rx2),maxx=Math.max(rx1,rx2),miny=Math.min(ry1,ry2),maxy=Math.max(ry1,ry2);
  return px>=minx&&px<=maxx&&py>=miny&&py<=maxy;
}
function bimMarqueeTest(pts,rx1,ry1,rx2,ry2,crossing){
  if(!pts.length)return false;
  var i,allIn=true,anyIn=false;
  for(i=0;i<pts.length;i++){
    var c=bimRectContains(rx1,ry1,rx2,ry2,pts[i][0],pts[i][1]);
    if(c)anyIn=true;else allIn=false;
  }
  return crossing?anyIn:allIn;
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

var ptsA=[[10,10],[20,10],[20,20],[10,20]];
var ptsB=[[90,10],[110,10],[110,20],[90,20]];
var ptsC=[[200,200],[210,200],[210,210],[200,210]];

assert('window mode: fully-enclosed object A matches', bimMarqueeTest(ptsA,0,0,100,100,false)===true);
assert('window mode: straddling object B does NOT match (not fully enclosed)', bimMarqueeTest(ptsB,0,0,100,100,false)===false);
assert('window mode: fully-outside object C does not match', bimMarqueeTest(ptsC,0,0,100,100,false)===false);

assert('crossing mode: fully-enclosed object A matches', bimMarqueeTest(ptsA,100,0,0,100,true)===true);
assert('crossing mode: straddling object B DOES match (touches)', bimMarqueeTest(ptsB,100,0,0,100,true)===true);
assert('crossing mode: fully-outside object C does not match', bimMarqueeTest(ptsC,100,0,0,100,true)===false);

function isCrossing(x1,x2){return x1>x2;}
assert('drag left-to-right (x1<x2) is window mode', isCrossing(10,90)===false);
assert('drag right-to-left (x1>x2) is crossing mode', isCrossing(90,10)===true);

assert('object with zero points never matches', bimMarqueeTest([],0,0,100,100,false)===false && bimMarqueeTest([],0,0,100,100,true)===false);
assert('degenerate zero-area rect still contains an exactly-coincident point', bimRectContains(50,50,50,50,50,50)===true);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
