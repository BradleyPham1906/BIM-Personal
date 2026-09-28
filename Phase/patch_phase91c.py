"""patch_phase91c.py -- Phase 91 part 3: name the Break measurement for what it is.

91b left the removed-length calculation correct but reading badly: a variable called `gone` that
actually holds the length of the piece that SURVIVED. Renamed while the reasoning is still fresh,
because the next person to read that line will be trying to work out whether it is right.
"""
import hashlib, pathlib, sys

BASE = '140e394cf723214be24d28b6150d7dbae209d359fb9eff55cd4e2518c918e455'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

OLD = """      var gone=bimBulgedLength(w.bim.centerline,w.bim.bulges,false);
      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.max(0,before-gone-bimBulgedLength(made.obj.bim.centerline,made.obj.bim.bulges,false)))+' removed')
                 :'Split into 2 walls');"""
NEW = """      /* What was removed is what neither surviving piece accounts for. Measured after the
         rebuild, on the arc lengths, so a curved break reports the length of the CURVE that
         went rather than the chord across the gap. */
      var keptA=bimBulgedLength(w.bim.centerline,w.bim.bulges,false);
      var keptB=bimBulgedLength(made.obj.bim.centerline,made.obj.bim.bulges,false);
      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.max(0,before-keptA-keptB))+' removed')
                 :'Split into 2 walls');"""
assert src.count(OLD) == 1, 'anchor count %d' % src.count(OLD)
out = src.replace(OLD, NEW, 1)
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
