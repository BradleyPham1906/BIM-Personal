#!/usr/bin/env python3
"""V172c, patch a: sun-hours and radiation on the model, by Ladybug. reference/research-ladybug-sun-radiation.md (5b).
The new files are already in src/: js/engine/ladybug/rays.js (the WASI runner for Radiance's gendaymtx, the
bounding-volume hierarchy and the study's rows, sent to the worker as text) and js/engine/ladybug/studies.js (the two
studies: geometry, runs, kept results, the drawing on the model, the rows in Analyze); src/py/bim_ladybug.py has the
sky, radiation, sun_vectors and sun_hours (embedded again here by tools/embed_py.py). This patch:
- the worker: ladybug-radiance's wheel with the others; gendaymtx.wasm fetched, checked by its SHA-256 and compiled,
  and numpy loaded, on the first study only; a study message (Ladybug's first call, the rays, Ladybug's sum by chunks
  of rows); its text made of rays.js's functions and its own;
- bimSolarFaces keeps each face's index, so a study's values go back on their faces;
- the rows in Analyze, their buttons, the drawing after the solids;
- the registry: app.solar, Ladybug's defaults (the ground's reflectance, the sensor's offset) and the steps an hour;
- the page and tools/app_layout.py list the two files; the hooks for the suite and the marker.
Run from the repository root: python3 Phase/patch_v172c_a.py
"""
import pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

GDM_SHA = '45726aea4f019ca39dd2c6ba1cdfe42554f523010b7ac6ed6b25504d70ef05e5'   # runtime/MANIFEST.json, radiance/gendaymtx.wasm
LBR_SHA = '66d57a562c3e896e9ae55e685a4f45e0a0ada28a8948b749966defa028a9e629'   # runtime/MANIFEST.json, ladybug_radiance-0.2.12

begin('2d40105de276cd2ff0c1bdf8ce811bdbf0e321b6642b2917d73c05f019ecb7b0')   # V172e as merged (PIPELINE.md)

# ---- the worker ----
R = 'js/engine/ladybug/runtime.js'
rep(R, "  /* the four wheels, as runtime/MANIFEST.json pins them */\n",
    "  /* the wheels, as runtime/MANIFEST.json pins them; __acad3dV172c: ladybug-radiance, for the studies on the model */\n")
rep(R, "    {f:'click-8.3.3-py3-none-any.whl',h:'a2bf429bb3033c89fa4936ffb35d5cb471e3719e1f3c8a7c3fff0b8314305613'}];\n",
    "    {f:'click-8.3.3-py3-none-any.whl',h:'a2bf429bb3033c89fa4936ffb35d5cb471e3719e1f3c8a7c3fff0b8314305613'},\n"
    "    {f:'ladybug_radiance-0.2.12-py3-none-any.whl',h:'" + LBR_SHA + "'}];\n"
    "  /* __acad3dV172c: Radiance's gendaymtx (the release rad6R0P1a) as WebAssembly, fetched on the first study only */\n"
    "  var BIM_LB_RAD={f:'radiance/gendaymtx.wasm',h:'" + GDM_SHA + "'};\n")
rep(R, "    var PY=null;\n", "    var PY=null,BASE='',RAD=null,GDM=null,NP=false;   /* __acad3dV172c */\n")
rep(R, "      var t0=Date.now(),B=m.base;\n", "      var t0=Date.now(),B=m.base;\n      BASE=B;RAD=m.rad||null;   /* __acad3dV172c */\n")
rep(R, "    self.onmessage=function(e){var m=e.data||{};if(m.t==='boot')boot(m);else if(m.t==='run'&&PY)run(m);};\n",
    """    /* __acad3dV172c: what a study needs beyond the weather's analyses, the first time: numpy (Pyodide's own, from
       the runtime, checked against its lock file) and gendaymtx, checked by its SHA-256, given to Python as
       bimGendaymtx(args, wea text) -> the program's stdout */
    function ensure(){
      var p=Promise.resolve();
      if(!NP)p=p.then(function(){return PY.loadPackage('numpy').then(function(){NP=true;});});
      if(!GDM)p=p.then(function(){
        if(!RAD)throw new Error('The runtime has no gendaymtx');
        return fetch(BASE+RAD.f).then(function(r){if(!r.ok)throw new Error(RAD.f+': HTTP '+r.status);return r.arrayBuffer();})
          .then(function(buf){return self.crypto.subtle.digest('SHA-256',buf).then(function(h){
            if(hex(h)!==RAD.h)throw new Error(RAD.f+' does not match its SHA-256');
            return WebAssembly.compile(buf);});})
          .then(function(mod){
            GDM=mod;
            self.bimGendaymtx=function(args,wea){
              var a=args&&args.toJs?args.toJs():args,r=bimLbWasiRun(GDM,['gendaymtx'].concat(a),new TextEncoder().encode(String(wea)));
              if(r.code)throw new Error('gendaymtx stopped ('+r.code+'): '+new TextDecoder().decode(r.stderr).slice(0,300));
              return r.stdout;
            };
          });
      });
      return p;
    }
    function call(fn,args){
      PY.globals.set('_bim_req',JSON.stringify({fn:fn,args:args||{}}));
      var r=JSON.parse(String(PY.runPython('import bim_ladybug\\nbim_ladybug.handle(_bim_req)'))),e;
      if(r&&r.error){e=new Error(r.error);e.trace=r.trace;throw e;}
      return r;
    }
    /* a study: Ladybug's first call (the sky, or the sun's steps), the rays over the model, then Ladybug's sum, by
       chunks of rows so the matrix stays small */
    function study(m){
      ensure().then(function(){
        var t0=Date.now(),pre=call(m.pre.fn,m.pre.args),V=bimLbStudyVecs(pre.vectors||[],m.tn||0,m.kind==='rad'),t1=Date.now();
        var H=bimLbBvhBuild(m.tris),n=m.sens.length/6,vals=[],a,b,M,r,t,rays=0,args,step=Math.max(1,Math.floor(400000/Math.max(1,V.length)));
        for(a=0;a<n;a=b){
          b=Math.min(n,a+step);t=Date.now();
          M=bimLbStudyRows(H,m.sens,V,a,b,m.kind==='rad');rays+=Date.now()-t;
          if(!V.length){r={values:[]};for(t=a;t<b;t++)r.values.push(0);}
          else{
            PY.globals.set('_bim_mtx',M);
            PY.runPython('import bim_ladybug\\nbim_ladybug.S["mtx"]=_bim_mtx.to_py()');
            args=JSON.parse(JSON.stringify(m.post.args||{}));args.rows=b-a;
            r=call(m.post.fn,args);
          }
          vals=vals.concat(r.values);
        }
        PY.runPython('import bim_ladybug\\nbim_ladybug.S["mtx"]=None');
        delete pre.vectors;
        say({t:'done',id:m.id,r:JSON.stringify({pre:pre,values:vals,dirs:V.length,ms:{first:t1-t0,rays:rays,all:Date.now()-t0}})});
      }).then(null,function(x){say({t:'err',id:m.id,s:String(x&&x.message||x),trace:x&&x.trace?String(x.trace):''});});
    }
    self.onmessage=function(e){var m=e.data||{};if(m.t==='boot')boot(m);else if(m.t==='run'&&PY)run(m);else if(m.t==='study'&&PY)study(m);};
""")
rep(R, "    if(m.t==='done')p.res(m.r);else p.rej(new Error(m.s||'The analysis failed'));\n",
    "    if(m.trace)console.warn('[BIM] Ladybug:\\n'+m.trace);   /* __acad3dV172c */\n"
    "    if(m.t==='done')p.res(m.r);else p.rej(new Error(m.s||'The analysis failed'));\n")
rep(R, "    try{w=new Worker(URL.createObjectURL(new Blob(['('+bimLbWorkerMain.toString()+')();'],{type:'text/javascript'})));}\n",
    "    /* __acad3dV172c: the worker's text is rays.js's functions, then its own */\n"
    "    var txt=[bimLbWasiRun,bimLbBvhBuild,bimLbBvhBlocked,bimLbStudyVecs,bimLbStudyRows].map(function(f){return f.toString();}).join('\\n')+\n"
    "      '\\n('+bimLbWorkerMain.toString()+')();';\n"
    "    try{w=new Worker(URL.createObjectURL(new Blob([txt],{type:'text/javascript'})));}\n")
rep(R, "      w.postMessage({t:'boot',base:bimLbBase(),dir:'pyodide/'+BIM_LB_PYODIDE+'/',wheels:BIM_LB_WHEELS,py:BIM_LB_PY});\n",
    "      w.postMessage({t:'boot',base:bimLbBase(),dir:'pyodide/'+BIM_LB_PYODIDE+'/',wheels:BIM_LB_WHEELS,py:BIM_LB_PY,rad:BIM_LB_RAD});\n")
rep(R, "  /* the runtime's state in words, for a panel */\n",
    """  /* __acad3dV172c: one study in the worker: msg {kind, tn, tris, sens, pre, post}, its two arrays handed over */
  function bimLbStudyCall(msg,transfer){
    return bimLbStart().then(function(){
      return new Promise(function(res,rej){
        var id=++A3D_LB.seq;
        msg.t='study';msg.id=id;
        A3D_LB.pend[id]={res:res,rej:rej,timer:setTimeout(function(){
          delete A3D_LB.pend[id];rej(new Error('The Ladybug study did not finish in '+Math.round(BIM_LB_STUDY_MS/1000)+' s'));},BIM_LB_STUDY_MS)};
        A3D_LB.w.postMessage(msg,transfer||[]);
      });
    }).then(function(txt){
      try{return JSON.parse(txt);}catch(eP){throw new Error('The Ladybug study answered something unreadable');}
    });
  }
  /* the runtime's state in words, for a panel */
""")

# ---- each face's index, for the values to go back on their faces ----
rep('js/engine/analysis/simulation.js',
    "      out.push({c:[cx/f.length+q[0],cy/f.length+q[1],cz/f.length+q[2]],n:[nx/L,ny/L,nz/L],area:L/2});\n",
    "      out.push({c:[cx/f.length+q[0],cy/f.length+q[1],cz/f.length+q[2]],n:[nx/L,ny/L,nz/L],area:L/2,i:i});   /* __acad3dV172c: i, the face */\n")

# ---- the rows, their buttons, the drawing ----
rep('js/engine/ladybug/panel.js', "    if(c==='open'){bimLbPickFile();return true;}\n",
    "    if(c==='open'){bimLbPickFile();return true;}\n"
    "    if(c==='study')return bimLbsAct(k);   /* __acad3dV172c: the studies on the model */\n")
rep('js/engine/analysis/analyze-tab.js', "    bimLbCards().forEach(function(c){C.push(c);});   /* __acad3dV172b: Ladybug's rows, in Climate */\n",
    "    bimLbCards().forEach(function(c){C.push(c);});   /* __acad3dV172b: Ladybug's rows, in Climate */\n"
    "    bimLbsCards().forEach(function(c){C.push(c);});   /* __acad3dV172c: and its studies on the model */\n")
rep('js/engine/map/terrain-3d.js', "    A3D.lastPolys=polys;\n    }\n    drawGrids(ctx,V,W,H);\n",
    "    A3D.lastPolys=polys;\n    }\n"
    "    if(!capMode)bimLbsDraw(ctx,V,W,H);       /* __acad3dV172c: a Ladybug study on the model, over the solids */\n"
    "    drawGrids(ctx,V,W,H);\n")

# ---- the registry ----
rep('js/engine/standards/registry.js',
    "    {id:'ashrae.dd',title:'Climatic design conditions',pub:'ASHRAE',kind:'data',area:'Climate',use:'Ladybug\\'s design days',anywhere:true,\n",
    """    /* __acad3dV172c */
    {id:'app.solar',title:'Sun and radiation on the model',pub:'This app',kind:'assumption',area:'Climate',use:'Ladybug\\'s incident radiation and direct sun hours on the model',anywhere:true,
      eds:[{id:'app.solar.1',name:'The app\\'s study settings (V172c): Ladybug\\'s own defaults',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app, taking the defaults of Ladybug Tools\\' LB Cumulative Sky Matrix (ground reflectance) and LB Incident Radiation and LB Direct Sun Hours (the points 10 cm off the surface)',w:'research-ladybug-sun-radiation.md, part 7b',u:'https://github.com/ladybug-tools/ladybug-grasshopper',lv:'A'},
        v:[{n:'ground_ref',v:0.2,u:'ratio',say:'the ground\\'s reflectance, Ladybug\\'s default: the ground hemisphere\\'s share of the sky'},
          {n:'offset',v:0.1,u:'m',say:'how far each face\\'s point is moved off the face, along its normal, before its rays are cast'},
          {n:'step_day',v:4,u:'steps/h',say:'direct sun on the day studied: the sun every quarter hour, as V148\\'s sun hours'},
          {n:'step_year',v:1,u:'steps/h',say:'direct sun over the year: the sun every hour, Ladybug\\'s default'}]}]},
    {id:'ashrae.dd',title:'Climatic design conditions',pub:'ASHRAE',kind:'data',area:'Climate',use:'Ladybug\\'s design days',anywhere:true,
""")

# ---- the hooks ----
H = 'js/engine/testing/hooks-ladybug.js'
rep(H, "  function bimLbErr(e){return {error:String(e&&e.message||e)};}\n",
    "  function bimLbErr(e){return {error:String(e&&e.message||e)};}\n"
    "  window.__acad3dV172c='gendaymtx,wasm,sha256,numpy,bvh,rays,sky,tregenza,reinhart,radiation,sunpath,directsun,faces,kept,stale,draw,legend,rows,registry';\n"
    "  window.__a3dLbStudy=function(k,o){return bimLbsRun(k,o).then(function(r){return JSON.parse(JSON.stringify(r));},bimLbErr);};\n"
    "  window.__a3dLbStudyGeo=function(ids){var G=bimLbsGeometry(ids);return {tris:G.tris.length/9,faces:G.faces,solids:G.solids,all:G.all,map:G.map};};\n"
    "  window.__a3dLbStudyCards=function(){return JSON.parse(JSON.stringify(bimLbsCards()));};\n"
    "  window.__a3dLbStudyStale=function(k){return bimLbsStale(k,bimLbsKept(k));};\n"
    "  window.__a3dLbStudyDrawn=function(){return A3D.lastLbsDrawn||null;};\n"
    "  window.__a3dLbStudyCol=function(k,v,lo,hi){return bimLbsCol(k,v,lo,hi);};\n"
    "  window.__a3dLbStudyPeriod=function(span,date){return bimLbsPeriod(span,date);};\n")

# ---- the page and the layout ----
rep('index.html', '<!-- @include js/engine/ladybug/panel.js -->\n',
    '<!-- @include js/engine/ladybug/panel.js -->\n'
    '<!-- @include js/engine/ladybug/rays.js -->\n'
    '<!-- @include js/engine/ladybug/studies.js -->\n')
LAY = ROOT / 'tools' / 'app_layout.py'
s = LAY.read_text(encoding='utf-8')
a1 = "    ('ladybug/panel.js', '  /* ================= __acad3dV172b: Ladybug in the analysis workspace ================='),\n"
assert s.count(a1) == 1, 'app_layout.py anchor'
s = s.replace(a1, a1 +
    "    ('ladybug/rays.js', '  /* ================= __acad3dV172c: the sky\\'s program and the rays, in the Ladybug worker ================='),\n"
    "    ('ladybug/studies.js', '  /* ================= __acad3dV172c: sun-hours and radiation on the model, by Ladybug ================='),\n")
LAY.write_text(s, encoding='utf-8')

# ---- the adapter's Python, embedded again ----
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_py.py')], check=True)
done()
