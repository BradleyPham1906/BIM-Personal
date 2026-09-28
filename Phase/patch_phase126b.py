"""patch_phase126b.py -- V126: the catalogue of sections.

Steel W shapes, IPE, channels, square HSS and pipes, and concrete rounds, added to the column and
beam type catalogues V102 started -- each a type whose params carry its profile, its material
(Steel for steel), and its width and depth as the profile's extent across and deep, so everything
that reads a member's width and depth (schedules, picking, grips, footings) keeps working.

Nominal dimensions only: AISC Steel Construction Manual and EN 10365 for the IPE, as published
dimensions; every property follows from them (126a), with fillets not modelled -- W12x26 comes to
7.56 in^2 against the manual's 7.65 and Ix 201 in^4 against 204, the fillets' share, stated.

A project stored before V126 gains the new types once, by id: its own types, and any it edited, are
untouched, and a steel type it later deletes is not put back (A3D.types.__v126 records the seeding).

The Type list in Properties groups the types by material, and Edit Type shows a profiled type's size
as set by its section -- not a width to type, which would contradict it."""
NAME = 'patch_phase126b.py'
BASE = 'ddf6c88819a18d25e74cfbea240060ae821bc7d583fd3249d17d11e83d831c00'
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


rep("""  /* __acad3dV102: the structural catalogue */
  var BEAM_TYPE_DEFAULTS=[""", r"""  /* __acad3dV126: a profile's extent without its outline -- this runs while the catalogues below are
     being built, before the round's segment count is set */
  function bimProfileBox(p){
    if(p.shape==='rect')return {y:p.d,z:p.b};
    if(p.shape==='circle'||p.shape==='pipe')return {y:p.D,z:p.D};
    if(p.shape==='hss')return {y:p.H,z:p.B};
    return {y:p.d,z:p.bf};
  }
  /* a profiled type: a column's width runs along its y, a beam's depth is its y */
  function bimSectionType(cat,id,name,prof,mat){
    var b=bimProfileBox(prof);
    return {id:id,name:name,params:cat==='column'?{width:b.y,depth:b.z,material:mat,profile:prof}:{width:b.z,depth:b.y,material:mat,profile:prof}};
  }
  var BIM_IN=0.0254;
  function bimW(d,bf,tf,tw){return {shape:'ibeam',d:d*BIM_IN,bf:bf*BIM_IN,tf:tf*BIM_IN,tw:tw*BIM_IN};}
  function bimIPE(d,bf,tf,tw){return {shape:'ibeam',d:d/1000,bf:bf/1000,tf:tf/1000,tw:tw/1000};}
  function bimC(d,bf,tf,tw){return {shape:'channel',d:d*BIM_IN,bf:bf*BIM_IN,tf:tf*BIM_IN,tw:tw*BIM_IN};}
  /* __acad3dV102: the structural catalogue */
  var BEAM_TYPE_DEFAULTS=[""")
rep("""    {id:'bt-400x700',name:'400 x 700mm',params:{width:0.4,depth:0.7,material:'Concrete'}}
  ];""", """    {id:'bt-400x700',name:'400 x 700mm',params:{width:0.4,depth:0.7,material:'Concrete'}}
  ];
  /* __acad3dV126: steel beams -- AISC W and C (inches), EN 10365 IPE (mm), nominal dimensions */
  [['bt-w8x31','W8x31',bimW(8.00,8.00,0.435,0.285)],['bt-w10x33','W10x33',bimW(9.73,7.96,0.435,0.290)],
   ['bt-w12x26','W12x26',bimW(12.2,6.49,0.380,0.230)],['bt-w14x30','W14x30',bimW(13.8,6.73,0.385,0.270)],
   ['bt-w16x40','W16x40',bimW(16.0,7.00,0.505,0.305)],['bt-w18x50','W18x50',bimW(18.0,7.50,0.570,0.355)],
   ['bt-w21x62','W21x62',bimW(21.0,8.24,0.615,0.400)],['bt-w24x76','W24x76',bimW(23.9,8.99,0.680,0.440)],
   ['bt-ipe200','IPE 200',bimIPE(200,100,8.5,5.6)],['bt-ipe240','IPE 240',bimIPE(240,120,9.8,6.2)],
   ['bt-ipe300','IPE 300',bimIPE(300,150,10.7,7.1)],['bt-ipe360','IPE 360',bimIPE(360,170,12.7,8.0)],
   ['bt-ipe400','IPE 400',bimIPE(400,180,13.5,8.6)],
   ['bt-c8x11','C8x11.5',bimC(8.00,2.26,0.390,0.220)],['bt-c10x15','C10x15.3',bimC(10.0,2.60,0.436,0.240)],
   ['bt-c12x21','C12x20.7',bimC(12.0,2.94,0.501,0.282)]
  ].forEach(function(r){BEAM_TYPE_DEFAULTS.push(bimSectionType('beam',r[0],r[1],r[2],'Steel'));});""")
rep("""    {id:'ct-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}}
  ];""", """    {id:'ct-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}}
  ];
  /* __acad3dV126: steel columns and concrete rounds */
  [['ct-w8x31','W8x31',{shape:'ibeam',d:8.00*0.0254,bf:8.00*0.0254,tf:0.435*0.0254,tw:0.285*0.0254},'Steel'],
   ['ct-w10x49','W10x49',{shape:'ibeam',d:10.0*0.0254,bf:10.0*0.0254,tf:0.560*0.0254,tw:0.340*0.0254},'Steel'],
   ['ct-w12x65','W12x65',{shape:'ibeam',d:12.1*0.0254,bf:12.0*0.0254,tf:0.605*0.0254,tw:0.390*0.0254},'Steel'],
   ['ct-w14x90','W14x90',{shape:'ibeam',d:14.0*0.0254,bf:14.5*0.0254,tf:0.710*0.0254,tw:0.440*0.0254},'Steel'],
   ['ct-hss6x6','HSS6x6x3/8',{shape:'hss',B:6*0.0254,H:6*0.0254,t:0.349*0.0254},'Steel'],
   ['ct-hss8x8','HSS8x8x1/2',{shape:'hss',B:8*0.0254,H:8*0.0254,t:0.465*0.0254},'Steel'],
   ['ct-hss10x10','HSS10x10x1/2',{shape:'hss',B:10*0.0254,H:10*0.0254,t:0.465*0.0254},'Steel'],
   ['ct-pipe6','Pipe 6 STD',{shape:'pipe',D:6.625*0.0254,t:0.280*0.0254},'Steel'],
   ['ct-pipe8','Pipe 8 STD',{shape:'pipe',D:8.625*0.0254,t:0.322*0.0254},'Steel'],
   ['ct-r400','Round 400mm',{shape:'circle',D:0.4},'Concrete'],
   ['ct-r500','Round 500mm',{shape:'circle',D:0.5},'Concrete'],
   ['ct-r600','Round 600mm',{shape:'circle',D:0.6},'Concrete']
  ].forEach(function(r){COL_TYPE_DEFAULTS.push(bimSectionType('column',r[0],r[1],r[2],r[3]));});""")

# ---- a stored project gains the sections once
rep("""    if(!A3D.activeWallType)A3D.activeWallType=A3D.types.wall[0].id;
    return A3D.types;""", """    /* __acad3dV126: a project stored before V126 gains the section types once, by id -- its own types
       are untouched, and one it deletes later is not put back */
    if(!A3D.types.__v126){
      ['column','beam'].forEach(function(cat){
        var have={},list=A3D.types[cat],k;
        for(k=0;k<list.length;k++)have[list[k].id]=1;
        TYPE_CATS[cat].defaults.forEach(function(dt){
          if(dt.params&&dt.params.profile&&!have[dt.id]){
            var cp=JSON.parse(JSON.stringify(dt));cp.graphics=bimSanitizeGraphics(cp.graphics);list.push(cp);
          }
        });
      });
      A3D.types.__v126=1;
    }
    if(!A3D.activeWallType)A3D.activeWallType=A3D.types.wall[0].id;
    return A3D.types;""")

# ---- the Type list, grouped by material
rep("""      cons+=bimPropRow('Type','<select data-propf="objtype">'+
        A3D.types[o.bim.type].map(function(x){return '<option value="'+x.id+'"'+(cur&&cur.id===x.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('')+
        '</select>');""", """      cons+=bimPropRow('Type','<select data-propf="objtype">'+bimTypeOptionsHtml(o.bim.type,cur&&cur.id)+'</select>');""")
rep("""  function bimAssignTypeTo(o,cat,typeId){""", """  /* __acad3dV126: a category's types as options, grouped by material once there is more than one */
  function bimTypeOptionsHtml(cat,curId){
    var list=A3D.types[cat]||[],groups=[],by={},i;
    for(i=0;i<list.length;i++){
      var m=(list[i].params&&list[i].params.material)||'Other';
      if(!by[m]){by[m]=[];groups.push(m);}
      by[m].push(list[i]);
    }
    function opts(a){return a.map(function(x){return '<option value="'+x.id+'"'+(curId===x.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('');}
    if(groups.length<2)return opts(list);
    return groups.map(function(g){return '<optgroup label="'+bimEsc(g)+'">'+opts(by[g])+'</optgroup>';}).join('');
  }
  function bimAssignTypeTo(o,cat,typeId){""")

# ---- Edit Type: a profiled type's size is its section's
rep("""    var paramRows=def.typeParams.map(function(k){
      return '<div class="a3d-dlgrow"><label>'+k.charAt(0).toUpperCase()+k.slice(1)+' (m)</label>'+
        '<input type="number" step="any" min="0.001" data-typep="'+k+'" value="'+t.params[k]+'"></div>';
    }).join('');""", """    var prof=t.params&&t.params.profile;   /* __acad3dV126 */
    var paramRows=(prof?'<div class="a3d-dlgrow"><label>Section</label><span class="a3d-pstatic">'+bimEsc(BIM_PROFILE_SHAPES[prof.shape]||prof.shape)+'</span></div>':'')+
      def.typeParams.map(function(k){
      return '<div class="a3d-dlgrow"><label>'+k.charAt(0).toUpperCase()+k.slice(1)+' (m)</label>'+
        '<input type="number" step="any" min="0.001" data-typep="'+k+'" value="'+t.params[k]+'"'+
        (prof?' disabled title="Set by the section: choose another type to change it"':'')+'></div>';
    }).join('');""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
