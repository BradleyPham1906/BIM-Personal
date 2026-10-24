#!/usr/bin/env python3
"""V170e: hooks for the suite -- which way each line of a march runs (by its points' order after the turn), the
site's centre it runs from, and true north.

Run from the repository root: python3 Phase/patch_phase170e.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '979834a4cc2ea359b9c9981185a6e10c6a8d95797babaca8ef0861e0d4ede019'   # V170d

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


rep("  window.__a3dAnimTint=function(h){return bimAnimTint(h);};\n",
    "  window.__a3dAnimTint=function(h){return bimAnimTint(h);};\n"
    "  /* a march's way: the points' order after the turn -- a line's, each pair's of segments, each polyline's */\n"
    "  window.__a3dAnimWay=function(id){var o=objById(id),g,I;if(!bimIsDiag(o))return null;g=o.dg.g;A3D_ANIM.c=null;\n"
    "    function idx(n){var P=[],i;for(i=0;i<n;i++)P.push([i,0,1]);return P;}\n"
    "    if(g.kind==='lines')return (g.lines||[]).map(function(Wl){return bimAnimOrientLine(o,Wl,idx(Wl.length)).map(function(p){return p[0];});});\n"
    "    I=bimAnimOrient(o,idx((g.pts||[]).length));return I.map(function(p){return p[0];});};\n"
    "  window.__a3dAnimCentre=function(){A3D_ANIM.c=null;return bimAnimCentre();};\n"
    "  /* the clock fed these frame times (ms), as requestAnimationFrame would: the frames drawn and the time gone on */\n"
    "  window.__a3dAnimTicks=function(ts){var f0=A3D_ANIM.frames,t0=A3D_ANIM.t,i;bimAnimHalt();A3D_ANIM.on=true;A3D_ANIM.paused=false;A3D_ANIM.last=0;A3D_ANIM.painted=0;\n"
    "    for(i=0;i<ts.length;i++){bimAnimTick(ts[i]);if(A3D_ANIM.raf){cancelAnimationFrame(A3D_ANIM.raf);A3D_ANIM.raf=0;}}\n"
    "    A3D_ANIM.on=false;A3D_ANIM.paused=true;return {frames:A3D_ANIM.frames-f0,dt:A3D_ANIM.t-t0};};\n")

rep("    raf:!!A3D_ANIM.raf,fr:{", "    raf:!!A3D_ANIM.raf,north:bimTrueNorthDeg(),fr:{")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
