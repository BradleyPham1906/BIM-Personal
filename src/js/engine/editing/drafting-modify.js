import { A3D, el } from '../core/state.js';
import { UNDO_STACK, bimEnterDraftingMode, bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimBuildWallGeometry, bimCarryBim, bimIsLocked } from '../bim/import-compliance.js';
import { bimDimKind } from '../annotation/dimensions.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { pick } from '../drawing/sketch-constraints.js';
import { bimDuplicateObject } from './selection-tools.js';
import { applyMergeWalls } from './precision-editing.js';
import { bimAfterSketchEdit, bimAfterWallRebuild, bimPropagateFrom } from '../bim/region-dependents.js';
import { BIM_BULGE_EPS, bimBulgeAt } from '../drawing/arc-storage.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { bimRelinkCopies, bimRelinkNote } from '../assets/blocks.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV250: AutoCAD's modify commands (D2) =================
     MOVE, COPY, STRETCH, EXPLODE, JOIN (polylines), OVERKILL, DRAWORDER and MATCHPROP, by
     AutoCAD's names and aliases. MOVE and COPY take a base point and a second point (a typed
     length along the rubber band works, as in LINE), STRETCH a crossing window first. COPY
     repeats until Enter or Esc, as AutoCAD's does.

     The geometry is in pure functions over plan points (bimStretchPts, bimExplodePoly,
     bimJoinPolys, bimOverkillPts, bimDrawOrder), tested without a canvas; the commands only
     gather the selection, call them, and record the undo. */
  function bimDmSelIds(){
    return (A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
  }
  function bimDmStart(tool,extra,msg){
    closeDlg();
    bimEnterDraftingMode();
    var sk={tool:tool,pts:[],y:bimGetActiveLevel().elev,on:null},k;
    for(k in extra)if(extra.hasOwnProperty(k))sk[k]=extra[k];
    A3D.sk=sk;
    a3dToast(msg);
    paint();
  }
  /* ---------- MOVE (M) and COPY (CO, CP) ---------- */
  function startMoveTool(){
    var ids=bimDmSelIds();
    if(!ids.length){a3dToast('Move: select the objects first');return;}
    bimDmStart('move',{dmIds:ids,skip:ids},'Move: specify the base point');
  }
  function startCopyTool(){
    var ids=bimDmSelIds();
    if(!ids.length){a3dToast('Copy: select the objects first');return;}
    bimDmStart('copy',{dmIds:ids,skip:ids,dmCopies:0},'Copy: specify the base point');
  }
  function bimMoveSelection(ids,d){
    var ok=0,locked=0,i,o;
    pushUndo();
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);
      if(!o)continue;
      if(bimIsLocked(o)){locked++;continue;}
      if(!o.pos)o.pos=[0,0,0];
      o.pos[0]+=d[0];o.pos[2]+=d[1];
      bimPropagateFrom([o.id],'transform',[d[0],0,d[1]]);
      ok++;
    }
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Moved '+ok+' object(s) '+bimFmtLen(Math.sqrt(d[0]*d[0]+d[1]*d[1]))+(locked?' ('+locked+' locked, skipped)':''));
    return ok;
  }
  function bimCopySelection(ids,d){
    var pairs=[],newIds=[],i,o,c;
    pushUndo();
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);
      if(!o)continue;
      c=bimDuplicateObject(o,d[0],d[1]);
      if(c){A3D.objs.push(c);newIds.push(c.id);pairs.push([o,c]);}
    }
    var cut=pairs.length?bimRelinkCopies(pairs,d[0],d[1],0):0;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(newIds.length?'Copied '+newIds.length+' object(s)'+bimRelinkNote(cut)+'; next point, or Enter to finish':
      'Nothing could be copied (unsupported object type)');
    return newIds;
  }
  /* ---------- STRETCH (S) ---------- */
  function startStretchTool(){
    bimDmStart('stretch',{dmPhase:'window'},'Stretch: click the first corner of a crossing window');
  }
  /* The points inside the window [x0,z0,x1,z1] move by d; the rest stay. */
  function bimStretchPts(pts,win,d){
    var x0=Math.min(win[0],win[2]),x1=Math.max(win[0],win[2]),z0=Math.min(win[1],win[3]),z1=Math.max(win[1],win[3]);
    var moved=0,out=pts.map(function(p){
      if(p[0]>=x0&&p[0]<=x1&&p[1]>=z0&&p[1]<=z1){moved++;return [p[0]+d[0],p[1]+d[1]];}
      return [p[0],p[1]];
    });
    return {pts:out,moved:moved,all:moved===pts.length};
  }
  function bimStretchApply(win,d){
    var touched=0,skipped=0,i,o,q,r,lw,loc;
    pushUndo();
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimLayerShown(o)||bimIsLocked(o))continue;
      q=bimObjOffset(o);
      /* the window is in world coordinates, the points in the object's own */
      loc=[win[0]-q[0],win[1]-q[2],win[2]-q[0],win[3]-q[2]];
      if((o.t==='sketch'||o.t==='room')&&o.pts&&o.pts.length){
        r=bimStretchPts(o.pts,loc,d);
        if(!r.moved)continue;
        o.pts=r.pts;
        if(o.t==='sketch')bimAfterSketchEdit(o);
        touched++;
      }else if(o.t==='dim'&&o.p1&&o.p2&&bimDimKind(o)==='linear'){
        r=bimStretchPts([o.p1,o.p2,o.d1,o.d2],loc,d);
        if(!r.moved)continue;
        o.p1=r.pts[0];o.p2=r.pts[1];o.d1=r.pts[2];o.d2=r.pts[3];
        o.length=Math.sqrt(Math.pow(o.p2[0]-o.p1[0],2)+Math.pow(o.p2[1]-o.p1[1],2));
        touched++;
      }else if(o.t==='text'&&o.pt){
        r=bimStretchPts([o.pt],loc,d);
        if(r.moved){o.pt=r.pts[0];touched++;}
      }else if(o.bim&&o.bim.type==='wall'&&o.bim.centerline){
        r=bimStretchPts(o.bim.centerline,loc,d);
        if(!r.moved)continue;
        lw=bimBuildWallGeometry(r.pts,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
        if(lw.error){skipped++;continue;}
        o.mesh=lw.mesh;o.bim=bimCarryBim(o.bim,lw.bim);bimAfterWallRebuild(o);
        touched++;
      }
    }
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(touched?'Stretched '+touched+' object(s)'+(skipped?' ('+skipped+' could not be rebuilt)':''):
      'Stretch: no points of lines, walls, rooms or dimensions in that window');
    return touched;
  }
  /* The clicks of MOVE, COPY and STRETCH, from skPlacePoint and from a typed length. */
  function bimDmPoint(sk,p){
    var d;
    if(sk.tool==='stretch'&&sk.dmPhase==='window'){
      sk.dmWin=(sk.dmWin||[]).concat([p]);
      if(sk.dmWin.length===1){a3dToast('Stretch: click the opposite corner');paint();return;}
      sk.dmPhase='base';sk.pts=[];
      a3dToast('Stretch: specify the base point');paint();return;
    }
    sk.pts.push([p[0],p[1]]);
    if(sk.pts.length===1){a3dToast((sk.tool==='move'?'Move':sk.tool==='copy'?'Copy':'Stretch')+': specify the second point, or type a distance');paint();return;}
    d=[sk.pts[1][0]-sk.pts[0][0],sk.pts[1][1]-sk.pts[0][1]];
    if(sk.tool==='move'){A3D.sk=null;bimMoveSelection(sk.dmIds,d);return;}
    if(sk.tool==='stretch'){
      var w=sk.dmWin;A3D.sk=null;
      bimStretchApply([w[0][0],w[0][1],w[1][0],w[1][1]],d);return;
    }
    /* COPY: the base point stays; each further point is another copy */
    bimCopySelection(sk.dmIds,d);
    sk.dmCopies++;
    sk.pts=[sk.pts[0]];
    A3D.sk=sk;
    paint();
  }
  function bimIsDmTool(sk){return !!sk&&(sk.tool==='move'||sk.tool==='copy'||sk.tool==='stretch');}
  /* ---------- EXPLODE (X) ---------- */
  /* A polyline as its segments, each one line or one arc with its own bulge. */
  function bimExplodePoly(pts,bulges,closed){
    var n=pts.length,segs=closed?n:n-1,out=[],i,b;
    for(i=0;i<segs;i++){
      var a=pts[i],c=pts[(i+1)%n];
      if(Math.abs(a[0]-c[0])+Math.abs(a[1]-c[1])<1e-12)continue;
      b=bimBulgeAt(bulges,i);
      out.push({pts:[[a[0],a[1]],[c[0],c[1]]],bulges:Math.abs(b)>BIM_BULGE_EPS?[b]:null});
    }
    return out;
  }
  function bimExplodeSelection(){
    var ids=bimDmSelIds(),made=[],gone=0,i,o,parts,j;
    if(!ids.length){a3dToast('Explode: select polylines first');return 0;}
    pushUndo();
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);
      if(!o||o.t!=='sketch'||bimIsLocked(o)||!o.pts||o.pts.length<3&&o.closed===false)continue;
      parts=bimExplodePoly(o.pts,o.bulges||null,o.closed!==false);
      if(parts.length<2)continue;
      for(j=0;j<parts.length;j++){
        A3D.counts.sketch=(A3D.counts.sketch||0)+1;
        var s={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:'Sketch '+A3D.counts.sketch,
          col:o.col,layer:o.layer,pos:bimObjOffset(o),pts:parts[j].pts,y:o.y,on:o.on||null,closed:false};
        if(parts[j].bulges)s.bulges=parts[j].bulges;
        A3D.objs.push(s);made.push(s.id);
      }
      A3D.objs.splice(A3D.objs.indexOf(o),1);gone++;
    }
    if(!gone){UNDO_STACK.pop();a3dToast('Explode: nothing to explode (select polylines of two or more segments)');return 0;}
    A3D.selSet=made;A3D.sel=made[0]||null;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Exploded '+gone+' polyline(s) into '+made.length+' segments');
    return made.length;
  }
  /* ---------- JOIN (J), polylines ---------- */
  /* Chains open polylines whose ends meet within tol into as few runs as possible. A run that is
     reversed has its points reversed and its bulges reversed and negated (an arc walked the other
     way turns the other way). A run that comes back to its start is closed. */
  function bimReversePoly(P){
    var pts=P.pts.slice().reverse(),b=null,i,n=P.pts.length;
    if(P.bulges){b=[];for(i=0;i<n-1;i++)b.push(-bimBulgeAt(P.bulges,n-2-i));}
    return {pts:pts,bulges:b};
  }
  function bimJoinPolys(list,tol){
    tol=tol>0?tol:1e-6;
    var pool=list.map(function(P){return {pts:P.pts.map(function(p){return [p[0],p[1]];}),bulges:P.bulges?P.bulges.slice(0,P.pts.length-1):null};});
    var out=[],same=function(a,b){return Math.abs(a[0]-b[0])<=tol&&Math.abs(a[1]-b[1])<=tol;};
    while(pool.length){
      var run=pool.shift(),grew=true;
      while(grew){
        grew=false;
        for(var i=0;i<pool.length;i++){
          var P=pool[i],head=run.pts[0],tail=run.pts[run.pts.length-1],Q=null,atEnd=true;
          if(same(tail,P.pts[0]))Q=P;
          else if(same(tail,P.pts[P.pts.length-1]))Q=bimReversePoly(P);
          else if(same(head,P.pts[P.pts.length-1])){Q=P;atEnd=false;}
          else if(same(head,P.pts[0])){Q=bimReversePoly(P);atEnd=false;}
          if(!Q)continue;
          var A=atEnd?run:Q,B=atEnd?Q:run;
          var ba=A.bulges||[],bb=B.bulges||[],nb=[],k;
          for(k=0;k<A.pts.length-1;k++)nb.push(ba[k]||0);
          for(k=0;k<B.pts.length-1;k++)nb.push(bb[k]||0);
          run={pts:A.pts.concat(B.pts.slice(1)),bulges:nb.some(function(v){return Math.abs(v)>BIM_BULGE_EPS;})?nb:null};
          pool.splice(i,1);grew=true;break;
        }
      }
      run.closed=false;
      if(run.pts.length>3&&same(run.pts[0],run.pts[run.pts.length-1])){
        run.pts.pop();run.closed=true;
        if(run.bulges)run.bulges=run.bulges.slice(0,run.pts.length);
      }
      out.push(run);
    }
    return out;
  }
  function bimJoinSelection(){
    var ids=bimDmSelIds(),src=[],i,o;
    for(i=0;i<ids.length;i++){o=objById(ids[i]);if(o&&o.t==='sketch'&&o.closed===false&&!bimIsLocked(o))src.push(o);}
    if(src.length<2)return false;
    var y0=src[0].y||0,q0=bimObjOffset(src[0]);
    var runs=bimJoinPolys(src.map(function(s){var q=bimObjOffset(s);
      return {pts:s.pts.map(function(p){return [p[0]+q[0]-q0[0],p[1]+q[2]-q0[2]];}),bulges:s.bulges||null};}),1e-4);
    if(runs.length>=src.length){a3dToast('Join: those lines do not meet end to end');return true;}
    pushUndo();
    for(i=0;i<src.length;i++)A3D.objs.splice(A3D.objs.indexOf(src[i]),1);
    var made=[];
    for(i=0;i<runs.length;i++){
      A3D.counts.sketch=(A3D.counts.sketch||0)+1;
      var s={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:'Sketch '+A3D.counts.sketch,
        col:src[0].col,layer:src[0].layer,pos:q0.slice(),pts:runs[i].pts,y:y0,on:src[0].on||null};
      if(!runs[i].closed)s.closed=false;
      if(runs[i].bulges)s.bulges=runs[i].bulges;
      A3D.objs.push(s);made.push(s.id);
    }
    A3D.selSet=made;A3D.sel=made[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Joined '+src.length+' objects into '+runs.length+' polyline(s)');
    return true;
  }
  /* JOIN: lines join into polylines; two walls merge as before. */
  function bimJoinCommand(){
    if(!bimJoinSelection())applyMergeWalls();
  }
  /* ---------- OVERKILL (OV) ---------- */
  /* One polyline without its repeated vertices (and without a closing vertex that repeats the first). */
  function bimOverkillPts(pts,bulges,closed,tol){
    tol=tol>0?tol:1e-6;
    var out=[],ob=[],i,n=pts.length;
    for(i=0;i<n;i++){
      var p=pts[i],last=out[out.length-1];
      if(last&&Math.abs(p[0]-last[0])<=tol&&Math.abs(p[1]-last[1])<=tol)continue;
      out.push([p[0],p[1]]);ob.push(bimBulgeAt(bulges,i));
    }
    if(closed&&out.length>2&&Math.abs(out[0][0]-out[out.length-1][0])<=tol&&Math.abs(out[0][1]-out[out.length-1][1])<=tol){out.pop();ob.pop();}
    return {pts:out,bulges:ob.some(function(v){return Math.abs(v)>BIM_BULGE_EPS;})?ob:null,removed:n-out.length};
  }
  /* A key that is the same for two sketches with the same geometry, either way round. */
  function bimOverkillKey(o,tol){
    var q=bimObjOffset(o),r=function(v){return Math.round(v/tol);};
    var w=o.pts.map(function(p){return r(p[0]+q[0])+','+r(p[1]+q[2]);});
    var b=(o.bulges||[]).map(function(v){return Math.round(v*1e6);});
    var f=w.join(';')+'|'+b.join(',')+'|'+(o.closed!==false)+'|'+r((o.y||0)+q[1]);
    var rb=(o.bulges||[]).slice().reverse().map(function(v){return Math.round(-v*1e6);});
    var g=w.slice().reverse().join(';')+'|'+rb.join(',')+'|'+(o.closed!==false)+'|'+r((o.y||0)+q[1]);
    return f<g?f:g;
  }
  function bimOverkill(ids,tol){
    tol=tol>0?tol:1e-4;
    var pool=ids&&ids.length?ids.map(objById).filter(Boolean):A3D.objs.slice();
    var seen={},dup=[],fixed=0,i,o,k;
    pushUndo();
    for(i=0;i<pool.length;i++){
      o=pool[i];
      if(o.t!=='sketch'||!o.pts||bimIsLocked(o)||!bimLayerShown(o))continue;
      var ok=bimOverkillPts(o.pts,o.bulges||null,o.closed!==false,tol);
      if(ok.removed&&ok.pts.length>=2){o.pts=ok.pts;if(ok.bulges)o.bulges=ok.bulges;else delete o.bulges;fixed++;bimAfterSketchEdit(o);}
      k=bimOverkillKey(o,tol);
      if(seen[k])dup.push(o);else seen[k]=1;
    }
    for(i=0;i<dup.length;i++)A3D.objs.splice(A3D.objs.indexOf(dup[i]),1);
    if(!dup.length&&!fixed){UNDO_STACK.pop();a3dToast('Overkill: no duplicates found');return {deleted:0,fixed:0};}
    A3D.sel=null;A3D.selSet=[];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Overkill: '+dup.length+' duplicate(s) deleted, '+fixed+' polyline(s) cleaned');
    return {deleted:dup.length,fixed:fixed};
  }
  /* ---------- DRAWORDER (DR) ---------- */
  /* The list with the chosen ids moved to the end (front) or the start (back), each group keeping
     its own order. */
  function bimDrawOrder(list,ids,where){
    var pick={},i,sel=[],rest=[];
    for(i=0;i<ids.length;i++)pick[ids[i]]=1;
    for(i=0;i<list.length;i++)(pick[list[i].id]?sel:rest).push(list[i]);
    return where==='back'?sel.concat(rest):rest.concat(sel);
  }
  function bimDrawOrderCommand(where){
    var ids=bimDmSelIds();
    if(!ids.length){a3dToast('Draw order: select the objects first');return;}
    pushUndo();
    A3D.objs=bimDrawOrder(A3D.objs,ids,where);
    paint();saveSoon();
    a3dToast(ids.length+' object(s) brought '+(where==='back'?'to the back':'to the front'));
  }
  function openDrawOrderDlg(){
    if(!bimDmSelIds().length){a3dToast('Draw order: select the objects first');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Draw order</div><div class="a3d-dlgbody">'+
      '<div class="a3d-propnote">Objects drawn later are drawn over the ones before them.</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="back">Send to back</button><button data-a3dlg="front">Bring to front</button></div>';
    el.root.appendChild(d);el.dlg=d;
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;
      var w=b.getAttribute('data-a3dlg');closeDlg();if(w==='front'||w==='back')bimDrawOrderCommand(w);});
  }
  /* ---------- MATCHPROP (MA) ---------- */
  var BIM_MATCH_PROPS=['layer','col','color','linetype','lineweight','ltScale','height','hatch','plWidth'];
  /* The source's properties copied to the destination; only those the source has. */
  function bimMatchProps(src,dst){
    var n=0,i,k;
    for(i=0;i<BIM_MATCH_PROPS.length;i++){
      k=BIM_MATCH_PROPS[i];
      if(src[k]===undefined)continue;
      dst[k]=(src[k]&&typeof src[k]==='object')?JSON.parse(JSON.stringify(src[k])):src[k];
      n++;
    }
    return n;
  }
  function startMatchPropTool(){
    var ids=bimDmSelIds(),src=ids.length===1?objById(ids[0]):null;
    bimDmStart('matchprop',{mpSrc:src?src.id:null},src?'Match properties: click the objects to change (Esc to finish)':
      'Match properties: click the source object');
  }
  function bimMatchPropClick(sk,xy){
    var o=pick(xy[0],xy[1]);
    if(!o||!o.id){a3dToast('Match properties: nothing there');return;}
    if(!sk.mpSrc){sk.mpSrc=o.id;a3dToast('Match properties: now click the objects to change (Esc to finish)');paint();return;}
    var s=objById(sk.mpSrc);
    if(!s||o.id===s.id)return;
    if(bimIsLocked(o)){a3dToast('That object is on a locked layer');return;}
    pushUndo();
    bimMatchProps(s,o);
    paint();saveSoon();
    a3dToast('Properties matched to '+(o.name||'the object'));
  }
export {
  bimDmPoint, bimDmSelIds, bimExplodeSelection, bimIsDmTool, bimJoinCommand, bimMatchPropClick, bimOverkill,
  openDrawOrderDlg, startCopyTool, startMatchPropTool, startMoveTool, startStretchTool
};
