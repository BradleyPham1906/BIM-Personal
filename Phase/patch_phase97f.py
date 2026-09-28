"""patch_phase97f.py -- __acad3dV97: an out-of-range segment is refused, not thrown on.

Found by the suite. bimSketchSegMid indexed o.pts[seg] with no range check, and the exported
insert computed the midpoint BEFORE bimInsertSketchVertex got to validate the segment -- so a
bad segment number raised a TypeError out of the page instead of returning the refusal the
function already knew how to give. The build contract is explicit that a new code path fails
gracefully, never by throwing.

The range check now lives in bimSketchSegMid itself, and the insert validates the point it is
handed, so neither can be reached with something it cannot use.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '1b0645650d78183b0c034baa32ce491db070993cab3160e329eaa7a0a25ec630'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  function bimSketchSegMid(o,seg){
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];""",
     """  function bimSketchSegMid(o,seg){
    if(!o||!o.pts||!(seg>=0&&seg<bimSketchSegCount(o))||Math.floor(seg)!==seg)return null;
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];"""),
    ("""    var segs=bimSketchSegCount(o);
    if(!(seg>=0&&seg<segs)||Math.floor(seg)!==seg)return {error:'There is no such segment'};""",
     """    var segs=bimSketchSegCount(o);
    if(!(seg>=0&&seg<segs)||Math.floor(seg)!==seg)return {error:'There is no such segment'};
    if(!pt||!isFinite(pt[0])||!isFinite(pt[1]))return {error:'That is not a point to insert'};"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:60])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
