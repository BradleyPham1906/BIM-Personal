"""patch_phase125c.py -- V125: the frame solve.

The direct stiffness method for a 3D frame, as any structural analysis text sets it out (McGuire,
Gallagher and Ziemian, Matrix Structural Analysis, ch. 4-5): six degrees of freedom a node, the 12 x 12
stiffness of a prismatic member in its own axes, turned into the model's axes, assembled, and solved.

  - Nodes are numbered by reverse Cuthill-McKee, so the stiffness is a narrow band, and the band is
    factored by Cholesky: the work grows with the model, not with its square.
  - A pinned beam end is a released rotation: the member's stiffness and fixed-end forces are
    condensed on it (k* = kaa - kab kbb^-1 kba), so the end carries no moment, and the end's own
    rotation is recovered afterwards for the deflected shape.
  - A load between the nodes enters as its fixed-end forces (uniform and point loads, both planes and
    axial); a member's end forces are its stiffness times its end displacements plus those fixed-end
    forces, so the forces inside it are exact for the loads it carries.
  - A model that cannot stand -- no supports, a column standing on nothing, a mechanism -- makes a
    pivot vanish. That is refused with the node and the direction it can move in, never answered with
    numbers that are not numbers.
  - Along each member, at twenty points a piece, at every point load and wherever a shear passes
    through zero (where a moment peaks): axial force, both shears,
    both moments, torsion, and the deflection (the end movements joined by cubic Hermite functions,
    plus the fixed-end deflection of the loads it carries -- exact for these loads).
  - Equilibrium is checked, not assumed: the reactions against everything applied.

Sign conventions, stated where they are read: axial force positive in tension; Mz positive sagging
(tension on the member's -y face -- the bottom of a beam); deflection in metres, in the model's axes."""
NAME = 'patch_phase125c.py'
BASE = '5fda0566956014d6017dcfc239559570a96375d4f65d350e3586c48d24eafbf1'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  function bimToggleTrib(){
""", r"""  /* ================= __acad3dV125: the frame solve (direct stiffness) ================= */
  /* A prismatic member's stiffness in its own axes; dofs u v w rx ry rz at each end. */
  function bimFrameKLocal(e){
    var L=e.L,E=e.E,G=e.G,A=e.sec.A,Iy=e.sec.Iy,Iz=e.sec.Iz,J=e.sec.J,k=[],i,j;
    for(i=0;i<12;i++){k.push([]);for(j=0;j<12;j++)k[i].push(0);}
    var a=E*A/L,t=G*J/L,z1=12*E*Iz/(L*L*L),z2=6*E*Iz/(L*L),z3=4*E*Iz/L,z4=2*E*Iz/L;
    var y1=12*E*Iy/(L*L*L),y2=6*E*Iy/(L*L),y3=4*E*Iy/L,y4=2*E*Iy/L;
    function s(r,c,v){k[r][c]=v;k[c][r]=v;}
    s(0,0,a);s(0,6,-a);s(6,6,a);
    s(3,3,t);s(3,9,-t);s(9,9,t);
    s(1,1,z1);s(1,5,z2);s(1,7,-z1);s(1,11,z2);s(5,5,z3);s(5,7,-z2);s(5,11,z4);s(7,7,z1);s(7,11,-z2);s(11,11,z3);
    s(2,2,y1);s(2,4,-y2);s(2,8,-y1);s(2,10,-y2);s(4,4,y3);s(4,8,y2);s(4,10,y4);s(8,8,y1);s(8,10,y2);s(10,10,y3);
    return k;
  }
  function bimFrameRot(e){return [e.ax.ex,e.ax.ey,e.ax.ez];}
  /* local = R global, for a 12-vector (four 3-blocks) */
  function bimFrameToLocal(R,g){
    var l=[],b,i;
    for(b=0;b<4;b++)for(i=0;i<3;i++)l.push(R[i][0]*g[b*3]+R[i][1]*g[b*3+1]+R[i][2]*g[b*3+2]);
    return l;
  }
  function bimFrameToGlobal(R,l){
    var g=[],b,i;
    for(b=0;b<4;b++)for(i=0;i<3;i++)g.push(R[0][i]*l[b*3]+R[1][i]*l[b*3+1]+R[2][i]*l[b*3+2]);
    return g;
  }
  /* The load an element carries, in its own axes: q (kN/m) and point loads {a, P}. */
  function bimFrameElLoad(e,ld){
    var R=bimFrameRot(e);
    function loc(v){return [bimVDot(R[0],v),bimVDot(R[1],v),bimVDot(R[2],v)];}
    return {q:loc(ld.q),pts:ld.pts.map(function(p){return {a:p.a,P:loc(p.P)};})};
  }
  /* Fixed-end forces (the forces the fixed ends put on the member) of those loads, local. */
  function bimFrameFef(e,lq){
    var L=e.L,r=[0,0,0,0,0,0,0,0,0,0,0,0],q=lq.q,i;
    r[0]-=q[0]*L/2;r[6]-=q[0]*L/2;
    r[1]-=q[1]*L/2;r[5]-=q[1]*L*L/12;r[7]-=q[1]*L/2;r[11]+=q[1]*L*L/12;
    r[2]-=q[2]*L/2;r[4]+=q[2]*L*L/12;r[8]-=q[2]*L/2;r[10]-=q[2]*L*L/12;
    for(i=0;i<lq.pts.length;i++){
      var a=lq.pts[i].a,b=L-a,P=lq.pts[i].P,L2=L*L,L3=L2*L;
      r[0]-=P[0]*b/L;r[6]-=P[0]*a/L;
      r[1]-=P[1]*b*b*(3*a+b)/L3;r[5]-=P[1]*a*b*b/L2;r[7]-=P[1]*a*a*(a+3*b)/L3;r[11]+=P[1]*a*a*b/L2;
      r[2]-=P[2]*b*b*(3*a+b)/L3;r[4]+=P[2]*a*b*b/L2;r[8]-=P[2]*a*a*(a+3*b)/L3;r[10]-=P[2]*a*a*b/L2;
    }
    return r;
  }
  /* Gauss-Jordan inverse of a small matrix (a released set is at most four rotations). */
  function bimSmallInv(M){
    var n=M.length,A=M.map(function(r,i){var x=r.slice();for(var j=0;j<n;j++)x.push(i===j?1:0);return x;}),i,j,k;
    for(i=0;i<n;i++){
      var p=i;for(k=i+1;k<n;k++)if(Math.abs(A[k][i])>Math.abs(A[p][i]))p=k;
      if(Math.abs(A[p][i])<1e-300)return null;
      var t=A[i];A[i]=A[p];A[p]=t;
      var d=A[i][i];for(j=0;j<2*n;j++)A[i][j]/=d;
      for(k=0;k<n;k++)if(k!==i){var f=A[k][i];if(f)for(j=0;j<2*n;j++)A[k][j]-=f*A[i][j];}
    }
    return A.map(function(r){return r.slice(n);});
  }
  /* Condense the released dofs out of an element's stiffness and fixed-end forces. Returns the
     condensed pair and what it needs to recover the released rotations. */
  function bimFrameCondense(kl,fef,rel){
    if(!rel||!rel.length)return {k:kl,fef:fef,inv:null};
    var keep=[],i,j,a,b;
    for(i=0;i<12;i++)if(rel.indexOf(i)<0)keep.push(i);
    var kbb=rel.map(function(r){return rel.map(function(c){return kl[r][c];});}),inv=bimSmallInv(kbb);
    if(!inv)return {k:kl,fef:fef,inv:null};
    var k=kl.map(function(r){return r.slice();}),f=fef.slice();
    for(i=0;i<keep.length;i++){
      a=keep[i];
      for(j=0;j<keep.length;j++){
        b=keep[j];var s=0,p,q;
        for(p=0;p<rel.length;p++)for(q=0;q<rel.length;q++)s+=kl[a][rel[p]]*inv[p][q]*kl[rel[q]][b];
        k[a][b]=kl[a][b]-s;
      }
      var sf=0,p2,q2;
      for(p2=0;p2<rel.length;p2++)for(q2=0;q2<rel.length;q2++)sf+=kl[a][rel[p2]]*inv[p2][q2]*fef[rel[q2]];
      f[a]=fef[a]-sf;
    }
    for(i=0;i<rel.length;i++){f[rel[i]]=0;for(j=0;j<12;j++){k[rel[i]][j]=0;k[j][rel[i]]=0;}}
    return {k:k,fef:f,inv:inv,rel:rel,kl:kl,fef0:fef};
  }
  /* Reverse Cuthill-McKee: a node order that keeps the stiffness a narrow band. */
  function bimFrameRcm(nN,els){
    var adj=[],i,seen=[],order=[];
    for(i=0;i<nN;i++){adj.push([]);seen.push(false);}
    for(i=0;i<els.length;i++){
      var a=els[i].n1,b=els[i].n2;
      if(adj[a].indexOf(b)<0)adj[a].push(b);
      if(adj[b].indexOf(a)<0)adj[b].push(a);
    }
    var byDeg=[];for(i=0;i<nN;i++)byDeg.push(i);
    byDeg.sort(function(x,y){return adj[x].length-adj[y].length||x-y;});
    for(var s=0;s<byDeg.length;s++){
      if(seen[byDeg[s]])continue;
      var queue=[byDeg[s]];seen[byDeg[s]]=true;
      while(queue.length){
        var n=queue.shift();order.push(n);
        var nb=adj[n].filter(function(x){return !seen[x];}).sort(function(x,y){return adj[x].length-adj[y].length||x-y;});
        for(i=0;i<nb.length;i++){seen[nb[i]]=true;queue.push(nb[i]);}
      }
    }
    return order.reverse();
  }
  var BIM_DOF_NAMES=['moves along X','moves along Y','moves along Z','turns about X','turns about Y','turns about Z'];
  function bimFrameSolve(model,combo,selfWeight){
    if(!model.els.length)return {error:'There are no columns or beams to analyse'};
    var nN=model.nodes.length,i,j,k,m,e;
    var sup=0;for(i=0;i<nN;i++)if(model.nodes[i].sup)sup++;
    if(!sup)return {error:'Nothing holds the frame up: no column stands on a footing or the lowest level, and no support is set'};
    var ld=bimStructLoads(model,combo,selfWeight);
    /* equation numbers: a restrained dof has none */
    var order=bimFrameRcm(nN,model.els),eq=[],nEq=0;
    for(i=0;i<nN;i++)eq.push([-1,-1,-1,-1,-1,-1]);
    for(k=0;k<order.length;k++){
      var nd=model.nodes[order[k]],fix=nd.sup==='fixed'?6:(nd.sup==='pinned'?3:0);
      for(j=0;j<6;j++)if(j>=fix)eq[order[k]][j]=nEq++;
    }
    function edofs(e){var d=[],j2;for(j2=0;j2<6;j2++)d.push(eq[e.n1][j2]);for(j2=0;j2<6;j2++)d.push(eq[e.n2][j2]);return d;}
    var hb=0;
    for(i=0;i<model.els.length;i++){
      var dd=edofs(model.els[i]).filter(function(x){return x>=0;});
      if(dd.length)hb=Math.max(hb,Math.max.apply(null,dd)-Math.min.apply(null,dd));
    }
    var K=[],F=new Float64Array(nEq);
    for(i=0;i<nEq;i++)K.push(new Float64Array(hb+1));
    var info=[];
    for(i=0;i<model.els.length;i++){
      e=model.els[i];
      var R=bimFrameRot(e),T=[],r,c;
      var lq=bimFrameElLoad(e,ld.el[i]),cond=bimFrameCondense(bimFrameKLocal(e),bimFrameFef(e,lq),e.rel);
      var kl=cond.k,fef=cond.fef;
      /* kg = T' kl T, with T four copies of R */
      var kg=[];
      for(r=0;r<12;r++){kg.push(new Array(12));}
      var tmp=[];
      for(r=0;r<12;r++){tmp.push(new Array(12));for(c=0;c<12;c++){var bc=Math.floor(c/3)*3,cc=c%3,sm=0;
        for(m=0;m<3;m++)sm+=kl[r][bc+m]*R[m][cc];tmp[r][c]=sm;}}
      for(r=0;r<12;r++){var br=Math.floor(r/3)*3,rr=r%3;for(c=0;c<12;c++){var sm2=0;
        for(m=0;m<3;m++)sm2+=R[m][rr]*tmp[br+m][c];kg[r][c]=sm2;}}
      var dofs=edofs(e);
      for(r=0;r<12;r++){if(dofs[r]<0)continue;for(c=0;c<12;c++){if(dofs[c]<dofs[r])continue;K[dofs[r]][dofs[c]-dofs[r]]+=kg[r][c];}}
      var fg=bimFrameToGlobal(R,fef);
      for(r=0;r<12;r++)if(dofs[r]>=0)F[dofs[r]]-=fg[r];
      info.push({R:R,kl:kl,lq:lq,fef:fef,dofs:dofs,cond:cond});
    }
    var nk;
    for(nk in ld.nodal)if(ld.nodal.hasOwnProperty(nk))for(j=0;j<3;j++){var q=eq[+nk][j];if(q>=0)F[q]+=ld.nodal[nk][j];}
    /* banded Cholesky, L stored by row as L[i][i-j] */
    var diag0=new Float64Array(nEq),maxd=0;
    for(i=0;i<nEq;i++){diag0[i]=K[i][0];if(diag0[i]>maxd)maxd=diag0[i];}
    var Lb=[];for(i=0;i<nEq;i++)Lb.push(new Float64Array(hb+1));
    function A(ii,jj){return jj<=ii?(ii-jj<=hb?K[jj][ii-jj]:0):0;}
    var bad=-1;
    for(i=0;i<nEq&&bad<0;i++){
      var j0=Math.max(0,i-hb);
      for(j=j0;j<=i;j++){
        var s=A(i,j),kk;
        for(kk=j0;kk<j;kk++)s-=Lb[i][i-kk]*Lb[j][j-kk];
        if(i===j){
          if(!(s>1e-10*Math.max(diag0[i],1e-12*maxd))||!isFinite(s)){bad=i;break;}
          Lb[i][0]=Math.sqrt(s);
        }else Lb[i][i-j]=s/Lb[j][0];
      }
    }
    if(bad>=0){
      var bn=-1,bd=-1;
      for(i=0;i<nN&&bn<0;i++)for(j=0;j<6;j++)if(eq[i][j]===bad){bn=i;bd=j;break;}
      var near='';
      for(i=0;i<model.els.length&&!near;i++)if(model.els[i].n1===bn||model.els[i].n2===bn)near=model.els[i].name;
      var np=model.nodes[bn]?model.nodes[bn].p:[0,0,0];
      return {error:'The frame is unstable: the node at '+np.map(function(v){return v.toFixed(2);}).join(', ')+
        (near?' ('+near+')':'')+' '+(BIM_DOF_NAMES[bd]||'moves')+' freely. Set a support, or connect it.',node:bn,dof:bd};
    }
    var y=new Float64Array(nEq),x=new Float64Array(nEq);
    for(i=0;i<nEq;i++){var s1=F[i];for(k=Math.max(0,i-hb);k<i;k++)s1-=Lb[i][i-k]*y[k];y[i]=s1/Lb[i][0];}
    for(i=nEq-1;i>=0;i--){var s2=y[i];for(k=i+1;k<=Math.min(nEq-1,i+hb);k++)s2-=Lb[k][k-i]*x[k];x[i]=s2/Lb[i][0];}
    var disp=[];
    for(i=0;i<nN;i++){var dv=[];for(j=0;j<6;j++)dv.push(eq[i][j]>=0?x[eq[i][j]]:0);disp.push(dv);}
    /* member end forces, and what the supports push back with */
    var nodeF=[];for(i=0;i<nN;i++)nodeF.push([0,0,0,0,0,0]);
    var elRes=[];
    for(i=0;i<model.els.length;i++){
      e=model.els[i];var inf=info[i];
      var dgl=disp[e.n1].concat(disp[e.n2]),dl=bimFrameToLocal(inf.R,dgl),f=[];
      for(r=0;r<12;r++){var sf=inf.fef[r];for(c=0;c<12;c++)sf+=inf.kl[r][c]*dl[c];f.push(sf);}
      /* a released end's own rotation: theta = -kbb^-1 (fef_b + kba d_a) */
      if(inf.cond.inv){
        var cd=inf.cond,p3,q3,c3;
        for(p3=0;p3<cd.rel.length;p3++){
          var th=0;
          for(q3=0;q3<cd.rel.length;q3++){
            var rhs=cd.fef0[cd.rel[q3]];
            for(c3=0;c3<12;c3++)if(cd.rel.indexOf(c3)<0)rhs+=cd.kl[cd.rel[q3]][c3]*dl[c3];
            th-=cd.inv[p3][q3]*rhs;
          }
          dl[cd.rel[p3]]=th;
        }
      }
      var fgl=bimFrameToGlobal(inf.R,f);
      for(j=0;j<6;j++){nodeF[e.n1][j]+=fgl[j];nodeF[e.n2][j]+=fgl[6+j];}
      elRes.push({f:f,dl:dl,lq:inf.lq});
    }
    var reactions=[],rs=[0,0,0];
    for(i=0;i<nN;i++){
      if(!model.nodes[i].sup)continue;
      var Rv=nodeF[i].slice(),an=ld.nodal[i]||[0,0,0];
      for(j=0;j<3;j++)Rv[j]-=an[j];
      for(j=0;j<6;j++)if(eq[i][j]>=0)Rv[j]=0;
      reactions.push({node:i,p:model.nodes[i].p,sup:model.nodes[i].sup,by:model.nodes[i].supBy,R:Rv});
      for(j=0;j<3;j++)rs[j]+=Rv[j];
    }
    var errMax=0;for(j=0;j<3;j++)errMax=Math.max(errMax,Math.abs(rs[j]+ld.total[j]));
    var res={combo:combo.name,selfWeight:!!selfWeight,disp:disp,els:elRes,reactions:reactions,
      equilibrium:{load:ld.total.slice(),reaction:rs,err:errMax},members:[]};
    for(i=0;i<model.members.length;i++)res.members.push(bimFrameMemberResult(model,res,i));
    return res;
  }
  /* Forces and deflection at x along one element, from its end forces f and its loads. */
  function bimFrameAt(e,er,x){
    var f=er.f,q=er.lq.q,pts=er.lq.pts,L=e.L,i;
    var N=-(f[0]+q[0]*x),Vy=f[1]+q[1]*x,Vz=f[2]+q[2]*x;
    var Mz=-f[5]+f[1]*x+q[1]*x*x/2,My=-(f[4]+f[2]*x+q[2]*x*x/2),Tq=-f[3];
    for(i=0;i<pts.length;i++){
      var a=pts[i].a,P=pts[i].P;
      if(x>a+1e-12){N-=P[0];Vy+=P[1];Vz+=P[2];Mz+=P[1]*(x-a);My-=P[2]*(x-a);}
    }
    /* deflection: Hermite on the end movements, plus the fixed-end deflection of the loads */
    var dl=er.dl,xi=x/L,h1=1-3*xi*xi+2*xi*xi*xi,h2=L*(xi-2*xi*xi+xi*xi*xi),h3=3*xi*xi-2*xi*xi*xi,h4=L*(-xi*xi+xi*xi*xi);
    var u=dl[0]+(dl[6]-dl[0])*xi;
    var v=h1*dl[1]+h2*dl[5]+h3*dl[7]+h4*dl[11];
    var w=h1*dl[2]-h2*dl[4]+h3*dl[8]-h4*dl[10];
    var EIz=e.E*e.sec.Iz,EIy=e.E*e.sec.Iy;
    v+=q[1]*x*x*(L-x)*(L-x)/(24*EIz);w+=q[2]*x*x*(L-x)*(L-x)/(24*EIy);
    for(i=0;i<pts.length;i++){
      var aa=pts[i].a,bb=L-aa,PP=pts[i].P,L3=L*L*L,fp;
      if(x<=aa)fp=x*x*(3*aa*L-(3*aa+bb)*x)*bb*bb/(6*L3);
      else{var xr=L-x;fp=xr*xr*(3*bb*L-(3*bb+aa)*xr)*aa*aa/(6*L3);}
      v+=PP[1]*fp/EIz;w+=PP[2]*fp/EIy;
    }
    return {N:N,Vy:Vy,Vz:Vz,Mz:Mz,My:My,T:Tq,u:u,v:v,w:w};
  }
  /* A member's results: the extremes along it, sampled at twenty points a piece and at every point
     load; its deflection measured from the line joining its moved ends, and its largest movement. */
  function bimFrameMemberResult(model,res,mi){
    var m=model.members[mi],out={id:m.id,name:m.name,kind:m.kind,L:m.L,N:[0,0],V:0,Mz:{v:0,at:0},My:{v:0,at:0},T:0,dmax:0,drel:0,samples:[]};
    var k,s,first=true;
    var d1=res.disp[m.n1],d2=res.disp[m.n2];
    for(k=0;k<m.els.length;k++){
      var e=model.els[m.els[k]],er=res.els[m.els[k]],xs=[],i;
      for(i=0;i<=20;i++)xs.push(e.L*i/20);
      for(i=0;i<er.lq.pts.length;i++)xs.push(er.lq.pts[i].a);
      xs.sort(function(a,b){return a-b;});
      /* and where a shear passes through zero -- where the moment peaks between loads -- so the
         extreme reported is the extreme, not the nearest sample to it */
      var qv=er.lq.q,zs=[];
      for(i=0;i+1<xs.length;i++){
        var x0=xs[i],x1=xs[i+1];
        if(x1-x0<1e-9)continue;
        var r0=bimFrameAt(e,er,x0+(x1-x0)*1e-9);
        if(Math.abs(qv[1])>1e-12){var zy=x0+(x1-x0)*1e-9-r0.Vy/qv[1];if(zy>x0&&zy<x1)zs.push(zy);}
        if(Math.abs(qv[2])>1e-12){var zz=x0+(x1-x0)*1e-9-r0.Vz/qv[2];if(zz>x0&&zz<x1)zs.push(zz);}
      }
      xs=xs.concat(zs).sort(function(a,b){return a-b;});
      for(i=0;i<xs.length;i++){
        var x=xs[i],r=bimFrameAt(e,er,x),sm=e.s0+x,R=bimFrameRot(e);
        var gd=[R[0][0]*r.u+R[1][0]*r.v+R[2][0]*r.w,R[0][1]*r.u+R[1][1]*r.v+R[2][1]*r.w,R[0][2]*r.u+R[1][2]*r.v+R[2][2]*r.w];
        if(first||r.N>out.N[1])out.N[1]=r.N;
        if(first||r.N<out.N[0])out.N[0]=r.N;
        first=false;
        var vv=Math.sqrt(r.Vy*r.Vy+r.Vz*r.Vz);if(vv>out.V)out.V=vv;
        if(Math.abs(r.Mz)>Math.abs(out.Mz.v))out.Mz={v:r.Mz,at:sm};
        if(Math.abs(r.My)>Math.abs(out.My.v))out.My={v:r.My,at:sm};
        if(Math.abs(r.T)>out.T)out.T=Math.abs(r.T);
        var mag=bimVLen(gd);if(mag>out.dmax)out.dmax=mag;
        /* movement across the line joining the member's moved ends */
        var t2=sm/m.L,ch=[d1[0]+(d2[0]-d1[0])*t2,d1[1]+(d2[1]-d1[1])*t2,d1[2]+(d2[2]-d1[2])*t2];
        var rel=bimVSub(gd,ch),along=bimVDot(rel,m.ax.ex);
        var tr=bimVLen(bimVSub(rel,[m.ax.ex[0]*along,m.ax.ex[1]*along,m.ax.ex[2]*along]));
        if(tr>out.drel)out.drel=tr;
        out.samples.push({s:sm,N:r.N,Mz:r.Mz,My:r.My,Vy:r.Vy,d:gd});
      }
    }
    return out;
  }
  function bimToggleTrib(){
""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
