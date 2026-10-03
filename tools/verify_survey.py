#!/usr/bin/env python3
"""verify_survey.py -- check a survey file with the app itself, headless, and write its report.

The checks are the app's own (V138's Survey Check), run in the real page, so this and the app can
never disagree.

  python3 tools/verify_survey.py SURVEY.txt [--format PNEZD] [--units m|ft|usft]
                                 [--base N,E,Z] [--code CHK] [--control "105=30.000, 201=28.45"]
                                 [--out report.html] [--app canvas_v10.html]
  python3 tools/verify_survey.py tests/data/surveys/NAME.json      (a sidecar: its file and settings)

Prints each check and the verdict; writes the report page next to the survey (or to --out). The exit
status is 0 for pass, 1 for warn, 2 for fail, 3 when the file cannot be read.

To make a survey part of the regression: put it in tests/data/surveys/ with a sidecar JSON
({"file", "format", "units", "base", "checkCode", "control", "expect": {...}}; see the seeds made
by tools/make_seed_survey.py). tests/bim_phase138_survey_check_browser_tests.py then holds every
later build to what the sidecar expects.

Needs Python's Playwright and Chromium (pip install playwright; playwright install chromium).
"""
import argparse, asyncio, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def parse():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('survey', help='a survey text file, or a sidecar .json')
    ap.add_argument('--format', default=None, choices=['PNEZD', 'PENZD', 'NEZ', 'ENZ'])
    ap.add_argument('--units', default=None, choices=['m', 'ft', 'usft'])
    ap.add_argument('--base', default=None, help='N,E,Z: the survey point at model 0,0 and the elevation at model 0 (default: the first point, 0)')
    ap.add_argument('--code', default=None, help='the description that marks check shots (default CHK; "" for none)')
    ap.add_argument('--control', default=None, help='known elevations, "name=elev, ..." in the survey units')
    ap.add_argument('--out', default=None, help='where to write the report page')
    ap.add_argument('--app', default=str(ROOT / 'canvas_v10.html'))
    return ap.parse_args()


async def main():
    a = parse()
    src = pathlib.Path(a.survey).resolve()
    meta = {}
    if src.suffix.lower() == '.json':
        meta = json.loads(src.read_text())
        src = src.parent / meta['file']
    try:
        text = src.read_text()
    except OSError as e:
        print('cannot read %s: %s' % (src, e))
        return 3
    fmt = a.format or meta.get('format', 'PNEZD')
    units = a.units or meta.get('units', 'm')
    base = meta.get('base')
    if a.base:
        n, e, z = (float(v) for v in a.base.split(','))
        base = {'n': n, 'e': e, 'z': z}
    code = a.code if a.code is not None else meta.get('checkCode', 'CHK')
    control = a.control if a.control is not None else meta.get('control', '')
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.goto('file://' + str(pathlib.Path(a.app).resolve()))
        await page.wait_for_function('()=>!!window.__acad3dV138', timeout=30000)
        r = await page.evaluate("(a)=>window.__a3dSurveyImport(a[0],a[1],a[2],a[3],a[4])", [text, fmt, units, base, code])
        if not r or r.get('error'):
            print('%s: %s' % (src.name, (r or {}).get('error', 'no surface')))
            await browser.close()
            return 3
        if control:
            await page.evaluate("(a)=>window.__a3dSurveyControl(a[0],a[1])", [r['id'], control])
        rep = await page.evaluate("(i)=>window.__a3dSurveyCheck(i)", r['id'])
        html = await page.evaluate("(i)=>window.__a3dSurveyReportHtml(i)", r['id'])
        await browser.close()
    print('%s  (%s, %s)' % (src.name, fmt, units))
    for it in rep['items']:
        print('  %-5s %-20s %s' % (it['status'].upper(), it['label'], it['text']))
    print('VERDICT: %s' % rep['verdict'].upper())
    out = pathlib.Path(a.out) if a.out else src.with_name(src.stem + '-survey-check.html')
    out.write_text(html)
    print('report: %s' % out)
    ex = meta.get('expect')
    if ex and ex.get('verdict') and ex['verdict'] != rep['verdict']:
        print('NOTE: the sidecar expects %s' % ex['verdict'].upper())
    return {'pass': 0, 'warn': 1, 'fail': 2}[rep['verdict']]


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
