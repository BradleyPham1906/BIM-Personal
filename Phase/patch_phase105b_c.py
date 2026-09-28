"""patch_phase105bc.py"""
NAME = 'patch_phase105bc'
BASE = 'ad3c18278cff4906e3a3a7fb30346af9508e03a28c902c283fa62976ee87f8cd'
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
# --- patch c: gross and net area for a level.

NEW = """  /* __acad3dV105b: AREA PLANS.

     Gross floor area is the area inside the exterior walls -- what IBC 202 measures, and what an
     occupant load on a gross factor is taken against. Net area is what the rooms on the level add
     up to. Both are DERIVED from what is drawn: the gross ring comes out of the same arrangement
     of wall centerlines the room tool traces, so a level cannot report a gross area that
     disagrees with the walls on it. */
  var BIM_AREA_EPS=1e-7;
  /* A dead-end wall is walked in and straight back out, so a traced face carries the run A,B,A.
     The pair cancels in a shoelace taken on the centerlines and does NOT cancel once each side
     has been pushed inward by a wall thickness, so the spurs come out BEFORE the offset. */
  function bimStripSpurs(pts,bulges,srcs){
    var P=pts.slice(),B=(bulges||[]).slice(),S=(srcs||[]).slice(),guard=0,n,i,a,c,d1,d2,np,nb,ns,m;
    while(guard++<4000){
      n=P.length;
      if(n<3)break;
      d1=-1;
      for(i=0;i<n;i++){
        a=P[i];c=P[(i+2)%n];
        if(Math.abs(a[0]-c[0])<1e-7&&Math.abs(a[1]-c[1])<1e-7){d1=i;break;}
      }
      if(d1<0)break;
      d2=(d1+1)%n;np=[];nb=[];ns=[];
      for(m=0;m<n;m++){
        if(m===d1||m===d2)continue;
        np.push(P[m]);nb.push(B[m]);ns.push(S[m]);
      }
      P=np;B=nb;S=ns;
    }
    return {pts:P,bulges:B,srcs:S};
  }
  function bimRingInsideRing(inner,outer){
    var i;
    for(i=0;i<inner.length;i++)if(!bimPointInPoly(inner[i],outer))return false;
    return true;
  }
  /* The inside face of one run of exterior walls. The face arrives traced CLOCKWISE, which puts
     the building on the RIGHT of the direction of travel; every edge is pushed that way by the
     depth of its own wall's body and the pushed lines are mitered together, so a corner between
     two different thicknesses lands where the two faces actually meet. */
  function bimGrossRingFromFace(face,cache){
    var st=bimStripSpurs(face.pts,face.bulges,face.srcs);
    if(st.pts.length<3)return null;
    var segs=[],n=st.pts.length,i,k,a,b,bl,flat,src;
    for(i=0;i<n;i++){
      a=st.pts[i];b=st.pts[(i+1)%n];bl=st.bulges[i]||0;src=st.srcs[i]||null;
      if(Math.abs(bl)>BIM_BULGE_EPS){
        /* A curved exterior wall is offset arc-wise, not chord-wise: flatten first, then push. */
        flat=bimFlattenPoly([a,b],[bl,0],false);
        for(k=0;k+1<flat.length;k++)segs.push({a:flat[k],b:flat[k+1],src:src});
      }else segs.push({a:a,b:b,src:src});
    }
    var lines=[],dx,dz,L,dir,nrm,mid,ins,rings;
    for(i=0;i<segs.length;i++){
      dx=segs[i].b[0]-segs[i].a[0];dz=segs[i].b[1]-segs[i].a[1];
      L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-9)continue;
      dir=[dx/L,dz/L];
      nrm=[dir[1],-dir[0]];
      mid=[(segs[i].a[0]+segs[i].b[0])/2,(segs[i].a[1]+segs[i].b[1])/2];
      ins=0;
      if(segs[i].src){
        if(!cache.hasOwnProperty(segs[i].src))cache[segs[i].src]=bimWallFaceRings(objById(segs[i].src));
        rings=cache[segs[i].src];
        ins=bimWallInsetAt(rings,mid,nrm);
        if(ins===null||!isFinite(ins))ins=0;
      }
      lines.push({a:[segs[i].a[0]+nrm[0]*ins,segs[i].a[1]+nrm[1]*ins],
                  b:[segs[i].b[0]+nrm[0]*ins,segs[i].b[1]+nrm[1]*ins],
                  dir:dir,inset:ins});
    }
    if(lines.length<3)return null;
    var ring=[],cur,nxt,hit,cap,dd;
    for(i=0;i<lines.length;i++){
      cur=lines[i];nxt=lines[(i+1)%lines.length];
      hit=bimLineLineIntersect(cur.a,cur.b,nxt.a,nxt.b);
      cap=6*Math.max(cur.inset,nxt.inset)+1e-6;
      dd=hit?Math.sqrt((hit[0]-cur.b[0])*(hit[0]-cur.b[0])+(hit[1]-cur.b[1])*(hit[1]-cur.b[1])):Infinity;
      if(hit&&isFinite(hit[0])&&isFinite(hit[1])&&dd<=cap)ring.push(hit);
      else {ring.push(cur.b);ring.push(nxt.a);}   /* parallel, or a miter that runs away: the jog */
    }
    var out=[],p;
    for(i=0;i<ring.length;i++){
      p=ring[i];
      if(out.length&&Math.abs(out[out.length-1][0]-p[0])<1e-9&&Math.abs(out[out.length-1][1]-p[1])<1e-9)continue;
      out.push(p);
    }
    if(out.length>2&&Math.abs(out[0][0]-out[out.length-1][0])<1e-9&&Math.abs(out[0][1]-out[out.length-1][1])<1e-9)out.pop();
    if(out.length<3)return null;
    return {pts:out,area:bimPolyArea(out),srcIds:face.srcIds?face.srcIds.slice():[]};
  }
  function bimLevelGrossRings(levelId){
    var lv=bimLevelById(levelId);
    if(!lv)return {rings:[],error:'no such level'};
    var edges=bimBoundaryEdges(lv.elev||0,{walls:true});
    if(edges.length<3)return {rings:[],level:lv};
    var arr,g,faces,rings=[],cache={},i,r;
    try{
      arr=bimArrangeEdges(edges);
      if(arr.error)return {rings:[],level:lv,error:arr.error};
      g=bimBuildEdgeGraph(arr.edges);
      faces=bimTraceEdgeFaces(g);
    }catch(eAR){
      console.warn('[BIM] Area plan could not trace the walls: ',eAR);
      return {rings:[],level:lv,error:'could not trace the walls on this level'};
    }
    for(i=0;i<faces.length;i++){
      /* The outer face is the clockwise one: exactly one per connected run of walls. */
      if(bimBulgedSignedArea(faces[i].pts,faces[i].bulges,true)>=-BIM_AREA_EPS)continue;
      try{r=bimGrossRingFromFace(faces[i],cache);}
      catch(eGR){console.warn('[BIM] Area plan could not offset a wall run: ',eGR);r=null;}
      if(r&&r.area>BIM_AREA_EPS)rings.push(r);
    }
    rings.sort(function(x,y){return y.area-x.area;});
    /* A closed run of partitions that touches nothing else is its own component and traces its
       own outer face. It sits INSIDE a footprint already counted, so counting it again would add
       the same floor twice. */
    var keep=[],j,inside;
    for(i=0;i<rings.length;i++){
      inside=false;
      for(j=0;j<keep.length&&!inside;j++)if(bimRingInsideRing(rings[i].pts,keep[j].pts))inside=true;
      if(!inside)keep.push(rings[i]);
    }
    return {rings:keep,level:lv};
  }
  /* One level's area plan. Occupant load is taken the way IBC 1004.5 takes it: the areas on a
     factor are summed FIRST and divided once, because rounding each room up on its own invents
     people who are not there. */
  function bimLevelAreas(levelId){
    var lv=bimLevelById(levelId),gr=bimLevelGrossRings(levelId);
    var out={levelId:levelId,level:lv?lv.name:'-',gross:null,net:0,efficiency:null,
             rooms:0,occupants:null,rings:gr.rings||[],note:''};
    if(!lv){out.note='no such level';return out;}
    var i,g=0,rooms=[],o;
    for(i=0;i<out.rings.length;i++)g+=out.rings[i].area;
    out.gross=out.rings.length?g:null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room'||o.levelId!==levelId)continue;
      rooms.push(o);
      if(o.area>0)out.net+=o.area;
    }
    out.rooms=rooms.length;
    if(out.gross!==null&&out.gross>BIM_AREA_EPS)out.efficiency=out.net/out.gross*100;
    /* A gross factor is taken against gross area. What the rooms do not cover -- the walls, and
       any corridor nobody has drawn as a room -- is shared out in proportion. That is an
       apportionment, so it is SAID here and in the schedule's Note rather than left to be found. */
    var scale=(out.gross!==null&&out.net>BIM_AREA_EPS)?out.gross/out.net:1;
    var groups={},lf,key,area,noFactor=0,k,tot=0,any=false,grossUsed=false;
    for(i=0;i<rooms.length;i++){
      lf=bimRoomLoadFactor(rooms[i]);
      if(!lf||!(rooms[i].area>0)){noFactor++;continue;}
      if(lf.basis&&String(lf.basis).toLowerCase().indexOf('gross')>=0){area=rooms[i].area*scale;grossUsed=true;}
      else area=rooms[i].area;
      key=lf.m2+'|'+(lf.basis||'');
      if(!groups[key])groups[key]={m2:lf.m2,area:0};
      groups[key].area+=area;
      any=true;
    }
    for(k in groups)if(groups.hasOwnProperty(k))tot+=Math.ceil(groups[k].area/groups[k].m2-1e-9);
    out.occupants=any?tot:null;
    var notes=[];
    if(gr.error)notes.push(gr.error);
    else if(!out.rings.length)notes.push('no closed run of walls to measure gross area from');
    if(noFactor)notes.push(noFactor+' room'+(noFactor===1?'':'s')+' with no load factor');
    if(grossUsed&&out.gross===null)notes.push('gross factors taken against room area: no gross area on this level');
    else if(grossUsed&&scale!==1)notes.push('gross factors apportioned at '+scale.toFixed(2)+'x room area');
    out.note=notes.join('; ');
    return out;
  }
"""

rep("  function bimBuildRoomSchedule(){", NEW + "  function bimBuildRoomSchedule(){", 1)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
