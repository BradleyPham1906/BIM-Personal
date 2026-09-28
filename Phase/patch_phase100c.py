"""patch_phase100c.py -- __acad3dV100: an interrupted wall chain is built, and drawing is undoable.

1. WALL. Its finisher opens the parameters dialog, so ending a wall chain by Escape, by a view
   change or by another command starting left a dialog up -- behind the next command, or over
   a view the user had just left. An interrupted chain is now built directly with the values
   the dialog would have offered, read from ONE function the dialog also uses, so the two cannot
   differ. Enter still opens the dialog: Enter is "finish, and let me set it up"; Escape is
   "stop, and keep what I drew".

2. UNDO NEVER SAW A DRAWING. Measured on the V99 build: draw a rectangle, a polyline or a line,
   press Undo -- it stays. addSketchObj, which every drawing command ends in, never took an undo
   snapshot. It now does, once per COMMAND: LINE makes one object per segment and takes a single
   snapshot for the whole run, and callers that already took one (BOUNDARY) say so.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'd93a7f969aa4e043c8626e91745faa0ecae81c057527484a2187e35f4e999fef'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""  function openWallDlg(pts,y0,closed,bulges){
    closeDlg();
    var lvl=bimGetActiveLevel();""",
     """  /* __acad3dV100: what the wall dialog offers, and what an interrupted chain is built with. */
  function bimWallDlgDefaults(){
    var lvl=bimGetActiveLevel();
    return {thk:0.3,hgt:lvl.height,align:'center'};
  }
  function openWallDlg(pts,y0,closed,bulges){
    closeDlg();
    var lvl=bimGetActiveLevel(),wd=bimWallDlgDefaults();"""),
    ("""      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.02" data-a3dp="thk" value="0.3"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.1" data-a3dp="hgt" value="'+lvl.height+'"></div>'+""",
     """      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.02" data-a3dp="thk" value="'+wd.thk+'"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.1" data-a3dp="hgt" value="'+wd.hgt+'"></div>'+"""),
    ("""    try{
      if(bimSketchKeepable(sk))bimFinishCurrent();
      else cancelSketch();
    }catch(eE){""",
     """    try{
      if(bimSketchKeepable(sk)&&sk.tool==='wall'){
        /* built with the dialog's own defaults -- no dialog left behind the next command */
        var wd=bimWallDlgDefaults(),wp=sk.pts.slice(),wb=sk.bulges?sk.bulges.slice():null,wy=sk.y;
        A3D.sk=null;
        buildWallSolid(wp,wy,wd.hgt,wd.thk,wd.align,false,wb);
      }
      else if(bimSketchKeepable(sk))bimFinishCurrent();
      else cancelSketch();
    }catch(eE){"""),
    ("""  function addSketchObj(pts2,opts){
    var sk=A3D.sk;if(!sk)return null;
    opts=opts||{};""",
     """  function addSketchObj(pts2,opts){
    var sk=A3D.sk;if(!sk)return null;
    opts=opts||{};
    if(!opts.noUndo)pushUndo();   /* __acad3dV100: a drawing was never undoable */"""),
    ("""    if(close&&pts.length>=3)pts.push([pts[0][0],pts[0][1]]);""",
     """    if(close&&pts.length>=3)pts.push([pts[0][0],pts[0][1]]);
    pushUndo();   /* __acad3dV100: ONE snapshot for the whole run, not one per segment */"""),
    ("""      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]]);""",
     """      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]],{noUndo:true});"""),
    ("""    var o=addSketchObj(res.pts,{bulges:res.bulges,toast:msg});""",
     """    var o=addSketchObj(res.pts,{bulges:res.bulges,toast:msg,noUndo:true});   /* __acad3dV100: snapshot taken above */"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
