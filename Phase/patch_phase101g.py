"""patch_phase101g.py -- __acad3dV101: Tag All says the right thing when there are no rooms.

With no rooms on the level, Tag All said every room was already tagged -- true of an empty set,
and no help. It now says there are no rooms to tag.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '0f1c37d5908a7081c6693b8e3f188aa233c90b0b4826cbb52a50383c70a1d0bb'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""    var todo=[],i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||!o.pts||o.pts.length<3)continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(!bimRoomTagged(o.id))todo.push(o);
    }
    if(!todo.length){""",
     """    var todo=[],i,o,seen=0;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||!o.pts||o.pts.length<3)continue;
      if(bimObjectLevelId(o)&&bimObjectLevelId(o)!==A3D.activeLevel)continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      seen++;
      if(!bimRoomTagged(o.id))todo.push(o);
    }
    if(!seen){a3dToast('There are no rooms on '+bimGetActiveLevel().name+' to tag');return [];}
    if(!todo.length){"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
