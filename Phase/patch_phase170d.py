#!/usr/bin/env python3
"""V170d: on a phone or a tablet (up to 1024 px, where V169's bar already ran past the screen at 768), Play and Stop
first in the status bar, as icons with their names for screen readers, the
level's caption giving them its room (the selector says "Level 0" itself); the hooks read the frame last drawn.

Run from the repository root: python3 Phase/patch_phase170d.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = 'e07cfbefb49de515d160e5417418ff5e7908df324ec6c65196ed00e73c36bedf'   # V170c

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


rep("@media(max-width:720px),(max-height:500px){.a3d-mapattr{top:4px;bottom:auto;left:6px;right:auto;max-width:70%}}\n",
    "@media(max-width:720px),(max-height:500px){.a3d-mapattr{top:4px;bottom:auto;left:6px;right:auto;max-width:70%}}\n"
    "@media(max-width:1024px),(max-height:500px){#a3d-animgrp{order:-1;margin-left:0;padding-left:0;border-left:0;padding-right:6px;border-right:1px solid #3a4048}#a3d-animgrp .a3d-stbtn span{display:none}#a3d-statusbar.a3d-hasanim .a3d-stlvl{font-size:0;gap:0}}/* __acad3dV170: first, as icons, on a phone or a tablet, where the bar runs past the screen */\n")
rep("""      g.hidden=!can;
      b.innerHTML=(A3D_ANIM.on?PILL_PAUSE:PILL_PLAY)+'<span>'+(A3D_ANIM.on?'PAUSE':'PLAY')+'</span>';
""", """      g.hidden=!can;
      var bar=document.getElementById('a3d-statusbar');if(bar)bar.classList.toggle('a3d-hasanim',can);
      b.innerHTML=(A3D_ANIM.on?PILL_PAUSE:PILL_PLAY)+'<span>'+(A3D_ANIM.on?'PAUSE':'PLAY')+'</span>';
      b.setAttribute('aria-label',A3D_ANIM.on?'Pause':'Play');
""")
rep("""'<button class="a3d-stbtn" id="a3d-animplay" data-a3danim="play" aria-pressed="false" title="Play the site analysis in motion">'""",
    """'<button class="a3d-stbtn" id="a3d-animplay" data-a3danim="play" aria-pressed="false" aria-label="Play" title="Play the site analysis in motion">'""")
rep("""'<button class="a3d-stbtn" id="a3d-animstop" data-a3danim="stop" title="Stop: the still drawing" hidden>'""",
    """'<button class="a3d-stbtn" id="a3d-animstop" data-a3danim="stop" aria-label="Stop" title="Stop: the still drawing" hidden>'""")
rep("  window.__a3dAnim=function(){var F=bimAnimFrame();",
    "  window.__a3dAnim=function(){var F=A3D_ANIM.fr||bimAnimFrame();")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
