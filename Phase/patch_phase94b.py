"""patch_phase94b.py -- __acad3dV94: the cline entity and the XLINE / RAY tools.

AutoCAD's XLINE keeps its root and lets you fan several construction lines out of one point,
and it offers its modes at the FIRST prompt rather than after a point is down. Both are copied,
because both are the reason the command is quick to use.

The bracket list is derived from BIM_CLINE_MODES (law 3), so the prompt cannot advertise Bisect
or Offset while the keys refuse them.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '0ab8664882ae07dfe91644320176ffd5b84c64f8480baf98f2eb0c4c648c73f1'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1};""",
     """  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1};"""),

    ("""  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',poly:'Polyline',""",
     """  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',circle:'Circle',arc:'Arc',polygon:'Polygon',point:'Point',xline:'Construction line',poly:'Polyline',"""),

    # ---- the entity and the tool, beside startPointTool
    ("""  function startPointTool(){""",
     """  /* __acad3dV94 */
  function bimAddCline(p,dir,isRay,y,layer){
    var len=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
    if(!(len>1e-12))return null;
    A3D.counts.cline=(A3D.counts.cline||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'cline',ray:!!isRay,
      name:(isRay?'Ray ':'Xline ')+A3D.counts.cline,col:'#8a7fd0',
      pos:[0,0,0],p:[p[0],p[1]],dir:[dir[0]/len,dir[1]/len],
      y:(typeof y==='number')?y:bimGetActiveLevel().elev,
      layer:(layer===undefined?A3D.activeLayer:layer)
    };
    A3D.objs.push(o);
    return o;
  }
  function startClineTool(isRay){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'xline',pts:[],ray:!!isRay,mode:null,angle:null,y:lvl.elev,on:null};
    bimSyncStatusHint();
    paint();
    a3dToast((isRay?'Ray':'Construction line')+': pick a point, or press '+
      bimClineModeKeyHint()+'; Escape when finished');
  }
  function bimClineModeKeyHint(){
    var out=[],i,name,m;
    for(i=0;i<BIM_CLINE_MODE_ORDER.length;i++){
      name=BIM_CLINE_MODE_ORDER[i];m=BIM_CLINE_MODES[name];
      if(m&&m.key)out.push(m.key+' for '+m.label.toLowerCase());
    }
    return out.join(', ');
  }
  /* A mode can only be chosen before a root is committed, which is where AutoCAD offers it.
     The prompt asks this same predicate, so the two cannot disagree. */
  function bimClineCanSetMode(sk){
    return !!(sk&&sk.tool==='xline'&&!sk.mode&&(!sk.pts||!sk.pts.length));
  }
  function bimSetClineMode(sk,mode){
    if(!bimClineCanSetMode(sk)||!BIM_CLINE_MODES[mode])return false;
    sk.mode=mode;
    sk.angle=null;
    bimSyncStatusHint();paint();
    return true;
  }
  /* The direction this sketch is currently able to produce without another point, or null when
     it still needs one. One predicate, consulted by the prompt and by the placement alike. */
  function bimClineReadyDir(sk){
    if(!sk||sk.tool!=='xline')return null;
    if(sk.mode==='hor'||sk.mode==='ver')return bimClineDir(sk.mode);
    if(sk.mode==='ang')return bimClineDir('ang',null,null,sk.angle);
    return null;
  }
  function bimPlaceCline(sk,p,dir){
    pushUndo();
    var o=bimAddCline(p,dir,sk.ray,sk.y,undefined);
    if(!o){
      console.warn('[BIM] Construction line could not be built',p,dir);
      a3dToast('That gives no direction for a construction line');
      return null;
    }
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function startPointTool(){"""),

    # ---- placement
    ("""    if(sk.tool==='point'){                      /* __acad3dV93 */""",
     """    if(sk.tool==='xline'){                      /* __acad3dV94 */
      var clDir=bimClineReadyDir(sk);
      if(clDir){
        /* Horizontal, vertical and angle all know their direction already, so every click is
           one finished construction line and the tool stays live for the next. */
        bimPlaceCline(sk,[gx,gz],clDir);
        return;
      }
      if(!sk.pts.length){
        sk.pts.push([gx,gz]);
        bimSyncStatusHint();paint();
        return;
      }
      clDir=bimClineDir(null,sk.pts[0],[gx,gz]);
      if(!clDir){a3dToast('Pick a point away from the first one');return;}
      /* The ROOT is kept, which is what lets a drafter fan several construction lines out of
         one point without restarting the command -- AutoCAD's own behaviour. */
      bimPlaceCline(sk,[sk.pts[0][0],sk.pts[0][1]],clDir);
      return;
    }
    if(sk.tool==='point'){                      /* __acad3dV93 */"""),

    # ---- an angle is a number, not a coordinate
    ("""  function bimCommitTypedPoint(str){
    var sk=A3D.sk;if(!sk)return false;""",
     """  function bimCommitTypedPoint(str){
    var sk=A3D.sk;if(!sk)return false;
    /* __acad3dV94: in Angle mode the first thing typed is an ANGLE, not a coordinate. Parsing
       it as a coordinate would take '30' as a direct distance entry along a rubber band that
       does not exist yet. */
    if(sk.tool==='xline'&&sk.mode==='ang'&&typeof sk.angle!=='number'){
      var av=parseFloat(str);
      if(!isFinite(av)){a3dToast('Enter the angle in degrees, then Enter');paint();return false;}
      sk.angle=av;
      bimSyncStatusHint();paint();
      a3dToast('Construction lines at '+av+' degrees: click to place them');
      return true;
    }"""),

    # ---- the prompt, derived
    ("""    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */""",
     """    if(sk.tool==='point')return 'Specify a point (Escape when finished):';   /* __acad3dV93 */
    /* __acad3dV94: the bracket list comes from the same table the keys consult, so it can
       never offer a mode that does nothing. */
    if(sk.tool==='xline'){
      var clWhat=sk.ray?'ray':'xline';
      if(bimClineCanSetMode(sk))
        return 'Specify a point or ['+bimClineModeLabels().join('/')+']:';
      if(sk.mode==='ang'&&typeof sk.angle!=='number')
        return 'Enter angle of '+clWhat+' in degrees:';
      if(bimClineReadyDir(sk))return 'Specify through point:';
      return sk.pts.length?'Specify through point:':'Specify a point:';
    }"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
