import { bimBulgeArc } from './arc-storage.js';

  /* ================= __acad3dV267: constraints on a sketch's arcs =================
     FreeCAD's Sketcher (and AutoCAD's GCTANGENT, DCRADIUS, DCDIAMETER) on the app's sketches, whose arcs are bulges on
     segments: a segment from point i to point i+1 with bulge b is an arc of radius c(1 + b^2) / (4|b|) on its chord c.
     The solver (sketch-constraints.js) takes the bulge of every arc a constraint names as one more unknown, so a radius
     drives its arc as FreeCAD's does, rather than only reporting it.
       radius(a, b, r)        the arc from point a to point b has radius r
       diameter(a, b, d)      ... diameter d
       pointonarc(p, a, b)    point p lies on the circle of the arc a-b
       tangent(l0, l1, a, b)  the line through l0, l1 touches the circle of the arc a-b
     An arc is named by its two end points, in either order, as they are clicked; it is stored by its own order. */
  var BIM_CON_ARC_KINDS={radius:1,diameter:1,pointonarc:1,tangent:1};
  function bimConIsArcKind(kind){return !!BIM_CON_ARC_KINDS[kind];}
  /* The segment between two neighbouring points: its first point's index (the bulge's), or -1. Pure. */
  function bimConArcSeg(n,a,b,closed){
    if(b===a+1)return a;
    if(a===b+1)return b;
    if(closed!==false&&n>2){if(a===n-1&&b===0)return a;if(b===n-1&&a===0)return b;}
    return -1;
  }
  /* The refs of an arc constraint with its arc stored as [seg, next]. */
  function bimConArcRefs(kind,refs,n,closed){
    var k=kind==='pointonarc'?1:kind==='tangent'?2:0,s=bimConArcSeg(n,refs[k],refs[k+1],closed);
    if(s<0)return null;
    var out=refs.slice();out[k]=s;out[k+1]=(s+1)%n;
    return out;
  }
  /* A bulge's starting value for the solver. A half circle (|b| = 1) is where the radius on a fixed chord is least, so
     its slope there is zero and the solver could not leave it; it starts a little flatter. */
  function bimConArcStart(b){return Math.abs(Math.abs(b)-1)<1e-3?b*0.97:b;}
  /* The segment a constraint's arc is on. */
  function bimConArcOf(c){var k=c.type==='pointonarc'?1:c.type==='tangent'?2:0;return c.refs[k];}
  function bimConArcResidual(kind,pts,refs,value,B){
    var k=kind==='pointonarc'?1:kind==='tangent'?2:0,a=refs[k],b=refs[k+1];
    var arc=bimBulgeArc(pts[a],pts[b],B?B[a]:0);
    if(!arc)return [1e3];   /* a straight segment has no circle: far from any answer */
    if(kind==='radius')return [arc.radius-value];
    if(kind==='diameter')return [2*arc.radius-value];
    if(kind==='pointonarc'){var p=pts[refs[0]];return [Math.sqrt((p[0]-arc.center[0])*(p[0]-arc.center[0])+(p[1]-arc.center[1])*(p[1]-arc.center[1]))-arc.radius];}
    var A=pts[refs[0]],L=pts[refs[1]],dx=L[0]-A[0],dz=L[1]-A[1],len=Math.sqrt(dx*dx+dz*dz)||1e-9;
    var dist=Math.abs((arc.center[0]-A[0])*dz-(arc.center[1]-A[1])*dx)/len;
    return [dist-arc.radius];
  }
export { bimConArcOf, bimConArcRefs, bimConArcResidual, bimConArcStart, bimConIsArcKind };
