#!/usr/bin/env python3
"""dump_catalog.py -- the app's own command catalogue and keyboard shortcuts, as JSON for the guide.

  python3 tools/dump_catalog.py [canvas_v10.html] [docs/data/catalog.json]

Opens the build headless (Playwright), reads the same catalogue the command search uses
(window.__a3dCommandCatalog) and the shortcuts panel's keys (window.__a3dShortcuts), with the
app's version, and writes them sorted. The guide's command reference is built from this file, and
the V142 suite fails when it no longer matches the build -- so the reference cannot fall behind."""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'canvas_v10.html'
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'docs' / 'data' / 'catalog.json'


async def read(html):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page()
        await p.goto('file://' + str(html))
        await p.wait_for_timeout(2000)
        d = await p.evaluate("""()=>({version:window.__a3dVersion?window.__a3dVersion():null,
          commands:window.__a3dCommandCatalog().map(function(c){return {id:c.id,name:c.name,aliases:c.aliases||[],desc:c.desc||'',kind:c.kind,
            where:c.where||[],keys:c.keys||null,anchor:window.__a3dDocsAnchor?window.__a3dDocsAnchor(c.id):c.id};}),
          shortcuts:window.__a3dShortcuts().map(function(g){return {grp:g.grp,rows:g.rows.map(function(r){return {keys:r.keys,alt:!!r.alt,label:r.label,cmd:r.cmd||null};})};})})""")
        await b.close()
    d['commands'].sort(key=lambda c: (c['name'], c['id']))
    return d


def main():
    d = asyncio.run(read(HTML))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%s: %d commands, %d shortcut groups, version %s' % (OUT, len(d['commands']), len(d['shortcuts']), (d['version'] or {}).get('v')))


if __name__ == '__main__':
    main()
