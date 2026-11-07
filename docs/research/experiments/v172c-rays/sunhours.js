// V172c experiment: direct-sun hours. (1) Ladybug's Sunpath against the app's bimSunCalc (src/js/engine/site/
// sun-position.js, read at run time) and the frame mapping (app x,y,z = Ladybug x,z,-y). (2) Ladybug's own
// DirectSunStudy.compute() with the matrix from the BVH rays, against the exact hours on a canyon floor.
var fs=require('fs'),REPO=process.argv[2],R=REPO+'/runtime',H=require(__dirname+'/bvh.js'),box=require(__dirname+'/scene.js');
var js=fs.readFileSync(REPO+'/src/js/engine/site/sun-position.js','utf8');
function grab(src,name){var i=src.indexOf('  function '+name+'('),j=src.indexOf('\n  }\n',i);if(i<0)throw new Error(name);return src.slice(i,j+4);}
eval(grab(js,'bimSunCalc'));
var LAT=39.8733,LON=-75.2268,TZ=-5;   // Philadelphia Intl. AP, as its EPW gives it
(async function(){
  var py=await require(R+'/pyodide/0.29.5/pyodide.js').loadPyodide({indexURL:R+'/pyodide/0.29.5/'});
  fs.readdirSync(R+'/wheels').forEach(function(f){py.unpackArchive(new Uint8Array(fs.readFileSync(R+'/wheels/'+f)),'wheel');});
  await py.loadPackage('numpy');
  var out=JSON.parse(py.runPython([
    'import json','from ladybug.sunpath import Sunpath','from ladybug.dt import DateTime',
    'sp = Sunpath(%s, %s, %s)'.replace('%s',LAT).replace('%s',LON).replace('%s',TZ),
    'res = {}','for (m, d) in ((3, 21), (6, 21), (12, 21)):',
    '    rows = []','    for k in range(96):',
    '        s = sp.calculate_sun(m, d, (k * 15 + 7.5) / 60.0)',
    '        rows.append([s.altitude, s.azimuth, list(s.sun_vector.to_array())])',
    '    res["%02d-%02d" % (m, d)] = rows','json.dumps(res)'].join('\n')));
  // (1) positions, at whole minutes (bimSunCalc takes HH:MM)
  var whole=JSON.parse(py.runPython([
    'res = []','for (m, d) in ((3, 21), (6, 21), (12, 21)):','    for k in range(0, 1440, 10):',
    '        s = sp.calculate_sun(m, d, k / 60.0)','        res.append([m, d, k, s.altitude, s.azimuth, list(s.sun_vector.to_array())])','json.dumps(res)'].join('\n')));
  var md=0,n=0,mvec=0;
  whole.forEach(function(r){
    var t=('0'+Math.floor(r[2]/60)).slice(-2)+':'+('0'+r[2]%60).slice(-2),a=bimSunCalc(LAT,LON,TZ,'2025-'+('0'+r[0]).slice(-2)+'-'+r[1],t);
    if(!a||r[3]<0)return;n++;
    md=Math.max(md,Math.abs(a.elevation-r[3]),Math.min(Math.abs(a.azimuth-r[4]),360-Math.abs(a.azimuth-r[4])));
    // the app's vector (bimSunVector with north at 0), towards the sun, against Ladybug's sun_vector reversed, mapped
    var az=a.azimuth*Math.PI/180,e=a.elevation*Math.PI/180,app=[Math.cos(e)*Math.sin(az),Math.sin(e),-Math.cos(e)*Math.cos(az)];
    var lb=[-r[5][0],-r[5][1],-r[5][2]],map=[lb[0],lb[2],-lb[1]];
    mvec=Math.max(mvec,Math.abs(app[0]-map[0]),Math.abs(app[1]-map[1]),Math.abs(app[2]-map[2]));
  });
  console.log('sun positions: '+n+' moments with the sun up (21 Mar, 21 Jun, 21 Dec, every 10 min): largest difference '+
    md.toFixed(4)+' deg (altitude or azimuth); vectors, mapped app = (x, z, -y): largest component difference '+mvec.toExponential(2));
  // (2) direct-sun hours on a canyon floor: walls along north-south (Ladybug y), W = H = 10 m, 200 m long
  var W=10,Ht=10,L=200,can=[box(-W/2-1,-L/2,0,-W/2,L/2,Ht),box(W/2,-L/2,0,W/2+1,L/2,Ht)],tris=can[0].o.tris.concat(can[1].o.tris),bv=H.build(tris);
  var P=[[0,0,0],[-3,0,0],[3,0,0]],N=[0,0,1];
  Object.keys(out).forEach(function(day){
    var V=out[day].filter(function(r){return r[0]>0;}).map(function(r){return [-r[2][0],-r[2][1],-r[2][2]];}),M=[],ex=[];
    P.forEach(function(p){var o=[p[0],p[1],p[2]+0.001];
      M.push(V.map(function(v){return v[2]>0&&!H.blocked(bv,o,v)?1:0;}));
      ex.push(V.reduce(function(s,v){if(v[2]<=0)return s;if(Math.abs(v[0])<1e-12)return s+0.25;
        var x=v[0]>0?W/2:-W/2,t=(x-p[0])/v[0],z=v[2]*t,y=v[1]*t;return s+((z<Ht&&Math.abs(y)<L/2)?0:0.25);},0));});
    py.globals.set('_M',JSON.stringify(M));
    var hrs=JSON.parse(py.runPython([
      'import json, numpy as np','from ladybug_radiance.study.directsun import DirectSunStudy',
      'st = DirectSunStudy.__new__(DirectSunStudy)','st._timestep = 4','st._intersection_matrix = np.array(json.loads(_M), dtype=bool)',
      'st._direct_sun_hours = None','DirectSunStudy.compute(st)','json.dumps(st._direct_sun_hours)'].join('\n')));
    console.log(day+': '+V.length+' quarter-hours of sun; direct-sun hours at x = 0, -3, +3 m: Ladybug '+hrs.map(function(h){return h.toFixed(2);}).join(', ')+
      '; exact '+ex.map(function(h){return h.toFixed(2);}).join(', '));
  });
})().catch(function(e){console.error('FAILED',e);process.exit(1);});
