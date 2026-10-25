#!/usr/bin/env python3
"""check_site.py -- the multi-file app Pages serves runs as the one-file build does.

  python3 tools/check_site.py

Builds the site into a temporary folder, serves it over http (as Pages does, not file://), and opens
index.html (the page, app/app.css and the three scripts) and canvas_v10.html (one file) at a
desktop and a phone size. Each must load every file it asks for, with no page error and no engine
error (__a3dErr), and the two must agree on every phase marker (window.__acad3dV*), the version,
the globals, the elements the engine built, and the pixels of the first screen. Needs Playwright's Python package and Pillow, as the
suites do."""
import asyncio, functools, http.server, io, pathlib, sys, tempfile, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_app  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402

SIZES = (('desktop', 1440, 900), ('phone', 390, 844))
READ = """() => {
  var m = {};
  Object.keys(window).filter(function(k){ return /^__acad3dV/.test(k); }).sort().forEach(function(k){ m[k] = String(window[k]); });
  return {markers: m, err: window.__a3dErr || null,
          version: (window.__a3dVersion && JSON.stringify(window.__a3dVersion())) || null,
          globals: Object.keys(window).sort().join(' '),
          elements: document.querySelectorAll('*').length,
          ids: Array.prototype.map.call(document.querySelectorAll('[id]'), function(e){ return e.id; }).sort().join(' ')};
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


async def load(browser, url, w, h):
    page = await browser.new_page(viewport={'width': w, 'height': h})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('requestfailed', lambda r: errors.append('failed: ' + r.url))
    page.on('response', lambda r: r.status >= 400 and errors.append('%d: %s' % (r.status, r.url)))
    await page.goto(url, wait_until='load')
    await page.wait_for_timeout(1500)
    state = await page.evaluate(READ)
    shot = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
    await page.close()
    return state, errors, shot


async def run(base):
    fails = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, w, h in SIZES:
            a, ea, sa = await load(browser, base + '/index.html', w, h)
            b, eb, sb = await load(browser, base + '/canvas_v10.html', w, h)
            px = ImageChops.difference(sa, sb).getbbox()
            checks = [
                ('every file loaded, no page error: the multi-file app', not ea, ea[:3]),
                ('every file loaded, no page error: the one file', not eb, eb[:3]),
                ('no engine error', a['err'] is None and b['err'] is None, (a['err'], b['err'])),
                ('the same phase markers (%d)' % len(b['markers']), a['markers'] == b['markers'] and len(a['markers']) > 100,
                 sorted(set(a['markers']) ^ set(b['markers']))[:5]),
                ('the same version', a['version'] == b['version'], (a['version'], b['version'])),
                ('the same globals (%d)' % len(b['globals'].split()), a['globals'] == b['globals'],
                 sorted(set(a['globals'].split()) ^ set(b['globals'].split()))[:5]),
                ('the same elements (%d)' % b['elements'], a['elements'] == b['elements'] and a['ids'] == b['ids'],
                 (a['elements'], b['elements'])),
                ('the same pixels', px is None, px),
            ]
            for label, ok, why in checks:
                print('%s  %s: %s%s' % ('PASS' if ok else 'FAIL', name, label, '' if ok else '  %r' % (why,)))
                fails += 0 if ok else 1
        await browser.close()
    return fails


def main():
    with tempfile.TemporaryDirectory() as d:
        build_app.write_site(d)
        (pathlib.Path(d) / 'canvas_v10.html').write_bytes(build_app.one_file().encode('utf-8'))
        handler = functools.partial(Quiet, directory=d)
        srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            fails = asyncio.run(run('http://127.0.0.1:%d' % srv.server_address[1]))
        finally:
            srv.shutdown()
    print('%d failures' % fails)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
