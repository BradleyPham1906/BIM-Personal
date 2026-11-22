import { bimPolySignedArea } from '../bim/rooms.js';

  /* ================= __acad3dV251: DXF fidelity, the entities (D7) =================
     What import-dxf.js dropped before this phase: TEXT and MTEXT, ELLIPSE, SPLINE, SOLID, and
     every block (INSERT, and DIMENSION, whose drawn lines and text AutoCAD keeps in an anonymous
     block named by its code 2). All of it is worked out here in DXF's own coordinates (x east,
     y north, angles counter-clockwise in degrees), before bimDxfToModel turns it into the model's.

     Sources: Autodesk's DXF Reference (2018), the ENTITIES section (TEXT, MTEXT, ELLIPSE, SPLINE,
     INSERT, DIMENSION, SOLID) and the BLOCKS section; MTEXT's inline codes from its "Inline codes"
     table; the B-spline evaluation is de Boor's algorithm with weights for a rational spline. */

  /* MTEXT's string without its formatting: \P is a new paragraph, braces group, \f \H \C \W \Q
     \T \A \L \O \K and their arguments go, \S a^b; stacks become a/b, \~ is a space, %%c %%d %%p
     are the diameter, degree and plus-minus signs (TEXT uses those too). */
  function dxfTextPlain(s){
    if(!s)return '';
    var t=String(s);
    t=t.replace(/\\P/g,'\n').replace(/\\~/g,' ');
    t=t.replace(/\\S([^;^#\/]*)[\^#\/]([^;]*);/g,'$1/$2');
    t=t.replace(/\\[fFHhCcWwQqTtAa][^;]*;/g,'');
    t=t.replace(/\\[LlOoKk]/g,'');
    t=t.replace(/\\\\/g,'\u0000').replace(/[{}]/g,'').replace(/\u0000/g,'\\');
    t=t.replace(/%%[cC]/g,'\u00d8').replace(/%%[dD]/g,'\u00b0').replace(/%%[pP]/g,'\u00b1').replace(/%%%/g,'%');
    return t;
  }
  /* An ELLIPSE as points: centre c, major axis end m (relative to c), minor/major ratio, from
     parameter t0 to t1 (radians; 0 to 2 pi is the whole ellipse). */
  function dxfEllipsePts(c,m,ratio,t0,t1,n){
    var a=Math.sqrt(m[0]*m[0]+m[1]*m[1]),ux=a?m[0]/a:1,uy=a?m[1]/a:0,b=a*ratio;
    if(!(t1>t0))t1+=Math.PI*2;
    var full=Math.abs(t1-t0-Math.PI*2)<1e-9,out=[],k;
    n=n||Math.max(24,Math.ceil((t1-t0)/(Math.PI*2)*72));
    for(k=0;k<=n;k++){
      if(full&&k===n)break;
      var t=t0+(t1-t0)*k/n,x=Math.cos(t)*a,y=Math.sin(t)*b;
      out.push([c[0]+x*ux-y*uy,c[1]+x*uy+y*ux]);
    }
    return {pts:out,closed:full};
  }
  /* A SPLINE as points: degree p, control points, knot vector, optional weights. Sampled
     uniformly in the parameter between the knots that bound the curve. With no usable knot
     vector the fit points are used, and failing those the control polygon. */
  function dxfSplinePts(p,ctrl,knots,weights,fit,n){
    var nc=ctrl?ctrl.length:0;
    if(!(p>=1)||nc<p+1||!knots||knots.length!==nc+p+1){
      if(fit&&fit.length>=2)return fit.map(function(q){return [q[0],q[1]];});
      return (ctrl||[]).map(function(q){return [q[0],q[1]];});
    }
    var u0=knots[p],u1=knots[nc],out=[],s,i,j,r;
    n=n||Math.max(16,nc*8);
    for(s=0;s<=n;s++){
      var u=u0+(u1-u0)*s/n;
      var k=p;
      while(k<nc-1&&u>=knots[k+1])k++;
      var d=[];
      for(j=0;j<=p;j++){
        var c=ctrl[k-p+j],w=weights&&weights.length===nc?weights[k-p+j]:1;
        d.push([c[0]*w,c[1]*w,w]);
      }
      for(r=1;r<=p;r++)for(j=p;j>=r;j--){
        i=k-p+j;
        var den=knots[i+p-r+1]-knots[i],al=den>0?(u-knots[i])/den:0;
        d[j]=[(1-al)*d[j-1][0]+al*d[j][0],(1-al)*d[j-1][1]+al*d[j][1],(1-al)*d[j-1][2]+al*d[j][2]];
      }
      out.push([d[p][0]/d[p][2],d[p][1]/d[p][2]]);
    }
    return out;
  }
  /* One entity carried through an INSERT: (p - base) scaled by sx, sy, turned by rot degrees,
     moved to the insertion point at. A mirroring insert (sx*sy < 0) reverses arcs. */
  function dxfXform(e,ins,base){
    var rr=(ins.rot||0)*Math.PI/180,cs=Math.cos(rr),sn=Math.sin(rr),sx=ins.sx||1,sy=ins.sy||1;
    var b=base||[0,0],mir=sx*sy<0;
    function P(q){
      var x=(q[0]-b[0])*sx,y=(q[1]-b[1])*sy;
      var o=[ins.at[0]+x*cs-y*sn,ins.at[1]+x*sn+y*cs];
      if(q.length>2)o.push(q[2]);
      return o;
    }
    var o={},k;
    for(k in e)if(e.hasOwnProperty(k))o[k]=e[k];
    if(ins.layer&&(e.layer==='0'||!e.layer))o.layer=ins.layer;   /* layer 0 in a block takes the insert's */
    if((e.color===null||e.color===undefined||e.color===0)&&ins.color!==null&&ins.color!==undefined)o.color=ins.color;
    if(e.p1)o.p1=P(e.p1);
    if(e.p2)o.p2=P(e.p2);
    if(e.p)o.p=P(e.p);
    if(e.pts)o.pts=e.pts.map(P);
    if(e.loops)o.loops=e.loops.map(function(l){return {flags:l.flags,pts:l.pts.map(P),bulges:l.bulges&&mir?l.bulges.map(function(v){return -(v||0);}):l.bulges};});   /* __acad3dV261 */
    if(e.type==='HATCH'&&typeof e.angle==='number')o.angle=(mir?-e.angle:e.angle)+(ins.rot||0);
    if(e.bulges&&mir)o.bulges=e.bulges.map(function(v){return -(v||0);});
    if(e.c)o.c=P(e.c);
    if(typeof e.r==='number')o.r=e.r*Math.abs(sx);
    if(e.type==='ARC'){
      var a1=e.a1,a2=e.a2;
      if(sx<0&&sy>0){a1=180-e.a2;a2=180-e.a1;}
      else if(sy<0&&sx>0){a1=-e.a2;a2=-e.a1;}
      else if(sx<0&&sy<0){a1=e.a1+180;a2=e.a2+180;}
      o.a1=a1+(ins.rot||0);o.a2=a2+(ins.rot||0);
    }
    if(e.type==='TEXT')o.rot=(e.rot||0)+(ins.rot||0);
    if(typeof e.h==='number')o.h=e.h*Math.abs(sy);
    return o;
  }
  /* Every INSERT replaced by its block's entities, nested blocks included (to a depth of 8, so a
     block that inserts itself cannot hang the import). A column or row array repeats it. */
  function dxfExpandInserts(list,blocks,depth){
    var out=[],i,j,cI,rI;
    depth=depth||0;
    for(i=0;i<list.length;i++){
      var e=list[i];
      if(e.type!=='INSERT'){out.push(e);continue;}
      var blk=blocks&&blocks[e.name];
      if(!blk||depth>8)continue;
      var inner=dxfExpandInserts(blk.ents,blocks,depth+1);
      var nc=Math.max(1,e.cols||1),nr=Math.max(1,e.rows||1);
      for(cI=0;cI<nc;cI++)for(rI=0;rI<nr;rI++){
        var rr=(e.rot||0)*Math.PI/180,ox=cI*(e.colSp||0),oy=rI*(e.rowSp||0);
        var at=[e.at[0]+ox*Math.cos(rr)-oy*Math.sin(rr),e.at[1]+ox*Math.sin(rr)+oy*Math.cos(rr)];
        var ins={at:at,sx:e.sx,sy:e.sy,rot:e.rot,layer:e.layer,color:e.color};
        for(j=0;j<inner.length;j++)out.push(dxfXform(inner[j],ins,blk.base));
      }
    }
    return out;
  }
  /* The entities this file adds, from one record's group codes, or null for a type it does not
     read. items are [code, value] pairs; num/str/all are import-dxf.js's readers. */
  function dxfEntityExtra(t,items,layer,color){
    var N=function(c,d){var i;for(i=0;i<items.length;i++)if(items[i][0]===c)return parseFloat(items[i][1]);return d;};
    var S=function(c,d){var i;for(i=0;i<items.length;i++)if(items[i][0]===c)return items[i][1];return d;};
    var A=function(c){var o=[],i;for(i=0;i<items.length;i++)if(items[i][0]===c)o.push(parseFloat(items[i][1]));return o;};
    var base={layer:layer,color:color};
    function mk(o){var k;for(k in base)if(base.hasOwnProperty(k))o[k]=base[k];return o;}
    if(t==='TEXT'||t==='ATTRIB'){
      if(t==='ATTRIB'&&(N(70,0)&1))return null;   /* an invisible attribute is not drawn */
      var tx=mk({type:'TEXT',text:dxfTextPlain(S(1,'')),p:[N(10,0),N(20,0),N(30,0)],h:N(40,0),rot:N(50,0)});
      if(t==='ATTRIB'&&S(2,''))tx.tag=S(2,'');   /* __acad3dV260: an attribute keeps its tag */
      return tx;
    }
    if(t==='MTEXT'){
      var s='',i;
      for(i=0;i<items.length;i++)if(items[i][0]===3)s+=items[i][1];
      s+=S(1,'');
      var rot=N(50,null);
      if(rot===null){var dx=N(11,null),dy=N(21,null);rot=(dx!==null&&dy!==null)?Math.atan2(dy,dx)*180/Math.PI:0;}
      return mk({type:'TEXT',text:dxfTextPlain(s),p:[N(10,0),N(20,0),N(30,0)],h:N(40,0),rot:rot});
    }
    if(t==='ELLIPSE'){
      var el=dxfEllipsePts([N(10,0),N(20,0)],[N(11,1),N(21,0)],N(40,1),N(41,0),N(42,Math.PI*2));
      return mk({type:'POLYPTS',pts:el.pts,closed:el.closed,z:N(30,0)});
    }
    if(t==='SPLINE'){
      var xs=A(10),ys=A(20),fx=A(11),fy=A(21),ctrl=[],fit=[],k;
      for(k=0;k<Math.min(xs.length,ys.length);k++)ctrl.push([xs[k],ys[k]]);
      for(k=0;k<Math.min(fx.length,fy.length);k++)fit.push([fx[k],fy[k]]);
      var pts=dxfSplinePts(N(71,3),ctrl,A(40),A(41),fit);
      return pts.length>=2?mk({type:'POLYPTS',pts:pts,closed:!!(N(70,0)&1)}):null;
    }
    if(t==='HATCH'){   /* __acad3dV261 */
      var loops=dxfHatchLoops(items);
      if(!loops.length)return null;
      var solid=N(70,0)===1||/^SOLID$/i.test(S(2,''));
      return mk({type:'HATCH',pattern:solid?'solid':dxfHatchPattern(S(2,'')),angle:N(52,0),scale:N(41,1),loops:loops});
    }
    if(t==='SOLID'||t==='TRACE'){
      /* the third and fourth corners are stored crossed: 1, 2, 4, 3 is the outline */
      var q=[[N(10,0),N(20,0)],[N(11,0),N(21,0)],[N(13,N(12,0)),N(23,N(22,0))],[N(12,0),N(22,0)]];
      if(Math.abs(q[2][0]-q[3][0])<1e-12&&Math.abs(q[2][1]-q[3][1])<1e-12)q.pop();
      return mk({type:'POLYPTS',pts:q,closed:true});
    }
    if(t==='INSERT'){
      return mk({type:'INSERT',name:S(2,''),at:[N(10,0),N(20,0)],sx:N(41,1),sy:N(42,N(41,1)),rot:N(50,0),
        cols:N(70,1),rows:N(71,1),colSp:N(44,0),rowSp:N(45,0)});
    }
    if(t==='DIMENSION'){
      /* its geometry is the anonymous block it names, already placed in world coordinates */
      var nm=S(2,'');
      return nm?mk({type:'INSERT',name:nm,at:[0,0],sx:1,sy:1,rot:0}):null;
    }
    return null;
  }
  /* ================= __acad3dV261: HATCH, read as a hatch =================
     A DXF HATCH's boundary paths (DXF Reference, HATCH, "Boundary path data"): 91 the number of paths; each starts
     with 92 (its flags: 1 external, 2 a polyline, 16 outermost); a polyline path is 72 (has bulges), 73 (closed),
     93 (vertices) and 10/20(/42) each; an edge path is 93 (edges) and each edge's 72: 1 line (10,20,11,21), 2 arc
     (10,20,40,50,51,73), 3 ellipse (10,20,11,21,40,50,51,73), 4 spline (its control points 10/20, sampled
     through their polygon). Pattern: 2 its name, 70 solid, 52 angle, 41 scale. */
  var BIM_DXF_HATCH_MAP={SOLID:'solid',ANSI31:'diagonal',ANSI32:'steel',ANSI33:'diagonal',ANSI34:'steel',ANSI35:'diagonal',
    ANSI36:'diagonal',ANSI37:'cross',ANSI38:'cross',NET:'cross','AR-BRSTD':'brick','AR-B816':'brick','AR-B88':'brick',
    BRICK:'brick','AR-CONC':'concrete','AR-SAND':'dots',DOTS:'dots',LINE:'horizontal',EARTH:'cross',STEEL:'steel'};
  function dxfHatchPattern(name){
    var n=String(name||'').toUpperCase();
    return BIM_DXF_HATCH_MAP.hasOwnProperty(n)?BIM_DXF_HATCH_MAP[n]:'diagonal';
  }
  function dxfHatchLoops(items){
    var i=0,loops=[],n;
    while(i<items.length&&items[i][0]!==91)i++;
    if(i>=items.length)return loops;
    n=parseInt(items[i][1],10)||0;i++;
    function num(){return parseFloat(items[i++][1]);}
    function seek(code){while(i<items.length&&items[i][0]!==code)i++;return i<items.length;}
    for(var L=0;L<n;L++){
      if(!seek(92))break;
      var flags=parseInt(items[i][1],10)||0;i++;
      var pts=[],bul=[];
      if(flags&2){
        var hasB=0,cnt=0;
        while(i<items.length&&items[i][0]!==10){
          if(items[i][0]===72)hasB=parseInt(items[i][1],10)||0;
          if(items[i][0]===93)cnt=parseInt(items[i][1],10)||0;
          i++;
        }
        for(var v=0;v<cnt&&i<items.length;v++){
          var x=0,y=0,b=0;
          if(items[i][0]===10)x=num();
          if(i<items.length&&items[i][0]===20)y=num();
          if(hasB&&i<items.length&&items[i][0]===42)b=num();
          pts.push([x,y]);bul.push(b);
        }
        loops.push({flags:flags,pts:pts,bulges:hasB?bul:null});
        continue;
      }
      if(!seek(93))break;
      var ne=parseInt(items[i][1],10)||0;i++;
      for(var e=0;e<ne;e++){
        if(!seek(72))break;
        var et=parseInt(items[i][1],10)||0;i++;
        var r={},seg=[];
        while(i<items.length&&items[i][0]!==72&&items[i][0]!==92&&items[i][0]!==97&&items[i][0]!==75){
          var c=items[i][0];
          if(c===10||c===20||c===11||c===21||c===40||c===50||c===51||c===73){r[c]=r[c]===undefined?parseFloat(items[i][1]):r[c];}
          if(et===4&&c===10){(r.cx=r.cx||[]).push(parseFloat(items[i][1]));}
          if(et===4&&c===20){(r.cy=r.cy||[]).push(parseFloat(items[i][1]));}
          i++;
        }
        if(et===1)seg=[[r[10],r[20]],[r[11],r[21]]];
        else if(et===2||et===3){
          var a0=(r[50]||0)*Math.PI/180,a1=(r[51]||0)*Math.PI/180,ccw=r[73]!==0,k;
          if(!ccw){a0=-a0;a1=-a1;}
          if(a1<a0&&ccw)a1+=Math.PI*2;
          if(et===2)for(k=0;k<=16;k++){var a=a0+(a1-a0)*k/16;seg.push([r[10]+Math.cos(a)*r[40],r[20]+Math.sin(a)*r[40]]);}
          else seg=dxfEllipsePts([r[10],r[20]],[r[11],r[21]],r[40],a0,a1,16).pts;
        }else if(et===4&&r.cx)for(k=0;k<Math.min(r.cx.length,r.cy.length);k++)seg.push([r.cx[k],r.cy[k]]);
        for(k=0;k<seg.length;k++){
          var last=pts[pts.length-1];
          if(!last||Math.abs(last[0]-seg[k][0])>1e-9||Math.abs(last[1]-seg[k][1])>1e-9)pts.push(seg[k]);
        }
      }
      if(pts.length>2&&Math.abs(pts[0][0]-pts[pts.length-1][0])<1e-9&&Math.abs(pts[0][1]-pts[pts.length-1][1])<1e-9)pts.pop();
      loops.push({flags:flags,pts:pts,bulges:null});
    }
    return loops.filter(function(l){return l.pts.length>=3||(l.pts.length===2&&l.bulges);});
  }
  /* The loops a hatch fills: those flagged external or outermost, else the largest; the rest are its islands. */
  function dxfHatchOuter(loops){
    var out=loops.filter(function(l){return l.flags&(1|16);});
    if(out.length)return out;
    var best=null,ba=-1,i;
    for(i=0;i<loops.length;i++){var a=Math.abs(bimPolySignedArea(loops[i].pts));if(a>ba){ba=a;best=loops[i];}}
    return best?[best]:[];
  }
export {
  dxfEllipsePts, dxfEntityExtra, dxfExpandInserts, dxfHatchOuter, dxfHatchPattern, dxfSplinePts, dxfTextPlain,
  dxfXform
};
