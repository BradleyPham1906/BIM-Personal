"""patch_phase88b.py -- Phase 88 part 2: the ARC command, and the consumers that draw curves.

Every place that needed the real shape now calls bimFlattenSketch. None of them tessellate for
themselves, so none of them can disagree about how.
"""
import hashlib, pathlib, sys

BASE = 'c2f23e12dad62c0baf868084a06cec635911e3f148a004d45d3844cf1687237b'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. addSketchObj carries bulges and an explicit closed flag ------------------------------
reps.append(("""  function addSketchObj(pts2){
    var sk=A3D.sk;if(!sk)return null;
    A3D.counts.sketch=(A3D.counts.sketch||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'sketch',name:'Sketch '+A3D.counts.sketch,col:'#5ec4b8',
      pos:[0,0,0],pts:pts2,y:sk.y,on:sk.on||null
    };
    A3D.objs.push(o);
    A3D.sk=null;
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created: use Pad to extrude or Pocket to cut');
    return o;
  }""",
"""  /* __acad3dV88: opts is {bulges, closed, toast}. All three are optional and every existing
     caller passes none of them, so a sketch made by LINE, PLINE, RECTANG or CIRCLE is byte for
     byte the object it was before this phase - no bulges key at all. */
  function addSketchObj(pts2,opts){
    var sk=A3D.sk;if(!sk)return null;
    opts=opts||{};
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
  }""", 1))

# ---- 2. the point branch ---------------------------------------------------------------------
reps.append(("""    }else if(sk.tool==='extend'){""",
"""    }else if(sk.tool==='arc'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3)finishArc();
    }else if(sk.tool==='extend'){""", 1))

# ---- 3. the tool label, typed coordinates, and the prompt -------------------------------------
reps.append(("""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',poly:'Polyline',""",
"""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',poly:'Polyline',""", 1))

reps.append(("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1};""",
"""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1};   /* __acad3dV88 */""", 1))

reps.append(("""    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';""",
"""    if(sk.tool==='circle')return n?'Specify radius:':'Specify center point:';
    /* __acad3dV88: three prompts for three points, and no bracket list - this build implements
       only the 3-point form, so offering [Center/End] would advertise what it refuses. */
    if(sk.tool==='arc')return n===0?'Specify start point of arc:'
      :(n===1?'Specify second point on arc:':'Specify end point of arc:');""", 1))

# ---- 4. the three renderers: draw the curve, not the chord ------------------------------------
reps.append(("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(o.pts,o.closed!==false,lay);""",
"""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay);   /* __acad3dV88 */""", 1))

reps.append(("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(o.pts,o.closed!==false,lay,o.id,rg,false);""",
"""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay,o.id,rg,false);   /* __acad3dV88 */""", 1))

reps.append(("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(o.pts,o.closed!==false,o.id,o.y,rg,false);""",
"""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,rg,false);   /* __acad3dV88 */""", 1))

# ---- 5. pick where the curve is, not where the chord is ---------------------------------------
reps.append(("""      var pts=o.pts,n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){
        var a=pts[k],b=pts[(k+1)%n];
        // __acad3dV75: pick where the sketch is DRAWN, not where its local array says.""",
"""      /* __acad3dV88: pick against the FLATTENED curve. An arc picked on its chord would be
         selectable along a line it is not drawn on, and unselectable where it is. */
      var pts=bimFlattenSketch(o),n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){
        var a=pts[k],b=pts[(k+1)%n];
        // __acad3dV75: pick where the sketch is DRAWN, not where its local array says.""", 1))

# ---- 6. command table, ribbon, hooks, marker --------------------------------------------------
reps.append(("""    extend:function(){startExtendTool();},""",
"""    arc:function(){startArcTool();},          /* __acad3dV88 */
    extend:function(){startExtendTool();},""", 1))

reps.append(("""    'bim:extend':ric('<path d="M3 12h11"/><path d="M11 8l4 4-4 4"/><path d="M19 4v16"/>'),""",
"""    'bim:extend':ric('<path d="M3 12h11"/><path d="M11 8l4 4-4 4"/><path d="M19 4v16"/>'),
    'bim:arc':ric('<path d="M4 19a15 15 0 0 1 16-14"/><circle cx="4" cy="19" r="1.4"/><circle cx="20" cy="5" r="1.4"/>'),""", 1))

reps.append(("""'bim:extend':'Extend',""", """'bim:extend':'Extend','bim:arc':'Arc',""", 1))

reps.append(("""    if(act==='bim:extend'){startExtendTool();return;}""",
"""    if(act==='bim:extend'){startExtendTool();return;}
    if(act==='bim:arc'){startArcTool();return;}""", 1))

reps.append(("""      ],small:['bim:wall','bim:room','bim:floor','bim:column']},""",
"""      ],small:['bim:arc','bim:wall','bim:room','bim:floor','bim:column']},""", 1))

reps.append(("""  window.__a3dExtendPolyline=bimExtendPolyline;""",
"""  /* __acad3dV88: the arc core, exposed so the suite asserts on the stored bulge and the
     geometry it describes rather than on a rendered picture. */
  window.__a3dBulgeArc=bimBulgeArc;
  window.__a3dBulgeFrom3Pts=bimBulgeFrom3Pts;
  window.__a3dFlattenPoly=bimFlattenPoly;
  window.__a3dFlattenSketch=function(id){var o=objById(id);return o?bimFlattenSketch(o):null;};
  window.__a3dBulgedLength=bimBulgedLength;
  window.__a3dBulgedArea=bimBulgedArea;
  window.__a3dPointOnSweptArc=bimPointOnSweptArc;
  window.__a3dArcSegments=bimArcSegments;
  window.__acad3dV88='bulgestorage,arc3point,flattenonce,arcpicking,arcprompts';
  window.__a3dExtendPolyline=bimExtendPolyline;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
