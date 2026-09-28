"""patch_phase123h.py -- V123: a primitive's Base Offset is its base.

Found in V123's visual review, beside the Dimensions 123g put back. Properties' Constraints show a
Base Offset for every object, read from its position's height. A wall's mesh stands on its base, so
there that is its offset; a primitive's mesh is centred on its position, so there it is its MIDDLE:
a 3.5 m box standing on the ground read "Base Offset 1750", a Height typed in Properties (which keeps
the base, 123g) or a pulled top (123f) moved the number while the base stayed put, and a Base
Offset typed as 0 sank the box half into the ground.

The row now reads and sets the base of a primitive -- its position plus the lowest point of its
centred mesh, the same meshMinY the size change keeps -- and is what it was for everything else."""
NAME = 'patch_phase123h.py'
BASE = 'ca830587d1058c12a84ffae5a28d169c9270481502a4a34a69bf7ad67080a4d7'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]

rep("""  function bimPrmLabel(t,param){return (BIM_PRM_LABELS[t]&&BIM_PRM_LABELS[t][param])||param;}
""", """  function bimPrmLabel(t,param){return (BIM_PRM_LABELS[t]&&BIM_PRM_LABELS[t][param])||param;}
  /* __acad3dV123: the height of a primitive's base -- its mesh is centred on its position, so the
     position is its middle. Null for anything else, whose mesh stands on its own base. */
  function bimPrimBase(o){
    if(!o||o.mesh||!o.prm||!TYPES[o.t])return null;
    var m=meshOf(o);
    if(!m||!m.v||!m.v.length)return null;
    return ((o.pos&&o.pos[1])||0)+meshMinY(m);
  }
""")
rep("""    cons+=bimPropLen('Base Offset',(o.pos&&o.pos[1])||0,'posy');""",
    """    var pbO=bimPrimBase(o);   /* __acad3dV123: a primitive's base, not its middle */
    cons+=bimPropLen('Base Offset',pbO!==null?pbO:((o.pos&&o.pos[1])||0),'posy');""")
rep("""        pushUndo();
        if(!o.pos)o.pos=[0,0,0];
        o.pos[1]=yv;
        paint();saveSoon();""", """        var pbY=bimPrimBase(o);   /* __acad3dV123: a primitive's row sets its base */
        pushUndo();
        if(!o.pos)o.pos=[0,0,0];
        o.pos[1]=pbY!==null?o.pos[1]+(yv-pbY):yv;
        paint();saveSoon();""")
rep("""    'sketchpull,primitivedimensions';""", """    'sketchpull,primitivedimensions,primitivebase';""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
