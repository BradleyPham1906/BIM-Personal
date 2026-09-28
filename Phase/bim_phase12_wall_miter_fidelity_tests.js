var A3D={};
var CSG_EPS=1e-5;
function a3dToast(){}
function meshOf(o){return o.mesh;}
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

  function buildWallSolid(pts,y0,height,thickness,align,closed){
    var res=bimBuildWallGeometry(pts,y0,height,thickness,align,closed);
    if(res.error){a3dToast(res.error);paint();return null;}
    pushUndo();
    A3D.counts.wall=(A3D.counts.wall||0)+1;
    res.bim.levelId=A3D.activeLevel;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:'#c7bfae',pos:[0,0,0],mesh:res.mesh,bim:res.bim};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
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

  function planeOf(v){var n=faceNormal(v);return {n:n,w:vdot(n,v[0])};}

  function cpoly(v,pl){return {v:v,p:pl||planeOf(v)};}

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

  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}

  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}

  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}

  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}

  function bimFindWallSegmentAt(wallObj,clickXZ){
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

  function bimBuildOpeningBoxPoly(center,dirXZ,width,thickness,sillY,height){
    var nx=-dirXZ[1],nz=dirXZ[0];
    var hw=width/2,ht=thickness/2+0.05;
    return [
      [center[0]-dirXZ[0]*hw-nx*ht,center[1]-dirXZ[1]*hw-nz*ht],
      [center[0]+dirXZ[0]*hw-nx*ht,center[1]+dirXZ[1]*hw-nz*ht],
      [center[0]+dirXZ[0]*hw+nx*ht,center[1]+dirXZ[1]*hw+nz*ht],
      [center[0]-dirXZ[0]*hw+nx*ht,center[1]-dirXZ[1]*hw+nz*ht]
    ];
  }

  function bimBuildWallOpening(wallObj,clickXZ,width,height,sillHeight){
    var seg=bimFindWallSegmentAt(wallObj,clickXZ);
    if(!seg)return {error:'Could not find a wall segment near that point'};
    var dx=seg.b[0]-seg.a[0],dz=seg.b[1]-seg.a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    var dir=[dx/len,dz/len];
    var openPoly;
    try{
      openPoly=sketchCCW(bimBuildOpeningBoxPoly(seg.center,dir,width,wallObj.bim.thickness,wallObj.bim.baseY+sillHeight,height));
      var openMesh=padMesh(openPoly,wallObj.bim.baseY+sillHeight,height);
      var wallPolys=meshPolys({mesh:wallObj.mesh,pos:[0,0,0]});
      var openPolys=meshPolys({mesh:openMesh,pos:[0,0,0]});
      var result=csgSubtract(wallPolys,openPolys);
    }catch(eD){
      return {error:'Opening cut failed: '+(eD&&eD.message?eD.message:eD)};
    }
    var nm=polysToMesh(result);
    if(!nm||!nm.f||nm.f.length<4)return {error:'Opening cut produced an empty result'};
    return {mesh:nm,center:seg.center,dir:dir};
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

  function csgSubtract(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());a.invert();return a.all();}

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

var res1=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
assert('closed wall builds without error', !res1.error, JSON.stringify(res1.error));
assert('closed wall mesh is watertight', checkWatertight(res1.mesh)===0, 'bad edges: '+checkWatertight(res1.mesh));
assert('closed wall stores innerLoop/outerLoop with 4 points each (one per corner, truly mitered)',
  res1.bim.innerLoop.length===4 && res1.bim.outerLoop.length===4);
var c0=res1.bim.innerLoop[0];
assert('mitered inner corner sits at a finite, sane position (no NaN/Infinity from a degenerate offset)',
  isFinite(c0[0])&&isFinite(c0[1]));

var res2=bimBuildWallGeometry([[0,0],[5,0],[5,3]],0,3,0.3,'center',false);
assert('open L-wall builds without error', !res2.error, JSON.stringify(res2.error));
assert('open L-wall mesh is watertight (has end caps)', checkWatertight(res2.mesh)===0, 'bad edges: '+checkWatertight(res2.mesh));
assert('open wall has no innerLoop/outerLoop (matches pre-existing convention: only closed walls get one)',
  !res2.bim.innerLoop && !res2.bim.outerLoop);

['left','right','center'].forEach(function(al){
  var r=bimBuildWallGeometry([[0,0],[4,0],[4,4],[0,4]],0,2.5,0.25,al,true);
  assert('align='+al+' closed wall builds cleanly', !r.error && checkWatertight(r.mesh)===0);
});

var res3=bimBuildWallGeometry([[0,0],[0,0],[5,0],[5,0],[5,3]],0,3,0.3,'center',false);
assert('wall with duplicate consecutive points still builds (deduped internally)', !res3.error, JSON.stringify(res3.error));
assert('deduped wall mesh is watertight', checkWatertight(res3.mesh)===0);

var wallForDoor=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
var wallObj={mesh:wallForDoor.mesh,bim:wallForDoor.bim,pos:[0,0,0]};
var cutRes=bimBuildWallOpening(wallObj,[3,0],0.9,2.1,0);
assert('door opening cut against a mitered wall succeeds', !cutRes.error, JSON.stringify(cutRes&&cutRes.error));
if(!cutRes.error){
  assert('cut result mesh has more geometry than the uncut wall (a hole was actually cut)',
    cutRes.mesh.v.length>wallForDoor.mesh.v.length);
}

A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',sel:null,sel2:null,meshes:{}};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
var wallObj2=buildWallSolid([[0,0],[5,0],[5,3],[0,3]],0,3,0.25,'center',true);
assert('buildWallSolid creates a real object via the new pipeline', !!wallObj2 && A3D.objs.length===1);
var rebuildOk=bimRebuildWall(wallObj2,0.35,2.8,'center');
assert('bimRebuildWall (used by the Properties panel) still works against the new pipeline', rebuildOk===true);
assert('rebuilt wall mesh is watertight', checkWatertight(wallObj2.mesh)===0);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
