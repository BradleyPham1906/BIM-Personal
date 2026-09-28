"""patch_phase125a.py -- V125: the analytical model, and where it is held up.

PIPELINE NOW, Track B item 1: "Structural object model -- loads, supports, load combinations,
results." Revit's analytical model is the reference: every physical member has an analytical line,
and the analysis runs on the lines, not on the solids. Here the lines are DERIVED on every call from
the live columns and beams (bimAnalyticalModel) and never stored, so they cannot fall out of step with
the model (law 3).

  - A column is a line up its centre, from its base to its top.
  - A beam is a line along its top -- Revit's default for a beam, which hangs below its level, so the
    beam's line lies in the level plane the columns reach.
  - Ends within 50 mm are one node (V106's tolerance). A node lying on another member's line, within
    the same tolerance, splits that member there, so a beam framing into a column part way up, or a
    secondary beam onto a girder, is connected.
  - A rectangle's section properties: A, both second moments, and J by the Saint-Venant series for a
    rectangle. E and G from the member's material card (E from its modulus, G = E / 2(1 + nu)) --
    the member's own material, else its type's, else Concrete.
  - A beam's ends are Rigid (a moment connection) or Pinned (a shear connection, which carries no
    bending moment): o.bim.struct.ends, Rigid unset. A pinned beam releases both bending rotations at
    both ends; the solve condenses them out of its stiffness.
  - A column's base is a support: Fixed or Pinned as set on it, or Free; unset, it is Fixed when it
    stands on a footing or on the lowest level, and otherwise it stands on whatever it meets there.
  - Walls, floors, roofs and the rest are not in the frame; the model lists them, so an analysis
    never implies it saw them.

Units: kN, m, kPa (kN/m2)."""
NAME = 'patch_phase125a.py'
BASE = '96d2bed3c8eaa0f4e43bd8f38ebbcd0d8d1adbe501491ff1a8ade5d06f8537e4'
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
""", r"""  /* ================= __acad3dV125: the analytical model =================
     Derived on every call from the live columns and beams, never stored: the lines cannot fall out
     of step with the members they stand for. Units kN, m, kPa. */
  var BIM_AN_TOL=0.05;
  var BIM_SUPPORTS=['fixed','pinned','free'];
  /* '210 GPa' -> kN/m2 */
  function bimModulusKPa(s){
    var m=/([0-9]*\.?[0-9]+)\s*(GPa|MPa|kPa)/i.exec(String(s||''));
    if(!m)return null;
    var v=parseFloat(m[1]),u=m[2].toLowerCase();
    return u==='gpa'?v*1e6:(u==='mpa'?v*1e3:v);
  }
  /* the member's own material, else its type's, else Concrete */
  function bimMemberMaterial(o){
    var n=o&&o.materialName||null;
    if(!n&&o&&o.bim&&o.bim.typeId){
      try{var ty=bimFindType(o.bim.typeCat||o.bim.type,o.bim.typeId);if(ty&&ty.params&&ty.params.material)n=ty.params.material;}
      catch(eT){console.warn('[BIM] A member type could not be read',eT);}
    }
    return bimMaterialByName(n||'Concrete')||bimMaterialByName('Concrete');
  }
  /* A rectangle hy deep along the member's local y and hz wide along its local z. J by the
     Saint-Venant series for a rectangle, a the long side and b the short. */
  function bimRectSection(hy,hz){
    var a=Math.max(hy,hz),b=Math.min(hy,hz);
    return {A:hy*hz,Iz:hz*hy*hy*hy/12,Iy:hy*hz*hz*hz/12,
            J:a*b*b*b*(1/3-0.21*(b/a)*(1-Math.pow(b/a,4)/12))};
  }
  function bimVSub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
  function bimVDot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function bimVLen(a){return Math.sqrt(bimVDot(a,a));}
  function bimVCross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function bimVUnit(a){var l=bimVLen(a);return l>1e-12?[a[0]/l,a[1]/l,a[2]/l]:null;}
  /* A member's local axes: x along it; y the reference direction made square to x; z = x cross y. */
  function bimMemberAxes(p1,p2,yRef){
    var ex=bimVUnit(bimVSub(p2,p1));
    if(!ex)return null;
    var y=bimVSub(yRef,[ex[0]*bimVDot(yRef,ex),ex[1]*bimVDot(yRef,ex),ex[2]*bimVDot(yRef,ex)]);
    var ey=bimVUnit(y);
    if(!ey){y=Math.abs(ex[1])<0.9?[0,1,0]:[1,0,0];ey=bimVUnit(bimVSub(y,[ex[0]*bimVDot(y,ex),ex[1]*bimVDot(y,ex),ex[2]*bimVDot(y,ex)]));}
    return {ex:ex,ey:ey,ez:bimVCross(ex,ey)};
  }
  function bimIsFrameMember(o){
    return !!(o&&o.t==='solid'&&o.bim&&(o.bim.type==='column'||o.bim.type==='beam'));
  }
  function bimStructOf(o){
    return (o&&o.bim&&o.bim.struct&&typeof o.bim.struct==='object')?o.bim.struct:{};
  }
  /* The lowest level's elevation: a column that starts there stands on the ground. */
  function bimLowestElev(){
    var i,m=Infinity;
    for(i=0;i<A3D.levels.length;i++)if(isFinite(A3D.levels[i].elev)&&A3D.levels[i].elev<m)m=A3D.levels[i].elev;
    return isFinite(m)?m:0;
  }
  /* A column's base support: what is set on it, or -- unset -- Fixed on a footing or the lowest
     level, and otherwise nothing: it stands on whatever it meets there. */
  function bimColumnSupport(o,baseY,automatic){
    var s=automatic?null:bimStructOf(o).support;
    if(BIM_SUPPORTS.indexOf(s)>=0)return {kind:s==='free'?null:s,set:true};
    if(bimFootingOf(o.id))return {kind:'fixed',set:false,why:'on its footing'};
    if(Math.abs(baseY-bimLowestElev())<=BIM_AN_TOL)return {kind:'fixed',set:false,why:'on the lowest level'};
    return {kind:null,set:false,why:'stands on what it meets'};
  }
  function bimAnalyticalModel(){
    var nodes=[],members=[],els=[],skipped=[],notAnalysed={},i,j,k;
    function nodeAt(p){
      for(var n=0;n<nodes.length;n++){
        var q=nodes[n].p;
        if(Math.abs(q[0]-p[0])<=BIM_AN_TOL&&Math.abs(q[1]-p[1])<=BIM_AN_TOL&&Math.abs(q[2]-p[2])<=BIM_AN_TOL)return n;
      }
      nodes.push({i:nodes.length,p:[p[0],p[1],p[2]],sup:null,supBy:null,supWhy:''});
      return nodes.length-1;
    }
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(!bimIsFrameMember(o)){
        if(o.t==='solid'&&o.bim&&o.bim.type&&o.bim.type!=='opening'){
          var kk=o.bim.type;notAnalysed[kk]=(notAnalysed[kk]||0)+1;
        }
        continue;
      }
      var q=bimObjOffset(o),b=o.bim,p1,p2,yRef,hy,hz;
      if(b.type==='column'){
        if(!b.center||!(b.height>0)||!(b.width>0)||!(b.depth>0)){skipped.push({id:o.id,name:o.name,why:'has no parametric size'});continue;}
        var r=b.rotation||0;
        p1=[b.center[0]+q[0],b.baseY+q[1],b.center[1]+q[2]];
        p2=[p1[0],p1[1]+b.height,p1[2]];
        yRef=[Math.cos(r),0,Math.sin(r)];hy=b.width;hz=b.depth;
      }else{
        if(!b.p1||!b.p2||!(b.width>0)||!(b.depth>0)){skipped.push({id:o.id,name:o.name,why:'has no parametric size'});continue;}
        var ty=(isFinite(b.topY)?b.topY:(b.baseY+b.depth))+q[1];
        p1=[b.p1[0]+q[0],ty,b.p1[1]+q[2]];
        p2=[b.p2[0]+q[0],ty,b.p2[1]+q[2]];
        yRef=[0,1,0];hy=b.depth;hz=b.width;
      }
      var ax=bimMemberAxes(p1,p2,yRef);
      if(!ax){skipped.push({id:o.id,name:o.name,why:'has no length'});continue;}
      var mat=bimMemberMaterial(o),E=bimModulusKPa(mat&&mat.youngsModulus);
      var nu=mat&&isFinite(mat.poissonRatio)?mat.poissonRatio:0.2;
      if(!(E>0)){skipped.push({id:o.id,name:o.name,why:'its material ('+(mat?mat.name:'none')+') has no modulus'});continue;}
      var sec=bimRectSection(hy,hz);
      members.push({id:o.id,name:o.name,kind:b.type,p1:p1,p2:p2,L:bimVLen(bimVSub(p2,p1)),ax:ax,
        n1:nodeAt(p1),n2:nodeAt(p2),sec:sec,E:E,G:E/(2*(1+nu)),rho:mat&&mat.density||0,material:mat?mat.name:'',
        hy:hy,hz:hz,els:[]});
    }
    /* a node on another member's line splits it there */
    for(i=0;i<members.length;i++){
      var m=members[i],on=[];
      for(k=0;k<nodes.length;k++){
        if(k===m.n1||k===m.n2)continue;
        var d=bimVSub(nodes[k].p,m.p1),s=bimVDot(d,m.ax.ex);
        if(s<=BIM_AN_TOL||s>=m.L-BIM_AN_TOL)continue;
        var perp=bimVSub(d,[m.ax.ex[0]*s,m.ax.ex[1]*s,m.ax.ex[2]*s]);
        if(bimVLen(perp)<=BIM_AN_TOL)on.push({n:k,s:s});
      }
      on.sort(function(a,c){return a.s-c.s;});
      var chain=[{n:m.n1,s:0}].concat(on).concat([{n:m.n2,s:m.L}]);
      for(j=0;j+1<chain.length;j++){
        var e={i:els.length,member:i,memberId:m.id,name:m.name,kind:m.kind,n1:chain[j].n,n2:chain[j+1].n,
          s0:chain[j].s,s1:chain[j+1].s,L:chain[j+1].s-chain[j].s,ax:m.ax,sec:m.sec,E:m.E,G:m.G,rho:m.rho};
        /* __acad3dV125: a pinned beam releases both bending rotations at its two ENDS -- the
           pieces between split points stay continuous */
        var rel=[];
        if(m.kind==='beam'&&bimStructOf(objById(m.id)).ends==='pinned'){
          if(j===0)rel.push(4,5);
          if(j+2===chain.length)rel.push(10,11);
        }
        e.rel=rel;
        els.push(e);m.els.push(e.i);
      }
    }
    /* supports: a column base */
    for(i=0;i<members.length;i++){
      if(members[i].kind!=='column')continue;
      var co=objById(members[i].id),sp=bimColumnSupport(co,members[i].p1[1]),nd=nodes[members[i].n1];
      if(sp.kind&&(!nd.sup||sp.kind==='fixed')){nd.sup=sp.kind;nd.supBy=members[i].id;nd.supWhy=sp.set?'set':sp.why;}
    }
    return {nodes:nodes,members:members,els:els,skipped:skipped,notAnalysed:notAnalysed};
  }
  function bimToggleTrib(){
""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
