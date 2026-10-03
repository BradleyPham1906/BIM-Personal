#!/usr/bin/env python3
"""bim_phase138_survey_check_browser_tests.py -- V138: verify the survey.

The owner: "build the genesis of a good foundation so data can be verified every time".

  1. EVERY DATASET in tests/data/surveys/: each survey file is read the way its JSON sidecar says,
     and its check must find what the sidecar expects. A real survey added there, with a sidecar,
     is held to it on every change from then on (tools/make_seed_survey.py writes the seeds).
  2. THE SEED'S FAULTS, one by one: the header and the mistyped line by number, the duplicate by
     name, the bust shot by name and size, the check shots' RMSE, the control points.
  3. CONTROL POINTS: off, missing, mistyped, one undo step.
  4. NO CHECK SHOTS: a blank code keeps every shot in the surface.
  5. THE PUBLIC TERRAIN: an offset datum, and feet read as metres, said.
  6. IN THE APP: the Survey Check group, Export Report, the dialog's file and code, SURVEYCHECK,
     kept with the project.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, sys, traceback
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / 'data' / 'surveys'
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


N0, E0 = 5000.0, 2000.0


def z_at(e, n):
    de, dn = e - E0, n - N0
    return 100 + 0.05 * de + 0.02 * dn + 2 * math.sin(de / 40) * math.cos(dn / 50)


def item(r, key):
    for it in (r or {}).get('items', []):
        if it['key'] == key:
            return it
    return {}


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV138")
        ck(bool(has), "__acad3dV138 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def fresh():
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);window.__a3dRefreshProps();}")

        async def load(meta, code=None):
            text = (DATA / meta['file']).read_text()
            r = await safe("(a)=>window.__a3dSurveyImport(a[0],a[1],a[2],a[3],a[4])",
                           [text, meta['format'], meta['units'], meta.get('base'), meta.get('checkCode', 'CHK') if code is None else code]) or {}
            if r.get('id') and meta.get('control'):
                await safe("(a)=>window.__a3dSurveyControl(a[0],a[1])", [r['id'], meta['control']])
            return r

        async def check(i):
            return await safe("(i)=>window.__a3dSurveyCheck(i)", i) or {}

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. every dataset in tests/data/surveys")
            metas = sorted(DATA.glob('*.json'))
            ck(len(metas) >= 2, "%d datasets to verify" % len(metas))
            for mp in metas:
                meta = json.loads(mp.read_text())
                ex = meta.get('expect', {})
                await fresh()
                r = await load(meta)
                rep = await check(r.get('id'))
                nm = mp.stem
                ck(r.get('id') and rep.get('verdict') == ex.get('verdict'), "%s: verdict %s (%s)" % (nm, ex.get('verdict'), rep.get('verdict')))
                if 'points' in ex:
                    ck(r.get('points') == ex['points'], "%s: %d points in the surface (%s)" % (nm, ex['points'], r.get('points')))
                if 'checks' in ex:
                    ck(r.get('checks') == ex['checks'], "%s: %d check shots kept out (%s)" % (nm, ex['checks'], r.get('checks')))
                if 'skippedLines' in ex:
                    got = (item(rep, 'read').get('detail') or {}).get('skipped')
                    ck(got == ex['skippedLines'], "%s: lines skipped %s (%s)" % (nm, ex['skippedLines'], got))
                if 'duplicates' in ex:
                    got = (item(rep, 'duplicates').get('detail') or {}).get('names')
                    ck(got == ex['duplicates'], "%s: duplicates %s (%s)" % (nm, ex['duplicates'], got))
                if 'busts' in ex:
                    got = [p['name'] for p in (item(rep, 'busts').get('detail') or {}).get('points', [])]
                    ck(got == ex['busts'], "%s: bust shots %s (%s)" % (nm, ex['busts'], got))
                for k in ('fidelity', 'triangles', 'control'):
                    if k in ex:
                        ck(item(rep, k).get('status') == ex[k], "%s: %s %s (%s: %s)" % (nm, k, ex[k], item(rep, k).get('status'), item(rep, k).get('text')))
                if 'checkStatus' in ex:
                    ck(item(rep, 'checks').get('status') == ex['checkStatus'], "%s: check shots %s (%s)" % (nm, ex['checkStatus'], item(rep, 'checks').get('text')))
                if 'checkRmseMax' in ex:
                    rm = (item(rep, 'checks').get('detail') or {}).get('rmse')
                    ck(rm is not None and rm <= ex['checkRmseMax'], "%s: check shots' RMSE within %s m (%s)" % (nm, ex['checkRmseMax'], rm))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the seed's faults, one by one")
            meta = json.loads((DATA / 'seed_site_m.json').read_text())
            await fresh()
            r = await load(meta)
            sid = r.get('id')
            rep = await check(sid)
            ck('lines 1, 59 could not be read' in item(rep, 'read').get('text', '') and item(rep, 'read').get('status') == 'warn',
               "the header and the mistyped easting, by line number: a warning (%s)" % item(rep, 'read').get('text'))
            ck('300' in item(rep, 'duplicates').get('text', '') and item(rep, 'duplicates').get('status') == 'warn', "the duplicate, by name: a warning")
            bp = (item(rep, 'busts').get('detail') or {}).get('points', [{}])
            ck(bp and abs(bp[0].get('dev', 0) - 3.0) < 0.25 and item(rep, 'busts').get('status') == 'fail' and '88 +' in item(rep, 'busts').get('text', ''),
               "the bust shot: point 88, about 3 m high, a failure (%s)" % item(rep, 'busts').get('text'))
            fd = item(rep, 'fidelity')
            ck(fd.get('status') == 'pass' and (fd.get('detail') or {}).get('max', 1) < 1e-6, "the surface passes through every point exactly")
            cs = item(rep, 'checks').get('detail') or {}
            ck(len(cs.get('shots', [])) == 6 and all(s['dev'] is not None and abs(s['dev']) < 0.05 for s in cs['shots']), "each check shot measured against the surface")
            ck('RMSE 0.0' in item(rep, 'checks').get('text', '') and 'worst' in item(rep, 'checks').get('text', ''), "its RMSE and worst said (%s)" % item(rep, 'checks').get('text'))
            want = math.sqrt(sum(s_['dev'] ** 2 for s_ in cs.get('shots', [])) / max(1, len(cs.get('shots', []))))
            ck(cs.get('rmse') is not None and abs(cs['rmse'] - want) < 1e-12, "the RMSE is the root of the mean square (%.5f)" % want)
            ck(item(rep, 'control').get('text') == '1 ok; 113 ok', "both control points ok (%s)" % item(rep, 'control').get('text'))
            ck(item(rep, 'triangles').get('status') == 'pass' and (item(rep, 'triangles').get('detail') or {}).get('degenerate') == 0, "no triangle without area")
            ck(item(rep, 'public').get('status') == 'none' and 'get the site context' in item(rep, 'public').get('text', ''), "no public terrain yet: said, not failed")
            ck(rep.get('verdict') == 'fail', "the verdict: fail, for the bust shot")
            # the surface must pass through its points: a point moved under a stale triangulation does not
            mv = await safe("(i)=>{var o=window.__a3dState().objs.filter(function(x){return x.id===i;})[0];var s=o.survey.map(function(p){return String(p[3])==='113'?[p[0]+25,p[1],p[2],p[3],p[4]]:p;});"
                            "window.__a3dTestObjSet(i,'survey',s);return s.length;}", sid)
            await safe("(i)=>window.__a3dTestObjSet(i,'pos',[0,0.0001,0])", sid)   # a new key for the report, the triangles kept
            fd = item(await check(sid), 'fidelity')
            ck(mv and fd.get('status') == 'fail', "a surface that no longer passes through its points fails (%s)" % fd.get('text'))
            await fresh()
            r = await load(meta)
            sid = r.get('id')

            # ---------------------------------------------------------------------------------
            print("\n-- 3. control points")
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the control's undo is its own
            ok = await safe("(i)=>window.__a3dSurveyControl(i,'1=100.500, 999=12')", sid)
            rep = await check(sid)
            ck(ok and item(rep, 'control').get('status') == 'fail' and item(rep, 'control').get('text') == '1 off by -0.500 m; 999 not in the survey',
               "an elevation 0.5 m off, and a name not surveyed: a failure, each said (%s)" % item(rep, 'control').get('text'))
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            rep = await check(sid)
            ck(item(rep, 'control').get('text') == '1 ok; 113 ok' and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.7, "one undo step, its own")
            await safe("(i)=>window.__a3dSurveyControl(i,'999=12')", sid)
            ck(item(await check(sid), 'control').get('status') == 'fail', "a control point not in the survey fails on its own")
            ok = await safe("(i)=>window.__a3dSurveyControl(i,'1:100')", sid)
            ck(ok is False and 'name=elevation' in await toast(), "a mistyped control is refused with the form")
            ok = await safe("(i)=>window.__a3dSurveyControl(i,'500=%.3f')" % (z_at(E0 + 31.7, N0 + 23.4) + 0.012), sid)
            rep = await check(sid)
            ck(item(rep, 'control').get('text') == '500 ok', "a check shot can be control too")
            await safe("(a)=>window.__a3dSurveyControl(a[0],a[1])", [sid, meta['control']])

            # ---------------------------------------------------------------------------------
            print("\n-- 4. no check shots")
            await fresh()
            r2 = await load(meta, code='')
            rep2 = await check(r2.get('id'))
            ck(r2.get('points') == 230 and r2.get('checks') == 0 and item(rep2, 'checks').get('status') == 'none', "a blank code keeps every shot in the surface (%s)" % r2.get('points'))

            # a flat car park: the scatter is nothing, so only the 0.5 m floor keeps a lid from being a bust
            await fresh()
            lot = '\n'.join('%d,%.3f,%.3f,%.3f,%s' % (i * 10 + j + 1, 1000 + 5 * i, 3000 + 5 * j, 50 + 0.01 * i + (0.3 if (i, j) == (4, 5) else 0),
                                                       'MH' if (i, j) == (4, 5) else 'PAV') for i in range(10) for j in range(10))
            rl = await safe("(t)=>window.__a3dSurveyImport(t,'PNEZD','m',{n:1000,e:3000,z:50},'CHK')", lot) or {}
            rpl = await check(rl.get('id'))
            ck(item(rpl, 'busts').get('status') == 'pass', "a flat car park: a manhole lid 0.3 m proud is not a bust (%s)" % item(rpl, 'busts').get('text'))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the public terrain")

            async def public(scale, offset):
                await fresh()
                rr = await load(json.loads((DATA / 'seed_site_usft.json').read_text()))
                g = []
                for i in range(20):
                    for j in range(20):
                        x, zz = -20 + 180 * i / 19, 20 - 180 * j / 19
                        g.append([x, zz, round((z_at(E0 + x, N0 - zz) - 100) * scale + offset, 3), '', ''])
                tid = await safe("(m)=>window.__a3dMakeTerrain(m)", g)
                await safe("(i)=>window.__a3dTestObjSet(i,'context',{kind:'terrain'})", tid)
                return await check(rr.get('id'))
            rep = await public(1, 0)
            pb = item(rep, 'public')
            ck(pb.get('status') == 'pass' and abs((pb.get('detail') or {}).get('offset', 9)) < 0.05 and abs((pb.get('detail') or {}).get('slope', 0) - 1) < 0.05,
               "the same ground: offset 0, relief ratio 1, a pass (%s)" % pb.get('text'))
            rep = await public(1, -2.5)
            pb = item(rep, 'public')
            ck(pb.get('status') == 'warn' and '2.50 m above the public terrain' in pb.get('text', '') and rep.get('verdict') == 'warn',
               "public ground 2.5 m lower: the survey sits 2.50 m above it, check the base elevation or datum (%s)" % pb.get('text'))
            rep = await public(0.3048, 0)
            pb = item(rep, 'public')
            ck(pb.get('status') == 'warn' and 'feet read as metres' in pb.get('text', ''), "the survey's relief 3.28 times the public's: feet read as metres? (%s)" % pb.get('text'))

            # ---------------------------------------------------------------------------------
            print("\n-- 6. in the app")
            await fresh()
            r = await load(meta)
            sid = r.get('id')
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", sid)
            h = await props_html()
            ck('data-a3dpgrp="Survey Check"' in h and 'a3d-svck-fail">✗ FAIL' in h and h.count('a3d-svrow') == 8, "a surface's Survey Check: the verdict and eight checks")
            ck('data-propsurvey="control"' in h and '113=' in h and 'data-propsurveyact="export"' in h, "its control points to edit, and Export Report")
            ok = await safe("""()=>{var e=document.querySelector('#a3d-propsbody [data-propsurvey="control"]');e.value='1=99.000';e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""")
            await page.wait_for_timeout(150)
            h = await props_html()
            ck(item(await check(sid), 'control').get('status') == 'fail' and '1 off by 1.000 m' in h, "a control edited in the panel is checked, and the panel says so")
            pdf = b''
            try:
                async with page.expect_download() as dl:
                    await safe("()=>document.querySelector('#a3d-propsbody [data-propsurveyact=\"export\"]').click()")
                pdf = pathlib.Path(await (await dl.value).path()).read_bytes()
                name = (await dl.value).suggested_filename
            except Exception as e:
                name = ''
                print('      (download failed: %s)' % str(e)[:120])
            txt = pdf.decode('utf-8', 'replace')
            ck(name.endswith('-survey-check.html') and '<h1>Survey check: ' in txt and 'Bust shots' in txt and 'FAIL' in txt.upper() and 'Tolerances' in txt,
               "Export Report saves the report as a page, with its tolerances (%s)" % name)
            # the dialog: a file, and the code
            await safe("()=>window.__a3dRunCmd('survey')")
            await page.wait_for_timeout(200)
            fi = await page.query_selector('[data-a3dp="filein"]')
            if fi:
                await fi.set_input_files(str(DATA / 'seed_site_m.txt'))
                await page.wait_for_timeout(300)
            val = await safe("()=>{var t=document.querySelector('[data-a3dp=\"pts\"]');return t?t.value:'';}") or ''
            fn = await safe("()=>{var t=document.querySelector('[data-a3dp=\"fname\"]');return t?t.textContent:'';}")
            ck(val == (DATA / 'seed_site_m.txt').read_text() and fn == 'seed_site_m.txt', "SURVEY opens a file into its box")
            code = await safe("()=>{var t=document.querySelector('[data-a3dp=\"chk\"]');return t?t.value:null;}")
            ck(code == 'CHK', "and names the check-shot code, CHK by default")
            await safe("""()=>{document.querySelector('[data-a3dp="bn"]').value='5000';document.querySelector('[data-a3dp="be"]').value='2000';
                document.querySelector('[data-a3dp="bz"]').value='100';document.querySelector('[data-a3dlg="ok"]').click();}""")
            await page.wait_for_timeout(300)
            ob = await safe("()=>window.__a3dState().objs.filter(function(o){return o.t==='terrain';}).map(function(o){return {id:o.id,n:o.survey.length,c:(o.checks||[]).length};})") or []
            ck(ob and ob[-1]['n'] == 224 and ob[-1]['c'] == 6, "and makes the surface with its check shots kept out (%s)" % ob[-1:])
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dRunCmd('surveycheck')")
            await page.wait_for_timeout(150)
            sel = await safe("()=>window.__a3dSelected?window.__a3dSelected():null")
            h = await props_html()
            ck('data-a3dpgrp="Survey Check"' in h and 'FAIL - see' in await toast() and 'bust shots' in await toast(), "SURVEYCHECK selects a surface and says its verdict (%s)" % await toast())
            await safe("(i)=>window.__a3dSurveyControl(i,'113=105.234')", ob[-1]['id'] if ob else None)
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ob2 = await safe("()=>window.__a3dState().objs.filter(function(o){return o.t==='terrain';}).map(function(o){return {id:o.id,c:(o.checks||[]).length,k:o.control||null,d:(o.source||{}).duplicates||null};})") or []
            ck(ob2 and ob2[-1]['c'] == 6 and ob2[-1]['k'] == [{'p': '113', 'z': 105.234}] and ob2[-1]['d'] == ['300'], "the check shots, control and duplicates are kept with the project")
            rep = await check(ob2[-1]['id'] if ob2 else None)
            ck(item(rep, 'control').get('status') == 'pass' and rep.get('verdict') == 'fail', "and checked the same after a reload")
            ck(not errs, "no page errors (%s)" % errs[:2])
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the harness crashed')
        await browser.close()
    print("\n%d/%d checks passed\nRESULT: %s" % (ck.n - len(ck.bad), ck.n, 'PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
