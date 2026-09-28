"""patch_phase125f.py -- V125: the hooks the suite reads the analysis through, and the marker.

Each returns plain data -- the model, a solve, what the display drew -- so the suite asserts on
numbers, never on how the screen looks."""
NAME = 'patch_phase125f.py'
BASE = '6c8e150b66cb4dc41753d57e1a30295d3c09eaa1d1f9679872b33d50e0a0780b'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  window.__acad3dV124='librarykinds,""", """  /* __acad3dV125: the analysis, read as data */
  window.__a3dStructModel=function(){
    var m=bimAnalyticalModel();
    return {nodes:m.nodes.map(function(n){return {p:n.p.slice(),sup:n.sup,why:n.supWhy};}),
      els:m.els.map(function(e){return {member:e.memberId,name:e.name,kind:e.kind,n1:e.n1,n2:e.n2,L:e.L,rel:e.rel.slice(),
        E:e.E,G:e.G,A:e.sec.A,Iy:e.sec.Iy,Iz:e.sec.Iz,J:e.sec.J,rho:e.rho,ey:e.ax.ey.slice()};}),
      notAnalysed:JSON.parse(JSON.stringify(m.notAnalysed)),skipped:JSON.parse(JSON.stringify(m.skipped))};
  };
  window.__a3dStructSolve=function(combo,selfWeight){
    var c=bimCombo(combo||A3D_STRUCT.combo);
    if(!c)return {error:'no such combination'};
    var r=bimFrameSolve(bimAnalyticalModel(),c,selfWeight===undefined?A3D_STRUCT.selfWeight:!!selfWeight);
    if(r.error)return {error:r.error,node:r.node,dof:r.dof};
    return JSON.parse(JSON.stringify({combo:r.combo,disp:r.disp,reactions:r.reactions,equilibrium:r.equilibrium,
      members:r.members.map(function(m){return {id:m.id,name:m.name,kind:m.kind,L:m.L,N:m.N,V:m.V,Mz:m.Mz,My:m.My,T:m.T,dmax:m.dmax,drel:m.drel,
        samples:m.samples.map(function(s){return {s:s.s,N:s.N,Mz:s.Mz,My:s.My,Vy:s.Vy};})};})}));
  };
  window.__a3dStructSettings=function(patch){
    var k;if(patch)for(k in patch)if(patch.hasOwnProperty(k)&&k!=='res')A3D_STRUCT[k]=patch[k];
    return {combo:A3D_STRUCT.combo,selfWeight:A3D_STRUCT.selfWeight,show:A3D_STRUCT.show,diagram:A3D_STRUCT.diagram,
      deflected:A3D_STRUCT.deflected,current:!!bimStructCurrent(),error:A3D_STRUCT.res&&A3D_STRUCT.res.error||null};
  };
  window.__a3dStructEditFor=function(id,st){
    var o=objById(id);if(!bimIsFrameMember(o))return false;
    bimStructEdit(o,function(s){var k;for(k in s)if(s.hasOwnProperty(k))delete s[k];for(k in st)if(st.hasOwnProperty(k))s[k]=JSON.parse(JSON.stringify(st[k]));});
    return true;
  };
  window.__a3dStructOf=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(bimStructOf(o))):null;};
  window.__a3dStructDrawn=function(){paint();return A3D.lastStructDrawn?JSON.parse(JSON.stringify(A3D.lastStructDrawn)):null;};
  window.__a3dCombos=function(){return BIM_COMBOS.map(function(c){return c.name;});};
  window.__acad3dV125='analyticalmodel,nodemerge,membersplit,rectsection,materialmodulus,supports,pinnedends,'+
    'loadcases,selfweight,lineload,pointload,lateralload,combinations,directstiffness,rcmband,cholesky,'+
    'unstablerefused,equilibrium,memberforces,shearzero,deflection,analysisdisplay,stale,analyzeoff,'+
    'structuralprops,analysisprops,supportcommand,loadcommand,analyzebutton,memberforceschedule,reactionschedule';
  window.__acad3dV124='librarykinds,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
