"""patch_phase97e.py -- __acad3dV97: remove a duplicate test export, again.

97d added window.__a3dGrips. The V75 test surface already had one -- defined later in the
file, so it silently won -- and it is the better of the two: it repaints first, so the grips it
returns are the ones for the current frame rather than the last one drawn.

This is the second phase running to shadow an existing export (V96 did it with
bimPatternSvgDef). A fix per occurrence is the symptom; the class is "a name can be assigned
twice and the later one wins without a word". The V97 suite now asserts that no __a3d function
export is defined twice anywhere in the file, so the third occurrence fails a test instead of
costing an investigation.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '98121da338d543cfed8140fe608930d142199c8b671a6a70c280b1b565bacbf9'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  window.__a3dGrips=function(){return (A3D.grips||[]).map(function(g){return {x:g.x,y:g.y,idx:g.idx,seg:g.seg,mid:!!g.mid,objId:g.objId};});};
"""
assert txt.count(OLD) == 1, 'dup count %d' % txt.count(OLD)
txt = txt.replace(OLD, '', 1)
assert txt.count('window.__a3dGrips=') == 1

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
