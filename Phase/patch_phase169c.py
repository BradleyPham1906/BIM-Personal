#!/usr/bin/env python3
"""V169c: assets -- the hooks, the version and the marker.

Run from the repository root: python3 Phase/patch_phase169c.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '48c684e9a8ee150de745a03e43165cbef2be176947fc884612d0a65ebdc46c26'   # V169b

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


rep("var BIM_APP_VERSION={v:'V168',date:'2026-10-18'};", "var BIM_APP_VERSION={v:'V169',date:'2026-10-19'};")

HOOKS = r'''  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry';
  window.__a3dEntKinds=function(){return BIM_ENT.map(function(e){return {k:e.k,name:e.name,cat:e.cat,kind:e.kind,p:JSON.parse(JSON.stringify(e.p))};});};
  window.__a3dEntPlace=function(key,x,z,p){var o=bimEntPlace(key,[x,z],p||null);return o?o.id:null;};
  /* an asset as placed: its parameters, its frame, and its size in its own frame (the markers left out) */
  window.__a3dEntInfo=function(id){
    var o=objById(id);
    if(!o||!o.asset||!o.mesh)return null;
    var F=bimEntFrame(o),q=bimObjOffset(o),v=o.mesh.v,ca=Math.cos(F.a),sa=Math.sin(F.a),mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],i,k;
    for(i=2;i<v.length;i++){
      var dx=v[i][0]-F.c[0],dz=v[i][2]-F.c[1],L=[dx*ca-dz*sa,v[i][1]-F.y,dx*sa+dz*ca];
      for(k=0;k<3;k++){if(L[k]<mn[k])mn[k]=L[k];if(L[k]>mx[k])mx[k]=L[k];}
    }
    return {k:o.asset.k,key:o.asset.key,p:JSON.parse(JSON.stringify(o.asset.p||{})),cf:o.asset.cf,heading:F.a,centre:[F.c[0]+q[0],F.c[1]+q[2]],base:q[1]+F.y,
      min:mn,max:mx,size:[mx[0]-mn[0],mx[1],mx[2]-mn[2]],faces:o.mesh.f.length,verts:v.length,name:o.name,col:o.col,layer:o.layer,
      body:o.asset.k==='person'?bimEntBody(o.asset.p||{}):null,tree:o.asset.k==='tree'?bimEntTreeSize(o.asset.p||{}):null};
  };
  window.__a3dEntSet=function(id,key,val){var o=objById(id);return o&&o.asset?bimEntPropSet(o,key,val,val===true):false;};
  window.__a3dEntInLeaf=function(date){return bimEntInLeaf(date);};
  window.__a3dEntSeason=function(){var G=bimEntSeason();return G?JSON.parse(JSON.stringify(G)):null;};
  window.__a3dClimGsl=function(js,lat){var G=bimClimGsl(js,lat);return G?{s:G.s,e:G.e,years:G.years,sh:G.sh}:null;};
  window.__a3dEntTurns=function(){return {turns:bimEntTurns(),drawn:A3D.lastTurns||0};};
  window.__a3dEntCrown=function(tags){return {ratio:bimEntCrownRatio(tags||{}),leaf:bimEntLeafOf(tags||{})};};
  /* the faces each solid casts a shadow with, on a date */
  window.__a3dShadowFaces=function(date){var L=bimShadowCasters(bimShadowGround(),date),o={};L.forEach(function(it){o[it.id]=it.f.length;});return o;};
'''
rep("  window.__a3dLand=function(){\n", HOOKS + "  window.__a3dLand=function(){\n")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
