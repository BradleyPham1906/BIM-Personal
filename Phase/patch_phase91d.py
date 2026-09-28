"""patch_phase91d.py -- Phase 91 part 4: delete the code Trim and Break no longer run.

bimTrimPolyline and bimBreakPolyline were the straight-only implementations. 91b replaced both
with the bulged versions, leaving the originals in the file with nothing calling them - and,
worse, with live test hooks, so a suite could go on "verifying" code the app never executes. That
is a false assurance, which the V85 lesson rates as worse than no check at all.

Span anchors, per the patch protocol: both regions contain non-ASCII (an em dash in the refusal
messages), so HEAD and TAIL are located and the slice between them removed, rather than retyping
the text.
"""
import hashlib, pathlib, sys

BASE = '070277a847d1415c5538ebcd369ea81c1db72429cda98df75a41ecb1674b62fb'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

out = src


def cut_span(text, head, tail, note):
    """Remove from head through the end of tail, asserting both are unique."""
    assert text.count(head) == 1, 'head not unique (%d): %s' % (text.count(head), head[:60])
    i = text.index(head)
    j = text.index(tail, i)
    assert text.count(tail, i) >= 1, 'tail not found after head'
    end = j + len(tail)
    removed = text[i:end]
    assert 'function' in removed and len(removed) > 200, 'span looks wrong: %d bytes' % len(removed)
    print('%s: removing %d bytes' % (note, len(removed)))
    return text[:i] + text[end:]


out = cut_span(
    out,
    "  function bimTrimPolyline(pts,closed,cutterPts,cutterClosed,clickPt){",
    "    return {pts:clean,cutAt:best.pt};\n  }\n",
    'bimTrimPolyline')

out = cut_span(
    out,
    "  function bimBreakPolyline(pts,closed,p1,p2){",
    "            removed:bimPolyLength(pts,false)-bimPolyLength(left,false)-bimPolyLength(right,false)};\n  }\n",
    'bimBreakPolyline')

# the hooks go with them
for hook in ("  window.__a3dBreakPolyline=bimBreakPolyline;\n",
             "  window.__a3dTrimPolyline=bimTrimPolyline;\n"):
    assert out.count(hook) == 1, 'hook not unique: %s' % hook.strip()
    out = out.replace(hook, '', 1)

for name in ('bimTrimPolyline', 'bimBreakPolyline'):
    assert name not in out, '%s still appears in the file' % name

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (%+d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
