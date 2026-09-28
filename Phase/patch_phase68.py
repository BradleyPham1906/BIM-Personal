"""
Phase 68 -- Rayon's two-panel split: navigation LEFT, inspector RIGHT.

Anchored search-and-replace against the byte-count-verified canvas_v10.html. Every anchor is
asserted to occur EXACTLY ONCE before substitution; any miss aborts before a byte is written.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'dbd0880d6ccc3fc06e3ee9e5a5f783f7291a2d84743008aeb67e330223f6b93b'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new):
    patches.append((name, old, new))


# ------------------------------------------------------------------ 1. CSS: the right inspector
P('css.right',
  "    '.a3d-body{display:flex;flex:1 1 auto;min-height:0}'+",
  "    '.a3d-body{display:flex;flex:1 1 auto;min-height:0}'+\n"
  "    /* __acad3dV68: Rayon's actual split, which V65-V67 got wrong. Rayon keeps a thin icon rail\n"
  "       on the left that opens NAVIGATION panels (layers, pages, materials, tables, comments)\n"
  "       and pins the INSPECTOR to the right edge -- Selection, Modify, Annotations / Block\n"
  "       instance, Custom properties. V65 stacked Properties and Project Browser together in one\n"
  "       LEFT column, which is Figma's arrangement, not Rayon's: it put \"what exists\" and \"what\n"
  "       is selected\" in the same scroll, so the two fought for height (the whole of V66) and\n"
  "       the right half of the window carried nothing at all.\n"
  "       Splitting them by question -- left answers \"what is in this model\", right answers \"what\n"
  "       is this thing\" -- is what makes both fit without a cap, and it is the layout that was\n"
  "       asked for. */\n"
  "    '#a3d-right{width:280px;flex:0 0 auto;min-width:0;background:#202428;"
  "border-left:1px solid #30353c;display:flex;flex-direction:column;overflow:hidden}'+\n"
  "    '#a3d-right:empty{display:none}'+\n"
  "    '#a3d-propssec{display:flex;flex-direction:column;flex:1 1 auto;min-height:0}'+\n"
  "    '#a3d-right #a3d-propsbody{flex:1 1 auto;min-height:0;max-height:none;overflow:auto}'+\n"
  "    '.a3d-rdrawerbtn{display:none;font-size:11px;padding:4px 9px}'+")

P('css.tablet',
  "      '.a3d-tree{width:224px}'+",
  "      '.a3d-tree{width:224px}'+\n"
  "      '#a3d-right{width:236px}'+")

P('css.compact',
  "      '.a3d-tree.open{display:flex}'+",
  "      '.a3d-tree.open{display:flex}'+\n"
  "      /* The inspector gets the same drawer treatment the navigator already had, opened by its\n"
  "         own toolbar button. A 280px pane pinned open beside a 296px dock on a 700px screen\n"
  "         would leave 124px of drawing, which is not a layout, it is a joke. */\n"
  "      '#a3d-right{position:absolute;top:0;right:0;bottom:0;width:78vw;max-width:290px;"
  "z-index:9650;display:none;box-shadow:-4px 0 18px rgba(0,0,0,0.45)}'+\n"
  "      '#a3d-right.open{display:flex}'+\n"
  "      '.a3d-rdrawerbtn{display:inline-block}'+")

# ------------------------------------------------------------------ 2. markup
P('markup.propssec',
  "      '<div class=\"a3d-tree\">'+\n"
  "        '<div class=\"a3d-palhd\">Properties</div>'+\n"
  "        '<div id=\"a3d-propsbody\" class=\"a3d-propsbody\"></div>'+",
  "      '<div class=\"a3d-tree\">'+\n"
  "        /* __acad3dV68: Properties is wrapped so the header and body move to the right panel as\n"
  "           ONE node. They were siblings of the Project Browser's header, so moving them apart\n"
  "           would have meant two appendChild calls and two chances to leave the palette half\n"
  "           split if one of them threw. */\n"
  "        '<div id=\"a3d-propssec\">'+\n"
  "          '<div class=\"a3d-palhd\">Properties</div>'+\n"
  "          '<div id=\"a3d-propsbody\" class=\"a3d-propsbody\"></div>'+\n"
  "        '</div>'+")

P('markup.rightpane',
  "      '</div></div>'+\n"
  "    '</div>'+\n"
  "    '<div class=\"a3d-status\" id=\"a3d-statusbar\">'+",
  "      '</div></div>'+\n"
  "      '<div id=\"a3d-right\"></div>'+\n"
  "    '</div>'+\n"
  "    '<div class=\"a3d-status\" id=\"a3d-statusbar\">'+")

P('markup.rdrawerbtn',
  "      '<button class=\"a3d-btn a3d-drawerbtn\" data-a3d=\"drawer\" title=\"Show panel\">\\u2630</button>'+",
  "      '<button class=\"a3d-btn a3d-drawerbtn\" data-a3d=\"drawer\" title=\"Show panel\">\\u2630</button>'+\n"
  "      '<button class=\"a3d-btn a3d-rdrawerbtn\" data-a3d=\"rdrawer\" title=\"Show properties\">Props</button>'+")

P('handler.rdrawer',
  "      if(act==='drawer'){var tr=root.querySelector('.a3d-tree');if(tr)tr.classList.toggle('open');}",
  "      if(act==='drawer'){var tr=root.querySelector('.a3d-tree');if(tr)tr.classList.toggle('open');}\n"
  "      if(act==='rdrawer'){var rp=document.getElementById('a3d-right');"
  "if(rp)rp.classList.toggle('open');}")

# ------------------------------------------------------------------ 3. move it on entry
P('enter.movesprops',
  "    size();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();",
  "    /* __acad3dV68: Properties moves to the right inspector. Deliberately its OWN try block,\n"
  "       not folded into the dock-nesting one above: if the file dock is missing the navigator\n"
  "       falls back to the shell's own left pane, and the inspector should still be on the right\n"
  "       -- one failure should not drag the other layout back to the pre-V68 shape. */\n"
  "    try{\n"
  "      var propsSec=el.root&&el.root.querySelector('#a3d-propssec');\n"
  "      var rightPane=el.root&&el.root.querySelector('#a3d-right');\n"
  "      if(propsSec&&rightPane&&propsSec.parentNode!==rightPane){\n"
  "        A3D._propsHome=propsSec.parentNode;\n"
  "        rightPane.appendChild(propsSec);\n"
  "        document.body.classList.add('a3d-props-right');\n"
  "      }\n"
  "    }catch(eRight){console.warn('[BIM] Could not move Properties to the right inspector; "
  "it stays in the left column.',eRight);a3dToast('Properties panel could not be docked right');}\n"
  "    size();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();")

P('exit.restoresprops',
  "  function exit3d(){\n"
  "    if(!A3D.on)return;\n"
  "    A3D.on=false;\n"
  "    window.__a3dOn=false;\n"
  "    closeDlg();",
  "  function exit3d(){\n"
  "    if(!A3D.on)return;\n"
  "    A3D.on=false;\n"
  "    window.__a3dOn=false;\n"
  "    closeDlg();\n"
  "    /* __acad3dV68: put Properties back above the Project Browser before the tree itself is\n"
  "       un-docked below, so the palette is whole again wherever it ends up. Order matters: the\n"
  "       tree move that follows carries this section with it only if it is back inside by now. */\n"
  "    try{\n"
  "      var propsBack=document.getElementById('a3d-propssec');\n"
  "      if(propsBack&&A3D._propsHome&&propsBack.parentNode!==A3D._propsHome){\n"
  "        A3D._propsHome.insertBefore(propsBack,A3D._propsHome.firstChild);\n"
  "      }\n"
  "      document.body.classList.remove('a3d-props-right');\n"
  "      var rpClose=document.getElementById('a3d-right');\n"
  "      if(rpClose)rpClose.classList.remove('open');\n"
  "    }catch(eRightBack){console.warn('[BIM] Could not return Properties to the palette.',eRightBack);}")

# ------------------------------------------------------------------ 4. retire the V66 cap
P('css.v66cap',
  "body.a3d-tree-docked #figma-layers-panel > .a3d-tree > #a3d-propsbody{\n"
  "  flex:0 1 auto;max-height:46%;min-height:110px;overflow:auto;}\n",
  "/* __acad3dV66's 46% cap on the docked Properties pane is gone with V68: Properties is no\n"
  "   longer in this column, so there is nothing left here for it to crowd. The Project Browser\n"
  "   rule below stays -- it is what gives the navigator the full height it now has. */\n")

# ------------------------------------------------------------------ apply
out = src
for name, old, new in patches:
    n = out.count(old)
    if n != 1:
        sys.exit('ANCHOR %s matched %d times (need exactly 1)' % (name, n))
    out = out.replace(old, new, 1)
    print('  applied %-22s (%+d chars)' % (name, len(new) - len(old)))

assert out.count('a3d-propssec') >= 4, 'props section not wired everywhere'
# The BASE palette rule (.a3d-propsbody{max-height:46%}) stays -- it is what sizes Properties
# when the palette is whole, outside BIM. Only the DOCKED-column override is retired here.
assert 'body.a3d-tree-docked #figma-layers-panel > .a3d-tree > #a3d-propsbody' not in out, \
    'the V66 docked cap survives'
assert out.count("'.a3d-propsbody{flex:0 1 auto;max-height:46%") == 1, 'base palette rule lost'
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
