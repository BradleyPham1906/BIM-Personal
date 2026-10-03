"""patch_phase131c.py -- V131: the hooks the suite reads usages through, and the marker."""
NAME = 'patch_phase131c.py'
BASE = '64ca7d8465ff3bb32c04b396b8f8ae059b65a8f9ad22c3913a6aa957cfea89b6'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  /* __acad3dV130: every tool in the panel, and the dock's pins */""", """  /* __acad3dV131: usages and live areas */
  window.__a3dUsages=function(){return JSON.parse(JSON.stringify(bimUsages()));};
  window.__a3dUsageDefaults=function(){return JSON.parse(JSON.stringify(BIM_USAGE_DEFAULTS));};
  window.__a3dUsageAssign=function(ids,usageId){return bimUsageAssign(ids,usageId||null);};
  window.__a3dUsageAdd=function(name){return bimUsageAdd(name);};
  window.__a3dUsageRemove=function(id){return bimUsageRemove(id);};
  window.__a3dUsageMeasure=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(bimUsageMeasure(o))):null;};
  window.__a3dUsageSummary=function(ids){return JSON.parse(JSON.stringify(bimUsageSummary(ids||null)));};
  window.__a3dUsageOf=function(id){var o=objById(id);return o?(o.usage||null):null;};
  window.__a3dExpr=function(src,vars){return bimExpr(src,vars||{});};
  window.__a3dSliceArea=function(id,y){var o=objById(id);return o?bimMeshSliceArea(o,y):null;};
  window.__acad3dV131='usagelibrary,usageintypes,usageonroomfloormass,massslicedbyfloor,floorslabgross,roomnetmeasured,'+
    'gbagfansa,formulaevaluator,formulaerrors,usageparams,usagepage,selectionareas,projectareas,usageeditor,usageschedule,'+
    'usagecommand,usagescommand,usageribbon,mirrorkeepsusage';
  /* __acad3dV130: every tool in the panel, and the dock's pins */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
