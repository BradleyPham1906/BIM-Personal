function bimPointInPoly(pt,poly){
  var x=pt[0],z=pt[1],inside=false,i,j;
  for(i=0,j=poly.length-1;i<poly.length;j=i++){
    var xi=poly[i][0],zi=poly[i][1],xj=poly[j][0],zj=poly[j][1];
    if(((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi))inside=!inside;
  }
  return inside;
}
function bimPolyArea(poly){
  var a=0,i,n=poly.length;
  for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
  return Math.abs(a)/2;
}
function bimPolySignedArea(poly){
  var a=0,i,n=poly.length;
  for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
  return a/2;
}

// ---- Planar graph face tracing ----
var NODE_TOL=4; // decimal places for node welding
function nodeKey(p){return p[0].toFixed(NODE_TOL)+','+p[1].toFixed(NODE_TOL);}

function bimBuildWallGraph(segments){
  // segments: [[ [x,z],[x,z] ], ...]
  var nodes={},adj={};
  function addNode(p){
    var k=nodeKey(p);
    if(!nodes[k]){nodes[k]=p;adj[k]=[];}
    return k;
  }
  var i;
  for(i=0;i<segments.length;i++){
    var a=addNode(segments[i][0]),b=addNode(segments[i][1]);
    if(a===b)continue;
    if(adj[a].indexOf(b)<0)adj[a].push(b);
    if(adj[b].indexOf(a)<0)adj[b].push(a);
  }
  return {nodes:nodes,adj:adj};
}

function bimTraceFaces(graph){
  // Standard planar-subdivision face tracing: walk each directed half-edge, always taking the
  // most-clockwise next edge, which enumerates every face of the arrangement exactly once.
  var nodes=graph.nodes,adj=graph.adj;
  var visited={},faces=[];
  function angleOf(fromK,toK){
    var a=nodes[fromK],b=nodes[toK];
    return Math.atan2(b[1]-a[1],b[0]-a[0]);
  }
  var k;
  for(k in adj){
    if(!adj.hasOwnProperty(k))continue;
    var neighbors=adj[k],ni;
    for(ni=0;ni<neighbors.length;ni++){
      var startFrom=k,startTo=neighbors[ni];
      var edgeId=startFrom+'>'+startTo;
      if(visited[edgeId])continue;
      var loop=[],curFrom=startFrom,curTo=startTo,guard=0;
      while(guard++<10000){
        visited[curFrom+'>'+curTo]=true;
        loop.push(nodes[curFrom]);
        // at curTo, pick the next edge: the one most clockwise from the reverse of our arrival
        var incomingAngle=angleOf(curTo,curFrom);
        var cand=adj[curTo],best=null,bestDelta=Infinity,ci;
        for(ci=0;ci<cand.length;ci++){
          var c=cand[ci];
          if(c===curFrom&&cand.length>1)continue; // avoid immediate backtrack unless dead-end
          var outAngle=angleOf(curTo,c);
          var delta=incomingAngle-outAngle;
          while(delta<=0)delta+=Math.PI*2;
          while(delta>Math.PI*2)delta-=Math.PI*2;
          if(delta<bestDelta){bestDelta=delta;best=c;}
        }
        if(best===null)best=curFrom; // dead-end: reverse
        var nextFrom=curTo,nextTo=best;
        if(nextFrom===startFrom&&nextTo===startTo)break;
        curFrom=nextFrom;curTo=nextTo;
      }
      if(loop.length>=3)faces.push(loop);
    }
  }
  return faces;
}

function bimFindEnclosingFace(pt,segments){
  if(!segments.length)return null;
  var graph=bimBuildWallGraph(segments);
  var faces=bimTraceFaces(graph);
  var candidates=[],i;
  for(i=0;i<faces.length;i++){
    var f=faces[i];
    if(f.length<3)continue;
    var area=bimPolyArea(f);
    if(area<1e-6)continue;
    // the outer boundary of the whole arrangement traces clockwise (negative signed area);
    // interior faces trace counter-clockwise. Skipping the outer face avoids matching the
    // infinite exterior region, which contains every click point.
    if(bimPolySignedArea(f)<0)continue;
    if(bimPointInPoly(pt,f))candidates.push({pts:f,area:area});
  }
  if(!candidates.length)return null;
  candidates.sort(function(a,b){return a.area-b.area;});
  return candidates[0];
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-4);}

// ---- Test 1: FOUR SEPARATE walls forming a rectangle (the exact case that used to fail) ----
var fourWalls=[
  [[0,0],[6,0]],
  [[6,0],[6,4]],
  [[6,4],[0,4]],
  [[0,4],[0,0]]
];
var f1=bimFindEnclosingFace([3,2],fourWalls);
assert('four separate wall segments forming a rectangle ARE detected as an enclosing room', !!f1);
assert('detected area matches the rectangle (6x4=24)', f1&&approx(f1.area,24), f1&&f1.area);

var f1out=bimFindEnclosingFace([50,50],fourWalls);
assert('a click far outside the rectangle finds nothing', f1out===null);

// ---- Test 2: two adjacent rooms sharing a wall -- click in each, get the correct one ----
var twoRooms=[
  [[0,0],[6,0]],
  [[6,0],[6,4]],
  [[6,4],[0,4]],
  [[0,4],[0,0]],
  [[6,0],[10,0]],
  [[10,0],[10,4]],
  [[10,4],[6,4]]
];
var left=bimFindEnclosingFace([3,2],twoRooms);
var right=bimFindEnclosingFace([8,2],twoRooms);
assert('left room detected with correct area (6x4=24)', left&&approx(left.area,24), left&&left.area);
assert('right room detected with correct area (4x4=16)', right&&approx(right.area,16), right&&right.area);
assert('the two adjacent rooms are genuinely different faces', left&&right&&!approx(left.area,right.area));

// ---- Test 3: L-shaped room from 6 separate segments ----
var lRoom=[
  [[0,0],[6,0]],
  [[6,0],[6,2]],
  [[6,2],[3,2]],
  [[3,2],[3,5]],
  [[3,5],[0,5]],
  [[0,5],[0,0]]
];
var fL=bimFindEnclosingFace([1,1],lRoom);
assert('L-shaped room from 6 separate segments is detected', !!fL);
// L-shape area: 6x2 + 3x3 = 12 + 9 = 21
assert('L-shaped room area is correct (21)', fL&&approx(fL.area,21), fL&&fL.area);
var fLnotch=bimFindEnclosingFace([4.5,3.5],lRoom);
assert('a click in the L-shape\'s notch (outside the room) correctly finds nothing', fLnotch===null);

// ---- Test 4: incomplete/open boundary (gap in the walls) correctly finds nothing ----
var openWalls=[
  [[0,0],[6,0]],
  [[6,0],[6,4]],
  [[6,4],[0,4]]
  // missing the 4th wall -- not enclosed
];
var fOpen=bimFindEnclosingFace([3,2],openWalls);
assert('an incomplete wall boundary (open on one side) correctly finds no enclosed room', fOpen===null);

// ---- Test 5: nested rooms -- a small room inside a bigger one picks the SMALLER ----
var nested=[
  [[0,0],[10,0]],[[10,0],[10,10]],[[10,10],[0,10]],[[0,10],[0,0]],
  [[2,2],[5,2]],[[5,2],[5,5]],[[5,5],[2,5]],[[2,5],[2,2]]
];
var inNested=bimFindEnclosingFace([3,3],nested);
assert('a click inside a nested inner room picks the SMALLER enclosing face (3x3=9)', inNested&&approx(inNested.area,9), inNested&&inNested.area);
var outNested=bimFindEnclosingFace([8,8],nested);
assert('a click in the outer room (outside the inner one) picks the outer region', outNested&&outNested.area>9);

// ---- Test 6: empty input handled ----
assert('no segments at all returns null, not a crash', bimFindEnclosingFace([0,0],[])===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
