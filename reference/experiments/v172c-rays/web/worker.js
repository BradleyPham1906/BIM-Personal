/* V172c experiment: the whole pipeline in a classic worker, as the app's Ladybug worker is. */
var module=undefined;
importScripts('runtime/pyodide/0.29.5/pyodide.js','wasi-run.js','bvh.js','scene.js');
function say(m){postMessage(m);}
var box=self.box;
(async function(){
  var T={},t=Date.now();
  var py=await loadPyodide({indexURL:new URL('runtime/pyodide/0.29.5/',location.href).href});T.pyodide=Date.now()-t;t=Date.now();
  var wh=['ladybug_geometry-1.35.7','ladybug_core-0.44.63','ladybug_comfort-0.19.13','click-8.3.3','ladybug_radiance-0.2.12'];
  var sp=py.runPython('import site\nsite.getsitepackages()[0]');
  for(var i=0;i<wh.length;i++){var b=await (await fetch('runtime/wheels/'+wh[i]+'-py3-none-any.whl')).arrayBuffer();py.unpackArchive(b,'wheel',{extractDir:sp});}
  T.wheels=Date.now()-t;t=Date.now();
  await py.loadPackage('numpy');T.numpy=Date.now()-t;t=Date.now();
  var mod=await WebAssembly.compile(await (await fetch('runtime/radiance/gendaymtx.wasm')).arrayBuffer());T.wasm=Date.now()-t;
  self.bimGendaymtx=function(args,wea){var r=bimWasiRun(mod,['gendaymtx'].concat(args.toJs()),new TextEncoder().encode(wea));
    if(r.code)throw new Error('gendaymtx exit '+r.code+': '+new TextDecoder().decode(r.stderr));return r.stdout;};
  py.FS.writeFile('/tmp/site.epw',new Uint8Array(await (await fetch('site.epw')).arrayBuffer()));
  t=Date.now();
  var sky=JSON.parse(py.runPython([
    'import os, json','os.makedirs("/tmp/sky", exist_ok=True)','from js import bimGendaymtx',
    'from ladybug_radiance.skymatrix import SkyMatrix',
    'def _run(self, wea_file, wea_duration):','    density = 2 if self.high_density else 1','    txt = open(wea_file).read()',
    '    d = bimGendaymtx(["-m", str(density), "-d", "-O1", "-A"], txt).to_py().tobytes()',
    '    s = bimGendaymtx(["-m", str(density), "-s", "-O1", "-A"], txt).to_py().tobytes()',
    '    return self._parse_mtx_data(d, wea_duration, density), self._parse_mtx_data(s, wea_duration, density)',
    'SkyMatrix._run_gendaymtx = _run','SKY = SkyMatrix.from_epw("/tmp/site.epw")','SKY.folder = "/tmp/sky"','SKY.compute_sky()',
    'json.dumps([SKY.direct_values, SKY.diffuse_values])'].join('\n')));
  T.sky=Date.now()-t;
  var ref=await (await fetch('ref_sky_phl.json')).json(),md=0;
  for(i=0;i<145;i++){md=Math.max(md,Math.abs(sky[0][i]-ref.tregenza.dir[i]),Math.abs(sky[1][i]-ref.tregenza.dif[i]));}
  T.skyMaxDiff=md;
  var D=await (await fetch('dome.json')).json(),V=D.tregenza.v.concat(D.tregenza.v.map(function(a){return [-a[0],-a[1],-a[2]];}));
  T.runs=[];
  for(var n of [100,1000,4000]){
    var g=Math.ceil(Math.sqrt(n)),sens=[],tris=[],seed=7,k;
    function rnd(){seed=(seed*16807)%2147483647;return seed/2147483647;}
    for(k=0;k<n;k++){var x=(k%g)*40,y=Math.floor(k/g)*40,bx=box(x,y,0,x+24,y+24,12+28*rnd());sens=sens.concat(bx.f);tris=tris.concat(bx.o.tris);}
    t=Date.now();var H=bimBvhBuild(tris),tb=Date.now()-t;t=Date.now();
    var M=new Float64Array(sens.length*V.length),j,s,o,c;
    for(k=0;k<sens.length;k++){s=sens[k];o=[s.p[0]+s.n[0]*0.01,s.p[1]+s.n[1]*0.01,s.p[2]+s.n[2]*0.01];
      for(j=0;j<V.length;j++){c=s.n[0]*V[j][0]+s.n[1]*V[j][1]+s.n[2]*V[j][2];if(c>0&&!bimBvhBlocked(H,o,V[j]))M[k*V.length+j]=c;}}
    var tr=Date.now()-t;t=Date.now();
    py.globals.set('_M',M);py.globals.set('_rows',sens.length);
    var tot=py.runPython([
      'import numpy as np','from ladybug_radiance.study.radiation import RadiationStudy',
      'from ladybug_geometry.geometry3d import Mesh3D, Point3D',
      'st = RadiationStudy.__new__(RadiationStudy)','st._sky_matrix = SKY',
      'st._intersection_matrix = np.asarray(_M.to_py()).reshape(_rows, 290)','st._radiation_values = None',
      'RadiationStudy.compute(st)','float(sum(st._radiation_values))'].join('\n'));
    T.runs.push({boxes:n,faces:sens.length,triangles:tris.length,bvh_ms:tb,rays_ms:tr,ladybug_sum_ms:Date.now()-t,sum_kwh_m2:tot});
  }
  say({ok:true,T:T,ua:navigator.userAgent});
})().catch(function(e){say({ok:false,err:String(e&&e.stack||e)});});
