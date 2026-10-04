"""patch_phase157b.py -- V157: test hooks for the surroundings in 3D.

Read-only views of the V157 helpers, beside V133's site-context hooks: what kind OSM tags make, a
road's use, a width in metres, a surface's width, and the points along a line. And Properties says
what a surface is: its use and width, a bridge's deck, a tunnel, a tree's or a pylon's height."""
NAME = 'patch_phase157b.py'
BASE = '56ac8c061d57bb4d883b6b127ec9172fc2030f8b25487caaf93a0d87b18e739a'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


rep("""  window.__a3dCtxDatum=function(){return bimCtxDatum();};""",
    """  window.__a3dCtxDatum=function(){return bimCtxDatum();};
  window.__a3dOsmKind=function(el){return bimOsmKind(el);};                 /* __acad3dV157 */
  window.__a3dRoadUse=function(tags){return bimRoadUse(tags||{});};
  window.__a3dTagMetres=function(v){return bimTagMetres(v);};
  window.__a3dCtxWidth=function(kind,tags){return bimCtxWidth(kind,tags||{});};
  window.__a3dCtxAlong=function(pts,step){return bimCtxAlong(pts,step);};""")

rep("""    if(c.part==='hole')r+=bimPropText('Ring','a hole in the area before it');""",
    """    if(c.part==='hole')r+=bimPropText('Ring','a hole in the area before it');
    if(c.use)r+=bimPropText('Use',BIM_ROAD_USE_LABEL[c.use]||c.use);   /* __acad3dV157: the surroundings in 3D */
    if(c.width)r+=bimPropText('Width',bimDispNum(c.width,2)+' m');
    if(c.bridge)r+=bimPropText('Bridge','its deck '+bimDispNum(c.deck,2)+' m above the ground, on piers every '+BIM_CTX_PIER+' m');
    if(c.tunnel)r+=bimPropText('Tunnel','below ground: its centre line only');
    if((c.kind==='trees'||c.kind==='power')&&c.height)r+=bimPropText('Height',bimDispNum(c.height,2)+' m'+(c.crown?', crown '+bimDispNum(c.crown,2)+' m across':''));
    if(c.row)r+=bimPropText('Planted','in a row, a tree every '+BIM_CTX_TREE_STEP+' m');""")
rep("""  var BIM_ROAD_COL={car:""", """  var BIM_ROAD_USE_LABEL={car:'car road',pedestrian:'pedestrian zone',footway:'footway',cycleway:'cycleway',path:'path'};
  var BIM_ROAD_COL={car:""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
