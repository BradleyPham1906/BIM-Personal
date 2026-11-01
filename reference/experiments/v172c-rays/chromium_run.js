// V172c experiment: drives web/index.html in the preinstalled Chromium and prints the worker's numbers.
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch(),p=await b.newPage();
  p.on('console',m=>{if(m.type()==='error')console.log('console error:',m.text());});
  await p.goto('http://127.0.0.1:8765/index.html');
  await p.waitForFunction(()=>window.__r,null,{timeout:300000});
  console.log(JSON.stringify(await p.evaluate(()=>window.__r),null,1));
  await b.close();
})().catch(e=>{console.error(e);process.exit(1);});
