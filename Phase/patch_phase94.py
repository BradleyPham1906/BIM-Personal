"""patch_phase94.py -- __acad3dV94 geometry core: lines with no endpoints.

One concern: the maths. No entity, no tool, no rendering here.

Three pieces:

  bimClipInfinite   Liang-Barsky against an axis-aligned rectangle. The parameter range is the
                    ONLY difference between an XLINE (-inf,+inf) and a RAY [0,+inf), so there
                    is one clipper and not two. Written parametrically rather than from a
                    slope, because a VERTICAL construction line is the most common one a
                    drafter draws and is exactly the case a slope has no value for.

  bimClineCrossings Where a construction line meets finite geometry, which is the whole reason
                    to draw one. The parameter on the infinite line is bounded only for a ray;
                    the parameter on the thing it crosses is always bounded. Two different
                    ranges, and swapping them puts snap points out past the end of a wall.

  BIM_CLINE_MODES   Horizontal, Vertical and Angle, as a table. The prompt's bracket list is
                    derived from this table, so it can never offer Bisect or Offset while the
                    keys refuse them.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '5ee869ed7bba2a709481f77c706e1c34e726fd7e9b8df9a9eafdfde07497df0f'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

ANCHOR = """  /* ================= __acad3dV93: walking a distance along a curve ===================="""

NEW = """  /* ================= __acad3dV94: construction lines =================

     XLINE is infinite in both directions, RAY in one. Neither can be stored as two points, so
     both are stored as a root and a direction and CLIPPED for every consumer that needs
     something finite to draw. */
  function bimIsCline(o){
    return !!(o&&o.t==='cline'&&o.p&&o.dir);
  }
  /* Liang-Barsky. tMin starts at the beginning of the entity's own parameter range, which is
     the single difference between an xline and a ray. No slope is ever formed: a vertical line
     takes the p=0 branch that every other direction also takes for one of its two axes, so it
     is not a special case that someone has to remember to write. */
  function bimClipInfinite(P,dir,isRay,box){
    if(!P||!dir||!box)return null;
    var len=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
    if(!(len>1e-12))return null;
    var d=[dir[0]/len,dir[1]/len];
    var tMin=isRay?0:-Infinity,tMax=Infinity;
    var p=[-d[0],d[0],-d[1],d[1]];
    var q=[P[0]-box.minX,box.maxX-P[0],P[1]-box.minZ,box.maxZ-P[1]];
    var i,t;
    for(i=0;i<4;i++){
      if(Math.abs(p[i])<1e-12){
        /* Parallel to this pair of edges. Outside them, no value of t brings it in. */
        if(q[i]<0)return null;
        continue;
      }
      t=q[i]/p[i];
      if(p[i]<0){if(t>tMin)tMin=t;}
      else{if(t<tMax)tMax=t;}
    }
    if(tMin>tMax)return null;
    if(!isFinite(tMin)||!isFinite(tMax))return null;
    return [[P[0]+d[0]*tMin,P[1]+d[1]*tMin],[P[0]+d[0]*tMax,P[1]+d[1]*tMax]];
  }
  /* The rectangle a construction line is drawn across: everything that has extent, padded so
     the line visibly runs past the drawing rather than stopping on its edge. Derived from the
     model, so it follows the drawing instead of being a number someone picked. */
  function bimDrawingExtent2D(pad){
    var mnx=Infinity,mxx=-Infinity,mnz=Infinity,mxz=-Infinity,i,b,any=false;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(bimIsCline(o))continue;           /* an infinite line cannot set the extent it needs */
      try{b=bimObjBounds2D(o);}catch(eB){b=null;}
      if(!b)continue;
      any=true;
      if(b.minX<mnx)mnx=b.minX;
      if(b.maxX>mxx)mxx=b.maxX;
      if(b.minZ<mnz)mnz=b.minZ;
      if(b.maxZ>mxz)mxz=b.maxZ;
    }
    if(!any){mnx=-10;mxx=10;mnz=-10;mxz=10;}
    var w=mxx-mnx,hh=mxz-mnz;
    var diag=Math.sqrt(w*w+hh*hh);
    var m=(typeof pad==='number'&&pad>0)?pad:Math.max(diag,20);
    return {minX:mnx-m,maxX:mxx+m,minZ:mnz-m,maxZ:mxz+m};
  }
  /* The finite piece of a construction line, for whichever consumer is asking. */
  function bimClineVisibleSeg(o,box){
    if(!bimIsCline(o))return null;
    return bimClipInfinite(o.p,o.dir,!!o.ray,box||bimDrawingExtent2D());
  }
  /* t is the parameter on the INFINITE line, bounded only for a ray; u is the parameter on the
     SEGMENT and is always bounded to [0,1]. */
  function bimClineSegIntersect(P,dir,isRay,A,B){
    var rx=dir[0],rz=dir[1];
    var sx=B[0]-A[0],sz=B[1]-A[1];
    var den=rx*sz-rz*sx;
    if(Math.abs(den)<1e-12)return null;
    var qpx=A[0]-P[0],qpz=A[1]-P[1];
    var t=(qpx*sz-qpz*sx)/den;
    var u=(qpx*rz-qpz*rx)/den;
    if(u<-1e-9||u>1+1e-9)return null;
    if(isRay&&t<-1e-9)return null;
    return [P[0]+rx*t,P[1]+rz*t];
  }
  function bimClineCircleHits(P,dir,isRay,C,r){
    var a=dir[0]*dir[0]+dir[1]*dir[1];
    if(a<1e-18)return [];
    var fx=P[0]-C[0],fz=P[1]-C[1];
    var b=2*(fx*dir[0]+fz*dir[1]);
    var c=fx*fx+fz*fz-r*r;
    var disc=b*b-4*a*c;
    if(disc<-1e-12)return [];
    var sq=Math.sqrt(Math.max(0,disc));
    var ts=[(-b-sq)/(2*a)],out=[],i;
    if(sq>1e-9)ts.push((-b+sq)/(2*a));
    for(i=0;i<ts.length;i++){
      if(isRay&&ts[i]<-1e-9)continue;
      out.push([P[0]+dir[0]*ts[i],P[1]+dir[1]*ts[i]]);
    }
    return out;
  }
  /* A crossing on the circle but not on the SWEPT part of the arc is not a crossing. */
  function bimClineArcIntersect(P,dir,isRay,A,B,bulge){
    var arc=bimBulgeArc(A,B,bulge);
    if(!arc){
      var s=bimClineSegIntersect(P,dir,isRay,A,B);
      return s?[s]:[];
    }
    var hits=bimClineCircleHits(P,dir,isRay,arc.center,arc.radius),out=[],i;
    for(i=0;i<hits.length;i++)
      if(bimPointOnSweptArc(arc,hits[i],1e-7))out.push(hits[i]);
    return out;
  }
  function bimClineCrossings(P,dir,isRay,pts,bulges,closed){
    if(!pts||pts.length<2||!P||!dir)return [];
    var n=pts.length,segs=closed?n:n-1,out=[],i,k,h,hs;
    for(i=0;i<segs;i++){
      var b=bimBulgeAt(bulges,i);
      if(Math.abs(b)<BIM_BULGE_EPS){
        h=bimClineSegIntersect(P,dir,isRay,pts[i],pts[(i+1)%n]);
        if(h)out.push(h);
      }else{
        hs=bimClineArcIntersect(P,dir,isRay,pts[i],pts[(i+1)%n],b);
        for(k=0;k<hs.length;k++)out.push(hs[k]);
      }
    }
    return out;
  }
  /* The construction modes, as a table. AutoCAD's XLINE also offers Bisect and Offset; this
     build implements neither, so neither is in the table and neither can reach a prompt. */
  var BIM_CLINE_MODES={
    hor:{key:'H',label:'Horizontal',dir:[1,0]},
    ver:{key:'V',label:'Vertical',dir:[0,1]},
    ang:{key:'A',label:'Angle',needsAngle:true}
  };
  var BIM_CLINE_MODE_ORDER=['hor','ver','ang'];
  function bimClineModeLabels(){
    var out=[],i,m;
    for(i=0;i<BIM_CLINE_MODE_ORDER.length;i++){
      m=BIM_CLINE_MODES[BIM_CLINE_MODE_ORDER[i]];
      if(m&&m.key)out.push(m.label);
    }
    return out;
  }
  function bimClineModeForKey(k){
    var i,name,m;
    if(!k)return null;
    for(i=0;i<BIM_CLINE_MODE_ORDER.length;i++){
      name=BIM_CLINE_MODE_ORDER[i];m=BIM_CLINE_MODES[name];
      if(m&&m.key&&m.key===String(k).toUpperCase())return name;
    }
    return null;
  }
  function bimClineDir(mode,root,second,angleDeg){
    var m=mode?BIM_CLINE_MODES[mode]:null;
    if(m&&m.dir)return [m.dir[0],m.dir[1]];
    if(m&&m.needsAngle){
      if(typeof angleDeg!=='number'||!isFinite(angleDeg))return null;
      var a=angleDeg*Math.PI/180;
      return [Math.cos(a),Math.sin(a)];
    }
    if(!root||!second)return null;
    var dx=second[0]-root[0],dz=second[1]-root[1];
    if(Math.sqrt(dx*dx+dz*dz)<1e-9)return null;
    return [dx,dz];
  }
""" + ANCHOR

assert txt.count(ANCHOR) == 1, 'anchor count %d' % txt.count(ANCHOR)
txt = txt.replace(ANCHOR, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
