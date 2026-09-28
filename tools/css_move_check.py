"""css_move_check.py OLD.html NEW.html -- every rule of every stylesheet, in document order, after
the engine has built its UI: the two builds must hold the same list, cssText for cssText."""
import asyncio, sys, json
from playwright.async_api import async_playwright
OLD, NEW = sys.argv[1], sys.argv[2]
# --removed=SELECTOR (repeatable): a rule the change deletes on purpose, left out of the old list
REMOVED = [a.split('=', 1)[1] for a in sys.argv[3:] if a.startswith('--removed=')]
JS = """()=>{var out=[];for(var i=0;i<document.styleSheets.length;i++){var s=document.styleSheets[i],o=s.ownerNode;
 var rules=[];try{for(var j=0;j<s.cssRules.length;j++)rules.push(s.cssRules[j].cssText);}catch(e){rules.push('ERR '+e);}
 out.push({owner:(o&&o.id)||(o&&o.tagName)||'',parent:o&&o.parentNode?o.parentNode.tagName:'',n:rules.length,rules:rules});}return out;}"""
async def grab(path):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1600, 'height': 950})
        await pg.goto('file://' + path)
        await pg.wait_for_function('()=>window.__a3dOn===true', timeout=20000)
        await pg.wait_for_timeout(800)
        r = await pg.evaluate(JS)
        await b.close()
        return r
async def main():
    a = await grab(OLD); b = await grab(NEW)
    print('old sheets', [(x['owner'], x['parent'], x['n']) for x in a])
    print('new sheets', [(x['owner'], x['parent'], x['n']) for x in b])
    fa = [r for x in a for r in x['rules'] if not any(r.startswith(sel + ' {') for sel in REMOVED)]
    fb = [r for x in b for r in x['rules']]
    print('rules old', len(fa), 'new', len(fb), 'IDENTICAL' if fa == fb else 'DIFFERENT')
    if fa != fb:
        for i, (x, y) in enumerate(zip(fa, fb)):
            if x != y:
                print('first difference at', i); print(' old', x[:200]); print(' new', y[:200]); break
    sys.exit(0 if fa == fb else 1)
asyncio.run(main())
