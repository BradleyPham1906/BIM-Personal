"""patch_phase97g.py -- __acad3dV97: a grip under the cursor beats a gizmo arm.

Found by driving the user's own scenario with the mouse: the midpoint grips were drawn, the
engine inserted vertices correctly when called directly, and pressing a grip by hand did
nothing to the vertex count. The move gizmo (V76) is tested BEFORE grips, and its arms run out
from the object's centre along the axes -- so on any SYMMETRIC shape, which is most of them, the
midpoint of an edge lies exactly on an arm. The press started a gizmo move of the whole sketch.
That is very probably what the user saw: grab a point, watch the whole shape move.

V76's reason for gizmo-first was that its arms reach outside the object and must not lose to
whatever lies under them. That is right for the object BODY and for other objects, and neither
the V76 nor the V78 suite tests a grip at all -- the order was never a decision about grips.
A grip is an 8-pixel point target the user aims at deliberately; an arm is a long band that can
be grabbed anywhere along its length. So a grip the pointer is actually on now wins, and the
gizmo still wins over everything else it always did.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '6ceea6ce734e58f64653bc4a9cbb0197f5c8fa07684d2abc12ae06c5396b1088'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

GIZMO = """    /* __acad3dV76: the gizmo is tested BEFORE grips and before the body drag. Its arms reach
       outside the object, so testing it later would let whatever lies under an arm win the
       click -- and the arm is the thing the user aimed at. */
    if(!A3D.sk&&ev.button===0&&!ev.ctrlKey&&!ev.metaKey&&!ev.shiftKey){
      var gz=bimPickGizmo(xy[0],xy[1]);
      if(gz){
        var gd=gz.rot?bimGizmoBeginRotate(gz,xy):bimGizmoBegin(gz,xy);
        if(gd){pushUndo();drag=gd;paint();}
        ev.preventDefault();
        return;
      }
    }
"""
assert txt.count(GIZMO) == 1, 'gizmo block count %d' % txt.count(GIZMO)

# the grip block, from its opening to the end of its ordinary-drag branch
g_head = "    if(!A3D.sk&&ev.button===0){\n      var grip=bimPickGrip(xy[0],xy[1]);\n"
assert txt.count(g_head) == 1
gs = txt.index(g_head)
g_tail = """        drag={grip:true,objId:grip.objId,idx:grip.idx,kind:grip.kind,elev:grip.elev,moved:false};
        ev.preventDefault();
        return;
      }
    }
"""
ge = txt.index(g_tail, gs) + len(g_tail)
grip_block = txt[gs:ge]
assert 'bimInsertSketchVertex' in grip_block, 'wrong grip span'

gzs = txt.index(GIZMO)
assert gzs + len(GIZMO) == gs, 'gizmo block is not immediately before the grip block'

NEW_ORDER = ("""    /* __acad3dV97: GRIPS FIRST, then the gizmo. A grip is an 8-pixel point target the user
       aims at on purpose; a gizmo arm is a long band that can be grabbed anywhere along it. On
       a symmetric shape an edge's midpoint grip sits exactly on an arm, so gizmo-first turned
       "add a vertex here" into "move the whole shape". The gizmo still wins over the body and
       over other objects, which is what V76 put it first for. */
""" + grip_block + GIZMO.replace(
    """    /* __acad3dV76: the gizmo is tested BEFORE grips and before the body drag. Its arms reach
       outside the object, so testing it later would let whatever lies under an arm win the
       click -- and the arm is the thing the user aimed at. */""",
    """    /* __acad3dV76: the gizmo is tested before the body drag. Its arms reach outside the
       object, so testing it later would let whatever lies under an arm win the click -- and
       the arm is the thing the user aimed at. (Grips now come first; see __acad3dV97 above.) */"""))

txt = txt[:gzs] + NEW_ORDER + txt[ge:]

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
