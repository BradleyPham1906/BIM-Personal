"""patch_phase133c.py -- V133: the hooks the suite reads the site context through, and the marker."""
NAME = 'patch_phase133c.py'
BASE = '1511f9d0405a5cab9482b958ae7e7af4111413cf7af0c49149e30d7aabd5e110'
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


rep("""  /* __acad3dV132: the map */
  window.__a3dModelToGeo""", """  /* __acad3dV133: site context */
  window.__a3dCtxSettings=function(){return bimCtxSettings();};
  window.__a3dCtxSet=function(f,v){return bimCtxSet(f,v);};
  window.__a3dCtxArea=function(){return bimCtxArea();};
  window.__a3dCtxQuery=function(){var a=bimCtxArea();return a?bimCtxQuery(a,bimCtxSettings().kinds):null;};
  window.__a3dCtxFetch=function(){return bimCtxFetch();};
  window.__a3dCtxBusy=function(){return !!A3D_CTX.busy;};
  window.__a3dCtxRemove=function(){return bimCtxRemove();};
  window.__a3dCtxOf=function(id){var o=objById(id);return o&&o.context?JSON.parse(JSON.stringify(o.context)):null;};
  window.__a3dCtxHeight=function(tags){return bimOsmHeight(tags);};
  window.__a3dCtxRings=function(members,role){return bimOsmRings(members,role);};
  window.__a3dCtxCredit=function(){return bimCtxCreditHtml(false);};
  window.__a3dCtxDatum=function(){return bimCtxDatum();};
  window.__acad3dV133='contextarea,overpassquery,osmkinds,multipolygonrings,buildingheights,extrudedbuildings,roadswatergreentrees,'+
    'terrarium,bilinearground,terraindatum,contextlayers,pinned,replacebykind,oneundo,failuresnamed,contextcredit,contextexport,'+
    'notamass,contextproperties,contextcommand,contextremove,contextribbon';
  /* __acad3dV132: the map */
  window.__a3dModelToGeo""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
