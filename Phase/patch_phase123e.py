"""patch_phase123e.py -- V123: a face of an object can be taken, seen, stepped through and let go.

SketchUp pushes and pulls a face; Rhino takes one with Ctrl+Shift+click (sub-object selection) and
puts the gumball on it; AutoCAD's PRESSPULL clicks one; Revit puts a shape handle on it. This app
had no way to take a face at all: every handle acted on the whole object.

This patch is the face itself -- what a face of each kind of object is, how one is taken, what is
drawn for it -- and the next patch (123f) moves it.

1. What a face is is the OBJECT's decision, never the mesh's (bimFaceDescribe). A box's six faces
   are its Length, Width and Height, each on its own side; a cylinder's top and bottom its Height
   and its curved side its Radius (a tube's inner and outer sides, a sphere's surface likewise); a
   wall's top is its Height and the ends of an open wall its Length; a column's top its Height; a
   closed sketch is a region to be pulled into a solid; a solid made only of faces (pads, cut
   solids, imported meshes) offers every flat face bounded by edges of 25 degrees or more. A face
   whose size belongs to something else says so and where it is set: a wall's sides (thickness is
   its type's), a column's sides, a floor's faces, an asset's, a cone's side.
2. A face is taken by a double-click on it, by Ctrl+Shift+click (Rhino's gesture), or by PRESSPULL
   (PP) and a click. In a plan a click on an object's outline takes the side seen edge-on there,
   which is how a plan is worked. A closed sketch drawn on a solid's face is taken before the face
   it lies on. Tab and Shift+Tab step through the object's faces; Esc lets go, back to the object.
3. The face is drawn filled and outlined, with one arrow along its outward normal and a read-out of
   its name and size; the gizmo and the grips step aside while it is held. The outward normal of a
   face of a solid is found by the parity of a ray's crossings, not the order of its corners, which
   an imported mesh does not keep; an open mesh has no inside, and its face points at the viewer.
4. A3D.face holds only which face -- the object, the face's key, its outward normal and a point on
   it. Everything drawn is read from the object on every paint, as the gizmo's centre is (V75), and
   the face lets go by itself when the selection changes, a tool starts, or the face is gone."""
NAME = 'patch_phase123e.py'
BASE = '493a15c4b9088798510a82c5731e3f89edb4b8b3bbbcd9ab9296d91ad882b97a'
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

FACES = r"""  /* ================= __acad3dV123: FACES -- PUSH AND PULL =================

     SketchUp's Push/Pull, Rhino's sub-object gumball, AutoCAD's PRESSPULL and Revit's shape handles
     all take ONE face of an object and move it along its own normal while the object follows. What
     "follows" means is the OBJECT's decision, never the mesh's: a box stays a parametric box with one
     face moved, a wall's top is its height and its ends its length, a column's top its height, a
     closed sketch becomes a solid, and a solid made only of faces moves the face and stretches its
     neighbours. A face whose size belongs to something else -- a wall's thickness to its type -- says
     so, and where it is set, instead of moving.

     A3D.face holds only WHICH face: the object's id, the face's key, its outward normal and a point
     on it. The outline, the arrow and the size are read from the object on every call
     (bimFaceCurrent), as the gizmo reads its centre -- never kept from the moment the face was taken
     -- and the face lets go by itself when the selection changes, a tool starts, or the face is
     gone. */
  var A3D_PUSH={min:0.01,edge:7,arm:74,pick:10,crease:25,listMax:200};
  /* A primitive's faces, as its own parameters: [parameter, the parameter's sign as the face moves
     out, whether the opposite face stays put (the position then follows by half the move), the
     size's name, the size's sign as the face moves out]. A face not listed is not pushed. */
  var BIM_PUSH_PRM={
    box:{'x+':['Length',1,1,'Length',1],'x-':['Length',1,1,'Length',1],'y+':['Height',1,1,'Height',1],
         'y-':['Height',1,1,'Height',1],'z+':['Width',1,1,'Width',1],'z-':['Width',1,1,'Width',1]},
    cyl:{'y+':['Height',1,1,'Height',1],'y-':['Height',1,1,'Height',1],curved:['Radius',1,0,'Radius',1]},
    cone:{'y+':['Height',1,1,'Height',1],'y-':['Height',1,1,'Height',1]},
    tube:{'y+':['Height',1,1,'Height',1],'y-':['Height',1,1,'Height',1],outer:['OuterRadius',1,0,'Outer radius',1],
          inner:['InnerRadius',-1,0,'Inner radius',-1]},
    prism:{'y+':['Height',1,1,'Height',1],'y-':['Height',1,1,'Height',1]},
    wedge:{'y+':['Ymax',1,1,'Height',1],'y-':['Ymin',-1,1,'Height',1]},
    sphere:{sphere:['Radius',1,0,'Radius',1]}
  };
  var BIM_FACE_NAMES={'y+':'Top','y-':'Bottom','x+':'Side','x-':'Side','z+':'Side','z-':'Side',curved:'Curved side',side:'Side',
    outer:'Outer side',inner:'Inner side',sphere:'Surface',top:'Top',bottom:'Bottom',start:'Start',end:'End',
    region:'Region',solid:'Face',other:'Face'};
  function bimNormalOk(N){return !!(N&&isFinite(N[0])&&isFinite(N[1])&&isFinite(N[2])&&(N[0]*N[0]+N[1]*N[1]+N[2]*N[2])>0.5);}
  function bimFaceCentroid(pts){
    var c=[0,0,0],i;
    for(i=0;i<pts.length;i++){c[0]+=pts[i][0];c[1]+=pts[i][1];c[2]+=pts[i][2];}
    return [c[0]/pts.length,c[1]/pts.length,c[2]/pts.length];
  }
  /* What kind of thing a face belongs to -- the only question the rest of this section asks of
     the object before its face. */
  function bimFaceObjKind(o){
    if(!o)return null;
    if(o.t==='sketch')return (o.closed!==false&&o.pts&&o.pts.length>=3&&!bimIsPoint(o))?'sketch':null;
    if(o.bim){
      if(o.bim.type==='wall')return 'wall';
      if(o.bim.type==='column')return 'column';
      return 'bim';
    }
    if(o.t==='opening')return 'bim';
    if(!o.mesh&&o.prm&&TYPES[o.t])return 'prm';
    var m=meshOf(o);
    return (m&&m.f&&m.f.length)?'solid':null;
  }
  /* What follows an object: anything made from it (a room, floor, roof, hatch) or bounded by it. */
  function bimFollowersOf(id){
    return A3D.objs.filter(function(o){
      if(o.id===id)return false;
      if(bimGraphRoomSourceId(o)===id)return true;
      return !!(bimIsRegionDep(o)&&o.region&&(o.region.members||[]).indexOf(id)>=0);
    });
  }
  /* An open wall's end: the end point, the direction out of the wall there, and whether the segment
     it ends is straight. */
  function bimWallEndInfo(o,which){
    var b=o.bim;
    if(!b||b.closed||!b.centerline||b.centerline.length<2)return null;
    var cl=b.centerline,n=cl.length,q=bimObjOffset(o);
    var i0=which==='start'?0:n-1,i1=which==='start'?1:n-2,seg=which==='start'?0:n-2;
    var P=cl[i0],Q=cl[i1],dx=P[0]-Q[0],dz=P[1]-Q[1],L=Math.sqrt(dx*dx+dz*dz);
    if(L<1e-9)return null;
    return {i:i0,j:i1,seg:seg,L:L,N:[dx/L,0,dz/L],P:[P[0]+q[0],(b.baseY||0)+q[1],P[1]+q[2]],
            straight:Math.abs(bimBulgeAt(b.bulges,seg))<=BIM_BULGE_EPS};
  }
  /* a wall's end cap: upright, with every corner within the wall's thickness of the end point */
  function bimWallCapAt(o,pts,e){
    var r=(o.bim.thickness||0)+1e-3,i;
    for(i=0;i<pts.length;i++){
      var dx=pts[i][0]-e.P[0],dz=pts[i][2]-e.P[2];
      if(dx*dx+dz*dz>r*r)return false;
    }
    return true;
  }
  /* WHICH FACE a mesh face is, for its object: the key the rest of the section speaks of. */
  function bimFaceKeyOf(o,m,fi){
    var kind=bimFaceObjKind(o);
    if(kind==='solid')return 'solid';
    var pts=bimFaceWorldPts(o,m,fi),N=faceNormal(pts),c=bimFaceCentroid(pts);
    if(!bimNormalOk(N))return 'other';
    var up=Math.abs(N[1])>0.999,upright=Math.abs(N[1])<1e-3,q=bimObjOffset(o);
    if(kind==='prm'){
      /* a primitive's mesh is centred on its position */
      if(up)return c[1]>q[1]?'y+':'y-';
      if(o.t==='sphere')return 'sphere';
      if(o.t==='box'){
        if(Math.abs(N[0])>0.999)return c[0]>q[0]?'x+':'x-';
        if(Math.abs(N[2])>0.999)return c[2]>q[2]?'z+':'z-';
        return 'other';
      }
      if(upright&&(o.t==='cyl'||o.t==='tube')){
        var rx=c[0]-q[0],rz=c[2]-q[2],rl=Math.sqrt(rx*rx+rz*rz);
        if(rl>1e-9&&Math.abs(N[0]*rx+N[2]*rz)/rl>0.9){
          if(o.t==='cyl')return 'curved';
          var p=mergePrm(o.t,o.prm);
          return rl>(p.OuterRadius+p.InnerRadius)/2*SCALE?'outer':'inner';
        }
      }
      return 'other';
    }
    if(kind==='wall'){
      var b=o.bim;
      if(up)return c[1]>(b.baseY||0)+q[1]+(b.height||0)/2?'top':'bottom';
      if(upright){
        var e0=bimWallEndInfo(o,'start'),e1=bimWallEndInfo(o,'end');
        if(e0&&bimWallCapAt(o,pts,e0))return 'start';
        if(e1&&bimWallCapAt(o,pts,e1))return 'end';
      }
      return 'side';
    }
    if(kind==='column'||kind==='bim'){
      var bb=objBBox(o),mid=bb?(bb.mn[1]+bb.mx[1])/2:q[1];
      if(up)return c[1]>mid?'top':'bottom';
      return 'side';
    }
    return 'other';
  }
  function bimPrmDim(o,param){
    var p=mergePrm(o.t,o.prm);
    if(param==='Ymax'||param==='Ymin')return (p.Ymax-p.Ymin)*SCALE;
    return p[param]*SCALE;
  }
  /* A primitive face that does not push says which of its parameters it follows. */
  function bimFaceWhyPrm(o,key){
    var nm=(TYPES[o.t]&&TYPES[o.t].n)||'This shape';
    if(o.t==='cone')return 'A cone\'s side follows its two radii and its height - set them in Properties';
    if(o.t==='prism')return 'A prism\'s sides move together - set its Circumradius in Properties';
    if(o.t==='wedge')return 'A wedge\'s sloping sides follow its limits - set them in Properties';
    if(o.t==='cyl')return 'The cut face of a part cylinder follows its Angle - set it in Properties';
    if(o.t==='torus'||o.t==='ellipsoid')return 'A '+nm.toLowerCase()+' has no flat face to push - set its radii in Properties';
    return 'This face follows the '+nm.toLowerCase()+'\'s parameters - set them in Properties';
  }
  /* The parity of a ray's crossings of the object's faces, from origin along dir, skipping one face. */
  function bimRayCrossings(o,m,org,dir,skip){
    var n=0,i;
    for(i=0;i<m.f.length;i++){
      if(i===skip||!m.f[i]||m.f[i].length<3)continue;
      var pts=bimFaceWorldPts(o,m,i),Nf=faceNormal(pts);
      if(!bimNormalOk(Nf))continue;
      var dn=vdot(dir,Nf);
      if(Math.abs(dn)<1e-12)continue;
      var t=(vdot(pts[0],Nf)-vdot(org,Nf))/dn;
      if(!(t>1e-7))continue;
      if(bimPointInFace([org[0]+dir[0]*t,org[1]+dir[1]*t,org[2]+dir[2]*t],pts,Nf))n++;
    }
    return n;
  }
  /* The last mesh's edges, by the positions of their ends -- an imported mesh repeats its corners per
     face, so indices alone do not say which faces meet. */
  var A3D_TOPO={m:null,em:null,open:false};
  function bimPosKey(p){return Math.round(p[0]*1e4)+','+Math.round(p[1]*1e4)+','+Math.round(p[2]*1e4);}
  function bimEdgeKey(a,b){
    var ka=bimPosKey(a),kb=bimPosKey(b);
    if(ka===kb)return null;
    return ka<kb?ka+'|'+kb:kb+'|'+ka;
  }
  function bimMeshTopo(m){
    if(A3D_TOPO.m===m)return A3D_TOPO;
    var em={},i,k,fc,open=false;
    for(i=0;i<m.f.length;i++){
      fc=m.f[i];
      if(!fc)continue;
      for(k=0;k<fc.length;k++){
        var ek=bimEdgeKey(m.v[fc[k]],m.v[fc[(k+1)%fc.length]]);
        if(ek)(em[ek]||(em[ek]=[])).push(i);
      }
    }
    for(k in em)if(em.hasOwnProperty(k)&&em[k].length<2){open=true;break;}
    A3D_TOPO={m:m,em:em,open:open};
    return A3D_TOPO;
  }
  /* The OUTWARD normal of a solid's face. The order of a face's corners says nothing an imported
     mesh keeps, so it is found by the parity of a ray's crossings from just outside the face, on two
     slightly different rays; an open mesh has no inside, and its face points at the viewer. */
  function bimSolidOutward(o,m,fi,N,P){
    var V=camVecs(A3D.cam),toCam=A3D.flat?V.d:[V.eye[0]-P[0],V.eye[1]-P[1],V.eye[2]-P[2]];
    var facing=vdot(N,toCam)>=0?N.slice():[-N[0],-N[1],-N[2]];
    if(bimMeshTopo(m).open)return facing;
    var jit=[[0.0123,0.0071,-0.0097],[-0.0089,0.0113,0.0061]],votes=0,i;
    var org=[P[0]+N[0]*1e-4,P[1]+N[1]*1e-4,P[2]+N[2]*1e-4];
    for(i=0;i<2;i++){
      var d=vnorm([N[0]+jit[i][0],N[1]+jit[i][1],N[2]+jit[i][2]]);
      votes+=(bimRayCrossings(o,m,org,d,fi)%2===0)?1:-1;
    }
    if(votes>0)return N.slice();
    if(votes<0)return [-N[0],-N[1],-N[2]];
    return facing;
  }
  /* The flat region a solid's face belongs to: every face on its plane that meets it edge to edge. */
  function bimMeshCoplanar(o,m,s,N){
    var em=bimMeshTopo(m).em,seen={},out=[],stack=[s],k,i;
    var off=vdot(N,bimFaceWorldPts(o,m,s)[0]);
    seen[s]=1;
    while(stack.length){
      var cur=stack.pop(),fc=m.f[cur];
      out.push(cur);
      for(k=0;k<fc.length;k++){
        var nb=em[bimEdgeKey(m.v[fc[k]],m.v[fc[(k+1)%fc.length]])]||[];
        for(i=0;i<nb.length;i++){
          var j=nb[i];
          if(seen[j])continue;
          var pts=bimFaceWorldPts(o,m,j),n=faceNormal(pts);
          if(bimNormalOk(n)&&Math.abs(vdot(n,N))>0.99996&&Math.abs(vdot(N,pts[0])-off)<5e-4){seen[j]=1;stack.push(j);}
        }
      }
    }
    return out;
  }
  /* A region is part of a curved surface when a neighbour across its outline turns by less than
     A3D_PUSH.crease degrees: a facet of a tessellated cylinder is not a face to push on its own. */
  function bimRegionSmooth(o,m,fis,N){
    var em=bimMeshTopo(m).em,inR={},i,j,k,cosC=Math.cos(A3D_PUSH.crease*Math.PI/180);
    for(i=0;i<fis.length;i++)inR[fis[i]]=1;
    for(i=0;i<fis.length;i++){
      var fc=m.f[fis[i]];
      for(k=0;k<fc.length;k++){
        var nb=em[bimEdgeKey(m.v[fc[k]],m.v[fc[(k+1)%fc.length]])]||[];
        for(j=0;j<nb.length;j++){
          if(inR[nb[j]])continue;
          var n=faceNormal(bimFaceWorldPts(o,m,nb[j]));
          if(bimNormalOk(n)&&Math.abs(vdot(n,N))>cosC)return true;
        }
      }
    }
    return false;
  }
  /* the solid face on the plane (N through seed) that holds the seed, or the nearest on that plane */
  function bimSolidSeedFace(o,m,seed,N){
    var i,best=-1,bd=1e18;
    for(i=0;i<m.f.length;i++){
      if(!m.f[i]||m.f[i].length<3)continue;
      var pts=bimFaceWorldPts(o,m,i),n=faceNormal(pts);
      if(!bimNormalOk(n)||Math.abs(vdot(n,N))<0.99996)continue;
      if(Math.abs(vdot(N,pts[0])-vdot(N,seed))>5e-4)continue;
      if(bimPointInFace(seed,pts,n))return i;
      var c=bimFaceCentroid(pts),dd=(c[0]-seed[0])*(c[0]-seed[0])+(c[1]-seed[1])*(c[1]-seed[1])+(c[2]-seed[2])*(c[2]-seed[2]);
      if(dd<bd){bd=dd;best=i;}
    }
    return best;
  }
  /* WHAT A FACE IS for its object -- whether it moves, what its size is called and how big it is, its
     outward normal, and when it does not move, why. ctx is where it was taken: the point, the face
     of the mesh, its normal as found; or A3D.face itself, whose normal is already outward. */
  function bimFaceDescribe(o,key,ctx){
    ctx=ctx||{};
    var kind=bimFaceObjKind(o),f={id:o.id,key:key,kindOf:kind,ok:false,why:'',name:BIM_FACE_NAMES[key]||'Face',
      dimName:null,dim:null,N:null};
    var q=bimObjOffset(o),tn;
    if(kind==='sketch'){
      f.kind='sketch';f.N=[0,1,0];f.dimName='Height';
      var on=o.on?objById(o.on):null;
      f.on=(on&&on.t!=='sketch')?on.id:null;
      /* a pull turns the sketch into a solid and the sketch is gone -- so a sketch that a room, a
         floor or a region is made from is not pulled out from under it */
      var fol=bimFollowersOf(o.id);
      if(fol.length)f.why=fol[0].name+(fol.length>1?' and '+(fol.length-1)+' more follow':' follows')+
        ' this sketch - pulling it into a solid would take it away; copy it (Ctrl+D) and pull the copy';
      else f.ok=true;
    }else if(kind==='prm'){
      var ent=(BIM_PUSH_PRM[o.t]||{})[key];
      var AX={'y+':[0,1,0],'y-':[0,-1,0],'x+':[1,0,0],'x-':[-1,0,0],'z+':[0,0,1],'z-':[0,0,-1]};
      if(AX[key])f.N=AX[key].slice();
      else if(key==='curved'||key==='outer'||key==='inner'||key==='sphere'){
        var P=ctx.seed||ctx.P||[q[0]+1,q[1],q[2]];
        var dir=ctx.dir?ctx.dir.slice():(key==='sphere'?vnorm([P[0]-q[0],P[1]-q[1],P[2]-q[2]]):vnorm([P[0]-q[0],0,P[2]-q[2]]));
        f.dir=dir;f.hy=(ctx.hy!==undefined&&ctx.hy!==null)?ctx.hy:P[1];
        f.N=key==='inner'?[-dir[0],-dir[1],-dir[2]]:dir.slice();
      }else f.N=bimNormalOk(ctx.N)?ctx.N.slice():[0,1,0];
      if(ent){
        f.ok=true;f.kind='prm';f.param=ent[0];f.psign=ent[1];f.oneSided=!!ent[2];f.dimName=ent[3];f.dsign=ent[4];
        f.dim=bimPrmDim(o,f.param);
      }else f.why=bimFaceWhyPrm(o,key);
    }else if(kind==='wall'){
      var b=o.bim;
      tn=bimTypeNameOf(o);
      if(key==='top')f.N=[0,1,0];
      else if(key==='bottom')f.N=[0,-1,0];
      else if(key==='start'||key==='end'){f.end=bimWallEndInfo(o,key);f.N=f.end?f.end.N.slice():[1,0,0];}
      else f.N=bimNormalOk(ctx.N)?ctx.N.slice():[1,0,0];
      if(!b.centerline)f.why='An imported wall has no parametric shape to push or pull';
      else if(key==='top'){f.ok=true;f.kind='wallTop';f.dimName='Height';f.dim=b.height;}
      else if(key==='start'||key==='end'){
        if(b.closed)f.why='A closed wall has no ends';
        else if(!f.end)f.why='This end has no length to pull';
        else if(!f.end.straight)f.why='The end of a curved wall is lengthened with its grip, or LENGTHEN';
        else{f.ok=true;f.kind='wallEnd';f.dimName='Length';f.dim=bimWallLength(b.centerline,b.closed,b.bulges);}
      }
      else if(key==='bottom')f.why='A wall stands on its level - its base is not pulled';
      else f.why='A wall\'s thickness comes from its type'+(tn?' ('+tn+')':'')+' - choose another type, or Edit Type, in Properties';
    }else if(kind==='column'){
      tn=bimTypeNameOf(o);
      f.N=key==='top'?[0,1,0]:(key==='bottom'?[0,-1,0]:(bimNormalOk(ctx.N)?ctx.N.slice():[1,0,0]));
      if(key==='top'){f.ok=true;f.kind='colTop';f.dimName='Height';f.dim=o.bim.height;}
      else if(key==='bottom')f.why='A column stands on its level - its base is not pulled';
      else f.why='A column\'s width and depth come from its type'+(tn?' ('+tn+')':'')+' - choose another type, or Edit Type, in Properties';
    }else if(kind==='bim'){
      tn=bimTypeNameOf(o);
      f.N=key==='top'?[0,1,0]:(key==='bottom'?[0,-1,0]:(bimNormalOk(ctx.N)?ctx.N.slice():[1,0,0]));
      var bt=o.bim?o.bim.type:o.t;
      if(bt==='familyInstance')f.why='An asset keeps its own shape - move it, or turn it with the ring';
      else if(bt==='floor'){
        if(key==='top')f.why='A floor\'s top is its level - set the level in Properties';
        else if(key==='bottom')f.why='A floor\'s thickness comes from its type'+(tn?' ('+tn+')':'')+' - choose another type, or Edit Type, in Properties';
        else f.why='A floor\'s outline comes from what it was made from - change that, or draw the floor again';
      }
      else f.why=bimObjTypeLabel(o)+' is sized in Properties - its faces are not pushed or pulled';
    }else if(kind==='solid'){
      var m=meshOf(o);
      f.kind='solid';
      var seed=ctx.seed||ctx.P;
      if(!m||!seed||!bimNormalOk(ctx.N))return null;
      if(ctx.outward)f.N=ctx.N.slice();
      else{
        var fi=(ctx.fi!==undefined)?ctx.fi:bimSolidSeedFace(o,m,seed,ctx.N);
        if(fi<0)return null;
        f.N=bimSolidOutward(o,m,fi,ctx.N,seed);
      }
      f.seed=seed.slice();
      var sf=bimSolidSeedFace(o,m,f.seed,f.N);
      if(sf<0)return null;
      f.fis=bimMeshCoplanar(o,m,sf,f.N);
      if(bimRegionSmooth(o,m,f.fis,f.N))f.why='This face is part of a curved surface - it is not pushed on its own';
      else f.ok=true;
    }else return null;
    if(f.ok&&bimIsLocked(o)){f.ok=false;f.why=o.name+' is pinned - unpin it in Properties to change it';}
    return f;
  }
  /* The drawn face: its polygons in the world, their outline, and the point its arrow stands on. */
  function bimRegionBoundary(polys){
    var cnt={},seg={},out=[],i,k,e;
    for(i=0;i<polys.length;i++){
      var pl=polys[i];
      for(k=0;k<pl.length;k++){
        var ek=bimEdgeKey(pl[k],pl[(k+1)%pl.length]);
        if(!ek)continue;
        cnt[ek]=(cnt[ek]||0)+1;
        seg[ek]=[pl[k],pl[(k+1)%pl.length]];
      }
    }
    for(e in cnt)if(cnt.hasOwnProperty(e)&&cnt[e]===1)out.push(seg[e]);
    return out;
  }
  function bimRegionCentre(polys){
    var c=[0,0,0],wsum=0,i;
    for(i=0;i<polys.length;i++){
      var pl=polys[i],n=[0,0,0],k;
      for(k=0;k<pl.length;k++){
        var p=pl[k],q=pl[(k+1)%pl.length];
        n[0]+=(p[1]-q[1])*(p[2]+q[2]);n[1]+=(p[2]-q[2])*(p[0]+q[0]);n[2]+=(p[0]-q[0])*(p[1]+q[1]);
      }
      var a=Math.sqrt(vdot(n,n))/2||1e-12,cc=bimFaceCentroid(pl);
      c[0]+=cc[0]*a;c[1]+=cc[1]*a;c[2]+=cc[2]*a;wsum+=a;
    }
    return [c[0]/wsum,c[1]/wsum,c[2]/wsum];
  }
  function bimFaceRegion(o,f){
    var polys=[],fis=[],i,C;
    if(f.kindOf==='sketch'){
      var q=bimObjOffset(o),y=(o.y||0)+q[1];
      var ring=bimSketchOutline(o).map(function(p){return [p[0]+q[0],y,p[1]+q[2]];});
      if(ring.length<3)return null;
      polys=[ring];
      return {polys:polys,edges:bimRegionBoundary(polys),C:bimRegionCentre(polys),fis:[]};
    }
    var m=meshOf(o);
    if(!m||!m.f)return null;
    if(f.kindOf==='solid')fis=f.fis||[];
    else for(i=0;i<m.f.length;i++)if(m.f[i]&&m.f[i].length>=3&&bimFaceKeyOf(o,m,i)===f.key)fis.push(i);
    if(!fis.length)return null;
    for(i=0;i<fis.length;i++)polys.push(bimFaceWorldPts(o,m,fis[i]));
    if(f.dir&&f.kind==='prm'){
      /* a curved face's arrow stands where the face was taken, on the surface as it is now */
      var qq=bimObjOffset(o),R=f.dim;
      C=(f.key==='sphere')?[qq[0]+f.dir[0]*R,qq[1]+f.dir[1]*R,qq[2]+f.dir[2]*R]:[qq[0]+f.dir[0]*R,f.hy,qq[2]+f.dir[2]*R];
    }else C=bimRegionCentre(polys);
    return {polys:polys,edges:bimRegionBoundary(polys),C:C,fis:fis};
  }
  /* THE FACE BEING WORKED, read from the object now -- or null, and the face let go, when the
     selection has moved on, a tool is running, or the face is not there any more. */
  function bimFaceCurrent(){
    var F=A3D.face;
    if(!F)return null;
    var o=objById(F.id);
    if(!o||A3D.sel!==F.id||(A3D.selSet&&A3D.selSet.length>1)||A3D.sk||A3D.conPick||!bimLayerShown(o)){
      A3D.face=null;return null;
    }
    var f=null,region=null;
    try{
      f=bimFaceDescribe(o,F.key,F);
      region=f?bimFaceRegion(o,f):null;
    }catch(eF){console.warn('[BIM] The face being worked could not be read',eF);}
    if(!f||!region){A3D.face=null;return null;}
    return {o:o,f:f,region:region};
  }
  /* TAKING A FACE. The object is selected, the face remembered by its key, its outward normal and a
     point on it; the gizmo steps aside (bimGizmoVisible) and the grips with it. */
  function bimFaceEnter(pk){
    var o=pk.o,f=bimFaceDescribe(o,pk.key,pk);
    if(!f){a3dToast('That face could not be read');return null;}
    A3D.sel=o.id;A3D.selSet=[o.id];A3D.sel2=null;A3D.selGrid=null;
    A3D.face={id:o.id,key:pk.key,N:f.N.slice(),outward:true,
              seed:(f.seed||pk.P||null),dir:f.dir||null,hy:(f.hy!==undefined?f.hy:null),fi:pk.fi};
    if(!A3D.face.seed){var rg=bimFaceRegion(o,f);A3D.face.seed=rg?rg.C.slice():[0,0,0];}
    A3D.facePick=false;
    bimCloseGizmoMenu();
    A3D.gizHover=null;A3D.gizHoverName=null;A3D.gizHoverHint=null;
    refreshTree();paint();
    return f;
  }
  function bimFaceExit(){
    if(!A3D.face)return false;
    A3D.face=null;
    bimCloseValueBox();
    refreshProps();paint();
    return true;
  }
  /* In a plan a box's sides are seen edge-on, as its outline: a click within A3D_PUSH.edge pixels of
     one takes that side -- the way a plan is worked -- rather than the top the ray meets. */
  function bimFaceEdgeOn(x,y,best){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),r=bimScreenRay(x,y),cands=[],i,j,u,v;
    if(best&&best.sketch)return null;
    if(best){
      if(Math.abs(vdot(best.N,r.d))<0.98)return null;
      cands.push(best.o);
    }
    var so=objById(A3D.sel),sk=so?bimFaceObjKind(so):null;
    if(so&&sk&&sk!=='sketch'&&cands.indexOf(so)<0&&bimLayerShown(so))cands.push(so);
    var pick=null,pd=A3D_PUSH.edge;
    for(i=0;i<cands.length;i++){
      var o=cands[i],m=meshOf(o);
      if(!m||!m.f)continue;
      for(j=0;j<m.f.length;j++){
        if(!m.f[j]||m.f[j].length<3)continue;
        var pts=bimFaceWorldPts(o,m,j),n=faceNormal(pts);
        if(!bimNormalOk(n)||Math.abs(vdot(n,r.d))>0.02)continue;
        var sp=pts.map(function(p){return toScreen(p,V,W,H);}),a=0,b=0,dmax=-1;
        for(u=0;u<sp.length;u++)for(v=u+1;v<sp.length;v++){
          var dd=(sp[u][0]-sp[v][0])*(sp[u][0]-sp[v][0])+(sp[u][1]-sp[v][1])*(sp[u][1]-sp[v][1]);
          if(dd>dmax){dmax=dd;a=u;b=v;}
        }
        var d=bimPointSegDist(x,y,sp[a][0],sp[a][1],sp[b][0],sp[b][1]);
        if(d<pd){pd=d;pick={o:o,fi:j,t:0,P:bimFaceCentroid(pts),N:n};}
      }
    }
    return pick;
  }
  /* The face under the cursor, of anything that can be picked: the nearest solid face the cursor's
     ray meets, unless a closed sketch lies in front of it or on it -- a rectangle drawn on a box's
     top is taken before the top -- or, in a plan, an outline the cursor is on. */
  function bimFacePickAt(x,y){
    var r=bimScreenRay(x,y),best=null,i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],k=bimFaceObjKind(o);
      if(!k||k==='sketch'||!bimLayerShown(o)||!bimLayerPickable(o)||!bimObjectVisibleOnLevel(o))continue;
      var h=bimRayHitObject(o,x,y);
      if(h&&(!best||h.t<best.t))best={o:o,fi:h.fi,t:h.t,P:h.P,N:h.N};
    }
    for(i=0;i<A3D.objs.length;i++){
      var s=A3D.objs[i];
      if(bimFaceObjKind(s)!=='sketch'||!bimLayerShown(s)||!bimLayerPickable(s)||!bimObjectVisibleOnLevel(s))continue;
      if(Math.abs(r.d[1])<1e-9)continue;
      var sy=bimWorldElev(s,s.y),t=(sy-r.o[1])/r.d[1];
      if(!(t>0)||(best&&t>best.t+1e-4))continue;
      /* lying ON the solid's face, a sketch is taken first only if it was drawn on that solid: a
         floor's own outline sketch lies on the floor's top, and the floor is what is meant there */
      if(best&&!best.sketch&&Math.abs(t-best.t)<=1e-4&&s.on!==best.o.id)continue;
      var P=[r.o[0]+r.d[0]*t,sy,r.o[2]+r.d[2]*t],sq=bimObjOffset(s);
      if(!bimPointInPoly([P[0]-sq[0],P[2]-sq[2]],bimSketchOutline(s)))continue;
      best={o:s,sketch:true,t:t,P:P,N:[0,1,0]};
    }
    var eo=bimFaceEdgeOn(x,y,best);
    if(eo)best=eo;
    if(!best)return null;
    if(best.sketch)return {o:best.o,key:'region',P:best.P,N:[0,1,0]};
    return {o:best.o,fi:best.fi,key:bimFaceKeyOf(best.o,meshOf(best.o),best.fi),P:best.P,N:best.N};
  }
  /* Every face of an object that moves, in the object's own order -- what Tab steps through. */
  function bimFaceList(o){
    var kind=bimFaceObjKind(o),out=[],m,i,k;
    if(kind==='sketch')return [{o:o,key:'region',P:null,N:[0,1,0]}];
    m=meshOf(o);
    if(!kind||!m||!m.f)return out;
    if(kind==='solid'){
      var seen={};
      for(i=0;i<m.f.length&&out.length<A3D_PUSH.listMax;i++){
        if(seen[i]||!m.f[i]||m.f[i].length<3)continue;
        var pts=bimFaceWorldPts(o,m,i),n=faceNormal(pts);
        if(!bimNormalOk(n))continue;
        var fis=bimMeshCoplanar(o,m,i,n);
        for(k=0;k<fis.length;k++)seen[fis[k]]=1;
        if(bimRegionSmooth(o,m,fis,n))continue;
        out.push({o:o,fi:i,key:'solid',P:bimFaceCentroid(pts),N:n,fis:fis});
      }
      return out;
    }
    var keys={};
    for(i=0;i<m.f.length;i++){
      if(!m.f[i]||m.f[i].length<3)continue;
      var key=bimFaceKeyOf(o,m,i);
      if(keys[key])continue;
      keys[key]=1;
      var p2=bimFaceWorldPts(o,m,i),c2=bimFaceCentroid(p2),n2=faceNormal(p2);
      var d=bimFaceDescribe(o,key,{P:c2,N:n2,fi:i});
      if(d&&d.ok)out.push({o:o,fi:i,key:key,P:c2,N:n2});
    }
    return out;
  }
  function bimFaceSame(pk,cur){
    if(pk.key!==cur.f.key)return false;
    if(cur.f.kindOf!=='solid')return true;
    return !!(cur.region.fis&&cur.region.fis.indexOf(pk.fi)>=0);
  }
  function bimFaceStep(dir){
    var cur=bimFaceCurrent();
    if(!cur)return false;
    var list=bimFaceList(cur.o),at=-1,i;
    if(!list.length){a3dToast(cur.o.name+' has no face that pushes or pulls');return false;}
    for(i=0;i<list.length;i++)if(bimFaceSame(list[i],cur)){at=i;break;}
    var nx=list[at<0?(dir>0?0:list.length-1):((at+dir+list.length)%list.length)];
    bimFaceEnter(nx);
    return true;
  }
  /* The keys a held face listens to. The handler, the key claim, the status bar and the shortcut
     sheet all read this table. */
  var A3D_FACE_KEYS=[
    {act:'next',keys:['Tab'],shift:false,say:['Tab'],label:'Next face of the object'},
    {act:'prev',keys:['Tab'],shift:true,say:['Shift+Tab'],label:'Previous face'},
    {act:'back',keys:['Escape'],say:['Esc'],label:'Let go of the face, back to the whole object'}
  ];
  function bimFaceKeyFor(ev){
    var i;
    for(i=0;i<A3D_FACE_KEYS.length;i++){
      var k=A3D_FACE_KEYS[i];
      if(k.keys.indexOf(ev.key)<0)continue;
      if(k.shift!==undefined&&k.shift!==!!ev.shiftKey)continue;
      return k;
    }
    return null;
  }
  function bimFaceKeyWords(act){
    var i;
    for(i=0;i<A3D_FACE_KEYS.length;i++)if(A3D_FACE_KEYS[i].act===act)return A3D_FACE_KEYS[i].say.join(', ');
    return '';
  }
  function bimFaceKeyRun(k,ev){
    if(k.act==='next')return bimFaceStep(1);
    if(k.act==='prev')return bimFaceStep(-1);
    if(k.act==='back')return bimFaceExit();
    return false;
  }
  /* How a face is taken, for the shortcut sheet -- the gestures bimFaceDblClick, onDown and the
     PRESSPULL command read. */
  var A3D_FACE_GESTURES=[
    {say:['Double-click'],label:'Take the face under the cursor to push or pull it'},
    {say:[A3D_MODKEY+'+Shift+click'],label:'Take a face, as Rhino picks a sub-object'},
    {say:['PRESSPULL'],label:'The command: click a face to take it'}
  ];
  /* The arrow along a face's outward normal, as screen geometry: A3D_PUSH.arm pixels long, and
     dropped when the normal points at the camera -- the arrows' own rule for an axis seen end-on.
     sx, sy are pixels per world unit along it: the push drag's contract. */
  function bimFaceArrow(f,rg,V,W,H){
    var C=rg.C,N=f.N;
    var s0=toScreen(C,V,W,H),s1=toScreen([C[0]+N[0],C[1]+N[1],C[2]+N[2]],V,W,H);
    var sr=toScreen([C[0]+V.r[0],C[1]+V.r[1],C[2]+V.r[2]],V,W,H);
    var sx=s1[0]-s0[0],sy=s1[1]-s0[1],px=Math.sqrt(sx*sx+sy*sy);
    var pr=Math.sqrt((sr[0]-s0[0])*(sr[0]-s0[0])+(sr[1]-s0[1])*(sr[1]-s0[1]));
    if(!isFinite(px)||!isFinite(s0[0])||!(px>=A3D_GIZ.edgeOn*pr)||px<1e-6)return null;
    var L=A3D_PUSH.arm/px,tip=toScreen([C[0]+N[0]*L,C[1]+N[1]*L,C[2]+N[2]*L],V,W,H);
    return {x0:s0[0],y0:s0[1],x1:tip[0],y1:tip[1],sx:sx,sy:sy,len2:sx*sx+sy*sy};
  }
  /* The read-out beside the face: its name and its size, or that it does not move. */
  function bimFaceReadout(cur){
    var f=cur.f;
    if(!f.ok)return f.name.toUpperCase()+'  -  DOES NOT MOVE';
    if(f.kind==='sketch')return 'REGION  PULL IT INTO A SOLID';
    return f.name.toUpperCase()+'  '+(f.dimName&&f.dim!==null?(f.dimName.toUpperCase()+' '+bimFmtLen(f.dim)):'PUSH / PULL');
  }
  function bimDrawFaceMode(ctx,V,W,H,cur){
    A3D.faceDraw=null;
    if(!cur)return;
    var f=cur.f,rg=cur.region,ok=f.ok,i,j,scr=[];
    var gold='#ffd479',grey='#8b98a8',hot=!!(A3D.faceHover||(drag&&drag.pp));
    ctx.save();
    ctx.globalAlpha=ok?(hot?0.40:0.28):0.22;
    ctx.fillStyle=ok?gold:grey;
    for(i=0;i<rg.polys.length;i++){
      var sp=rg.polys[i].map(function(p){return toScreen(p,V,W,H);});
      scr.push(sp);
      ctx.beginPath();ctx.moveTo(sp[0][0],sp[0][1]);
      for(j=1;j<sp.length;j++)ctx.lineTo(sp[j][0],sp[j][1]);
      ctx.closePath();ctx.fill();
    }
    ctx.globalAlpha=1;
    ctx.lineWidth=2;ctx.lineJoin='round';ctx.lineCap='round';
    ctx.strokeStyle='rgba(13,17,23,0.85)';ctx.lineWidth=4;
    ctx.beginPath();
    for(i=0;i<rg.edges.length;i++){
      var ea=toScreen(rg.edges[i][0],V,W,H),eb=toScreen(rg.edges[i][1],V,W,H);
      ctx.moveTo(ea[0],ea[1]);ctx.lineTo(eb[0],eb[1]);
    }
    ctx.stroke();
    ctx.strokeStyle=ok?gold:grey;ctx.lineWidth=2;
    ctx.stroke();
    var ar=ok?bimFaceArrow(f,rg,V,W,H):null,c=toScreen(rg.C,V,W,H);
    if(ar){
      var ux=ar.x1-ar.x0,uy=ar.y1-ar.y0,L=Math.sqrt(ux*ux+uy*uy)||1,hd=A3D_GIZ.head,w=5.6;
      ux/=L;uy/=L;
      ctx.strokeStyle='rgba(13,17,23,0.85)';ctx.lineWidth=5.2;
      ctx.beginPath();ctx.moveTo(ar.x0,ar.y0);ctx.lineTo(ar.x1-ux*hd,ar.y1-uy*hd);ctx.stroke();
      ctx.strokeStyle=hot?'#fff3cf':gold;ctx.lineWidth=hot?3.6:2.8;
      ctx.beginPath();ctx.moveTo(ar.x0,ar.y0);ctx.lineTo(ar.x1-ux*hd,ar.y1-uy*hd);ctx.stroke();
      ctx.fillStyle=hot?'#fff3cf':gold;
      ctx.beginPath();ctx.moveTo(ar.x1,ar.y1);
      ctx.lineTo(ar.x1-ux*hd-uy*w,ar.y1-uy*hd+ux*w);ctx.lineTo(ar.x1-ux*hd+uy*w,ar.y1-uy*hd-ux*w);
      ctx.closePath();ctx.fill();
      ctx.beginPath();ctx.arc(ar.x0,ar.y0,4.2,0,Math.PI*2);ctx.fill();
    }else if(ok&&isFinite(c[0])){
      /* the face points at the viewer: a dot to click, where the arrow would stand */
      ctx.fillStyle=gold;ctx.strokeStyle='#0d1117';ctx.lineWidth=1.4;
      ctx.beginPath();ctx.arc(c[0],c[1],5.5,0,Math.PI*2);ctx.fill();ctx.stroke();
    }
    var txt=bimFaceReadout(cur);
    ctx.font='600 12px "Segoe UI",Inter,system-ui,sans-serif';
    var tw=ctx.measureText(txt).width,bx=(ar?ar.x1:c[0])+14,by=(ar?ar.y1:c[1])-26;
    bx=Math.max(4,Math.min(bx,W-tw-24));by=Math.max(4,Math.min(by,H-28));
    ctx.fillStyle='rgba(13,17,23,0.88)';ctx.strokeStyle=ok?gold:grey;ctx.lineWidth=1;
    ctx.beginPath();
    if(ctx.roundRect)ctx.roundRect(bx,by,tw+16,20,4);else ctx.rect(bx,by,tw+16,20);
    ctx.fill();ctx.stroke();
    ctx.fillStyle='#e6edf3';ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillText(txt,bx+8,by+10);
    ctx.restore();
    A3D.faceDraw={scr:scr,arrow:ar,c:[c[0],c[1]],text:txt};
  }
  /* What of the held face is under the cursor: its arrow (or the dot standing for it), the face, or
     nothing -- read from what the last paint drew, like every other handle. */
  function bimFaceHitAt(x,y){
    var fd=A3D.faceDraw,i;
    if(!fd||!A3D.face)return null;
    if(fd.arrow&&bimPointSegDist(x,y,fd.arrow.x0,fd.arrow.y0,fd.arrow.x1,fd.arrow.y1)<=A3D_PUSH.pick)return 'arrow';
    if(!fd.arrow&&Math.abs(x-fd.c[0])<=A3D_PUSH.pick&&Math.abs(y-fd.c[1])<=A3D_PUSH.pick)return 'arrow';
    for(i=0;i<fd.scr.length;i++)if(inPoly(x,y,fd.scr[i]))return 'face';
    return null;
  }
  /* The status bar while a face is held: what it is, what it takes, and the keys -- from the tables. */
  function bimFaceHint(cur){
    var f=cur.f,o=cur.o,what=f.name+' of '+o.name,keys=bimFaceKeyWords('next')+' for another face, '+bimFaceKeyWords('back')+' for the whole object';
    if(!f.ok)return what+': '+f.why+'.  '+keys;
    var size=(f.dimName&&f.dim!==null)?(' ('+f.dimName+' '+bimFmtLen(f.dim)+')'):'';
    return what+size+': drag the arrow or the face to push or pull it, or click it to type '+
      (f.dimName?('the '+f.dimName.toLowerCase()):'how far')+'.  '+keys;
  }
  /* Taking a face by double-click. Two clicks on a gizmo handle are two clicks on a handle, so a
     click's value box waiting to open is let go here and the face under the handle taken. */
  function bimFaceDblClick(ev){
    try{
      if(!A3D.on||A3D.sk||A3D.conPick||A3D.zoomWindow||bimSheetOnScreen()||ev.button!==0)return;
      if(A3D_CLICKBOX_T){clearTimeout(A3D_CLICKBOX_T);A3D_CLICKBOX_T=null;}
      bimCloseValueBox();
      var xy=cvXY(ev),pk=bimFacePickAt(xy[0],xy[1]);
      if(!pk)return;
      bimFaceEnter(pk);
      ev.preventDefault();
    }catch(eD){
      console.warn('[BIM] The face under the cursor could not be taken',eD);
      a3dToast('That face could not be taken - see the console');
    }
  }
  /* PRESSPULL: the next click on a face takes it, as AutoCAD's command does. */
  function bimPressPullCommand(){
    if(bimSheetOnScreen()){a3dToast('PRESSPULL works in a model view');return false;}
    if(A3D.sk)bimEndSketch();
    A3D.facePick=true;
    bimSyncStatusHint();
    a3dToast('PRESSPULL: click a face to push or pull it (Esc to cancel)');
    return true;
  }
"""

# 1. the section, before the grips
rep("""  function bimPickGrip(x,y){""", FACES + """  function bimPickGrip(x,y){""")

# 2. a face held: the gizmo and the grips step aside, and the face is drawn
rep("""    return !!(A3D.on!==false)&&!A3D.sk&&!A3D.conPick&&!A3D.sheetCapture&&!A3D.gizHidden;""",
    """    return !!(A3D.on!==false)&&!A3D.sk&&!A3D.conPick&&!A3D.sheetCapture&&!A3D.gizHidden&&
      !A3D.face;   /* __acad3dV123: a held face has its own arrow */""")
rep("""  function bimDrawGrips(ctx,V,W,H){
    A3D.grips=[];""", """  function bimDrawGrips(ctx,V,W,H){
    A3D.grips=[];
    if(A3D.face)return;   /* __acad3dV123: a held face is worked by its arrow alone */""")
rep("""    if(!capMode){
      bimDrawGrips(ctx,V,W,H);
      bimDrawGizmo(ctx,V,W,H);   // __acad3dV76: after grips, so an arm never hides a grip""",
    """    if(!capMode){
      var faceNow=bimFaceCurrent();   /* __acad3dV123: read first, so a face that has lapsed lets the gizmo back */
      bimDrawGrips(ctx,V,W,H);
      bimDrawGizmo(ctx,V,W,H);   // __acad3dV76: after grips, so an arm never hides a grip
      bimDrawFaceMode(ctx,V,W,H,faceNow);""")

# 3. taking a face with the mouse: PRESSPULL's click, and Ctrl+Shift+click
rep("""    /* __acad3dV97: GRIPS FIRST, then the gizmo. A grip is an 8-pixel point target the user""",
    """    /* __acad3dV123: PRESSPULL's click takes a face; Ctrl+Shift+click takes one at any time (Rhino's
       sub-object pick). Off every face the click is what it always was. */
    if(ev.button===0&&!A3D.sk&&!A3D.conPick&&(A3D.facePick||((ev.ctrlKey||ev.metaKey)&&ev.shiftKey))){
      var fpk=bimFacePickAt(xy[0],xy[1]);
      if(fpk){bimFaceEnter(fpk);ev.preventDefault();return;}
      if(A3D.facePick){
        A3D.facePick=false;bimSyncStatusHint();
        a3dToast('No face there - PRESSPULL ended');
        ev.preventDefault();return;
      }
    }
    /* __acad3dV97: GRIPS FIRST, then the gizmo. A grip is an 8-pixel point target the user""")

# 4. the double-click, and the cursor leaving the drawing clears what the status bar said of a handle
rep("""    el.cv.addEventListener('mouseleave',function(){
      if(A3D.gizHover===null||A3D.gizHover===undefined)return;
      A3D.gizHover=null;A3D.gizHoverName=null;
      paint();
    });""", """    el.cv.addEventListener('mouseleave',function(){
      if(A3D.gizHover===null||A3D.gizHover===undefined)return;
      A3D.gizHover=null;A3D.gizHoverName=null;A3D.gizHoverHint=null;   /* __acad3dV123 */
      bimSyncStatusHint();
      paint();
    });
    el.cv.addEventListener('dblclick',bimFaceDblClick);   /* __acad3dV123: take a face */""")

# 5. keys: the held face's, and Escape lets go of it (and of PRESSPULL) before anything further out
rep("""    if(el.dlg&&ev.key!=='Escape'&&!/^F\\d+$/.test(ev.key))return;""",
    """    if(el.dlg&&ev.key!=='Escape'&&!/^F\\d+$/.test(ev.key))return;
    /* __acad3dV123: a held face's keys, from A3D_FACE_KEYS (Escape is in the chain below) */
    if(A3D.face&&!drag&&!ev.ctrlKey&&!ev.metaKey&&!ev.altKey&&ev.key!=='Escape'){
      var fkey=bimFaceKeyFor(ev);
      if(fkey&&bimFaceCurrent()){bimFaceKeyRun(fkey,ev);ev.preventDefault();ev.stopImmediatePropagation();return;}
    }""")
rep("""      if(A3D.sk){bimEndSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}   /* __acad3dV100 */""",
    """      if(A3D.sk){bimEndSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}   /* __acad3dV100 */
      /* __acad3dV123: PRESSPULL waiting for its click, then a held face -- inner to the selection */
      if(A3D.facePick){A3D.facePick=false;bimSyncStatusHint();a3dToast('PRESSPULL cancelled');ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.face&&bimFaceCurrent()){bimFaceExit();ev.preventDefault();ev.stopImmediatePropagation();return;}""")
rep("""      if(bimGizmoWantsKey(ev))return true;               /* __acad3dV112 */""",
    """      if(bimGizmoWantsKey(ev))return true;               /* __acad3dV112 */
      if(A3D.face&&!drag&&!ev.ctrlKey&&!ev.metaKey&&!ev.altKey&&bimFaceKeyFor(ev)&&bimFaceCurrent())return true;   /* __acad3dV123 */""")

# 6. the command
rep("""    ['GIZMO',['GZ'],'gizmo','Show the transform gizmo, or set its alignment'],""",
    """    ['GIZMO',['GZ'],'gizmo','Show the transform gizmo, or set its alignment'],
    ['PRESSPULL',['PP','PUSHPULL'],'presspull','Push or pull a face: click the face, then drag its arrow or type'],   /* __acad3dV123 */""")
rep("""    gizmo:function(){bimGizmoCommand();},     /* __acad3dV110 */""",
    """    gizmo:function(){bimGizmoCommand();},     /* __acad3dV110 */
    presspull:function(){bimPressPullCommand();},   /* __acad3dV123 */""")

# 7. the status bar: PRESSPULL waiting, a held face, and how to take one
rep("""    /* __acad3dV123: the handle under the cursor, and what it does -- set by onHover, cleared the
       moment the cursor leaves it */""", """    /* __acad3dV123: PRESSPULL waiting for its click; a held face and what it takes */
    if(A3D.facePick)return 'PRESSPULL: click a face to push or pull it, or Esc to cancel';
    var fcur=A3D.face?bimFaceCurrent():null;
    if(fcur)return bimFaceHint(fcur);
    /* __acad3dV123: the handle under the cursor, and what it does -- set by onHover, cleared the
       moment the cursor leaves it */""")
rep("""      if(o)return o.name+'  \\u00b7  '+bimObjTypeLabel(o);""",
    """      if(o)return o.name+'  \\u00b7  '+bimObjTypeLabel(o)+
        (bimFaceObjKind(o)?'  \\u00b7  drag to move it, double-click a face to push or pull':'');   /* __acad3dV123 */""")

# 8. the shortcut sheet: how a face is taken, and its keys
rep("""    return A3D_KEYS.concat([{grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS)}]);""",
    """    return A3D_KEYS.concat([{grp:'Faces',rows:rows(A3D_FACE_GESTURES).concat(rows(A3D_FACE_KEYS))},   /* __acad3dV123 */
      {grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS)}]);""")

# 9. what a suite reads: the held face as drawn, and what the model says of faces
rep("""  window.__acad3dV112='objectsnapondrags,typedexactvalue,escapecancels,ctrldragcopies,shiftfine,movablepivot,oneenddragpath';""",
"""  window.__acad3dV112='objectsnapondrags,typedexactvalue,escapecancels,ctrldragcopies,shiftfine,movablepivot,oneenddragpath';
  /* __acad3dV123: the held face, as drawn and as the model sees it -- a suite aims at the arrow the
     user sees and checks the size the object reports */
  window.__a3dFace=function(){
    paint();
    var cur=bimFaceCurrent();
    if(!cur)return null;
    var f=cur.f,fd=A3D.faceDraw;
    return {id:cur.o.id,key:f.key,kind:f.kind||null,ok:f.ok,why:f.why,name:f.name,dimName:f.dimName,dim:f.dim,
            N:f.N.slice(),C:cur.region.C.slice(),polys:cur.region.polys.length,edges:cur.region.edges.length,
            arrow:fd&&fd.arrow?{x0:fd.arrow.x0,y0:fd.arrow.y0,x1:fd.arrow.x1,y1:fd.arrow.y1,sx:fd.arrow.sx,sy:fd.arrow.sy}:null,
            dot:fd?fd.c.slice():null,text:fd?fd.text:null,
            screen:fd?fd.scr.map(function(p){return p.map(function(q){return [q[0],q[1]];});}):null};
  };
  window.__a3dFaceList=function(id){
    var o=objById(id||A3D.sel);
    return o?bimFaceList(o).map(function(p){return p.key;}):[];
  };
  window.__a3dFacePickAt=function(x,y){var p=bimFacePickAt(x,y);return p?{id:p.o.id,key:p.key}:null;};
  window.__a3dFaceHitAt=function(x,y){paint();return bimFaceHitAt(x,y);};
  window.__a3dFaceKeys=function(){
    return A3D_FACE_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),shift:k.shift,say:k.say.slice(),label:k.label};});
  };
  window.__a3dValueBox=function(){
    if(!A3D_VALBOX)return null;
    return {label:A3D_VALBOX.label,value:A3D_VALBOX.input.value,error:A3D_VALBOX.err.textContent,
            focused:document.activeElement===A3D_VALBOX.input};
  };
  window.__a3dStatusHint=function(){return bimStatusHintText();};
  window.__a3dFacePending=function(){return {facePick:!!A3D.facePick,clickWaiting:!!A3D_CLICKBOX_T};};""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
