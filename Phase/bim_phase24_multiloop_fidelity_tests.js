var A3D={objs:[],layers:[{id:'layer-0',name:'Model',visible:true,locked:false}],activeLayer:'layer-0'};
  var BIM_NODE_TOL=4;

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

  function bimPolySignedArea(poly){
    var a=0,i,n=poly.length;
    for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
    return a/2;
  }

  function bimGraphNodeKey(p){return p[0].toFixed(BIM_NODE_TOL)+','+p[1].toFixed(BIM_NODE_TOL);}

  function bimCollectWallSegments(y0){
    var segs=[],i,k;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='solid'||!o.bim||o.bim.type!=='wall'||!o.bim.centerline)continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(Math.abs(o.bim.baseY-y0)>0.5)continue;
      var cl=o.bim.centerline,n=cl.length;
      var segCount=o.bim.closed?n:n-1;
      for(k=0;k<segCount;k++)segs.push([cl[k],cl[(k+1)%n]]);
    }
    return segs;
  }

  function bimBuildWallGraph(segments){
    var nodes={},adj={};
    function addNode(p){
      var key=bimGraphNodeKey(p);
      if(!nodes[key]){nodes[key]=p;adj[key]=[];}
      return key;
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
        if(visited[startFrom+'>'+startTo])continue;
        var loop=[],curFrom=startFrom,curTo=startTo,guard=0;
        while(guard++<10000){
          visited[curFrom+'>'+curTo]=true;
          loop.push(nodes[curFrom]);
          var incomingAngle=angleOf(curTo,curFrom);
          var cand=adj[curTo],best=null,bestDelta=Infinity,ci;
          for(ci=0;ci<cand.length;ci++){
            var c=cand[ci];
            if(c===curFrom&&cand.length>1)continue;
            var outAngle=angleOf(curTo,c);
            var delta=incomingAngle-outAngle;
            while(delta<=0)delta+=Math.PI*2;
            while(delta>Math.PI*2)delta-=Math.PI*2;
            if(delta<bestDelta){bestDelta=delta;best=c;}
          }
          if(best===null)best=curFrom;
          var nextFrom=curTo,nextTo=best;
          if(nextFrom===startFrom&&nextTo===startTo)break;
          curFrom=nextFrom;curTo=nextTo;
        }
        if(loop.length>=3)faces.push(loop);
      }
    }
    return faces;
  }

  function bimFindEnclosingWallFace(pt,y0){
    var segments=bimCollectWallSegments(y0);
    if(segments.length<3)return null;
    var faces,graph;
    try{
      graph=bimBuildWallGraph(segments);
      faces=bimTraceFaces(graph);
    }catch(eF){
      console.warn('[BIM] Multi-wall boundary tracing failed: ',eF);
      return null;
    }
    var candidates=[],i;
    for(i=0;i<faces.length;i++){
      var f=faces[i];
      if(f.length<3)continue;
      var area=bimPolyArea(f);
      if(area<1e-6)continue;
      if(bimPolySignedArea(f)<0)continue;
      if(bimPointInPoly(pt,f))candidates.push({pts:f,area:area});
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return a.area-b.area;});
    return candidates[0];
  }

  function bimFindRoomBoundaryAt(pt,y0){
    var candidates=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3){
        if(Math.abs(o.bim.baseY-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.bim.innerLoop))candidates.push({pts:o.bim.innerLoop.slice(),y:o.bim.baseY,sourceType:'wall',sourceId:o.id,wallHeight:o.bim.height});
      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=3){
        if(Math.abs(o.y-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.pts))candidates.push({pts:o.pts.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});
      }
    }
    if(candidates.length){
      candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
      return candidates[0];
    }
    var face=bimFindEnclosingWallFace(pt,y0);
    if(face){
      var wh=0,j;
      for(j=0;j<A3D.objs.length;j++){
        var wo=A3D.objs[j];
        if(wo.t==='solid'&&wo.bim&&wo.bim.type==='wall'&&wo.bim.height&&Math.abs(wo.bim.baseY-y0)<=0.5){wh=wo.bim.height;break;}
      }
      return {pts:face.pts,y:y0,sourceType:'wallgroup',sourceId:null,wallHeight:wh};
    }
    return null;
  }

  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-4;}
function mkWall(id,cl,closed){return {id:id,t:'solid',name:id,bim:{type:'wall',centerline:cl,closed:!!closed,baseY:0,height:3,thickness:0.3},layer:'layer-0'};}

// four SEPARATE walls (the case that used to fail entirely)
A3D.objs=[mkWall('w1',[[0,0],[6,0]]),mkWall('w2',[[6,0],[6,4]]),mkWall('w3',[[6,4],[0,4]]),mkWall('w4',[[0,4],[0,0]])];
var r=bimFindRoomBoundaryAt([3,2],0);
assert('four separate walls detected as a room via the REAL embedded code', !!r);
assert('detected via the new wallgroup path, not the old single-object path', r&&r.sourceType==='wallgroup');
assert('area is correct (24)', r&&approx(bimPolyArea(r.pts),24), r&&bimPolyArea(r.pts));
assert('wall height is picked up for Roof placement', r&&r.wallHeight===3);
assert('click outside finds nothing', bimFindRoomBoundaryAt([50,50],0)===null);

// backward compat: a SINGLE closed wall still uses the original path
A3D.objs=[{id:'wc',t:'solid',name:'wc',bim:{type:'wall',closed:true,baseY:0,height:3,centerline:[[0,0],[6,0],[6,4],[0,4]],innerLoop:[[0.15,0.15],[5.85,0.15],[5.85,3.85],[0.15,3.85]]},layer:'layer-0'}];
var r2=bimFindRoomBoundaryAt([3,2],0);
assert('single closed wall still uses the original innerLoop path (backward compatible)', r2&&r2.sourceType==='wall');

// hidden-layer walls excluded
A3D.layers.push({id:'hid',name:'Hidden',visible:false,locked:false});
A3D.objs=[mkWall('w1',[[0,0],[6,0]]),mkWall('w2',[[6,0],[6,4]]),mkWall('w3',[[6,4],[0,4]]),mkWall('w4',[[0,4],[0,0]])];
A3D.objs.forEach(function(o){o.layer='hid';});
assert('walls on a hidden layer are excluded from multi-loop detection', bimFindRoomBoundaryAt([3,2],0)===null);
A3D.objs.forEach(function(o){o.layer='layer-0';});

// different elevation excluded
A3D.objs.forEach(function(o){o.bim.baseY=10;});
assert('walls at a different level elevation are excluded', bimFindRoomBoundaryAt([3,2],0)===null);
A3D.objs.forEach(function(o){o.bim.baseY=0;});

// two adjacent rooms
A3D.objs=[mkWall('a',[[0,0],[6,0]]),mkWall('b',[[6,0],[6,4]]),mkWall('c',[[6,4],[0,4]]),mkWall('d',[[0,4],[0,0]]),
          mkWall('e',[[6,0],[10,0]]),mkWall('f',[[10,0],[10,4]]),mkWall('g',[[10,4],[6,4]])];
var L=bimFindRoomBoundaryAt([3,2],0),R=bimFindRoomBoundaryAt([8,2],0);
assert('left of two adjacent rooms: area 24', L&&approx(bimPolyArea(L.pts),24), L&&bimPolyArea(L.pts));
assert('right of two adjacent rooms: area 16', R&&approx(bimPolyArea(R.pts),16), R&&bimPolyArea(R.pts));

// incomplete boundary
A3D.objs=[mkWall('a',[[0,0],[6,0]]),mkWall('b',[[6,0],[6,4]]),mkWall('c',[[6,4],[0,4]])];
assert('incomplete (open) wall boundary correctly finds nothing', bimFindRoomBoundaryAt([3,2],0)===null);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
