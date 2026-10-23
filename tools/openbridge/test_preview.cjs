/* Requires an available Playwright installation and local Chromium; no network. */
var assert=require('assert'),path=require('path'),fs=require('fs');
var chromium=require('playwright').chromium;
(async function(){
 var browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/local/bin/chromium',args:['--no-sandbox']});
 var context=await browser.newContext({acceptDownloads:true}),page=await context.newPage(),errors=[],remote=[],checks=0;
 page.on('pageerror',function(e){errors.push(String(e));});page.on('request',function(r){if(/^https?:/.test(r.url()))remote.push(r.url());});
 function check(v){assert.ok(v);checks++;}
 await page.goto('file://'+path.resolve(__dirname,'../../wip/openbridge-ui-preview.html'));
 check(await page.locator('.card').count()===17);
 check(await page.locator('#download').isDisabled());
 await page.locator('#search').fill('layers');check(await page.locator('.card').count()===1);
 await page.locator('.card').click();check((await page.locator('#selection').textContent()).indexOf('chart-layers')===0);
 check(!(await page.locator('#download').isDisabled()));
 var downloadPromise=page.waitForEvent('download');await page.locator('#download').click();var download=await downloadPromise;
 check(download.suggestedFilename()==='chart-layers.svg');var saved=await download.path();check(fs.readFileSync(saved,'utf8')===fs.readFileSync(path.resolve(__dirname,'../../vendor/openbridge/icons/chart-layers.svg'),'utf8'));
 await page.locator('#search').fill('<img src=x onerror=alert(1)>');check(await page.locator('.card').count()===0);check(await page.locator('.empty').isVisible());check(await page.locator('#grid img').count()===0);
 await page.locator('#reset').click();check(await page.locator('.card').count()===17);check(await page.locator('#download').isDisabled());
 for(var theme of ['day','bright','dusk','night']){await page.locator('#theme').selectOption(theme);check(await page.locator('body').getAttribute('data-obc-theme')===theme);check(await page.evaluate(function(){return !!getComputedStyle(document.body).getPropertyValue('--element-active-color').trim();}));}
 await page.emulateMedia({colorScheme:'dark'});await page.reload();check(await page.locator('#theme').inputValue()==='dusk');
 for(var width of [1200,390]){await page.setViewportSize({width:width,height:844});check(await page.evaluate(function(){return document.documentElement.scrollWidth<=window.innerWidth;}));}
 check(errors.length===0);check(remote.length===0);
 console.log(JSON.stringify({checks:checks,errors:errors,remoteRequests:remote,download:'verified exact SVG bytes',viewports:[1200,390],themes:['day','bright','dusk','night']},null,2));
 await browser.close();
})().catch(function(e){console.error(e);process.exit(1);});
