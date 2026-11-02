// V172c experiment: the app's rays (verbatim, as rays_exact.js) over city blocks: n boxes on a grid, 12 to 40 m
// high, every face but the bottom a sensor (5 a box), Tregenza's 145 sky + 145 ground directions. Node, one thread.
var fs=require('fs'),SRC=process.argv[2],D=JSON.parse(fs.readFileSync(process.argv[3]));
var js=fs.readFileSync(SRC+'/src/js/engine/analysis/simulation.js','utf8');
function grab(name){var i=js.indexOf('  function '+name+'('),j=js.indexOf('\n  }\n',i);return js.slice(i,j+4);}
eval(grab('bimRayBox')+grab('bimRayTri')+grab('bimRayBlocked'));
var box=require(__dirname+'/scene.js');
var V=D.tregenza.v.concat(D.tregenza.v.map(function(a){return [-a[0],-a[1],-a[2]];}));
[20,100,400].forEach(function(n){
  var g=Math.ceil(Math.sqrt(n)),occ=[],sens=[],i,seed=7;
  function rnd(){seed=(seed*16807)%2147483647;return seed/2147483647;}
  for(i=0;i<n;i++){var x=(i%g)*40,y=Math.floor(i/g)*40,b=box(x,y,0,x+24,y+24,12+28*rnd());occ.push(b.o);sens=sens.concat(b.f);}
  var t0=Date.now(),rays=0,seen=0,j,s,o,c;
  for(i=0;i<sens.length;i++){s=sens[i];o=[s.p[0]+s.n[0]*0.01,s.p[1]+s.n[1]*0.01,s.p[2]+s.n[2]*0.01];
    for(j=0;j<V.length;j++){c=s.n[0]*V[j][0]+s.n[1]*V[j][1]+s.n[2]*V[j][2];if(c<=0)continue;rays++;if(!bimRayBlocked(o,V[j],occ))seen++;}}
  var ms=Date.now()-t0;
  console.log(n,'boxes,',sens.length,'sensors,',rays,'rays cast,',(100*seen/rays).toFixed(1)+'% seen:',ms,'ms,',Math.round(rays/ms*1000),'rays/s');
});
