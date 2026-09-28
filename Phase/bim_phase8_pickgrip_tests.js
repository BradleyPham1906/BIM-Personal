var A3D={cam:{yaw:0,pitch:0.6,dist:20,tx:0,ty:0,tz:0},objs:[],flat:false,lastPolys:[],grips:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],activeLayer:'layer-0'};
var CSG_EPS=1e-5;
var el={cv:{width:800,height:600}};
var drag=null;

  function toScreen(p,V,W,H){
    var x=p[0]-V.eye[0],y=p[1]-V.eye[1],z=p[2]-V.eye[2];
    var xc=x*V.r[0]+y*V.r[1]+z*V.r[2];
    var yc=x*V.u[0]+y*V.u[1]+z*V.u[2];
    var zc=x*V.d[0]+y*V.d[1]+z*V.d[2];
    if(A3D.flat){
      var k=H*1.2/Math.max(A3D.cam.dist,0.5);
      return [W/2+xc*k,H/2-yc*k,Math.max(-zc,0.5)];
    }
    var w=-zc;if(w<0.5)w=0.5;
    var f=H*1.2;
    return [W/2+xc*f/w,H/2-yc*f/w,w];
  }

  function camVecs(c){
    var cy=Math.cos(c.yaw),sy=Math.sin(c.yaw),cp=Math.cos(c.pitch),sp=Math.sin(c.pitch);
    var d=[cp*sy,sp,cp*cy];
    var r=vnorm(vcross([0,1,0],d));
    var u=vcross(d,r);
    return {d:d,r:r,u:u,eye:[c.tx+d[0]*c.dist,c.ty+d[1]*c.dist,c.tz+d[2]*c.dist]};
  }

  function inPoly(x,y,pts){
    var inside=false,i,j;
    for(i=0,j=pts.length-1;i<pts.length;j=i++){
      var xi=pts[i][0],yi=pts[i][1],xj=pts[j][0],yj=pts[j][1];
      var hit=((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi);
      if(hit)inside=!inside;
    }
    return inside;
  }

  function bimPointSegDist(px,py,x1,y1,x2,y2){
    var dx=x2-x1,dy=y2-y1;
    var len2=dx*dx+dy*dy;
    var t=len2>1e-9?((px-x1)*dx+(py-y1)*dy)/len2:0;
    t=Math.max(0,Math.min(1,t));
    var cx=x1+t*dx,cy=y1+t*dy;
    var ex=px-cx,ey=py-cy;
    return Math.sqrt(ex*ex+ey*ey);
  }

  function bimPickSketch(x,y){
    var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height;
    var best=null,bestD=8,i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='sketch')continue;
      var lyr=bimLayerOf(o);
      if(lyr&&(lyr.visible===false||lyr.locked))continue;
      var pts=o.pts,n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){
        var a=pts[k],b=pts[(k+1)%n];
        var pa=toScreen([a[0],o.y,a[1]],V,W,H),pb=toScreen([b[0],o.y,b[1]],V,W,H);
        var d=bimPointSegDist(x,y,pa[0],pa[1],pb[0],pb[1]);
        if(d<bestD){bestD=d;best=o;}
      }
    }
    return best;
  }

  function bimGetEditablePoints(o){
    if(!o)return null;
    if(o.t==='sketch')return {pts:o.pts,y:o.y,kind:'sketch'};
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline)return {pts:o.bim.centerline,y:o.bim.baseY,kind:'wall'};
    return null;
  }

  function bimPickGrip(x,y){
    if(!A3D.grips)return null;
    var i,best=null,bestD=8;
    for(i=0;i<A3D.grips.length;i++){
      var g=A3D.grips[i],dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<bestD){bestD=d;best=g;}
    }
    return best;
  }

  function bimDragSketchPoint(o,idx,newXZ){
    if(!o||!o.pts||idx<0||idx>=o.pts.length)return false;
    o.pts[idx]=[newXZ[0],newXZ[1]];
    return true;
  }

  function bimDragWallPoint(o,idx,newXZ){
    if(!o||!o.bim||!o.bim.centerline||idx<0||idx>=o.bim.centerline.length)return false;
    var cl=o.bim.centerline.slice();
    cl[idx]=[newXZ[0],newXZ[1]];
    var res=bimBuildWallGeometry(cl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
    if(res.error)return false;
    res.bim.levelId=o.bim.levelId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    return true;
  }

  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
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

var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height;

A3D.objs=[{t:'sketch',id:'sk1',y:0,pts:[[0,0],[10,0]],closed:false}];
var onLine=toScreen([5,0,0],V,W,H);
var hitSketch=bimPickSketch(onLine[0],onLine[1]);
assert('bimPickSketch finds a sketch when clicking directly on its line', hitSketch&&hitSketch.id==='sk1', JSON.stringify(hitSketch));

var farAway=toScreen([50,0,50],V,W,H);
var missSketch=bimPickSketch(farAway[0],farAway[1]);
assert('bimPickSketch returns null when clicking far from any sketch', missSketch===null);

A3D.objs=[{t:'sketch',id:'sk2',y:0,pts:[[0,0],[10,0]],closed:false,layer:'layer-hidden'}];
A3D.layers.push({id:'layer-hidden',name:'Hidden',color:'#fff',visible:false,locked:false});
var hitHidden=bimPickSketch(onLine[0],onLine[1]);
assert('bimPickSketch ignores sketches on a hidden layer', hitHidden===null);
A3D.layers.pop();

A3D.objs=[{t:'sketch',id:'sk3',y:0,pts:[[0,0],[10,0]],closed:false,layer:'layer-locked'}];
A3D.layers.push({id:'layer-locked',name:'Locked',color:'#fff',visible:true,locked:true});
var hitLocked=bimPickSketch(onLine[0],onLine[1]);
assert('bimPickSketch ignores sketches on a locked layer', hitLocked===null);
A3D.layers.pop();

var sk={t:'sketch',y:0,pts:[[1,1],[2,2]]};
var ep1=bimGetEditablePoints(sk);
assert('sketch is editable (points + elevation exposed)', ep1&&ep1.kind==='sketch'&&ep1.pts.length===2);

var wallObj={t:'solid',bim:{type:'wall',centerline:[[0,0],[5,0],[5,5]],baseY:2}};
var ep2=bimGetEditablePoints(wallObj);
assert('wall is editable via its stored centerline', ep2&&ep2.kind==='wall'&&ep2.pts.length===3&&ep2.y===2);

var plainSolid={t:'solid',mesh:{v:[],f:[]}};
var ep3=bimGetEditablePoints(plainSolid);
assert('a plain solid (no bim metadata) is not editable', ep3===null);

A3D.grips=[{x:100,y:100,idx:0,objId:'a',kind:'sketch',elev:0},{x:300,y:300,idx:1,objId:'a',kind:'sketch',elev:0}];
var g1=bimPickGrip(102,101);
assert('bimPickGrip finds the nearest grip within threshold', g1&&g1.idx===0);
var g2=bimPickGrip(500,500);
assert('bimPickGrip returns null when no grip is within threshold', g2===null);

var skd={pts:[[0,0],[5,5],[9,9]]};
var okDrag=bimDragSketchPoint(skd,1,[7,7]);
assert('bimDragSketchPoint reports success', okDrag===true);
assert('bimDragSketchPoint updates only the targeted point', skd.pts[0][0]===0 && skd.pts[1][0]===7 && skd.pts[1][1]===7 && skd.pts[2][0]===9);
var badDrag=bimDragSketchPoint(skd,99,[1,1]);
assert('bimDragSketchPoint rejects an out-of-range index gracefully', badDrag===false);

var room=sketchCCW([[0,0],[6,0],[6,4],[0,4]]);
var gg=bimBuildWallGeometry(room,0,3,0.3,'center',true);
assert('setup: wall geometry builds for the drag test', !gg.error, JSON.stringify(gg.error));
var wallO={id:'w1',t:'solid',mesh:gg.mesh,bim:gg.bim};
wallO.bim.levelId='lvl-0';
var okWallDrag=bimDragWallPoint(wallO,1,[9,0]);
assert('bimDragWallPoint reports success', okWallDrag===true);
assert('bimDragWallPoint updates the stored centerline point', wallO.bim.centerline[1][0]===9 && wallO.bim.centerline[1][1]===0);
assert('bimDragWallPoint preserves levelId across the live rebuild', wallO.bim.levelId==='lvl-0');
assert('bimDragWallPoint actually regenerated the mesh (not a no-op)', wallO.mesh.f.length>0);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
