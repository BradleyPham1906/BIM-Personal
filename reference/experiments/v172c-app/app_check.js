// V172c browser check: the built app, both studies on three boxes, the fixture's weather; console errors reported.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const REPO=process.argv[2],EPW=process.argv[3],PAGES='https://bradleypham1906.github.io/BIM-Personal/runtime/';
(async()=>{
  const b=await chromium.launch(),ctx=await b.newContext({viewport:{width:1500,height:950}});
  const fetched=[];
  await ctx.route(PAGES+'**',async r=>{const rel=r.request().url().slice(PAGES.length).split('?')[0];fetched.push(rel);
    const p=path.join(REPO,'runtime',rel);if(!fs.existsSync(p))return r.fulfill({status:404,body:'no'});
    const ct=rel.endsWith('.wasm')?'application/wasm':rel.endsWith('.js')?'application/javascript':'application/octet-stream';
    r.fulfill({status:200,body:fs.readFileSync(p),headers:{'Access-Control-Allow-Origin':'*','Content-Type':ct}});});
  const p=await ctx.newPage(),errs=[],warns=[];
  p.on('pageerror',e=>errs.push('pageerror: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('console.error: '+m.text());if(m.type()==='warning'&&/BIM/.test(m.text()))warns.push(m.text().slice(0,400));});
  await p.goto('file://'+path.join(REPO,'canvas_v10.html'));await p.waitForTimeout(2500);
  const out={};
  out.marker=await p.evaluate(()=>window.__acad3dV172c);
  // the site, and three boxes: a 30 m tower south of two 12 m blocks
  await p.evaluate(()=>{window.__a3dEnter();
    function box(id,x0,z0,x1,z1,h){return {id:id,t:'solid',name:id,col:'#9db0c4',pos:[0,0,0],layer:'layer-0',
      mesh:{v:[[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,h,z0],[x1,h,z0],[x1,h,z1],[x0,h,z1]],
        f:[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]}};}
    window.__a3dTestSetObjs([box('A',0,0,20,20,12),box('B',30,0,50,20,12),box('T',10,30,30,50,30)]);
    window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();});
  for(const [k,v] of [['sunlat','40'],['sunlon','-75'],['suntz','-5'],['sundate','2017-12-21']]){
    await p.fill('#a3d-propsbody [data-propmodel="'+k+'"]',v);await p.keyboard.press('Enter');await p.waitForTimeout(80);}
  out.sunSettings=await p.evaluate(()=>window.__a3dSunSettings());
  out.geo=await p.evaluate(()=>{var g=window.__a3dLbStudyGeo(null);return {tris:g.tris,faces:g.faces,solids:g.solids,all:g.all};});
  out.cardsBefore=await p.evaluate(()=>window.__a3dLbStudyCards().map(c=>[c.id,c.state,c.acts.map(a=>[a.act,a.off||''])]));
  // direct sun first: no weather needed
  let t=Date.now();
  out.sun=await p.evaluate(()=>window.__a3dLbStudy('sun').then(R=>R.error?R:{min:R.r.min,max:R.r.max,mean:R.r.mean,count:R.r.count,dirs:R.r.dirs,pre:R.r.pre,ms:R.r.ms,top:R.r.faces.A&&R.r.faces.A[1],tower_n:R.r.faces.T}));
  out.sunMs=Date.now()-t;
  // the weather, then radiation
  const b64=fs.readFileSync(EPW).toString('base64');
  out.src=await p.evaluate(a=>window.__a3dLbOpenB64('fixture.epw',a).then(s=>s.error?s:{kind:s.kind,hours:s.hours}),b64);
  t=Date.now();
  out.rad=await p.evaluate(()=>window.__a3dLbStudy('rad').then(R=>R.error?R:{min:R.r.min,max:R.r.max,mean:R.r.mean,total:R.r.total,area:R.r.area,count:R.r.count,dirs:R.r.dirs,pre:R.r.pre,ms:R.r.ms,v:R.v,faces:R.r.faces}));
  out.radMs=Date.now()-t;out.versions=await p.evaluate(()=>window.__a3dLbState().versions);
  out.stale=await p.evaluate(()=>[window.__a3dLbStudyStale('rad'),window.__a3dLbStudyStale('sun')]);
  await p.evaluate(()=>{window.__a3dSetView('home',false);window.__a3dFit();window.__a3dTestPaint();});await p.waitForTimeout(600);await p.evaluate(()=>window.__a3dTestPaint());
  out.drawn=await p.evaluate(()=>window.__a3dLbStudyDrawn());
  out.cardsAfter=await p.evaluate(()=>window.__a3dLbStudyCards().map(c=>[c.id,c.state,c.status]));
  await p.screenshot({path:process.argv[4]});
  out.fetched=fetched.filter(f=>/radiance|numpy|radiance-0/.test(f));
  console.log(JSON.stringify(out,null,1));
  console.log('ERRORS',JSON.stringify(errs,null,1));console.log('BIM WARNINGS',JSON.stringify(warns,null,1));
  await b.close();
})().catch(e=>{console.error('FAILED',e);process.exit(1);});
