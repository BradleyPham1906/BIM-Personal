"""patch_phase94c.py -- __acad3dV94: the mode keys.

H, V and A at the first prompt, exactly where AutoCAD offers them. The keys are resolved
through bimClineModeForKey, which reads the same table bimClineModeLabels prints, so a key and
the prompt that advertises it cannot drift apart.

Placed ahead of the V90 arc-mode branch deliberately: 'A' means arc there and angle here, and
bimCanArc is false for a construction line, but relying on that ordering by accident is how the
next tool to want 'A' breaks this one.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'f0fa1766e4471a7f9974b4bb93c31e6c45db9824fc7db45bed39637d9c730cc1'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """      }else{
        if((ev.key==='u'||ev.key==='U')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.pts.length){
          bimUndoLastPoint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }"""

NEW = """      }else{
        /* __acad3dV94: XLINE's construction modes, claimed before any other tool's letters so
           the match is explicit rather than a consequence of branch order. */
        if(A3D.sk.tool==='xline'&&!ev.ctrlKey&&!ev.metaKey&&bimClineCanSetMode(A3D.sk)){
          var clMode=bimClineModeForKey(ev.key);
          if(clMode){
            bimSetClineMode(A3D.sk,clMode);
            ev.preventDefault();ev.stopImmediatePropagation();return;
          }
        }
        if((ev.key==='u'||ev.key==='U')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.pts.length){
          bimUndoLastPoint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }"""

assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
