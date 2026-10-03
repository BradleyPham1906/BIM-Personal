"""patch_phase134c.py -- V134: the hooks the suite reads the data layers through, and the marker."""
NAME = 'patch_phase134c.py'
BASE = 'b65df9b4dee496195e3d18e88045d8087da690cba6960f7f442908f1ac7b0c96'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')
old = """  /* __acad3dV133: site context */
  window.__a3dCtxSettings"""
assert t.count(old) == 1
t = t.replace(old, """  /* __acad3dV134: data layers */
  window.__a3dDataLayers=function(){return JSON.parse(JSON.stringify(bimDataList()));};
  window.__a3dDataFeatures=function(id){return JSON.parse(JSON.stringify(bimDataFeats(id)));};
  window.__a3dDataPresets=function(){return JSON.parse(JSON.stringify(BIM_DATA_PRESETS));};
  window.__a3dDataKind=function(u){return bimDataKind(u);};
  window.__a3dDataQueryUrl=function(id){var L=bimDataById(id),a=bimCtxArea();return L&&a?bimDataQueryUrl(L,a):null;};
  window.__a3dDataAdd=function(u,n,c,cr){var id=bimDataAdd(u,n,c,cr);return Promise.resolve(id?A3D_DATA.pending[id]:null).then(function(r){return {id:id,result:r||null};});};
  window.__a3dDataFetch=function(id){return Promise.resolve(bimDataFetch(id));};
  window.__a3dDataBusy=function(id){return !!A3D_DATA.busy[id];};
  window.__a3dDataRemove=function(id){return bimDataRemove(id);};
  window.__a3dDataSet=function(id,f,v){return bimDataSet(id,f,v);};
  window.__a3dDataPick=function(sx,sy){return bimDataPick(sx,sy);};
  window.__a3dDataSel=function(){return A3D_DATA.sel?JSON.parse(JSON.stringify(A3D_DATA.sel)):null;};
  window.__a3dDataSelect=function(layer,fi){A3D_DATA.sel=layer?{layer:layer,fi:fi}:null;refreshProps();paint();return true;};
  window.__a3dDataToProperty=function(){var p=bimDataToProperty();return p?p.id:null;};
  window.__a3dDataDrawn=function(){return A3D.lastDataDrawn||0;};
  window.__a3dDataCredit=function(){return bimDataCreditHtml();};
  window.__acad3dV134='datakinds,arcgisquery,wfsgetfeature,geojsonfile,presets,areafilter,maxfeatures,featuresoutsideundo,'+
    'featuressaved,planoverlay,notonpaper,clicktoread,pickorder,parceltoproperty,failuresnamed,datacredit,datapanel,datacommand';
""" + old)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
