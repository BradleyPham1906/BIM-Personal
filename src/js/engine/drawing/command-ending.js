  /* ================= __acad3dV100: ending a command keeps what was drawn =================
     Which in-progress commands have something worth keeping: a LINE, PLINE or WALL with at
     least one complete segment. Everything else (an arc with two of its three points, a
     rectangle with one corner, a pick tool) has nothing complete and is simply ended. */
  function bimSketchKeepable(sk){
    return !!(sk&&sk.pts&&sk.pts.length>=2&&(sk.tool==='line'||sk.tool==='poly'||sk.tool==='wall'));
  }
  /* The one way a command is interrupted -- Escape, a view change, another command starting.
     Keeps through the SAME finisher Enter uses, so the two cannot produce different things. */
  function bimEndSketch(){
    var sk=A3D.sk;
    if(!sk)return false;
    try{
      if(bimSketchKeepable(sk)&&sk.tool==='wall'){
        /* built with the dialog's own defaults -- no dialog left behind the next command */
        var wd=bimWallDlgDefaults(),wp=sk.pts.slice(),wb=sk.bulges?sk.bulges.slice():null,wy=sk.y;
        A3D.sk=null;
        buildWallSolid(wp,wy,wd.hgt,wd.thk,wd.align,false,wb);
      }
      else if(bimSketchKeepable(sk))bimFinishCurrent();
      else cancelSketch();
    }catch(eE){
      console.warn('[BIM] Ending the command failed; the points drawn were not kept.',eE);
      a3dToast('The command could not be ended cleanly - see the console');
      A3D.sk=null;paint();
    }
    bimSyncStatusHint();
    return true;
  }
  function startSketch(tool){
    if(!SK_TOOLS[tool])return;
    closeDlg();
    bimEnterDraftingMode();
    bimRecordCmd(function(){startSketch(tool);},SK_TOOLS[tool]);   // __acad3dV86: Enter repeats it
    var y0=bimGetActiveLevel().elev,onId=null,so=objById(A3D.sel);
    if(so&&so.t!=='sketch'){
      var bb=objBBox(so);
      if(bb){y0=bb.mx[1];onId=so.id;}
    }
    A3D.sk={tool:tool,pts:[],y:y0,on:onId};
    a3dToast('Sketch '+SK_TOOLS[tool]+': click points on the plan'+(onId?' (top face of '+so.name+')':' (ground plane)')+(tool==='poly'?'; C or click the first point to close, Enter to leave it open':''));
    paint();
  }
  /* __acad3dV88: opts is {bulges, closed, toast}. All three are optional and every existing
     caller passes none of them, so a sketch made by LINE, PLINE, RECTANG or CIRCLE is byte for
     byte the object it was before this phase - no bulges key at all. */
  function addSketchObj(pts2,opts){
    var sk=A3D.sk;if(!sk)return null;
    opts=opts||{};
    if(!opts.noUndo)pushUndo();   /* __acad3dV100: a drawing was never undoable */
    A3D.counts.sketch=(A3D.counts.sketch||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'sketch',name:'Sketch '+A3D.counts.sketch,col:'#5ec4b8',
      pos:[0,0,0],pts:pts2,y:sk.y,on:sk.on||null
    };
    if(opts.bulges&&bimHasBulge(opts.bulges))o.bulges=opts.bulges.slice();
    if(opts.closed===false)o.closed=false;
    A3D.objs.push(o);
    A3D.sk=null;
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(opts.toast||(o.name+' created: use Pad to extrude or Pocket to cut'));
    return o;
  }
  /* ARC, AutoCAD's default form: start, a point ON the arc, end. The middle point is not the
     apex and is not assumed to be - bimBulgeFrom3Pts takes the circle through all three and
     the direction that actually passes through the middle one. */
  function finishArc(){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<3)return null;
    var p1=sk.pts[0],pm=sk.pts[1],p2=sk.pts[2];
    var b=bimBulgeFrom3Pts(p1,pm,p2);
    if(!isFinite(b)){
      console.warn('[BIM] Arc: three points gave no usable bulge',p1,pm,p2);
      A3D.sk=null;paint();
      a3dToast('Those three points do not define an arc');
      return null;
    }
    if(Math.abs(b)<BIM_BULGE_EPS){
      /* Colinear points have no arc. Drawn as the line they describe, and SAID, rather than
         silently emitting a degenerate arc or silently emitting nothing. */
      return addSketchObj([[p1[0],p1[1]],[p2[0],p2[1]]],
        {closed:false,toast:'Those three points are in a straight line - drawn as a line'});
    }
    var arc=bimBulgeArc(p1,p2,b);
    return addSketchObj([[p1[0],p1[1]],[p2[0],p2[1]]],
      {bulges:[b,0],closed:false,
       toast:'Arc created, radius '+(arc?bimFmtLen(arc.radius):'?')});
  }
  function startArcTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'arc',pts:[],y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
  }
  /* __acad3dV93: POLYGON. The side count and the form are settled before any point is
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
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;
    var a=sk.pts[0],b=sk.pts[1];
    if(Math.abs(a[0]-b[0])<0.05||Math.abs(a[1]-b[1])<0.05){a3dToast('Rectangle is too small');sk.pts=[];paint();return null;}
    return addSketchObj([[a[0],a[1]],[b[0],a[1]],[b[0],b[1]],[a[0],b[1]]]);
  }
  /* __acad3dV93: two vertices, both bulge 1. The 24-gon this replaces was the last piece of
     geometry in the build that approximated a shape the storage can hold exactly. */
  function finishCircle(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;
    var c=sk.pts[0],e=sk.pts[1];
    var r=Math.sqrt((e[0]-c[0])*(e[0]-c[0])+(e[1]-c[1])*(e[1]-c[1]));
    if(r<0.05){a3dToast('Circle is too small');sk.pts=[];paint();return null;}
    var cir=bimCircleSketch(c,r);
    if(!cir||cir.error){
      console.warn('[BIM] Circle could not be built',c,r,cir&&cir.error);
      sk.pts=[];paint();
      a3dToast(cir&&cir.error?cir.error:'That circle could not be built');
      return null;
    }
    return addSketchObj(cir.pts,{bulges:cir.bulges,
      toast:'Circle created, radius '+bimFmtLen(r)});
  }
  /* __acad3dV93 */
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
  /* __acad3dV100: open is AutoCAD's Enter -- the polyline ends where it is, and two points
     are a valid polyline. Closed (no argument) is Close: C, or clicking the first point. */
  function finishPoly(open){
    var sk=A3D.sk;if(!sk)return null;
    if(open){
      if(sk.pts.length<2)return null;
      var ob=sk.bulges?sk.bulges.slice(0,sk.pts.length-1):null;
      return addSketchObj(sk.pts.slice(),{bulges:ob,closed:false,
        toast:'Polyline created, open, '+(sk.pts.length-1)+' segment'+(sk.pts.length===2?'':'s')});
    }
    if(sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges});   /* __acad3dV90 */
  }

