"""patch_phase104b.py -- __acad3dV104: the plan SVG was mirrored too.

V103 recorded "SVG (y down) is unaffected". Measured while writing this phase's suite: false.
bimBuildSVG wrote svg_y = -z with a matching viewBox, i.e. it treated model +Z as UP -- the plan's
mirror image, exactly like the DXF. SVG's y runs down, as the canvas's does, so the correct
mapping is svg_y = +z. The sheet viewport writer was already right (it projects through the
camera). Six coordinate sites and the viewBox, one mapping.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'b85eed92288f3cee376915561d9d822eed3e97a19204277bd1b986546bca7c41'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
L = txt.index('  function bimBuildSVG(mode){')
E = txt.index('\n  function ', L + 10)
body = txt[L:E]
for tok in ['(-cmd.pts[q][1])', '(-cmd.outer[q2][1])', '(-cmd.inner[q2][1])', '(-cmd.a[1])', '(-cmd.b[1])', '(-cmd.pt[1])']:
    assert body.count(tok) == 1, tok
    body = body.replace(tok, tok.replace('(-', '(', 1))
OLDVB = "var vbX=minX-margin,vbY=-(maxZ)-margin,"
assert body.count(OLDVB) == 1
body = body.replace(OLDVB, "var vbX=minX-margin,vbY=minZ-margin,   /* __acad3dV104: y down, as the plan */\n        ")
txt = txt[:L] + body + txt[E:]
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
