"""patch_phase137b.py -- V137: Buildings on the terrain in the Site Context group; a building's
standing height in its properties; hooks and the marker."""
NAME = 'patch_phase137b.py'
BASE = '4c8907d1555e64696e4cb80a123cfb2fa277adc08b909dce566a7f35c675798f'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""    r+=bimPropRow('Get','<div class="a3d-ctxks">'+ck+'</div>');""", """    r+=bimPropRow('Get','<div class="a3d-ctxks">'+ck+'</div>');
    r+=bimPropRow('Buildings','<label class="a3d-ctxk"><input type="checkbox" data-propctx="onGround"'+(st.onGround?' checked':'')+
      '> On the terrain</label>');   /* __acad3dV137 */""")
rep("""    bimCtxSet(k,k.indexOf('kind:')===0?f.checked:f.value);""", """    bimCtxSet(k,(k.indexOf('kind:')===0||k==='onGround')?f.checked:f.value);   /* __acad3dV137 */""")
rep("""      if(c.ground!=null)r+=bimPropText('Ground',bimDispNum(c.ground,2)+' m from model y 0, on the terrain');""",
    """      if(c.ground!=null)r+=bimPropText('Ground',bimDispNum(c.ground,2)+' m from model y 0, on the terrain');
      if(c.standY)r+=bimPropText('Stands at',bimDispNum(c.standY,2)+' m: the lowest ground under it');   /* __acad3dV137 */""")
rep("""  /* __acad3dV136: the lens */
  window.__a3dLens=""", """  /* __acad3dV137: the map on 3D terrain */
  window.__a3dTerrain3d=function(){return A3D.lastTerrain3d?JSON.parse(JSON.stringify(A3D.lastTerrain3d)):null;};
  window.__a3dTinHeightAt=function(id,x,z){var o=objById(id),tin=o?bimTerrainTin(o):null;return tin?bimTinHeightAt(tin,x,z):null;};
  window.__a3dCtxStand=function(on){return bimCtxStand(!!on);};
  window.__a3dDrapeTiles=function(ext,z,maxz){return bimDrapeTiles(ext,z,maxz||19);};
  window.__a3dTerrainPolys=function(){return (A3D.lastPolys||[]).filter(function(p){return p.terrain;}).length;};
  window.__acad3dV137='terrain3d,terrainshaded,terraindrape,drapetiles,drapeparent,drapediscard,terrain2d,ctxonground,ctxgroundsetting,ctxgroundundo,ctxgroundfetch';
  /* __acad3dV136: the lens */
  window.__a3dLens=""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
