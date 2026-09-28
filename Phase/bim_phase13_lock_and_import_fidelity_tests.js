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
  function bimFindWallSegmentAt(wallObj,clickXZ){
    if(!wallObj||!wallObj.bim||!wallObj.bim.centerline||!wallObj.bim.centerline.length)return null;
    var cl=wallObj.bim.centerline,n=cl.length,closed=wallObj.bim.closed;
    var segCount=closed?n:n-1,i,best=null;
    for(i=0;i<segCount;i++){
      var a=cl[i],b=cl[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      var len2=dx*dx+dz*dz;
      var t=len2>1e-9?(((clickXZ[0]-a[0])*dx+(clickXZ[1]-a[1])*dz)/len2):0;
      t=Math.max(0.08,Math.min(0.92,t));
      var cx=a[0]+t*dx,cz=a[1]+t*dz;
      var ddx=clickXZ[0]-cx,ddz=clickXZ[1]-cz;
      var d=Math.sqrt(ddx*ddx+ddz*ddz);
      if(!best||d<best.d)best={a:a,b:b,t:t,center:[cx,cz],d:d};
    }
    return best;
  }

  function bimFindWallNear(xz,y0){
    var i,o,best=null,bestSeg=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='solid'||!o.bim||o.bim.type!=='wall')continue;
      if(Math.abs(o.bim.baseY-y0)>0.5)continue;
      var seg=bimFindWallSegmentAt(o,xz);
      if(seg&&seg.d<1.5&&(!bestSeg||seg.d<bestSeg.d)){bestSeg=seg;best=o;}
    }
    if(!best)return null;
    return {wall:best,seg:bestSeg};
  }

  function bimRebuildWall(o,newThickness,newHeight,newAlign){
    if(!o||!o.bim||o.bim.type!=='wall')return false;
    if(!o.bim.centerline){a3dToast('This wall has no parametric data (likely imported) \u2014 thickness/height/alignment cannot be edited');return false;}
    if(bimIsLocked(o)){a3dToast(o.name+' is locked (Pin) \u2014 unlock it first to edit');return false;}
    var b=o.bim;
    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    res.bim.levelId=b.levelId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
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

  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
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

  function bimTryRecoverWallFromRectProfile(profXZ,baseY,height){
    if(!profXZ||profXZ.length!==4)return null;
    var P=sketchCCW(profXZ.slice());
    var i,edges=[];
    for(i=0;i<4;i++){
      var a=P[i],b=P[(i+1)%4];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      edges.push({a:a,b:b,len:Math.sqrt(dx*dx+dz*dz),dx:dx,dz:dz});
    }
    var e0=edges[0],e1=edges[1],e2=edges[2],e3=edges[3];
    function closeLen(x,y){return Math.abs(x-y)<Math.max(0.02,0.02*Math.max(x,y));}
    if(!closeLen(e0.len,e2.len)||!closeLen(e1.len,e3.len))return null;
    function perp(u,v){var cosA=(u.dx*v.dx+u.dz*v.dz)/((u.len*v.len)||1);return Math.abs(cosA)<0.06;}
    if(!perp(e0,e1)||!perp(e1,e2))return null;
    var longEdges,shortEdges;
    if(e0.len>=e1.len){longEdges=[e0,e2];shortEdges=[e1,e3];}
    else{longEdges=[e1,e3];shortEdges=[e0,e2];}
    var thickness=shortEdges[0].len;
    if(thickness<1e-4)return null;
    var c1=[(shortEdges[0].a[0]+shortEdges[0].b[0])/2,(shortEdges[0].a[1]+shortEdges[0].b[1])/2];
    var c2=[(shortEdges[1].a[0]+shortEdges[1].b[0])/2,(shortEdges[1].a[1]+shortEdges[1].b[1])/2];
    var runLen=Math.sqrt(Math.pow(c2[0]-c1[0],2)+Math.pow(c2[1]-c1[1],2));
    if(runLen<1e-3)return null;
    return {centerline:[c1,c2],thickness:thickness,align:'center',closed:false,baseY:baseY,height:height};
  }

  function bimIsLocked(o){return !!(o&&o.locked);}

  function bimSetLocked(o,val){
    if(!o)return false;
    pushUndo();
    o.locked=!!val;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+(val?' locked (Pin)':' unlocked'));
    return true;
  }

  function delSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Nothing selected to delete');return false;}
    var lockedSkipped=0;
    var deletable=ids.filter(function(id){
      var oo=objById(id);
      if(oo&&bimIsLocked(oo)){lockedSkipped++;return false;}
      return true;
    });
    if(!deletable.length){a3dToast('Selected object(s) are locked (Pin) \u2014 unlock first to delete');return false;}
    pushUndo();
    var idSet={},i;
    for(i=0;i<deletable.length;i++)idSet[deletable[i]]=true;
    for(i=0;i<A3D.objs.length;i++){
      var oo=A3D.objs[i];
      if(oo.t==='opening'&&oo.bim&&idSet[oo.bim.hostWallId])idSet[oo.id]=true;
    }
    var kept=[];
    for(i=0;i<A3D.objs.length;i++){if(!idSet[A3D.objs[i].id])kept.push(A3D.objs[i]);}
    var removedCount=A3D.objs.length-kept.length;
    A3D.objs=kept;
    if(idSet[A3D.sel])A3D.sel=null;
    if(idSet[A3D.sel2])A3D.sel2=null;
    A3D.selSet=A3D.selSet.filter(function(id){return !idSet[id];});
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(removedCount+' object(s) deleted'+(lockedSkipped?' ('+lockedSkipped+' locked object(s) skipped)':''));
    return true;
  }

  function bimDuplicateObject(o,dx,dz){
    var copy;
    if(o.t==='opening')return null;
    if(o.t==='sketch'){
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
    }else if(o.bim&&o.bim.type==='wall'){
      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
      if(res.error)return null;
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      res.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return null;
      var newProf=o.bim.profile.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return null;
      A3D.counts.floor=(A3D.counts.floor||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Floor_'+A3D.counts.floor,col:o.col,pos:[0,0,0],mesh:res2.mesh,
        bim:{type:'floor',thickness:o.bim.thickness,material:o.bim.material,levelId:o.bim.levelId,baseY:o.bim.baseY,profile:newProf},layer:o.layer};
    }else if(o.bim&&o.bim.type==='column'){
      var newCenter=[o.bim.center[0]+dx,o.bim.center[1]+dz];
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height);
      if(res3.error)return null;
      A3D.counts.column=(A3D.counts.column||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Column_'+A3D.counts.column,col:o.col,pos:[0,0,0],mesh:res3.mesh,
        bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter},layer:o.layer};
    }else if(o.t==='room'){
      A3D.counts.room=(A3D.counts.room||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:o.col,pos:[0,0,0],
        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,
        sourceType:o.sourceType,sourceId:o.sourceId,layer:o.layer};
    }else{
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pos=[o.pos[0]+dx,o.pos[1],o.pos[2]+dz];
      copy.name=o.name+' copy';
    }
    return copy;
  }

  function bimBuildColumnGeometry(center,y0,w,dep,h){
    var hw=w/2,hd=dep/2;
    var quad=[[center[0]-hw,center[1]-hd],[center[0]+hw,center[1]-hd],[center[0]+hw,center[1]+hd],[center[0]-hw,center[1]+hd]];
    var mesh;
    try{mesh=padMesh(sketchCCW(quad),y0,h);}
    catch(eC){return {error:'Column build failed: '+(eC&&eC.message?eC.message:eC)};}
    if(!mesh||!mesh.f||mesh.f.length<4)return {error:'Column produced an empty solid'};
    return {mesh:mesh};
  }

  function bimBuildFloorGeometry(profPts,y,thickness){
    var m;
    try{m=padMesh(profPts,y-thickness,thickness);}
    catch(eF){console.warn('[BIM] Floor solid build failed: ',eF);return {error:'Floor build failed: '+(eF&&eF.message?eF.message:eF)};}
    if(!m||!m.f||m.f.length<4)return {error:'Floor produced an empty solid: check the source profile'};
    return {mesh:m};
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- 1. The two original crashes are now fixed ----
var importedWall={id:'ifc-1',t:'solid',bim:{type:'wall',imported:true,ifcType:'IFCWALLSTANDARDCASE',name:'Basic Wall'},mesh:{v:[],f:[]},layer:'layer-0'};
A3D.objs=[importedWall];
var r1ok=true,r1val;
try{r1val=bimFindWallSegmentAt(importedWall,[1,1]);}catch(e){r1ok=false;}
assert('bimFindWallSegmentAt no longer crashes on an imported wall without centerline', r1ok);
assert('bimFindWallSegmentAt returns null (not a fabricated hit) for a wall without centerline', r1val===null);

var r2ok=true,r2val;
try{r2val=bimRebuildWall(importedWall,0.3,3,'center');}catch(e){r2ok=false;}
assert('bimRebuildWall no longer crashes on an imported wall without centerline', r2ok);
assert('bimRebuildWall returns false (declines gracefully) for a wall without centerline', r2val===false);
assert('bimRebuildWall explains why via toast', TOASTS.some(function(t){return t.indexOf('parametric')>=0;}));

// ---- 2. Lock/Pin blocks delete ----
TOASTS.length=0;UNDO_STACK.length=0;
var lockedObj={id:'locked-1',t:'box',prm:{},pos:[0,0,0],locked:true,layer:'layer-0'};
var freeObj={id:'free-1',t:'box',prm:{},pos:[0,0,0],layer:'layer-0'};
A3D.objs=[lockedObj,freeObj];
A3D.selSet=['locked-1'];
var delRes1=delSelection();
assert('delSelection refuses to delete a locked-only selection', delRes1===false);
assert('locked object survives the delete attempt', objById('locked-1')!==null);
assert('no undo snapshot was pushed for a no-op delete', UNDO_STACK.length===0);

A3D.selSet=['locked-1','free-1'];
var delRes2=delSelection();
assert('delSelection deletes the unlocked member and skips the locked one in a mixed selection', delRes2===true);
assert('locked object still survives', objById('locked-1')!==null);
assert('unlocked object was actually deleted', objById('free-1')===null);
assert('delete summary toast mentions the skipped locked object', TOASTS.some(function(t){return t.indexOf('locked')>=0;}));

// ---- 3. bimSetLocked toggles cleanly and pushes undo ----
UNDO_STACK.length=0;
var toggleObj={id:'t1',t:'box',prm:{},pos:[0,0,0],layer:'layer-0'};
assert('object starts unlocked', bimIsLocked(toggleObj)===false);
bimSetLocked(toggleObj,true);
assert('bimSetLocked(true) locks the object', bimIsLocked(toggleObj)===true);
assert('locking pushes an undo snapshot', UNDO_STACK.length===1);
bimSetLocked(toggleObj,false);
assert('bimSetLocked(false) unlocks the object', bimIsLocked(toggleObj)===false);

// ---- 4. bimDuplicateObject never propagates lock to the copy ----
var lockedWall={id:'lw1',t:'room',pts:[[0,0],[2,0],[2,2],[0,2]],y:0,area:4,pos:[0,0,0],locked:true,layer:'layer-0'};
var dup=bimDuplicateObject(lockedWall,1,1);
assert('duplicating a locked object produces an UNLOCKED copy (new working geometry, not more reference geometry)',
  dup&&!dup.locked);

// ---- 5. IFC rectangular-wall recovery integrates correctly end to end ----
var cleanProfile=[[0,-0.15],[4,-0.15],[4,0.15],[0,0.15]];
var rec=bimTryRecoverWallFromRectProfile(cleanProfile,0,3);
assert('setup: recovery succeeds for a clean rectangular IFC-style profile', rec!==null);
var built=bimBuildWallGeometry(rec.centerline,rec.baseY,rec.height,rec.thickness,rec.align,rec.closed);
assert('a recovered wall\'s parametrics actually build a valid wall solid via the real pipeline', !built.error, JSON.stringify(built.error));
assert('rebuilt wall mesh is non-empty', built.mesh.f.length>0);

var messyProfile=[[0,0],[4,0],[4,0.4],[0,0.1]]; // not a clean rectangle
var recFail=bimTryRecoverWallFromRectProfile(messyProfile,0,3);
assert('a non-rectangular IFC profile correctly fails recovery (stays a safe imported-only wall)', recFail===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
