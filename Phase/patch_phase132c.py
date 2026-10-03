"""patch_phase132c.py -- V132: the hooks the suite reads the map through, and the marker."""
NAME = 'patch_phase132c.py'
BASE = '52ebb7386b762ea980bac2b56416a4f15324799a84f8f3fcbdac26925fd865c2'
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


rep("""  /* __acad3dV131: usages and live areas */""", """  /* __acad3dV132: the map */
  window.__a3dModelToGeo=function(x,z){return bimModelToGeo(x,z);};
  window.__a3dGeoToModel=function(lon,lat){return bimGeoToModel(lon,lat);};
  window.__a3dMapSettings=function(){return bimMapSettings();};
  window.__a3dMapSet=function(f,v){return bimMapSet(f,v);};
  window.__a3dMapCommand=function(){return bimMapCommand();};
  window.__a3dMapTiles=function(){
    var c=A3D.cam,r=bimMapPlan(camVecs(c),cvW(),cvH());
    return {style:r.style,reason:r.reason,z:r.z,mpp:r.mpp||null,extent:r.extent||null,
      tiles:r.tiles.map(function(x){return {x:x.x,y:x.y,z:x.z,url:bimMapTileUrl(r.tpl,x.x,x.y,x.z)};})};
  };
  window.__a3dMapTileCorners=function(x,y,z){var o=bimMapOrigin();return o?bimMapTileCorners({x:x,y:y,z:z},o,0):null;};
  window.__a3dMapDrawn=function(){return A3D.lastMapDrawn?JSON.parse(JSON.stringify(A3D.lastMapDrawn)):null;};
  window.__a3dMapFooter=function(){return bimMapFooterHtml();};
  window.__a3dMapCache=function(){
    var k,s={ok:0,loading:0,fail:0},n=0;
    for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)){n++;s[A3D_MAP.cache[k].state]=(s[A3D_MAP.cache[k].state]||0)+1;}
    return {n:n,count:A3D_MAP.n,inflight:A3D_MAP.inflight,states:s,fail:JSON.parse(JSON.stringify(A3D_MAP.fail))};
  };
  window.__a3dMapFind=function(q){return bimMapFind(q);};
  window.__a3dMapFindReset=function(){A3D_MAP.lastFind=0;};
  window.__a3dGeoImportText=function(text,name){return bimGeoImportText(text,name);};
  window.__a3dGeoExport=function(){return JSON.parse(JSON.stringify(bimGeoExportFC()));};
  window.__a3dGeoOf=function(id){var o=objById(id);return o&&o.geo?JSON.parse(JSON.stringify(o.geo)):null;};
  /* the camera's fields, set and painted: the suite's views of the map at a known scale */
  window.__a3dCamSet=function(c){
    var k;
    for(k in c)if(c.hasOwnProperty(k)&&typeof c[k]==='number'&&isFinite(c[k])&&A3D.cam.hasOwnProperty(k))A3D.cam[k]=c[k];
    paint();
    return JSON.parse(JSON.stringify(A3D.cam));
  };
  window.__acad3dV132='mapstyles,mapoffbydefault,georefwgs84,truenorthonmap,webmercatortiles,zoomfrommpp,tilecap,'+
    'tilestore,parentfallback,corsfailuresnamed,glbasemap,canvasbasemap,notonpaper,mapcredit,mapsettingsinsite,'+
    'nominatimfind,onefindasecond,geojsonimport,kmlimport,projectedrefused,sitedatalayer,geojsonexport,massfootprint,'+
    'mapcommand,findaddresscommand,geoimportcommand,geoexportcommand,mapribbon';
  /* __acad3dV131: usages and live areas */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
