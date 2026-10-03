"""patch_phase139b.py -- V139 (LOD-A): CityJSON out and in.

- UTM (WGS84), forward and back, by Krueger's series to the third order (under a millimetre within
  the zone); no library.
- CITYJSONOUT: the buildings (context buildings and parts, and CityJSON objects) as CityJSON 2.0 in
  the site's UTM zone, heights above sea level when the site has a datum. Buildings with parts are a
  Building with BuildingPart children; each solid's faces typed ground, roof or wall; the LOD and how
  it was made in the attributes; OSM's credit with the data.
- CITYJSONIN: a CityJSON file's buildings (and any other city objects with surfaces) as solids on a
  CityJSON layer, the highest LOD of each; UTM files placed on the site; any other grid placed by its
  centre at model 0,0 and named; every solid checked as it comes in."""
NAME = 'patch_phase139b.py'
BASE = '1274a6c9b513c5ff6e3c16b0434540de97db2a4bc69893592503ede5c14a62a6'
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


CJ = r"""  /* ================= __acad3dV139: CityJSON =================
     CityGML's JSON form (cityjson.org, 2.0): vertices once, as integers with a scale and a translate;
     city objects with geometry by LOD; surfaces typed. Written in the site's UTM zone, so the file
     lands where the site is in any CityJSON viewer. */
  var BIM_UTM_K0=0.9996;
  function bimUtmZone(lon){return Math.max(1,Math.min(60,Math.floor((lon+180)/6)+1));}
  function bimAtanh(x){return 0.5*Math.log((1+x)/(1-x));}
  function bimCosh(x){return (Math.exp(x)+Math.exp(-x))/2;}
  /* Krueger's series (third order), WGS84 */
  function bimUtmSeries(){
    var f=1/298.257223563,n=f/(2-f),n2=n*n,n3=n2*n;
    return {A:BIM_WGS84_A/(1+n)*(1+n2/4+n2*n2/64),e:Math.sqrt(f*(2-f)),
      al:[n/2-2*n2/3+5*n3/16,13*n2/48-3*n3/5,61*n3/240],
      be:[n/2-2*n2/3+37*n3/96,n2/48+n3/15,17*n3/480],
      de:[2*n-2*n2/3-2*n3,7*n2/3-8*n3/5,56*n3/15]};
  }
  /* [easting, northing] in a zone (north, or south with its false northing) */
  function bimUtmFwd(lon,lat,zone,south){
    var S=bimUtmSeries(),l0=((zone-1)*6-180+3)*BIM_D2R,ph=lat*BIM_D2R,dl=lon*BIM_D2R-l0,j;
    var tt=bimSinh(bimAtanh(Math.sin(ph))-S.e*bimAtanh(S.e*Math.sin(ph)));
    var xi=Math.atan2(tt,Math.cos(dl)),et=bimAtanh(Math.sin(dl)/Math.sqrt(1+tt*tt)),x=et,y=xi;
    for(j=1;j<=3;j++){x+=S.al[j-1]*Math.cos(2*j*xi)*bimSinh(2*j*et);y+=S.al[j-1]*Math.sin(2*j*xi)*bimCosh(2*j*et);}
    return [500000+BIM_UTM_K0*S.A*x,(south?10000000:0)+BIM_UTM_K0*S.A*y];
  }
  /* [longitude, latitude] */
  function bimUtmInv(E,N,zone,south){
    var S=bimUtmSeries(),l0=((zone-1)*6-180+3)*BIM_D2R,xi=(N-(south?10000000:0))/(BIM_UTM_K0*S.A),et=(E-500000)/(BIM_UTM_K0*S.A),j;
    var xp=xi,ep=et;
    for(j=1;j<=3;j++){xp-=S.be[j-1]*Math.sin(2*j*xi)*bimCosh(2*j*et);ep-=S.be[j-1]*Math.cos(2*j*xi)*bimSinh(2*j*et);}
    var chi=Math.asin(Math.sin(xp)/bimCosh(ep)),ph=chi;
    for(j=1;j<=3;j++)ph+=S.de[j-1]*Math.sin(2*j*chi);
    return [(l0+Math.atan2(bimSinh(ep),Math.cos(xp)))/BIM_D2R,ph/BIM_D2R];
  }
  function bimUtmEpsg(zone,south){return (south?32700:32600)+zone;}
  /* a reference system's EPSG code, from any of the ways CityJSON writes it */
  function bimCrsEpsg(s){
    var m=/EPSG(?:\/\d+\/|::?|\/)(\d+)\s*$/i.exec(String(s||''));
    return m?+m[1]:null;
  }
  var BIM_CJ_SURF={roof:'RoofSurface',wall:'WallSurface',ground:'GroundSurface'};
  /* a face's type by its normal: up is roof, down is ground, else wall */
  function bimCjFaceType(pts){
    var n=faceNormal(pts);
    if(n[1]>0.99)return 'roof';
    if(n[1]<-0.99)return 'ground';
    return 'wall';
  }
  /* a building's faces as world polygons: a context building's from its footprint (one ground, one
     roof, a wall per edge), anything else's from its mesh */
  function bimCjFaces(o){
    var c=o.context,q=bimObjOffset(o),m=meshOf(o),i,j,F=[];
    if(!m)return F;
    if(c&&c.kind==='buildings'&&c.footprint&&c.footprint.length>=3){
      var y0=Infinity,y1=-Infinity,P=sketchCCW(c.footprint),n=P.length;
      for(i=0;i<m.v.length;i++){y0=Math.min(y0,m.v[i][1]);y1=Math.max(y1,m.v[i][1]);}
      y0+=q[1];y1+=q[1];
      F.push(P.map(function(p){return [p[0]+q[0],y0,p[1]+q[2]];}));
      F.push(P.slice().reverse().map(function(p){return [p[0]+q[0],y1,p[1]+q[2]];}));
      for(i=0;i<n;i++){
        j=(i+1)%n;
        F.push([[P[j][0]+q[0],y0,P[j][1]+q[2]],[P[i][0]+q[0],y0,P[i][1]+q[2]],[P[i][0]+q[0],y1,P[i][1]+q[2]],[P[j][0]+q[0],y1,P[j][1]+q[2]]]);
      }
      return F;
    }
    for(i=0;i<m.f.length;i++){
      if(m.f[i].length<3)continue;
      F.push(m.f[i].map(function(k){var p=m.v[k];return [p[0]+q[0],p[1]+q[1],p[2]+q[2]];}));
    }
    return F;
  }
  function bimCjAttrs(o){
    var c=o.context,L=bimLodOf(o),a={},k,n=0;
    if(o.cityjson&&o.cityjson.attributes)for(k in o.cityjson.attributes)if(o.cityjson.attributes.hasOwnProperty(k))a[k]=o.cityjson.attributes[k];
    if(o.name)a.name=o.name;
    if(c){
      for(k in c.tags)if(c.tags.hasOwnProperty(k)&&n<60){n++;a['osm:'+k]=c.tags[k];}
      a.source=c.source;a.credit=c.credit;a.osmType=c.osm;a.osmId=c.id;
      a.measuredHeight=c.height;
      if(c.minHeight)a.minHeight=c.minHeight;
      a.heightFrom=c.heightFrom;
      if(c.fetched)a.fetched=c.fetched;
    }
    if(L){a.lod=L.lod;a.lodMethod=L.how;}
    return a;
  }
  /* the CityJSON document, or {error} */
  function bimCityJsonDoc(){
    var org=bimMapOrigin();
    if(!org)return {error:'Set the site latitude and longitude first, or find an address: they put the buildings on the earth'};
    var B=bimLodBuildings();
    if(!B.length)return {error:'There are no buildings to export: get them with CONTEXT, or import CityJSON'};
    var zone=bimUtmZone(org.lon),south=org.lat<0,datum=bimCtxDatum(),V=[],VK={},CO={},ids={},i,j,k;
    var mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],faces=[];
    function vid(p){
      var g=bimModelToGeo(p[0],p[2],org),u=bimUtmFwd(g[0],g[1],zone,south),w=[u[0],u[1],p[1]+(datum===null?0:datum)];
      var r=[Math.round(w[0]*1000),Math.round(w[1]*1000),Math.round(w[2]*1000)],kk=r.join(',');
      if(!VK.hasOwnProperty(kk)){VK[kk]=V.length;V.push(r);for(var d=0;d<3;d++){mn[d]=Math.min(mn[d],r[d]);mx[d]=Math.max(mx[d],r[d]);}}
      return VK[kk];
    }
    function uid(s){s=String(s).replace(/[^A-Za-z0-9_.:-]/g,'_')||'object';var u=s,n=2;while(ids[u])u=s+'-'+(n++);ids[u]=1;return u;}
    for(i=0;i<B.length;i++){
      var o=B[i],L=bimLodOf(o),F=bimCjFaces(o),shell=[],vals=[],sur=[],si={},c=o.context,cj=o.cityjson,id,type;
      if(!F.length)continue;
      for(j=0;j<F.length;j++){
        var ft=bimCjFaceType(F[j]);
        if(!si.hasOwnProperty(ft)){si[ft]=sur.length;sur.push({type:BIM_CJ_SURF[ft]});}
        vals.push(si[ft]);
        shell.push([F[j].map(vid)]);
      }
      var surf=!!(cj&&cj.surface);
      var geom=surf?{type:'MultiSurface',lod:L.lod||'1',boundaries:shell,semantics:{surfaces:sur,values:vals}}:
        {type:'Solid',lod:L.lod||'1',boundaries:[shell],semantics:{surfaces:sur,values:[vals]}};
      type=cj?(cj.type||'Building'):(c.buildingPart?'BuildingPart':'Building');
      id=uid(cj?cj.id:('osm-'+c.osm+'-'+c.id+(c.buildingPart?'-part':'')));
      CO[id]={type:type,attributes:bimCjAttrs(o),geometry:[geom]};
      faces.push(F.length);
      /* a part's building: one Building, with the parts as its children */
      var par=null;
      if(c&&c.buildingPart&&c.building)par={key:'osm-'+c.building.osm+'-'+c.building.id,attrs:{name:c.building.name||undefined,source:c.source,credit:c.credit,osmType:c.building.osm,osmId:c.building.id}};
      /* a BuildingPart must have a Building (CityJSON's schema): a part in no outline gets one of its own */
      else if(c&&c.buildingPart)par={key:'osm-'+c.osm+'-'+c.id,attrs:{name:o.name||undefined,source:c.source,credit:c.credit,osmType:c.osm,osmId:c.id,
        note:'OpenStreetMap has this building part with no building outline around it'}};
      else if(cj&&cj.parent)par={key:String(cj.parent),attrs:cj.parentAttributes||{}};
      if(par){
        if(!CO[par.key]){ids[par.key]=1;CO[par.key]={type:cj&&cj.parentType?cj.parentType:'Building',attributes:par.attrs,children:[]};}
        if(!CO[par.key].children)CO[par.key].children=[];
        CO[par.key].children.push(id);CO[id].parents=[par.key];
        if(!cj&&CO[id].type==='Building')CO[id].type='BuildingPart';
      }
    }
    for(k in CO)if(CO.hasOwnProperty(k)&&CO[k].attributes){
      var A=CO[k].attributes,kk2;for(kk2 in A)if(A.hasOwnProperty(kk2)&&A[kk2]===undefined)delete A[kk2];
    }
    var tr=[mn[0]/1000,mn[1]/1000,mn[2]/1000];
    for(i=0;i<V.length;i++)V[i]=[V[i][0]-mn[0],V[i][1]-mn[1],V[i][2]-mn[2]];
    return {type:'CityJSON',version:'2.0',
      transform:{scale:[0.001,0.001,0.001],translate:tr},
      metadata:{title:bimFileStem()+(datum===null?' (heights from model level 0: the site has no datum)':' (heights above sea level)'),
        referenceSystem:'https://www.opengis.net/def/crs/EPSG/0/'+bimUtmEpsg(zone,south),
        geographicalExtent:[mn[0]/1000,mn[1]/1000,mn[2]/1000,mx[0]/1000,mx[1]/1000,mx[2]/1000],
        referenceDate:new Date().toISOString().slice(0,10)},
      CityObjects:CO,vertices:V};
  }
  function bimCityJsonExport(){
    var d=bimCityJsonDoc();
    if(d.error){a3dToast(d.error);return d;}
    var fn=bimFileStem()+'.city.json',n=Object.keys(d.CityObjects).length;
    try{bimTriggerDownload(JSON.stringify(d),fn,'application/city+json');}
    catch(eX){console.warn('[BIM] CityJSON export failed',eX);a3dToast('CityJSON export failed - see the console');return {error:String(eX)};}
    a3dToast('Exported '+fn+': '+n+' city object'+(n===1?'':'s')+' in UTM zone '+(bimCrsEpsg(d.metadata.referenceSystem)%100)+
      (bimCrsEpsg(d.metadata.referenceSystem)>32700?'S':'N')+' (EPSG:'+bimCrsEpsg(d.metadata.referenceSystem)+')');
    return d;
  }
  /* ---- in ---- */
  var BIM_CJ_MAX=5000,BIM_CJ_TYPES={Solid:1,MultiSolid:1,CompositeSolid:1,MultiSurface:1,CompositeSurface:1};
  function bimCjCleanAttrs(a){
    var o={},k,n=0,v;
    for(k in a)if(a&&a.hasOwnProperty(k)&&n<60){
      n++;v=a[k];
      if(v===null||typeof v==='number'||typeof v==='boolean')o[String(k).slice(0,60)]=v;
      else if(typeof v==='string')o[String(k).slice(0,60)]=v.slice(0,300);
      else{try{o[String(k).slice(0,60)]=JSON.stringify(v).slice(0,300);}catch(eS){}}
    }
    return o;
  }
  /* a face's triangles in its own plane, when it is not convex (the GL fans a face) */
  function bimCjFaceSplit(ring,W){
    if(ring.length<=3)return [ring];
    var pts=ring.map(function(k){return W[k];}),n=faceNormal(pts),ax=Math.abs(n[0]),ay=Math.abs(n[1]),az=Math.abs(n[2]),u,v,i,s=0,conv=true;
    if(ax>=ay&&ax>=az){u=1;v=2;}else if(ay>=az){u=2;v=0;}else{u=0;v=1;}
    var P2=pts.map(function(p){return [p[u],p[v]];});
    for(i=0;i<P2.length;i++){
      var a=P2[i],b=P2[(i+1)%P2.length],c=P2[(i+2)%P2.length],cr=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]);
      if(Math.abs(cr)<1e-12)continue;
      if(!s)s=cr>0?1:-1;else if((cr>0?1:-1)!==s){conv=false;break;}
    }
    if(conv)return [ring];
    /* earClip wants the ring counter-clockwise in the plane: a clockwise one is clipped reversed, and
       each triangle turned back, so the face keeps its side */
    var flip=false,ar=0,N=ring.length;
    for(i=0;i<P2.length;i++){var j=(i+1)%P2.length;ar+=P2[i][0]*P2[j][1]-P2[j][0]*P2[i][1];}
    if(ar<0){P2=P2.slice().reverse();flip=true;}
    return earClip(P2).map(function(tr){
      if(!flip)return [ring[tr[0]],ring[tr[1]],ring[tr[2]]];
      return [ring[N-1-tr[2]],ring[N-1-tr[1]],ring[N-1-tr[0]]];
    });
  }
  /* parse and place; returns {ids, ...} or {error} */
  function bimCityJsonImportText(text,name){
    name=String(name||'CityJSON');
    var d;
    try{d=JSON.parse(text);}catch(eJ){var m0=name+' is not JSON: '+(eJ&&eJ.message?eJ.message:eJ);a3dToast(m0);return {error:m0};}
    if(!d||d.type!=='CityJSON'||!d.CityObjects||!d.vertices){
      var m1=(d&&d.type==='CityJSONFeature')?name+' is CityJSON Lines (one feature per line): open the full CityJSON file':name+' is not a CityJSON file';
      a3dToast(m1);return {error:m1};
    }
    var tr=d.transform||{scale:[1,1,1],translate:[0,0,0]},sc=tr.scale||[1,1,1],tl=tr.translate||[0,0,0];
    var epsg=bimCrsEpsg(d.metadata&&d.metadata.referenceSystem),utm=null,i,j,k;
    if(epsg>32600&&epsg<=32660)utm={zone:epsg-32600,south:false};
    else if(epsg>32700&&epsg<=32760)utm={zone:epsg-32700,south:true};
    var W=[],mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity];
    for(i=0;i<d.vertices.length;i++){
      var r=d.vertices[i],w=[r[0]*sc[0]+tl[0],r[1]*sc[1]+tl[1],r[2]*sc[2]+tl[2]];
      W.push(w);
      for(k=0;k<3;k++){mn[k]=Math.min(mn[k],w[k]);mx[k]=Math.max(mx[k],w[k]);}
    }
    if(!W.length){var m2='No vertices in '+name;a3dToast(m2);return {error:m2};}
    /* each city object's highest LOD with surfaces */
    var picks=[],tmpl=0,holes=0,none=0,trunc=false,ids=Object.keys(d.CityObjects);
    for(i=0;i<ids.length;i++){
      var co=d.CityObjects[ids[i]],best=null,bl=-1;
      (co.geometry||[]).forEach(function(g){
        if(g&&g.type==='GeometryInstance'){tmpl++;return;}
        if(!g||!BIM_CJ_TYPES[g.type])return;
        var l=parseFloat(g.lod);if(!isFinite(l))l=0;
        if(l>bl){bl=l;best=g;}
      });
      if(!best){if(!(co.children&&co.children.length))none++;continue;}
      if(picks.length>=BIM_CJ_MAX){trunc=true;break;}
      picks.push({id:ids[i],co:co,g:best});
    }
    if(!picks.length){
      var m3='Nothing in '+name+' with surfaces to place'+(tmpl?' ('+tmpl+' template geometr'+(tmpl===1?'y':'ies')+' are not read)':'');
      a3dToast(m3);return {error:m3};
    }
    var org=bimMapOrigin(),placed=false,datum=bimCtxDatum(),local=!utm;
    var cE=(mn[0]+mx[0])/2,cN=(mn[1]+mx[1])/2;
    pushUndo();
    undoSuspend=true;
    var out=[],nOk=0,nBad=0,lods={},types={};
    try{
      if(utm&&!org){
        var cg=bimUtmInv(cE,cN,utm.zone,utm.south);
        if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
        A3D.site.sun=A3D.site.sun||{};
        A3D.site.sun.lat=Math.round(cg[1]*1e7)/1e7;A3D.site.sun.lon=Math.round(cg[0]*1e7)/1e7;
        org=bimMapOrigin();placed=true;
      }
      var z0=(utm&&datum!==null)?datum:mn[2];
      /* a file vertex in the model: x east-ish, y up, z south-ish */
      var MC={},M=function(ix){
        if(MC.hasOwnProperty(ix))return MC[ix];
        var w=W[ix],p;
        if(utm){var g=bimUtmInv(w[0],w[1],utm.zone,utm.south);p=bimGeoToModel(g[0],g[1],org);}
        else p=[w[0]-cE,-(w[1]-cN)];
        return (MC[ix]=[p[0],w[2]-z0,p[1]]);
      };
      var was=A3D.activeLayer,ly=addLayer('CityJSON','#c9b48a');
      if(bimLayerById(was))A3D.activeLayer=was;
      for(i=0;i<picks.length;i++){
        var pk=picks[i],g2=pk.g,rings=[],sh;
        if(g2.type==='Solid')sh=[g2.boundaries[0]||[]];
        else if(g2.type==='MultiSolid'||g2.type==='CompositeSolid')sh=(g2.boundaries||[]).map(function(s){return s[0]||[];});
        else sh=[g2.boundaries||[]];
        sh.forEach(function(shell){(shell||[]).forEach(function(srf){if(srf&&srf.length){rings.push(srf[0]);holes+=srf.length-1;}});});
        var vmap={},v=[],f=[];
        rings.forEach(function(rg){
          var loc=[];
          (rg||[]).forEach(function(ix){
            if(!vmap.hasOwnProperty(ix)){vmap[ix]=v.length;v.push(M(ix));}
            loc.push(vmap[ix]);
          });
          if(loc.length>=3)bimCjFaceSplit(loc,v).forEach(function(ff){f.push(ff);});
        });
        if(f.length<1)continue;
        var surf=!(g2.type==='Solid'||g2.type==='MultiSolid'||g2.type==='CompositeSolid');
        var at=bimCjCleanAttrs(pk.co.attributes||{}),par=(pk.co.parents||[])[0],pco=par?d.CityObjects[par]:null;
        var nm=at.name||(pco&&pco.attributes&&pco.attributes.name?pco.attributes.name+' part':'')||(pk.co.type+' '+pk.id);
        var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',pos:[0,0,0],mesh:{v:v,f:f},
          name:String(nm).slice(0,60),layer:ly.id,col:ly.color||'#c9b48a',locked:true};
        o.cityjson={id:String(pk.id).slice(0,120),type:pk.co.type,lod:String(g2.lod),geomType:g2.type,surface:surf,
          attributes:at,file:name.slice(0,120),crs:epsg?'EPSG:'+epsg:'none given',placed:local?'centred':'utm'};
        if(par){o.cityjson.parent=String(par).slice(0,120);if(pco){o.cityjson.parentType=pco.type;o.cityjson.parentAttributes=bimCjCleanAttrs(pco.attributes||{});}}
        var chk=bimSolidCheck(o.mesh,{surface:surf});
        if(chk.valid)nOk++;else nBad++;
        lods[o.cityjson.lod]=(lods[o.cityjson.lod]||0)+1;types[pk.co.type]=(types[pk.co.type]||0)+1;
        A3D.objs.push(o);out.push(o.id);
      }
    }finally{undoSuspend=false;}
    refreshTree();refreshLayers();refreshProps();fitScene();paint();saveSoon();
    var ts=Object.keys(types).map(function(x){return types[x]+' '+x;}).join(', '),ls=Object.keys(lods).sort().map(function(x){return 'LOD'+x;}).join(', ');
    a3dToast('CityJSON: '+ts+' ('+ls+') from '+name+' on the CityJSON layer; '+nOk+' valid'+(nBad?', '+nBad+' with problems (see each one\'s LOD group)':'')+
      (local?'; '+(epsg?'EPSG:'+epsg+' is not a grid this app converts':'it names no grid')+': placed by its centre at model 0,0, heights from its lowest point':'')+
      (placed?'; the site latitude and longitude were set to its centre':'')+
      (holes?'; '+holes+' opening'+(holes===1?'':'s')+' in faces filled':'')+(tmpl?'; '+tmpl+' template geometr'+(tmpl===1?'y':'ies')+' not read':'')+
      (trunc?'; stopped at '+BIM_CJ_MAX+' objects':''));
    return {ids:out,valid:nOk,bad:nBad,lods:lods,types:types,epsg:epsg,local:local,placedSite:placed,holes:holes,templates:tmpl,truncated:trunc};
  }
  function bimCityJsonPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.json,.cityjson,application/json';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)bimCityJsonFile(f);};
    inp.click();
    return true;
  }
  function bimCityJsonFile(file){
    var name=(file&&file.name)||'CityJSON';
    var rd=new FileReader();
    rd.onerror=function(){a3dToast('Failed to read '+name);};
    rd.onload=function(ev){
      try{bimCityJsonImportText(String(ev.target.result||''),name);}
      catch(eC){console.warn('[BIM] CityJSON import',eC);a3dToast('CityJSON import failed: '+(eC&&eC.message?eC.message:eC));}
    };
    rd.readAsText(file);
  }
"""
rep("""  /* ================= __acad3dV134: data layers =================""",
    CJ + """  /* ================= __acad3dV134: data layers =================""")
# the one import entry: a .city.json or .cityjson is CityJSON, any other .json a project
rep("""    }else if(ext==='json'){
      bimOpenProjectFileObj(file);   /* __acad3dV115: the one project-file reader */""",
    """    }else if(ext==='cityjson'||(ext==='json'&&/\\.city\\.json$/i.test(name))){   /* __acad3dV139 */
      bimCityJsonFile(file);
    }else if(ext==='json'){
      bimOpenProjectFileObj(file);   /* __acad3dV115: the one project-file reader */""")
rep("""      a3dToast('Unsupported file type: .'+ext+' (supported: .dxf, .ifc, .obj, .stl, .json project files, .geojson and .kml site data)');""",
    """      a3dToast('Unsupported file type: .'+ext+' (supported: .dxf, .ifc, .obj, .stl, .json project files, .geojson and .kml site data, .city.json CityJSON)');""")
rep("""      '<input type="file" id="a3d-filein" accept=".dxf,.ifc,.obj,.stl,.json,.geojson,.kml" style="display:none">'+""",
    """      '<input type="file" id="a3d-filein" accept=".dxf,.ifc,.obj,.stl,.json,.geojson,.kml,.cityjson" style="display:none">'+""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
