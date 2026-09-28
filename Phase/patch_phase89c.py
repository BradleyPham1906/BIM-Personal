"""patch_phase89c.py -- Phase 89 part 3: FILLET with a radius.

The V87 deferral, collected. Geometry ported verbatim from bim_phase89_fillet_prototype.js (18/18,
including tangency at both ends and both turn directions).

The V87 stub is REPLACED, not wrapped: it carried a toast saying a rounded fillet needs arc
geometry "which this build does not store yet", and leaving that sentence in a build that does
store it is precisely the leftover Standing Law 1 is about.
"""
import hashlib, pathlib, sys

P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
src = P.read_text(encoding='utf-8')
b0 = len(src.encode('utf-8'))
assert 'function bimWallIsCurved(o)' in src, 'patch_phase89b.py must run first'

reps = []

# ---- 1. the geometry ------------------------------------------------------------------------
reps.append(("""  /* FILLET at radius 0 is exactly the corner miter Join Walls already performs, so it dispatches
     there rather than growing a second implementation of the same corner. The toast names the
     radius so nobody reads this as a rounded fillet; a radius fillet needs arc storage, which
     Phase 88 decides. */
  function applyFilletCorner(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Fillet needs two walls: click the first, Ctrl+click the second');return;}
    applyWallJoin();
    a3dToast('Filleted at radius 0 (square corner). A rounded fillet needs arc geometry, which this build does not store yet.');
  }""",
"""  /* ---------- __acad3dV89: FILLET with a radius, the V87 deferral collected.

     At radius 0 this is the square corner Join Walls performs; above 0 it cuts both walls back
     to their tangent points and builds the arc between them as a real curved wall. One code
     path computes both, so the two cannot disagree about where the corner is.

     The tangent distance is r/tan(theta/2) for an interior angle theta, and the arc sweeps
     (pi - theta) in the direction of the turn. The turn direction comes from the TRAVEL
     vectors - into the corner along -uA and out along +uB - not from uA and uB themselves,
     which point the same way (back down each wall) and would give the wrong sign for one of
     them. Both signs and the tangency are proved in Phase/bim_phase89_fillet_prototype.js. ---- */
  function bimSetEnd(cl,idx,pt){
    var out=cl.map(function(p){return [p[0],p[1]];});
    out[idx]=[pt[0],pt[1]];
    return out;
  }
  function bimFilletCorner(clA,closedA,clB,closedB,radius){
    if(closedA||closedB)return {error:'Fillet needs two open walls'};
    if(!clA||clA.length<2||!clB||clB.length<2)return {error:'Both walls need a usable centerline'};
    if(!isFinite(radius)||radius<0)return {error:'Fillet radius must be zero or greater'};
    var endsA=[0,clA.length-1],endsB=[0,clB.length-1],best=null,ia,ib;
    for(ia=0;ia<2;ia++)for(ib=0;ib<2;ib++){
      var pa=clA[endsA[ia]],pb=clB[endsB[ib]];
      var d=(pa[0]-pb[0])*(pa[0]-pb[0])+(pa[1]-pb[1])*(pa[1]-pb[1]);
      if(!best||d<best.d)best={d:d,ai:endsA[ia],bi:endsB[ib]};
    }
    var aNb=best.ai===0?1:clA.length-2,bNb=best.bi===0?1:clB.length-2;
    var ip=bimLineLineIntersect(clA[aNb],clA[best.ai],clB[bNb],clB[best.bi]);
    if(!ip)return {error:'Those two walls are parallel - there is no corner to fillet'};
    function unitFrom(corner,to){
      var vx=to[0]-corner[0],vz=to[1]-corner[1],L=Math.sqrt(vx*vx+vz*vz);
      if(L<1e-9)return null;
      return {u:[vx/L,vz/L],len:L};
    }
    var ra=unitFrom(ip,clA[aNb]),rb=unitFrom(ip,clB[bNb]);
    if(!ra||!rb)return {error:'A wall has zero length at the corner'};
    var dot=Math.max(-1,Math.min(1,ra.u[0]*rb.u[0]+ra.u[1]*rb.u[1]));
    var theta=Math.acos(dot);
    if(theta<1e-6||Math.PI-theta<1e-6)
      return {error:'Those walls are colinear at the corner - there is no angle to fillet'};
    if(radius<1e-9)
      return {a:bimSetEnd(clA,best.ai,ip),b:bimSetEnd(clB,best.bi,ip),corner:ip,radius:0,fillet:null};
    var t=radius/Math.tan(theta/2);
    if(t>=ra.len)return {error:'Radius is too large for the first wall ('+bimFmtLen(ra.len)+' available)'};
    if(t>=rb.len)return {error:'Radius is too large for the second wall ('+bimFmtLen(rb.len)+' available)'};
    var tangA=[ip[0]+ra.u[0]*t,ip[1]+ra.u[1]*t];
    var tangB=[ip[0]+rb.u[0]*t,ip[1]+rb.u[1]*t];
    var inDir=[-ra.u[0],-ra.u[1]],outDir=rb.u;
    var cross=inDir[0]*outDir[1]-inDir[1]*outDir[0];
    var sweep=(cross>=0?1:-1)*(Math.PI-theta);
    return {a:bimSetEnd(clA,best.ai,tangA),b:bimSetEnd(clB,best.bi,tangB),
            fillet:{pts:[tangA,tangB],bulges:[Math.tan(sweep/4),0]},
            corner:ip,radius:radius,tangent:t,sweep:sweep};
  }
  /* AutoCAD remembers the fillet radius between runs, and so does this. */
  function bimFilletRadius(){
    return (typeof A3D.filletRadius==='number'&&isFinite(A3D.filletRadius))?A3D.filletRadius:0.5;
  }
  function applyFilletCorner(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Fillet needs two walls: click the first, Ctrl+click the second');return;}
    if(!a.bim||a.bim.type!=='wall'||!a.bim.centerline||!b.bim||b.bim.type!=='wall'||!b.bim.centerline){
      a3dToast('Fillet works on two editable walls');return;
    }
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of those walls is locked - unlock to fillet');return;}
    if(bimRefuseIfCurved(a,'Fillet')||bimRefuseIfCurved(b,'Fillet'))return;
    openFilletDlg(a.id,b.id);
  }
  function openFilletDlg(idA,idB){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Fillet</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Radius</label><input type="number" step="any" min="0" data-a3dp="r" value="'+bimFilletRadius()+'"></div>'+
      '<div class="a3d-propnote">Radius 0 gives a square corner. Above 0, both walls are cut back to their tangent points and the arc between them is built as a curved wall.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var rI=d.querySelector('[data-a3dp="r"]');
    function submit(){
      var r=parseFloat(rI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(r)||r<0){eb.textContent='Radius must be zero or greater';return;}
      A3D.filletRadius=r;
      closeDlg();
      bimApplyFillet(idA,idB,r);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    rI.focus();rI.select();
  }
  function bimApplyFillet(idA,idB,radius){
    try{
      var a=objById(idA),b=objById(idB);
      if(!a||!b){a3dToast('One of those walls no longer exists');return false;}
      var r=bimFilletCorner(a.bim.centerline,a.bim.closed,b.bim.centerline,b.bim.closed,radius);
      if(r.error){a3dToast('Fillet: '+r.error);return false;}
      /* The curved wall is built BEFORE anything is committed, so a failure here leaves both
         walls untouched rather than half-filleted. */
      var arcWall=null;
      if(r.fillet){
        arcWall=bimNewWallFromSource(a,r.fillet.pts,false,'Fillet',r.fillet.bulges);
        if(arcWall.error){a3dToast('Fillet: '+arcWall.error);return false;}
      }
      pushUndo();
      var ra=bimRebuildWallFrom(a,r.a,false,null);
      if(ra.error){a3dToast('Fillet: '+ra.error);return false;}
      var rb=bimRebuildWallFrom(b,r.b,false,null);
      if(rb.error){a3dToast('Fillet: '+rb.error);return false;}
      if(arcWall){
        A3D.objs.push(arcWall.obj);
        A3D.sel=arcWall.obj.id;A3D.sel2=null;A3D.selSet=[arcWall.obj.id];
      }else{
        A3D.sel=a.id;A3D.sel2=null;A3D.selSet=[a.id];
      }
      refreshTree();refreshHud();paint();saveSoon();
      a3dToast(radius>0?('Filleted at radius '+bimFmtLen(radius)+' - '+arcWall.obj.name+' created')
                       :'Filleted at radius 0 (square corner)');
      return true;
    }catch(eF){
      console.warn('[BIM] Fillet failed.',eF);
      a3dToast('Fillet could not complete');
      return false;
    }
  }""", 1))

# ---- 2. test hooks --------------------------------------------------------------------------
reps.append(("""  window.__a3dBulgeArc=bimBulgeArc;""",
"""  /* __acad3dV89 */
  window.__a3dFilletCorner=bimFilletCorner;
  window.__a3dApplyFillet=bimApplyFillet;
  window.__a3dWallIsCurved=function(id){var o=objById(id);return bimWallIsCurved(o);};
  window.__a3dWallLength=function(id){
    var o=objById(id);
    return (o&&o.bim&&o.bim.centerline)?bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges):null;
  };
  window.__a3dCurvedWall=function(pts,bulges,thk,hgt,align,closed){
    var lvl=bimGetActiveLevel();
    var o=buildWallSolid(pts,lvl.elev,hgt||lvl.height,thk||0.3,align||'center',!!closed,bulges);
    return o?o.id:null;
  };
  window.__acad3dV89='curvedwalls,filletradius,arclengthinschedules,mirrornegatesbulge,curverefusals';
  window.__a3dBulgeArc=bimBulgeArc;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

# The V87 sentence that is no longer true must be gone, not merely unreachable.
assert 'does not store yet' not in out, 'the superseded arc-storage claim is still in the file'

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
