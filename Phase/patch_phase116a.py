"""patch_phase116a.py -- V116 Model and layout tabs, part 1: a sheet is on screen only through the view
path. Two ways in (the New Sheet dialog and the ribbon's Sheet command) opened the sheet directly and
left the view state saying Plan; the sheet toolbar's Close, deleting the open sheet and undoing its
creation all closed the paper and left the view state saying Sheet. Leaving for a sheet now remembers
the model view, and every way back returns to it. One label for a sheet, one next free number, and
Sheet Setup validates before it changes anything."""
NAME = 'patch_phase116a.py'
BASE = '2d0f9968752e968acb0536ac239d55fe082d911b041cbd7c119ae4bf2fcf3b69'
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
# ---- 1. the model view a sheet was opened from ----------------------------------------------------------
rep("  var A3D_VIEW={kind:'plan',id:null,name:'Floor Plan'};\n",
    r'''  var A3D_VIEW={kind:'plan',id:null,name:'Floor Plan'};
  /* __acad3dV116: where the model was when a sheet was opened -- the view and its camera -- so the
     Model tab goes back to exactly that, the way AutoCAD's does. Per project: the project tabs keep
     it with the rest of a project's runtime state. */
  var A3D_LAST_MODEL_VIEW=null;
''')
rep("      if(kind!=='sheet')bimCloseSheetView();\n",
    "      if(kind==='sheet'&&A3D_VIEW.kind!=='sheet'){   /* __acad3dV116 */\n"
    "        A3D_LAST_MODEL_VIEW={kind:A3D_VIEW.kind,id:A3D_VIEW.id,\n"
    "          cam:{yaw:A3D.cam.yaw,pitch:A3D.cam.pitch,dist:A3D.cam.dist,tx:A3D.cam.tx,ty:A3D.cam.ty,tz:A3D.cam.tz}};\n"
    "      }\n"
    "      if(kind!=='sheet')bimCloseSheetView();\n")

# ---- 2. one label and one next number for a sheet ---------------------------------------------------------
rep("  function bimSheetById(id){\n",
    r'''  /* __acad3dV116: the one label for a sheet -- layout tab, sheet toolbar, view menu, Project Browser
     and print title all read it, so a rename shows everywhere at once. */
  function bimSheetLabel(sh){
    if(!sh)return 'Sheet';
    var n=String(sh.number==null?'':sh.number).trim(),m=String(sh.name==null?'':sh.name).trim();
    return (n&&m)?(n+' - '+m):(n||m||'Sheet');
  }
  /* __acad3dV116: the next number no sheet has. It was 'A'+(101+count), which repeats a number as
     soon as one sheet is deleted: with A101 and A102, delete A101 and the next sheet was A102 again. */
  function bimNextSheetNumber(){
    var max=100,i,m;
    for(i=0;i<A3D.sheets.length;i++){
      m=/^A(\d+)$/i.exec(String(A3D.sheets[i].number==null?'':A3D.sheets[i].number).trim());
      if(m&&+m[1]>max)max=+m[1];
    }
    return 'A'+(max+1);
  }
  /* __acad3dV116: three places deleted a sheet, two asked first in different words, one did not ask.
     One path now: it names the sheet and says the delete can be undone, which it can. */
  function bimConfirmDeleteSheet(id){
    var sh=bimSheetById(id);
    if(!sh)return false;
    if(!window.confirm('Delete sheet "'+bimSheetLabel(sh)+'"? Undo (Ctrl+Z) brings it back.'))return false;
    return bimDeleteSheet(id);
  }
  function bimSheetById(id){
''')
rep("      number:number||('A'+(101+A3D.sheets.length)),name:name||'Untitled',\n",
    "      number:number||bimNextSheetNumber(),name:name||'Untitled',   /* __acad3dV116 */\n")
rep("'<div class=\"a3d-dlgrow\"><label>Number</label><input type=\"text\" data-a3dp=\"num\" value=\"A'+(101+A3D.sheets.length)+'\"></div>'+\n",
    "'<div class=\"a3d-dlgrow\"><label>Number</label><input type=\"text\" data-a3dp=\"num\" value=\"'+bimEsc(bimNextSheetNumber())+'\"></div>'+\n")
rep("      return sh?(sh.number+' - '+sh.name):'Sheet';\n", "      return bimSheetLabel(sh);   /* __acad3dV116 */\n")
rep("    if(el.sheetnum)el.sheetnum.textContent=sheet.number+' - '+sheet.name;\n",
    "    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */\n")
rep("        h+=bimBrowserLeaf(sh.number+' - '+sh.name,{data:'data-a3dbsheetgo=\"'+sh.id+'\"',\n",
    "        h+=bimBrowserLeaf(bimSheetLabel(sh),{data:'data-a3dbsheetgo=\"'+sh.id+'\"',   /* __acad3dV116 */\n")
rep("'<html><head><title>'+bimEsc(sheet.number+' - '+sheet.name)+'</title>'",
    "'<html><head><title>'+bimEsc(bimSheetLabel(sheet))+'</title>'", 2)
rep("      else if(act==='del'){closeDlg();if(confirm('Delete sheet \"'+sheet.number+' - '+sheet.name+'\"? This cannot be undone from here.'))bimDeleteSheet(sheet.id);}\n",
    "      else if(act==='del'){closeDlg();bimConfirmDeleteSheet(sheet.id);}   /* __acad3dV116: the one delete path */\n")
rep("        if(shObj&&confirm('Delete sheet \"'+shObj.number+' - '+shObj.name+'\"?'))bimDeleteSheet(shId);\n",
    "        if(shObj)bimConfirmDeleteSheet(shId);   /* __acad3dV116: the one delete path */\n")
for bad in ("number+' - '+", "(101+A3D.sheets.length)+'"):
    if bad in t:
        sys.exit('ABORT: a second derivation is left: ' + bad)

# ---- 3. every way onto a sheet goes through the view path -------------------------------------------------
rep("      var s=bimAddSheet(num,name||'Untitled',sizeI.value);\n      bimOpenSheetView(s.id);\n",
    "      var s=bimAddSheet(num,name||'Untitled',sizeI.value);\n"
    "      bimActivateView('sheet',s.id);   /* __acad3dV116: through the view path, so the view state says Sheet */\n")
rep("    if(act==='bim:sheet'){if(A3D.sheets.length){bimOpenSheetView(A3D.activeSheetId&&bimSheetById(A3D.activeSheetId)?A3D.activeSheetId:A3D.sheets[0].id);}else{bimOpenNewSheetDlg();}return;}\n",
    "    if(act==='bim:sheet'){if(A3D.sheets.length){bimActivateView('sheet',A3D.activeSheetId&&bimSheetById(A3D.activeSheetId)?A3D.activeSheetId:A3D.sheets[0].id);}else{bimOpenNewSheetDlg();}return;}   /* __acad3dV116 */\n")

# ---- 4. and every way off it goes back to the model view it came from ----------------------------------------
rep("  function bimCloseSheetView(){\n",
    r'''  /* __acad3dV116: the Model tab. Back to the view the sheet was opened from, with its camera; a view
     that no longer exists falls back to the plan of the active level. */
  function bimSheetOnScreen(){return !!(el.sheetview&&el.sheetview.classList.contains('open'));}
  function bimShowModel(){
    if(A3D_VIEW.kind!=='sheet'&&!bimSheetOnScreen())return true;
    var m=A3D_LAST_MODEL_VIEW||{kind:'plan',id:A3D.activeLevel,cam:null};
    var ok=bimActivateView(m.kind,m.id,{anim:false});
    if(!ok)ok=bimActivateView('plan',A3D.activeLevel,{anim:false});
    if(ok&&m.cam){
      A3D.cam={yaw:m.cam.yaw,pitch:m.cam.pitch,dist:m.cam.dist,tx:m.cam.tx,ty:m.cam.ty,tz:m.cam.tz};
      paint();
    }
    return ok;
  }
  function bimCloseSheetView(){
''')
rep("    if(sheetCloseBtn2)sheetCloseBtn2.addEventListener('click',function(){bimCloseSheetView();});\n",
    "    if(sheetCloseBtn2)sheetCloseBtn2.addEventListener('click',function(){bimShowModel();});   /* __acad3dV116: the Model tab's path */\n")
rep("        if(A3D.activeSheetId===id)A3D.activeSheetId=A3D.sheets.length?A3D.sheets[0].id:null;\n        refreshBrowser();bimSheetViewRefresh();saveSoon();\n",
    "        var wasOn=(A3D.activeSheetId===id&&bimSheetOnScreen());   /* __acad3dV116 */\n"
    "        if(A3D.activeSheetId===id)A3D.activeSheetId=A3D.sheets.length?A3D.sheets[0].id:null;\n"
    "        if(wasOn)bimShowModel();\n"
    "        refreshBrowser();bimSheetViewRefresh();saveSoon();\n")
rep("    if(!sheet){el.sheetview.classList.remove('open');return;}\n",
    "    if(!sheet){\n"
    "      /* __acad3dV116: the sheet on screen is gone -- an undo of its creation, say. Its paper went\n"
    "         away before and the view state kept saying Sheet; the model it came from comes back. */\n"
    "      if(bimSheetOnScreen()||A3D_VIEW.kind==='sheet')bimShowModel();\n"
    "      else el.sheetview.classList.remove('open');\n"
    "      return;\n    }\n")

# ---- 5. Sheet Setup checks everything before it changes anything --------------------------------------------
rep("      pushUndo();\n      sheet.number=num;sheet.name=name||'Untitled';sheet.sizeKey=sizeI.value;\n      if(sizeI.value==='Custom'){\n        var cw=parseFloat(cwI.value),ch=parseFloat(chI.value);\n        if(!isFinite(cw)||cw<10||!isFinite(ch)||ch<10){document.getElementById('a3d-dlgerr').textContent='Custom size must be at least 10mm';return;}\n        sheet.w=cw;sheet.h=ch;\n      }else{\n        sheet.w=SHEET_SIZES[sizeI.value].w;sheet.h=SHEET_SIZES[sizeI.value].h;\n      }\n",
    "      /* __acad3dV116: a bad custom size used to be found after the undo step was taken and the number,\n"
    "         name and size key were already changed -- half a Sheet Setup, kept. Checked first now. */\n"
    "      var cw=parseFloat(cwI.value),ch=parseFloat(chI.value);\n"
    "      if(sizeI.value==='Custom'&&(!isFinite(cw)||cw<10||!isFinite(ch)||ch<10)){document.getElementById('a3d-dlgerr').textContent='Custom size must be at least 10mm';return;}\n"
    "      pushUndo();\n      sheet.number=num;sheet.name=name||'Untitled';sheet.sizeKey=sizeI.value;\n"
    "      if(sizeI.value==='Custom'){sheet.w=cw;sheet.h=ch;}\n"
    "      else{sheet.w=SHEET_SIZES[sizeI.value].w;sheet.h=SHEET_SIZES[sizeI.value].h;}\n")

# ---- 6. the project tabs carry the model view with the rest of a project's runtime state ----------------------
rep("    var stash={undo:UNDO_STACK,redo:REDO_STACK,view:{kind:A3D_VIEW.kind,id:A3D_VIEW.id},\n",
    "    var stash={undo:UNDO_STACK,redo:REDO_STACK,view:{kind:A3D_VIEW.kind,id:A3D_VIEW.id},lastModel:A3D_LAST_MODEL_VIEW,   /* __acad3dV116 */\n")
rep("    if(!shown)bimActivateView(window.ACAD_WS_CUR==='3d'?'3d':'plan',A3D.activeLevel,{anim:false});\n",
    "    if(!shown)bimActivateView(window.ACAD_WS_CUR==='3d'?'3d':'plan',A3D.activeLevel,{anim:false});\n"
    "    A3D_LAST_MODEL_VIEW=(rt&&rt.lastModel)||null;   /* __acad3dV116: after the activation, which would record the other project's */\n")

# ---- 7. the test surface opens and closes sheets the way the app does ---------------------------------------------
rep("  window.__a3dOpenSheetView=bimOpenSheetView;\n",
    "  window.__a3dOpenSheetView=function(id){return bimActivateView('sheet',id);};   /* __acad3dV116: the view path, not around it */\n")
rep("  window.__a3dCloseSheetView=bimCloseSheetView;\n",
    "  window.__a3dCloseSheetView=function(){return bimShowModel();};   /* __acad3dV116 */\n")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
