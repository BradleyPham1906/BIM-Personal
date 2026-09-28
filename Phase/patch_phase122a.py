"""patch_phase122a.py -- V122: a page is the same page at any size, and it shows nothing that is not on it.

The owner, in V119: "Need a presentation for doing presentation with clients. using layout spaces,
with multi pages view like a pdf viewer." A presentation draws every sheet at sizes the layout never
did: a thumbnail a few centimetres wide, a page fitted to the window, a page filling a projector.

1. A raster of a sheet had one resolution per pixel-per-millimetre. The title block's text, a
   viewport's label, a schedule's rows, a dimension's text in a viewport are all sized in pixels, for
   the layout's 3 px/mm; drawn at 6 px/mm -- the PNG export and the raster print -- every one of them
   came out at half its size on the paper. A page now has a layout resolution and a backing scale: it
   is laid out at the layout's 3 px/mm and drawn at that times the scale, the way the model view
   draws on a high-density screen (cvScale). The PNG export and the raster print are the layout at
   twice its pixels, the same image size they always were, with the proportions of the sheet on
   screen. The finest line a sheet draws is one pixel of the image, not one of the layout.

2. The model's selection was drawn on the sheets. A viewport's render cleared A3D.sel and A3D.sel2,
   and rooms, room tags, dimensions, text, notes, hatches, grids, terrain and property lines all
   draw selected from A3D.selSet or A3D.selGrid -- so a room selected in the model was blue on its
   sheet, in the PNG, in the raster print, and would have been in front of a client. A render clears
   all four, and draws no unfinished sketch: a tool left running showed its rubber band on paper.

3. A schedule on a sheet never drew. bimDrawScheduleViewport called a column's fmt as a function;
   fmt is the number of decimals, so every schedule with a number column -- all of them -- threw on
   its first row and came out a grey box on screen, in the PNG, and in the print's embedded image. A
   cell is formatted by bimFmtScheduleValue, the formatter the schedule table itself uses.

4. A3D_REV counts changes to the model: saveSoon, which every change passes through, moves it. The
   pages, their thumbnails and the slideshow draw a page again only when it has moved."""
NAME = 'patch_phase122a.py'
BASE = '3a76b3b596792badf104bbacaaa91a6af162bff326bac82ec2723c85b9338b88'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]

# ---- 3. the model's revision
rep("""  var saveT=null;
""", """  var saveT=null;
  /* __acad3dV122: the model's revision, moved by every change (saveSoon). What draws a page -- the
     pages, their thumbnails, the slideshow -- keeps the revision it drew at and draws again only when
     this has moved. */
  var A3D_REV=0;
""")
rep("""    bimRegenerateRegions();
    if(saveT)clearTimeout(saveT);
""", """    bimRegenerateRegions();
    A3D_REV++;   /* __acad3dV122 */
    if(saveT)clearTimeout(saveT);
""")

# ---- 1. a page: laid out at pxPerMM, drawn at pxPerMM x scale
rep("""  function bimRenderSheet(sheet,pxPerMM,paperOnly){
    /* __acad3dV121: paper alone is an export or a print, and so a plot; on screen a sheet shows
       what AutoCAD's layout shows -- a no-plot layer drawn, a locked one faded */
    if(paperOnly)return bimWithPlotPass(A3D.presentMode,function(){return bimRenderSheetPaper(sheet,pxPerMM,true);});
    return bimRenderSheetPaper(sheet,pxPerMM,false);
  }
  function bimRenderSheetPaper(sheet,pxPerMM,paperOnly){
    var pxW=Math.round(sheet.w*pxPerMM),pxH=Math.round(sheet.h*pxPerMM);
    var cv=el.sheetcv;
    if(!cv)return null;
    if(cv.width!==pxW)cv.width=pxW;
    if(cv.height!==pxH)cv.height=pxH;
    var ctx=cv.getContext('2d');
    ctx.fillStyle='#ffffff';ctx.fillRect(0,0,pxW,pxH);
""", """  function bimRenderSheet(sheet,pxPerMM,paperOnly,cv,scale){
    /* __acad3dV121: paper alone is an export or a print, and so a plot; on screen a sheet shows
       what AutoCAD's layout shows -- a no-plot layer drawn, a locked one faded */
    if(paperOnly)return bimWithPlotPass(A3D.presentMode,function(){return bimRenderSheetPaper(sheet,pxPerMM,true,cv,scale);});
    return bimRenderSheetPaper(sheet,pxPerMM,false,cv,scale);
  }
  /* __acad3dV122: `cv` is the canvas drawn on -- the sheet view's own when it is left out -- and
     `scale` its pixels to one of the layout's. The page is laid out at pxPerMM, as every size in it
     was made for (the title block's text, a viewport's label, a schedule's rows, the text in a
     viewport), and drawn at pxPerMM x scale, so it is the same page at any resolution: a thumbnail,
     a page fitted to the window, a projector. */
  function bimRenderSheetPaper(sheet,pxPerMM,paperOnly,cvIn,scale){
    var s=(isFinite(scale)&&scale>0)?scale:1;
    var pxW=Math.round(sheet.w*pxPerMM),pxH=Math.round(sheet.h*pxPerMM);
    var cv=cvIn||el.sheetcv;
    if(!cv)return null;
    var dW=Math.max(1,Math.round(sheet.w*pxPerMM*s)),dH=Math.max(1,Math.round(sheet.h*pxPerMM*s));
    if(cv.width!==dW)cv.width=dW;
    if(cv.height!==dH)cv.height=dH;
    var ctx=cv.getContext('2d');
    ctx.setTransform(s,0,0,s,0,0);
    ctx.fillStyle='#ffffff';ctx.fillRect(0,0,pxW,pxH);
""")
rep("""      try{bimCompositeViewport(ctx,sheet.viewports[i],0,0,pxPerMM);}
""", """      try{bimCompositeViewport(ctx,sheet.viewports[i],0,0,pxPerMM,s);}   /* __acad3dV122 */
""")
rep("""  function bimCompositeViewport(ctx,vp,pageOriginPxX,pageOriginPxY,pxPerMM){
""", """  function bimCompositeViewport(ctx,vp,pageOriginPxX,pageOriginPxY,pxPerMM,scale){
""")
rep("""          var img=bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom,vp.pan);
          ctx.drawImage(img,destX,destY,destW,destH);
""", """          var img=bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom,vp.pan,scale);   /* __acad3dV122 */
          ctx.drawImage(img,destX,destY,destW,destH);
""")

# ---- 1 and 2. the viewport's render: at the page's scale, and with nothing selected
rep("""  function bimRenderSourceToCanvas(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan){
    pxW=Math.max(1,Math.round(pxW));pxH=Math.max(1,Math.round(pxH));
    var cam=bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan);   /* __acad3dV116 */
    var scratch=bimGetScratchCanvas(pxW,pxH);
    var sctx=scratch.getContext('2d');
""", """  function bimRenderSourceToCanvas(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan,scale){
    pxW=Math.max(1,Math.round(pxW));pxH=Math.max(1,Math.round(pxH));
    var cam=bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan);   /* __acad3dV116 */
    /* __acad3dV122: drawn at the page's scale -- paint() lays out at cv.width / cvScale(cv), as it
       does on a high-density screen, so the view is the one the layout shows, at more pixels */
    var bs=(isFinite(scale)&&scale>0)?scale:1;
    var scratch=bimGetScratchCanvas(Math.max(1,Math.round(pxW*bs)),Math.max(1,Math.round(pxH*bs)));
    scratch.__a3dScale=bs;
    var sctx=scratch.getContext('2d');
""")
rep("""        savedActiveViewId=A3D.activeViewId,savedSection=A3D.section,savedSel=A3D.sel,savedSel2=A3D.sel2,
        savedView=A3D.view;
""", """        savedActiveViewId=A3D.activeViewId,savedSection=A3D.section,savedSel=A3D.sel,savedSel2=A3D.sel2,
        savedView=A3D.view,savedSelSet=A3D.selSet,savedSelGrid=A3D.selGrid;   /* __acad3dV122 */
""")
rep("""      A3D.activeViewId=null;A3D.sel=null;A3D.sel2=null;A3D.view=src.label||'';
""", """      A3D.activeViewId=null;A3D.sel=null;A3D.sel2=null;A3D.view=src.label||'';
      /* __acad3dV122: the whole selection. sel and sel2 were cleared and the rest drew: a room, its
         tag, a dimension, a text, a note, a hatch, terrain and a property line selected in the model
         read A3D.selSet, a grid A3D.selGrid, and came out blue on the sheet and its plots. */
      A3D.selSet=[];A3D.selGrid=null;
""")
rep("""      A3D.activeViewId=savedActiveViewId;A3D.section=savedSection;A3D.sel=savedSel;A3D.sel2=savedSel2;A3D.view=savedView;
    }
    return scratch;
""", """      A3D.activeViewId=savedActiveViewId;A3D.section=savedSection;A3D.sel=savedSel;A3D.sel2=savedSel2;A3D.view=savedView;
      A3D.selSet=savedSelSet;A3D.selGrid=savedSelGrid;   /* __acad3dV122 */
      /* the scratch is shared: the next user draws on it unscaled (bimBuildScheduleImageEmbed) */
      scratch.__a3dScale=1;sctx.setTransform(1,0,0,1,0,0);
    }
    return scratch;
""")

# ---- 2. no unfinished sketch on paper
rep("""    drawSkLivePreview(ctx,V,W,H);
    if(!capMode){
""", """    if(!capMode)drawSkLivePreview(ctx,V,W,H);   /* __acad3dV122: a tool's rubber band is not on the paper */
    if(!capMode){
""")

# ---- 1. the whole-sheet rasters: the layout at twice its pixels
rep("""      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,true);   /* __acad3dV116 */
""", """      /* __acad3dV122: the layout's page at twice its pixels -- the same image size as before, with the
         title block, the labels and the text in the viewports the size they are on the sheet */
      var cv=bimRenderSheet(sheet,SHEET_PREVIEW_PXMM,true,null,SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);
""", 2)

# ---- 1. the finest line is a pixel of the image
rep("""    if(pm)return Math.max(1,(d?BIM_LW_DEFAULT:+mm)*pm);
""", """    if(pm)return Math.max(1/cvScale(el.cv),(d?BIM_LW_DEFAULT:+mm)*pm);   /* __acad3dV122: a pixel of the image */
""")

# ---- 4. a schedule on a sheet: its cells formatted by the one schedule formatter
rep("""        var txt=col.fmt?col.fmt(val,rows[i]):String(val==null?'':val);
""", """        /* __acad3dV122: fmt is the number of decimals (V19), never a function -- calling it threw on
           the first number, and every schedule on a sheet was a grey box. The table's own formatter. */
        var txt=bimFmtScheduleValue(val,col.fmt);
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
