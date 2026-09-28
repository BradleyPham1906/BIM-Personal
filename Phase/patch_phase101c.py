"""patch_phase101c.py -- __acad3dV101: Tag Room is reachable, and so is Tag All.

The ribbon has shown "Tag Room" since the V70 shell, GREYED, listed in A3DR_UNIMPL as a command
Revit has and this app did not. It is implemented now, so it leaves that list (law 1: a greyed
button for a command that works is a lie in the other direction). It is wired in every place a
command is reached from -- ribbon (three panels already name it), command line and palette
(ROOMTAG / RT, TAGALLROOMS / TAGALL), and the drawing prompt -- and Tag All Rooms joins it on
the Room & Area and Tag panels.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '1e4beca96e6a96903cfcc6974c073d93eaae9f625bcc5f46568c20818890fbd0'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""    }else if(sk.tool==='room'){
      var roomY=sk.y;""",
     """    }else if(sk.tool==='roomtag'){   /* __acad3dV101: stays live for the next room */
      bimTagRoomAt([gx,gz]);
    }else if(sk.tool==='room'){
      var roomY=sk.y;"""),
    ("""    if(sk.tool==='hatch')return 'Pick an internal point to hatch (Escape when finished):'; /* __acad3dV96 */""",
     """    if(sk.tool==='roomtag')return 'Select a room to tag (Escape when finished):';   /* __acad3dV101 */
    if(sk.tool==='hatch')return 'Pick an internal point to hatch (Escape when finished):'; /* __acad3dV96 */"""),
    ("""leader:'Leader'};""", """leader:'Leader',roomtag:'Tag Room'};"""),
    ("""    'bim:tagroom':1,'bim:tagcat':1,'bim:linkcad':1,""",
     """    'bim:tagcat':1,'bim:linkcad':1,   /* __acad3dV101: bim:tagroom implemented */"""),
    ("""    if(act==='bim:room'){startRoomTool();return;}""",
     """    if(act==='bim:room'){startRoomTool();return;}
    if(act==='bim:tagroom'){startRoomTagTool();return;}       /* __acad3dV101 */
    if(act==='bim:tagallrooms'){bimTagAllRooms();return;}     /* __acad3dV101 */"""),
    ("""    'bim:tagroom':ric('<path d="M4 4h9l7 7-9 9-7-7z"/><circle cx="9" cy="9" r="1.6"/>'),""",
     """    'bim:tagroom':ric('<path d="M4 4h9l7 7-9 9-7-7z"/><circle cx="9" cy="9" r="1.6"/>'),
    'bim:tagallrooms':ric('<path d="M3 6h7l5 5-7 7-5-5z"/><path d="M11 4h5l5 5-5 5"/>'),   /* __acad3dV101 */"""),
    ("""      {t:'Room & Area',small:['bim:room','bim:tagroom']},""",
     """      {t:'Room & Area',small:['bim:room','bim:tagroom','bim:tagallrooms']},"""),
    ("""      {t:'Tag',small:['bim:tagroom','bim:tagcat']}""",
     """      {t:'Tag',small:['bim:tagroom','bim:tagallrooms','bim:tagcat']}"""),
    ("""      'bim:tagroom':'Tag Room','bim:tagcat':'Tag by Category',""",
     """      'bim:tagroom':'Tag Room','bim:tagallrooms':'Tag All Rooms','bim:tagcat':'Tag by Category',"""),
    ("""    room:function(){startRoomTool();},""",
     """    room:function(){startRoomTool();},
    roomtag:function(){startRoomTagTool();},          /* __acad3dV101 */
    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */"""),
    ("""    ['ROOM',['RM'],'room','Tag a closed region as a room'],""",
     """    ['ROOM',['RM'],'room','Make a room from an enclosed region'],
    ['ROOMTAG',['RT','TAGROOM'],'roomtag','Tag a room with its number and name'],
    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
