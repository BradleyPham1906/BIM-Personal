"""
Phase 67 -- BIM status bar.

Anchored search-and-replace against the byte-count-verified canvas_v10.html. Every anchor is
asserted to occur EXACTLY ONCE before substitution; any miss aborts before a byte is written.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'e37aadb1126d80ed2c9b077b55e2a940d5231362b6be5c360332581d07652807'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new):
    patches.append((name, old, new))


# ---------------------------------------------------------------- 1. CSS: the bar itself
P('css.statusbar',
  "    '.a3d-body{display:flex;flex:1 1 auto;min-height:0}'+",
  "    '.a3d-body{display:flex;flex:1 1 auto;min-height:0}'+\n"
  "    /* __acad3dV67: the BIM status bar. Phase 64 documented the last remaining shell\n"
  "       difference: the 2D workspace has #acad-status pinned to the bottom of the window and\n"
  "       the BIM workspace had nothing there, because #acad-status's four toggles drive\n"
  "       window.CAD/cadRun (the 2D engine) and would be dead controls in BIM. This is the\n"
  "       honest fix -- the same 26px strip, the same colours, type and toggle language, in the\n"
  "       same screen position, carrying BIM's OWN state. It is the third flex child of #acad3d\n"
  "       (toolbar / body / status) so it spans the work area exactly, which is what the\n"
  "       --figma-dock-w contract already defines as \"the same position\" in this shell. */\n"
  "    '.a3d-status{display:flex;align-items:center;gap:8px;padding:0 10px;height:26px;flex:0 0 auto;"
  "background:#1d2022;border-top:1px solid #101214;"
  "font:11px/1 \"Segoe UI\",Inter,system-ui,sans-serif;color:#a9abae;user-select:none}'+\n"
  "    '.a3d-stspring{flex:1 1 auto}'+\n"
  "    '.a3d-sthint{color:#9ec1ff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}'+\n"
  "    '.a3d-stcoords{font-variant-numeric:tabular-nums;color:#c8ced6;white-space:nowrap;"
  "min-width:150px;text-align:right}'+\n"
  "    '.a3d-stlvl{display:flex;align-items:center;gap:5px;white-space:nowrap}'+\n"
  "    '.a3d-stlvl select{background:#24282c;border:1px solid #3a4048;color:#dfe4ea;border-radius:3px;"
  "font-size:11px;padding:1px 4px;font-family:inherit;max-width:140px}'+\n"
  "    '#a3d-snapgrp{display:flex;gap:4px}'+\n"
  "    '.a3d-stbtn{display:inline-flex;align-items:center;gap:5px;background:transparent;"
  "border:1px solid transparent;color:#8d9196;border-radius:3px;"
  "font-size:10.5px;letter-spacing:.04em;padding:3px 7px;cursor:pointer;font-family:inherit}'+\n"
  "    '.a3d-stbtn svg{width:12px;height:12px;flex:0 0 auto}'+\n"
  "    '.a3d-stbtn:hover{background:#2b3138;color:#dfe4ea}'+\n"
  "    '.a3d-stbtn.on{background:#2f5d8a;border-color:#3f75a8;color:#e6eef6}'+")

# ---------------------------------------------------------------- 2. CSS: pref + compact tier
P('css.pillpos',
  "    '#a3d-snappill{position:absolute;left:14px;bottom:14px;display:flex;gap:4px;"
  "background:#22262b;border:1px solid #3a4048;border-radius:8px;padding:4px;z-index:9600;"
  "box-shadow:0 4px 14px rgba(0,0,0,0.35)}'+\n",
  "")

P('css.hidepanel',
  "    '#a3d-snappill.a3d-hide-panel,#a3d-pill.a3d-hide-panel{display:none}'+",
  "    '#a3d-snapgrp.a3d-hide-panel,#a3d-pill.a3d-hide-panel{display:none}'+")

P('css.compact',
  "      '#a3d-pill,#a3d-snappill{padding:6px}'+",
  "      '#a3d-pill{padding:6px}'+\n"
  "      /* On the compact tier the bar is the ONLY snap surface, so its buttons have to be\n"
  "         thumb-sized like the pills they replaced; the hint text is what gives way for them. */\n"
  "      '.a3d-status{height:40px}'+\n"
  "      '.a3d-sthint{display:none}'+\n"
  "      '.a3d-stbtn{padding:9px 11px;font-size:12px}'+\n"
  "      '.a3d-stcoords{min-width:0;font-size:10.5px}'+\n"
  "      '.a3d-stlvl select{font-size:13px;max-width:96px}'+")

# ---------------------------------------------------------------- 3. markup: retire the pill
P('markup.removepill',
  "      '<div id=\"a3d-snappill\">'+\n"
  "      '<button class=\"a3d-pbtn on\" data-a3dsnap=\"point\" title=\"Object snap (F3)\">'+PILL_SNAP+'</button>'+\n"
  "      '<button class=\"a3d-pbtn\" data-a3dsnap=\"ortho\" title=\"Ortho lock (F8)\">'+PILL_ORTHO+'</button>'+\n"
  "      '<button class=\"a3d-pbtn\" data-a3dsnap=\"grid\" title=\"Grid snap (F9)\">'+PILL_GRID+'</button>'+\n"
  "      '</div>'+\n"
  "      '<div id=\"a3d-pill\">'+",
  "      /* __acad3dV67: the floating snap pill moved into the status bar. Two surfaces carrying\n"
  "         the same three A3D_SNAP toggles would be duplicate controls, and the pill sat at\n"
  "         left:14px;bottom:14px -- exactly where the bar now is. The navigation pill stays: it\n"
  "         carries camera state, not drawing state, and belongs over the viewport it drives. */\n"
  "      '<div id=\"a3d-pill\">'+")

# ---------------------------------------------------------------- 4. markup: add the bar
P('markup.statusbar',
  "      '</div></div>'+\n"
  "    '</div>';\n"
  "    document.body.appendChild(root);",
  "      '</div></div>'+\n"
  "    '</div>'+\n"
  "    '<div class=\"a3d-status\" id=\"a3d-statusbar\">'+\n"
  "      '<span id=\"a3d-sthint\" class=\"a3d-sthint\"></span>'+\n"
  "      '<span class=\"a3d-stspring\"></span>'+\n"
  "      '<label class=\"a3d-stlvl\" title=\"Active level -- new walls, floors and sketches are placed here\">'+\n"
  "        'Level <select id=\"a3d-stlevel\"></select></label>'+\n"
  "      '<span id=\"a3d-stcoords\" class=\"a3d-stcoords\" title=\"Cursor position on the active level plane\">\\u2014</span>'+\n"
  "      '<span id=\"a3d-snapgrp\">'+\n"
  "        '<button class=\"a3d-stbtn\" data-a3dsnap=\"point\" title=\"Object snap (F3)\">'+PILL_SNAP+'<span>SNAP</span></button>'+\n"
  "        '<button class=\"a3d-stbtn\" data-a3dsnap=\"ortho\" title=\"Ortho lock (F8)\">'+PILL_ORTHO+'<span>ORTHO</span></button>'+\n"
  "        '<button class=\"a3d-stbtn\" data-a3dsnap=\"grid\" title=\"Grid snap (F9)\">'+PILL_GRID+'<span>GRID</span></button>'+\n"
  "      '</span>'+\n"
  "    '</div>';\n"
  "    document.body.appendChild(root);")

# ---------------------------------------------------------------- 5. pref target + label
P('pref.map',
  "  var UI_PANEL_MAP={sidebar:'.a3d-tree',snappill:'#a3d-snappill',navpill:'#a3d-pill',hud:'.a3d-hud'};",
  "  /* __acad3dV67: the 'snappill' KEY is kept although the pill is gone, so a user who had\n"
  "     already hidden the snap toggles keeps them hidden -- the saved preference is about the\n"
  "     controls, not about the element that used to host them. Only the target and label move. */\n"
  "  var UI_PANEL_MAP={sidebar:'.a3d-tree',snappill:'#a3d-snapgrp',navpill:'#a3d-pill',hud:'.a3d-hud'};")

P('pref.label',
  "          '<label><input type=\"checkbox\" data-a3dui=\"snappill\" checked> Snap Pill</label>'+",
  "          '<label><input type=\"checkbox\" data-a3dui=\"snappill\" checked> Snap Toggles</label>'+")

# ---------------------------------------------------------------- 6. element refs + wiring
P('wire.refs',
  "    el.snappill=root.querySelector('#a3d-snappill');",
  "    el.sthint=root.querySelector('#a3d-sthint');\n"
  "    el.stcoords=root.querySelector('#a3d-stcoords');\n"
  "    el.stlevel=root.querySelector('#a3d-stlevel');\n"
  "    if(el.stlevel)el.stlevel.addEventListener('change',function(){\n"
  "      setActiveLevel(el.stlevel.value);\n"
  "    });\n"
  "    el.snappill=root.querySelector('#a3d-snapgrp');")

P('wire.hover',
  "    el.cv.addEventListener('mousemove',onHover);",
  "    el.cv.addEventListener('mousemove',onHover);\n"
  "    /* __acad3dV67: onHover only runs while a sketch is active (it returns early on !A3D.sk),\n"
  "       so the coordinate read-out needs its own listener or it would be blank except while\n"
  "       drawing -- which is the one time the on-canvas length label already tells you. */\n"
  "    el.cv.addEventListener('mousemove',bimStatusHover);\n"
  "    el.cv.addEventListener('mouseleave',bimStatusHoverOut);")

# ---------------------------------------------------------------- 7. the status bar's own code
P('code.status',
  "  var A3D_SNAP={point:true,grid:false,gridSize:0.5,ortho:false,pxThreshold:12};\n"
  "  function syncSnapPill(){",
  "  var A3D_SNAP={point:true,grid:false,gridSize:0.5,ortho:false,pxThreshold:12};\n"
  "  /* __acad3dV67: BIM status bar read-outs. Every field here reflects state the BIM engine\n"
  "     actually owns -- A3D.sk, A3D.sel/selSet, A3D.levels/activeLevel, A3D_SNAP -- which is the\n"
  "     whole reason the 2D bar could not simply be shown in this mode. */\n"
  "  function bimStatusHintText(){\n"
  "    var sk=A3D.sk,o,n;\n"
  "    if(sk){\n"
  "      var msg=(SK_TOOLS[sk.tool]||sk.tool);\n"
  "      if(sk.pts&&sk.pts.length)msg+=' \\u00b7 click the next point, or type a length + Enter';\n"
  "      else msg+=' \\u00b7 click to start';\n"
  "      return msg;\n"
  "    }\n"
  "    n=(A3D.selSet&&A3D.selSet.length)||0;\n"
  "    if(n>1)return n+' objects selected';\n"
  "    if(A3D.sel){\n"
  "      o=objById(A3D.sel);\n"
  "      if(o)return o.name+'  \\u00b7  '+o.t;\n"
  "    }\n"
  "    return 'Ready';\n"
  "  }\n"
  "  function bimSyncStatusHint(){\n"
  "    if(!el.sthint)return;\n"
  "    el.sthint.textContent=bimStatusHintText();\n"
  "  }\n"
  "  function bimSyncStatusLevel(){\n"
  "    if(!el.stlevel)return;\n"
  "    var h='',i,lv;\n"
  "    for(i=0;i<A3D.levels.length;i++){\n"
  "      lv=A3D.levels[i];\n"
  "      h+='<option value=\"'+bimEsc(lv.id)+'\"'+(lv.id===A3D.activeLevel?' selected':'')+'>'+\n"
  "        bimEsc(lv.name)+'</option>';\n"
  "    }\n"
  "    if(el.stlevel.innerHTML!==h)el.stlevel.innerHTML=h;\n"
  "    el.stlevel.value=A3D.activeLevel;\n"
  "  }\n"
  "  function bimStatusCoordText(g){\n"
  "    if(!g)return '\\u2014';\n"
  "    /* World axes here are X / Z on the ground plane with Y up; the bar reports them as the\n"
  "       plan X / Y a drafter expects, and the third figure is the ACTIVE LEVEL's elevation,\n"
  "       which is the plane the point was actually solved on -- not the cursor's own height. */\n"
  "    return 'X '+g[0].toFixed(3)+'   Y '+g[2].toFixed(3)+'   Z '+(bimGetActiveLevel().elev).toFixed(3);\n"
  "  }\n"
  "  function bimStatusHover(ev){\n"
  "    if(!el.stcoords)return;\n"
  "    var xy=cvXY(ev);\n"
  "    var g=groundPoint(xy[0],xy[1],bimGetActiveLevel().elev);\n"
  "    el.stcoords.textContent=bimStatusCoordText(g);\n"
  "  }\n"
  "  function bimStatusHoverOut(){\n"
  "    if(el.stcoords)el.stcoords.textContent='\\u2014';\n"
  "  }\n"
  "  function bimSyncStatusBar(){\n"
  "    bimSyncStatusHint();\n"
  "    bimSyncStatusLevel();\n"
  "  }\n"
  "  function syncSnapPill(){")

# ---------------------------------------------------------------- 8. keep it in sync
P('sync.paint',
  "  function syncSnapPill(){\n"
  "    if(!el.snappill)return;",
  "  function syncSnapPill(){\n"
  "    bimSyncStatusHint();\n"
  "    if(!el.snappill)return;")

P('sync.levels',
  "  function refreshLevels(){\n"
  "    if(el.browser)refreshBrowser();",
  "  function refreshLevels(){\n"
  "    bimSyncStatusLevel();\n"
  "    if(el.browser)refreshBrowser();")

P('sync.tree',
  "  function refreshTree(){\n"
  "    if(!el.rows)return;",
  "  function refreshTree(){\n"
  "    bimSyncStatusHint();\n"
  "    if(!el.rows)return;")

# ---------------------------------------------------------------- 9. retire the canvas message
P('canvas.msg',
  "    ctx.save();\n"
  "    ctx.font='11px system-ui,sans-serif';\n"
  "    var st=SK_TOOLS[sk.tool]||sk.tool;\n"
  "    var msg=st+(A3D_SNAP.ortho?' \\u00b7 ORTHO (F8)':'')+(A3D_SNAP.point?' \\u00b7 SNAP (F3)':'')+"
  "(A3D_SNAP.grid?' \\u00b7 GRID (F9)':'')+(sk.pts.length?' \\u00b7 type a length + Enter':'');\n"
  "    var tw2=ctx.measureText(msg).width;\n"
  "    ctx.fillStyle='rgba(20,22,26,0.85)';\n"
  "    ctx.fillRect(10,10,tw2+16,20);\n"
  "    ctx.fillStyle='#9ec1ff';\n"
  "    ctx.fillText(msg,18,20);\n"
  "    ctx.restore();",
  "    /* __acad3dV67: the tool/modifier banner used to be painted into the canvas at (10,10),\n"
  "       over the drawing, restating what the snap pill beside it already showed. Both now live\n"
  "       in the status bar, which is where the 2D workspace has always put them -- so the same\n"
  "       information is in the same place in both modes and the drawing area is clear.\n"
  "       bimSyncStatusHint() is called from the paint path so the bar tracks the live tool. */\n"
  "    bimSyncStatusHint();")

# ---------------------------------------------------------------- apply
out = src
for name, old, new in patches:
    n = out.count(old)
    if n != 1:
        sys.exit('ANCHOR %s matched %d times (need exactly 1)' % (name, n))
    out = out.replace(old, new, 1)
    print('  applied %-20s (+%d chars)' % (name, len(new) - len(old)))

# post-conditions
assert 'a3d-snappill' not in out, 'stale #a3d-snappill reference survives'
assert out.count("id=\\\"a3d-statusbar\\\"") + out.count('id="a3d-statusbar"') >= 1
assert out.count('bimSyncStatusLevel') >= 3
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
