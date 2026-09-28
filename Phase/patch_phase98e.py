"""patch_phase98e.py -- __acad3dV98: marker and test surface for annotation and grid editing."""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '220db902df7161094400a3bb9c055e3ad355d4a85bcd2d5f4cba0f891696436b'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  window.__acad3dV97='sourcecontract,everydependentfollows,dependentframe,cutsaysso,addvertex,constraintindexshift,chainedsources';"""
NEW = OLD + """
  /* __acad3dV98: annotations and grids can be touched and edited. */
  window.__a3dCreateAngularDim=bimCreateAngularDim;
  window.__a3dCreateRadialDim=bimCreateRadialDim;
  window.__a3dCreateLeader=bimCreateLeader;
  window.__a3dAnnotGripPoints=function(id){
    var o=objById(id),p=o?bimAnnotGripPoints(o):null;
    return p?JSON.parse(JSON.stringify(p)):null;
  };
  window.__a3dSelectedGrid=function(){var g=bimSelectedGrid();return g?g.id:null;};
  window.__a3dSelectGrid=bimSelectGrid;
  window.__a3dRenameGrid=bimRenameGrid;
  window.__a3dSetGridEnds=bimSetGridEnds;
  window.__a3dPickGrid=function(x,y){var g=bimPickGrid(x,y);return g?g.id:null;};
  window.__acad3dV98='edgesource,annotpickfirst,annotallkinds,annotgrips,gridselect,gridgrips,griddrag,griddelete,gridprops';"""

assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
