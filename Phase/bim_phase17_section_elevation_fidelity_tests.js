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
  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}

  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}

  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}

  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}

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

  function triOk(a,b,c){
    var n=vcross(vsub(b,a),vsub(c,a));
    return (n[0]*n[0]+n[1]*n[1]+n[2]*n[2])>1e-12;
  }

  function cpoly(v,pl){return {v:v,p:pl||planeOf(v)};}

  function planeOf(v){var n=faceNormal(v);return {n:n,w:vdot(n,v[0])};}

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

  function csgIntersect(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.invert();b.clipTo(a);b.invert();a.clipTo(b);b.clipTo(a);a.build(b.all());a.invert();return a.all();}

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
  };  function bimModelExtentSize(){
    if(!A3D.objs.length)return 50;
    var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],i,j,k;
    for(i=0;i<A3D.objs.length;i++){
      var m=A3D.objs[i].mesh;if(!m)continue;
      for(j=0;j<m.v.length;j++){
        for(k=0;k<3;k++){
          var vv=m.v[j][k]+A3D.objs[i].pos[k];
          if(vv<mn[k])mn[k]=vv;
          if(vv>mx[k])mx[k]=vv;
        }
      }
    }
    var sz=Math.max(mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2]);
    return (isFinite(sz)&&sz>0)?sz*3+20:50;
  }

  function bimBuildHalfSpaceBox(P,dir,keepSign,size){
    var perp=[-dir[1],dir[0]];
    function pt(u,v){return [P[0]+dir[0]*u+perp[0]*v,P[1]+dir[1]*u+perp[1]*v];}
    var footprint=[pt(-size,0),pt(size,0),pt(size,keepSign*size),pt(-size,keepSign*size)];
    return padMesh(sketchCCW(footprint),-size,size*2);
  }

  function bimComputeSectionCuts(P,dir,keepSign){
    var size=bimModelExtentSize();
    var boxMesh=bimBuildHalfSpaceBox(P,dir,keepSign,size);
    var cuts={},i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='solid'||!o.mesh||!o.mesh.f||!o.mesh.f.length)continue;
      try{
        var objPolys=meshPolys(o);
        var boxPolys=meshPolys({mesh:boxMesh,pos:[0,0,0]});
        var cutPolys=csgIntersect(objPolys,boxPolys);
        cuts[o.id]=polysToMesh(cutPolys);
      }catch(eC){
        console.warn('[BIM] Section cut failed for object '+o.id+': ',eC);
      }
    }
    return cuts;
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

// ---- 1. Section cut of a real box object (via the actual embedded pipeline) ----
var boxA={id:'boxA',t:'solid',name:'Box',pos:[0,0,0],mesh:padMesh(sketchCCW([[0,0],[10,0],[10,10],[0,10]]),0,4),layer:'layer-0'};
A3D.objs=[boxA];
var cuts=bimComputeSectionCuts([5,0],[0,1],1);
assert('section cut computes a result for the box', !!cuts['boxA']);
assert('cut mesh is watertight', checkWatertight(cuts['boxA'])===0, checkWatertight(cuts['boxA']));
var xs=cuts['boxA'].v.map(function(p){return p[0];});
assert('keepSign=1 keeps the correct (lower-X) half', Math.max.apply(null,xs)<=5.001);

var cuts2=bimComputeSectionCuts([5,0],[0,1],-1);
var xs2=cuts2['boxA'].v.map(function(p){return p[0];});
assert('keepSign=-1 keeps the opposite (upper-X) half', Math.min.apply(null,xs2)>=4.999);

// ---- 2. meshOf becomes section-aware without touching the object's real mesh ----
var originalMeshRef=boxA.mesh;
A3D.section={p:[5,0],dir:[0,1],keepSign:1,cutMeshes:cuts};
var mo=meshOf(boxA);
assert('meshOf returns the CUT mesh while a section is active', mo===cuts['boxA']);
assert('the object\'s own .mesh field is completely untouched (non-destructive)', boxA.mesh===originalMeshRef);
A3D.section=null;
assert('meshOf reverts to the real mesh once section is cleared', meshOf(boxA)===originalMeshRef);

// ---- 3. Full enter/exit lifecycle via the real embedded functions ----
A3D.cam={yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3};
A3D.flat=false;A3D.view='Home';
bimEnterSection([5,0],[0,1]);
assert('entering a section activates A3D.section', !!A3D.section);
assert('entering a section switches to orthographic (flat) mode', A3D.flat===true);
assert('entering a section sets the view label', A3D.view==='Section');
assert('entering a section remembers the prior camera for restoration', A3D.section.prevCam.tx===1&&A3D.section.prevCam.ty===2&&A3D.section.prevCam.tz===3);

var camAfterEnter={yaw:A3D.cam.yaw,pitch:A3D.cam.pitch};
bimFlipSection();
assert('flipping toggles keepSign', A3D.section.keepSign===-1);
assert('flipping re-aims the camera to the opposite yaw', Math.abs(A3D.cam.yaw-camAfterEnter.yaw)>1);

bimExitSection();
assert('exiting clears A3D.section', A3D.section===null);
assert('exiting restores the exact prior camera position', A3D.cam.tx===1&&A3D.cam.ty===2&&A3D.cam.tz===3);
assert('exiting restores the prior flat/view state', A3D.flat===false&&A3D.view==='Home');

// ---- 4. Real mitered wall: section preserves correct wall thickness at the cut ----
// (build a minimal wall-shaped box standing in for the real ribbon-mesh output, since we're
// testing the SECTION pipeline here, not re-deriving wall geometry -- already covered elsewhere)
var wallStandin={id:'wallX',t:'solid',name:'Wall',pos:[0,0,0],
  mesh:padMesh(sketchCCW([[0,-0.15],[6,-0.15],[6,0.15],[0,0.15]]),0,3),layer:'layer-0'};
A3D.objs=[wallStandin];
var wallCuts=bimComputeSectionCuts([3,0],[0,1],1);
var wc=wallCuts['wallX'];
var zs=wc.v.map(function(p){return p[2];});
assert('wall section cut preserves the full 0.3m thickness at the cut face',
  Math.abs(Math.min.apply(null,zs)-(-0.15))<1e-6 && Math.abs(Math.max.apply(null,zs)-0.15)<1e-6);

// ---- 5. Elevation views (setView) are genuinely orthographic; Home/Iso stay perspective ----
assert('VIEWS.front is flagged orthographic', VIEWS.front.ortho===true);
assert('VIEWS.right is flagged orthographic', VIEWS.right.ortho===true);
assert('VIEWS.top is flagged orthographic', VIEWS.top.ortho===true);
assert('VIEWS.home is NOT orthographic (stays perspective for navigation)', VIEWS.home.ortho===false);
assert('VIEWS.iso is NOT orthographic', VIEWS.iso.ortho===false);
assert('elevation views are labeled clearly', VIEWS.front.label.indexOf('Elevation')>=0 && VIEWS.right.label.indexOf('Elevation')>=0);

setView('front',false);
assert('calling setView(front) actually activates orthographic mode', A3D.flat===true);
setView('home',false);
assert('calling setView(home) actually deactivates orthographic mode', A3D.flat===false);

// ---- 6. groundPoint declines gracefully for near-horizontal (elevation) cameras ----
A3D.flat=true;
A3D.cam={yaw:0,pitch:0.02,dist:20,tx:0,ty:0,tz:0};
var gp=groundPoint(650,150,0);
assert('groundPoint returns null for a near-horizontal (elevation-like) camera instead of an unstable point', gp===null);
A3D.cam={yaw:0,pitch:1.52,dist:20,tx:0,ty:0,tz:0};
var gp2=groundPoint(400,300,0);
assert('groundPoint still works normally for a near-top-down (plan) camera', gp2!==null && isFinite(gp2[0]));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
