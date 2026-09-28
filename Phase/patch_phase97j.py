"""patch_phase97j.py -- __acad3dV97: a stale gizmo is dead too.

Law 2, and this is exactly the case it exists for. 97h found that A3D.grips was hit-tested from
the LAST paint, so a selection change with no repaint left the old object's grips live. The
same mistake was then looked for elsewhere -- and the move/rotate gizmo has it too: A3D.gizmo is
built during paint for the selection of that moment, and bimPickGizmo tested it without asking
whether that was still the selection. A drag on an unselected sketch, at the spot where its
rotate ring had last been drawn, ROTATED it. The V97 suite caught it through a check written
for the grips, because the ring passes through the very spot the midpoint grip had been.

The gizmo already records the ids it was built for, from bimGizmoIds. The pick now compares
those with bimGizmoIds() now -- the same function, so the two cannot disagree about what "the
selection" means -- and a gizmo built for a different selection answers nothing.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '87890fec189359c73992b91659298abce0e94f320b9d3f8b06fc5e7048d19d4d'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  function bimPickGizmo(x,y){
    if(!bimGizmoVisible())return null;
    var g=A3D.gizmo;
    if(!g)return null;"""
NEW = """  function bimPickGizmo(x,y){
    if(!bimGizmoVisible())return null;
    var g=A3D.gizmo;
    if(!g)return null;
    /* __acad3dV97: A3D.gizmo is what the LAST paint drew, for the selection of that moment. If
       the selection has changed since with no repaint, this gizmo belongs to objects that are
       no longer selected, and a drag on it moved or rotated them. Compared through the same
       function that built it, so "the selection" means one thing in both places. */
    var now=bimGizmoIds(),was=g.ids||[];
    if(now.length!==was.length)return null;
    var gi;
    for(gi=0;gi<now.length;gi++)if(was.indexOf(now[gi])<0)return null;"""
assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
