"""patch_phase98d.py -- __acad3dV98: a grid line can be selected and edited.

REPORTED: "I can't touch or edit ... grid lines." Measured: a grid could be placed and deleted
from the Levels panel, and nothing else. A click on it selected nothing, it had no grips, no
properties, Delete did nothing, and a misplaced grid could only be deleted and redrawn.

Grids stay datums in A3D.grids (Phase 42's decision: they span every level and are not model
elements), so they get a selection of their own, A3D.selGrid, which is live only while no
object is selected -- selecting anything else supersedes it without every selection path in
the file having to know grids exist. Then the ordinary editing verbs, each through the paths
objects already use rather than parallel ones:

  click           selects (the model under a grid still wins: grids are drawn beneath it)
  end grips       drag either end, snapped like any grip
  body drag       drag the line to move it
  Delete / menu   delSelection removes it
  Escape          clears it
  Properties      name (rename, duplicates refused), both ends, read-only length
  Levels panel    clicking a grid's row selects it
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'f2eba5e23020d1558bdbcd431b1040a9c8fbbfa6b3d7c522bf99e6d6205c127d'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

GRID_FNS = """
  /* ================= __acad3dV98: selecting and editing a grid ================= */
  function bimGridById(id){
    var i;
    if(!id||!A3D.grids)return null;
    for(i=0;i<A3D.grids.length;i++)if(A3D.grids[i].id===id)return A3D.grids[i];
    return null;
  }
  /* The selected grid, or null. An object selection supersedes it. */
  function bimSelectedGrid(){
    if(!A3D.selGrid)return null;
    if(A3D.sel||(A3D.selSet&&A3D.selSet.length))return null;
    return bimGridById(A3D.selGrid);
  }
  function bimSelectGrid(id){
    var g=bimGridById(id);
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D.selGrid=g?g.id:null;
    refreshLevels();refreshTree();paint();
    return !!g;
  }
  /* Picked where it is DRAWN: the line at the active level's elevation, and the two bubbles. */
  function bimPickGrid(x,y){
    if(A3D.section||!A3D.grids||!A3D.grids.length)return null;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),y0=bimGetActiveLevel().elev;
    var best=null,bestD=Infinity,i,g,s1,s2,d,db;
    for(i=A3D.grids.length-1;i>=0;i--){
      g=A3D.grids[i];
      s1=toScreen([g.p1[0],y0,g.p1[1]],V,W,H);s2=toScreen([g.p2[0],y0,g.p2[1]],V,W,H);
      d=bimPointSegDist(x,y,s1[0],s1[1],s2[0],s2[1]);
      d=(d<6)?d:Infinity;
      db=Math.min(Math.sqrt((x-s1[0])*(x-s1[0])+(y-s1[1])*(y-s1[1])),
                  Math.sqrt((x-s2[0])*(x-s2[0])+(y-s2[1])*(y-s2[1])));
      if(db<=10)d=0;
      if(d<bestD){bestD=d;best=g;}
    }
    return best;
  }
  function bimRenameGrid(id,name){
    var g=bimGridById(id),i;
    if(!g){a3dToast('That grid no longer exists');return false;}
    name=String(name===undefined||name===null?'':name).replace(/^\\s+|\\s+$/g,'');
    if(!name){a3dToast('A grid needs a name');return false;}
    if(name===g.name)return true;
    for(i=0;i<A3D.grids.length;i++){
      if(A3D.grids[i].id!==id&&A3D.grids[i].name===name){
        a3dToast('Grid '+name+' already exists - grid names must be unique');return false;
      }
    }
    pushUndo();
    var was=g.name;
    g.name=name;
    refreshLevels();refreshProps();paint();saveSoon();
    a3dToast('Grid '+was+' renamed to '+name);
    return true;
  }
  function bimSetGridEnds(id,p1,p2){
    var g=bimGridById(id);
    if(!g){a3dToast('That grid no longer exists');return false;}
    if(!p1||!p2||!isFinite(p1[0])||!isFinite(p1[1])||!isFinite(p2[0])||!isFinite(p2[1])){
      a3dToast('Grid ends must be numbers');return false;
    }
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    if(Math.sqrt(dx*dx+dz*dz)<1e-6){a3dToast('Grid line is too short');return false;}
    pushUndo();
    g.p1=[p1[0],p1[1]];g.p2=[p2[0],p2[1]];
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimGridPropsHtml(g){
    var dx=g.p2[0]-g.p1[0],dz=g.p2[1]-g.p1[1];
    var h='<div class="a3d-ptypehd">'+
      '<div class="a3d-ptypeic">'+(a3drIcon('bim:grid')||a3drIcon('box'))+'</div>'+
      '<div class="a3d-ptypetx"><div class="a3d-ptypename">Grid '+bimEsc(g.name)+'</div>'+
      '<div class="a3d-ptypesub">Grids : Grid</div></div>'+
      '<button class="a3d-pedit" data-gridact="delete" title="Delete this grid">Delete</button>'+
      '</div>';
    var ident=bimPropRow('Name','<input type="text" data-gridf="name" value="'+bimEsc(g.name)+'">');
    function lenIn(label,v,f){
      return bimPropRow(bimLenLabel(label),'<input type="number" step="any" data-gridf="'+f+
        '" value="'+bimDispLen(v)+'">');
    }
    var geo=lenIn('Start X',g.p1[0],'x1')+lenIn('Start Y',g.p1[1],'y1')+
            lenIn('End X',g.p2[0],'x2')+lenIn('End Y',g.p2[1],'y2')+
            bimPropLenText('Length',Math.sqrt(dx*dx+dz*dz));
    return h+bimPropGroup('Identity Data',ident)+bimPropGroup('Extents',geo);
  }
"""

EDITS = [
    # --- the functions, after bimRemoveGrid
    ("""      A3D.grids.splice(i,1);
      refreshLevels();refreshTree();paint();saveSoon();
      a3dToast('Grid '+nm+' deleted');
      return true;
    }
    return false;
  }
""",
     """      A3D.grids.splice(i,1);
      if(A3D.selGrid===id)A3D.selGrid=null;   /* __acad3dV98 */
      refreshLevels();refreshTree();paint();saveSoon();
      a3dToast('Grid '+nm+' deleted');
      return true;
    }
    return false;
  }
""" + GRID_FNS),

    # --- drawn highlighted when selected
    ("""    var y0=bimGetActiveLevel().elev,i;
    ctx.save();
    for(i=0;i<A3D.grids.length;i++){
      var g=A3D.grids[i];
      var s1=toScreen([g.p1[0],y0,g.p1[1]],V,W,H),s2=toScreen([g.p2[0],y0,g.p2[1]],V,W,H);
      ctx.beginPath();
      ctx.moveTo(s1[0],s1[1]);ctx.lineTo(s2[0],s2[1]);
      ctx.strokeStyle='#6f7681';
      ctx.lineWidth=1;""",
     """    var y0=bimGetActiveLevel().elev,i,selG=bimSelectedGrid();
    ctx.save();
    for(i=0;i<A3D.grids.length;i++){
      var g=A3D.grids[i],gSel=(selG&&selG.id===g.id);   /* __acad3dV98 */
      var s1=toScreen([g.p1[0],y0,g.p1[1]],V,W,H),s2=toScreen([g.p2[0],y0,g.p2[1]],V,W,H);
      ctx.beginPath();
      ctx.moveTo(s1[0],s1[1]);ctx.lineTo(s2[0],s2[1]);
      ctx.strokeStyle=gSel?'#4ea1ff':'#6f7681';
      ctx.lineWidth=gSel?1.6:1;"""),
    ("""        ctx.fillStyle='rgba(20,22,26,0.85)';ctx.fill();
        ctx.strokeStyle='#8f97a3';ctx.lineWidth=1.1;ctx.stroke();""",
     """        ctx.fillStyle='rgba(20,22,26,0.85)';ctx.fill();
        ctx.strokeStyle=gSel?'#4ea1ff':'#8f97a3';ctx.lineWidth=gSel?1.6:1.1;ctx.stroke();"""),

    # --- grips at both ends
    ("""  function bimDrawGrips(ctx,V,W,H){
    A3D.grips=[];
    var o=objById(A3D.sel);""",
     """  function bimDrawGrips(ctx,V,W,H){
    A3D.grips=[];
    var gs=bimSelectedGrid();   /* __acad3dV98: a selected grid's two ends */
    if(gs&&!A3D.section){
      var gy=bimGetActiveLevel().elev,gk,gsp;
      for(gk=0;gk<2;gk++){
        gsp=toScreen([(gk?gs.p2:gs.p1)[0],gy,(gk?gs.p2:gs.p1)[1]],V,W,H);
        A3D.grips.push({x:gsp[0],y:gsp[1],idx:gk,objId:gs.id,kind:'grid',elev:gy});
        ctx.save();
        ctx.fillStyle=(drag&&drag.grip&&drag.kind==='grid'&&drag.idx===gk)?'#ffd479':'#4ea1ff';
        ctx.strokeStyle='#0d1117';ctx.lineWidth=1.2;
        ctx.fillRect(gsp[0]-4,gsp[1]-4,8,8);ctx.strokeRect(gsp[0]-4,gsp[1]-4,8,8);
        ctx.restore();
      }
      return;
    }
    var o=objById(A3D.sel);"""),
    ("""      if(g.objId!==A3D.sel)continue;
      var dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);""",
     """      if(g.kind==='grid'){   /* __acad3dV98: live only while that grid is the selection */
        var sgG=bimSelectedGrid();
        if(!sgG||sgG.id!==g.objId)continue;
      }else if(g.objId!==A3D.sel)continue;
      var dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);"""),

    # --- grip drag writes the grid end
    ("""      var fakeSk={y:drag.elev,pts:[]};
      var snapped=bimSnapPoint(xy,g0,fakeSk);
      var o=objById(drag.objId);""",
     """      var fakeSk={y:drag.elev,pts:[]};
      var snapped=bimSnapPoint(xy,g0,fakeSk);
      if(drag.kind==='grid'){   /* __acad3dV98: grids are world datums -- no object offset */
        var gg=bimGridById(drag.objId);
        if(gg){
          var other=drag.idx?gg.p1:gg.p2;
          var gdx=snapped[0]-other[0],gdz=snapped[1]-other[1];
          if(Math.sqrt(gdx*gdx+gdz*gdz)>=1e-6){
            if(drag.idx)gg.p2=[snapped[0],snapped[1]];else gg.p1=[snapped[0],snapped[1]];
            drag.moved=true;
          }
          paint();saveSoon();
        }
        return;
      }
      var o=objById(drag.objId);"""),

    # --- body drag of a selected grid
    ("""        if(A3D.selSet&&A3D.selSet.length>1&&A3D.selSet.indexOf(hit.id)>=0){
          drag.mvGroup=A3D.selSet.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
          drag.mvStart=drag.mvGroup.map(function(id){var oo=objById(id);return oo?[oo.pos[0],oo.pos[1],oo.pos[2]]:null;});
          var g0=groundPoint(xy[0],xy[1],drag.my);
          drag.mvOrigin=g0?[g0[0],g0[2]]:[0,0];
        }
      }
    }""",
     """        if(A3D.selSet&&A3D.selSet.length>1&&A3D.selSet.indexOf(hit.id)>=0){
          drag.mvGroup=A3D.selSet.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
          drag.mvStart=drag.mvGroup.map(function(id){var oo=objById(id);return oo?[oo.pos[0],oo.pos[1],oo.pos[2]]:null;});
          var g0=groundPoint(xy[0],xy[1],drag.my);
          drag.mvOrigin=g0?[g0[0],g0[2]]:[0,0];
        }
      }
      /* __acad3dV98: pressing on the SELECTED grid drags it. The undo snapshot is taken on
         the first real movement, so a click that selects nothing new adds no undo step. */
      if(!hit){
        var sgD=bimSelectedGrid(),gpD=sgD?bimPickGrid(xy[0],xy[1]):null;
        if(gpD&&gpD.id===sgD.id){
          var gy0=bimGetActiveLevel().elev,gO=groundPoint(xy[0],xy[1],gy0);
          if(gO)drag.gridMv={id:gpD.id,y:gy0,o:[gO[0],gO[2]],p1:gpD.p1.slice(),p2:gpD.p2.slice(),undo:false};
        }
      }
    }"""),
    ("""    if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>3||Math.abs(xy[1]-drag.y0)>3))drag.moved=true;
    if(!drag.moved)return;
    if(drag.mv){""",
     """    if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>3||Math.abs(xy[1]-drag.y0)>3))drag.moved=true;
    if(!drag.moved)return;
    if(drag.gridMv){   /* __acad3dV98 */
      var gm=drag.gridMv,gmG=bimGridById(gm.id),gN=groundPoint(xy[0],xy[1],gm.y);
      if(gmG&&gN){
        if(!gm.undo){pushUndo();gm.undo=true;}
        var mdx=gN[0]-gm.o[0],mdz=gN[2]-gm.o[1];
        gmG.p1=[gm.p1[0]+mdx,gm.p1[1]+mdz];gmG.p2=[gm.p2[0]+mdx,gm.p2[1]+mdz];
        paint();saveSoon();
      }
      return;
    }
    if(drag.mv){"""),
    ("""    var wasSk=drag.sk,moved=drag.moved,pan=drag.pan,wasGrip=drag.grip,wasMarquee=drag.marquee;""",
     """    var wasSk=drag.sk,moved=drag.moved,pan=drag.pan,wasGrip=drag.grip,wasMarquee=drag.marquee;
    var wasGridMv=drag.gridMv;   /* __acad3dV98 */"""),
    ("""    if(wasGrip){refreshTree();paint();saveSoon();return;}""",
     """    if(wasGrip){refreshTree();paint();saveSoon();return;}
    if(wasGridMv&&moved){refreshProps();paint();saveSoon();return;}   /* __acad3dV98 */"""),

    # --- a click selects a grid when nothing in the model is under the cursor
    ("""    var o=pick(xy[0],xy[1]);
    if(ev.ctrlKey||ev.metaKey){
      if(o&&o.id!==A3D.sel)A3D.sel2=(A3D.sel2===o.id)?null:o.id;
    }else{
      A3D.sel=o?o.id:null;
      A3D.selSet=o?[o.id]:[];
      if(!o)A3D.sel2=null;
      if(A3D.sel2===A3D.sel)A3D.sel2=null;
    }
    refreshTree();paint();""",
     """    var o=pick(xy[0],xy[1]);
    if(ev.ctrlKey||ev.metaKey){
      if(o&&o.id!==A3D.sel)A3D.sel2=(A3D.sel2===o.id)?null:o.id;
    }else{
      A3D.sel=o?o.id:null;
      A3D.selSet=o?[o.id]:[];
      if(!o)A3D.sel2=null;
      if(A3D.sel2===A3D.sel)A3D.sel2=null;
      /* __acad3dV98: grids are drawn beneath the model, so they are picked after it */
      var gpk=o?null:bimPickGrid(xy[0],xy[1]);
      A3D.selGrid=gpk?gpk.id:null;
      if(gpk)refreshLevels();
    }
    refreshTree();paint();"""),

    # --- Escape clears it
    ("""      if(A3D.sel||A3D.sel2||(A3D.selSet&&A3D.selSet.length)){
        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
        refreshTree();refreshProps();paint();""",
     """      if(A3D.sel||A3D.sel2||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid()){
        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];A3D.selGrid=null;   /* __acad3dV98 */
        refreshLevels();refreshTree();refreshProps();paint();"""),

    # --- Delete removes it, through the one delete path
    ("""  function delSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Nothing selected to delete');return false;}""",
     """  function delSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length&&bimSelectedGrid())return bimRemoveGrid(A3D.selGrid);   /* __acad3dV98 */
    if(!ids.length){a3dToast('Nothing selected to delete');return false;}"""),
    ("""    if(A3D.on){
      if(A3D.sel)delSelection();
      return true;
    }""",
     """    if(A3D.on){
      if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();   /* __acad3dV98 */
      return true;
    }"""),

    # --- Properties
    ("""    var o=objById(A3D.sel);
    if(!o){
      /* __acad3dV73: with nothing selected the inspector describes the MODEL, the way the""",
     """    var o=objById(A3D.sel);
    var gP=o?null:bimSelectedGrid();   /* __acad3dV98 */
    if(gP){el.propsbody.innerHTML=bimGridPropsHtml(gP);return;}
    if(!o){
      /* __acad3dV73: with nothing selected the inspector describes the MODEL, the way the"""),
    ("""    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      /* __acad3dV73: the no-selection model fields.""",
     """    /* __acad3dV98: the selected grid's fields. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var gi=ev.target&&ev.target.closest?ev.target.closest('[data-gridf]'):null;
      if(!gi)return;
      var gg=bimSelectedGrid();
      if(!gg)return;
      try{
        var gf=gi.getAttribute('data-gridf');
        if(gf==='name'){if(!bimRenameGrid(gg.id,gi.value))refreshProps();return;}
        var v=bimLenInputToMetres(gi.value);
        if(v===null){a3dToast('Grid ends must be numbers');refreshProps();return;}
        var np1=gg.p1.slice(),np2=gg.p2.slice();
        if(gf==='x1')np1[0]=v;else if(gf==='y1')np1[1]=v;
        else if(gf==='x2')np2[0]=v;else if(gf==='y2')np2[1]=v;
        else return;
        if(!bimSetGridEnds(gg.id,np1,np2))refreshProps();
      }catch(eGP){
        console.warn('[BIM] Grid property edit failed',eGP);
        a3dToast('That grid could not be edited - see the console');
      }
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var ga=ev.target&&ev.target.closest?ev.target.closest('[data-gridact]'):null;
      if(!ga)return;
      var gg=bimSelectedGrid();
      if(gg&&ga.getAttribute('data-gridact')==='delete')bimRemoveGrid(gg.id);
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      /* __acad3dV73: the no-selection model fields."""),

    # --- Levels panel: the row shows and sets the selection
    ("""      h+='<div class="a3d-lvlrow" data-a3dgrid="'+gd.id+'">'+""",
     """      h+='<div class="a3d-lvlrow'+(A3D.selGrid===gd.id&&!A3D.sel?' active':'')+'" data-a3dgrid="'+gd.id+'">'+   /* __acad3dV98 */"""),
    ("""      var row=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlvl]'):null;
      if(row){setActiveLevel(row.getAttribute('data-a3dlvl'));return;}""",
     """      var row=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlvl]'):null;
      if(row){setActiveLevel(row.getAttribute('data-a3dlvl'));return;}
      var grow=ev.target&&ev.target.closest?ev.target.closest('[data-a3dgrid]'):null;   /* __acad3dV98 */
      if(grow){bimSelectGrid(grow.getAttribute('data-a3dgrid'));return;}"""),

    # --- the status bar names it
    ("""      if(o)return o.name+'  \\u00b7  '+bimObjTypeLabel(o);
    }
    return 'Ready';""",
     """      if(o)return o.name+'  \\u00b7  '+bimObjTypeLabel(o);
    }
    var sgH=bimSelectedGrid();   /* __acad3dV98 */
    if(sgH)return 'Grid '+sgH.name+'  \\u00b7  Grids : Grid';
    return 'Ready';"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
