"""patch_phase118c.py -- V118: after any field's change, Properties shows the model -- one refresh,
registered last, in place of V105's room-field workaround and of each branch remembering.

V105 deferred the room fields' rebuild to a timer and then focused, by key, the field a Tab or Enter
had been aimed at, because the rebuild destroyed the field the browser was about to focus. The rebuild
keeps its elements now (118a), so the browser's own Tab lands where it was aimed, and a click into
another field is kept too -- which the workaround could not do. It goes.

And a refused edit has to show the model again, which each branch had to remember: most did, and the
wall's Type did not. Measured: on a pinned wall, the Type dropdown's change was refused ("pinned --
unpin to change its type") and the dropdown went on showing the type the wall does not have. One
delegate, registered after every other change handler on the panel, re-renders it from the model
whatever the handlers did -- applied, refused, or refused without saying so."""
NAME = 'patch_phase118c.py'
BASE = 'fe0d5c45702374a267dd64f923338bf31b976ce98d12f4d0c653df0d7666d5b6'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
rep("      /* __acad3dV105: rebuild once the focus has settled, then put the cursor where the user sent\n"
    "         it -- the field a Tab or Enter was aimed at. The edit rebuilds the panel before the\n"
    "         browser moves the focus, so a Tab from Occupancy to Load Factor -- the way these two are\n"
    "         filled in -- used to leave the cursor nowhere. */\n"
    "      setTimeout(function(){\n"
    "        var ae=document.activeElement,k=A3D.roomFieldNext||((ae&&ae.getAttribute)?ae.getAttribute('data-roomf'):null),n;\n"
    "        A3D.roomFieldNext=null;\n"
    "        refreshProps();\n"
    "        if(k&&el.propsbody){n=el.propsbody.querySelector('[data-roomf=\"'+k+'\"]');if(n)n.focus();}\n"
    "      },0);\n"
    "    });\n",
    r'''      /* __acad3dV118: V105 deferred the rebuild to a timer here and refocused the field a Tab or Enter
         had been aimed at, because the rebuild used to destroy the field the browser was about to
         focus. The rebuild keeps its elements now, and the panel's last change delegate shows the
         model after every edit. */
    });
''')
rep("    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){   /* __acad3dV105: where Tab / Enter was aimed */\n"
    "      if(ev.key!=='Tab'&&ev.key!=='Enter')return;\n"
    "      var ri=ev.target&&ev.target.closest?ev.target.closest('[data-roomf]'):null;\n"
    "      if(!ri)return;\n"
    "      var all=Array.prototype.slice.call(el.propsbody.querySelectorAll('[data-roomf]')),i=all.indexOf(ri);\n"
    "      var nx=ev.key==='Enter'?ri:all[i+(ev.shiftKey?-1:1)];\n"
    "      A3D.roomFieldNext=nx?nx.getAttribute('data-roomf'):null;\n"
    "      setTimeout(function(){A3D.roomFieldNext=null;},60);   /* no edit, no change event: forget it */\n"
    "    });\n", "")
rep("      bimSetGraphicsOverride(go,gmode,gkey,gval);\n      refreshProps();saveSoon();\n    });\n    el.pill=root.querySelector('#a3d-navgrp');",
    "      bimSetGraphicsOverride(go,gmode,gkey,gval);\n      refreshProps();saveSoon();\n    });\n"
    r'''    /* __acad3dV118: whatever a field's change did -- applied, refused, or refused without saying so --
       the panel ends showing the model. Registered after every other change handler on the panel, so
       it runs last. A refused Type change on a pinned wall used to leave the dropdown showing a type
       the wall does not have, because that one branch did not refresh; now no branch has to. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(){
      try{refreshProps();}
      catch(eRP){console.warn('[BIM] Properties could not be refreshed after an edit.',eRP);a3dToast('Properties could not be refreshed - see the console');}
    });
    el.pill=root.querySelector('#a3d-navgrp');''')
if 'roomFieldNext' in t:
    sys.exit('ABORT: V105\'s refocus is still referenced')
last = t.index("the panel ends showing the model. Registered after every other change handler")
k = t.find("el.propsbody.addEventListener('change'", last)
if t.find("el.propsbody.addEventListener('change'", k + 1) >= 0:
    sys.exit('ABORT: a change handler on the panel is registered after the refresh that must run last')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
