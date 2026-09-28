"""patch_phase93g.py -- __acad3dV93: DIVIDE and MEASURE.

Both place POINT nodes along a selected object, and both measure along the CURVE, so an arc
gets marks at equal arc length rather than bunched where it bends.

They differ in one thing: DIVIDE takes a count and neither endpoint is marked (n segments means
n-1 marks), MEASURE takes a spacing, steps it off from the start, and reports what is left over
at the far end instead of swallowing it.

One source function answers 'what curve is this object', so a wall centreline and a sketch are
divided by identical code -- which is also why a CURVED wall divides correctly with nothing
written for it here.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '3fb49d8d7cd30862b0a499cced29e92acf39474d533ecfb4fca79b9c49466f69'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1};""",
     """  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1};"""),

    # ---- the source curve, and the two commands, placed after startPointTool
    ("""  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that""",
     """  /* What curve does this object describe? One answer for both commands, so a wall and a
     sketch divide through identical code -- which is also why a CURVED wall divides correctly
     with nothing written for it, and why an arc's marks land at equal ARC LENGTH. */
  function bimDivideSource(o){
    if(!o)return null;
    if(bimIsPoint(o))return null;
    if(o.t==='sketch'&&o.pts&&o.pts.length>=2)
      return {pts:o.pts,bulges:o.bulges||null,closed:o.closed!==false,y:o.y};
    if(o.t==='solid'&&o.bim&&o.bim.centerline&&o.bim.centerline.length>=2)
      return {pts:o.bim.centerline,bulges:o.bim.bulges||null,closed:!!o.bim.closed,y:o.bim.baseY};
    return null;
  }
  function bimPlaceMarks(o,src,pts,label){
    pushUndo();
    var made=[],i,p;
    for(i=0;i<pts.length;i++){
      p=bimAddPoint(pts[i][0],pts[i][1],src.y,o.layer);
      made.push(p.id);
    }
    A3D.selSet=made;A3D.sel=made.length?made[0]:null;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(label);
    return made;
  }
  function bimApplyDivide(id,n){
    var o=objById(id);
    if(!o){a3dToast('Divide: select an object first');return null;}
    var src=bimDivideSource(o);
    if(!src){a3dToast('Divide works on sketches and walls (selected object is a '+
      (bimIsPoint(o)?'point':(o.t||'?'))+')');return null;}
    var res=bimDividePoints(src.pts,src.bulges,src.closed,n);
    if(res.error){a3dToast('Divide: '+res.error);return null;}
    if(!res.points.length){a3dToast('Divide placed no points');return null;}
    return bimPlaceMarks(o,src,res.points,'Divided into '+n+': '+res.points.length+
      ' point(s) every '+bimFmtLen(res.spacing));
  }
  function bimApplyMeasure(id,d){
    var o=objById(id);
    if(!o){a3dToast('Measure: select an object first');return null;}
    var src=bimDivideSource(o);
    if(!src){a3dToast('Measure works on sketches and walls (selected object is a '+
      (bimIsPoint(o)?'point':(o.t||'?'))+')');return null;}
    var res=bimMeasurePoints(src.pts,src.bulges,src.closed,d);
    if(res.error){a3dToast('Measure: '+res.error);return null;}
    if(!res.points.length){a3dToast('Measure placed no points');return null;}
    /* The remainder is stated. A drafter stepping off a bar spacing needs to know what is left
       at the far end, and a command that hides it has answered a different question. */
    return bimPlaceMarks(o,src,res.points,'Measured every '+bimFmtLen(d)+': '+
      res.points.length+' point(s), '+bimFmtLen(res.leftover)+' left over');
  }
  function bimOpenSpacingDlg(kind){
    var id=A3D.sel;
    var o=id?objById(id):null;
    if(!o||!bimDivideSource(o)){
      a3dToast((kind==='divide'?'Divide':'Measure')+': select a sketch or a wall first');
      return;
    }
    var src=bimDivideSource(o);
    var L=bimBulgedLength(src.pts,src.bulges,src.closed);
    closeDlg();
    var isDiv=(kind==='divide');
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(isDiv?'Divide':'Measure')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>'+(isDiv?'Number of segments':'Segment length')+'</label>'+
      '<input type="number" step="'+(isDiv?'1':'any')+'" data-a3dp="v" value="'+(isDiv?'4':(L/4).toFixed(3))+'"></div>'+
      '<div class="a3d-propnote">'+bimEsc(o.name||'Object')+' is '+bimFmtLen(L)+' long, measured along the curve.'+
      (isDiv?' Dividing into n places n-1 points; the ends are not marked.'
            :' Points are stepped off from the start; any remainder is left at the far end.')+'</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var vI=d.querySelector('[data-a3dp="v"]');
    function submit(){
      var v=parseFloat(vI.value);
      var eb=document.getElementById('a3d-dlgerr');
      /* Validated by the same builder the command runs, so the dialog cannot accept a value
         the geometry would then refuse. */
      var probe=isDiv?bimDividePoints(src.pts,src.bulges,src.closed,v)
                     :bimMeasurePoints(src.pts,src.bulges,src.closed,v);
      if(probe.error){eb.textContent=probe.error;return;}
      closeDlg();
      if(isDiv)bimApplyDivide(id,v);else bimApplyMeasure(id,v);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    vI.focus();vI.select();
  }
  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that"""),

    # ---- registry: MEASURE stops being an alias of DIST, and the four new rows land
    ("""    ['DIST',['DI','MEASURE'],'measure','Measure distance'],""",
     """    /* __acad3dV93: MEASURE was an alias of DIST. In AutoCAD they are different commands --
       DIST reports a distance, MEASURE steps points off along an object -- so the alias made
       the real command unreachable by its own name. */
    ['DIST',['DI'],'measure','Measure distance'],
    ['DIVIDE',['DIV'],'divide','Place points dividing an object into equal parts'],
    ['MEASURE',['ME'],'measurePts','Place points at a set spacing along an object'],"""),

    # ---- dispatch
    ("""    arc:function(){startArcTool();},          /* __acad3dV88 */""",
     """    arc:function(){startArcTool();},          /* __acad3dV88 */
    polygon:function(){openPolygonDlg();},    /* __acad3dV93 */
    pointTool:function(){startPointTool();},  /* __acad3dV93 */
    divide:function(){bimOpenSpacingDlg('divide');},     /* __acad3dV93 */
    measurePts:function(){bimOpenSpacingDlg('measure');},/* __acad3dV93 */"""),

    # ---- test surface
    ("""  /* __acad3dV92 */
  window.__a3dGrowEnd=bimGrowEnd;""",
     """  /* __acad3dV93 */
  window.__a3dPointAtLength=bimPointAtLength;
  window.__a3dDividePoints=bimDividePoints;
  window.__a3dMeasurePoints=bimMeasurePoints;
  window.__a3dCircleSketch=bimCircleSketch;
  window.__a3dPolygonSketch=bimPolygonSketch;
  window.__a3dSketchOutline=function(id){var o=objById(id);return o?bimSketchOutline(o):null;};
  window.__a3dIsPoint=function(id){return bimIsPoint(objById(id));};
  window.__a3dPointMarkerSegs=bimPointMarkerSegs;
  window.__a3dAddPoint=function(x,z,y){var o=bimAddPoint(x,z,y);refreshTree();paint();return o.id;};
  window.__a3dStartPolygon=startPolygonTool;
  window.__a3dApplyDivide=bimApplyDivide;
  window.__a3dApplyMeasure=bimApplyMeasure;
  window.__a3dDivideSource=function(id){var o=objById(id);var s=bimDivideSource(o);
    return s?{pts:s.pts.map(function(p){return [p[0],p[1]];}),bulges:s.bulges?s.bulges.slice():null,closed:s.closed}:null;};
  window.__acad3dV93='realcircle,polygon,pointnode,divide,measure,arclengthwalk,viewportflattens';
  /* __acad3dV92 */
  window.__a3dGrowEnd=bimGrowEnd;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
