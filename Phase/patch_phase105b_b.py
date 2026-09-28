"""patch_phase105bb.py"""
NAME = 'patch_phase105bb'
BASE = 'e1163664153c5b977cb8d66bb9d95ce4e70bfed3a17fd7f58cacbcd0d52d55fb'
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
# --- patch b: per-edge source on a traced face, and one level-by-id lookup.

rep("""        var loopPts=[],loopB=[],loopS={},h=h0,guard=0,ok=true;
        while(guard++<20000){
          seen[hid(h)]=1;
          loopPts.push(bimHalfFrom(g,h));
          loopB.push(bimHalfBulge(g,h));
          if(g.edges[h.e].src)loopS[g.edges[h.e].src]=1;   /* __acad3dV98 */
""","""        var loopPts=[],loopB=[],loopSrc=[],loopS={},h=h0,guard=0,ok=true;
        while(guard++<20000){
          seen[hid(h)]=1;
          loopPts.push(bimHalfFrom(g,h));
          loopB.push(bimHalfBulge(g,h));
          loopSrc.push(g.edges[h.e].src||null);   /* __acad3dV105b: which object gave THIS edge */
          if(g.edges[h.e].src)loopS[g.edges[h.e].src]=1;   /* __acad3dV98 */
""",1)

rep("""        if(ok&&loopPts.length>=2)faces.push({pts:loopPts,bulges:loopB,srcIds:Object.keys(loopS)});
""","""        if(ok&&loopPts.length>=2)faces.push({pts:loopPts,bulges:loopB,srcs:loopSrc,srcIds:Object.keys(loopS)});
""",1)

rep("""  function bimLevelName(levelId){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId)return A3D.levels[i].name;
    return '-';
  }
""","""  /* __acad3dV105b: one lookup, so a caller that wants a level's elevation and a caller that wants
     its name cannot find different levels. */
  function bimLevelById(levelId){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId)return A3D.levels[i];
    return null;
  }
  function bimLevelName(levelId){
    var lv=bimLevelById(levelId);
    return lv?lv.name:'-';
  }
""",1)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
