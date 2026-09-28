var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],meshes:{},section:null,
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}],
  cam:{yaw:-0.7,pitch:0.42,dist:20,tx:0,ty:0,tz:0},
  flat:false,view:'Home',prevCam:null,prevView:null,frames:0};
var DEFCAM={dist:20,tx:0,ty:0,tz:0};
var CSG_EPS=1e-5;
var TYPES={};
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
function a3dToast(){}
function closeDlg(){}
var el={flip:{textContent:'',setAttribute:function(){}},root:{classList:{add:function(){},remove:function(){},toggle:function(){}}},cv:{width:800,height:600}};
function mergePrm(){return {};}
  function bimClipTriangle(A,B,C,dA,dB,dC){
    var pts=[A,B,C],ds=[dA,dB,dC];
    var keep=[ds[0]>=-1e-7,ds[1]>=-1e-7,ds[2]>=-1e-7];
    var numKeep=(keep[0]?1:0)+(keep[1]?1:0)+(keep[2]?1:0);
    if(numKeep===3)return {kept:[[A,B,C]],cutEdge:null};
    if(numKeep===0)return {kept:[],cutEdge:null};
    var outPts=[],intersections=[],i;
    for(i=0;i<3;i++){
      var j=(i+1)%3;
      var pi=pts[i],pj=pts[j],di=ds[i],dj=ds[j];
      if(keep[i])outPts.push(pi);
      if(keep[i]!==keep[j]){
        var t=di/(di-dj);
        var ip=[pi[0]+(pj[0]-pi[0])*t,pi[1]+(pj[1]-pi[1])*t,pi[2]+(pj[2]-pi[2])*t];
        outPts.push(ip);
        intersections.push(ip);
      }
    }
    var tris=[];
    for(i=1;i<outPts.length-1;i++)tris.push([outPts[0],outPts[i],outPts[i+1]]);
    var cutEdge=(intersections.length===2)?[intersections[0],intersections[1]]:null;
    return {kept:tris,cutEdge:cutEdge};
  }

  function bimChainEdgesToLoops(edges){
    function keyOf(p){return p[0].toFixed(4)+','+p[1].toFixed(4)+','+p[2].toFixed(4);}
    function edgeKey(a,b){return a<b?a+'|'+b:b+'|'+a;}
    var pointByKey={},adj={},i;
    for(i=0;i<edges.length;i++){
      var k1=keyOf(edges[i][0]),k2=keyOf(edges[i][1]);
      if(k1===k2)continue;
      pointByKey[k1]=edges[i][0];pointByKey[k2]=edges[i][1];
      if(!adj[k1])adj[k1]=[];
      if(!adj[k2])adj[k2]=[];
      adj[k1].push(k2);
      adj[k2].push(k1);
    }
    var usedEdge={},loops=[];
    var allKeys=Object.keys(adj),ki;
    for(ki=0;ki<allKeys.length;ki++){
      var startKey=allKeys[ki];
      var neighbors=adj[startKey],ni;
      for(ni=0;ni<neighbors.length;ni++){
        var ek=edgeKey(startKey,neighbors[ni]);
        if(usedEdge[ek])continue;
        var loop=[startKey];
        var current=startKey,next=neighbors[ni];
        usedEdge[edgeKey(current,next)]=true;
        var guard=0;
        while(next!==startKey&&guard++<10000){
          loop.push(next);
          var nextNeighbors=adj[next],found=null,nj;
          for(nj=0;nj<nextNeighbors.length;nj++){
            var ek2=edgeKey(next,nextNeighbors[nj]);
            if(!usedEdge[ek2]){found=nextNeighbors[nj];usedEdge[ek2]=true;break;}
          }
          if(found===null)break;
          current=next;next=found;
        }
        if(next===startKey&&loop.length>=3)loops.push(loop.map(function(k){return pointByKey[k];}));
      }
    }
    return loops;
  }

  function bimCapLoop(loop3D,normal){
    if(loop3D.length<3)return [];
    var n=normal;
    var arbitrary=Math.abs(n[0])<0.9?[1,0,0]:[0,1,0];
    var u=vnorm(vcross(arbitrary,n));
    var v=vcross(n,u);
    var pts2D=loop3D.map(function(p){return [vdot(p,u),vdot(p,v)];});
    var area=0,i;
    for(i=0;i<pts2D.length;i++){var j=(i+1)%pts2D.length;area+=pts2D[i][0]*pts2D[j][1]-pts2D[j][0]*pts2D[i][1];}
    var pts3=loop3D.slice(),pts2=pts2D.slice();
    if(area<0){pts3.reverse();pts2.reverse();}
    var tris=earClip(pts2);
    var out=[];
    for(i=0;i<tris.length;i++)out.push([pts3[tris[i][0]],pts3[tris[i][1]],pts3[tris[i][2]]]);
    return out;
  }

  function bimClipMeshToPlane(mesh,planeP,planeN){
    var kept=[],cutEdges=[],i,j;
    for(i=0;i<mesh.f.length;i++){
      var fc=mesh.f[i];
      var faceTris=[];
      for(j=2;j<fc.length;j++)faceTris.push([fc[0],fc[j-1],fc[j]]);
      var t;
      for(t=0;t<faceTris.length;t++){
        var tri=faceTris[t];
        var A=mesh.v[tri[0]],B=mesh.v[tri[1]],C=mesh.v[tri[2]];
        var dA=vdot(vsub(A,planeP),planeN),dB=vdot(vsub(B,planeP),planeN),dC=vdot(vsub(C,planeP),planeN);
        var res=bimClipTriangle(A,B,C,dA,dB,dC);
        kept=kept.concat(res.kept);
        if(res.cutEdge)cutEdges.push(res.cutEdge);
      }
    }
    var loops=bimChainEdgesToLoops(cutEdges);
    var capTris=[];
    for(i=0;i<loops.length;i++)capTris=capTris.concat(bimCapLoop(loops[i],planeN));
    return bimWeldMesh(kept.concat(capTris));
  }

  function bimComputeSectionCuts(P,dir,keepSign){
    var perp=[-dir[1],dir[0]];
    var planeN=[perp[0]*keepSign,0,perp[1]*keepSign];
    var cuts={},i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='solid'||!o.mesh||!o.mesh.f||!o.mesh.f.length)continue;
      try{
        var localP=[P[0]-o.pos[0],0-o.pos[1],P[1]-o.pos[2]];
        cuts[o.id]=bimClipMeshToPlane(o.mesh,localP,planeN);
      }catch(eC){
        console.warn('[BIM] Section cut failed for object '+o.id+': ',eC);
      }
    }
    return cuts;
  }

  function bimWeldMesh(rawFaces){
    var vm={},verts=[],faces=[],i,j;
    function vid(p){
      var k=p[0].toFixed(5)+','+p[1].toFixed(5)+','+p[2].toFixed(5);
      if(vm[k]===undefined){vm[k]=verts.length;verts.push(p);}
      return vm[k];
    }
    for(i=0;i<rawFaces.length;i++){
      var f=[];
      for(j=0;j<rawFaces[i].length;j++)f.push(vid(rawFaces[i][j]));
      faces.push(f);
    }
    return {v:verts,f:faces};
  }

  function bimEnterSection(P,dir){
    var keepSign=1;
    var cuts=bimComputeSectionCuts(P,dir,keepSign);
    var c=A3D.cam;
    A3D.section={p:P,dir:dir,keepSign:keepSign,cutMeshes:cuts,
      prevCam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},prevFlat:A3D.flat,prevView:A3D.view};
    bimAimSectionCamera();
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    refreshTree();paint();saveSoon();
    a3dToast('Section view active \u2014 use Flip Section to see the other side, Exit Section to return');
  }

  function bimFlipSection(){
    if(!A3D.section){a3dToast('No active section to flip');return;}
    A3D.section.keepSign=-A3D.section.keepSign;
    A3D.section.cutMeshes=bimComputeSectionCuts(A3D.section.p,A3D.section.dir,A3D.section.keepSign);
    bimAimSectionCamera();
    paint();saveSoon();
  }

  function bimExitSection(){
    if(!A3D.section)return;
    var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView;
    var c=A3D.cam;
    c.yaw=prev.yaw;c.pitch=prev.pitch;c.dist=prev.dist;c.tx=prev.tx;c.ty=prev.ty;c.tz=prev.tz;
    A3D.flat=prevFlat;
    A3D.view=prevView||'Home';
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    A3D.section=null;
    refreshHud();paint();saveSoon();
    a3dToast('Exited section view');
  }

  function bimAimSectionCamera(){
    if(!A3D.section)return;
    var perp=[-A3D.section.dir[1],A3D.section.dir[0]];
    var viewDirX=-perp[0]*A3D.section.keepSign,viewDirZ=-perp[1]*A3D.section.keepSign;
    var yaw=Math.atan2(viewDirX,viewDirZ);
    var c=A3D.cam;
    c.yaw=yaw;c.pitch=0.02;
    A3D.flat=true;
    if(el.flip){el.flip.textContent='3D';el.flip.setAttribute('title','Go to 3D (Shift + >)');}
    if(el.root)el.root.classList.add('flat');
    fitScene();
    A3D.view='Section';
    refreshHud();
  }

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

  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}

  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}

  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}

  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}

  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }

  function earClip(P){
    var idx=[],i,n=P.length,tris=[],guard=0;
    for(i=0;i<n;i++)idx.push(i);
    function cross2(o,a2,b2){return (a2[0]-o[0])*(b2[1]-o[1])-(a2[1]-o[1])*(b2[0]-o[0]);}
    function inTri(p,a2,b2,c2){
      var d1=cross2(p,a2,b2),d2=cross2(p,b2,c2),d3=cross2(p,c2,a2);
      var neg=(d1<0)||(d2<0)||(d3<0),pos=(d1>0)||(d2>0)||(d3>0);
      return !(neg&&pos);
    }
    while(idx.length>3&&guard++<3000){
      var cut=false;
      for(i=0;i<idx.length;i++){
        var i0=idx[(i+idx.length-1)%idx.length],i1=idx[i],i2=idx[(i+1)%idx.length];
        if(cross2(P[i0],P[i1],P[i2])<=1e-9)continue;
        var ok=true,k;
        for(k=0;k<idx.length;k++){
          var ix=idx[k];
          if(ix===i0||ix===i1||ix===i2)continue;
          if(inTri(P[ix],P[i0],P[i1],P[i2])){ok=false;break;}
        }
        if(!ok)continue;
        tris.push([i0,i1,i2]);
        idx.splice(i,1);
        cut=true;
        break;
      }
      if(!cut)break;
    }
    if(idx.length===3)tris.push([idx[0],idx[1],idx[2]]);
    return tris;
  }

  function padMesh(P,y0,h){
    var n=P.length,v=[],f=[],i,j;
    for(i=0;i<n;i++)v.push([P[i][0],y0,P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],y0+h,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][0],tris[i][1],tris[i][2]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][2]+n,tris[i][1]+n,tris[i][0]+n]);
    for(i=0;i<n;i++){
      j=(i+1)%n;
      f.push([j,i,i+n,j+n]);
    }
    return {v:v,f:f};
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function bimGetActiveLevel(){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)return A3D.levels[i];
    return A3D.levels[0]||{id:'lvl-0',name:'Level 0',elev:0,height:3};
  }

  function groundPoint(sx,sy,y0){
    var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height,f=H*1.2;
    if(A3D.flat){
      var k=f/Math.max(A3D.cam.dist,0.5);
      var xc=(sx-W/2)/k,yc=(H/2-sy)/k;
      var px=V.eye[0]+V.r[0]*xc+V.u[0]*yc,pz=V.eye[2]+V.r[2]*xc+V.u[2]*yc;
      var dn=V.d[1];
      if(Math.abs(dn)<0.15)return null;
      var py=V.eye[1]+V.r[1]*xc+V.u[1]*yc;
      var t2=(y0-py)/(-dn);
      px+=-V.d[0]*t2;pz+=-V.d[2]*t2;
      return [px,y0,pz];
    }
    var a=(sx-W/2)/f,b=(H/2-sy)/f;
    var dir=[V.r[0]*a+V.u[0]*b-V.d[0],V.r[1]*a+V.u[1]*b-V.d[1],V.r[2]*a+V.u[2]*b-V.d[2]];
    if(Math.abs(dir[1])<1e-6)return null;
    var t=(y0-V.eye[1])/dir[1];
    if(t<=0)return null;
    return [V.eye[0]+dir[0]*t,y0,V.eye[2]+dir[2]*t];
  }

  function camVecs(c){
    var cy=Math.cos(c.yaw),sy=Math.sin(c.yaw),cp=Math.cos(c.pitch),sp=Math.sin(c.pitch);
    var d=[cp*sy,sp,cp*cy];
    var r=vnorm(vcross([0,1,0],d));
    var u=vcross(d,r);
    return {d:d,r:r,u:u,eye:[c.tx+d[0]*c.dist,c.ty+d[1]*c.dist,c.tz+d[2]*c.dist]};
  }

  function toggleFlat(){
    if(A3D.sk)cancelSketch();
    if(A3D.flat){
      A3D.flat=false;
      var c=A3D.cam;
      if(A3D.prevCam){c.yaw=A3D.prevCam.yaw;c.pitch=A3D.prevCam.pitch;}
      A3D.view=A3D.prevView||'Home';
    }else{
      A3D.prevCam={yaw:A3D.cam.yaw,pitch:A3D.cam.pitch};
      A3D.prevView=A3D.view;
      A3D.flat=true;
      A3D.cam.yaw=0;A3D.cam.pitch=1.52;
      A3D.view='Plan';
    }
    if(el.flip){
      el.flip.textContent=A3D.flat?'3D':'2D';
      el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');
    }
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    refreshHud();paint();saveSoon();
  }

  function fitScene(){
    if(!A3D.objs.length){setView('home');return;}
    var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],i,j,k;
    for(i=0;i<A3D.objs.length;i++){
      var m=meshOf(A3D.objs[i]);if(!m)continue;
      for(j=0;j<m.v.length;j++){
        for(k=0;k<3;k++){
          var vv=m.v[j][k]+A3D.objs[i].pos[k];
          if(vv<mn[k])mn[k]=vv;
          if(vv>mx[k])mx[k]=vv;
        }
      }
    }
    var c=A3D.cam;
    c.tx=(mn[0]+mx[0])/2;c.ty=(mn[1]+mx[1])/2;c.tz=(mn[2]+mx[2])/2;
    var sz=Math.max(mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2])+3.2;
    c.dist=Math.max(14,sz*1.6);
    A3D.view='Custom';
    refreshHud();paint();saveSoon();
  }

  var VIEWS={
    home:{yaw:-0.7,pitch:0.42,label:'Home',ortho:false},
    iso:{yaw:-0.7,pitch:0.42,label:'Isometric',ortho:false},
    top:{yaw:0,pitch:1.52,label:'Top (Plan)',ortho:true},
    bottom:{yaw:0,pitch:-1.52,label:'Bottom',ortho:true},
    front:{yaw:0,pitch:0.02,label:'Front Elevation',ortho:true},
    back:{yaw:Math.PI,pitch:0.02,label:'Back Elevation',ortho:true},
    right:{yaw:Math.PI/2,pitch:0.02,label:'Right Elevation',ortho:true},
    left:{yaw:-Math.PI/2,pitch:0.02,label:'Left Elevation',ortho:true}
  };

  function setView(name,anim){
    var v=VIEWS[name];if(!v)return;
    A3D.flat=!!v.ortho;
    A3D.prevCam=null;A3D.prevView=null;
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    A3D.view=v.label;
    refreshHud();
    var c=A3D.cam;
    var to={yaw:v.yaw,pitch:v.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz};
    if(name==='home'){to.dist=DEFCAM.dist;to.tx=DEFCAM.tx;to.ty=DEFCAM.ty;to.tz=DEFCAM.tz;}
    if(anim===false){
      c.yaw=to.yaw;c.pitch=to.pitch;c.dist=to.dist;c.tx=to.tx;c.ty=to.ty;c.tz=to.tz;
      paint();saveSoon();return;
    }
    var from={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz};
    var t0=Date.now(),dur=260;
    function step(){
      var t=Math.min(1,(Date.now()-t0)/dur);
      var e=1-Math.pow(1-t,3),k;
      for(k in to)if(to.hasOwnProperty(k))c[k]=from[k]+(to[k]-from[k])*e;
      paint();
      if(t<1&&A3D.on)requestAnimationFrame(step);
      else saveSoon();
    }
    requestAnimationFrame(step);
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function checkWatertight(mesh){
  var edgeCount={},i,j;
  for(i=0;i<mesh.f.length;i++){
    var fc=mesh.f[i];
    for(j=0;j<fc.length;j++){
      var a=fc[j],b=fc[(j+1)%fc.length];
      var k=a<b?a+'_'+b:b+'_'+a;
      edgeCount[k]=(edgeCount[k]||0)+1;
    }
  }
  var bad=0,k2;
  for(k2 in edgeCount)if(edgeCount[k2]!==2)bad++;
  return bad;
}

// ---- 1. THE definitive test: the real embedded pipeline on the exact case that broke CSG ----
var boxA={id:'boxA',t:'solid',name:'Box',pos:[0,0,0],mesh:padMesh(sketchCCW([[0,0],[10,0],[10,10],[0,10]]),0,4),layer:'layer-0'};
A3D.objs=[boxA];
var cuts=bimComputeSectionCuts([5,0],[0,1],1);
assert('section cut computes a result', !!cuts['boxA']);
assert('cut mesh is WATERTIGHT (the real embedded pipeline, the exact case that failed before)', checkWatertight(cuts['boxA'])===0, checkWatertight(cuts['boxA']));
var xs=cuts['boxA'].v.map(function(p){return p[0];});
assert('keepSign=1 keeps the correct half', Math.max.apply(null,xs)<=5.001);

var cuts2=bimComputeSectionCuts([5,0],[0,1],-1);
assert('opposite keepSign is also watertight', checkWatertight(cuts2['boxA'])===0, checkWatertight(cuts2['boxA']));

// ---- 2. Non-destructive: meshOf hooking still works correctly ----
var originalMeshRef=boxA.mesh;
A3D.section={p:[5,0],dir:[0,1],keepSign:1,cutMeshes:cuts};
assert('meshOf returns the cut mesh while section is active', meshOf(boxA)===cuts['boxA']);
assert('the object\'s real mesh is untouched', boxA.mesh===originalMeshRef);
A3D.section=null;
assert('meshOf reverts once section clears', meshOf(boxA)===originalMeshRef);

// ---- 3. Full lifecycle via the real embedded functions, now with WORKING geometry ----
A3D.cam={yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3};
A3D.flat=false;A3D.view='Home';
bimEnterSection([5,0],[0,1]);
assert('entering activates section mode', !!A3D.section);
assert('entering computes a genuinely watertight cut for the real object in the scene',
  checkWatertight(A3D.section.cutMeshes['boxA'])===0);
bimFlipSection();
assert('flipping recomputes a still-watertight cut', checkWatertight(A3D.section.cutMeshes['boxA'])===0);
bimExitSection();
assert('exiting restores the exact prior camera', A3D.cam.tx===1&&A3D.cam.ty===2&&A3D.cam.tz===3);
assert('exiting clears section state', A3D.section===null);

// ---- 4. Real mitered wall standin: thickness preserved AND watertight this time ----
var wallStandin={id:'wallX',t:'solid',name:'Wall',pos:[0,0,0],
  mesh:padMesh(sketchCCW([[0,-0.15],[6,-0.15],[6,0.15],[0,0.15]]),0,3),layer:'layer-0'};
A3D.objs=[wallStandin];
var wallCuts=bimComputeSectionCuts([3,0],[0,1],1);
var wc=wallCuts['wallX'];
assert('wall cut is fully watertight (previously silently broken, now fixed)', checkWatertight(wc)===0, checkWatertight(wc));
var zs=wc.v.map(function(p){return p[2];});
assert('wall cut still preserves full 0.3m thickness', Math.abs(Math.min.apply(null,zs)-(-0.15))<1e-6&&Math.abs(Math.max.apply(null,zs)-0.15)<1e-6);

// ---- 5. Elevations still genuinely orthographic (unaffected by the section fix) ----
assert('VIEWS.front is orthographic', VIEWS.front.ortho===true);
assert('VIEWS.home is NOT orthographic', VIEWS.home.ortho===false);
setView('front',false);
assert('setView(front) activates orthographic mode', A3D.flat===true);

// ---- 6. groundPoint fix still in place ----
A3D.flat=true;A3D.cam={yaw:0,pitch:0.02,dist:20,tx:0,ty:0,tz:0};
assert('groundPoint still declines for near-horizontal cameras', groundPoint(650,150,0)===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
