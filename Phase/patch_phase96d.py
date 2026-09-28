"""patch_phase96d.py -- __acad3dV96: one export of bimPatternSvgDef, not two.

Found by the suite. The V63 test surface already exported bimPatternSvgDef, through a wrapper
that spells out six parameters and drops anything after them. 96c added a second export of the
same name earlier in the file, so the V63 wrapper -- defined later -- silently won, and every
angle handed to the export was discarded on the way through.

Nothing failed loudly. The function existed, it was callable, it returned a valid <pattern>,
and it ignored its seventh argument. That is the shape of the bug law 1 is about: a superseded
thing that still runs.

One export, and it forwards what it is given rather than re-listing the signature, so the next
parameter this function gains cannot be dropped the same way.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '10db6a3698954d2320328bd38de0ebbbcd2261d7174cb0ae89d541dfdb56ebed'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

# the V63 wrapper: forward everything, so a new parameter cannot be silently dropped again
OLD_WRAP = """  window.__a3dPatternSvgDef=function(id,n,color,unitsPerMm,scale,flipY){
    return bimPatternSvgDef(id,n,color,unitsPerMm,scale,flipY);
  };"""
NEW_WRAP = """  /* __acad3dV96: forwards its arguments instead of re-listing them. The six-parameter version
     of this wrapper silently dropped the angle bimPatternSvgDef gained in V96, and shadowed the
     second export that did pass it. */
  window.__a3dPatternSvgDef=function(){
    return bimPatternSvgDef.apply(null,arguments);
  };"""
assert txt.count(OLD_WRAP) == 1, 'wrapper count %d' % txt.count(OLD_WRAP)
txt = txt.replace(OLD_WRAP, NEW_WRAP, 1)

# and the duplicate added in 96c goes
OLD_DUP = """  window.__a3dPatternRotation=bimPatternRotation;
  window.__a3dPatternSvgDef=bimPatternSvgDef;
"""
NEW_DUP = """  window.__a3dPatternRotation=bimPatternRotation;
"""
assert txt.count(OLD_DUP) == 1, 'dup count %d' % txt.count(OLD_DUP)
txt = txt.replace(OLD_DUP, NEW_DUP, 1)

assert txt.count('window.__a3dPatternSvgDef=') == 1, 'still %d exports' % txt.count('window.__a3dPatternSvgDef=')

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
