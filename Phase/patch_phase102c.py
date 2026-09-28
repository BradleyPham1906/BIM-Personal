"""patch_phase102c.py -- __acad3dV102: the foundation tools are reachable, and scheduled.

The ribbon's Foundation panel has shown "Wall Foundation" and "Slab" greyed as unimplemented since
the V70 shell. Both work now and leave A3DR_UNIMPL (law 1); "Slab" is renamed "Foundation Slab",
which is what it makes; "Isolated Footing" joins them. All four are on the command line too:
FOOTING (FTG), FOOTINGSALL, WALLFOUNDATION (WF), FOUNDATIONSLAB (FS). The footing tools stay live
for the next click, as Revit's do.

Two schedules: Isolated Footings and Wall Foundations, each with its host, its type, its sizes and
its concrete volume -- the quantity a foundation schedule exists to give.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '84c4018817ff4425ecbffed5b18c59c82322f421bf760489db1b507bae36a831'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""    }else if(sk.tool==='roomtag'){   /* __acad3dV101: stays live for the next room */""",
     """    }else if(sk.tool==='footing'){   /* __acad3dV102: stays live */
      var fc=bimColumnAtWorld([gx,gz]);
      if(!fc)a3dToast('Isolated Footing: click a column');else bimAddFootingUnder(fc);
    }else if(sk.tool==='wallfoundation'){   /* __acad3dV102: stays live */
      var fw=bimWallAtWorld([gx,gz]);
      if(!fw)a3dToast('Wall Foundation: click a wall');else bimAddFootingUnder(fw);
    }else if(sk.tool==='foundslab'){   /* __acad3dV102 */
      var fsy=sk.y;
      A3D.sk=null;
      bimFoundationSlabAt([gx,gz],fsy);
    }else if(sk.tool==='roomtag'){   /* __acad3dV101: stays live for the next room */"""),
    ("""    if(sk.tool==='roomtag')return 'Select a room to tag (Escape when finished):';   /* __acad3dV101 */""",
     """    if(sk.tool==='roomtag')return 'Select a room to tag (Escape when finished):';   /* __acad3dV101 */
    if(sk.tool==='footing')return 'Select a column to put a footing under (Escape when finished):';   /* __acad3dV102 */
    if(sk.tool==='wallfoundation')return 'Select a wall to put a foundation under (Escape when finished):';
    if(sk.tool==='foundslab')return 'Pick a point inside the slab boundary:';"""),
    ("""leader:'Leader',roomtag:'Tag Room'};""",
     """leader:'Leader',roomtag:'Tag Room',footing:'Isolated Footing',wallfoundation:'Wall Foundation',foundslab:'Foundation Slab'};"""),
    ("""    'bim:truss':1,'bim:brace':1,'bim:foundwall':1,'bim:foundslab':1,'bim:rebar':1,""",
     """    'bim:truss':1,'bim:brace':1,'bim:rebar':1,   /* __acad3dV102: foundwall and foundslab implemented */"""),
    ("""    'bim:foundslab':ric('<rect x="2" y="12" width="20" height="7"/><path d="M6 12V8M18 12V8"/>'),""",
     """    'bim:foundslab':ric('<rect x="2" y="12" width="20" height="7"/><path d="M6 12V8M18 12V8"/>'),
    'bim:footing':ric('<rect x="4" y="15" width="16" height="5"/><rect x="10" y="4" width="4" height="11"/>'),   /* __acad3dV102 */"""),
    ("""      {t:'Foundation',small:['bim:foundwall','bim:foundslab']},""",
     """      {t:'Foundation',small:['bim:footing','bim:foundwall','bim:foundslab']},"""),
    ("""'bim:foundwall':'Wall Foundation',""", """'bim:foundwall':'Wall Foundation','bim:footing':'Isolated Footing',"""),
    ("""      'bim:foundslab':'Slab',""", """      'bim:foundslab':'Foundation Slab',"""),
    ("""    if(act==='bim:tagroom'){startRoomTagTool();return;}       /* __acad3dV101 */""",
     """    if(act==='bim:tagroom'){startRoomTagTool();return;}       /* __acad3dV101 */
    if(act==='bim:footing'){startFootingTool('column');return;}  /* __acad3dV102 */
    if(act==='bim:foundwall'){startFootingTool('wall');return;}
    if(act==='bim:foundslab'){startFoundationSlabTool();return;}"""),
    ("""    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */""",
     """    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */
    footing:function(){startFootingTool('column');},  /* __acad3dV102 */
    footingall:function(){bimFootingsUnderAllColumns();},
    wallfoundation:function(){startFootingTool('wall');},
    foundslab:function(){startFoundationSlabTool();},"""),
    ("""    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],""",
     """    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],
    ['FOOTING',['FTG'],'footing','Isolated footing under a column'],
    ['FOOTINGSALL',[],'footingall','Footings under every column on the active level'],
    ['WALLFOUNDATION',['WF'],'wallfoundation','Strip footing under a wall'],
    ['FOUNDATIONSLAB',['FS'],'foundslab','Foundation slab in an enclosed region'],"""),
    # schedules
    ("""  function bimBuildColumnSchedule(){""",
     """  /* __acad3dV102 */
  function bimBuildFootingSchedule(kind){
    return A3D.objs.filter(function(o){return bimIsFooting(o)&&o.bim.type===kind;}).map(function(o){
      var h=bimFootingHostOf(o);
      return {name:o.name,type:bimTypeNameOf(o)||'-',host:h?h.name:'(none)',width:o.bim.width,
        length:bimFootingLength(o),thickness:o.bim.thickness,volume:bimFootingVolume(o),
        level:bimLevelName(o.bim.levelId)};
    });
  }
  function bimBuildColumnSchedule(){"""),
    ("""    beam:{label:'Beams',build:bimBuildBeamSchedule,""",
     """    footing:{label:'Isolated Footings',build:function(){return bimBuildFootingSchedule('footing');},cols:[{key:'name',label:'Name'},{key:'type',label:'Type'},{key:'host',label:'Under'},{key:'width',label:'Width (m)',fmt:2},{key:'length',label:'Length (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'volume',label:'Concrete (m\\u00b3)',fmt:3},{key:'level',label:'Level'}]},   /* __acad3dV102 */
    stripfooting:{label:'Wall Foundations',build:function(){return bimBuildFootingSchedule('stripfooting');},cols:[{key:'name',label:'Name'},{key:'type',label:'Type'},{key:'host',label:'Under'},{key:'length',label:'Length (m)',fmt:2},{key:'width',label:'Width (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'volume',label:'Concrete (m\\u00b3)',fmt:3},{key:'level',label:'Level'}]},
    beam:{label:'Beams',build:bimBuildBeamSchedule,"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
