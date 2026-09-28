"""patch_phase99h.py -- __acad3dV99: one floor-profile builder, and a graph read-out for tests.

The Floor tool built its profile inline from the traced boundary. A test that wants a floor on a
region would have had to copy that literal, and a copy is a second answer (law 3). The profile
is now built by bimFloorProfileFrom, which the tool and the test export both call.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '30bc19d4e19dacf92fa2754bbb1fecfe0442ccaa92994370180fbe49b1c4d8f1'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""      openFloorDlg({pts:sketchCCW(flB.pts),y:flB.y,sourceType:flB.sourceType,sourceId:flB.sourceId,
                    region:flB.region||null});   /* __acad3dV97, region __acad3dV99 */""",
     """      openFloorDlg(bimFloorProfileFrom(flB));   /* __acad3dV97, region __acad3dV99 */"""),
    ("""  function buildFloorSolid(prof,thickness,material,lvl){""",
     """  /* __acad3dV99: the profile a floor is built from, from a traced boundary. */
  function bimFloorProfileFrom(b){
    return {pts:sketchCCW(b.pts),y:b.y,sourceType:b.sourceType,sourceId:b.sourceId,
            region:b.region?bimCloneRegion(b.region):null};
  }
  function buildFloorSolid(prof,thickness,material,lvl){"""),
    ("""  window.__a3dFollowsText=function(id){return bimFollowsText(objById(id));};""",
     """  window.__a3dFollowsText=function(id){return bimFollowsText(objById(id));};
  window.__a3dGraphRelationsOf=function(id){return bimGraphRelationsOf(id);};
  window.__a3dFloorAt=function(pt,y,thk){
    var b=bimFindRoomBoundaryAt(pt,y||0);
    if(!b)return null;
    var o=buildFloorSolid(bimFloorProfileFrom(b),thk||0.2,'Concrete Slab',bimGetActiveLevel());
    return o?o.id:null;
  };"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
