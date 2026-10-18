#!/usr/bin/env python3
"""V167i: what the full regression found.

- V114 asks that every CSS rule can match something code creates. The level badges' classes
  (lv-P, lv-S, lv-U, lv-A) and an edition applied outside its place (h-outside) were made by joining
  a prefix to a value, which its reading cannot see. They are written whole now.
- V141 asks that each Properties tab is far shorter than all its groups at once. The Standards
  group, eighteen topics, the catalogue and the packs, made the Site tab nearly as long as all of
  them. It starts closed, as Graphics' Technical and Presentation do; STANDARDS and a pack being
  looked at open it.

Run from the repository root: python3 Phase/patch_phase167i.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = 'fd6db48bd2b17bd62e10b7b549245e94b7d541ecd7983d7bd32e2f2ccae9d089'   # after patch_phase167h.py

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


# ---- the badges' classes, whole ----
rep("  var BIM_STD_AREAS=[",
    "  var BIM_STD_LV_CLS={P:'lv-P',S:'lv-S',U:'lv-U',A:'lv-A'};   /* __acad3dV167i: written whole, so V114 sees them made */\n"
    "  var BIM_STD_AREAS=[")
rep("    return '<span class=\"a3d-stdlv lv-'+bimEsc(lv)+'\" title=",
    "    return '<span class=\"a3d-stdlv '+(BIM_STD_LV_CLS[lv]||'')+'\" title=")
rep("      '<span class=\"a3d-stdhow h-'+bimEsc(how)+'\">'",
    "      '<span class=\"a3d-stdhow'+(how==='outside'?' h-outside':'')+'\">'")

# ---- the group starts closed ----
rep("    'Graphics \u2014 Technical':false,'Graphics \u2014 Presentation':false};",
    "    'Graphics \u2014 Technical':false,'Graphics \u2014 Presentation':false,Standards:false};   /* __acad3dV167i: long; STANDARDS opens it */")

# ---- the marker ----
rep("whonoise,noliterals,dm2unread';", "whonoise,noliterals,dm2unread,classeswhole,groupclosed';")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
