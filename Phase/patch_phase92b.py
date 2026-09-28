"""patch_phase92b.py -- Phase 92 part 2: Extend and Lengthen run on the curve, and the
straight-only versions are deleted.

Same shape as V91: one implementation, the V89 refusals removed, and the replaced functions taken
out of the file along with their test hooks so no suite can verify code the app never runs.
"""
import hashlib, pathlib, sys

BASE = 'f0b308b4449198cec95f0aac3fa3786cd33370db4a2acdee371a5b977204fff7'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

reps.append(("""      if(bimRefuseIfCurved(target,'Extend')||bimRefuseIfCurved(bound,'Extend'))return false;   /* __acad3dV89 */
      var r=bimExtendPolyline(target.bim.centerline,target.bim.closed,
                              bound.bim.centerline,bound.bim.closed,clickPt);
      if(r.error){a3dToast('Extend: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(target,r.pts,target.bim.closed);""",
"""      /* __acad3dV92: an arc end extends along its own circle. */
      var r=bimExtendBulged(target.bim.centerline,target.bim.bulges,target.bim.closed,
                            bound.bim.centerline,bound.bim.bulges,bound.bim.closed,clickPt);
      if(r.error){a3dToast('Extend: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(target,r.pts,target.bim.closed,r.bulges);""", 1))

reps.append(("""      if(bimRefuseIfCurved(w,'Lengthen'))return false;   /* __acad3dV89 */
      var r=bimLengthenPolyline(w.bim.centerline,w.bim.closed,mode,value,clickPt);
      if(r.error){a3dToast('Lengthen: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.pts,w.bim.closed);""",
"""      /* __acad3dV92: on an arc this changes the sweep, not the radius. */
      var r=bimLengthenBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,mode,value,clickPt);
      if(r.error){a3dToast('Lengthen: '+r.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.pts,w.bim.closed,r.bulges);""", 1))

# the Lengthen dialog quotes the current length, which must now be the arc length
reps.append(("""    var cur=bimPolyLength(w.bim.centerline,w.bim.closed);""",
"""    var cur=bimBulgedLength(w.bim.centerline,w.bim.bulges,w.bim.closed);   /* __acad3dV92 */""", 1))

# ---- hooks and marker -------------------------------------------------------------------------
reps.append(("""  /* __acad3dV91 */
  window.__a3dProjectOntoBulged=bimProjectOntoBulged;""",
"""  /* __acad3dV92 */
  window.__a3dGrowEnd=bimGrowEnd;
  window.__a3dLengthenBulged=bimLengthenBulged;
  window.__a3dExtendBulged=bimExtendBulged;
  window.__acad3dV92='arcextend,arclengthen,growendsweep,startendasymmetry,straightonlyversionsdeleted';
  /* __acad3dV91 */
  window.__a3dProjectOntoBulged=bimProjectOntoBulged;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)


def cut_span(text, head, tail, note):
    assert text.count(head) == 1, 'head not unique (%d): %s' % (text.count(head), head[:60])
    i = text.index(head)
    j = text.index(tail, i)
    end = j + len(tail)
    removed = text[i:end]
    assert 'function' in removed and len(removed) > 200, 'span looks wrong: %d bytes' % len(removed)
    print('%s: removing %d bytes' % (note, len(removed)))
    return text[:i] + text[end:]


out = cut_span(
    out,
    "  function bimExtendPolyline(pts,closed,bPts,bClosed,clickPt){",
    "    return {pts:out,atPt:[best.pt[0],best.pt[1]],endIdx:endIdx,added:best.t};\n  }\n",
    'bimExtendPolyline')
out = cut_span(
    out,
    "  function bimLengthenPolyline(pts,closed,mode,value,clickPt){",
    "    return {pts:out,length:target,delta:change,endIdx:endIdx};\n  }\n",
    'bimLengthenPolyline')

for hook in ("  window.__a3dExtendPolyline=bimExtendPolyline;\n",
             "  window.__a3dLengthenPolyline=bimLengthenPolyline;\n"):
    assert out.count(hook) == 1, 'hook not unique: %s' % hook.strip()
    out = out.replace(hook, '', 1)

for name in ('bimExtendPolyline', 'bimLengthenPolyline',
             "bimRefuseIfCurved(target,'Extend')", "bimRefuseIfCurved(w,'Lengthen')"):
    assert name not in out, '%s survived' % name

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (%+d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
