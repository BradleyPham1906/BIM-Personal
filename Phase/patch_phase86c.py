"""patch_phase86c.py -- the prompt offered an option the keys would refuse.

Measured on V86's own build:

    0,0      -> prompt 'Specify next point or [Undo]:'          pts=1
    @10,0    -> prompt 'Specify next point or [Close/Undo]:'    pts=2   <- offers Close
    @0,-8    -> prompt 'Specify next point or [Close/Undo]:'    pts=3

but bimCanClose requires 3 points for LINE and for PLINE. So at 2 points the bracket list
advertised Close and pressing C did nothing. A prompt that lists an option the command will
refuse is the same class of fault as the dead palette this phase set out to fix -- it is just
smaller and harder to see.

THE FIX IS STRUCTURAL, not a corrected constant. The bracket list is now DERIVED from
bimCanClose, the same predicate the C key consults, so the two cannot disagree again. This is
V74's rule -- never hand-list what can be derived -- applied to a prompt string.

A DELIBERATE DEPARTURE FROM AUTOCAD, recorded so it is not mistaken for a bug. AutoCAD offers
PLINE's Close after ONE segment (two points); its own transcripts show
    Specify next point or [Arc/Close/Halfwidth/Length/Undo/Width]:
at the prompt following the second point. This app requires three points, because finishPoly
builds a closed sketch profile and a two-point "closed polyline" is a line doubled back on
itself -- a degenerate profile that Floor, Room and Roof cannot use. Offering it would produce
either an error or a bad object. So the threshold is three points for both tools, and the prompt
now says so truthfully rather than advertising AutoCAD's threshold over this app's behaviour.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '60ef43ab54c2657dbb41cbbcf843142a2d0c27ce401369f85389160f2d9ebf23'

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


HEAD = "  function bimPromptFor(sk){"
TAIL = "    var msg=(SK_TOOLS[sk.tool]||sk.tool);"

# Anchored on a SPAN rather than on reproduced text: the wall prompts contain a literal U+00B7
# in the file, and re-typing it into this patch is exactly the kind of transcription that fails
# silently. The span is located, checked for uniqueness, and replaced wholesale.
i = text.find(HEAD)
j = text.find(TAIL, i)
if i < 0 or j < 0 or text.count(HEAD) != 1:
    print('ABORT: could not locate a unique bimPromptFor span (i=%d j=%d n=%d)'
          % (i, j, text.count(HEAD)))
    sys.exit(1)

NEW = """  /* The bracket list is DERIVED from the predicates the keys themselves consult, so a prompt
     can never advertise an option the command would refuse. The first version of this function
     hard-coded the thresholds and immediately drifted: it offered [Close/Undo] at two points
     while bimCanClose required three, so C did nothing at the exact moment the prompt said it
     would.

     bimCanClose is three points for both LINE and PLINE. AutoCAD offers PLINE's Close after one
     segment, but finishPoly builds a closed sketch profile and a two-point closed polyline is a
     line doubled back on itself -- a degenerate profile Floor, Room and Roof cannot use. The
     threshold is this app's, and the prompt states this app's. */
  function bimPromptOpts(sk){
    var n=sk.pts?sk.pts.length:0,o=[];
    if(bimCanClose(sk))o.push('Close');
    if(n)o.push('Undo');
    return o.length?(' or ['+o.join('/')+']'):'';
  }
  function bimPromptFor(sk){
    var n=sk.pts?sk.pts.length:0;
    if(sk.tool==='line')return n?('Specify next point'+bimPromptOpts(sk)+':'):'Specify first point:';
    if(sk.tool==='poly')return n?('Specify next point'+bimPromptOpts(sk)+':'):'Specify start point:';
    if(sk.tool==='rect')return n?'Specify other corner point:':'Specify first corner point:';
    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';
    if(sk.tool==='wall')return n?('Wall \\u00b7 Specify next point'+bimPromptOpts(sk)+':')
                                :'Wall \\u00b7 Specify start point:';
"""
text = text[:i] + NEW + text[j:]
edits += 1
print('  edit %d ok: the bracket list is derived from the close rule' % edits)


OLD_HOOK = "  window.__a3dParseCoord=function(s){return bimParseCoordInput(s,A3D.sk);};"
NEW_HOOK = ("  window.__a3dParseCoord=function(s){return bimParseCoordInput(s,A3D.sk);};\n"
            "  window.__a3dSkPts=function(){return A3D.sk?A3D.sk.pts.map(function(p){return [p[0],p[1]];}):null;};")
sub(OLD_HOOK, NEW_HOOK, 'the sketch points are readable for verification')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
