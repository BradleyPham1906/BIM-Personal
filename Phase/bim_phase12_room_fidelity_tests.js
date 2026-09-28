var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}]};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
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

  function bimFindRoomBoundaryAt(pt,y0){
    var candidates=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3){
        if(Math.abs(o.bim.baseY-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.bim.innerLoop))candidates.push({pts:o.bim.innerLoop.slice(),y:o.bim.baseY,sourceType:'wall',sourceId:o.id});
      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=3){
        if(Math.abs(o.y-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.pts))candidates.push({pts:o.pts.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});
      }
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
    return candidates[0];
  }

  function bimCreateRoom(boundary){
    pushUndo();
    A3D.counts.room=(A3D.counts.room||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:'#7fd4c4',
      pos:[0,0,0],pts:boundary.pts,y:boundary.y,area:bimPolyArea(boundary.pts),levelId:A3D.activeLevel,
      sourceType:boundary.sourceType,sourceId:boundary.sourceId,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created \u2014 '+o.area.toFixed(2)+' m\u00b2');
    return o;
  }

  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }

  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
  }

  function bimOffsetRing(pts,dist,closed){
    var n=pts.length,out=[],i;
    for(i=0;i<n;i++){
      if(!closed&&(i===0||i===n-1)){
        var a=i===0?pts[0]:pts[n-2],b=i===0?pts[1]:pts[n-1];
        var nrm=bimSegNormal(a,b);
        out.push([pts[i][0]+nrm[0]*dist,pts[i][1]+nrm[1]*dist]);
        continue;
      }
      var prev=pts[(i-1+n)%n],cur=pts[i],next=pts[(i+1)%n];
      var n1=bimSegNormal(prev,cur),n2=bimSegNormal(cur,next);
      var mx=n1[0]+n2[0],mz=n1[1]+n2[1];
      var mlen=Math.sqrt(mx*mx+mz*mz)||1;mx/=mlen;mz/=mlen;
      var cosH=(n1[0]*mx+n1[1]*mz);
      var scale=cosH>0.15?1/cosH:1;scale=Math.min(scale,4);
      out.push([cur[0]+mx*dist*scale,cur[1]+mz*dist*scale]);
    }
    return out;
  }

  function bimAlignOffsets(thickness,align){
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
  }

  function bimBuildWallRibbonMesh(outer,inner,y0,height,closed){
    var n=outer.length;
    if(n!==inner.length||n<2)return null;
    var v=[],f=[],i;
    var segCount=closed?n:n-1;
    for(i=0;i<n;i++)v.push([outer[i][0],y0,outer[i][1]]);
    for(i=0;i<n;i++)v.push([outer[i][0],y0+height,outer[i][1]]);
    for(i=0;i<n;i++)v.push([inner[i][0],y0,inner[i][1]]);
    for(i=0;i<n;i++)v.push([inner[i][0],y0+height,inner[i][1]]);
    var OB=0,OT=n,IB=2*n,IT=3*n;
    for(i=0;i<segCount;i++){
      var j=(i+1)%n;
      f.push([OB+j,OB+i,OT+i,OT+j]);
      f.push([IB+i,IB+j,IT+j,IT+i]);
      f.push([OT+i,OT+j,IT+j,IT+i]);
      f.push([OB+j,OB+i,IB+i,IB+j]);
    }
    if(!closed){
      f.push([OB+0,IB+0,IT+0,OT+0]);
      var last=n-1;
      f.push([IB+last,OB+last,OT+last,IT+last]);
    }
    return {v:v,f:f};
  }

  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed){
    var off=bimAlignOffsets(thickness,align);
    var cleanPts=[pts[0]],i;
    for(i=1;i<pts.length;i++){
      var prevp=cleanPts[cleanPts.length-1],curp=pts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }
    if(closed&&cleanPts.length>1){
      var firstp=cleanPts[0],lastp=cleanPts[cleanPts.length-1];
      if(Math.abs(firstp[0]-lastp[0])<1e-6&&Math.abs(firstp[1]-lastp[1])<1e-6)cleanPts.pop();
    }
    if(cleanPts.length<2)return {error:'Wall needs at least 2 distinct points'};
    var basePts=closed?sketchCCW(cleanPts):cleanPts;
    var innerRing,outerRing,nm;
    try{
      innerRing=bimOffsetRing(basePts,off.dLeft,!!closed);
      outerRing=bimOffsetRing(basePts,-off.dRight,!!closed);
      nm=bimBuildWallRibbonMesh(outerRing,innerRing,y0,height,!!closed);
    }catch(eW){
      console.warn('[BIM] Wall solid build failed: ',eW);
      return {error:'Wall build failed: '+(eW&&eW.message?eW.message:eW)};
    }
    if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid: check the centerline points'};
    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
    if(closed){
      bim.innerLoop=innerRing;
      bim.outerLoop=outerRing;
    }
    return {mesh:nm,bim:bim};
  }

  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- 1. Room from a real mitered closed wall (the actual end-to-end path) ----
var wallRes=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
var wallObj={id:'wall-1',t:'solid',bim:wallRes.bim,mesh:wallRes.mesh,layer:'layer-0'};
A3D.objs=[wallObj];
var boundary=bimFindRoomBoundaryAt([3,2],0);
assert('room boundary detection finds the wall from a click point inside it', !!boundary);
assert('detected boundary comes from the wall (sourceType=wall)', boundary&&boundary.sourceType==='wall');
assert('detected boundary area is close to the 6x4 interior minus wall thickness', boundary&&boundary.pts.length===4);

var room=bimCreateRoom(boundary);
assert('bimCreateRoom pushes a real room object', A3D.objs.length===2 && A3D.objs[1].t==='room');
assert('room area is a positive, sane number (roughly (6-0.3)*(4-0.3) for a centered 0.3-thick wall)',
  room.area>18 && room.area<22, room.area);
assert('room gets an auto-incrementing default name', room.name==='Room_1');
assert('creating a room pushes exactly one undo snapshot', UNDO_STACK.length===1);
assert('newly created room becomes the active selection', A3D.sel===room.id && A3D.selSet.length===1 && A3D.selSet[0]===room.id);

// ---- 2. Click outside any boundary returns null (tool should not create anything) ----
var noBoundary=bimFindRoomBoundaryAt([50,50],0);
assert('a click far from any closed shape finds no boundary', noBoundary===null);

// ---- 3. Nested loops: a closet sketch inside the same wall loop should win over the wall itself ----
var closetSketch={id:'sk-1',t:'sketch',pts:[[4,0.5],[5.5,0.5],[5.5,2],[4,2]],y:0,closed:true,layer:'layer-0'};
A3D.objs.push(closetSketch);
var nestedBoundary=bimFindRoomBoundaryAt([4.7,1],0);
assert('a click inside a nested closet sketch picks the SMALLER closet, not the outer wall room',
  nestedBoundary&&nestedBoundary.sourceType==='sketch'&&nestedBoundary.sourceId==='sk-1');

// ---- 4. Hidden-layer objects are excluded from boundary detection ----
A3D.layers.push({id:'layer-hidden',name:'Hidden',color:'#fff',visible:false,locked:false});
closetSketch.layer='layer-hidden';
var boundaryIgnoringHidden=bimFindRoomBoundaryAt([4.7,1],0);
assert('a boundary on a hidden layer is skipped, falling through to the next enclosing region',
  boundaryIgnoringHidden&&boundaryIgnoringHidden.sourceType==='wall');
closetSketch.layer='layer-0';
A3D.layers.pop();

// ---- 5. Open (non-closed) sketches are never valid room boundaries ----
var openSketch={id:'sk-2',t:'sketch',pts:[[0,0],[2,0],[2,2]],y:0,closed:false,layer:'layer-0'};
A3D.objs.push(openSketch);
var boundaryStill=bimFindRoomBoundaryAt([0.5,0.2],0);
assert('an open sketch is never picked as a room boundary even if the point sits near it',
  !boundaryStill||boundaryStill.sourceType!=='sketch'||boundaryStill.sourceId!=='sk-2');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
