"""patch_phase105ba.py"""
NAME = 'patch_phase105ba'
BASE = 'ce1046069ed850f595b4d28520acf54f4ef9e4637276b40bfe69bf480a7af915'
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
# --- patch a: the wall's base ring, factored out, plus its two built faces in world plan coords.

OLD_WG = """  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges){
    var off=bimAlignOffsets(thickness,align);
    var geomPts=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    var cleanPts=[geomPts[0]],i;
    for(i=1;i<geomPts.length;i++){
      var prevp=cleanPts[cleanPts.length-1],curp=geomPts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }
    if(closed&&cleanPts.length>1){
      var firstp=cleanPts[0],lastp=cleanPts[cleanPts.length-1];
      if(Math.abs(firstp[0]-lastp[0])<1e-6&&Math.abs(firstp[1]-lastp[1])<1e-6)cleanPts.pop();
    }
    if(cleanPts.length<2)return {error:'Wall needs at least 2 distinct points'};
    var basePts=closed?sketchCCW(cleanPts):cleanPts;
"""

NEW_WG = """  /* __acad3dV105b: the points a wall's body is actually built from -- flattened when it carries
     bulges, de-duplicated, and wound CCW when it closes. Lifted out of bimBuildWallGeometry so
     that the area plan can rebuild a wall's two faces from the SAME ring the solid was built
     from. Two copies of these lines would disagree the first time either one changed, and the
     disagreement would show up as a gross area that quietly misses a wall thickness. */
  function bimWallBasePts(pts,bulges,closed){
    if(!pts||pts.length<2)return {error:'Wall needs at least 2 distinct points'};
    var geomPts=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    var cleanPts=[geomPts[0]],i,prevp,curp;
    for(i=1;i<geomPts.length;i++){
      prevp=cleanPts[cleanPts.length-1];curp=geomPts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }
    if(closed&&cleanPts.length>1){
      var firstp=cleanPts[0],lastp=cleanPts[cleanPts.length-1];
      if(Math.abs(firstp[0]-lastp[0])<1e-6&&Math.abs(firstp[1]-lastp[1])<1e-6)cleanPts.pop();
    }
    if(cleanPts.length<2)return {error:'Wall needs at least 2 distinct points'};
    return {pts:closed?sketchCCW(cleanPts):cleanPts};
  }
  /* Both faces of a wall's body, in WORLD plan coordinates. */
  function bimWallFaceRings(o){
    if(!o||o.t!=='solid'||!o.bim||o.bim.type!=='wall'||!o.bim.centerline)return null;
    var base=bimWallBasePts(o.bim.centerline,o.bim.bulges||null,!!o.bim.closed);
    if(base.error)return null;
    var off=bimAlignOffsets(o.bim.thickness,o.bim.align),q=bimObjOffset(o),ra,rb;
    try{
      ra=bimOffsetRing(base.pts,off.dLeft,!!o.bim.closed);
      rb=bimOffsetRing(base.pts,-off.dRight,!!o.bim.closed);
    }catch(eFR){console.warn('[BIM] Wall face rings failed: ',eFR);return null;}
    function world(r){var out=[],k;for(k=0;k<r.length;k++)out.push([r[k][0]+q[0],r[k][1]+q[2]]);return out;}
    return {a:world(ra),b:world(rb),closed:!!o.bim.closed,thickness:o.bim.thickness};
  }
  function bimNearestOnPoly(poly,p,closed){
    if(!poly||poly.length<2)return null;
    var best=null,bd=Infinity,n=poly.length,segs=closed?n:n-1,i,a,b,dx,dz,L2,tt,qx,qz,d;
    for(i=0;i<segs;i++){
      a=poly[i];b=poly[(i+1)%n];
      dx=b[0]-a[0];dz=b[1]-a[1];L2=dx*dx+dz*dz;
      tt=L2>1e-12?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
      if(tt<0)tt=0;else if(tt>1)tt=1;
      qx=a[0]+dx*tt;qz=a[1]+dz*tt;
      d=(qx-p[0])*(qx-p[0])+(qz-p[1])*(qz-p[1]);
      if(d<bd){bd=d;best=[qx,qz];}
    }
    return best;
  }
  /* How deep a wall's body reaches from the point p in the direction n. Measured off the BUILT
     faces instead of assumed from 'align', so a left- or right-aligned wall insets by its whole
     thickness on the side its body is on and by nothing on the other -- and so that no sign
     convention is copied out of bimOffsetRing, where a later change to it would not be noticed. */
  function bimWallInsetAt(rings,p,n){
    if(!rings)return null;
    var qa=bimNearestOnPoly(rings.a,p,rings.closed),qb=bimNearestOnPoly(rings.b,p,rings.closed);
    var da=qa?((qa[0]-p[0])*n[0]+(qa[1]-p[1])*n[1]):-Infinity;
    var db=qb?((qb[0]-p[0])*n[0]+(qb[1]-p[1])*n[1]):-Infinity;
    var d=da>db?da:db;
    if(!isFinite(d)||d<0)return null;
    return d;
  }
  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges){
    var off=bimAlignOffsets(thickness,align);
    var base=bimWallBasePts(pts,bulges,closed);
    if(base.error)return {error:base.error};
    var basePts=base.pts;
"""

rep(OLD_WG, NEW_WG, 1)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
