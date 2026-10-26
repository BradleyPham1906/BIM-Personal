"""Ladybug Tools in the browser, unchanged, through Pyodide (reference/research-ladybug-tools.md, 3).

python3 -I wip/ladybug-poc/run.py EPW_FILE
Downloads Pyodide 0.29.5 and the pinned wheels; prints Ladybug's results and the timings.
"""
import sys, os, pathlib
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).resolve().parent
epw = open(sys.argv[1], encoding='latin-1').read()
proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
with sync_playwright() as p:
    b = p.chromium.launch(proxy={'server': proxy} if proxy else None)
    pg = b.new_context(ignore_https_errors=bool(proxy)).new_page()
    sizes = {'n': 0, 'bytes': 0}
    def resp(r):
        sizes['n'] += 1; sizes['bytes'] += int(r.headers.get('content-length') or 0)
    pg.on('response', resp)
    pg.goto(here.joinpath('page.html').as_uri())
    print(pg.evaluate('t=>run(t)', epw))
    print('honeybee', pg.evaluate('window.HB'))
    print('\n'.join(pg.evaluate('LOG')))
    print('responses', sizes)
    b.close()
