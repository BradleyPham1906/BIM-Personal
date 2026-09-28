"""patch_phase123i.py -- V123: a door's head is not the wall's top.

Found in V123's visual review: holding the top of a wall with a door drew the door's head as part of
the top. A wall's faces were keyed by direction and half height only -- any horizontal face above
half height was 'top', below it 'bottom', and every upright face that was not an end cap 'side'. So
a door's head (above half height, facing down) was part of the top the arrow pulls, a window's sill
(below it, facing up) part of the bottom, and each jamb part of the side whose thickness the type
sets.

A horizontal face is now the wall's top or bottom only where the wall's top or bottom is; an upright
face that runs across the wall, where it is not an end, is a jamb. Both are the opening's: the face
says so and where the opening is sized. Which way a face's corners run is not read -- a cut wall's
mesh is not promised to keep it -- only where the face is and which way it lies against the wall's
line (bimWallTangentAt, arcs included)."""
NAME = 'patch_phase123i.py'
BASE = '25bcf87faf1c51bdb5835fef830c83ce6af46c8cf591c0f43ff59c91e8bbf9f3'
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

rep("""  /* WHICH FACE a mesh face is, for its object: the key the rest of the section speaks of. */
  function bimFaceKeyOf(o,m,fi){""", """  /* __acad3dV123: the direction of a wall's line in plan nearest a world point -- along the segment,
     or along the arc's tangent there. Null when the wall has no line. */
  function bimWallTangentAt(o,c){
    var b=o.bim,cl=b&&b.centerline;
    if(!cl||cl.length<2)return null;
    var q=bimObjOffset(o),pr=bimProjectOntoBulged(cl,b.bulges,!!b.closed,[c[0]-q[0],c[2]-q[2]]);
    if(!pr)return null;
    var A=cl[pr.seg],B=cl[(pr.seg+1)%cl.length],arc=bimBulgeArc(A,B,bimBulgeAt(b.bulges,pr.seg));
    var t=arc?[-(pr.pt[1]-arc.center[1]),pr.pt[0]-arc.center[0]]:[B[0]-A[0],B[1]-A[1]];
    var L=Math.sqrt(t[0]*t[0]+t[1]*t[1]);
    return L>1e-12?[t[0]/L,t[1]/L]:null;
  }
  /* WHICH FACE a mesh face is, for its object: the key the rest of the section speaks of. */
  function bimFaceKeyOf(o,m,fi){""")
rep("""    if(kind==='wall'){
      var b=o.bim;
      if(up)return c[1]>(b.baseY||0)+q[1]+(b.height||0)/2?'top':'bottom';
      if(upright){
        var e0=bimWallEndInfo(o,'start'),e1=bimWallEndInfo(o,'end');
        if(e0&&bimWallCapAt(o,pts,e0))return 'start';
        if(e1&&bimWallCapAt(o,pts,e1))return 'end';
      }
      return 'side';
    }""", """    if(kind==='wall'){
      /* __acad3dV123: the top and the bottom are where the wall's top and bottom are -- a door's head
         is above half height and a window's sill below it, and both are the opening's. An upright
         face across the wall's line that is not an end is a jamb, the opening's too. */
      var b=o.bim,yb=(b.baseY||0)+q[1],yt=yb+(b.height||0);
      if(up){
        if(Math.abs(c[1]-yt)<1e-3)return 'top';
        if(Math.abs(c[1]-yb)<1e-3)return 'bottom';
        return 'opening';
      }
      if(upright){
        var e0=bimWallEndInfo(o,'start'),e1=bimWallEndInfo(o,'end');
        if(e0&&bimWallCapAt(o,pts,e0))return 'start';
        if(e1&&bimWallCapAt(o,pts,e1))return 'end';
        var tg=bimWallTangentAt(o,c);
        if(tg&&Math.abs(N[0]*tg[0]+N[2]*tg[1])>0.7)return 'opening';
      }
      return 'side';
    }""")
rep("""    region:'Region',solid:'Face',other:'Face'};""", """    region:'Region',solid:'Face',other:'Face',opening:'Opening face'};   /* __acad3dV123: opening */""")
rep("""      else if(key==='bottom')f.why='A wall stands on its level - its base is not pulled';
      else f.why='A wall\\'s thickness comes from its type'""", """      else if(key==='bottom')f.why='A wall stands on its level - its base is not pulled';
      else if(key==='opening')f.why='This face is an opening\\'s - select the door or window to size or move it';   /* __acad3dV123 */
      else f.why='A wall\\'s thickness comes from its type'""")
rep("""    'sketchpull,primitivedimensions,primitivebase';""", """    'sketchpull,primitivedimensions,primitivebase,openingfaces';""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
