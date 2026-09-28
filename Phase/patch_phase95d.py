"""patch_phase95d.py -- __acad3dV95: the BIM toolset reaches the command line.

Found by the suite failing. Typing ROOM into the palette started BOUNDARY, because there is no
ROOM command -- and there is no FLOOR, CEILING, ROOF, STAIR, COLUMN, BEAM, DOOR, WINDOW,
SECTION or gridline command either. Every one of those eleven start functions has exactly two
references in the file: its definition, and one ribbon button.

So in a BIM application, the entire BIM toolset has never been reachable from the command line.
This is the third time this class has surfaced -- V87 found ROTATE, ARRAYRECT, ARRAYPOLAR,
ALIGN and JOIN in the same state, V90 found WALL -- and each time it was found by wanting to
drive the tool from a test rather than by reading the code.

GRID is deliberately NOT the name used for the structural gridline tool. CADCMDS already has a
GRID that toggles grid snap, which is AutoCAD's meaning, and two commands answering to one name
is the ambiguity this file has been paying off all week. The gridline tool gets GRIDLINE.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '274b468e0b4d8549c08eaff526b5ce09eeb9c12dd5cd96e8dbf03048ea32d8bd'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

ROWS = """    ['ROOM',['RM'],'room','Tag a closed region as a room'],
    ['FLOOR',['FL','SLAB'],'floorTool','Place a floor slab in a closed region'],
    ['CEILING',['CEIL'],'ceilingTool','Place a ceiling in a closed region'],
    ['ROOF',['RF'],'roofTool','Place a roof over a closed region'],
    ['STAIR',['STAIRS'],'stairTool','Draw a stair run'],
    ['COLUMN',['COL'],'columnTool','Place a column'],
    ['BEAM',['BM'],'beamTool','Draw a beam between two points'],
    ['DOOR',['DR'],'doorTool','Place a door in a wall'],
    ['WINDOW',['WIN'],'windowTool','Place a window in a wall'],
    ['GRIDLINE',['GL'],'gridline','Draw a structural gridline'],
    ['SECTION',['SEC'],'sectionTool','Cut a section through the model'],
"""

EDITS = [
    ("""    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],""",
     ROWS + """    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],"""),

    ("""    boundary:function(){startBoundaryTool();},/* __acad3dV95 */""",
     """    /* __acad3dV95: the BIM toolset, reachable from the command line for the first time.
       Each of these already worked from the ribbon and from nowhere else. */
    room:function(){startRoomTool();},
    floorTool:function(){startFloorTool();},
    ceilingTool:function(){startCeilingTool();},
    roofTool:function(){startRoofTool();},
    stairTool:function(){startStairTool();},
    columnTool:function(){startColumnTool();},
    beamTool:function(){startBeamTool();},
    doorTool:function(){startDoorTool();},
    windowTool:function(){startWindowTool();},
    gridline:function(){startGridTool();},
    sectionTool:function(){startSectionTool();},
    boundary:function(){startBoundaryTool();},/* __acad3dV95 */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
