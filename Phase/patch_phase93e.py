"""patch_phase93e.py -- __acad3dV93: POLYGON, and typed radii for CIRCLE.

POLYGON asks for the side count and the form up front, then takes centre and radius the way
CIRCLE does. AutoCAD's two forms are kept apart properly: INSCRIBED puts the vertices on the
circle of the given radius, CIRCUMSCRIBED puts the edge midpoints on it, so the same radius
gives the larger polygon. The circumscribed radius is derived inside bimPolygonSketch rather
than asked for twice.

Second, unrelated only in appearance: CIRCLE was missing from BIM_COORD_TOOLS, so the key
handler never opened a typing buffer for it and a typed radius did nothing at all. The V87
comment in skPlacePoint says a typed coordinate reaches the same handler a click does; for
CIRCLE it could not, because the gate upstream excluded the tool. Same class as the V87 bug,
one tool the fix missed.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '8bbade966c360c9a8dc37807a03829be712798fe78b9f11c89228be1628f6ee2'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1};   /* __acad3dV88 */""",
     """  /* __acad3dV93: circle was missing. skPlacePoint has handled a typed circle radius since
     V87, but this gate is upstream of it, so the buffer never opened and the keystrokes fell
     through to the viewport. polygon joins on the same terms. */
  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1};"""),

    ("""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',poly:'Polyline',""",
     """  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',poly:'Polyline',"""),

    # finishPolygon, beside finishCircle
    ("""  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;""",
     """  /* __acad3dV93 */
  function finishPolygon(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;
    var c=sk.pts[0],e=sk.pts[1];
    var r=Math.sqrt((e[0]-c[0])*(e[0]-c[0])+(e[1]-c[1])*(e[1]-c[1]));
    /* The angle from the centre to the second click is where the first vertex goes, so the
       polygon follows the pointer instead of always landing flat-topped. */
    var a0=Math.atan2(e[1]-c[1],e[0]-c[0]);
    var res=bimPolygonSketch(c,sk.sides,r,!!sk.circumscribed,a0);
    if(!res||res.error){
      console.warn('[BIM] Polygon could not be built',c,sk.sides,r,res&&res.error);
      sk.pts=[];paint();
      a3dToast(res&&res.error?res.error:'That polygon could not be built');
      return null;
    }
    return addSketchObj(res.pts,{toast:res.sides+'-sided polygon created, '+
      (sk.circumscribed?'circumscribed about':'inscribed in')+' radius '+bimFmtLen(r)});
  }
  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;"""),

    # the tool starter and its dialog, beside startArcTool
    ("""  function finishRect(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;""",
     """  /* __acad3dV93: POLYGON. The side count and the form are settled before any point is
     taken, which is AutoCAD's order too -- it asks for sides first. */
  function startPolygonTool(sides,circumscribed){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'polygon',pts:[],y:lvl.elev,on:null,
            sides:sides,circumscribed:!!circumscribed};
    bimSyncStatusHint();
    paint();
    a3dToast('Polygon: '+sides+' sides, '+(circumscribed?'circumscribed':'inscribed')+
      ' - click the centre, then a point on the circle');
  }
  function openPolygonDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Polygon</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Number of sides</label><input type="number" step="1" min="3" max="1024" data-a3dp="n" value="6"></div>'+
      '<div class="a3d-dlgrow"><label>Form</label><select data-a3dp="f">'+
      '<option value="i">Inscribed in circle</option>'+
      '<option value="c">Circumscribed about circle</option></select></div>'+
      '<div class="a3d-propnote">Inscribed puts the vertices on the circle you pick; circumscribed puts the edge midpoints on it, so the same radius gives a larger polygon.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var nI=d.querySelector('[data-a3dp="n"]');
    function submit(){
      var n=parseInt(nI.value,10);
      var eb=document.getElementById('a3d-dlgerr');
      /* Checked against the same builder the command uses, so the dialog can never accept a
         count the geometry would then refuse. */
      var probe=bimPolygonSketch([0,0],n,1,false);
      if(probe.error){eb.textContent=probe.error;return;}
      var circ=d.querySelector('[data-a3dp="f"]').value==='c';
      closeDlg();
      startPolygonTool(n,circ);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function finishRect(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;"""),

    # the point handler
    ("""    if(sk.tool==='rect'||sk.tool==='circle'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){if(sk.tool==='rect')finishRect();else finishCircle();}
    }""",
     """    if(sk.tool==='rect'||sk.tool==='circle'||sk.tool==='polygon'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=2){
        if(sk.tool==='rect')finishRect();
        else if(sk.tool==='polygon')finishPolygon();   /* __acad3dV93 */
        else finishCircle();
      }
    }"""),

    # the prompt
    ("""    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';""",
     """    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';
    /* __acad3dV93: the form is already chosen, so the prompt states it rather than offering
       [Inscribed/Circumscribed] at a point where no key would answer it. */
    if(sk.tool==='polygon')return n?('Specify radius of circle ('+
      (sk.circumscribed?'circumscribed':'inscribed')+'):'):'Specify center of polygon:';"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
