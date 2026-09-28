"""patch_phase99g.py -- __acad3dV99: keep the seed where the user put it.

Found by the first probe: bimRegionRecord moved the seed to the middle of the new shape after
EVERY trace. A room clicked near its left wall, then split by a new line, came back as the RIGHT
half, because the seed had quietly moved to the centre. Revit keeps a room's location point
where it was placed. The seed is now moved only when it is no longer inside the region the
trace found -- the fallback case, where the old seed landed on or outside the new boundary.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'b24a25d32e31e9defdbb608902fad2da58c70652d1697342a972f61685d5a84a'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = """    var q=bimObjOffset(o),ip=bimInteriorPoint(b.ring),i,allWalls=b.srcIds.length>0,m;
    o.region.members=b.srcIds.slice();
    o.region.sig=b.sig;
    o.region.open=false;
    if(ip)o.region.seed=[ip[0]-q[0],ip[1]-q[2]];"""
NEW = """    var q=bimObjOffset(o),i,allWalls=b.srcIds.length>0,m,ip;
    o.region.members=b.srcIds.slice();
    o.region.sig=b.sig;
    o.region.open=false;
    if(!bimPointInPoly(bimRegionSeedWorld(o),b.ring)){
      ip=bimInteriorPoint(b.ring);
      if(ip)o.region.seed=[ip[0]-q[0],ip[1]-q[2]];
    }"""
assert txt.count(OLD) == 1
txt = txt.replace(OLD, NEW, 1)
OLD2 = """  /* Record what a successful trace found: its members, the plane signature, and a fresh seed
     well inside the new shape, so the next trace does not start from a point on an edge. */"""
NEW2 = """  /* Record what a successful trace found: its members and the plane signature. The seed stays
     where the user put it unless it is no longer inside the region found (then a point inside
     the new shape, so the next trace does not start from a point on an edge). */"""
assert txt.count(OLD2) == 1
txt = txt.replace(OLD2, NEW2, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
