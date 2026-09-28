"""patch_phase91e.py -- Phase 91 part 5: "nothing on that side" means zero LENGTH.

Found by the V87 suite immediately after 91d repointed it at the live function, which is the
whole argument for repointing it rather than deleting it: breaking exactly at an endpoint
produces a piece with two IDENTICAL points - two points, no length - and a vertex-count guard
accepts it happily. The straight-only code deduplicated first and so never saw the case.

Trim gets the same treatment: trimming at a wall's own endpoint has the same degenerate outcome.
"""
import hashlib, pathlib, sys

BASE = '05903060ae2b978ad8ee95ee8e6bc8704f7599c8ba92115ec42e9855f0330d5b'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

reps.append(("""    if(s1.a.pts.length<2)
      return {error:'That break point is at the start of the wall — there would be nothing on that side'};
    if(s2.b.pts.length<2)
      return {error:'That break point is at the end of the wall — there would be nothing on that side'};""",
"""    /* "Nothing on that side" means ZERO LENGTH, not fewer than two points. Splitting exactly at
       an endpoint yields a piece with two IDENTICAL points - a two-point wall of no length -
       which a vertex count accepts. The straight-only code this replaced deduplicated first and
       so never met the case. */
    if(bimBulgedLength(s1.a.pts,s1.a.bulges,false)<1e-9)
      return {error:'That break point is at the start of the wall — there would be nothing on that side'};
    if(bimBulgedLength(s2.b.pts,s2.b.bulges,false)<1e-9)
      return {error:'That break point is at the end of the wall — there would be nothing on that side'};""", 1))

reps.append(("""    var keep=((click.seg+click.t)>(best.seg+best.t))?split.a:split.b;
    if(keep.pts.length<2)return {error:'Trim would remove the whole wall'};""",
"""    var keep=((click.seg+click.t)>(best.seg+best.t))?split.a:split.b;
    /* Same rule as Break: a cut at the wall's own end leaves two coincident points, which is
       not a wall. Measured, not counted. */
    if(bimBulgedLength(keep.pts,keep.bulges,false)<1e-9)
      return {error:'Trim would remove the whole wall'};""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
