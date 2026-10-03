"""patch_phase139a.py -- V139 (LOD-A): buildings by their parts, labelled LODs, valid solids.

- CONTEXT also reads OSM's building:part (Simple 3D Buildings). A building outline with parts inside
  it is not extruded; each part is, from its min_height (or building:min_level x 3 m) to its height:
  LOD1.3. A building with no parts stays one block at one height: LOD1.2.
- Every context building says its LOD and how it was made.
- bimSolidCheck: a mesh checked as val3dity checks a solid (its rules, ISO 19107; not its code):
  faces with too few points or no area, non-planar faces, an open shell, non-manifold edges, faces
  turned the wrong way, more than one piece, a shell turned inside out. Codes are val3dity's.
- Parts stand on the lowest ground under their whole building (V137), so they do not step."""
NAME = 'patch_phase139a.py'
BASE = 'f2a259d2af039f63c7e5a2b76a27dc8bdd4ef705968db59615739bdfb1476aa5'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the query: building parts too ----
rep("""    if(k.buildings)q.push('way["building"]'+b+';','relation["building"]["type"="multipolygon"]'+b+';');""",
    """    if(k.buildings)q.push('way["building"]'+b+';','relation["building"]["type"="multipolygon"]'+b+';',
      'way["building:part"]'+b+';','relation["building:part"]["type"="multipolygon"]'+b+';');   /* __acad3dV139: LOD1.3 */""")
rep("""    if(t.building&&t.building!=='no')return 'buildings';
    if(t.highway)return 'roads';""", """    if(t.building&&t.building!=='no')return 'buildings';
    if(t['building:part']&&t['building:part']!=='no')return 'buildings';   /* __acad3dV139: a part */
    if(t.highway)return 'roads';""")
rep("""      f={kind:kind,osm:el.type,id:el.id,tags:el.tags||{},outer:[],inner:[],line:null,point:null};""",
    """      f={kind:kind,osm:el.type,id:el.id,tags:el.tags||{},outer:[],inner:[],line:null,point:null};
      if(kind==='buildings'&&!(f.tags.building&&f.tags.building!=='no'))f.part=true;   /* __acad3dV139 */""")

# ---- placing: parts inside their building, each from its base to its top ----
rep("""    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();
    pushUndo();
    undoSuspend=true;
    try{
      /* what this fetch brings replaces what an earlier one brought, kind by kind */""",
    """    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();
    var pinfo=feats?bimCtxPairParts(feats):{of:{},has:{}},nParts=0,nWhole=0,lowParts=0;   /* __acad3dV139 */
    pushUndo();
    undoSuspend=true;
    try{
      /* what this fetch brings replaces what an earlier one brought, kind by kind */""")
rep("""        if(f.kind==='buildings'){
          var hh=bimOsmHeight(f.tags);
          for(j=0;j<f.outer.length;j++){
            var Pp=sketchCCW(f.outer[j]),mesh=null;
            if(Pp.length<3)continue;
            try{mesh=padMesh(Pp,y0,hh.h);}catch(eM){mesh=null;}
            if(!mesh)continue;""", """        if(f.kind==='buildings'){
          var hh=bimOsmHeight(f.tags),rg=f.part?bimOsmPartRange(f.tags):{min:0,minFrom:'',h:hh.h,from:hh.from};   /* __acad3dV139 */
          if(!f.part&&pinfo.has[i]){nWhole++;continue;}   /* its parts stand for it */
          if(f.part&&rg.h-rg.min<0.01){lowParts++;continue;}
          for(j=0;j<f.outer.length;j++){
            var Pp=sketchCCW(f.outer[j]),mesh=null;
            if(Pp.length<3)continue;
            try{mesh=padMesh(Pp,y0+rg.min,rg.h-rg.min);}catch(eM){mesh=null;}
            if(!mesh)continue;""")
rep("""            c=rec('buildings',f);c.height=Math.round(hh.h*100)/100;c.heightFrom=hh.from;c.footprint=Pp;
            c.ground=ground([cx/Pp.length,cz/Pp.length]);""", """            c=rec('buildings',f);c.height=Math.round(hh.h*100)/100;c.heightFrom=hh.from;c.footprint=Pp;
            c.ground=ground([cx/Pp.length,cz/Pp.length]);
            c.lod=f.part?'1.3':'1.2';   /* __acad3dV139 */
            if(f.part){
              nParts++;c.buildingPart=true;
              if(rg.min>0){c.minHeight=Math.round(rg.min*100)/100;c.minFrom=rg.minFrom;}
              var pw=pinfo.of[i+'_'+j];
              if(pw){
                var pf=feats[pw.f];
                c.building={osm:pf.osm,id:pf.id,name:String(pf.tags.name||'').slice(0,60)};
                c.standFp=sketchCCW(pf.outer[pw.r]);
                if(!f.tags.name)o.name=String((pf.tags.name||('Building '+pf.osm+' '+pf.id))+' part').slice(0,60);
              }
            }""")
rep("""      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null};""",
    """      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null};
      if(nParts)A3D.site.context.last.parts=nParts;   /* __acad3dV139 */""")
rep("""      (yards?'; '+yards+' courtyard'+(yards===1?'':'s')+' filled':'')+(trunc?'; stopped at '+BIM_CTX_MAX_FEATURES+' features':'')+""",
    """      (yards?'; '+yards+' courtyard'+(yards===1?'':'s')+' filled':'')+(trunc?'; stopped at '+BIM_CTX_MAX_FEATURES+' features':'')+
      (nParts?'; '+nParts+' building part'+(nParts===1?'':'s')+' at their own heights (LOD1.3)':'')+   /* __acad3dV139 */
      (lowParts?'; '+lowParts+' part'+(lowParts===1?'':'s')+' with no height above '+(lowParts===1?'its':'their')+' base left out':'')+""")
rep("""    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards};
  }""", """    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards,parts:nParts,wholes:nWhole,lowParts:lowParts};
  }""")
# V137: parts stand where their building stands
rep("""        fp=o.context.footprint||[];h=null;""", """        fp=o.context.standFp||o.context.footprint||[];h=null;   /* __acad3dV139: a part, on its building's ground */""")

ENGINE = r"""  /* ================= __acad3dV139: LOD1.3 from building parts, and valid solids =================
     OSM's Simple 3D Buildings: a building's outline, and parts inside it each with its own height and
     min_height. Where parts are, the outline is not extruded: the parts are (LOD1.3, Biljecki's
     refined LODs). The checks are val3dity's rules for a solid (ISO 19107), written here. */
  /* a length tag in metres: "12.5", "12.5 m", "40 ft"; null when it does not read */
  function bimOsmMetres(s){
    var m=/^\s*(-?[0-9]*\.?[0-9]+)\s*(m|metres|meters|ft|feet|')?\s*$/i.exec(String(s==null?'':s).replace(/,/g,'.')),v;
    if(!m)return null;
    v=parseFloat(m[1]);
    if(m[2]&&/^(ft|feet|')$/i.test(m[2]))v*=0.3048;
    return isFinite(v)?v:null;
  }
  /* a part's base and top: min_height (or building:min_level x 3 m) to its height */
  function bimOsmPartRange(t){
    t=t||{};
    var top=bimOsmHeight(t),mn=bimOsmMetres(t.min_height),from='min_height',L;
    if(mn===null||mn<0||mn>=1000){
      mn=null;L=parseFloat(t['building:min_level']);
      if(isFinite(L)&&L>0&&L<300){mn=L*BIM_CTX_LEVEL_H;from='levels';}
    }
    if(mn===null){mn=0;from='';}
    return {min:mn,minFrom:from,h:top.h,from:top.from};
  }
  /* a point well inside a ring: the middle of its largest ear */
  function bimRingInside(P){
    var tr=earClip(P),best=null,ba=-1,i,a,b,c,ar;
    for(i=0;i<tr.length;i++){
      a=P[tr[i][0]];b=P[tr[i][1]];c=P[tr[i][2]];
      ar=Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]));
      if(ar>ba){ba=ar;best=[(a[0]+b[0]+c[0])/3,(a[1]+b[1]+c[1])/3];}
    }
    return best||P[0];
  }
  /* each part ring's building: the smallest building outline its inside point is in */
  function bimCtxPairParts(feats){
    var of={},has={},i,j,k,r,ip,best,ba,ar;
    for(i=0;i<feats.length;i++){
      if(feats[i].kind!=='buildings'||!feats[i].part)continue;
      for(j=0;j<feats[i].outer.length;j++){
        if(feats[i].outer[j].length<3)continue;
        ip=bimRingInside(sketchCCW(feats[i].outer[j]));best=null;ba=Infinity;
        for(k=0;k<feats.length;k++){
          if(feats[k].kind!=='buildings'||feats[k].part)continue;
          for(r=0;r<feats[k].outer.length;r++){
            if(feats[k].outer[r].length<3||!bimPointInPoly(ip,feats[k].outer[r]))continue;
            ar=bimPolyArea(feats[k].outer[r]);
            if(ar<ba){ba=ar;best={f:k,r:r};}
          }
        }
        if(best){of[i+'_'+j]=best;has[best.f]=1;}
      }
    }
    return {of:of,has:has};
  }
  /* ---- LOD: what each building is, and how it was made ---- */
  var BIM_LOD_TEXT={'0':'a footprint or roof outline, flat','1':'a block: the footprint extruded to one height',
    '1.2':'a block: the whole footprint extruded to one height','1.3':'a part of a building, extruded to its own height',
    '2':'roof shapes on walls straight up from the footprint','2.2':'roof planes, with dormers and other roof parts over about 2 m',
    '3':'the facade: openings, overhangs and roof details'};
  function bimLodText(l){
    l=String(l==null?'':l);
    return BIM_LOD_TEXT[l]||BIM_LOD_TEXT[l.charAt(0)]||'';
  }
  /* {lod, how} for a building object; null for anything else */
  function bimLodOf(o){
    if(!o)return null;
    if(o.cityjson){
      var cj=o.cityjson;
      return {lod:String(cj.lod||''),how:(cj.attributes&&cj.attributes.lodMethod)?String(cj.attributes.lodMethod):
        ('from '+(cj.file||'a CityJSON file')+(cj.crs?' ('+cj.crs+')':''))};
    }
    var c=o.context;
    if(!c||c.kind!=='buildings')return null;
    var hf=({height:'its height tag',levels:'its levels at '+BIM_CTX_LEVEL_H+' m each',assumed:'an assumed '+BIM_CTX_DEFAULT_H+' m (OSM gives no height or levels)'})[c.heightFrom]||'its height';
    if(c.buildingPart||c.lod==='1.3')
      return {lod:'1.3',how:'an OpenStreetMap building part, from '+(c.minHeight?bimDispNum(c.minHeight,2)+' m ('+(c.minFrom==='levels'?'its min level':'its min_height')+')':'the ground')+
        ' up to '+bimDispNum(c.height,2)+' m ('+hf+')'};
    return {lod:'1.2',how:'the OpenStreetMap footprint, extruded to '+bimDispNum(c.height,2)+' m ('+hf+')'};
  }
  /* ---- the solid check (val3dity's rules and error codes) ---- */
  var BIM_SOLID_TOL={snap:0.001,planar:0.01,area:1e-8};
  var BIM_SOLID_ERR={
    101:'too few points',105:'a face with no area',203:'a face that is not flat',
    301:'too few faces',302:'not closed',303:'edges shared by more than two faces',305:'more than one piece',
    307:'faces turned the wrong way',405:'turned inside out'};
  /* m: {v:[[x,y,z]], f:[[i,..]]}; o.surface: a set of surfaces, not a solid (closure not asked) */
  function bimSolidCheck(m,o){
    o=o||{};
    var T=BIM_SOLID_TOL,key={},can=[],P=[],F=[],err={},i,j,k,a,b,fc,q;
    function bad(code){err[code]=(err[code]||0)+1;}
    if(!m||!m.v||!m.f)return {valid:false,errors:[{code:301,label:BIM_SOLID_ERR[301],count:1}],faces:0,vertices:0,volume:0};
    for(i=0;i<m.v.length;i++){
      var p=m.v[i],kk=Math.round(p[0]/T.snap)+','+Math.round(p[1]/T.snap)+','+Math.round(p[2]/T.snap);
      if(!key.hasOwnProperty(kk)){key[kk]=P.length;P.push(p);}
      can.push(key[kk]);
    }
    for(i=0;i<m.f.length;i++){
      fc=[];
      for(j=0;j<m.f[i].length;j++){q=can[m.f[i][j]];if(q===undefined)continue;if(!fc.length||fc[fc.length-1]!==q)fc.push(q);}
      while(fc.length>1&&fc[0]===fc[fc.length-1])fc.pop();
      if(fc.length<3){bad(101);continue;}
      var nx=0,ny=0,nz=0,cx=0,cy=0,cz=0;
      for(j=0;j<fc.length;j++){
        a=P[fc[j]];b=P[fc[(j+1)%fc.length]];
        nx+=(a[1]-b[1])*(a[2]+b[2]);ny+=(a[2]-b[2])*(a[0]+b[0]);nz+=(a[0]-b[0])*(a[1]+b[1]);
        cx+=a[0];cy+=a[1];cz+=a[2];
      }
      var nl=Math.sqrt(nx*nx+ny*ny+nz*nz);
      if(nl/2<T.area){bad(105);continue;}
      cx/=fc.length;cy/=fc.length;cz/=fc.length;
      if(fc.length>3){
        var dm=0;
        for(j=0;j<fc.length;j++){a=P[fc[j]];dm=Math.max(dm,Math.abs((a[0]-cx)*nx+(a[1]-cy)*ny+(a[2]-cz)*nz)/nl);}
        if(dm>T.planar)bad(203);
      }
      F.push(fc);
    }
    /* edges: each undirected edge, and how many times each way */
    var E={},up={};
    for(i=0;i<F.length;i++)for(j=0;j<F[i].length;j++){
      a=F[i][j];b=F[i][(j+1)%F[i].length];
      k=a<b?a+'_'+b:b+'_'+a;
      if(!E[k])E[k]={fw:0,bw:0,faces:[]};
      if(a<b)E[k].fw++;else E[k].bw++;
      E[k].faces.push(i);
    }
    for(i=0;i<F.length;i++)up[i]=i;
    function root(x){while(up[x]!==x){up[x]=up[up[x]];x=up[x];}return x;}
    var open=0,nonman=0,wrong=0;
    for(k in E)if(E.hasOwnProperty(k)){
      var e=E[k],n=e.fw+e.bw;
      if(n===1)open++;
      else if(n>2)nonman++;
      else if(e.fw!==1)wrong++;
      for(j=1;j<e.faces.length;j++)up[root(e.faces[j])]=root(e.faces[0]);
    }
    var parts={};
    for(i=0;i<F.length;i++)parts[root(i)]=1;
    var pieces=Object.keys(parts).length,vol=0;
    for(i=0;i<F.length;i++)for(j=1;j+1<F[i].length;j++){
      a=P[F[i][0]];b=P[F[i][j]];var c=P[F[i][j+1]];
      vol+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
    }
    if(!o.surface){
      if(F.length<4)bad(301);
      if(open)err[302]=open;
      if(nonman)err[303]=nonman;
      if(wrong)err[307]=wrong;
      if(pieces>1)err[305]=pieces;
      if(!open&&!nonman&&!wrong&&F.length>=4&&vol<0)bad(405);
    }
    var list=[];
    for(k in err)if(err.hasOwnProperty(k))list.push({code:+k,label:BIM_SOLID_ERR[k],count:err[k]});
    list.sort(function(x,y){return x.code-y.code;});
    return {valid:!list.length,errors:list,faces:F.length,vertices:P.length,pieces:pieces,
      volume:Math.round(Math.abs(vol)*1000)/1000,surface:!!o.surface};
  }
  function bimSolidCheckText(r){
    if(!r)return '';
    if(r.valid)return (r.surface?'valid surfaces':'a valid solid')+': '+r.faces+' faces'+(r.surface?'':', '+bimDispNum(r.volume,1)+' m³');
    return r.errors.map(function(e){return e.label+' ('+e.code+(e.count>1?', '+e.count:'')+')';}).join('; ');
  }
  function bimObjSolidCheck(o){
    var m=meshOf(o);
    if(!m)return null;
    return bimSolidCheck(m,{surface:!!(o.cityjson&&o.cityjson.surface)});
  }
  /* the buildings this checks: context buildings and CityJSON objects */
  function bimLodBuildings(){
    return A3D.objs.filter(function(o){return !!bimLodOf(o);});
  }
  /* LODCHECK: every building's LOD and solid, in one toast; the first with a problem selected */
  function bimLodCheck(){
    var B=bimLodBuildings(),i,r,ok=0,badL=[],lods={},codes={};
    if(!B.length){a3dToast('There are no buildings to check: get them with CONTEXT, or import CityJSON');return null;}
    for(i=0;i<B.length;i++){
      var L=bimLodOf(B[i]).lod||'?';lods[L]=(lods[L]||0)+1;
      r=bimObjSolidCheck(B[i]);
      if(r&&r.valid)ok++;
      else{badL.push(B[i].id);(r?r.errors:[]).forEach(function(e){codes[e.code]=1;});}
    }
    var ls=Object.keys(lods).sort().map(function(l){return lods[l]+' LOD'+l;}).join(', ');
    if(badL.length){
      A3D.sel=badL[0];A3D.sel2=null;A3D.selSet=[badL[0]];
      refreshTree();refreshProps();paint();
    }
    a3dToast(B.length+' building'+(B.length===1?'':'s')+' ('+ls+'): '+ok+' valid'+
      (badL.length?'; '+badL.length+' with problems ('+Object.keys(codes).map(function(c){return BIM_SOLID_ERR[c]+' '+c;}).join(', ')+'), the first selected':''));
    return {buildings:B.length,valid:ok,bad:badL,lods:lods,codes:Object.keys(codes).map(Number)};
  }
"""
rep("""  /* ================= __acad3dV134: data layers =================""",
    ENGINE + """  /* ================= __acad3dV134: data layers =================""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
