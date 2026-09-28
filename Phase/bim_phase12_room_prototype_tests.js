function bimPointInPoly(pt,poly){
  var x=pt[0],z=pt[1],inside=false,i,j;
  for(i=0,j=poly.length-1;i<poly.length;j=i++){
    var xi=poly[i][0],zi=poly[i][1],xj=poly[j][0],zj=poly[j][1];
    var intersect=((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi);
    if(intersect)inside=!inside;
  }
  return inside;
}
function bimPolyArea(poly){
  var a=0,i,n=poly.length;
  for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
  return Math.abs(a)/2;
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- point-in-polygon ----
var square=[[0,0],[6,0],[6,4],[0,4]];
assert('point clearly inside a rectangle is detected', bimPointInPoly([3,2],square)===true);
assert('point clearly outside a rectangle is rejected', bimPointInPoly([10,10],square)===false);
assert('point just outside an edge is rejected', bimPointInPoly([-0.01,2],square)===false);
assert('point just inside an edge is accepted', bimPointInPoly([0.01,2],square)===true);

var lshape=[[0,0],[6,0],[6,2],[3,2],[3,4],[0,4]];
assert('point inside the "notch" cutout of an L-shape is rejected', bimPointInPoly([4.5,3],lshape)===false);
assert('point inside the main body of an L-shape is accepted', bimPointInPoly([1,1],lshape)===true);

// ---- shoelace area ----
assert('6x4 rectangle has area 24', approx(bimPolyArea(square),24));
var tri=[[0,0],[4,0],[0,3]];
assert('3-4-... right triangle has area 6', approx(bimPolyArea(tri),6));
assert('area is orientation-independent (CW vs CCW give the same magnitude)', approx(bimPolyArea(square.slice().reverse()),24));

// ---- smallest-enclosing-region selection (nested loops: closet inside a bigger room) ----
function findSmallest(pt,candidates){
  var matches=candidates.filter(function(c){return bimPointInPoly(pt,c.pts);});
  if(!matches.length)return null;
  matches.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
  return matches[0];
}
var bigRoom={name:'big',pts:[[0,0],[10,0],[10,10],[0,10]]};
var closet={name:'closet',pts:[[7,7],[9,7],[9,9],[7,9]]};
var pickInClosetOnly=findSmallest([8,8],[bigRoom,closet]);
assert('a click inside a nested smaller loop picks the SMALLER region, not the outer one', pickInClosetOnly.name==='closet');
var pickInBigOnly=findSmallest([2,2],[bigRoom,closet]);
assert('a click outside the nested loop but inside the outer one picks the outer region', pickInBigOnly.name==='big');
var pickOutsideBoth=findSmallest([50,50],[bigRoom,closet]);
assert('a click outside every candidate returns no match', pickOutsideBoth===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
