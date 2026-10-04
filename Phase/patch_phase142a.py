"""patch_phase142a.py -- V142: the user guide, and versions.

The owner: "something documented like AutoCAD and Rhinoceros on their websites ... as this app
evolves we need documentation and versioning". The guide lives beside the app (docs/), on the same
GitHub Pages site, so it opens offline from the repository too.

- The app knows its version (V142, and the date) and says it: Statistics, on the Project tab, has
  Version with a link to its release notes and to the user guide.
- DOCS (GUIDE, MANUAL, USERGUIDE) opens the guide; RELEASENOTES (VERSION, WHATSNEW) the notes for
  this version.
- F1 in the command search opens the highlighted command's page in the command reference.
- Hooks; the marker."""
NAME = 'patch_phase142a.py'
BASE = '2318f9ba19eb452e6badb03f1bbcfb0ea90cbf960936c19e967664eeb0e96d5d'
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


DOCS = r"""  /* ================= __acad3dV142: the user guide, and versions =================
     The guide is in docs/ beside the app, on the same site (and in the repository, so it opens
     offline). Its command reference has a section per command, anchored by the command's id. */
  var BIM_APP_VERSION={v:'V142',date:'2026-10-04'};
  var BIM_DOCS_BASE='docs/';
  /* a command's anchor in the reference: cmd:LINE -> cmd-LINE, act:bim:wall -> act-bim-wall */
  function bimDocsAnchor(id){return String(id||'').replace(/[^A-Za-z0-9_-]+/g,'-');}
  function bimDocsUrl(page,anchor){return BIM_DOCS_BASE+page+(anchor?'#'+anchor:'');}
  var A3D_GUIDE={opened:[]};
  function bimDocsOpen(page,anchor){
    var u=bimDocsUrl(page,anchor),w=null;
    A3D_GUIDE.opened.push(u);
    try{w=window.open(u,'_blank','noopener');}catch(eW){w=null;}
    a3dToast('Opening the user guide: '+u+(w?'':' (allow pop-ups for this page if nothing opened)'));
    return u;
  }
  function bimVersionHtml(){
    return '<a class="a3d-ctxlink" href="'+bimEsc(bimDocsUrl('changelog.html',BIM_APP_VERSION.v.toLowerCase()))+'" target="_blank" rel="noopener" data-docslink="notes">'+
      bimEsc(BIM_APP_VERSION.v)+', '+bimEsc(BIM_APP_VERSION.date)+'</a> · '+
      '<a class="a3d-ctxlink" href="'+bimEsc(bimDocsUrl('index.html'))+'" target="_blank" rel="noopener" data-docslink="guide">User Guide</a>';
  }
"""
rep("""  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================""",
    DOCS + """  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================""")
rep("""    srows+=bimPropText('Sheets',A3D.sheets.length);""", """    srows+=bimPropText('Sheets',A3D.sheets.length);
    srows+=bimPropRow('Version','<span class="a3d-pstatic">'+bimVersionHtml()+'</span>');   /* __acad3dV142 */""")
rep("""    ['ANALYSES',['ANALYZEPANEL','ANALYSISPANEL'],'analyses',""",
    """    ['DOCS',['GUIDE','MANUAL','USERGUIDE'],'docs','Open the user guide: getting started, every topic, and the command reference'],   /* __acad3dV142 */
    ['RELEASENOTES',['VERSION','WHATSNEW'],'releasenotes','What changed in this version, and every version before it'],
    ['ANALYSES',['ANALYZEPANEL','ANALYSISPANEL'],'analyses',""")
rep("""    analyses:function(){bimAnalyzeCommandTab();},                 /* __acad3dV141 */""",
    """    analyses:function(){bimAnalyzeCommandTab();},                 /* __acad3dV141 */
    docs:function(){bimDocsOpen('index.html');},                  /* __acad3dV142 */
    releasenotes:function(){bimDocsOpen('changelog.html',BIM_APP_VERSION.v.toLowerCase());},""")
rep("""    ANALYSES:'analysis analyses""", """    DOCS:'help documentation manual guide tutorial learn how reference f1',   /* __acad3dV142 */
    RELEASENOTES:'version changelog release notes history what is new updates',
    ANALYSES:'analysis analyses""")
# F1 in the command search: the highlighted command's page
rep("""      else if(e.key==='Enter'){runIdx(active);e.preventDefault();e.stopPropagation();}
      else if(e.key==='Escape'){closePal();}""", """      else if(e.key==='Enter'){runIdx(active);e.preventDefault();e.stopPropagation();}
      else if(e.key==='F1'){   /* __acad3dV142: the highlighted command's page in the guide */
        var hc=rows[active];e.preventDefault();e.stopPropagation();
        if(hc&&hc.kind!=='key'&&window.__a3dDocsOpen){closePal();window.__a3dDocsOpen('commands.html',hc.id);}
        else if(window.__a3dDocsOpen){closePal();window.__a3dDocsOpen('index.html');}
      }
      else if(e.key==='Escape'){closePal();}""")
rep("""  /* __acad3dV141: tabs and the Analyze tab */""", """  /* __acad3dV142: the guide and the version */
  window.__a3dVersion=function(){return JSON.parse(JSON.stringify(BIM_APP_VERSION));};
  window.__a3dDocsOpen=function(page,id){return bimDocsOpen(page,id?bimDocsAnchor(id):'');};
  window.__a3dDocsOpened=function(){return A3D_GUIDE.opened.slice();};
  window.__a3dDocsAnchor=function(id){return bimDocsAnchor(id);};
  window.__acad3dV142='appversion,versionrow,docscommand,releasenotescommand,f1help,docsanchors';
  /* __acad3dV141: tabs and the Analyze tab */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
