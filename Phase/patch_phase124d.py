"""patch_phase124d.py -- V124: a template is a starting project.

PIPELINE, V124: "a template is a starting project (V115's project tabs)." Save as Template keeps the
whole project on screen -- levels, grids, layers, types, views, sheets, title block, objects -- as a
library entry, and using one opens a NEW project tab that starts as a copy of it, named the way
every new project is (Project1, Project2 ...). The template itself is never changed by what is done
in the project made from it.

The record is written under its own key, acad3dTemplateV1:<id>, before the entry is added, so a
store too full to take it adds nothing and says so -- never an entry with no project behind it. A
template whose stored project has gone (cleared site data) says so when it is used."""
NAME = 'patch_phase124d.py'
BASE = 'e0c06fd90bc1c6e85f456890ac27e06b45fe2e6715535a1541ca40458dab1bbf'
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


rep("""  function bimNameFromFile(filename){
""", r"""  /* ================= __acad3dV124: templates -- a starting project =================
     The record goes under its own key before the entry is added, so a full store adds nothing. */
  function bimTemplateSave(name){
    var rec=JSON.parse(JSON.stringify(bimProjectRecord()));
    delete rec.docId;
    var id='tpl-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6);
    try{localStorage.setItem(A3D_TEMPLATE_PREFIX+id,JSON.stringify(rec));}
    catch(eS){
      console.warn('[BIM] The template could not be stored.',eS);
      a3dToast('The template could not be saved: browser storage is full');
      return null;
    }
    var entry={id:id,kind:'template',name:name,category:'Templates',manufacturer:'',
      count:Array.isArray(rec.objs)?rec.objs.length:0,
      levels:Array.isArray(rec.levels)?rec.levels.length:0,
      sheets:Array.isArray(rec.sheets)?rec.sheets.length:0,
      createdAt:new Date().toISOString()};
    entry.thumb=bimRecsThumb(rec.objs||[]);
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
  /* A new project tab that starts as a copy of the template. Returns the new project's id. */
  function bimTemplateUse(entry){
    if(!entry||bimAssetKind(entry)!=='template')return null;
    var raw=null,rec=null;
    try{raw=localStorage.getItem(A3D_TEMPLATE_PREFIX+entry.id);}
    catch(eG){console.warn('[BIM] Browser storage could not be read.',eG);}
    if(raw==null){a3dToast('The project stored for "'+entry.name+'" is no longer in this browser\'s storage');return null;}
    try{rec=JSON.parse(raw);}catch(eP){console.warn('[BIM] A stored template is not valid JSON: '+entry.id,eP);rec=null;}
    if(!rec||typeof rec!=='object'){a3dToast('"'+entry.name+'" could not be used: its stored project is damaged');return null;}
    if(!rec.titleBlock||typeof rec.titleBlock!=='object')rec.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};
    rec.titleBlock.project=bimNextProjectName();
    var id=bimDocsAdd(rec,'create');
    if(id)a3dToast('New project '+rec.titleBlock.project+' from the template "'+entry.name+'"');
    return id;
  }
  function openSaveTemplateDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Save as Template</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(bimProjectLabel()+' template')+'" maxlength="60"></div>'+
      '<div class="a3d-propnote">Keeps this whole project -- its levels, grids, layers, types, views, sheets, title block and '+
      A3D.objs.length+' object(s) -- as the start of new projects. A project made from it is a copy: the template does not change.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Save</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]');
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      closeDlg();
      var e=bimTemplateSave(name);
      if(!e)return;
      refreshFamilyPanel();
      a3dToast('Saved template "'+e.name+'" to the library');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function bimNameFromFile(filename){
""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
