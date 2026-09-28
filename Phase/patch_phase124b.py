"""patch_phase124b.py -- V124: an imported model asks what its numbers mean.

PIPELINE, V124: "An imported model needs its unit (OBJ carries none: ask, and show the size it would
come in at) and a thumbnail." Before V124 an OBJ or STL was taken as metres whatever it was drawn
in: a chair modelled in millimetres came in 450 m wide, and one from a Z-up program lay on its back.

The import dialog now asks two things and shows what they mean before anything is added:
  Unit     mm, cm, m, in, ft -- the first guess is the one that brings the largest side nearest a
           metre and a half, the size of most things a library holds; the dialog says it is a guess
  Up       Y up (OBJ's usual convention) or Z up (STL's, and most CAD programs')
and, live, the size it would come in at in the project's unit, with a picture of it standing the way
it will stand. The unit and the file it came from are kept on the entry.

The conversion is one function, bimImportModelMesh, reached by the dialog and by nothing else, so
what the dialog shows is what the library gets."""
NAME = 'patch_phase124b.py'
BASE = 'b3953a785bb0e17a1612b337df82908ca952092abb4f48b65cddaefdac838ca3'
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


# ---- the file's kind decides the first guess of the up axis
rep("""    function afterParse(mesh){
      if(!mesh||!mesh.v.length||!mesh.f.length){a3dToast('No usable geometry found in '+name);return;}
      openImportFamilyNameDlg(mesh,name.replace(/\\.[^.]+$/,''));
    }
""", """    function afterParse(mesh){
      if(!mesh||!mesh.v.length||!mesh.f.length){a3dToast('No usable geometry found in '+name);return;}
      openImportFamilyNameDlg(mesh,name.replace(/\\.[^.]+$/,''),{ext:ext,source:name});   /* __acad3dV124 */
    }
""")

# ---- the dialog
head = "  function openImportFamilyNameDlg(mesh,suggestedName){\n"
tail = "  function startFamilyPlaceTool(famId){\n"
c = t.count(head)
if c != 1:
    sys.exit('ABORT: dialog head %d occurrences' % c)
s = t.index(head)
e = t.index(tail, s)
old_block = t[s:e]
if old_block.count('\n') != 28:
    sys.exit('ABORT: dialog span is %d lines, expected 28' % old_block.count('\n'))
new_block = r"""  /* __acad3dV124: what an imported model's numbers mean. OBJ carries no unit and STL none either,
     so the unit is asked, and the up axis with it; bimImportModelMesh is the one conversion, so what
     the dialog shows is what the library gets. */
  var A3D_IMPORT_UNITS=[['mm',0.001,'millimetres'],['cm',0.01,'centimetres'],['m',1,'metres'],
    ['in',0.0254,'inches'],['ft',0.3048,'feet']];
  function bimImportUnitScale(u){
    var i;
    for(i=0;i<A3D_IMPORT_UNITS.length;i++)if(A3D_IMPORT_UNITS[i][0]===u)return A3D_IMPORT_UNITS[i][1];
    return 1;
  }
  /* Z up to Y up is a quarter turn about X: the model's up (+Z) becomes +Y and its +Y runs away
     from the viewer, to -Z, so a right-handed model stays right-handed and is not mirrored. */
  function bimImportModelMesh(mesh,unit,zUp){
    var f=bimImportUnitScale(unit);
    return {v:mesh.v.map(function(p){return zUp?[p[0]*f,p[2]*f,-p[1]*f]:[p[0]*f,p[1]*f,p[2]*f];}),
      f:mesh.f.map(function(fc){return fc.slice();})};
  }
  /* The first guess: the unit that brings the largest side nearest 1.5 m. A guess is all it can be
     -- 180 is a person in centimetres and a door in millimetres -- so the dialog shows the size. */
  function bimGuessImportUnit(mesh){
    var b=bimMeshBounds(mesh),E=Math.max(b.mx[0]-b.mn[0],b.mx[1]-b.mn[1],b.mx[2]-b.mn[2]);
    if(!(E>0)||!isFinite(E))return 'm';
    var best='m',bd=Infinity,i;
    for(i=0;i<A3D_IMPORT_UNITS.length;i++){
      var d=Math.abs(Math.log(E*A3D_IMPORT_UNITS[i][1]/1.5));
      if(d<bd-1e-12){bd=d;best=A3D_IMPORT_UNITS[i][0];}
    }
    return best;
  }
  function openImportFamilyNameDlg(mesh,suggestedName,opt){
    opt=opt||{};
    closeDlg();
    var guess=bimGuessImportUnit(mesh),zUp=opt.ext==='stl';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Import Model</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(suggestedName)+'" maxlength="60"></div>'+
      '<div class="a3d-dlgrow"><label>Category</label><select data-a3dp="cat">'+
        FAMILY_CATEGORIES.map(function(c){return '<option value="'+c+'">'+c+'</option>';}).join('')+
      '</select></div>'+
      '<div class="a3d-dlgrow"><label>Drawn in</label><select data-a3dp="unit">'+
        A3D_IMPORT_UNITS.map(function(u){return '<option value="'+u[0]+'"'+(u[0]===guess?' selected':'')+'>'+u[2]+'</option>';}).join('')+
      '</select></div>'+
      '<div class="a3d-dlgrow"><label>Up axis</label><select data-a3dp="up">'+
        '<option value="y"'+(zUp?'':' selected')+'>Y up</option><option value="z"'+(zUp?' selected':'')+'>Z up</option>'+
      '</select></div>'+
      '<div class="a3d-impprev"><img data-a3dp="thumb" alt=""><div data-a3dp="size" class="a3d-impsize"></div></div>'+
      '<div class="a3d-propnote">The file does not say what unit it was drawn in: the first choice is a guess from its size. Check the size above.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Import</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]'),cI=d.querySelector('[data-a3dp="cat"]');
    var uI=d.querySelector('[data-a3dp="unit"]'),yI=d.querySelector('[data-a3dp="up"]');
    var sz=d.querySelector('[data-a3dp="size"]'),im=d.querySelector('[data-a3dp="thumb"]');
    function current(){return bimImportModelMesh(mesh,uI.value,yI.value==='z');}
    function show(){
      var m=current(),b=bimMeshBounds(m),u=bimUnitLabel();
      sz.textContent='Comes in at '+bimDispLen(b.mx[0]-b.mn[0])+' '+u+' wide, '+bimDispLen(b.mx[2]-b.mn[2])+' '+u+
        ' deep and '+bimDispLen(b.mx[1]-b.mn[1])+' '+u+' high';
      var th=bimMeshThumb(m,120,90);
      if(th)im.src=th;else im.removeAttribute('src');
    }
    uI.addEventListener('change',show);yI.addEventListener('change',show);
    show();
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      var m=current();
      closeDlg();
      var fam=bimFamilyLibraryAdd({name:name,category:cI.value,mesh:m,unit:uI.value,source:opt.source||''});
      refreshFamilyPanel();
      var s=fam.mesh.size||[0,0,0],u=bimUnitLabel();
      a3dToast('Imported "'+fam.name+'" into the library ('+bimDispLen(s[0])+' x '+bimDispLen(s[2])+' x '+bimDispLen(s[1])+' '+u+')');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
"""
t = t[:s] + esc(new_block) + t[e:]

# ---- its preview's two rules
rep(""".a3d-famrow{display:flex;""", """.a3d-impprev{display:flex;align-items:center;gap:10px;margin:6px 0}
.a3d-impprev img{width:120px;height:90px;background:#1b1f24;border:1px solid #2f353c;border-radius:6px;flex:0 0 auto}
.a3d-impsize{font-size:11.5px;color:#dfe4ea;line-height:1.45}
.a3d-famrow{display:flex;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
