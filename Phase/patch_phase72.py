"""
Phase 72 -- the click offset and the blurry render. One root cause, two symptoms.

THE BUG. cvXY(ev) returns CSS pixels (ev.clientX - rect.left). groundPoint(), toScreen(), picking
and paint() all work in BACKING-STORE pixels (el.cv.width / el.cv.height). Those two are only the
same number when (a) the display is 1x and (b) size() has run since the last time the viewport box
changed. Neither holds in practice:

  - devicePixelRatio appears ZERO times in the whole file. On a 2x display the backing store is
    half the physical resolution, so the browser upscales it: blurry lines, blurry text, line
    weights and glyphs that read as "off scale".
  - size() is called from exactly TWO places: a window resize, and once in enter3d. Any layout
    change that resizes .a3d-vp WITHOUT a window resize leaves the backing store stale. Measured:
    collapsing the left dock takes the CSS box to 1266px while the backing store stays 1024px, so
    the canvas is stretched 1.236x and a click at x=400 lands at 400/1.236 = 323 in model space --
    77px from the cursor, growing with distance from the left edge.

THE FIX, in three parts:
  1. The backing store is sized in DEVICE pixels and the 2D context is scaled by the same factor,
     so every existing drawing call keeps working in CSS pixels and comes out crisp.
  2. All geometry reads go through cvW()/cvH(), which return the LOGICAL (CSS-pixel) size. The
     divisor is stored on the canvas element itself, so the scratch canvas used for sheet capture
     -- which replaces el.cv wholesale and is already 1:1 -- is untouched by any of this.
  3. A ResizeObserver on .a3d-vp calls size(). That fixes the whole CLASS of stale-backing bugs
     rather than the one instance found, which is the point: hunting every layout change that can
     resize the viewport is a losing game.

Anchored search-and-replace. Every anchor is asserted to match an EXACT expected count.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = '2061cd5707b6bb21e7251572c6d7e5d583d8b79031054aeee09e1cf8bce8fe48'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new, count=1):
    patches.append((name, old, new, count))


# ---------------------------------------------------------------- 1. logical size helpers
P('code.helpers',
  "  function size(){\n"
  "    var vp=el.root.querySelector('.a3d-vp');\n"
  "    el.cv.width=vp.clientWidth;\n"
  "    el.cv.height=vp.clientHeight;\n"
  "    bimSyncGlCanvasSize();\n"
  "    paint();\n"
  "  }",
  "  /* __acad3dV72: the canvas has TWO sizes and the code had been using one of them for both\n"
  "     jobs. el.cv.width/height is the BACKING STORE in device pixels; cvW()/cvH() are the\n"
  "     LOGICAL size in CSS pixels, which is the space cvXY() -- and therefore every mouse event --\n"
  "     lives in. Mixing them is what put the first click off the cursor.\n"
  "\n"
  "     The divisor is stored on the canvas ELEMENT rather than read from A3D, because sheet\n"
  "     capture swaps el.cv for a scratch canvas that is already 1:1 (see bimRenderViewportTo).\n"
  "     A scratch canvas carries no __a3dScale, so it divides by 1 and behaves exactly as it did\n"
  "     before this phase -- no capture path has to know that screen rendering is now scaled. */\n"
  "  function cvScale(c){return (c&&c.__a3dScale)||1;}\n"
  "  function cvW(){return el.cv?el.cv.width/cvScale(el.cv):0;}\n"
  "  function cvH(){return el.cv?el.cv.height/cvScale(el.cv):0;}\n"
  "  function bimDevicePixelRatio(){\n"
  "    var d=window.devicePixelRatio||1;\n"
  "    if(!isFinite(d)||d<=0)d=1;\n"
  "    /* Capped at 3. Past that the backing store grows as the square for no visible gain, and a\n"
  "     * 4x phone would be allocating ~50MB for one viewport. */\n"
  "    return Math.min(3,Math.max(1,d));\n"
  "  }\n"
  "  function size(){\n"
  "    var vp=el.root.querySelector('.a3d-vp');\n"
  "    if(!vp||!el.cv)return;\n"
  "    var dpr=bimDevicePixelRatio();\n"
  "    var wCss=vp.clientWidth,hCss=vp.clientHeight;\n"
  "    var wDev=Math.max(1,Math.round(wCss*dpr)),hDev=Math.max(1,Math.round(hCss*dpr));\n"
  "    /* Assigning width/height clears the canvas even when the value is unchanged, so both are\n"
  "       guarded -- a ResizeObserver that fires on every layout pass would otherwise blank the\n"
  "       drawing between frames. */\n"
  "    if(el.cv.width!==wDev)el.cv.width=wDev;\n"
  "    if(el.cv.height!==hDev)el.cv.height=hDev;\n"
  "    el.cv.__a3dScale=dpr;\n"
  "    bimSyncGlCanvasSize();\n"
  "    paint();\n"
  "  }\n"
  "  /* __acad3dV72: size() used to be called from exactly two places -- a window resize and once\n"
  "     on entering the workspace. Every other thing that resizes the viewport (collapsing the file\n"
  "     dock, opening the inspector, the status bar appearing, a discipline change reflowing the\n"
  "     shell) left the backing store stale and the cursor mapping wrong. Observing the element is\n"
  "     the fix for the CLASS of bug; chasing each layout change individually is not. */\n"
  "  var A3D_VP_OBS=null;\n"
  "  function bimObserveViewport(){\n"
  "    if(A3D_VP_OBS||typeof ResizeObserver==='undefined')return;\n"
  "    var vp=el.root&&el.root.querySelector('.a3d-vp');\n"
  "    if(!vp)return;\n"
  "    A3D_VP_OBS=new ResizeObserver(function(){if(A3D.on)size();});\n"
  "    A3D_VP_OBS.observe(vp);\n"
  "  }")

# ---------------------------------------------------------------- 2. geometry reads go logical
P('geom.repeated',
  "var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height;",
  "var V=camVecs(A3D.cam),W=cvW(),H=cvH();",
  count=6)

P('geom.sketchlabel',
  "toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,el.cv.width,el.cv.height)",
  "toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH())")

P('geom.ground',
  "var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height,f=H*1.2;",
  "var V=camVecs(A3D.cam),W=cvW(),H=cvH(),f=H*1.2;")

P('geom.project',
  "    var p=toScreen(pos,V,el.cv.width,el.cv.height);",
  "    var p=toScreen(pos,V,cvW(),cvH());")

P('geom.marquee',
  "    var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height,polys=[],i,j,k;",
  "    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),polys=[],i,j,k;")

# ---------------------------------------------------------------- 3. paint draws in CSS pixels
P('paint.transform',
  "  function paint(){\n"
  "    var cv=el.cv;if(!cv||!el.ctx)return;\n"
  "    var ctx=el.ctx,W=cv.width,H=cv.height,c=A3D.cam,V=camVecs(c),i,j,k;",
  "  function paint(){\n"
  "    var cv=el.cv;if(!cv||!el.ctx)return;\n"
  "    /* __acad3dV72: scale the context by the device pixel ratio and keep every drawing call\n"
  "       below in CSS pixels. Done here rather than once in size() because any ctx.setTransform\n"
  "       or ctx.restore elsewhere in a frame would silently drop it, and a lost transform is a\n"
  "       quarter-size drawing in the top-left corner -- loud, but only after it ships. The scratch\n"
  "       canvas used for sheet capture has no __a3dScale, so this is the identity there. */\n"
  "    var ctx=el.ctx,pxs=cvScale(cv);\n"
  "    ctx.setTransform(pxs,0,0,pxs,0,0);\n"
  "    var W=cv.width/pxs,H=cv.height/pxs,c=A3D.cam,V=camVecs(c),i,j,k;")

# ---------------------------------------------------------------- 4. GL keeps device pixels
P('gl.devicepx',
  "  function bimGlRender(V,W,H){\n"
  "    var G=bimGlInit();\n"
  "    if(!G)return false;\n"
  "    var gl=G.gl;\n"
  "    if(G.cv.width!==W||G.cv.height!==H){G.cv.width=W;G.cv.height=H;}\n"
  "    gl.viewport(0,0,W,H);",
  "  /* __acad3dV72: W and H arrive in CSS pixels, because the projection matrix has to agree with\n"
  "     toScreen() exactly or the GL layer and the 2D overlay drift apart. The GL canvas and its\n"
  "     viewport, though, are the backing store and must be in DEVICE pixels -- otherwise the whole\n"
  "     shaded layer renders at half resolution under a crisp overlay. */\n"
  "  function bimGlRender(V,W,H){\n"
  "    var G=bimGlInit();\n"
  "    if(!G)return false;\n"
  "    var gl=G.gl;\n"
  "    var gs=cvScale(el.cv);\n"
  "    var wDev=Math.max(1,Math.round(W*gs)),hDev=Math.max(1,Math.round(H*gs));\n"
  "    if(G.cv.width!==wDev||G.cv.height!==hDev){G.cv.width=wDev;G.cv.height=hDev;}\n"
  "    gl.viewport(0,0,wDev,hDev);")

# ---------------------------------------------------------------- 5. observe on entry
P('enter.observe',
  "    size();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();",
  "    size();\n"
  "    bimObserveViewport();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();")

# ---------------------------------------------------------------- apply
out = src
for name, old, new, count in patches:
    n = out.count(old)
    if n != count:
        sys.exit('ANCHOR %s matched %d times (need exactly %d)' % (name, n, count))
    out = out.replace(old, new)
    print('  applied %-20s x%d' % (name, count))

# The meaningful invariant is not a raw count -- it is that NO GEOMETRY site still reads the
# backing store. The legitimate device-pixel readers left are cvW/cvH themselves, size(),
# bimSyncGlCanvasSize (the GL backing store) and bimGetCanvasRGB (pixel export).
assert 'camVecs(A3D.cam),W=el.cv.width' not in out, 'a geometry site still reads device pixels'
assert 'toScreen(pos,V,el.cv.width' not in out, 'the project hook still reads device pixels'
assert 'cvW()' in out and '__a3dScale' in out
print('remaining el.cv.width refs: %d (cvW, size x2, glsync x2, export)'
      % out.count('el.cv.width'))
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('wrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
