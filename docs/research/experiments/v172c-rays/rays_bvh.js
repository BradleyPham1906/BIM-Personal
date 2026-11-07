// V172c experiment: the BVH (bvh.js) against the app's rays: the same answer for every ray, and the time.
var fs=require('fs'),SRC=process.argv[2],D=JSON.parse(fs.readFileSync(process.argv[3])),H=require(__dirname+'/bvh.js');
var js=fs.readFileSync(SRC+'/src/js/engine/analysis/simulation.js','utf8');
function grab(name){var i=js.indexOf('  function '+name+'('),j=js.indexOf('\n  }\n',i);return js.slice(i,j+4);}
eval(grab('bimRayBox')+grab('bimRayTri')+grab('bimRayBlocked'));
var box=require(__dirname+'/scene.js');
var V=D.tregenza.v.concat(D.tregenza.v.map(function(a){return [-a[0],-a[1],-a[2]];}));
var compareUpTo=+process.argv[4]||400;
[20,100,400,1000,4000].forEach(function(n){
  var g=Math.ceil(Math.sqrt(n)),occ=[],sens=[],tris=[],i,seed=7;
  function rnd(){seed=(seed*16807)%2147483647;return seed/2147483647;}
  for(i=0;i<n;i++){var x=(i%g)*40,y=Math.floor(i/g)*40,b=box(x,y,0,x+24,y+24,12+28*rnd());occ.push(b.o);sens=sens.concat(b.f);tris=tris.concat(b.o.tris);}
  var tb=Date.now(),bv=H.build(tris),build=Date.now()-tb;
  var t0=Date.now(),rays=0,seen=0,diff=0,j,s,o,c,r,ms;
  var res=new Uint8Array(sens.length*V.length);
  for(i=0;i<sens.length;i++){s=sens[i];o=[s.p[0]+s.n[0]*0.01,s.p[1]+s.n[1]*0.01,s.p[2]+s.n[2]*0.01];
    for(j=0;j<V.length;j++){c=s.n[0]*V[j][0]+s.n[1]*V[j][1]+s.n[2]*V[j][2];if(c<=0)continue;rays++;r=!H.blocked(bv,o,V[j]);res[i*V.length+j]=r?1:0;if(r)seen++;}}
  ms=Date.now()-t0;
  if(n<=compareUpTo){
    for(i=0;i<sens.length;i++){s=sens[i];o=[s.p[0]+s.n[0]*0.01,s.p[1]+s.n[1]*0.01,s.p[2]+s.n[2]*0.01];
      for(j=0;j<V.length;j++){c=s.n[0]*V[j][0]+s.n[1]*V[j][1]+s.n[2]*V[j][2];if(c<=0)continue;if((!bimRayBlocked(o,V[j],occ)?1:0)!==res[i*V.length+j])diff++;}}
  }
  console.log(n,'boxes,',sens.length,'faces,',tris.length,'triangles: BVH built',build,'ms; ',rays,'rays',ms,'ms,',Math.round(rays/ms*1000),'rays/s;',
    n<=compareUpTo?diff+' differ from the app\'s rays':'not compared');
});
