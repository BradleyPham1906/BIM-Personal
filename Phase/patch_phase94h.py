"""patch_phase94h.py -- __acad3dV94: the SECOND Canvas-era letter gate.

94g fixed one of them. Law 2 says grep for the same mistake before believing a fix is done,
and this is the case that proves it: there are TWO capture-phase gates on window that swallow
plain letters ahead of the drafting engine, one at "Capture before the old single-key shortcut
listener" and one in installFinalSafeShortcutGate. Fixing only the first left V and H just as
dead as they were, and the suite said so.

The second gate blocks one letter more than the first -- 's' -- so its delegation is written
against the same predicate rather than the same list.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'c5307233175bca264d85a9ae30885368bdd7720e6912403c2b5e91b9e0dceea4'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """    // Always block old unmodified letter shortcuts before they reach legacy handlers.
    if(!mod && ['v','h','n','s'].includes(k)){e.stopImmediatePropagation();return}"""

NEW = """    // Always block old unmodified letter shortcuts before they reach legacy handlers.
    if(!mod && ['v','h','n','s'].includes(k)){
      /* __acad3dV94: the second of two capture-phase gates doing this. Both are registered on
         window at load, ahead of the BIM engine's own handler, so these letters have never
         reached the drafting workspace. Delegated, not duplicated: the drawing says whether it
         wants the key, and anything it does not want is still swallowed exactly as before. */
      try{ if(window.__a3dOn&&window.__a3dWantsKey&&window.__a3dWantsKey(e))return; }catch(err4){}
      e.stopImmediatePropagation();return;
    }"""

assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
