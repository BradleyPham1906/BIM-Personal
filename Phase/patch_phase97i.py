"""patch_phase97i.py -- __acad3dV97: the undo snapshot is taken BEFORE the insert.

97h moved the insert from the press to the first movement, and put pushUndo after it -- so the
snapshot captured the sketch WITH the new vertex, and undo would have restored the already
edited shape. Caught on reading the patch back, before any test ran against it. The snapshot
now precedes the mutation, as every other pushUndo in this file does.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'c6b1f4e61228efc6fcd6d556a7bbf661c1baa0e221a894c3dcceed2bfa03b277'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "        var pmo=objById(drag.objId);\n        var pins=pmo?bimInsertSketchVertex(pmo,drag.pendingMid.seg,bimSketchSegMid(pmo,drag.pendingMid.seg))\n                    :{error:'That sketch no longer exists'};\n        drag.pendingMid=null;\n        if(pins.error){a3dToast('Add vertex: '+pins.error);drag=null;paint();return;}\n        pushUndo();\n        drag.idx=pins.idx;"
NEW = "        var pmo=objById(drag.objId);\n        /* the snapshot BEFORE the insert, so undo restores the shape as it was */\n        if(pmo)pushUndo();\n        var pins=pmo?bimInsertSketchVertex(pmo,drag.pendingMid.seg,bimSketchSegMid(pmo,drag.pendingMid.seg))\n                    :{error:'That sketch no longer exists'};\n        drag.pendingMid=null;\n        if(pins.error){a3dToast('Add vertex: '+pins.error);drag=null;paint();return;}\n        drag.idx=pins.idx;"
assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
