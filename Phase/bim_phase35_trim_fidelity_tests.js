var A3D={objs:[],counts:{},seq:1,layers:[],activeLayer:'L1',activeLevel:'lvl-0',sel:null,sel2:null,selSet:[]};
var UNDO=[];function pushUndo(){UNDO.push(1);}
function refreshTree(){} function paint(){} function saveSoon(){}
var TOASTS=[];function a3dToast(m){TOASTS.push(m);}
  function bimSegIntersectParams(a1,a2,b1,b2){
    var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
    var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
    var den=d1x*d2z-d1z*d2x;
    if(Math.abs(den)<1e-12)return null;
    var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
    var t=(dx*d2z-dz*d2x)/den;
    var u=(dx*d1z-dz*d1x)/den;
    return {pt:[a1[0]+d1x*t,a1[1]+d1z*t],t:t,u:u};
  }

  function bimPtSegDist2D(p,a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1];
    var L2=dx*dx+dz*dz;
    var t=L2?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
    t=Math.max(0,Math.min(1,t));
    return Math.sqrt(Math.pow(p[0]-(a[0]+dx*t),2)+Math.pow(p[1]-(a[1]+dz*t),2));
  }

  function bimTrimPolyline(pts,closed,cutterPts,cutterClosed,clickPt){
    if(closed)return {error:'Trim needs an open wall (a closed loop has no free end to remove)'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    var n=pts.length,cn=cutterPts.length;
    var cSegs=cutterClosed?cn:cn-1;
    var best=null,i,j;
    for(i=0;i<n-1;i++){
      for(j=0;j<cSegs;j++){
        var r=bimSegIntersectParams(pts[i],pts[i+1],cutterPts[j],cutterPts[(j+1)%cn]);
        if(!r)continue;
        if(r.t<-1e-9||r.t>1+1e-9)continue;
        if(r.u<-1e-9||r.u>1+1e-9)continue;
        if(!best)best={seg:i,t:r.t,pt:r.pt};
      }
    }
    if(!best)return {error:'Those two walls do not cross \u2014 nothing to trim'};
    var clickSeg=-1,clickT=0,bestD=Infinity,k;
    for(k=0;k<n-1;k++){
      var d=bimPtSegDist2D(clickPt,pts[k],pts[k+1]);
      if(d<bestD){
        bestD=d;clickSeg=k;
        var dx=pts[k+1][0]-pts[k][0],dz=pts[k+1][1]-pts[k][1];
        var L2=dx*dx+dz*dz;
        clickT=L2?((clickPt[0]-pts[k][0])*dx+(clickPt[1]-pts[k][1])*dz)/L2:0;
        clickT=Math.max(0,Math.min(1,clickT));
      }
    }
    var out=[];
    if((clickSeg+clickT)>(best.seg+best.t)){
      for(k=0;k<=best.seg;k++)out.push([pts[k][0],pts[k][1]]);
      out.push([best.pt[0],best.pt[1]]);
    }else{
      out.push([best.pt[0],best.pt[1]]);
      for(k=best.seg+1;k<n;k++)out.push([pts[k][0],pts[k][1]]);
    }
    var clean=[out[0]];
    for(k=1;k<out.length;k++){
      var pv=clean[clean.length-1];
      if(Math.abs(pv[0]-out[k][0])>1e-6||Math.abs(pv[1]-out[k][1])>1e-6)clean.push(out[k]);
    }
    if(clean.length<2)return {error:'Trim would remove the whole wall'};
    return {pts:clean,cutAt:best.pt};
  }

  function bimApplyTrim(cutterId,clickPt){
    var cutter=objById(cutterId);
    if(!cutter){a3dToast('Cutting wall no longer exists');return;}
    var target=null,bestD=Infinity,i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.id===cutterId)continue;
      if(!o.bim||o.bim.type!=='wall'||!o.bim.centerline)continue;
      if(bimIsLocked(o))continue;
      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        var d=bimPtSegDist2D(clickPt,cl[k],cl[(k+1)%n]);
        if(d<bestD){bestD=d;target=o;}
      }
    }
    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    var r=bimTrimPolyline(target.bim.centerline,target.bim.closed,cutter.bim.centerline,cutter.bim.closed,clickPt);
    if(r.error){a3dToast('Trim: '+r.error);return;}
    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false);
    if(res.error){a3dToast('Trim: '+res.error);return;}
    pushUndo();
    res.bim.levelId=target.bim.levelId;
    target.mesh=res.mesh;
    target.bim=res.bim;
    refreshTree();paint();saveSoon();
    a3dToast(target.name+' trimmed');
  }

  function bimIsLocked(o){return !!(o&&o.locked);}

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
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

  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
  }

  function bimAlignOffsets(thickness,align){
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
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

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}
function mkWall(id,cl){
  var r=bimBuildWallGeometry(cl,0,3,0.3,'center',false);
  return {id:id,t:'solid',name:id,bim:r.bim,mesh:r.mesh,pos:[0,0,0],layer:'L1'};
}

// two crossing walls
var target=mkWall('W_target',[[0,0],[10,0]]);
var cutter=mkWall('W_cutter',[[6,-5],[6,5]]);
A3D.objs=[target,cutter];
UNDO.length=0;
bimApplyTrim('W_cutter',[9,0]);
assert('real bimApplyTrim pushes one undo', UNDO.length===1, UNDO.length);
assert('target wall centerline truncated at the intersection',
  target.bim.centerline.length===2&&approx(target.bim.centerline[1][0],6), JSON.stringify(target.bim.centerline));
assert('trimmed wall keeps its original start point', approx(target.bim.centerline[0][0],0));
assert('trimmed wall rebuilt with real geometry', target.mesh&&target.mesh.f.length>0);
assert('trim reports success', TOASTS.some(function(t){return t.indexOf('trimmed')>=0;}), TOASTS.join('|'));

// opposite side
var t2=mkWall('T2',[[0,0],[10,0]]);
A3D.objs=[t2,cutter];
bimApplyTrim('W_cutter',[1,0]);
assert('clicking the other side keeps the far portion', approx(t2.bim.centerline[0][0],6)&&approx(t2.bim.centerline[1][0],10), JSON.stringify(t2.bim.centerline));

// non-crossing -> refused, geometry untouched
var t3=mkWall('T3',[[0,20],[10,20]]);
A3D.objs=[t3,cutter];
var before=JSON.stringify(t3.bim.centerline);
TOASTS.length=0;UNDO.length=0;
bimApplyTrim('W_cutter',[5,20]);
assert('non-crossing walls: geometry left untouched', JSON.stringify(t3.bim.centerline)===before);
assert('non-crossing walls: no undo pushed for a no-op', UNDO.length===0);
assert('non-crossing walls: explains why', TOASTS.some(function(t){return t.indexOf('do not cross')>=0||t.indexOf('closer')>=0;}), TOASTS.join('|'));

// locked target is skipped
var t4=mkWall('T4',[[0,0],[10,0]]);
t4.locked=true;
A3D.objs=[t4,cutter];
var before4=JSON.stringify(t4.bim.centerline);
bimApplyTrim('W_cutter',[9,0]);
assert('a locked wall is never trimmed', JSON.stringify(t4.bim.centerline)===before4);

// closed loop refused
var t5=mkWall('T5',[[0,0],[8,0],[8,8],[0,8]]);
t5.bim.closed=true;
A3D.objs=[t5,cutter];
TOASTS.length=0;
bimApplyTrim('W_cutter',[4,0]);
assert('a closed wall loop is refused with a clear reason', TOASTS.some(function(t){return t.indexOf('closed loop')>=0||t.indexOf('open wall')>=0;}), TOASTS.join('|'));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
