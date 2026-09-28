"""patch_phase124a.py -- V124: the library's store -- kinds, a starter set, thumbnails, templates.

The owner, in V123: the Assets library "can be built upon from time to time like when I go online
and collect items, obj, or import models" and is "a way to quickly drag and drop stuff"; in V119,
Assets "should be blocks templates premade for easy drag and drop into the project not an overview
of stuff".

V21's Family Library is the store this grows from: its own key (acad3dFamilyLibrary), surviving
every project. An entry now has a KIND:
  model     a mesh placed as an independent instance -- every entry stored before V124 is one
  block     a set of object records inserted as independent copies at a point (124c)
  template  a starting project (124d); its record is stored under its own key,
            acad3dTemplateV1:<id>, so one large template cannot damage the library's key
A kind is read through bimAssetKind, so an entry without one is a model and nothing stored is
rewritten.

A starter set of models is generated in code -- never stored, never deletable -- so the library is
not empty on the first day: furniture and fixtures at real sizes. bimFamilyLibraryGet resolves
them, so every placement path that takes a family id takes a starter model unchanged.

Every entry has a thumbnail: bimMeshThumb draws a mesh flat-shaded from above one corner, faces
sorted back to front, and bimRecsThumb draws a block or template's records in plan. An entry made
before V124 gets one the first time it is drawn.

Also removed: the family list refreshFamilyPanel wrote into #a3d-famrows, an element built with
display:none and never shown, with its Place and remove buttons and their click handler -- controls
no pointer could reach (law 1). The library is shown in the Project Browser and the Assets tab."""
NAME = 'patch_phase124a.py'
BASE = '9a04845a10e625c92a872ec867b345e424c5071cab12ad61b2bb443988573941'
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


# ---- 1. an entry records its kind and carries a thumbnail
rep("""  function bimFamilyLibraryAdd(fam){
    var entry={
      id:'fam-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      name:fam.name,category:fam.category||'Other',manufacturer:fam.manufacturer||'',
      mesh:bimNormalizeMeshForFamily(fam.mesh),createdAt:new Date().toISOString()
    };
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
""", """  function bimFamilyLibraryAdd(fam){
    var entry={
      id:'fam-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      kind:'model',   /* __acad3dV124 */
      name:fam.name,category:fam.category||'Other',manufacturer:fam.manufacturer||'',
      mesh:bimNormalizeMeshForFamily(fam.mesh),createdAt:new Date().toISOString()
    };
    /* __acad3dV124: the unit and the file an imported model came from, and its thumbnail */
    if(fam.unit)entry.unit=fam.unit;
    if(fam.source)entry.source=fam.source;
    entry.thumb=bimMeshThumb(entry.mesh);
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
""")

# ---- 2. removing a template removes its stored project; a starter model cannot be removed
rep("""  function bimFamilyLibraryRemove(id){
    var idx=-1,i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id){idx=i;break;}
    if(idx<0)return false;
    A3D_FAMLIB.splice(idx,1);
    bimSaveFamilyLibrary();
    return true;
  }
  function bimFamilyLibraryGet(id){
    var i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id)return A3D_FAMLIB[i];
    return null;
  }
""", """  function bimFamilyLibraryRemove(id){
    var idx=-1,i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id){idx=i;break;}
    if(idx<0)return false;
    /* __acad3dV124: a template's project is stored under its own key, and goes with it */
    if(bimAssetKind(A3D_FAMLIB[idx])==='template'){
      try{localStorage.removeItem(A3D_TEMPLATE_PREFIX+id);}
      catch(eR){console.warn('[BIM] A template\\'s stored project could not be removed.',eR);}
    }
    A3D_FAMLIB.splice(idx,1);
    bimSaveFamilyLibrary();
    return true;
  }
  function bimFamilyLibraryGet(id){
    var i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id)return A3D_FAMLIB[i];
    /* __acad3dV124: the starter set resolves through the same lookup, so every placement path
       takes it unchanged */
    for(i=0;i<A3D_ASSET_BUILTINS.length;i++)if(A3D_ASSET_BUILTINS[i].id===id)return A3D_ASSET_BUILTINS[i];
    return null;
  }
  /* ================= __acad3dV124: the Assets library =================
     One store, three kinds: a MODEL is a mesh placed as an independent instance (every entry
     written before V124 is one), a BLOCK is a set of object records inserted as independent copies,
     a TEMPLATE is a starting project. The kind is read here and nowhere else, so an entry without
     one is a model and nothing already stored has to be rewritten. */
  var A3D_TEMPLATE_PREFIX='acad3dTemplateV1:';
  function bimAssetKind(e){
    var k=e&&e.kind;
    return (k==='block'||k==='template')?k:'model';
  }
  /* the user's entries of one kind, in the library's own order */
  function bimLibEntries(kind){
    var out=[],i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(bimAssetKind(A3D_FAMLIB[i])===kind)out.push(A3D_FAMLIB[i]);
    return out;
  }
  /* A mesh made of parts, each a box [cx,cy,cz,lx,ly,lz] or a cylinder {cyl:[cx,cy,cz,r,h]}, with
     its centre given in metres and its base on y=0 once it is normalised. */
  function bimAsmMesh(parts){
    var meshes=[],i,j;
    for(i=0;i<parts.length;i++){
      var p=parts[i],m,c;
      if(p.cyl){m=mkCylP(p.cyl[3],p.cyl[4],360,20);c=[p.cyl[0],p.cyl[1],p.cyl[2]];}
      else{m=mkBoxP(p[3],p[4],p[5]);c=[p[0],p[1],p[2]];}
      var mv=[];
      for(j=0;j<m.v.length;j++)mv.push([m.v[j][0]+c[0],m.v[j][1]+c[1],m.v[j][2]+c[2]]);
      meshes.push({v:mv,f:m.f});
    }
    return bimMergeMeshes(meshes);
  }
  /* The starter set: real sizes, in metres. Front is +Z. */
  var A3D_ASSET_STARTER=[
    {k:'chair',name:'Chair',cat:'Furniture',parts:[[-0.2,0.225,0.2,0.04,0.45,0.04],[0.2,0.225,0.2,0.04,0.45,0.04],
      [-0.2,0.225,-0.2,0.04,0.45,0.04],[0.2,0.225,-0.2,0.04,0.45,0.04],[0,0.47,0,0.45,0.05,0.45],
      [0,0.72,-0.205,0.45,0.45,0.04]]},
    {k:'table',name:'Dining table',cat:'Furniture',parts:[[0,0.73,0,1.6,0.04,0.9],[-0.74,0.355,-0.39,0.06,0.71,0.06],
      [0.74,0.355,-0.39,0.06,0.71,0.06],[-0.74,0.355,0.39,0.06,0.71,0.06],[0.74,0.355,0.39,0.06,0.71,0.06]]},
    {k:'desk',name:'Desk',cat:'Furniture',parts:[[0,0.73,0,1.4,0.04,0.7],[-0.68,0.355,0,0.04,0.71,0.66],
      [0.68,0.355,0,0.04,0.71,0.66],[0,0.45,-0.3,1.32,0.4,0.02]]},
    {k:'bed',name:'Double bed',cat:'Furniture',parts:[[0,0.175,0.03,1.6,0.35,2.04],[0,0.45,0.05,1.5,0.2,1.95],
      [0,0.45,-1.02,1.6,0.9,0.06]]},
    {k:'sofa',name:'Sofa',cat:'Furniture',parts:[[0,0.2,0.05,1.6,0.4,0.8],[0,0.625,-0.35,2.0,0.45,0.2],
      [-0.9,0.325,0.05,0.2,0.65,0.8],[0.9,0.325,0.05,0.2,0.65,0.8]]},
    {k:'cabinet',name:'Base cabinet',cat:'Furniture',parts:[[0,0.43,0,0.6,0.86,0.58],[0,0.88,0.01,0.62,0.04,0.6]]},
    {k:'wc',name:'WC',cat:'Fixtures',parts:[{cyl:[0,0.2,0.12,0.19,0.4]},[0,0.575,-0.17,0.4,0.35,0.18]]},
    {k:'basin',name:'Basin',cat:'Fixtures',parts:[{cyl:[0,0.35,0,0.08,0.7]},[0,0.78,0.05,0.55,0.16,0.45]]},
    {k:'bath',name:'Bathtub',cat:'Fixtures',parts:[[0,0.275,0,1.7,0.55,0.75]]}
  ];
  var A3D_ASSET_BUILTINS=A3D_ASSET_STARTER.map(function(s){
    return {id:'builtin:'+s.k,kind:'model',builtin:true,name:s.name,category:s.cat,manufacturer:'',
      mesh:bimNormalizeMeshForFamily(bimAsmMesh(s.parts)),thumb:''};
  });
  /* A mesh drawn from above one corner, flat-shaded, back faces first: what the thing looks like.
     No face is culled, so a mesh whose faces run either way round still draws whole. */
  function bimMeshThumb(mesh,w,h){
    w=w||96;h=h||72;
    try{
      if(!mesh||!mesh.v||!mesh.v.length||!mesh.f||!mesh.f.length)return '';
      var c=document.createElement('canvas');c.width=w;c.height=h;
      var g=c.getContext('2d');if(!g)return '';
      var S2=Math.SQRT2,S6=Math.sqrt(6),i,k;
      var P=mesh.v.map(function(v){return [(v[0]-v[2])/S2,-(2*v[1]-v[0]-v[2])/S6];});
      var mnx=Infinity,mny=Infinity,mxx=-Infinity,mxy=-Infinity;
      for(i=0;i<P.length;i++){
        if(P[i][0]<mnx)mnx=P[i][0];if(P[i][0]>mxx)mxx=P[i][0];
        if(P[i][1]<mny)mny=P[i][1];if(P[i][1]>mxy)mxy=P[i][1];
      }
      var pad=6,sc=Math.min((w-2*pad)/Math.max(mxx-mnx,1e-9),(h-2*pad)/Math.max(mxy-mny,1e-9));
      var ox=(w-(mxx-mnx)*sc)/2-mnx*sc,oy=(h-(mxy-mny)*sc)/2-mny*sc;
      var L=[0.36,0.84,0.4],faces=[];
      for(i=0;i<mesh.f.length;i++){
        var f=mesh.f[i];if(!f||f.length<3)continue;
        var n=[0,0,0],d=0;
        for(k=0;k<f.length;k++){
          var a=mesh.v[f[k]],b=mesh.v[f[(k+1)%f.length]];
          if(!a||!b){n=null;break;}
          n[0]+=(a[1]-b[1])*(a[2]+b[2]);n[1]+=(a[2]-b[2])*(a[0]+b[0]);n[2]+=(a[0]-b[0])*(a[1]+b[1]);
          d+=a[0]+a[1]+a[2];
        }
        if(!n)continue;
        var nl=Math.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])||1;
        faces.push({f:f,d:d/f.length,l:Math.abs(n[0]*L[0]+n[1]*L[1]+n[2]*L[2])/nl});
      }
      faces.sort(function(p,q){return p.d-q.d;});
      g.lineWidth=0.6;g.strokeStyle='rgba(20,28,40,.55)';
      for(i=0;i<faces.length;i++){
        var ff=faces[i].f,sh=Math.round(95+faces[i].l*120);
        g.fillStyle='rgb('+Math.round(sh*0.82)+','+Math.round(sh*0.9)+','+sh+')';
        g.beginPath();
        for(k=0;k<ff.length;k++){
          var q=P[ff[k]];
          if(k)g.lineTo(ox+q[0]*sc,oy+q[1]*sc);else g.moveTo(ox+q[0]*sc,oy+q[1]*sc);
        }
        g.closePath();g.fill();
        if(faces.length<4000)g.stroke();
      }
      return c.toDataURL('image/png');
    }catch(eT){console.warn('[BIM] A thumbnail could not be drawn.',eT);return '';}
  }
  /* The plan lines of a set of object records: outlines, centrelines, profiles and the top view of
     every mesh, each in world plan coordinates (x, z). */
  function bimRecsPlanLines(recs){
    var out=[],i,j,k;
    function add(pts,close,off){
      if(!pts||pts.length<2)return;
      var ln=[];
      for(k=0;k<pts.length;k++){var p=pts[k];if(p&&isFinite(p[0])&&isFinite(p[1]))ln.push([p[0]+off[0],p[1]+off[1]]);}
      if(close&&ln.length>2)ln.push(ln[0]);
      if(ln.length>1)out.push(ln);
    }
    for(i=0;i<(recs||[]).length;i++){
      var r=recs[i];if(!r)continue;
      var q=r.pos||[0,0,0],off=[q[0]||0,q[2]||0];
      if(r.mesh&&r.mesh.f&&r.mesh.v){
        for(j=0;j<r.mesh.f.length&&j<3000;j++){
          var f=r.mesh.f[j],pl=[];
          for(k=0;k<f.length;k++){var v=r.mesh.v[f[k]];if(v)pl.push([v[0],v[2]]);}
          add(pl,true,off);
        }
      }else if(r.pts){add(r.pts,r.t==='room'||r.closed,off);}
      else if(r.t==='dim'&&r.p1&&r.p2){add([r.p1,r.d1||r.p1,r.d2||r.p2,r.p2],false,off);}
      else if(r.t==='text'&&r.pt){add([[r.pt[0]-0.3,r.pt[1]],[r.pt[0]+0.3,r.pt[1]]],false,off);}
    }
    return out;
  }
  function bimRecsThumb(recs,w,h){
    w=w||96;h=h||72;
    try{
      var L=bimRecsPlanLines(recs),i,k;
      if(!L.length)return '';
      var c=document.createElement('canvas');c.width=w;c.height=h;
      var g=c.getContext('2d');if(!g)return '';
      var mnx=Infinity,mnz=Infinity,mxx=-Infinity,mxz=-Infinity;
      for(i=0;i<L.length;i++)for(k=0;k<L[i].length;k++){
        var p=L[i][k];
        if(p[0]<mnx)mnx=p[0];if(p[0]>mxx)mxx=p[0];if(p[1]<mnz)mnz=p[1];if(p[1]>mxz)mxz=p[1];
      }
      var pad=6,sc=Math.min((w-2*pad)/Math.max(mxx-mnx,1e-9),(h-2*pad)/Math.max(mxz-mnz,1e-9));
      var ox=(w-(mxx-mnx)*sc)/2-mnx*sc,oy=(h-(mxz-mnz)*sc)/2-mnz*sc;
      g.strokeStyle='#c9d6e6';g.lineWidth=1;g.lineJoin='round';
      for(i=0;i<L.length;i++){
        g.beginPath();
        for(k=0;k<L[i].length;k++){
          var x=ox+L[i][k][0]*sc,y=oy+L[i][k][1]*sc;
          if(k)g.lineTo(x,y);else g.moveTo(x,y);
        }
        g.stroke();
      }
      return c.toDataURL('image/png');
    }catch(eT){console.warn('[BIM] A thumbnail could not be drawn.',eT);return '';}
  }
  /* An entry's thumbnail, made the first time it is asked for when the entry has none -- every
     entry stored before V124, and the starter set -- and kept, so it is drawn once. */
  function bimAssetThumb(e){
    if(!e)return '';
    if(typeof e.thumb==='string'&&e.thumb)return e.thumb;
    var kd=bimAssetKind(e),th='';
    if(kd==='model')th=bimMeshThumb(e.mesh);
    else if(kd==='block')th=bimRecsThumb(e.recs);
    e.thumb=th;
    if(th&&!e.builtin)bimSaveFamilyLibrary();
    return th;
  }
""")

# ---- 3. the Project Browser's Families are the library's models
rep("""    var byCat={};
    for(i=0;i<A3D_FAMLIB.length;i++){
      var f=A3D_FAMLIB[i];
      if(!byCat[f.category])byCat[f.category]=[];
      byCat[f.category].push(f);
    }
    h+=bimBrowserGroup('families','Families',A3D_FAMLIB.length,0);
""", """    var byCat={},libModels=bimLibEntries('model');   /* __acad3dV124: blocks and templates are not families */
    for(i=0;i<libModels.length;i++){
      var f=libModels[i];
      if(!byCat[f.category])byCat[f.category]=[];
      byCat[f.category].push(f);
    }
    h+=bimBrowserGroup('families','Families',libModels.length,0);
""")

# ---- 4. the famrows list had no element to fill since its panel was retired
rep("""  function refreshFamilyPanel(){
    if(el.browser)refreshBrowser();
    if(!el.famrows)return;
    if(!A3D_FAMLIB.length){el.famrows.innerHTML='<div class="a3d-propnote">No families yet. Select an object and click Save, or Import an OBJ/STL.</div>';return;}
    var sorted=A3D_FAMLIB.slice().sort(function(a,b){
      if(a.category!==b.category)return a.category<b.category?-1:1;
      return a.name<b.name?-1:1;
    });
    var h='',i;
    for(i=0;i<sorted.length;i++){
      var f=sorted[i];
      h+='<div class="a3d-famrow" data-famid="'+f.id+'">'+
        '<div class="a3d-famcat">'+bimEsc(f.category)+'</div>'+
        '<div class="a3d-famname">'+bimEsc(f.name)+'</div>'+
        '<button class="a3d-famplace" data-famplace="'+f.id+'" title="Place an instance">Place</button>'+
        '<button class="a3d-famdel" data-famdel="'+f.id+'" title="Remove from library">\\u00d7</button>'+
      '</div>';
    }
    el.famrows.innerHTML=h;
  }
""", """  function refreshFamilyPanel(){
    /* __acad3dV124: the library shows in the Project Browser's Families and in the Assets tab.
       The list this also wrote into #a3d-famrows, an element that was never shown, is gone. */
    if(el.browser)refreshBrowser();
    refreshAssets();
  }
""")
rep("""        '<div id="a3d-famrows" style="display:none"></div>'+
""", "")
rep("""    el.famrows=root.querySelector('#a3d-famrows');
""", "")
rep("""    if(el.famrows)el.famrows.addEventListener('click',function(ev){
      var placeBtn=ev.target&&ev.target.closest?ev.target.closest('[data-famplace]'):null;
      if(placeBtn){ev.stopPropagation();startFamilyPlaceTool(placeBtn.getAttribute('data-famplace'));return;}
      var delBtn=ev.target&&ev.target.closest?ev.target.closest('[data-famdel]'):null;
      if(delBtn){
        ev.stopPropagation();
        var fid=delBtn.getAttribute('data-famdel');
        var fam=bimFamilyLibraryGet(fid);
        if(fam&&confirm('Remove "'+fam.name+'" from the Family Library? Instances already placed in the model are not affected.')){
          bimFamilyLibraryRemove(fid);
          refreshFamilyPanel();
          a3dToast('Removed from Family Library');
        }
      }
    });
""", "")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
