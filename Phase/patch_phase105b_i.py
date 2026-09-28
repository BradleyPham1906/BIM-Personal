"""patch_phase105bi.py"""
NAME = 'patch_phase105bi'
BASE = '74aa407d072c8745b78c35a3b7ff84ff4995f76d2cda85b51ce3ec82c86b5b61'
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
# --- patch i: the wall body's depth is measured by a ray, not by the nearest point on a ring.

NEW = """  /* The far crossing of the ray p + t*n with a polyline, for t in [0, lim].

     This replaces a nearest-point-on-the-ring lookup, which answered the right number for a
     straight wall and had no defensible answer at all when the nearest part of the ring belonged
     to a different run of the same wall. A ray asks the question the caller actually has: how
     deep is this body in this direction. lim is the wall's own thickness, and it is what stops
     the ray reaching the FAR side of a closed wall and reporting the width of the building as a
     wall inset. */
  function bimRayPolyDepth(poly,closed,p,n,lim){
    if(!poly||poly.length<2)return null;
    var best=null,m=poly.length,segs=closed?m:m-1,i,a,b,ex,ez,wx,wz,D,t,u;
    for(i=0;i<segs;i++){
      a=poly[i];b=poly[(i+1)%m];
      ex=b[0]-a[0];ez=b[1]-a[1];
      D=ex*n[1]-n[0]*ez;
      if(Math.abs(D)<1e-12)continue;
      wx=a[0]-p[0];wz=a[1]-p[1];
      t=(ex*wz-wx*ez)/D;
      u=(n[0]*wz-wx*n[1])/D;
      if(u<-1e-9||u>1+1e-9)continue;
      if(t<-1e-9||t>lim)continue;
      if(best===null||t>best)best=t;
    }
    return best;
  }
  /* How deep a wall's body reaches from the point p in the direction n. Measured off the BUILT
     faces instead of assumed from 'align', so a left- or right-aligned wall insets by its whole
     thickness on the side its body is on and by nothing on the other -- and so that no sign
     convention is copied out of bimOffsetRing, where a later change to it would not be noticed. */
  function bimWallInsetAt(rings,p,n){
    if(!rings)return null;
    var lim=(rings.thickness>0?rings.thickness:0)+1e-6;
    var ta=bimRayPolyDepth(rings.a,rings.closed,p,n,lim);
    var tb=bimRayPolyDepth(rings.b,rings.closed,p,n,lim);
    if(ta===null)return tb;
    if(tb===null)return ta;
    return ta>tb?ta:tb;
  }
"""

span("  function bimNearestOnPoly(poly,p,closed){", "  function bimBuildWallGeometry(", NEW, 27)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
