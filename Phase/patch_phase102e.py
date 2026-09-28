"""patch_phase102e.py -- __acad3dV102: marker and test surface."""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = 'f3e18696ecbecfe6db3f54d26bb39b68bbc87298e71d4b9d1fb53e5fdb6f09b6'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "  window.__acad3dV101='roomdata,roomnumbering,roomtag,tagall,taglayout,tagfollowsmove,tagdeletedwithroom,orphansweep,exportlabels';"
assert txt.count(OLD) == 1
NEW = OLD + """
  /* __acad3dV102: structural foundations and the type catalogue. */
  window.__a3dAddFootingUnder=function(hostId){var f=bimAddFootingUnder(objById(hostId));return f?f.id:null;};
  window.__a3dFootingsUnderAll=bimFootingsUnderAllColumns;
  window.__a3dFootingOf=function(hostId){var f=bimFootingOf(hostId);return f?f.id:null;};
  window.__a3dFootingVolume=function(id){return bimFootingVolume(objById(id));};
  window.__a3dTypesOf=function(cat){bimEnsureTypes();return JSON.parse(JSON.stringify(A3D.types[cat]||[]));};
  window.__a3dAssignType=function(id,typeId){var o=objById(id);if(!o||!o.bim)return false;pushUndo();var ok=bimAssignTypeTo(o,o.bim.type,typeId);saveSoon();return ok;};
  window.__a3dApplyTypeParams=function(cat,typeId,params){
    var t=bimFindType(cat,typeId),k;if(!t)return null;pushUndo();
    for(k in params)if(params.hasOwnProperty(k))t.params[k]=params[k];
    var r=bimApplyTypeToInstances(cat,typeId);saveSoon();return r;};
  window.__a3dFoundationSlabAt=function(pt,y){var o=bimFoundationSlabAt(pt,y||0);return o?o.id:null;};
  window.__a3dRectFootprint=bimRectFootprint;
  window.__acad3dV102='typecatalogue,beamtypes,footingtypes,isolatedfooting,wallfoundation,foundationslab,footingfollowshost,footingschedules,rotatedfootprintexport';"""
txt = txt.replace(OLD, NEW, 1)
for name in ['__a3dAddFootingUnder','__a3dFootingsUnderAll','__a3dFootingOf','__a3dFootingVolume','__a3dTypesOf','__a3dAssignType','__a3dApplyTypeParams','__a3dFoundationSlabAt','__a3dRectFootprint']:
    n = len(re.findall(r'window\.' + re.escape(name) + r'\s*=', txt))
    assert n == 1, '%s defined %d times' % (name, n)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
