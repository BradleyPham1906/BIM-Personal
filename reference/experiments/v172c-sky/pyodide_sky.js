// V172c experiment: Ladybug's SkyMatrix in Pyodide 0.29.5 (the committed runtime), gendaymtx as WebAssembly.
var fs=require('fs'),S=process.argv[2],R=process.argv[3],EPW=process.argv[4];
var run=require(__dirname+'/wasi-run.js');
var mod=new WebAssembly.Module(fs.readFileSync(S+'/wasi/gendaymtx.wasm'));
globalThis.bimGendaymtx=function(args,wea){
  var r=run(mod,['gendaymtx'].concat(args.toJs?args.toJs():args),new TextEncoder().encode(wea));
  if(r.code)throw new Error('gendaymtx exit '+r.code+': '+new TextDecoder().decode(r.stderr));
  return r.stdout;
};
(async function(){
  var t0=Date.now(),py=await require(R+'/pyodide/0.29.5/pyodide.js').loadPyodide({indexURL:R+'/pyodide/0.29.5/'});
  var t1=Date.now();
  var whl=fs.readdirSync(R+'/wheels').map(function(f){return R+'/wheels/'+f;}).concat([S+'/dl/lbr.whl']);
  whl.forEach(function(p){py.unpackArchive(new Uint8Array(fs.readFileSync(p)),'wheel');});
  py.FS.writeFile('/tmp/site.epw',new Uint8Array(fs.readFileSync(EPW)));
  var t2=Date.now();
  var res=py.runPython([
    'import json, time, os',
    'os.makedirs("/tmp/sky", exist_ok=True)',
    'from js import bimGendaymtx',
    'import ladybug_radiance.skymatrix as sm',
    'from ladybug_radiance.skymatrix import SkyMatrix',
    'def _run(self, wea_file, wea_duration):',
    '    density = 2 if self.high_density else 1',
    '    txt = open(wea_file).read()',
    '    d = bimGendaymtx(["-m", str(density), "-d", "-O1", "-A"], txt).to_py().tobytes()',
    '    s = bimGendaymtx(["-m", str(density), "-s", "-O1", "-A"], txt).to_py().tobytes()',
    '    return self._parse_mtx_data(d, wea_duration, density), self._parse_mtx_data(s, wea_duration, density)',
    'SkyMatrix._run_gendaymtx = _run',
    'out = {}',
    'for dens in (False, True):',
    '    t = time.time()',
    '    m = SkyMatrix.from_epw("/tmp/site.epw", high_density=dens)',
    '    m.folder = "/tmp/sky"',
    '    m.compute_sky()',
    '    out["reinhart" if dens else "tregenza"] = {"dir": m.direct_values, "dif": m.diffuse_values, "sec": time.time() - t}',
    'json.dumps(out)'].join('\n'));
  var t3=Date.now(),got=JSON.parse(res),ref=JSON.parse(fs.readFileSync(S+'/exp/ref_sky_phl.json'));
  console.log('pyodide load',t1-t0,'ms; wheels',t2-t1,'ms; two skies',t3-t2,'ms');
  ['tregenza','reinhart'].forEach(function(k){
    var md=0,n=0;['dir','dif'].forEach(function(c){for(var i=0;i<ref[k][c].length;i++){md=Math.max(md,Math.abs(got[k][c][i]-ref[k][c][i]));n++;}});
    console.log(k,n,'values; largest difference from the native run:',md,'kWh/m2; Python sky time',got[k].sec.toFixed(2),'s');
  });
})().catch(function(e){console.error('FAILED',e);process.exit(1);});
