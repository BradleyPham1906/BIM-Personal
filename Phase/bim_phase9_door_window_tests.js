var CSG_EPS=1e-5;
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

  function csgSubtract(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());a.invert();return a.all();}
  function csgIntersect(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();b.clipTo(a);b.invert();a.clipTo(b);b.clipTo(a);a.build(b.all());a.invert();return a.all();}
  function doBool(kind){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Booleans need two solids: click the first, Ctrl+click the second');return null;}
    var res;
    try{
      var pa=meshPolys(a),pb=meshPolys(b);
      if(kind==='union')res=csgUnion(pa,pb);
      else if(kind==='cut')res=csgSubtract(pa,pb);
      else res=csgIntersect(pa,pb);
    }catch(e3){a3dToast('Boolean failed: '+String(e3&&e3.message||e3));return null;}
    var m=polysToMesh(res||[]);
    if(!m.f||m.f.length<4){a3dToast('Boolean produced an empty result (no overlap?)');return null;}
    pushUndo();
    A3D.counts[kind]=(A3D.counts[kind]||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'solid',name:BOOLNAMES[kind]+' '+A3D.counts[kind],
      col:a.col||(TYPES[a.t]||{}).c||'#9db4c8',
      pos:[0,0,0],mesh:m
    };
    var ia=A3D.objs.indexOf(a),ib=A3D.objs.indexOf(b);
    A3D.objs.splice(Math.max(ia,ib),1);
    A3D.objs.splice(Math.min(ia,ib),1);
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    return o;
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

  function bimWallSegQuad(a,b,dLeft,dRight){
    var n=bimSegNormal(a,b);
    var lx=n[0]*dLeft,lz=n[1]*dLeft,rx=-n[0]*dRight,rz=-n[1]*dRight;
    return [[a[0]+lx,a[1]+lz],[b[0]+lx,b[1]+lz],[b[0]+rx,b[1]+rz],[a[0]+rx,a[1]+rz]];
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

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

var g=bimBuildWallGeometry([[0,0],[10,0]],0,3,0.3,'center',false);
assert('setup: wall builds successfully', !g.error, JSON.stringify(g.error));
var wallO={id:'w1',t:'solid',mesh:g.mesh,bim:g.bim};
var beforeFaces=wallO.mesh.f.length;

var res=bimBuildWallOpening(wallO,[5,0],0.9,2.1,0);
assert('door opening cut succeeds (real embedded code)', !res.error, JSON.stringify(res.error));
assert('cut result has more faces than the solid wall', res.mesh.f.length>beforeFaces);

var xs=res.mesh.v.map(function(v){return v[0];});
assert('opening edges present at ~4.55 and ~5.45', xs.some(function(x){return Math.abs(x-4.55)<0.02;}) && xs.some(function(x){return Math.abs(x-5.45)<0.02;}));

var ys=res.mesh.v.map(function(v){return v[1];});
assert('door head height (2.1) present in result', ys.some(function(y){return Math.abs(y-2.1)<0.02;}));

var res2=bimBuildWallOpening(wallO,[2,0],1.2,1.2,0.9);
assert('window opening cut succeeds (real embedded code)', !res2.error, JSON.stringify(res2.error));
var ys2=res2.mesh.v.map(function(v){return v[1];});
assert('window sill (0.9) and head (2.1) both present', ys2.some(function(y){return Math.abs(y-0.9)<0.02;}) && ys2.some(function(y){return Math.abs(y-2.1)<0.02;}));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
