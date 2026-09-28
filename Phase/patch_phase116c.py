"""patch_phase116c.py -- V116 Model and layout tabs, part 3: model space through a viewport, AutoCAD's
MSPACE and Revit's Activate View. Double-click a viewport to work in it: a drag pans the model inside
it and the wheel steps through standard scales about the cursor; double-click outside it or Escape
returns to paper space. The pan is part of the viewport, so preview, PNG, SVG and print all solve the
same camera. While a sheet is on screen, keys, commands and tools that act on the model are held back
from the model hidden behind the paper."""
NAME = 'patch_phase116c.py'
BASE = '2aa92cded3e49ae8134b5caa1040281f129742fc404a0c03c1c8b6c2b4d8099b'
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
# ---- 1. state and scales ------------------------------------------------------------------------------------
rep("    sheets:[], activeSheetId:null, sheetSelVp:null, sheetDrag:null,\n",
    "    sheets:[], activeSheetId:null, sheetSelVp:null, sheetDrag:null,\n"
    "    sheetActiveVp:null,   /* __acad3dV116: the viewport being worked in (model space), or null for paper space */\n")
rep("  var SHEET_SCALES=[\n    {label:'1:20',denom:20},{label:'1:50',denom:50},{label:'1:100',denom:100},\n    {label:'1:200',denom:200},{label:'1:500',denom:500}\n  ];\n",
    r'''  /* __acad3dV116: the standard metric scales, detail to site. The five that were here stopped at
     1:500, too coarse for the civil work this app is for, and they are also the steps the wheel
     takes in a viewport, so a viewport's scale is always one a drawing set can carry. */
  var SHEET_SCALES=[
    {label:'1:1',denom:1},{label:'1:2',denom:2},{label:'1:5',denom:5},{label:'1:10',denom:10},
    {label:'1:20',denom:20},{label:'1:25',denom:25},{label:'1:50',denom:50},{label:'1:100',denom:100},
    {label:'1:200',denom:200},{label:'1:250',denom:250},{label:'1:500',denom:500},{label:'1:1000',denom:1000},
    {label:'1:1250',denom:1250},{label:'1:2000',denom:2000},{label:'1:2500',denom:2500},{label:'1:5000',denom:5000}
  ];
''')

# ---- 2. the pan is part of the camera every output solves ------------------------------------------------------
rep("  function bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom){\n    var base=src.cam;\n    if(scaleMode==='ratio'){\n      var mmPerModelUnit=1000/Math.max(1,scaleDenom||100);\n      var pxPerModelUnit=mmPerModelUnit*pxPerMM;\n      var dist=1.2*pxH/Math.max(pxPerModelUnit,1e-6);\n      return {yaw:base.yaw,pitch:base.pitch,dist:dist,tx:base.tx,ty:base.ty,tz:base.tz};\n    }\n",
    r'''  /* __acad3dV116: pan is where the viewport looks, in metres along the view's right and up from the
     source's own target -- the same frame 'fit' recentres in below. Only a fixed-scale viewport has
     one; a fitted viewport recentres on the model every time it is drawn. */
  function bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan){
    var base=src.cam;
    if(scaleMode==='ratio'){
      var mmPerModelUnit=1000/Math.max(1,scaleDenom||100);
      var pxPerModelUnit=mmPerModelUnit*pxPerMM;
      var dist=1.2*pxH/Math.max(pxPerModelUnit,1e-6);
      var tx=base.tx,ty=base.ty,tz=base.tz;
      if(pan&&isFinite(pan[0])&&isFinite(pan[1])&&(pan[0]||pan[1])){
        var Vp=camVecs({yaw:base.yaw,pitch:base.pitch,dist:1,tx:base.tx,ty:base.ty,tz:base.tz});
        tx+=Vp.r[0]*pan[0]+Vp.u[0]*pan[1];ty+=Vp.r[1]*pan[0]+Vp.u[1]*pan[1];tz+=Vp.r[2]*pan[0]+Vp.u[2]*pan[1];
      }
      return {yaw:base.yaw,pitch:base.pitch,dist:dist,tx:tx,ty:ty,tz:tz};
    }
''')
rep("  function bimRenderSourceToCanvas(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom){\n    pxW=Math.max(1,Math.round(pxW));pxH=Math.max(1,Math.round(pxH));\n    var cam=bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom);\n",
    "  function bimRenderSourceToCanvas(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan){\n    pxW=Math.max(1,Math.round(pxW));pxH=Math.max(1,Math.round(pxH));\n    var cam=bimSheetSolveCamera(src,pxW,pxH,pxPerMM,scaleMode,scaleDenom,pan);   /* __acad3dV116 */\n")
rep("bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom)",
    "bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom,vp.pan)", 2)
rep("    var cam=bimSheetSolveCamera(src,wMM,hMM,1,vp.scaleMode,vp.scaleDenom);\n",
    "    var cam=bimSheetSolveCamera(src,wMM,hMM,1,vp.scaleMode,vp.scaleDenom,vp.pan);   /* __acad3dV116 */\n")
if t.count('bimSheetSolveCamera(') != 3 or t.count('vp.pan)') != 3:
    sys.exit('ABORT: a caller of the viewport camera does not carry the pan')

# ---- 3. the paper and the working decorations are separate -------------------------------------------------------
rep("  function bimRenderSheet(sheet,pxPerMM){\n",
    "  /* __acad3dV116: paperOnly draws the sheet as it prints -- no selection outline, no model-space\n"
    "     highlight. The exports asked for that by clearing and restoring the selection around the call;\n"
    "     a flag cannot be left set by a render that throws. */\n"
    "  function bimRenderSheet(sheet,pxPerMM,paperOnly){\n")
rep("    if(A3D.sheetSelVp){\n      var sv=null;for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===A3D.sheetSelVp){sv=sheet.viewports[i];break;}\n",
    r'''    if(!paperOnly&&A3D.sheetActiveVp){   /* __acad3dV116: model space -- the rest of the sheet recedes */
      var av=bimSheetVp(sheet,A3D.sheetActiveVp);
      if(av){
        var ax=av.x*pxPerMM,ay=av.y*pxPerMM,aw=av.w*pxPerMM,ah=av.h*pxPerMM;
        ctx.save();
        ctx.fillStyle='rgba(22,26,32,0.34)';
        ctx.fillRect(0,0,pxW,ay);ctx.fillRect(0,ay+ah,pxW,pxH-ay-ah);
        ctx.fillRect(0,ay,ax,ah);ctx.fillRect(ax+aw,ay,pxW-ax-aw,ah);
        ctx.strokeStyle='#2f7fe0';ctx.lineWidth=3;ctx.strokeRect(ax+1.5,ay+1.5,aw-3,ah-3);
        ctx.restore();
      }
    }
    if(!paperOnly&&A3D.sheetSelVp){
      var sv=null;for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===A3D.sheetSelVp){sv=sheet.viewports[i];break;}
''')
rep("      var wasSel=A3D.sheetSelVp;A3D.sheetSelVp=null;\n      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM);\n      A3D.sheetSelVp=wasSel;\n",
    "      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,true);   /* __acad3dV116 */\n")
rep("      var wasSel=A3D.sheetSelVp;A3D.sheetSelVp=null;\n      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM);\n      var dataURL=cv.toDataURL('image/png');\n      A3D.sheetSelVp=wasSel;bimSheetViewRefresh();\n",
    "      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,true);   /* __acad3dV116 */\n      var dataURL=cv.toDataURL('image/png');\n      bimSheetViewRefresh();\n")
if 'wasSel' in t:
    sys.exit('ABORT: an export still toggles the selection around the render')

# ---- 4. model space and paper space ---------------------------------------------------------------------------------
rep("  function bimSheetPointerDown(ev){\n    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;\n    var mm=bimSheetEvtToMM(ev,el.sheetcv);\n",
    r'''  /* ================= __acad3dV116: model space through a viewport =================
     AutoCAD's MSPACE and Revit's Activate View. Double-click a viewport and it becomes a window onto
     the model: a drag pans it, the wheel steps through the standard scales about the cursor, and the
     rest of the sheet recedes. Double-click outside it, Escape or PAPER returns to paper space. The
     viewport keeps its pan and scale, so every output shows what was set here. */
  function bimSheetVp(sheet,id){
    var i;
    if(!sheet||!id)return null;
    for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===id)return sheet.viewports[i];
    return null;
  }
  function bimSheetInVp(vp,mm){return mm[0]>=vp.x&&mm[0]<=vp.x+vp.w&&mm[1]>=vp.y&&mm[1]<=vp.y+vp.h;}
  function bimNextScale(d,dir){
    var i;
    if(dir<0){for(i=SHEET_SCALES.length-1;i>=0;i--)if(SHEET_SCALES[i].denom<d-1e-9)return SHEET_SCALES[i].denom;return d;}
    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>d+1e-9)return SHEET_SCALES[i].denom;
    return d;
  }
  /* A fitted viewport has no fixed scale or centre to pan from. The first pan or zoom gives it both:
     the smallest standard scale that still shows everything the fit showed, centred where the fit
     was -- read back from the fit's own camera, so this cannot drift from how 'fit' frames. */
  function bimSheetVpToRatio(vp){
    if(vp.scaleMode==='ratio'){
      if(!vp.pan||!isFinite(vp.pan[0])||!isFinite(vp.pan[1]))vp.pan=[0,0];
      return true;
    }
    var src=bimResolveViewportSource(vp);
    if(src.error||!src.cam)return false;
    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);
    var mmPerM=1.2*vp.h/Math.max(cam.dist,1e-9),want=1000/Math.max(mmPerM,1e-9),d=SHEET_SCALES[SHEET_SCALES.length-1].denom,i;
    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>=want-1e-6){d=SHEET_SCALES[i].denom;break;}
    var V=camVecs({yaw:src.cam.yaw,pitch:src.cam.pitch,dist:1,tx:src.cam.tx,ty:src.cam.ty,tz:src.cam.tz});
    var dx=cam.tx-src.cam.tx,dy=cam.ty-src.cam.ty,dz=cam.tz-src.cam.tz;
    vp.pan=[dx*V.r[0]+dy*V.r[1]+dz*V.r[2],dx*V.u[0]+dy*V.u[1]+dz*V.u[2]];
    vp.scaleMode='ratio';vp.scaleDenom=d;
    return true;
  }
  function bimSetModelSpace(id){
    if(!bimSheetOnScreen()){a3dToast('MSPACE works on a sheet: open one from the layout tabs');return false;}
    var sheet=bimSheetById(A3D.activeSheetId),vp=null,i;
    if(!sheet)return false;
    vp=bimSheetVp(sheet,id)||bimSheetVp(sheet,A3D.sheetSelVp);
    if(!vp)for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].kind!=='schedule'){vp=sheet.viewports[i];break;}
    if(!vp){a3dToast('This sheet has no viewport onto the model: add one with + Viewport');return false;}
    if(vp.kind==='schedule'){a3dToast('A schedule has no model to work in');return false;}
    var src=bimResolveViewportSource(vp);
    if(src.error){a3dToast('That viewport cannot be worked in: '+src.error);return false;}
    A3D.sheetActiveVp=vp.id;A3D.sheetSelVp=null;A3D.sheetDrag=null;
    bimSheetViewRefresh();bimSyncStatusHint();
    return true;
  }
  function bimSetPaperSpace(){
    if(!A3D.sheetActiveVp)return false;
    A3D.sheetActiveVp=null;A3D.sheetDrag=null;
    bimSheetViewRefresh();bimSyncStatusHint();
    return true;
  }
  function bimDeleteSheetViewport(id){
    var sheet=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sheet,id);
    if(!vp)return false;
    pushUndo();
    sheet.viewports.splice(sheet.viewports.indexOf(vp),1);
    if(A3D.sheetSelVp===id)A3D.sheetSelVp=null;
    if(A3D.sheetActiveVp===id)A3D.sheetActiveVp=null;
    bimSheetViewRefresh();bimSyncStatusHint();saveSoon();
    a3dToast('Viewport deleted');
    return true;
  }
  var A3D_VP_WHEEL_T=0;
  function bimSheetWheel(ev){
    if(!A3D.sheetActiveVp||!el.sheetcv)return;
    var sheet=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sheet,A3D.sheetActiveVp);
    if(!vp)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    if(!bimSheetInVp(vp,mm)||!ev.deltaY)return;
    ev.preventDefault();
    var dir=ev.deltaY<0?-1:1;
    if(vp.scaleMode==='ratio'&&bimNextScale(vp.scaleDenom,dir)===vp.scaleDenom)return;
    var now=Date.now();
    if(now-A3D_VP_WHEEL_T>600)pushUndo();   /* one undo step for a run of wheel notches */
    A3D_VP_WHEEL_T=now;
    if(!bimSheetVpToRatio(vp))return;
    var d1=vp.scaleDenom,d2=bimNextScale(d1,dir);
    if(d2!==d1){
      /* the model point under the cursor stays under the cursor */
      var ox=mm[0]-(vp.x+vp.w/2),oy=mm[1]-(vp.y+vp.h/2);
      vp.pan=[vp.pan[0]+ox*(d1-d2)/1000,vp.pan[1]-oy*(d1-d2)/1000];
      vp.scaleDenom=d2;
    }
    bimSheetViewRefresh();saveSoon();
  }
  function bimSheetContextMenu(ev){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet||!el.sheetcv)return;
    ev.preventDefault();
    var mm=bimSheetEvtToMM(ev,el.sheetcv),hit=bimSheetHitTest(sheet,mm),items=[];
    if(hit){
      if(!A3D.sheetActiveVp){A3D.sheetSelVp=hit.vp.id;bimSheetViewRefresh();}
      if(hit.vp.kind!=='schedule')items.push(A3D.sheetActiveVp===hit.vp.id?['Paper space','pspace']:['Work in this viewport','mspace']);
      items.push(['Viewport properties…','props']);
      items.push(['Delete viewport','del',true]);
    }else if(A3D.sheetActiveVp){
      items.push(['Paper space','pspace']);
    }else{
      items.push(['Add viewport…','add']);
      items.push(['Sheet setup…','setup']);
    }
    bimLtMenuOpen(ev.clientX,ev.clientY,items,function(a){
      if(a==='mspace')bimSetModelSpace(hit.vp.id);
      else if(a==='pspace')bimSetPaperSpace();
      else if(a==='props')bimOpenViewportPropsDlg(hit.vp.id);
      else if(a==='del')bimDeleteSheetViewport(hit.vp.id);
      else if(a==='add')bimOpenAddViewportDlg();
      else if(a==='setup')bimOpenSheetPropsDlg();
    });
  }
  /* On a sheet the paper is what is on screen. A key that would start a tool or edit a model object
     would act on something the user cannot see, so only these reach past the paper: Escape (out of
     the viewport, then the selection), Delete (the selected viewport), the Ctrl shortcuts (undo,
     redo, save, open) and the function keys. */
  function bimSheetKey(ev){
    var tg=ev.target;
    if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.tagName==='SELECT'||tg.isContentEditable))return false;
    if(el.dlg||ev.ctrlKey||ev.metaKey||/^F\d+$/.test(ev.key))return false;
    if(ev.key==='Escape'){
      if(A3D.sheetActiveVp)bimSetPaperSpace();
      else if(A3D.sheetSelVp){A3D.sheetSelVp=null;bimSheetViewRefresh();}
    }else if((ev.key==='Delete'||ev.key==='Backspace')&&!A3D.sheetActiveVp&&A3D.sheetSelVp){
      bimDeleteSheetViewport(A3D.sheetSelVp);
    }
    ev.preventDefault();ev.stopImmediatePropagation();
    return true;
  }
  function bimSheetPointerDown(ev){
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    if(A3D.sheetActiveVp){   /* __acad3dV116: a drag inside the viewport pans; nothing on the paper can be picked */
      var avp=bimSheetVp(sheet,A3D.sheetActiveVp);
      if(avp&&bimSheetInVp(avp,mm)&&!ev.button){
        ev.preventDefault();
        A3D.sheetDrag={mode:'pan',vpId:avp.id,startMM:mm,orig:null};
      }
      return;
    }
    if(ev.button)return;   /* __acad3dV116: a right-click opens the menu; it does not start a move */
''')
rep("    var o=A3D.sheetDrag.orig;\n    if(A3D.sheetDrag.mode==='move'){\n",
    r'''    if(A3D.sheetDrag.mode==='pan'){   /* __acad3dV116 */
      var pd=A3D.sheetDrag;
      if(!pd.orig){
        if(Math.abs(dx)<0.3&&Math.abs(dy)<0.3)return;   /* a click is not a pan */
        pushUndo();
        if(!bimSheetVpToRatio(vp)){A3D.sheetDrag=null;return;}
        pd.orig=[vp.pan[0],vp.pan[1]];
      }
      var mPerMM=vp.scaleDenom/1000;
      vp.pan=[pd.orig[0]-dx*mPerMM,pd.orig[1]+dy*mPerMM];
      bimSheetViewRefresh();
      return;
    }
    var o=A3D.sheetDrag.orig;
    if(A3D.sheetDrag.mode==='move'){
''')
rep("  function bimSheetDblClick(ev){\n    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;\n    var mm=bimSheetEvtToMM(ev,el.sheetcv);\n    var hit=bimSheetHitTest(sheet,mm);\n    if(hit)bimOpenViewportPropsDlg(hit.vp.id);\n  }\n",
    r'''  function bimSheetDblClick(ev){
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    var hit=bimSheetHitTest(sheet,mm);
    /* __acad3dV116: double-click is the way into a viewport and back out, in AutoCAD and in Revit
       alike. It used to open the properties dialog, which is on the right-click menu now. A schedule
       has no model to work in, so its double-click still opens its properties. */
    if(hit&&hit.vp.kind!=='schedule'){bimSetModelSpace(hit.vp.id);return;}
    if(hit){bimOpenViewportPropsDlg(hit.vp.id);return;}
    bimSetPaperSpace();
  }
''')
rep("      el.sheetcv.addEventListener('dblclick',bimSheetDblClick);\n",
    "      el.sheetcv.addEventListener('dblclick',bimSheetDblClick);\n"
    "      el.sheetcv.addEventListener('wheel',bimSheetWheel,{passive:false});   /* __acad3dV116 */\n"
    "      el.sheetcv.addEventListener('contextmenu',bimSheetContextMenu);\n")
rep("    A3D.activeSheetId=id;A3D.sheetSelVp=null;\n",
    "    A3D.activeSheetId=id;A3D.sheetSelVp=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */\n")
rep("      A3D.activeSheetId=null;A3D.sheetSelVp=null;A3D.sheetDrag=null;\n",
    "      A3D.activeSheetId=null;A3D.sheetSelVp=null;A3D.sheetDrag=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */\n")
rep("    A3D.sel=null;A3D.sel2=null;A3D.meshes={};\n    bimSyncActiveGlobal();\n    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();bimSheetViewRefresh();paint();\n",
    "    A3D.sel=null;A3D.sel2=null;A3D.meshes={};\n"
    "    if(A3D.sheetActiveVp&&!bimSheetVp(bimSheetById(A3D.activeSheetId),A3D.sheetActiveVp))A3D.sheetActiveVp=null;   /* __acad3dV116 */\n"
    "    bimSyncActiveGlobal();\n    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();bimSheetViewRefresh();paint();\n")

# the viewport dialog: one delete path, and a scale it cannot list is shown, not silently replaced
rep("      else if(act==='del'){\n        closeDlg();\n        pushUndo();\n        var idx=sheet.viewports.indexOf(vp);if(idx>=0)sheet.viewports.splice(idx,1);\n        if(A3D.sheetSelVp===vp.id)A3D.sheetSelVp=null;\n        bimSheetViewRefresh();saveSoon();\n      }else closeDlg();\n",
    "      else if(act==='del'){\n        closeDlg();\n        bimDeleteSheetViewport(vp.id);   /* __acad3dV116: the one delete path */\n      }else closeDlg();\n")
rep("    for(i=0;i<SHEET_SCALES.length;i++)sopts+='<option value=\"'+SHEET_SCALES[i].denom+'\"'+(vp.scaleMode==='ratio'&&SHEET_SCALES[i].denom===vp.scaleDenom?' selected':'')+'>'+SHEET_SCALES[i].label+'</option>';\n",
    "    var listed=false;\n"
    "    for(i=0;i<SHEET_SCALES.length;i++){if(SHEET_SCALES[i].denom===vp.scaleDenom)listed=true;sopts+='<option value=\"'+SHEET_SCALES[i].denom+'\"'+(vp.scaleMode==='ratio'&&SHEET_SCALES[i].denom===vp.scaleDenom?' selected':'')+'>'+SHEET_SCALES[i].label+'</option>';}\n"
    "    /* __acad3dV116: a scale not in the list is shown as it is; OK used to set the first one listed */\n"
    "    if(vp.scaleMode==='ratio'&&!listed&&isFinite(vp.scaleDenom))sopts='<option value=\"'+vp.scaleDenom+'\" selected>1:'+vp.scaleDenom+'</option>'+sopts;\n")

# ---- 5. keys, commands and tools do not reach the model behind the paper ---------------------------------------------------
rep("    if(bimStartShowing())return;\n",
    "    if(bimStartShowing())return;\n"
    "    if(bimSheetOnScreen()&&bimSheetKey(ev))return;   /* __acad3dV116 */\n")
rep("    if(bimStartShowing()&&!BIM_START_CMDS[act]){a3dToast('Open a project to use that command');return false;}\n",
    "    if(bimStartShowing()&&!BIM_START_CMDS[act]){a3dToast('Open a project to use that command');return false;}\n"
    "    /* __acad3dV116: on a sheet only the commands that make sense on paper run */\n"
    "    if(bimSheetOnScreen()&&!BIM_SHEET_CMDS[act]){a3dToast('That works on the model: go to the Model tab first');return false;}\n")
rep("  var BIM_START_CMDS={newProject:1,openJson:1};\n",
    "  var BIM_START_CMDS={newProject:1,openJson:1};\n"
    "  var BIM_SHEET_CMDS={saveJson:1,openJson:1,newProject:1,closeProject:1,undo:1,redo:1,print:1,   /* __acad3dV116 */\n"
    "    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1};\n"
    "  var BIM_SHEET_ACTS={'bim:sheet':1,'bim:titleblock':1,'bim:projinfo':1,'bim:uipanels':1,'m:saveproj':1,'m:openproj':1};\n")
rep("    var act=b.getAttribute('data-a3dr');\n",
    "    var act=b.getAttribute('data-a3dr');\n"
    "    if(bimSheetOnScreen()&&!BIM_SHEET_ACTS[act]){a3dToast('That works on the model: go to the Model tab first');return;}   /* __acad3dV116 */\n")
rep("    '#a3d-sheetcanvas{",
    "    '.a3d-sheetview.open~#a3d-dock{display:none}'+   /* __acad3dV116: the model's tools, not the paper's */\n"
    "    '#a3d-statusbar.a3d-onsheet .a3d-stlvl,#a3d-statusbar.a3d-onsheet #a3d-stcoords,#a3d-statusbar.a3d-onsheet #a3d-snapgrp,#a3d-statusbar.a3d-onsheet #a3d-navgrp{display:none}'+\n"
    "    '#a3d-sheetcanvas{")
rep("    var sp=document.getElementById('a3d-stspace');\n",
    "    var bar=document.getElementById('a3d-statusbar');\n"
    "    if(bar)bar.classList.toggle('a3d-onsheet',bimSheetOnScreen());   /* the model's aids step aside on paper */\n"
    "    var sp=document.getElementById('a3d-stspace');\n")

# ---- 6. what the status bar says on a sheet ---------------------------------------------------------------------------------
rep("  function bimStatusHintText(){\n    var sk=A3D.sk,o,n;\n",
    r'''  function bimStatusHintText(){
    var sk=A3D.sk,o,n;
    if(bimSheetOnScreen()){   /* __acad3dV116 */
      if(A3D.sheetActiveVp){
        var avs=bimSheetVp(bimSheetById(A3D.activeSheetId),A3D.sheetActiveVp);
        return 'Model space in '+((avs&&avs.label)||'the viewport')+': drag to pan, wheel for the next scale, double-click outside or Escape for paper space';
      }
      return 'Paper space: drag a viewport to move it, its corner to size it, double-click it to work in it';
    }
''')

# ---- 7. test surface -------------------------------------------------------------------------------------------------------
rep("  window.__a3dSheetIsOpen=function(){return !!(el.sheetview&&el.sheetview.classList.contains('open'));};\n",
    "  window.__a3dSheetIsOpen=function(){return !!(el.sheetview&&el.sheetview.classList.contains('open'));};\n"
    "  /* __acad3dV116 */\n"
    "  window.__a3dSheetSpace=function(){\n"
    "    var sh=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sh,A3D.sheetActiveVp);\n"
    "    return {onSheet:bimSheetOnScreen(),sheet:A3D.activeSheetId,activeVp:A3D.sheetActiveVp,selVp:A3D.sheetSelVp,\n"
    "            view:A3D_VIEW.kind,viewId:A3D_VIEW.id,viewName:A3D_VIEW.name,\n"
    "            vp:vp?{pan:vp.pan||null,scaleMode:vp.scaleMode,scaleDenom:vp.scaleDenom}:null};\n"
    "  };\n"
    "  window.__a3dSheetVpCamera=function(sheetId,vpId,pxPerMM){\n"
    "    var vp=bimSheetVp(bimSheetById(sheetId),vpId);if(!vp)return null;\n"
    "    var src=bimResolveViewportSource(vp);if(src.error)return null;\n"
    "    return bimSheetSolveCamera(src,vp.w*(pxPerMM||1),vp.h*(pxPerMM||1),pxPerMM||1,vp.scaleMode,vp.scaleDenom,vp.pan);\n"
    "  };\n")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
