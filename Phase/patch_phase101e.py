"""patch_phase101e.py -- __acad3dV101: dead label arithmetic removed; marker and test surface."""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = 'ed410c5f91176813bbc907ee70bda67cdeeee57bc84c63a81e00348998e36389'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
DEAD = """        var cx=0,cz=0,r;
        for(r=0;r<o.pts.length;r++){cx+=o.pts[r][0];cz+=o.pts[r][1];}
        if(!bimRoomTagged(o.id))"""
assert txt.count(DEAD) == 3, txt.count(DEAD)
txt = txt.replace(DEAD, "        if(!bimRoomTagged(o.id))")
OLD = "  window.__acad3dV100='escapekeeps,viewchangekeeps,newcommandkeeps,plineenteropen,plinetwopoints';"
assert txt.count(OLD) == 1
NEW = OLD + """
  /* __acad3dV101: room data and room tags. */
  window.__a3dTagRoomAt=function(pt){var t=bimTagRoomAt(pt);return t?t.id:null;};
  window.__a3dTagAllRooms=bimTagAllRooms;
  window.__a3dSetRoomField=function(id,k,v){return bimSetRoomField(objById(id),k,v);};
  window.__a3dNextRoomNumber=bimNextRoomNumber;
  window.__a3dRoomTagText=function(id){var o=objById(id);return o?bimRoomTagText(o):null;};
  window.__a3dRoomTagged=bimRoomTagged;
  window.__acad3dV101='roomdata,roomnumbering,roomtag,tagall,taglayout,tagfollowsmove,tagdeletedwithroom,orphansweep,exportlabels';"""
txt = txt.replace(OLD, NEW, 1)
for name in ['__a3dTagRoomAt','__a3dTagAllRooms','__a3dSetRoomField','__a3dNextRoomNumber','__a3dRoomTagText','__a3dRoomTagged']:
    n = len(re.findall(r'window\.' + re.escape(name) + r'\s*=', txt))
    assert n == 1, '%s defined %d times' % (name, n)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
