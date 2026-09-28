"""
Phase 69 -- One material library, shared by the 2D board and the BIM model.

The first MODEL-level bridge between two of the three data models in this file. Everything before
it (V64-V68) unified the shell; this makes the BIM solids read the same material cards the 2D
whiteboard already assigns to its wire shapes.

Anchored search-and-replace. Every anchor is asserted to occur EXACTLY ONCE before substitution.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'e53c044bb5101074b0463939f1599e6e384a5dc0fed0e53dd1bc5fc692673c4e'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new):
    patches.append((name, old, new))


# ------------------------------------------------------------------ 1. publish the library
P('cards.bridge',
  "];\nvar matDlg=null,matSel=null;",
  "];\n"
  "/* __acad3dV69: the 2D board's material cards, published for the BIM module. This is the FIRST\n"
  "   model-level connection between the two engines in this file -- everything before it unified\n"
  "   the shell only. Deliberately the SAME ARRAY, not a copy: two lists that start identical and\n"
  "   drift are worse than one list, and 'one connected model' (Product Principle 3) means the\n"
  "   BIM inspector and the board's Material Cards dialog cannot disagree about what Concrete is.\n"
  "   Published on window because the two engines live in separate <script> blocks with no shared\n"
  "   scope; the BIM side reads it through bimMaterialCards() and treats an absent library as\n"
  "   'no materials available' rather than failing. */\n"
  "window.__WB_MATERIAL_CARDS=CARDS;\n"
  "var matDlg=null,matSel=null;")

# ------------------------------------------------------------------ 2. BIM-side material model
P('bim.helpers',
  "  function bimResolveGraphics(o,mode){",
  "  /* __acad3dV69: BIM's view of the shared material library. Cards carry real engineering data\n"
  "     (density kg/m3, Young's modulus, Poisson ratio) plus a hatch definition, so assigning one\n"
  "     to a solid gives BOTH a plan cut pattern and a quantity takeoff from the same act. */\n"
  "  function bimMaterialCards(){\n"
  "    var c=window.__WB_MATERIAL_CARDS;\n"
  "    return (c&&c.length)?c:[];\n"
  "  }\n"
  "  function bimMaterialByName(n){\n"
  "    var cards=bimMaterialCards(),i;\n"
  "    for(i=0;i<cards.length;i++)if(cards[i].name===n)return cards[i];\n"
  "    return null;\n"
  "  }\n"
  "  function bimMaterialOf(o){\n"
  "    return (o&&o.materialName)?bimMaterialByName(o.materialName):null;\n"
  "  }\n"
  "  /* A card's hatch is {angle, gap, cross} in the board's own terms; this app's pattern engine\n"
  "     takes a NAMED pattern from BIM_HATCH_PATTERNS. Mapping rather than adding a second hatch\n"
  "     renderer keeps one pattern pipeline -- the one Phase 53 already tested against canvas,\n"
  "     SVG and the sheet exporter. Angles are folded into [0,180) first so 225 reads as 45. */\n"
  "  function bimMaterialPattern(card){\n"
  "    if(!card||!card.hatch)return null;\n"
  "    var h=card.hatch,a=((h.angle||0)%180+180)%180,name;\n"
  "    if(h.cross)name='cross';\n"
  "    else if(a<=15||a>=165)name='horizontal';\n"
  "    else if(a>=75&&a<=105)name='vertical';\n"
  "    else if(a<90)name='diagonal';\n"
  "    else name='diagonal-reverse';\n"
  "    return {pattern:name,patternColor:card.color||'#555555',\n"
  "      patternScale:Math.max(0.1,Math.min(8,(h.gap||8)/8))};\n"
  "  }\n"
  "  /* Volume is reported ONLY for a mesh that bounds a closed volume. The divergence-theorem\n"
  "     figure is exact for a closed surface and MEANINGLESS for an open one, and a plausible\n"
  "     wrong mass on a quantity takeoff is worse than no mass at all (Product Principle 2), so an\n"
  "     unclosed or corrupt mesh returns null and the UI shows an em dash. */\n"
  "  function bimObjVolume(o){\n"
  "    if(!o||!o.mesh||!o.mesh.v||!o.mesh.f||!o.mesh.f.length)return null;\n"
  "    var c=bimMeshClosureCheck(o.mesh);\n"
  "    if(!c||!c.closed||c.corrupt)return null;\n"
  "    return Math.abs(c.vol);\n"
  "  }\n"
  "  function bimObjMass(o){\n"
  "    var card=bimMaterialOf(o),vol=bimObjVolume(o);\n"
  "    if(!card||vol===null||!card.density)return null;\n"
  "    return card.density*vol;\n"
  "  }\n"
  "  function bimSetMaterial(o,name){\n"
  "    if(!o)return false;\n"
  "    if(!name){delete o.materialName;return true;}\n"
  "    if(!bimMaterialByName(name))return false;\n"
  "    o.materialName=name;\n"
  "    return true;\n"
  "  }\n"
  "  var BIM_MAT_COLS=[{key:'material',label:'Material'},\n"
  "    {key:'volume',label:'Volume (m\\u00b3)',fmt:3},{key:'mass',label:'Mass (kg)',fmt:1}];\n"
  "  function bimMatRow(o){\n"
  "    return {material:o.materialName||null,volume:bimObjVolume(o),mass:bimObjMass(o)};\n"
  "  }\n"
  "  function bimMergeRow(base,extra){\n"
  "    var k;for(k in extra)if(extra.hasOwnProperty(k))base[k]=extra[k];\n"
  "    return base;\n"
  "  }\n"
  "  function bimResolveGraphics(o,mode){")

# ------------------------------------------------------------------ 3. material feeds the hatch
P('bim.graphics',
  "    mode=(mode==='presentation')?'presentation':'technical';\n"
  "    var out=bimDefaultGraphics();\n"
  "    var cat=o&&o.bim&&(o.bim.typeCat||o.bim.type);",
  "    mode=(mode==='presentation')?'presentation':'technical';\n"
  "    var out=bimDefaultGraphics();\n"
  "    /* __acad3dV69: an assigned material supplies the cut pattern, exactly as it does in Revit.\n"
  "       It sits BELOW the type default and the instance override in the chain, so it is a\n"
  "       starting point a user can always overrule, never a value that fights an explicit choice.\n"
  "       Nothing changes for an object with no material: bimMaterialOf returns null and this is a\n"
  "       no-op, which is why assigning a material is the only thing that can alter an existing\n"
  "       drawing's appearance. */\n"
  "    var matCard=bimMaterialOf(o),matPat=matCard?bimMaterialPattern(matCard):null;\n"
  "    if(matPat){out.pattern=matPat.pattern;out.patternColor=matPat.patternColor;\n"
  "      out.patternScale=matPat.patternScale;}\n"
  "    var cat=o&&o.bim&&(o.bim.typeCat||o.bim.type);")

# ------------------------------------------------------------------ 4. Properties group
P('props.group',
  "      h+=bimPropGroup('Graphics \u2014 '+gLabel,grows);\n"
  "    }\n",
  "      h+=bimPropGroup('Graphics \u2014 '+gLabel,grows);\n"
  "    }\n"
  "\n"
  "    /* ---- __acad3dV69: Materials and Finishes (Revit's own group name for this). One select\n"
  "       assigns a card; everything under it is DERIVED and read-only, because those figures come\n"
  "       from the shared library and the model's own geometry -- editing them here would be\n"
  "       editing a copy. Volume and Mass show an em dash when the solid's mesh does not bound a\n"
  "       closed volume rather than a number that would be wrong. ---- */\n"
  "    var matRows='',matCards=bimMaterialCards(),mci,curMat=bimMaterialOf(o);\n"
  "    if(matCards.length&&o.t==='solid'){\n"
  "      var matOpts='<option value=\"\"'+(o.materialName?'':' selected')+'>\\u2014 none \\u2014</option>';\n"
  "      for(mci=0;mci<matCards.length;mci++){\n"
  "        matOpts+='<option value=\"'+bimEsc(matCards[mci].name)+'\"'+\n"
  "          (o.materialName===matCards[mci].name?' selected':'')+'>'+\n"
  "          bimEsc(matCards[mci].name)+' \\u00b7 '+bimEsc(matCards[mci].kind)+'</option>';\n"
  "      }\n"
  "      matRows+=bimPropRow('Material','<select data-propmat=\"1\">'+matOpts+'</select>');\n"
  "      if(curMat){\n"
  "        matRows+=bimPropText('Density (kg/m\\u00b3)',curMat.density);\n"
  "        matRows+=bimPropText('Young\\u2019s Modulus',curMat.youngsModulus);\n"
  "        matRows+=bimPropText('Poisson\\u2019s Ratio',curMat.poissonRatio);\n"
  "      }\n"
  "      var mVol=bimObjVolume(o),mMass=bimObjMass(o);\n"
  "      matRows+=bimPropText('Volume (m\\u00b3)',mVol===null?'\\u2014':mVol.toFixed(4));\n"
  "      matRows+=bimPropText('Mass (kg)',mMass===null?'\\u2014':mMass.toFixed(2));\n"
  "      h+=bimPropGroup('Materials and Finishes',matRows);\n"
  "    }\n")

# ------------------------------------------------------------------ 5. the select writes back
P('props.change',
  "      var go=objById(A3D.sel);\n"
  "      if(!go)return;\n"
  "      var fillOn=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxfillon]'):null;",
  "      var go=objById(A3D.sel);\n"
  "      if(!go)return;\n"
  "      /* __acad3dV69: material assignment. refreshProps AND paint: the material supplies the\n"
  "         plan cut pattern, so the drawing changes with the palette and a repaint is not\n"
  "         optional here the way it is for a purely informational field. */\n"
  "      var mSel=ev.target&&ev.target.closest?ev.target.closest('[data-propmat]'):null;\n"
  "      if(mSel){\n"
  "        pushUndo();\n"
  "        if(!bimSetMaterial(go,mSel.value)){\n"
  "          a3dToast('That material is not in the library');refreshProps();return;\n"
  "        }\n"
  "        a3dToast(mSel.value?('Material set to '+mSel.value):'Material cleared');\n"
  "        refreshProps();paint();saveSoon();\n"
  "        return;\n"
  "      }\n"
  "      var fillOn=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxfillon]'):null;")

# ------------------------------------------------------------------ 6. schedules
P('sched.wall.close',
  "        level:bimLevelName(o.bim.levelId),\n"
  "        imported:!!o.bim.imported\n"
  "      };",
  "        level:bimLevelName(o.bim.levelId),\n"
  "        imported:!!o.bim.imported\n"
  "      });")

P('sched.wall.open',
  "      var hasCenterline=!!(o.bim.centerline);\n"
  "      var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed):null;\n"
  "      return {\n",
  "      var hasCenterline=!!(o.bim.centerline);\n"
  "      var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed):null;\n"
  "      return bimMergeRow(bimMatRow(o),{\n")

P('sched.ceiling',
  "      return {name:o.name,area:o.bim.profile?bimPolyArea(o.bim.profile):null,"
  "height:o.bim.heightAbove,thickness:o.bim.thickness,level:bimLevelName(o.bim.levelId)};",
  "      return bimMergeRow(bimMatRow(o),{name:o.name,"
  "area:o.bim.profile?bimPolyArea(o.bim.profile):null,"
  "height:o.bim.heightAbove,thickness:o.bim.thickness,level:bimLevelName(o.bim.levelId)});")

P('sched.beam',
  "      return {name:o.name,span:o.bim.length,width:o.bim.width,depth:o.bim.depth,\n"
  "        level:bimLevelName(o.bim.levelId),topY:o.bim.topY};",
  "      return bimMergeRow(bimMatRow(o),{name:o.name,span:o.bim.length,width:o.bim.width,"
  "depth:o.bim.depth,\n"
  "        level:bimLevelName(o.bim.levelId),topY:o.bim.topY});")

P('sched.column',
  "      return {name:o.name,width:o.bim.width,depth:o.bim.depth,height:o.bim.height,"
  "level:bimLevelName(o.bim.levelId)};",
  "      return bimMergeRow(bimMatRow(o),{name:o.name,width:o.bim.width,depth:o.bim.depth,"
  "height:o.bim.height,level:bimLevelName(o.bim.levelId)});")

P('sched.cols.wall',
  "{key:'height',label:'Height (m)',fmt:2},{key:'area',label:'Area (m\\u00b2)',fmt:2}]},\n"
  "    ceiling:",
  "{key:'height',label:'Height (m)',fmt:2},{key:'area',label:'Area (m\\u00b2)',fmt:2}]"
  ".concat(BIM_MAT_COLS)},\n"
  "    ceiling:")

P('sched.cols.ceiling',
  "{key:'height',label:'Height (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:3}]},\n"
  "    column:",
  "{key:'height',label:'Height (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:3}]"
  ".concat(BIM_MAT_COLS)},\n"
  "    column:")

P('sched.cols.column',
  "{key:'depth',label:'Depth (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}]},\n"
  "    beam:",
  "{key:'depth',label:'Depth (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}]"
  ".concat(BIM_MAT_COLS)},\n"
  "    beam:")

P('sched.cols.beam',
  "{key:'depth',label:'Depth (m)',fmt:2},{key:'topY',label:'Top elev (m)',fmt:3}]}\n"
  "  };",
  "{key:'depth',label:'Depth (m)',fmt:2},{key:'topY',label:'Top elev (m)',fmt:3}]"
  ".concat(BIM_MAT_COLS)}\n"
  "  };")

# ------------------------------------------------------------------ apply
out = src
for name, old, new in patches:
    n = out.count(old)
    if n != 1:
        sys.exit('ANCHOR %s matched %d times (need exactly 1)' % (name, n))
    out = out.replace(old, new, 1)
    print('  applied %-22s (%+d chars)' % (name, len(new) - len(old)))

# the wall-schedule edit is two anchors that must both have landed
assert 'bimMergeRow(bimMatRow(o),{' in out
assert out.count('.concat(BIM_MAT_COLS)') == 4, 'not every solid schedule got the columns'
assert out.count('window.__WB_MATERIAL_CARDS') == 2, 'expect the publish and the BIM read'
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
