// Verify wall/floor build + in-place rebuild logic extracted verbatim from the patched file.
var A3D={objs:[],seq:1,counts:{},activeLevel:'lvl-0'};
var CSG_EPS=1e-5;
var UNDO_STACK=[],REDO_STACK=[],UNDO_MAX=50,undoSuspend=false;
function a3dToast(msg){ /* no-op in test */ }
function refreshTree(){ /* no-op: DOM refresh, not under test here */ }
function paint(){ /* no-op: canvas render, not under test here */ }
function saveSoon(){ /* no-op: localStorage persistence, not under test here */ }

  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
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

  function meshOf(o){
    if(o.mesh)return o.mesh;
    var key=o.t+'|'+JSON.stringify(o.prm||{});
    if(!A3D.meshes[key]){
      var tp=TYPES[o.t];
      if(!tp)return null;
      A3D.meshes[key]=tp.mk(mergePrm(o.t,o.prm));
    }
    return A3D.meshes[key];
  }

  function planeOf(v){var n=faceNormal(v);return {n:n,w:vdot(n,v[0])};}
  function cpoly(v,pl){return {v:v,p:pl||planeOf(v)};}
  function cflip(p){
    return {v:p.v.slice().reverse(),p:{n:[-p.p.n[0],-p.p.n[1],-p.p.n[2]],w:-p.p.w}};
  }

  function cpoly(v,pl){return {v:v,p:pl||planeOf(v)};}
  function cflip(p){
    return {v:p.v.slice().reverse(),p:{n:[-p.p.n[0],-p.p.n[1],-p.p.n[2]],w:-p.p.w}};
  }

  function cflip(p){
    return {v:p.v.slice().reverse(),p:{n:[-p.p.n[0],-p.p.n[1],-p.p.n[2]],w:-p.p.w}};
  }

  function csplit(pl,poly,cof,cob,fr,bk){
    var CO=0,FR=1,BK=2,SP=3,t=0,ts=[],i;
    for(i=0;i<poly.v.length;i++){
      var d=vdot(pl.n,poly.v[i])-pl.w;
      var ty=d<-CSG_EPS?BK:(d>CSG_EPS?FR:CO);
      t|=ty;ts.push(ty);
    }
    if(t===CO){(vdot(pl.n,poly.p.n)>0?cof:cob).push(poly);}
    else if(t===FR){fr.push(poly);}
    else if(t===BK){bk.push(poly);}
    else{
      var f=[],b=[];
      for(i=0;i<poly.v.length;i++){
        var j=(i+1)%poly.v.length,ti=ts[i],tj=ts[j],vi=poly.v[i],vj=poly.v[j];
        if(ti!==BK)f.push(vi);
        if(ti!==FR)b.push(vi);
        if((ti|tj)===SP){
          var tt=(pl.w-vdot(pl.n,vi))/vdot(pl.n,vsub(vj,vi));
          var vv=[vi[0]+(vj[0]-vi[0])*tt,vi[1]+(vj[1]-vi[1])*tt,vi[2]+(vj[2]-vi[2])*tt];
          f.push(vv);b.push(vv);
        }
      }
      if(f.length>=3)fr.push({v:f,p:poly.p});
      if(b.length>=3)bk.push({v:b,p:poly.p});
    }
  }

  function triOk(a,b,c){
    var n=vcross(vsub(b,a),vsub(c,a));
    return (n[0]*n[0]+n[1]*n[1]+n[2]*n[2])>1e-12;
  }

  function meshPolys(o){
    var m=meshOf(o),i,j;
    if(!m||!m.f||!m.f.length)return [];
    var tris=[];
    for(i=0;i<m.f.length;i++){
      var fc=m.f[i];
      for(j=2;j<fc.length;j++){
        var a=fc[0],b=fc[j-1],c=fc[j];
        if(a===b||b===c||a===c)continue;
        tris.push([a,b,c]);
      }
    }
    function ek(x,y){return x<y?x+'_'+y:y+'_'+x;}
    var em={};
    function addE(t,x,y){var kk=ek(x,y);if(!em[kk])em[kk]=[];em[kk].push({t:t,s:x<y?1:-1});}
    for(i=0;i<tris.length;i++){addE(i,tris[i][0],tris[i][1]);addE(i,tris[i][1],tris[i][2]);addE(i,tris[i][2],tris[i][0]);}
    var flip=[],comp=[],nc=0;
    for(i=0;i<tris.length;i++){flip.push(false);comp.push(-1);}
    var s0,e2,q;
    for(s0=0;s0<tris.length;s0++){
      if(comp[s0]!==-1)continue;
      comp[s0]=nc;
      var Q=[s0];
      while(Q.length){
        var cur=Q.pop(),T3=tris[cur];
        var te=[[T3[0],T3[1]],[T3[1],T3[2]],[T3[2],T3[0]]];
        for(e2=0;e2<3;e2++){
          var ex=te[e2][0],ey=te[e2][1];
          var cs=(ex<ey?1:-1)*(flip[cur]?-1:1);
          var lst=em[ek(ex,ey)]||[];
          for(q=0;q<lst.length;q++){
            var nb=lst[q];
            if(nb.t===cur||comp[nb.t]!==-1)continue;
            comp[nb.t]=nc;
            if(nb.s===cs)flip[nb.t]=true;
            Q.push(nb.t);
          }
        }
      }
      nc++;
    }
    var wv=[];
    for(i=0;i<m.v.length;i++)wv.push([m.v[i][0]+o.pos[0],m.v[i][1]+o.pos[1],m.v[i][2]+o.pos[2]]);
    var vol=[];
    for(i=0;i<nc;i++)vol.push(0);
    for(i=0;i<tris.length;i++){
      var t2=flip[i]?[tris[i][0],tris[i][2],tris[i][1]]:tris[i];
      vol[comp[i]]+=vdot(wv[t2[0]],vcross(wv[t2[1]],wv[t2[2]]));
    }
    var out=[];
    for(i=0;i<tris.length;i++){
      var t3=flip[i]?[tris[i][0],tris[i][2],tris[i][1]]:tris[i];
      if(vol[comp[i]]<0)t3=[t3[0],t3[2],t3[1]];
      var A=wv[t3[0]],B=wv[t3[1]],C=wv[t3[2]];
      if(!triOk(A,B,C))continue;
      out.push(cpoly([A,B,C],null));
    }
    return out;
  }

  function polysToMesh(polys){
    var vm={},verts=[],faces=[],fseen={},i,j;
    function vid(p){
      var k=p[0].toFixed(4)+','+p[1].toFixed(4)+','+p[2].toFixed(4);
      if(vm[k]===undefined){vm[k]=verts.length;verts.push([p[0],p[1],p[2]]);}
      return vm[k];
    }
    for(i=0;i<polys.length;i++){
      var f=[],ok=true;
      for(j=0;j<polys[i].v.length;j++){
        var id2=vid(polys[i].v[j]);
        if(f.indexOf(id2)>=0){ok=false;break;}
        f.push(id2);
      }
      if(!ok||f.length<3)continue;
      var fk=f.slice().sort(function(a,b){return a-b;}).join('_');
      if(fseen[fk])continue;
      fseen[fk]=1;
      faces.push(f);
    }
    return {v:verts,f:faces};
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

  function bimWallSegQuad(a,b,dLeft,dRight){
    var n=bimSegNormal(a,b);
    var lx=n[0]*dLeft,lz=n[1]*dLeft,rx=-n[0]*dRight,rz=-n[1]*dRight;
    return [[a[0]+lx,a[1]+lz],[b[0]+lx,b[1]+lz],[b[0]+rx,b[1]+rz],[a[0]+rx,a[1]+rz]];
  }

  function bimAlignOffsets(thickness,align){
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
  }

  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed){
    var off=bimAlignOffsets(thickness,align);
    var n=pts.length,segCount=closed?n:n-1,i,acc=null;
    if(segCount<1)return {error:'Wall needs at least 2 distinct points'};
    try{
      for(i=0;i<segCount;i++){
        var a=pts[i],b=pts[(i+1)%n];
        if(Math.abs(a[0]-b[0])<1e-6&&Math.abs(a[1]-b[1])<1e-6)continue;
        var quad=sketchCCW(bimWallSegQuad(a,b,off.dLeft,off.dRight));
        var segMesh=padMesh(quad,y0,height);
        var segPolys=meshPolys({mesh:segMesh,pos:[0,0,0]});
        acc=acc?csgUnion(acc,segPolys):segPolys;
      }
    }catch(eW){
      console.warn('[BIM] Wall solid build failed: ',eW);
      return {error:'Wall build failed: '+(eW&&eW.message?eW.message:eW)};
    }
    var nm=polysToMesh(acc||[]);
    if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid: check the centerline points'};
    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
    if(closed){
      bim.innerLoop=bimOffsetRing(sketchCCW(pts),off.dLeft,true);
      bim.outerLoop=bimOffsetRing(sketchCCW(pts),-off.dRight,true);
    }
    return {mesh:nm,bim:bim};
  }

  function bimRebuildWall(o,newThickness,newHeight,newAlign){
    if(!o||!o.bim||o.bim.type!=='wall')return false;
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

  function bimBuildFloorGeometry(profPts,y,thickness){
    var m;
    try{m=padMesh(profPts,y-thickness,thickness);}
    catch(eF){console.warn('[BIM] Floor solid build failed: ',eF);return {error:'Floor build failed: '+(eF&&eF.message?eF.message:eF)};}
    if(!m||!m.f||m.f.length<4)return {error:'Floor produced an empty solid: check the source profile'};
    return {mesh:m};
  }

  function bimRebuildFloor(o,newThickness,newMaterial){
    if(!o||!o.bim||o.bim.type!=='floor'||!o.bim.profile)return false;
    var res=bimBuildFloorGeometry(o.bim.profile,o.bim.baseY,newThickness);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    o.mesh=res.mesh;
    o.bim.thickness=newThickness;
    o.bim.material=newMaterial;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }

  function clampLevelElev(e){
    e=Number(e);
    if(!isFinite(e))return 0;
    if(e<-1000)e=-1000;
    if(e>1000)e=1000;
    return e;
  }

  function bimSnapshotState(){
    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,layers:A3D.layers,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer});
  }

  function bimRestoreState(json){
    var st;
    try{st=JSON.parse(json);}catch(eR){console.warn('[BIM] Corrupted undo snapshot, ignoring.',eR);return false;}
    undoSuspend=true;
    A3D.objs=st.objs||[];
    A3D.levels=(st.levels&&st.levels.length)?st.levels:A3D.levels;
    A3D.layers=(st.layers&&st.layers.length)?st.layers:A3D.layers;
    A3D.activeLevel=st.activeLevel||A3D.activeLevel;
    A3D.activeLayer=st.activeLayer||A3D.activeLayer;
    A3D.sel=null;A3D.sel2=null;A3D.meshes={};
    bimSyncActiveGlobal();
    refreshTree();refreshHud();refreshLevels();refreshLayers();paint();
    undoSuspend=false;
    return true;
  }

  function pushUndo(){
    if(undoSuspend)return;
    UNDO_STACK.push(bimSnapshotState());
    if(UNDO_STACK.length>UNDO_MAX)UNDO_STACK.shift();
    REDO_STACK.length=0;
  }

  function doUndo(){
    if(!UNDO_STACK.length){a3dToast('Nothing to undo');return;}
    REDO_STACK.push(bimSnapshotState());
    var st=UNDO_STACK.pop();
    if(bimRestoreState(st)){saveSoon();a3dToast('Undo');}
  }

  function doRedo(){
    if(!REDO_STACK.length){a3dToast('Nothing to redo');return;}
    UNDO_STACK.push(bimSnapshotState());
    var st=REDO_STACK.pop();
    if(bimRestoreState(st)){saveSoon();a3dToast('Redo');}
  }

  function CNode(polys){this.pl=null;this.f=null;this.b=null;this.po=[];if(polys&&polys.length)this.build(polys);}
  CNode.prototype.invert=function(){
    var i;
    for(i=0;i<this.po.length;i++)this.po[i]=cflip(this.po[i]);
    if(this.pl)this.pl={n:[-this.pl.n[0],-this.pl.n[1],-this.pl.n[2]],w:-this.pl.w};
    if(this.f)this.f.invert();
    if(this.b)this.b.invert();
    var t=this.f;this.f=this.b;this.b=t;
  };
  CNode.prototype.clipPolys=function(polys){
    if(!this.pl)return polys.slice();
    var fr=[],bk=[],i;
    for(i=0;i<polys.length;i++)csplit(this.pl,polys[i],fr,bk,fr,bk);
    if(this.f)fr=this.f.clipPolys(fr);
    bk=this.b?this.b.clipPolys(bk):[];
    return fr.concat(bk);
  };
  CNode.prototype.clipTo=function(o){
    this.po=o.clipPolys(this.po);
    if(this.f)this.f.clipTo(o);
    if(this.b)this.b.clipTo(o);
  };
  CNode.prototype.all=function(){
    var p=this.po.slice();
    if(this.f)p=p.concat(this.f.all());
    if(this.b)p=p.concat(this.b.all());
    return p;
  };
  CNode.prototype.build=function(polys){
    if(!polys||!polys.length)return;
    var i;
    if(!this.pl)this.pl={n:polys[0].p.n.slice(),w:polys[0].p.w};
    var fr=[],bk=[];
    for(i=0;i<polys.length;i++)csplit(this.pl,polys[i],this.po,this.po,fr,bk);
    if(fr.length){if(!this.f)this.f=new CNode(null);this.f.build(fr);}
    if(bk.length){if(!this.b)this.b=new CNode(null);this.b.build(bk);}
  };
  function csgUnion(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());return a.all();}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

var room=sketchCCW([[0,0],[6,0],[6,4],[0,4]]);
var g1=bimBuildWallGeometry(room,0,3,0.3,'center',true);
assert('initial wall geometry builds successfully', !g1.error, JSON.stringify(g1.error));
var ys1=g1.mesh.v.map(function(v){return v[1];});
assert('initial wall height matches requested height (3)', Math.max.apply(null,ys1)-Math.min.apply(null,ys1)===3);

var o={id:'a3d-test-1',t:'solid',name:'Wall_1',col:'#c7bfae',pos:[0,0,0],mesh:g1.mesh,bim:g1.bim};
o.bim.levelId='lvl-0';

var okRebuild=bimRebuildWall(o,0.6,5,'left');
assert('bimRebuildWall reports success', okRebuild===true);
assert('rebuilt wall bim.thickness updated to 0.6', o.bim.thickness===0.6);
assert('rebuilt wall bim.height updated to 5', o.bim.height===5);
assert('rebuilt wall bim.align updated to left', o.bim.align==='left');
assert('rebuilt wall levelId preserved through rebuild', o.bim.levelId==='lvl-0');
var ys2=o.mesh.v.map(function(v){return v[1];});
assert('rebuilt wall mesh height reflects new height (5)', Math.max.apply(null,ys2)-Math.min.apply(null,ys2)===5, 'range='+(Math.max.apply(null,ys2)-Math.min.apply(null,ys2)));

var xs2=o.mesh.v.map(function(v){return v[0];});
assert('rebuilt (left-aligned) wall footprint still spans the original 6x4 room plan',
  Math.min.apply(null,xs2)<=0 && Math.max.apply(null,xs2)>=6, 'xrange='+Math.min.apply(null,xs2)+'..'+Math.max.apply(null,xs2));

var badG=bimBuildWallGeometry([[1,1],[1,1]],0,3,0.3,'center',false);
assert('degenerate wall geometry returns an error object (not a throw)', !!badG.error);

var floorProfile=[[1,1],[5,1],[5,3],[1,3]];
var fg1=bimBuildFloorGeometry(floorProfile,3,0.2);
assert('initial floor geometry builds successfully', !fg1.error, JSON.stringify(fg1.error));
var fo={id:'a3d-test-2',t:'solid',name:'Floor_1',col:'#9aa79a',pos:[0,0,0],mesh:fg1.mesh,
  bim:{type:'floor',thickness:0.2,material:'Concrete Slab',levelId:'lvl-0',baseY:3,profile:floorProfile.slice()}};
var fys1=fo.mesh.v.map(function(v){return v[1];});
assert('initial floor sits directly below its base elevation (3)', Math.max.apply(null,fys1)===3 && Math.min.apply(null,fys1)===2.8,
  'range='+Math.min.apply(null,fys1)+'..'+Math.max.apply(null,fys1));

var okFloorRebuild=bimRebuildFloor(fo,0.5,'Steel Deck');
assert('bimRebuildFloor reports success', okFloorRebuild===true);
assert('rebuilt floor thickness updated', fo.bim.thickness===0.5);
assert('rebuilt floor material updated', fo.bim.material==='Steel Deck');
var fys2=fo.mesh.v.map(function(v){return v[1];});
assert('rebuilt floor still sits below the SAME base elevation (3), just thicker', Math.max.apply(null,fys2)===3 && Math.min.apply(null,fys2)===2.5,
  'range='+Math.min.apply(null,fys2)+'..'+Math.max.apply(null,fys2));

var legacyFloor={id:'a3d-test-3',t:'solid',name:'Floor_legacy',bim:{type:'floor',thickness:0.2,material:'Concrete Slab',baseY:3}};
var legacyResult=bimRebuildFloor(legacyFloor,0.4,'Timber Deck');
assert('rebuilding a floor without a stored profile fails gracefully (no throw, returns false)', legacyResult===false);

UNDO_STACK.length=0;REDO_STACK.length=0;
A3D.objs=[o,fo];
pushUndo();
assert('pushUndo records a snapshot', UNDO_STACK.length===1);
var parsed=JSON.parse(UNDO_STACK[0]);
assert('undo snapshot round-trips object count correctly', parsed.objs.length===2);
assert('undo snapshot preserves wall bim metadata', parsed.objs[0].bim.type==='wall' && parsed.objs[0].bim.thickness===0.6);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
