"""patch_phase136c.py -- V136: hooks for the suite, and the marker."""
NAME = 'patch_phase136c.py'
BASE = '209a9025998f0e440e14811e64175de3a6bbcad73b0574df8954c86999cbbf90'
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


rep("""  /* __acad3dV135: find open data */
  window.__a3dFindPortals=""", """  /* __acad3dV136: the lens */
  window.__a3dLens=function(by,prop){if(by!==undefined)bimLensSet(by,prop);return bimLensSettings();};
  window.__a3dLensCol=function(id){var o=objById(id);A3D_LENS.cur=null;return o?bimLensCol(o):null;};
  window.__a3dLensValue=function(id){var o=objById(id);return o?bimLensValue(o,bimLensSettings()):null;};
  window.__a3dLensLegend=function(){return A3D.lastLensLegend?JSON.parse(JSON.stringify(A3D.lastLensLegend)):null;};
  window.__a3dLensPropKeys=function(){return bimLensPropKeys();};
  window.__a3dLensRamp=function(){return BIM_LENS_RAMP.slice();};
  window.__a3dLensNone=function(){return BIM_LENS_NONE;};
  window.__a3dDataAttrKeys=function(id){return bimDataAttrKeys(id);};
  window.__a3dDataFeatCol=function(id,fi){var L=bimDataById(id);return L?bimDataFeatCol(L,bimDataLensScale(L),fi):null;};
  window.__a3dLensCommand=function(){return bimLensCommand();};
  window.__a3dTestLegendOnPaper=function(){var s=A3D.sheetCapture;A3D.sheetCapture=true;try{drawLensLegend(el.ctx,null,0,0);}finally{A3D.sheetCapture=s;}return A3D.lastLensLegend;};
  window.__a3dTestLevelName=function(id,n){var i;for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id){A3D.levels[i].name=n;A3D_LENS.cur=null;return true;}return false;};
  window.__a3dTestObjSet=function(id,k,v){var o=objById(id);if(!o)return false;if(v===null)delete o[k];else o[k]=v;A3D_LENS.cur=null;return true;};
  window.__acad3dV136='lensby,lensusage,lenslevel,lenstype,lenslayer,lensmaterial,lensheight,lensprop,lensramp,lensnovalue,lensgl,lens2d,'+
    'lensoverpresentation,lensundo,lenssaved,lenslegend,datalens,dataopacity,lenspanel,lenscommand';
  /* __acad3dV135: find open data */
  window.__a3dFindPortals=""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
