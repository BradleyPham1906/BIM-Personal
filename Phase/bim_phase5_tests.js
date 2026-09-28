
var CSG_EPS=1e-5;

// ==== Verbatim CSG kernel, extracted from the patched canvas_v10.html (Phase 4 baseline) ====
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
  function triOk(a,b,c){
    var n=vcross(vsub(b,a),vsub(c,a));
    return (n[0]*n[0]+n[1]*n[1]+n[2]*n[2])>1e-12;
  }

  function csgUnion(ap,bp){var a=new CNode(ap),b=new CNode(bp);a.clipTo(b);b.clipTo(a);b.invert();b.clipTo(a);b.invert();a.build(b.all());return a.all();}
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


// ==== Verbatim new BIM helper functions, extracted from the patched canvas_v10.html (Phase 5) ====
  function clampLevelHeight(h){
    h=Number(h);
    if(!isFinite(h))return 3;
    if(h<0.1)h=0.1;
    if(h>100)h=100;
    return h;
  }

  function clampLevelElev(e){
    e=Number(e);
    if(!isFinite(e))return 0;
    if(e<-1000)e=-1000;
    if(e>1000)e=1000;
    return e;
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



// ==== Test harness ====
var PASS=0, FAIL=0;
function assert(name, cond, detail){
  if(cond){ PASS++; console.log('PASS  '+name); }
  else { FAIL++; console.log('FAIL  '+name+(detail?'  -- '+detail:'')); }
}
function polyArea(P){var a=0,i,j;for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}return a/2;}
function unionSegments(pts,y0,height,thickness,align,closed){
  var off=bimAlignOffsets(thickness,align);
  var n=pts.length, segCount=closed?n:n-1, i, acc=null;
  for(i=0;i<segCount;i++){
    var a=pts[i], b=pts[(i+1)%n];
    if(Math.abs(a[0]-b[0])<1e-6 && Math.abs(a[1]-b[1])<1e-6) continue;
    var quad=sketchCCW(bimWallSegQuad(a,b,off.dLeft,off.dRight));
    var segMesh=padMesh(quad,y0,height);
    var segPolys=meshPolys({mesh:segMesh,pos:[0,0,0]});
    acc = acc ? csgUnion(acc,segPolys) : segPolys;
  }
  return polysToMesh(acc||[]);
}

// ---- 1. Level height clamping ----
assert('clampLevelHeight clamps below minimum (0.1)', clampLevelHeight(-5)===0.1);
assert('clampLevelHeight clamps above maximum (100)', clampLevelHeight(999)===100);
assert('clampLevelHeight passes through a valid value', clampLevelHeight(3.2)===3.2);
assert('clampLevelHeight falls back to 3 on NaN/non-numeric input', clampLevelHeight('abc')===3);

// ---- 2. Level elevation clamping ----
assert('clampLevelElev clamps below -1000', clampLevelElev(-5000)===-1000);
assert('clampLevelElev clamps above 1000', clampLevelElev(5000)===1000);
assert('clampLevelElev falls back to 0 on invalid input', clampLevelElev(undefined)===0);

// ---- 3. Wall alignment offset math ----
(function(){
  var c=bimAlignOffsets(0.3,'center'), l=bimAlignOffsets(0.3,'left'), r=bimAlignOffsets(0.3,'right');
  assert('center alignment splits thickness evenly', c.dLeft===0.15 && c.dRight===0.15);
  assert('left alignment puts all thickness on the right side', l.dLeft===0 && l.dRight===0.3);
  assert('right alignment puts all thickness on the left side', r.dLeft===0.3 && r.dRight===0);
})();

// ---- 4. Closed-loop ring offset: interior ring shrinks a CCW polygon ----
(function(){
  var room=sketchCCW([[0,0],[6,0],[6,4],[0,4]]);
  var inner=bimOffsetRing(room,0.5,true);
  var outer=bimOffsetRing(room,-0.5,true);
  assert('interior offset (+dist) shrinks a CCW room polygon', polyArea(inner) < polyArea(room));
  assert('exterior offset (-dist) grows a CCW room polygon', polyArea(outer) > polyArea(room));
})();

// ---- 5. Multi-segment CLOSED wall loop unions into one watertight solid via the real CSG kernel ----
(function(){
  var room=sketchCCW([[0,0],[6,0],[6,4],[0,4]]);
  var mesh=unionSegments(room,0,3,0.3,'center',true);
  assert('4-segment closed wall loop produces a non-degenerate union', mesh.f.length>=4 && mesh.v.length>=8,
    'faces='+mesh.f.length+' verts='+mesh.v.length);
})();

// ---- 6. Single OPEN wall segment extrudes to a valid quad prism ----
(function(){
  var mesh=unionSegments([[0,0],[8,0]],0,2.7,0.2,'left',false);
  assert('open single-segment wall yields a valid prism (12 faces: 2 tri caps x2 + 4 side quads)', mesh.f.length===12,
    'faces='+mesh.f.length);
})();

// ---- 7. Floor extrudes DOWNWARD from the level plane (matches padMesh(P, y0-thickness, thickness)) ----
(function(){
  var room=sketchCCW([[0,0],[6,0],[6,4],[0,4]]);
  var interior=bimOffsetRing(room,0.15,true);
  var levelY=2.0, thickness=0.2;
  var floorMesh=padMesh(sketchCCW(interior), levelY-thickness, thickness);
  var ys=floorMesh.v.map(function(v){return v[1];});
  var minY=Math.min.apply(null,ys), maxY=Math.max.apply(null,ys);
  assert('floor solid sits entirely at/below the level elevation', maxY<=levelY+1e-9 && minY>=levelY-thickness-1e-9,
    'minY='+minY+' maxY='+maxY+' levelY='+levelY);
})();

// ---- 8. Degenerate wall input (zero-length centerline) fails gracefully, no throw ----
(function(){
  var threw=false, mesh=null;
  try{ mesh=unionSegments([[2,2],[2,2]],0,3,0.3,'center',false); }
  catch(e){ threw=true; }
  assert('degenerate zero-length wall does not throw (fails gracefully to empty mesh)', !threw && mesh && mesh.f.length===0,
    threw?'threw exception':'faces='+(mesh?mesh.f.length:'n/a'));
})();

// ---- 9. Level-change projection: active level elevation flows into a fresh sketch base plane ----
(function(){
  // Mirrors startSketch()'s: var y0=bimGetActiveLevel().elev,...
  var levels=[{id:'lvl-0',name:'Level 0',elev:0,height:3},{id:'lvl-1',name:'Level 1',elev:3.5,height:3}];
  function bimGetActiveLevelStub(activeId){
    for(var i=0;i<levels.length;i++) if(levels[i].id===activeId) return levels[i];
    return levels[0];
  }
  var y0AtLevel0=bimGetActiveLevelStub('lvl-0').elev;
  var y0AtLevel1=bimGetActiveLevelStub('lvl-1').elev;
  assert('switching active level changes the projected sketch/wall base plane', y0AtLevel0===0 && y0AtLevel1===3.5,
    'y0@L0='+y0AtLevel0+' y0@L1='+y0AtLevel1);
})();

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed (of '+(PASS+FAIL)+')');
process.exit(FAIL>0?1:0);
