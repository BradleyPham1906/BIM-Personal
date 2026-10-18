#!/usr/bin/env python3
"""V167e: the version, the phase marker and the hooks the suite drives the Standards group with.

Run from the repository root: python3 Phase/patch_phase167e.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'af71b87a7543940a7516173dad0722aca90ad2952d7c51417f9c4ac2fa12ad6d'   # after patch_phase167d.py

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


rep("  var BIM_APP_VERSION={v:'V166',date:'2026-10-12'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166 */",
    "  var BIM_APP_VERSION={v:'V167',date:'2026-10-18'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167 */")

HOOKS = r'''  window.__a3dStdCommand=function(){return bimStdCommand();};
  window.__a3dStdUi=function(){return JSON.parse(JSON.stringify({open:A3D_STD_UI.open,edit:A3D_STD_UI.edit,place:A3D_STD_UI.place,pending:A3D_STD_UI.pending?{file:A3D_STD_UI.pending.file,diff:A3D_STD_UI.pending.diff}:null}));};
  window.__a3dStdPackLook=function(text,file){return bimStdPackLook(text,file);};
  window.__a3dDgStdChanged=function(a){return bimDgStdChanged(a);};
  window.__a3dSaStdText=function(auto){return bimSaStdText({auto:auto});};
  window.__acad3dV167='registry,records,reader,place,placefromaddress,date,overrides,reasons,ordered,picks,stamps,outofdate,findingstd,accessstd,contextstd,packs,sha256,packdiff,catalogue,standardsgroup,standardscommand,valuesinwords';
'''
rep("  window.__acad3dV166b=", HOOKS + "  window.__acad3dV166b=")
for name in ['__a3dStdCommand', '__a3dStdUi', '__a3dStdPackLook', '__a3dDgStdChanged', '__a3dSaStdText', '__acad3dV167']:
    n = s.count('window.%s=' % name)
    if n != 1:
        sys.exit('window.%s= defined %d times' % (name, n))

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
