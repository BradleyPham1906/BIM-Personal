"""patch_phase99i.py -- __acad3dV99: rename the floor test export 99h shadowed.

__a3dFloorAt already exists further down the file (a different signature), and a later
definition wins, so 99h's export was dead on arrival. Renamed to __a3dFloorOnRegionAt. This
script also asserts that NO export it names exists twice, so the check that caught it is now
part of the patch rather than left to the suite.
"""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = '0e345e6e3a37075892ea084c125085b9371179db2bc416116f43c5e50b3182c7'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = """  window.__a3dFloorAt=function(pt,y,thk){
    var b=bimFindRoomBoundaryAt(pt,y||0);"""
NEW = """  window.__a3dFloorOnRegionAt=function(pt,y,thk){
    var b=bimFindRoomBoundaryAt(pt,y||0);"""
assert txt.count(OLD) == 1
assert txt.count('window.__a3dFloorOnRegionAt=') == 0
txt = txt.replace(OLD, NEW, 1)
for name in ['__a3dFloorOnRegionAt', '__a3dGraphRelationsOf', '__a3dRegenerateRegions',
             '__a3dIsRegionDep', '__a3dRegionOf', '__a3dFollowsText', '__a3dFloorAt']:
    n = len(re.findall(r'window\.' + re.escape(name) + r'\s*=', txt))
    assert n == 1, '%s defined %d times' % (name, n)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
