"""patch_phase146b.py -- V146: history in the app.

- Properties, Project tab: a History group -- what has changed since the last version, a message
  and Commit (Enter commits), Discard Changes, and the versions newest first, each with its
  changes and Restore.
- An element's Properties: its own History.
- Commands COMMIT and HISTORY. The hooks, the version and the marker."""
NAME = 'patch_phase146b.py'
BASE = '58fd398d796c282262e69de370c82686c0f261c6f868d4c6dbe3eccb6d628574'
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


UI = r"""  /* __acad3dV146: the History group and its actions */
  var A3D_HIST_OPEN={},A3D_HIST_MSG='';   /* the message as typed: a re-render of the panel must not lose it */
  function bimHistWhen(iso){
    var d=new Date(iso);if(isNaN(d.getTime()))return '';
    function p(n){return n<10?'0'+n:''+n;}
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes());
  }
  function bimHistStatsTxt(s){
    if(!s)return '';
    var r=[];if(s.added)r.push('+'+s.added);if(s.changed)r.push('~'+s.changed);if(s.removed)r.push('−'+s.removed);
    return r.join(' ')||'no change';
  }
  function bimHistListHtml(d,max){
    return d.slice(0,max).map(function(x){
      return '<div class="a3d-histd a3d-histd-'+x.kind+'" data-histkey="'+bimEsc(x.key)+'" data-histkind="'+x.kind+'"><b>'+(x.kind==='added'?'+':x.kind==='removed'?'−':'~')+'</b> '+bimEsc(x.label)+
        (x.props&&x.props.length?'<div class="a3d-histp">'+x.props.slice(0,6).map(function(p){return bimEsc(p.text);}).join('<br>')+(x.props.length>6?'<br>and '+(x.props.length-6)+' more':'')+'</div>':'')+'</div>';
    }).join('')+(d.length>max?'<div class="a3d-histmore">and '+(d.length-max)+' more</div>':'');
  }
  function bimHistHtml(){
    var H=bimHist(),head=bimHistHead(),d=[],r='';
    try{d=bimHistChanges();}catch(eD){console.warn('[BIM] history',eD);}
    r+='<div class="a3d-hist">';
    r+='<div class="a3d-histst" data-histstate="'+(d.length?'dirty':'clean')+'">'+(head?(d.length?d.length+' change'+(d.length===1?'':'s')+' since "'+bimEsc(head.msg)+'"':'No changes since "'+bimEsc(head.msg)+'"'):
      (d.length?'No version yet: '+d.length+' element'+(d.length===1?'':'s')+' to commit':'No version yet, and nothing to commit'))+'</div>';
    r+='<div class="a3d-histrow"><input type="text" data-histmsg maxlength="200" placeholder="What changed (Enter commits)" value="'+bimEsc(A3D_HIST_MSG)+'"><button type="button" data-histact="commit"'+(d.length?'':' disabled')+'>Commit</button></div>';
    if(d.length){
      r+='<div class="a3d-histchg" data-histchanges>'+bimHistListHtml(d,20)+'</div>';
      if(head)r+='<div class="a3d-histrow"><button type="button" data-histact="discard">Discard Changes</button></div>';
    }
    var C=H.commits.slice().reverse(),sz=bimHistSize();
    if(C.length)r+='<div class="a3d-histlog">'+C.slice(0,30).map(function(c){
      var open=!!A3D_HIST_OPEN[c.id];
      return '<div class="a3d-histc'+(c.id===H.head?' a3d-histc-head':'')+'" data-histc="'+c.id+'"><div class="a3d-histcm">'+bimEsc(c.msg)+(c.id===H.head?' <span class="a3d-histtag">latest</span>':'')+'</div>'+
        '<div class="a3d-histmeta">'+bimHistWhen(c.at)+(c.by?' &middot; '+bimEsc(c.by):'')+' &middot; '+bimHistStatsTxt(c.stats)+'</div>'+
        '<div class="a3d-histacts"><button type="button" data-histact="show:'+c.id+'">'+(open?'Hide':'Changes')+'</button><button type="button" data-histact="restore:'+c.id+'">Restore</button></div>'+
        (open?'<div class="a3d-histchg">'+bimHistListHtml(bimHistCommitDiff(c),40)+'</div>':'')+'</div>';
    }).join('')+(C.length>30?'<div class="a3d-histmore">and '+(C.length-30)+' older</div>':'')+'</div>';
    if(C.length)r+='<div class="a3d-histsize">'+C.length+' version'+(C.length===1?'':'s')+', '+sz.blobs+' stored element'+(sz.blobs===1?'':'s')+' ('+Math.round(sz.chars/1024)+' KB), saved with the project</div>';
    return r+'</div>';
  }
  function bimHistObjHtml(o){
    var L=bimHistOf('o:'+o.id);
    if(!L.length)return bimPropText('History','not in any version yet');
    return L.slice(0,6).map(function(x){
      return '<div class="a3d-histd a3d-histd-'+x.kind+'" data-histobj="'+x.id+'"><b>'+(x.kind==='added'?'+':x.kind==='removed'?'−':'~')+'</b> '+bimEsc(x.msg)+' <span class="a3d-histmeta">'+bimHistWhen(x.at)+'</span>'+
        (x.props&&x.props.length?'<div class="a3d-histp">'+x.props.slice(0,4).map(function(p){return bimEsc(p.text);}).join('<br>')+'</div>':'')+'</div>';
    }).join('')+(L.length>6?'<div class="a3d-histmore">and '+(L.length-6)+' earlier</div>':'');
  }
  function bimHistDoCommit(msg){
    var r=bimHistCommit(msg);
    if(r.error){a3dToast(r.error);return r;}
    A3D_HIST_MSG='';
    a3dToast('Committed "'+r.msg+'": '+bimHistStatsTxt(r.stats));
    refreshProps();
    return r;
  }
  function bimHistDoRestore(id){
    var r=bimHistRestore(id);
    if(r.error){a3dToast(r.error);return r;}
    a3dToast('Restored "'+r.msg+'": commit to keep it as the latest, or Undo to go back');
    return r;
  }
  function bimHistAct(k,ev){
    if(k==='commit'){var inp=document.querySelector('#a3d-propsbody [data-histmsg]');return bimHistDoCommit((inp&&inp.value)||A3D_HIST_MSG);}
    if(k==='discard'){var hd=bimHistHead();return hd?bimHistDoRestore(hd.id):null;}
    if(k.indexOf('show:')===0){var id=k.slice(5);A3D_HIST_OPEN[id]=!A3D_HIST_OPEN[id];refreshProps();return true;}
    if(k.indexOf('restore:')===0)return bimHistDoRestore(k.slice(8));
    return false;
  }
  /* COMMIT and HISTORY: the History group, on the Project tab */
  function bimHistReveal(focus){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('History');
    refreshProps();paint();
    if(focus)setTimeout(function(){var i=document.querySelector('#a3d-propsbody [data-histmsg]');if(i)i.focus();},0);
    return true;
  }
  function bimHistCommitCommand(){
    var d=bimHistChanges(),hd=bimHistHead();
    if(!d.length){a3dToast(hd?'Nothing has changed since "'+hd.msg+'"':'There is nothing to commit yet');return false;}
    return bimHistReveal(true);
  }
"""

rep("""  /* ================= __acad3dV138: verify the survey ================= */""",
    UI + """  /* ================= __acad3dV138: verify the survey ================= */""")
rep("""    h+=bimPTab('project',bimPropGroup('Statistics',srows));""",
    """    h+=bimPTab('project',bimPropGroup('Statistics',srows));
    h+=bimPTab('project',bimPropGroup('History',bimHistHtml()));   /* __acad3dV146 */""")
rep("""    if(name==='Identity Data'||name==='Statistics')return 'project';""",
    """    if(name==='Identity Data'||name==='Statistics'||name==='History')return 'project';   /* __acad3dV146: History */""")
rep("""    if(bimLodOf(o))h+=bimPropGroup('LOD',bimLodHtml(o));   /* __acad3dV139 */""",
    """    if(bimLodOf(o))h+=bimPropGroup('LOD',bimLodHtml(o));   /* __acad3dV139 */
    if(A3D.history&&A3D.history.commits&&A3D.history.commits.length)h+=bimPropGroup('History',bimHistObjHtml(o));   /* __acad3dV146 */""")
rep("""    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var rb=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxreset]'):null;""",
    """    /* __acad3dV146: the History group's buttons, and Enter in its message */
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var hb=ev.target&&ev.target.closest?ev.target.closest('[data-histact]'):null;
      if(!hb||hb.disabled)return;
      bimHistAct(hb.getAttribute('data-histact'),ev);
    });
    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histmsg'))A3D_HIST_MSG=ev.target.value;
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      if(ev.key!=='Enter'||!ev.target||!ev.target.hasAttribute||!ev.target.hasAttribute('data-histmsg'))return;
      ev.preventDefault();ev.stopPropagation();
      bimHistDoCommit(ev.target.value);
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var rb=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxreset]'):null;""")
rep("""    ['GRADE',['GRADING','DAYLIGHT','GRADEPADS'],""", """    ['COMMIT',['CHECKPOINT','SAVEVERSION'],'commit','Keep this state of the model as a version, with a message: what changed, element by element'],   /* __acad3dV146 */
    ['HISTORY',['VERSIONS','VERSIONHISTORY'],'history','The model\\'s versions: what changed in each, element by element, and Restore'],
    ['GRADE',['GRADING','DAYLIGHT','GRADEPADS'],""")
rep("""    grade:function(){bimGradeCommand();},              /* __acad3dV145 */""", """    grade:function(){bimGradeCommand();},              /* __acad3dV145 */
    commit:function(){bimHistCommitCommand();},        /* __acad3dV146 */
    history:function(){bimHistReveal(false);},""")
rep("""    GRADE:'grading pad daylight slope cut fill embankment batter earthwork proposed surface site',   /* __acad3dV145 */""",
    """    GRADE:'grading pad daylight slope cut fill embankment batter earthwork proposed surface site',   /* __acad3dV145 */
    COMMIT:'commit version save checkpoint snapshot git history revision',   /* __acad3dV146 */
    HISTORY:'history versions revisions changes log diff restore git timeline',""")
rep(""".a3d-lodtag{""", """.a3d-hist{display:flex;flex-direction:column;gap:6px;font-size:12px}
.a3d-histst{color:#c9d1d9}.a3d-histrow{display:flex;gap:6px}.a3d-histrow input{flex:1;min-width:0}
.a3d-histchg{display:flex;flex-direction:column;gap:3px;margin:2px 0 4px}
.a3d-histd{color:#c9d1d9;line-height:1.35}.a3d-histd b{display:inline-block;width:12px}
.a3d-histd-added b{color:#81c784}.a3d-histd-removed b{color:#e57373}.a3d-histd-changed b{color:#ffb74d}
.a3d-histp{color:#9aa5b0;font-size:11px;margin-left:14px}.a3d-histmore,.a3d-histsize,.a3d-histmeta{color:#8a949e;font-size:11px}
.a3d-histc{border-top:1px solid rgba(255,255,255,.08);padding:6px 0}.a3d-histcm{color:#e8edf2}
.a3d-histtag{font-size:10px;padding:1px 5px;border-radius:3px;background:rgba(110,160,255,.18);color:#8fb4ff}
.a3d-histacts{display:flex;gap:6px;margin-top:3px}
.a3d-lodtag{""")
rep("""  window.__a3dTerrainLegend=function(){""", """  window.__a3dHistCommit=function(msg){return bimHistCommit(msg);};   /* __acad3dV146 */
  window.__a3dHistory=function(){var H=bimHist();return {head:H.head,commits:JSON.parse(JSON.stringify(H.commits)),size:bimHistSize()};};
  window.__a3dHistChanges=function(){return JSON.parse(JSON.stringify(bimHistChanges()));};
  window.__a3dHistCommitDiff=function(id){var c=bimHistCommitById(id);return c?JSON.parse(JSON.stringify(bimHistCommitDiff(c))):null;};
  window.__a3dHistRestore=function(id){return bimHistRestore(id);};
  window.__a3dHistOf=function(id){return JSON.parse(JSON.stringify(bimHistOf('o:'+id)));};
  window.__a3dHash=function(s){return bimHash(String(s));};
  window.__a3dCanon=function(v){return bimCanon(v);};
  window.__a3dTerrainLegend=function(){""")
rep("""  var BIM_APP_VERSION={v:'V145',date:'2026-10-04'};   /* __acad3dV145 */""", """  var BIM_APP_VERSION={v:'V146',date:'2026-10-04'};   /* __acad3dV146 */""")
rep("""  window.__acad3dV145='""", """  window.__acad3dV146='canon,hash128,elementtree,blobstore,commit,diff,fielddiff,idrecords,restore,elementhistory,historygroup,historycommands,savedwithproject';
  window.__acad3dV145='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
