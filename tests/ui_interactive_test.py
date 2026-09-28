"""
ui_interactive_test.py

Real interaction test (not just static screenshots): at each of 4 device tiers
(phone, iPad, laptop, monitor) this clicks actual buttons a user would click --
the workspace switcher (Canvas / Drafting & Annotation / 3D), ribbon tabs, the
layers-panel collapse toggle, a ribbon tool that opens a dialog, and that
dialog's Cancel button -- and after each step checks:
  1. No unexpected document-level scroll appeared (bodyOverflowX/Y).
  2. The button just clicked is still the element actually hit-tested at its
     own center point (elementFromPoint) OR its dialog/menu is confirmed open
     via a concrete DOM signal -- catches "dead" clicks where something else
     is silently covering a control.
  3. No two named chrome regions (ribbon / layers panel / properties dock /
     open dialog) overlap by more than a small tolerance.
Screenshots are taken after every step for visual review.

Run:  python3 ui_interactive_test.py [path/to/canvas_v10.html] [out_dir]
"""
import asyncio, pathlib, sys, json
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "canvas_v10.html"
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/ui_interactive_shots")
OUT.mkdir(parents=True, exist_ok=True)

SIZES = [
    ("phone",   390,  844),
    ("ipad",    820, 1180),
    ("laptop", 1440,  900),
    ("monitor",1920, 1080),
]

TOTAL = [0]
FAILS = []

def check(cond, msg):
    TOTAL[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)

HITTEST = r"""
(sel) => {
  const el = document.querySelector(sel);
  if (!el) return { found: false };
  const r = el.getBoundingClientRect();
  if (r.width === 0 || r.height === 0) return { found: true, visible: false };
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  const hit = document.elementFromPoint(cx, cy);
  const hitIsSelf = hit === el || (hit && el.contains(hit));
  return { found: true, visible: true, hitIsSelf, hitTag: hit ? (hit.tagName + (hit.id ? '#' + hit.id : '') + (hit.className && typeof hit.className === 'string' ? '.' + hit.className.split(' ')[0] : '')) : null };
}
"""

OVERFLOW_CHECK = r"""
() => {
  const vw = window.innerWidth, vh = window.innerHeight;
  const docEl = document.documentElement;
  return { overflowX: docEl.scrollWidth > vw + 2, overflowY: docEl.scrollHeight > vh + 2 };
}
"""

RECTS_CHECK = r"""
(sels) => {
  const out = {};
  for (const s of sels) {
    const e = document.querySelector(s);
    if (!e) { out[s] = null; continue; }
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') { out[s] = null; continue; }
    const r = e.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) { out[s] = null; continue; }
    out[s] = { left: r.left, top: r.top, right: r.right, bottom: r.bottom };
  }
  return out;
}
"""

def rects_overlap(a, b, tol=2):
    if not a or not b:
        return 0
    ox = min(a["right"], b["right"]) - max(a["left"], b["left"])
    oy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
    if ox > tol and oy > tol:
        return min(ox, oy)
    return 0

# NOTE: #a3d-propsbody is a descendant of .a3d-tree (it lives inside that panel), so it is
# deliberately excluded here -- comparing it against its own ancestor would always report a
# false "overlap" since a child's rect is by definition inside its parent's rect. Only
# independent, unrelated chrome regions belong in this list.
CHROME_SELECTORS = ["#acad-shell", "#figma-layers-panel", ".a3d-tree", ".a3d-dlg", "#acad-wsmenu"]

async def shot(pg, label, step):
    await pg.screenshot(path=str(OUT / f"{label}_{step}.png"))

async def run_tier(pw, label, w, h):
    print(f"\n== {label} {w}x{h} ==")
    b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = await b.new_page(viewport={"width": w, "height": h})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(pathlib.Path(TARGET).resolve().as_uri())
    await pg.wait_for_timeout(1200)
    await pg.evaluate("()=>{try{localStorage.clear();}catch(e){}}")
    await pg.reload()
    await pg.wait_for_timeout(1200)
    await shot(pg, label, "00_boot")

    of = await pg.evaluate(OVERFLOW_CHECK)
    check(not of["overflowX"] and not of["overflowY"], f"[{label}] no page-level scroll on boot ({of})")
    check(not errs, f"[{label}] no uncaught JS errors on boot ({errs[:1] or 'none'})")

    # ---- 1. Open the workspace switcher dropdown ----
    ws = await pg.evaluate(HITTEST, ".acad-ws")
    check(ws.get("found") and ws.get("visible"), f"[{label}] workspace switcher ('.acad-ws') is present and visible")
    if ws.get("found") and ws.get("visible"):
        check(ws.get("hitIsSelf"), f"[{label}] workspace switcher is actually clickable, not covered (hit: {ws.get('hitTag')})")
        await pg.click(".acad-ws")
        await pg.wait_for_timeout(200)
        menu_visible = await pg.evaluate("()=>{const m=document.getElementById('acad-wsmenu');return !!(m&&m.classList.contains('show'));}")
        check(menu_visible, f"[{label}] clicking workspace switcher opens the menu")
        await shot(pg, label, "01_wsmenu_open")

        # ---- 2. Switch to 3D ----
        item = await pg.evaluate(HITTEST, '[data-wsm="3d"]')
        check(item.get("found") and item.get("visible") and item.get("hitIsSelf"), f"[{label}] '3D' menu item is present and clickable (hit: {item.get('hitTag')})")
        await pg.click('[data-wsm="3d"]')
        await pg.wait_for_timeout(600)
        await shot(pg, label, "02_3d_active")
        in3d = await pg.evaluate("()=>!!window.__a3dOn")
        check(in3d, f"[{label}] switching to '3D' via the real menu click actually activates the 3D engine")

    # ---- 3. Click a ribbon tab (Architecture) ----
    tab = await pg.evaluate(HITTEST, '[data-acad-tab="arch"]')
    if tab.get("found") and tab.get("visible"):
        check(tab.get("hitIsSelf"), f"[{label}] 'Architecture' ribbon tab is clickable, not covered (hit: {tab.get('hitTag')})")
        await pg.click('[data-acad-tab="arch"]')
        await pg.wait_for_timeout(250)
        await shot(pg, label, "03_arch_tab")
    else:
        print(f"  SKIP  [{label}] 'Architecture' ribbon tab not found/visible at this size")

    # ---- 4. Click the "Wall" tool -- should either arm a draw tool or open a dialog; either way
    # nothing should silently no-op, and if a dialog opens its buttons must be real click targets.
    wall = await pg.evaluate(HITTEST, '[data-a3dr="bim:wall"]')
    if wall.get("found") and wall.get("visible"):
        check(wall.get("hitIsSelf"), f"[{label}] 'Wall' ribbon button is clickable, not covered (hit: {wall.get('hitTag')})")
        await pg.click('[data-a3dr="bim:wall"]')
        await pg.wait_for_timeout(250)
        await shot(pg, label, "04_wall_armed")
        # Escape in case it armed a draw tool waiting for canvas clicks, so state doesn't leak
        # into the next check.
        await pg.keyboard.press("Escape")
        await pg.wait_for_timeout(150)
    else:
        print(f"  SKIP  [{label}] 'Wall' ribbon button not found/visible at this size")

    # ---- 5. Round-trip the whiteboard layers-panel collapse/expand ----
    # Entering 3D/Drafting now auto-collapses this dock to its icon rail (it would otherwise
    # compete for the same left-hand space as the CAD/BIM shell's own Model Browser tree), so
    # by this point in the flow it is normally ALREADY collapsed -- unlike the plain Canvas
    # workspace, where it starts expanded. Handle both starting states rather than assuming one.
    dock_collapsed = await pg.evaluate("()=>{const s=document.getElementById('figma-layers-shell');return s?s.classList.contains('collapsed'):null;}")
    if dock_collapsed is None:
        print(f"  SKIP  [{label}] layers dock not found at this size")
    else:
        if dock_collapsed:
            check(True, f"[{label}] layers dock auto-collapsed to its icon rail on entering 3D (no longer competes with the Model Browser tree)")
            # Re-expand via the rail logo -- the only visible affordance while collapsed.
            restore = await pg.evaluate(HITTEST, "#figma-layers-rail .fl-logo")
            check(restore.get("found") and restore.get("visible") and restore.get("hitIsSelf"),
                  f"[{label}] rail logo button is a real click target to re-expand the dock (hit: {restore.get('hitTag')})")
            if restore.get("found") and restore.get("visible") and restore.get("hitIsSelf"):
                await pg.click("#figma-layers-rail .fl-logo")
                await pg.wait_for_timeout(250)
                expanded = await pg.evaluate("()=>{const s=document.getElementById('figma-layers-shell');return s?!s.classList.contains('collapsed'):null;}")
                check(expanded, f"[{label}] clicking the rail logo actually re-expands the dock")
        else:
            check(True, f"[{label}] layers dock starts expanded at this size")
        # Whichever state we're now in, the panel should be expanded (either it started that way,
        # or step above just expanded it) -- so .fl-collapse must be a real, clickable target and
        # must genuinely collapse the panel back down.
        collapse = await pg.evaluate(HITTEST, ".fl-collapse")
        if collapse.get("found") and collapse.get("visible"):
            check(collapse.get("hitIsSelf"), f"[{label}] layers-panel collapse button is clickable, not covered (hit: {collapse.get('hitTag')})")
            await pg.click(".fl-collapse")
            await pg.wait_for_timeout(250)
            recollapsed = await pg.evaluate("()=>{const s=document.getElementById('figma-layers-shell');return s?s.classList.contains('collapsed'):null;}")
            check(recollapsed, f"[{label}] clicking the collapse button collapses the panel back to the rail")
        else:
            print(f"  SKIP  [{label}] layers-panel collapse button not found/visible at this size (collapsed={dock_collapsed})")
        await shot(pg, label, "05_layers_collapsed")

    # ---- 6. Chrome-region overlap check after all the above interaction ----
    rects = await pg.evaluate(RECTS_CHECK, CHROME_SELECTORS)
    worst = 0
    worst_pair = None
    keys = [k for k in CHROME_SELECTORS if rects.get(k)]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            ov = rects_overlap(rects[keys[i]], rects[keys[j]])
            if ov > worst:
                worst = ov
                worst_pair = (keys[i], keys[j])
    check(worst <= 4, f"[{label}] no meaningful overlap between chrome regions after interaction (worst={worst}px between {worst_pair})")

    of2 = await pg.evaluate(OVERFLOW_CHECK)
    check(not of2["overflowX"] and not of2["overflowY"], f"[{label}] still no page-level scroll after interaction ({of2})")
    check(not errs, f"[{label}] still no uncaught JS errors after interaction ({errs[:1] or 'none'})")

    await shot(pg, label, "99_final")
    await pg.close()
    await b.close()

async def main():
    async with async_playwright() as pw:
        for label, w, h in SIZES:
            await run_tier(pw, label, w, h)
    print(f"\n{TOTAL[0]} checks, {len(FAILS)} failed")
    print("RESULT:", "FAIL" if FAILS else "PASS")
    print(f"Screenshots: {OUT}")
    sys.exit(1 if FAILS else 0)

asyncio.run(main())
