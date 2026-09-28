"""
ui_responsive_audit.py

Read-only diagnostic pass: loads canvas_v10.html at a matrix of real device
viewport sizes (phone portrait/landscape, tablet portrait/landscape, laptop,
monitor), for both the 2D drafting workspace and the 3D/BIM workspace, and
reports concrete layout problems -- horizontal overflow (the one thing that
breaks a webapp on mobile more than anything else), elements clipped outside
the viewport, and overlapping chrome -- rather than guessing at CSS fixes
blind. Also takes a screenshot per case for visual review.

This makes NO edits. Run before and after each responsive-CSS sub-phase to
see exactly what changed.

Run:  python3 ui_responsive_audit.py [path/to/canvas_v10.html] [out_dir]
"""
import asyncio, pathlib, sys, json
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/ui_audit_shots")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("phone_portrait",   390,  844),
    ("phone_landscape",  844,  390),
    ("tablet_portrait",  768, 1024),
    ("tablet_landscape", 1024, 768),
    ("laptop",           1366, 900),
    ("monitor",          1920, 1080),
    ("ultrawide",        2560, 1080),
]

OVERFLOW_PROBE = r"""
() => {
  const vw = window.innerWidth, vh = window.innerHeight;
  const docEl = document.documentElement;
  const bodyOverflowX = docEl.scrollWidth > vw + 2;
  const bodyOverflowY = docEl.scrollHeight > vh + 2;
  // Find visible CHROME elements (toolbars, panels, dialogs, ribbon, tree, dock
  // controls) whose bounding box extends past the viewport edges by a
  // meaningful margin. Deliberately EXCLUDES the infinite pannable/zoomable
  // canvas surfaces (#world under the whiteboard's #viewport, and the 3D
  // WebGL/2D drawing canvases) -- content living in world-space is expected
  // to extend past the viewport when panned or zoomed, exactly like Figma;
  // that is not a responsive-layout bug.
  const EXCLUDE_ROOTS = ['#world', '#a3d-canvas', '#a3d-glcanvas', '#edges', '#draws'];
  function insideExcluded(el) {
    for (const sel of EXCLUDE_ROOTS) { const r = document.querySelector(sel); if (r && r.contains(el)) return true; }
    return false;
  }
  const offenders = [];
  const all = document.querySelectorAll('body *');
  let checked = 0;
  for (const el of all) {
    if (checked > 4000) break; // safety cap
    if (insideExcluded(el)) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    checked++;
    const overRight = r.right - vw;
    const overBottom = r.bottom - vh;
    const overLeft = -r.left;
    const overTop = -r.top;
    if (overRight > 8 || overBottom > 8 || overLeft > 8 || overTop > 8) {
      offenders.push({
        tag: el.tagName.toLowerCase(),
        id: el.id || null,
        cls: (el.className && typeof el.className === 'string') ? el.className.slice(0, 60) : null,
        rect: { left: Math.round(r.left), top: Math.round(r.top), right: Math.round(r.right), bottom: Math.round(r.bottom) },
        overRight: Math.round(overRight), overBottom: Math.round(overBottom),
        overLeft: Math.round(overLeft), overTop: Math.round(overTop)
      });
    }
  }
  // Sort worst first, cap the list.
  offenders.sort((a, b) => Math.max(b.overRight, b.overBottom, b.overLeft, b.overTop) - Math.max(a.overRight, a.overBottom, a.overLeft, a.overTop));
  return { vw, vh, bodyOverflowX, bodyOverflowY, scrollWidth: docEl.scrollWidth, scrollHeight: docEl.scrollHeight, offenderCount: offenders.length, offenders: offenders.slice(0, 12) };
}
"""

async def audit_case(pg, label, w, h, mode):
    await pg.set_viewport_size({"width": w, "height": h})
    await pg.wait_for_timeout(350)
    res = await pg.evaluate(OVERFLOW_PROBE)
    shot = OUT / f"{mode}_{label}.png"
    await pg.screenshot(path=str(shot))
    return res, shot

async def main():
    url = pathlib.Path(TARGET).resolve().as_uri()
    report = {"canvas": {}, "drafting": {}, "bim3d": {}}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])

        # ---- Canvas whiteboard (the default landing workspace) ----
        pg = await b.new_page()
        await pg.goto(url)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
        await pg.reload()
        await pg.wait_for_timeout(1500)
        for label, w, h in VIEWPORTS:
            res, shot = await audit_case(pg, label, w, h, "canvas")
            report["canvas"][label] = {"size": [w, h], **res, "screenshot": str(shot)}
        await pg.close()

        # ---- 2D Drafting workspace (AutoCAD-style: topbar/toolbar/formatbar/sidepanel) ----
        pg1 = await b.new_page()
        await pg1.goto(url)
        await pg1.wait_for_timeout(1500)
        await pg1.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
        await pg1.reload()
        await pg1.wait_for_timeout(1500)
        # Real UI flow: click the doc-tabs "+" (New Drawing), same path a user takes.
        opened = await pg1.evaluate("""()=>{
            const btn = document.querySelector('#acad-doctabs [data-dt="plus"]');
            if (btn) { btn.click(); return true; }
            return false;
        }""")
        await pg1.wait_for_timeout(800)
        for label, w, h in VIEWPORTS:
            res, shot = await audit_case(pg1, label, w, h, "drafting")
            report["drafting"][label] = {"size": [w, h], "opened_via_plus": opened, **res, "screenshot": str(shot)}
        await pg1.close()

        # ---- 3D/BIM workspace ----
        pg2 = await b.new_page()
        await pg2.goto(url)
        await pg2.wait_for_timeout(1500)
        await pg2.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
        await pg2.reload()
        await pg2.wait_for_timeout(1500)
        await pg2.evaluate("()=>{ if (window.__a3dEnter) window.__a3dEnter(); }")
        await pg2.wait_for_timeout(1200)
        for label, w, h in VIEWPORTS:
            res, shot = await audit_case(pg2, label, w, h, "bim3d")
            report["bim3d"][label] = {"size": [w, h], **res, "screenshot": str(shot)}
        await pg2.close()

        await b.close()

    print(json.dumps(report, indent=2)[:200])  # sanity print, full report goes to file
    (OUT / "report.json").write_text(json.dumps(report, indent=2))

    print("\n================ SUMMARY ================")
    for ws in ("canvas", "drafting", "bim3d"):
        print(f"\n-- {ws.upper()} workspace --")
        for label, data in report[ws].items():
            flag = "PAGE-SCROLL" if (data["bodyOverflowX"] or data["bodyOverflowY"]) else "ok"
            print(f"  {label:18s} {data['size'][0]:5d}x{data['size'][1]:<5d} {flag:8s} offenders={data['offenderCount']:3d} scrollW={data['scrollWidth']:5d} (vw={data['vw']})")
            if data["offenderCount"] > 0:
                for o in data["offenders"][:5]:
                    tag = f"{o['tag']}#{o['id']}" if o['id'] else f"{o['tag']}.{(o['cls'] or '').split()[0] if o['cls'] else ''}"
                    print(f"      - {tag:30s} rect={o['rect']} overR={o['overRight']} overB={o['overBottom']} overL={o['overLeft']} overT={o['overTop']}")
    print(f"\nFull report + screenshots: {OUT}")

asyncio.run(main())
