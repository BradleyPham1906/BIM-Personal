"""patch_phase86b.py -- the palette kept keyboard focus after running a command.

Found while probing V86's own work, which is the only reason it was found at all: the command
ran, so the obvious check passed.

    after palette run, activeElement: INPUT
    typing buffer: {'active': False, 'buf': ''}

Running LINE from Cmd+K left focus in the palette's (now hidden) text input. The BIM key chain
opens with

    if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable))return;

so every keystroke after that went to the hidden input and was swallowed. The tool started and
the very next thing the user did -- type a coordinate, press C to close, press Escape to cancel --
silently did nothing.

This is worse than the dead palette it sits behind, because the command visibly works. Closing
the palette now returns focus to the drawing, which is what a command line does.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '08290189019148379a6a19008e04472d4e8c86313707e6eef034895288962703'

src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    print('ABORT: baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
    sys.exit(1)
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')
edits = 0


def sub(old, new, label, count=1):
    global text, edits
    n = text.count(old)
    if n != count:
        print('ABORT: %s: expected %d occurrence(s), found %d' % (label, count, n))
        sys.exit(1)
    text = text.replace(old, new, count)
    edits += 1
    print('  edit %d ok: %s' % (edits, label))


OLD = """    function runIdx(i){
      var c=rows[i]; if(!c) return;
      pal.classList.remove('show');"""
NEW = """    /* __acad3dV86: hand the keyboard back to the drawing.

       The BIM key chain begins "if the event target is an INPUT, return", so leaving focus in
       the palette's hidden input meant every keystroke AFTER a command was swallowed: the tool
       started, and then typing a coordinate, pressing C to close or pressing Escape to cancel
       all did nothing at all. Measured: activeElement was INPUT and the typing buffer stayed
       empty. A command line that keeps the keyboard after it runs is not a command line. */
    function closePal(){
      pal.classList.remove('show');
      try{input.blur();}catch(eB){}
      try{if(document.activeElement===input)document.body.focus();}catch(eF){}
    }
    function runIdx(i){
      var c=rows[i]; if(!c) return;
      closePal();"""
sub(OLD, NEW, 'running a command returns focus to the drawing')

OLD_ESC = "      else if(e.key==='Escape'){pal.classList.remove('show');}"
NEW_ESC = "      else if(e.key==='Escape'){closePal();}"
sub(OLD_ESC, NEW_ESC, 'dismissing the palette returns focus too')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
