"""patch_phase105bf.py"""
NAME = 'patch_phase105bf'
BASE = 'fb404504cca99fd1be154f3830075e33251e462bb181f7f281fe5fdbc7b1146f'
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
# --- patch f: one inset core, used from both sides, and a face that is two curved edges.

NEW = """  /* Push every edge of a traced face to one side by the depth of its own wall's body, and miter
     the pushed lines together. side = +1 takes the RIGHT of travel, which is the inside of a
     building for the clockwise outer face; side = -1 takes the LEFT, which is the inside of a
     room for a counter-clockwise interior face. One function, so gross area and net area cannot
     drift apart. */
  function bimInsetFaceRing(fpts,fbulges,fsrcs,cache,side){
    var st=bimStripSpurs(fpts,fbulges,fsrcs);
    if(st.pts.length<2)return null;
    var segs=[],n=st.pts.length,i,k,a,b,bl,flat,src;
    for(i=0;i<n;i++){
      a=st.pts[i];b=st.pts[(i+1)%n];bl=st.bulges[i]||0;src=st.srcs[i]||null;
      if(Math.abs(bl)>BIM_BULGE_EPS){
        /* A curved wall is offset arc-wise, not chord-wise: flatten first, then push. */
        flat=bimFlattenPoly([a,b],[bl,0],false);
        for(k=0;k+1<flat.length;k++)segs.push({a:flat[k],b:flat[k+1],src:src});
      }else segs.push({a:a,b:b,src:src});
    }
    var lines=[],dx,dz,L,dir,nrm,mid,ins,rings;
    for(i=0;i<segs.length;i++){
      dx=segs[i].b[0]-segs[i].a[0];dz=segs[i].b[1]-segs[i].a[1];
      L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-9)continue;
      dir=[dx/L,dz/L];
      nrm=[dir[1]*side,-dir[0]*side];
      mid=[(segs[i].a[0]+segs[i].b[0])/2,(segs[i].a[1]+segs[i].b[1])/2];
      ins=0;
      if(segs[i].src){
        if(!cache.hasOwnProperty(segs[i].src))cache[segs[i].src]=bimWallFaceRings(objById(segs[i].src));
        rings=cache[segs[i].src];
        ins=bimWallInsetAt(rings,mid,nrm);
        if(ins===null||!isFinite(ins))ins=0;
      }
      lines.push({a:[segs[i].a[0]+nrm[0]*ins,segs[i].a[1]+nrm[1]*ins],
                  b:[segs[i].b[0]+nrm[0]*ins,segs[i].b[1]+nrm[1]*ins],
                  dir:dir,inset:ins});
    }
    if(lines.length<3)return null;
    var ring=[],cur,nxt,hit,cap,dd;
    for(i=0;i<lines.length;i++){
      cur=lines[i];nxt=lines[(i+1)%lines.length];
      hit=bimLineLineIntersect(cur.a,cur.b,nxt.a,nxt.b);
      cap=6*Math.max(cur.inset,nxt.inset)+1e-6;
      dd=hit?Math.sqrt((hit[0]-cur.b[0])*(hit[0]-cur.b[0])+(hit[1]-cur.b[1])*(hit[1]-cur.b[1])):Infinity;
      if(hit&&isFinite(hit[0])&&isFinite(hit[1])&&dd<=cap)ring.push(hit);
      else {ring.push(cur.b);ring.push(nxt.a);}   /* parallel, or a miter that runs away: the jog */
    }
    var out=[],p;
    for(i=0;i<ring.length;i++){
      p=ring[i];
      if(out.length&&Math.abs(out[out.length-1][0]-p[0])<1e-9&&Math.abs(out[out.length-1][1]-p[1])<1e-9)continue;
      out.push(p);
    }
    if(out.length>2&&Math.abs(out[0][0]-out[out.length-1][0])<1e-9&&Math.abs(out[0][1]-out[out.length-1][1])<1e-9)out.pop();
    if(out.length<3)return null;
    return out;
  }
  /* The inside face of one run of exterior walls: the face arrives traced CLOCKWISE, which puts
     the building on the RIGHT of the direction of travel. */
  function bimGrossRingFromFace(face,cache){
    var out=bimInsetFaceRing(face.pts,face.bulges,face.srcs,cache,1);
    if(!out)return null;
    return {pts:out,area:bimPolyArea(out),srcIds:face.srcIds?face.srcIds.slice():[]};
  }
"""

span("  function bimGrossRingFromFace(face,cache){", "  function bimLevelGrossRings(levelId){", NEW, 51)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
