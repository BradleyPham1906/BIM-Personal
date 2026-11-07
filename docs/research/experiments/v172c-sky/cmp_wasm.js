// V172c experiment: gendaymtx.wasm (through the ES5 shim) against the native build, byte for byte.
var fs=require('fs'),cp=require('child_process'),run=require(__dirname+'/wasi-run.js');
var S=process.argv[2],wea=fs.readFileSync(process.argv[3]);
var mod=new WebAssembly.Module(fs.readFileSync(S+'/wasi/gendaymtx.wasm'));
[['-m','1','-d','-O1','-A'],['-m','1','-s','-O1','-A'],['-m','2','-d','-O1','-A'],['-m','2','-s','-O1','-A']].forEach(function(a){
  var t0=Date.now(),r=run(mod,['gendaymtx'].concat(a),new Uint8Array(wea)),tw=Date.now()-t0;
  t0=Date.now();var nat=cp.execFileSync(S+'/ref/gendaymtx',a,{input:wea,maxBuffer:1<<28});var tn=Date.now()-t0;
  var same=Buffer.compare(Buffer.from(r.stdout),nat)===0;
  console.log(a.join(' '),'exit',r.code,'wasm',r.stdout.length,'B',tw,'ms; native',nat.length,'B',tn,'ms; identical:',same,
    r.stderr.length?'stderr: '+Buffer.from(r.stderr).toString().slice(0,200):'');
});
