"""patch_phase119h.py -- V119: the ViewCube can be clicked only where it is drawn.

The cube is drawn in 3D only, and the list of its faces' outlines that a click is tested against was
refilled each time it was drawn and never emptied when it was not. So a flat view kept the outlines of
the last 3D frame -- at boot, the frames before the plan opened -- and an invisible cube answered
clicks. Measured on the V119 build before this patch, in the floor plan: of 121 clicks on a grid over
the empty top-right corner of the canvas, 51 switched the view, most of them to the Left Elevation.
Its Home button, the same.

The outlines and Home's box are emptied whenever the cube is not drawn. __a3dCubeFaces reports where
the faces are on the page, so a suite can click them with the mouse: the cube is drawn on the canvas
and has no elements of its own."""
NAME = 'patch_phase119h.py'
BASE = 'bf81a87195ef3564a12dbc7b4338f0f60bfdb63bd6eab43e5ce385bd2b8d6fa2'
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
rep("      if(!A3D.flat)drawCube(ctx,W,H,V);\n",
    "      if(!A3D.flat)drawCube(ctx,W,H,V);\n"
    "      else{A3D.cubePolys=[];A3D.homeRect=null;}   /* __acad3dV119: not drawn, not clickable */\n")
rep("  window.__a3dSetView=function(n,anim){setView(n,anim===undefined?false:anim);};\n",
    r'''  window.__a3dSetView=function(n,anim){setView(n,anim===undefined?false:anim);};
  /* __acad3dV119: where the ViewCube's faces and its Home button are on the page, for a suite to
     click with the mouse. Empty while the cube is not drawn. */
  window.__a3dCubeFaces=function(){
    var r=el.cv?el.cv.getBoundingClientRect():null,out=[],i,j,p,sx,sy;
    if(!r)return out;
    for(i=0;i<A3D.cubePolys.length;i++){
      p=A3D.cubePolys[i].pts;sx=0;sy=0;
      for(j=0;j<p.length;j++){sx+=p[j][0];sy+=p[j][1];}
      out.push({n:A3D.cubePolys[i].n,x:r.left+sx/p.length,y:r.top+sy/p.length});
    }
    if(A3D.homeRect)out.push({n:'home',x:r.left+A3D.homeRect[0]+A3D.homeRect[2]/2,y:r.top+A3D.homeRect[1]+A3D.homeRect[3]/2});
    return out;
  };
''')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
