"""patch_phase126e.py -- V126: test hooks and the marker."""
NAME = 'patch_phase126e.py'
BASE = '3262813496098af50fe28a1c4fe567bbdaad477806541051f3e862358d9afa0f'
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


rep("""  window.__acad3dV125='analyticalmodel,""", """  /* __acad3dV126: section profiles */
  window.__a3dProfileProps=function(p){return bimProfileProblem(p)?null:bimProfileProps(p);};
  window.__a3dProfileProblem=function(p){return bimProfileProblem(p);};
  window.__a3dProfileLoops=function(p){return bimProfileProblem(p)?null:bimProfileLoops(p);};
  window.__a3dSweepVolume=function(p,len){return bimMeshSignedVolume(bimSweepMesh(p,len,function(y,z,s){return [s,y,z];}));};
  window.__a3dMeshVolume=function(id){var o=objById(id);return o&&o.mesh?bimMeshSignedVolume(o.mesh):null;};
  window.__a3dMemberSection=function(id){
    var o=objById(id);if(!bimIsFrameMember(o))return null;
    var pf=bimMemberSection(o);
    return {section:JSON.parse(JSON.stringify(pf)),props:bimProfileProblem(pf)?null:bimProfileProps(pf),problem:bimProfileProblem(pf)};
  };
  window.__a3dSectionTypes=function(){
    bimEnsureTypes();var out=[];
    ['column','beam'].forEach(function(c){(A3D.types[c]||[]).forEach(function(ty){
      if(ty.params&&ty.params.profile)out.push({cat:c,id:ty.id,name:ty.name,material:ty.params.material||'',shape:ty.params.profile.shape});});});
    return out;
  };
  window.__a3dTypeParams=function(cat,id){var ty=bimFindType(cat,id);return ty?JSON.parse(JSON.stringify(ty.params)):null;};
  window.__acad3dV126='profileshapes,profileprops,profileloops,sweepmesh,sectioncatalogue,typeseeding,typegroups,'+
    'edittypelocked,beamsection,columnsection,sectionrebuilds,sizelocked,sectionanalysis,sectionprops,assetsections';
  window.__acad3dV125='analyticalmodel,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
