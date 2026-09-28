"""patch_phase126a.py -- V126: a section profile -- its outline, its properties, its solid.

PIPELINE, Track B item 2: "Section-profile library -- steel sections, reinforcement, bolt patterns."
V125 treated every member as a solid rectangle (bimRectSection). A profile is a shape with
dimensions, in the member's own y-z plane (y the depth direction -- up in a beam, the width direction
in a column -- z across it):

  rect     b (across), d (deep)
  circle   D
  hss      B (across), H (deep), t -- a rectangular hollow section
  pipe     D, t
  ibeam    d, bf, tf, tw -- W shapes and IPE
  channel  d, bf, tf, tw -- its back (the web) on one side

Its properties are computed from those dimensions, exact for the idealised shape (fillets and
rounded corners are not modelled, and every read-out says so): A, Iz (bending in its y direction),
Iy, and J -- the Saint-Venant series for a rectangle, pi D^4/32 for a round, Bredt's 4 Am^2 t / p for a
thin closed wall, the sum of b t^3 / 3 for an open section. A channel's centroid is off its back; the
outline is placed so the centroid is on the member's line. Its shear centre is not modelled, and
angles are left out: their principal axes lie across the legs.

No tabulated property is bundled: a section's name and nominal dimensions are facts, and everything
else follows from them -- one reader of a profile, so the solid, the analysis and the read-out cannot
disagree (law 3).

The solid is the profile swept along the member (bimSweepMesh): side faces along every edge, the
ends capped -- by ear clipping for an outline, by a ring for a hollow section -- and turned outward
by its own signed volume, so it is closed and faces out whichever way the outline runs."""
NAME = 'patch_phase126a.py'
BASE = '43c6439d714639197131a7d8a49ddfa99bd890619339f5d03d2b86c8e559307b'
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


rep("""  function bimBuildBeamGeometry(p1,p2,topY,w,dep){""", r"""  /* ================= __acad3dV126: section profiles ================= */
  var BIM_PROFILE_SHAPES={rect:'Rectangle',circle:'Round',hss:'Rectangular hollow (HSS)',pipe:'Pipe',ibeam:'I (W, IPE)',channel:'Channel'};
  var BIM_ROUND_N=32;
  /* Is a profile one this app can build and analyse? null when it is, the reason when not. */
  function bimProfileProblem(p){
    if(!p||!BIM_PROFILE_SHAPES[p.shape])return 'not a known section shape';
    var need={rect:['b','d'],circle:['D'],hss:['B','H','t'],pipe:['D','t'],ibeam:['d','bf','tf','tw'],channel:['d','bf','tf','tw']}[p.shape],i;
    for(i=0;i<need.length;i++)if(!(p[need[i]]>0))return 'its '+need[i]+' must be a positive length';
    if(p.shape==='hss'&&!(2*p.t<Math.min(p.B,p.H)))return 'its walls meet: 2t must be less than B and H';
    if(p.shape==='pipe'&&!(2*p.t<p.D))return 'its wall fills it: 2t must be less than D';
    if((p.shape==='ibeam'||p.shape==='channel')&&!(2*p.tf<p.d&&p.tw<p.bf))return 'its flanges or web do not fit its depth and width';
    return null;
  }
  /* The profile's centroidal properties, in m and m^4. y is its depth direction, z across it. */
  function bimProfileProps(p){
    var A,Iz,Iy,J,zc=0,PI=Math.PI;
    if(p.shape==='rect'){
      var s=bimRectSection(p.d,p.b);A=s.A;Iz=s.Iz;Iy=s.Iy;J=s.J;
    }else if(p.shape==='circle'){
      A=PI*p.D*p.D/4;Iz=Iy=PI*Math.pow(p.D,4)/64;J=PI*Math.pow(p.D,4)/32;
    }else if(p.shape==='pipe'){
      var di=p.D-2*p.t;
      A=PI*(p.D*p.D-di*di)/4;Iz=Iy=PI*(Math.pow(p.D,4)-Math.pow(di,4))/64;J=2*Iz;
    }else if(p.shape==='hss'){
      var bi=p.B-2*p.t,hi=p.H-2*p.t,Am=(p.B-p.t)*(p.H-p.t),per=2*((p.B-p.t)+(p.H-p.t));
      A=p.B*p.H-bi*hi;Iz=(p.B*p.H*p.H*p.H-bi*hi*hi*hi)/12;Iy=(p.H*p.B*p.B*p.B-hi*bi*bi*bi)/12;
      J=4*Am*Am*p.t/per;
    }else{
      var hw=p.d-2*p.tf;
      A=2*p.bf*p.tf+hw*p.tw;
      Iz=(p.bf*p.d*p.d*p.d-(p.bf-p.tw)*hw*hw*hw)/12;
      J=(2*p.bf*p.tf*p.tf*p.tf+hw*p.tw*p.tw*p.tw)/3;
      if(p.shape==='ibeam')Iy=(2*p.tf*p.bf*p.bf*p.bf+hw*p.tw*p.tw*p.tw)/12;
      else{
        /* the back of the channel at z = 0, its flanges running to z = bf */
        zc=(2*p.bf*p.tf*p.bf/2+hw*p.tw*p.tw/2)/A;
        Iy=2*(p.tf*p.bf*p.bf*p.bf/12+p.bf*p.tf*Math.pow(p.bf/2-zc,2))+(hw*p.tw*p.tw*p.tw/12+hw*p.tw*Math.pow(p.tw/2-zc,2));
      }
    }
    return {A:A,Iz:Iz,Iy:Iy,J:J,zc:zc};
  }
  /* The outline -- and the hole of a hollow section -- as [y, z] points about the centroid.
     A round is a 32-gon: its solid is that polygon, its properties the true circle's. */
  function bimProfileLoops(p){
    var out,inn=null,i,hd,hb;
    function ring(r){var a=[];for(var k=0;k<BIM_ROUND_N;k++){var th=2*Math.PI*k/BIM_ROUND_N;a.push([r*Math.cos(th),r*Math.sin(th)]);}return a;}
    if(p.shape==='rect'){hd=p.d/2;hb=p.b/2;out=[[-hd,-hb],[hd,-hb],[hd,hb],[-hd,hb]];}
    else if(p.shape==='circle')out=ring(p.D/2);
    else if(p.shape==='pipe'){out=ring(p.D/2);inn=ring(p.D/2-p.t);}
    else if(p.shape==='hss'){
      hd=p.H/2;hb=p.B/2;out=[[-hd,-hb],[hd,-hb],[hd,hb],[-hd,hb]];
      inn=[[-hd+p.t,-hb+p.t],[hd-p.t,-hb+p.t],[hd-p.t,hb-p.t],[-hd+p.t,hb-p.t]];
    }else if(p.shape==='ibeam'){
      var D2=p.d/2,B2=p.bf/2,W2=p.tw/2,F=D2-p.tf;
      out=[[-D2,-B2],[-D2,B2],[-F,B2],[-F,W2],[F,W2],[F,B2],[D2,B2],[D2,-B2],[F,-B2],[F,-W2],[-F,-W2],[-F,-B2]];
    }else{
      var zc=bimProfileProps(p).zc,C2=p.d/2,G=C2-p.tf;
      out=[[-C2,0],[-C2,p.bf],[-G,p.bf],[-G,p.tw],[G,p.tw],[G,p.bf],[C2,p.bf],[C2,0]].map(function(q){return [q[0],q[1]-zc];});
    }
    return {outer:out,inner:inn};
  }
  /* the profile's extent: its depth along y and width across z */
  function bimProfileExtent(p){
    var L=bimProfileLoops(p).outer,mn=[Infinity,Infinity],mx=[-Infinity,-Infinity],i;
    for(i=0;i<L.length;i++){mn[0]=Math.min(mn[0],L[i][0]);mn[1]=Math.min(mn[1],L[i][1]);mx[0]=Math.max(mx[0],L[i][0]);mx[1]=Math.max(mx[1],L[i][1]);}
    return {depth:mx[0]-mn[0],width:mx[1]-mn[1],ymax:mx[0]};
  }
  function bimLoopArea(L){var a=0,i;for(i=0;i<L.length;i++){var q=L[(i+1)%L.length];a+=L[i][0]*q[1]-q[0]*L[i][1];}return a/2;}
  /* Sweep a profile along a length: place(y, z, s) is the world point at (y, z) on the profile, s
     along the member. Closed, and turned outward by its signed volume. */
  function bimSweepMesh(p,len,place){
    var lp=bimProfileLoops(p),out=lp.outer.slice(),inn=lp.inner?lp.inner.slice():null,v=[],f=[],i,j,n,m;
    if(bimLoopArea(out)<0)out.reverse();
    if(inn&&bimLoopArea(inn)<0)inn.reverse();
    n=out.length;
    for(i=0;i<n;i++)v.push(place(out[i][0],out[i][1],0));
    for(i=0;i<n;i++)v.push(place(out[i][0],out[i][1],len));
    for(i=0;i<n;i++){j=(i+1)%n;f.push([i,j,j+n,i+n]);}
    if(inn){
      m=inn.length;var b=2*n;
      for(i=0;i<m;i++)v.push(place(inn[i][0],inn[i][1],0));
      for(i=0;i<m;i++)v.push(place(inn[i][0],inn[i][1],len));
      for(i=0;i<m;i++){j=(i+1)%m;f.push([b+j,b+i,b+i+m,b+j+m]);}
      /* the ends are rings, outer to inner vertex for vertex */
      for(i=0;i<n;i++){j=(i+1)%n;f.push([j,i,b+i,b+j]);f.push([i+n,j+n,b+j+m,b+i+m]);}
    }else{
      var tris=earClip(out);
      for(i=0;i<tris.length;i++){
        f.push([tris[i][2],tris[i][1],tris[i][0]]);
        f.push([tris[i][0]+n,tris[i][1]+n,tris[i][2]+n]);
      }
    }
    var mesh={v:v,f:f};
    if(bimMeshSignedVolume(mesh)<0)mesh.f=mesh.f.map(function(fc){return fc.slice().reverse();});
    return mesh;
  }
  function bimMeshSignedVolume(m){
    var V=0,i,k;
    for(i=0;i<m.f.length;i++){
      var fc=m.f[i],a=m.v[fc[0]];
      for(k=1;k+1<fc.length;k++){
        var b=m.v[fc[k]],c=m.v[fc[k+1]];
        V+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
      }
    }
    return V;
  }
  function bimBuildBeamGeometry(p1,p2,topY,w,dep){""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
