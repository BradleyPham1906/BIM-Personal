"""
bim_phase42_browser_tests.py

Phase 42 regression suite: level-datum integrity, structural grid datums, beam engine.
Loads the real canvas_v10.html in Chromium and evaluates data/test_3d5.js against the
shipped code, so the assertions exercise production paths, not a prototype copy.

Run:  python3 bim_phase42_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"
SUITE = pathlib.Path(__file__).with_name("data") / "test_3d5.js"

async def main():
    src = SUITE.read_text(encoding="utf-8")
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        page_errors = []
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        await pg.goto(pathlib.Path(TARGET).absolute().as_uri())
        await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
        await pg.evaluate("()=>window.__a3dEnter&&window.__a3dEnter()")
        await pg.wait_for_timeout(800)
        res = await pg.evaluate("()=>eval(" + repr(src).replace("'", '"', 0) + ")"
                                if False else "(src)=>eval(src)", src)
        for ln in res["lines"]:
            print(ln)
        print("\n%d checks, %d failed" % (res["pass"] + res["fail"], res["fail"]))
        if page_errors:
            print("\nUNCAUGHT PAGE ERRORS:")
            for e in page_errors[:10]:
                print("  " + e)
        await b.close()
        bad = res["fail"] or page_errors
        print("RESULT:", "FAIL" if bad else "PASS")
        sys.exit(1 if bad else 0)

asyncio.run(main())
