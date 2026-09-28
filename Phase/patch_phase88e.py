"""patch_phase88e.py -- Phase 88 part 5: two test hooks.

__a3dImportDXF lets the suite feed a DXF string straight back in, which is what makes the round
trip testable at all - the file-input path cannot be driven headlessly. __a3dToScreen projects a
world point the way the renderer does, so a pick can be aimed at the arc rather than at its chord.
"""
import hashlib, pathlib, sys

BASE = '92950ada27aef1f3f6cdd596b6530b64f88c73f8d4d335a259f113fad1857448'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

OLD = "  window.__a3dBuildDXF=bimBuildDXF;"
NEW = """  window.__a3dBuildDXF=bimBuildDXF;
  /* __acad3dV88: the DXF round trip, and a projection the suite can aim a click with. */
  window.__a3dImportDXF=function(text){return bimImportDXF(text,'test.dxf');};
  window.__a3dToScreen=function(p,y){
    return toScreen([p[0],(typeof y==='number')?y:0,p[1]],camVecs(A3D.cam),cvW(),cvH());
  };"""
assert src.count(OLD) == 1, 'anchor count %d' % src.count(OLD)
out = src.replace(OLD, NEW, 1)
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
