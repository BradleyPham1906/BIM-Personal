var A3D={objs:[],counts:{},seq:1,layers:[],activeLayer:'L1',activeLevel:'lvl-0',sel:null,sel2:null,selSet:[],meshes:{}};
var TYPES={};var UNDO=[];
function pushUndo(){UNDO.push(1);}
function refreshTree(){} function refreshHud(){} function paint(){} function saveSoon(){}
var TOASTS=[];function a3dToast(m){TOASTS.push(m);}
  function bimOffsetPoints(pts,dist,closed){
    if(!pts||pts.length<2)return null;
    if(Math.abs(dist)<1e-9)return null;
    return bimOffsetRing(pts,dist,!!closed);
  }

  function bimObjBounds2D(o){
    var pts=null,i;
    if(o.bim&&o.bim.type==='wall'&&o.bim.centerline)pts=o.bim.centerline;
    else if(o.bim&&o.bim.profile)pts=o.bim.profile;
    else if(o.bim&&o.bim.footprint)pts=o.bim.footprint;
    else if(o.t==='room'||o.t==='sketch')pts=o.pts;
    else if(o.bim&&o.bim.center)pts=[o.bim.center];
    else if(o.t==='text')pts=[o.pt];
    if(pts&&pts.length){
      var ox=(o.pos&&o.pos[0])||0,oz=(o.pos&&o.pos[2])||0;
      var mnx=Infinity,mxx=-Infinity,mnz=Infinity,mxz=-Infinity;
      for(i=0;i<pts.length;i++){
        var x=pts[i][0]+ox,z=pts[i][1]+oz;
        if(x<mnx)mnx=x;if(x>mxx)mxx=x;if(z<mnz)mnz=z;if(z>mxz)mxz=z;
      }
      return {minX:mnx,maxX:mxx,minZ:mnz,maxZ:mxz};
    }
    var m=meshOf(o);
    if(m&&m.v&&m.v.length){
      var ox2=(o.pos&&o.pos[0])||0,oz2=(o.pos&&o.pos[2])||0;
      var a=Infinity,b=-Infinity,c=Infinity,d=-Infinity;
      for(i=0;i<m.v.length;i++){
        var vx=m.v[i][0]+ox2,vz=m.v[i][2]+oz2;
        if(vx<a)a=vx;if(vx>b)b=vx;if(vz<c)c=vz;if(vz>d)d=vz;
      }
      return {minX:a,maxX:b,minZ:c,maxZ:d};
    }
    return null;
  }

  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      var ncl=bimOffsetPoints(o.bim.centerline,dist,o.bim.closed);
      if(!ncl)return {error:'Offset distance cannot be zero'};
      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
      if(res.error)return {error:res.error};
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      res.bim.levelId=o.bim.levelId;
      return {obj:{id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,
        col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer}};
    }
    if(o.t==='sketch'){
      var npts=bimOffsetPoints(o.pts,dist,o.closed!==false);
      if(!npts)return {error:'Offset distance cannot be zero'};
      return {obj:{id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:(o.name||'Sketch')+' offset',
        col:o.col,pos:[0,0,0],pts:npts,y:o.y,closed:o.closed,layer:o.layer}};
    }
    return {error:'Offset works on walls and sketches (selected object is a '+(o.t||'?')+')'};
  }

  function bimOffsetSelection(ids,dist){
    pushUndo();
    var made=[],fails=0,i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var r=bimOffsetObject(o,dist);
      if(r.error){fails++;continue;}
      A3D.objs.push(r.obj);made.push(r.obj.id);
    }
    if(!made.length){a3dToast('Offset failed: nothing offsettable in the selection');return;}
    A3D.selSet=made;A3D.sel=made[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Offset '+made.length+' object(s)'+(fails?' ('+fails+' skipped)':''));
  }

  function bimAlignEdgeValue(b,axis,edge){
    if(axis==='x')return edge==='min'?b.minX:(edge==='max'?b.maxX:(b.minX+b.maxX)/2);
    return edge==='min'?b.minZ:(edge==='max'?b.maxZ:(b.minZ+b.maxZ)/2);
  }

  function bimAlignSelection(ids,axis,edge){
    var ref=objById(ids[0]);
    if(!ref){a3dToast('Reference object not found');return;}
    var rb=bimObjBounds2D(ref);
    if(!rb){a3dToast('Reference object has no measurable extent');return;}
    var target=bimAlignEdgeValue(rb,axis,edge);
    pushUndo();
    var moved=0,skipped=0,i;
    for(i=1;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o||bimIsLocked(o)){skipped++;continue;}
      var b=bimObjBounds2D(o);
      if(!b){skipped++;continue;}
      var delta=target-bimAlignEdgeValue(b,axis,edge);
      if(!o.pos)o.pos=[0,0,0];
      if(axis==='x')o.pos[0]+=delta;else o.pos[2]+=delta;
      moved++;
    }
    refreshTree();paint();saveSoon();
    a3dToast('Aligned '+moved+' object(s)'+(skipped?' ('+skipped+' skipped)':''));
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

  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
  }

  function bimAlignOffsets(thickness,align){
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
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

  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function bimIsLocked(o){return !!(o&&o.locked);}

  function meshOf(o){
    if(A3D.section&&A3D.section.cutMeshes&&A3D.section.cutMeshes.hasOwnProperty(o.id))return A3D.section.cutMeshes[o.id];
    if(o.mesh)return o.mesh;
    var key=o.t+'|'+JSON.stringify(o.prm||{});
    if(!A3D.meshes[key]){
      var tp=TYPES[o.t];
      if(!tp)return null;
      A3D.meshes[key]=tp.mk(mergePrm(o.t,o.prm));
    }
    return A3D.meshes[key];
  }

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}

// offset a REAL wall through the real embedded pipeline
var wr=bimBuildWallGeometry([[0,0],[10,0]],0,3,0.3,'center',false);
var wall={id:'w1',t:'solid',name:'Wall_1',bim:wr.bim,mesh:wr.mesh,pos:[0,0,0],layer:'L1'};
A3D.objs=[wall];
var r=bimOffsetObject(wall,2);
assert('real bimOffsetObject offsets a wall without error', !r.error, JSON.stringify(r.error));
assert('offset wall is a new distinct object', r.obj&&r.obj.id!==wall.id);
assert('offset wall centerline moved perpendicular by the distance', approx(r.obj.bim.centerline[0][1],2), JSON.stringify(r.obj.bim.centerline));
assert('offset wall keeps thickness/height/align', r.obj.bim.thickness===0.3&&r.obj.bim.height===3);
assert('offset wall has real rebuilt geometry', r.obj.mesh&&r.obj.mesh.f.length>0);

var imported={id:'iw',t:'solid',bim:{type:'wall',imported:true},mesh:{v:[],f:[]},pos:[0,0,0]};
assert('offsetting an imported wall with no centerline is refused cleanly', !!bimOffsetObject(imported,1).error);
assert('offsetting a room is refused with an explanatory message', !!bimOffsetObject({id:'r',t:'room',pts:[[0,0]],pos:[0,0,0]},1).error);

// bounds
var sk={id:'s1',t:'sketch',pts:[[2,3],[8,3],[8,9],[2,9]],y:0,pos:[0,0,0],closed:true};
var b=bimObjBounds2D(sk);
assert('bounds computed from sketch points', b&&approx(b.minX,2)&&approx(b.maxX,8)&&approx(b.minZ,3)&&approx(b.maxZ,9), JSON.stringify(b));
sk.pos=[5,0,1];
var b2=bimObjBounds2D(sk);
assert('bounds include the object position offset', approx(b2.minX,7)&&approx(b2.minZ,4), JSON.stringify(b2));
sk.pos=[0,0,0];

// align via the real embedded function
var refO={id:'ref',t:'sketch',pts:[[0,0],[4,0],[4,4],[0,4]],y:0,pos:[0,0,0],closed:true};
var mv={id:'mv',t:'sketch',pts:[[0,0],[2,0],[2,2],[0,2]],y:0,pos:[10,0,7],closed:true};
A3D.objs=[refO,mv];
UNDO.length=0;
bimAlignSelection(['ref','mv'],'x','min');
assert('align pushes one undo', UNDO.length===1);
assert('aligned object min X now matches the reference min X', approx(bimObjBounds2D(mv).minX,0), JSON.stringify(bimObjBounds2D(mv)));
assert('align on X leaves Z untouched', approx(mv.pos[2],7));

bimAlignSelection(['ref','mv'],'z','center');
assert('align centre on Z matches midpoints', approx((bimObjBounds2D(mv).minZ+bimObjBounds2D(mv).maxZ)/2,2), JSON.stringify(bimObjBounds2D(mv)));

// locked objects are skipped
mv.pos=[20,0,20];mv.locked=true;
TOASTS.length=0;
bimAlignSelection(['ref','mv'],'x','min');
assert('a locked object is not moved by align', approx(mv.pos[0],20));
assert('align reports the skip', TOASTS.some(function(t){return t.indexOf('skipped')>=0;}), TOASTS.join('|'));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
