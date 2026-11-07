import asyncio, pathlib, json
from playwright.async_api import async_playwright

SIZES = [
    ("phone",   390,  844),
    ("ipad",    820, 1180),
    ("laptop", 1440,  900),
    ("monitor",1920, 1080),
]

PROBE = r"""
() => {
  function rect(sel) { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return { sel, left: Math.round(r.left), top: Math.round(r.top), right: Math.round(r.right), bottom: Math.round(r.bottom),
             display: cs.display, visibility: cs.visibility, opacity: cs.opacity, z: cs.zIndex }; }
  const ids = ['#acad-shell', '#acad-tabs', '#acad-panels', '#acad-doctabs', '#figma-layers-shell', '#figma-layers-rail', '#figma-layers-panel', '#viewport', '#sidepanel', '#acad-start'];
  const rects = {}; ids.forEach(s => rects[s] = rect(s));
  const bodyClasses = document.body.className;
  // Overlap check: does the ribbon's bottom edge exceed where the layers panel starts?
  let overlapPx = null;
  if (rects['#acad-shell'] && rects['#figma-layers-panel']) {
    const ribbonBottom = rects['#acad-shell'].bottom;
    const panelTop = rects['#figma-layers-panel'].top;
    overlapPx = ribbonBottom - panelTop; // positive = overlap, negative = gap
  }
  return { bodyClasses, rects, overlapPx };
}
"""

async def main():
    url = pathlib.Path("canvas_v10.html").resolve().as_uri()
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for label, w, h in SIZES:
            pg = await b.new_page(viewport={"width": w, "height": h})
            await pg.goto(url)
            await pg.wait_for_timeout(1200)
            await pg.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
            await pg.reload()
            await pg.wait_for_timeout(1200)
            res = await pg.evaluate(PROBE)
            print(f"\n=== {label} {w}x{h} ===")
            print("body classes:", res["bodyClasses"])
            print("overlapPx (ribbon bottom - layers panel top):", res["overlapPx"])
            for sel, r in res["rects"].items():
                print(f"  {sel:24s} {r}")
            await pg.screenshot(path=f"/tmp/overlap_{label}.png")
            await pg.close()
        await b.close()

asyncio.run(main())
