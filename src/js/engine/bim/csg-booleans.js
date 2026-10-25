  // ---- __acad3dV3: CSG solid booleans + pair selection + drag-move ----
  var CSG_EPS=1e-5;
  /* __acad3dV114: published for the chrome outside this engine -- the quick-access bar, the command
     palette, the project tabs and the Start page all toast through it (V120). */
  window.__a3dToast=function(m){return a3dToast(m);};
  function a3dToast(msg){
    try{
      var tx=document.getElementById('a3d-toast');
      if(!tx){
        tx=document.createElement('div');
        tx.id='a3d-toast';
        tx.style.cssText='position:fixed;left:calc((100vw + var(--a3d-left-w,0px)) / 2);transform:translateX(-50%);bottom:16px;background:#1f2733;color:#dfe7f1;border:1px solid #3b4a5e;border-radius:6px;padding:8px 14px;font-size:12px;z-index:99990;opacity:0;transition:opacity .25s;pointer-events:none;';
        /* __acad3dV115: on the page, not inside the drawing area: the Start page sits above the
           drawing area, and a message about what just happened there has to be seen */
        document.body.appendChild(tx);
      }
      /* __acad3dV99: toasts raised in the same turn stack, so a consequence is not hidden
         by the summary of the action that caused it */
      if(a3dToast._same&&tx.textContent){
        var lines=(tx.textContent+'\n'+msg).split('\n');
        tx.textContent=lines.slice(Math.max(0,lines.length-4)).join('\n');
      }else tx.textContent=msg;
      tx.style.whiteSpace='pre-line';
      if(!a3dToast._same){a3dToast._same=true;setTimeout(function(){a3dToast._same=false;},0);}
      tx.style.opacity='1';
      if(a3dToast._t)clearTimeout(a3dToast._t);
      a3dToast._t=setTimeout(function(){tx.style.opacity='0';},2600);
    }catch(e2){}
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
  var BOOLNAMES={union:'Union',cut:'Cut',isect:'Intersect'};
  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
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
  function groundPoint(sx,sy,y0){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),f=H*1.2;
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
