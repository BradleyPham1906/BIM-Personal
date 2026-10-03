"""patch_phase138b.py -- V138: verify the survey, in the app.

- SURVEY's dialog opens a file (.txt, .csv, .pnezd, .xyz), and names the code that marks check shots
  (CHK by default; blank for none).
- A selected surface has a Survey Check group: the verdict, each check with its result, the control
  points (name=elevation), and Export Report.
- SURVEYCHECK (VERIFYSURVEY, QA) selects a surface and opens its check.
- Hooks for the suites and tools/verify_survey.py; the marker."""
NAME = 'patch_phase138b.py'
BASE = '24b6f93e24d3aa4031e9327ac406e9aaa18bb293b5d70b1c65f25a8d54373b58'
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


UI = r"""  /* ================= __acad3dV138: the survey check in Properties ================= */
  var BIM_SURVEY_MARK={pass:'✓',warn:'!',fail:'✗',none:'–'};
  function bimSurveyCheckHtml(o){
    var r=bimSurveyCheck(o),h='',i,it,ctl;
    if(!r)return '';
    h+='<div class="a3d-prow"><div class="a3d-plabel">Verdict</div><div class="a3d-pval"><span class="a3d-svck a3d-svck-'+r.verdict+'">'+
      BIM_SURVEY_MARK[r.verdict]+' '+r.verdict.toUpperCase()+'</span></div></div>';
    for(i=0;i<r.items.length;i++){
      it=r.items[i];
      h+='<div class="a3d-prow a3d-svrow" data-svitem="'+it.key+'"><div class="a3d-plabel">'+bimEsc(it.label)+'</div><div class="a3d-pval">'+
        '<span class="a3d-svck a3d-svck-'+it.status+'">'+BIM_SURVEY_MARK[it.status]+'</span> <span class="a3d-pstatic">'+bimEsc(it.text)+'</span></div></div>';
    }
    ctl=(o.control||[]).map(function(c){return c.p+'='+c.z;}).join(', ');
    h+=bimPropRow('Control','<input type="text" data-propsurvey="control" value="'+bimEsc(ctl)+'" placeholder="105=30.000, 201=28.45" spellcheck="false" '+
      'title="Points whose elevation you know, in the survey’s units">');
    h+=bimPropRow('','<button type="button" class="a3d-pedit" data-propsurveyact="export">Export Report</button>');
    return h;
  }
  function bimSurveyPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propsurvey]'):null;
    if(!f)return false;
    var o=objById(A3D.sel);
    if(f.getAttribute('data-propsurvey')==='control'&&o)bimSurveySetControl(o,f.value);
    return true;
  }
  function bimSurveyPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propsurveyact]'):null;
    if(!b)return false;
    var o=objById(A3D.sel);
    if(b.getAttribute('data-propsurveyact')==='export'&&o)bimSurveyReportExport(o);
    return true;
  }
  /* SURVEYCHECK: the selected surface, or the first */
  function bimSurveyCheckCommand(){
    var o=objById(A3D.sel),i;
    if(!o||o.t!=='terrain'){o=null;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].t==='terrain'&&A3D.objs[i].survey){o=A3D.objs[i];break;}}
    if(!o){a3dToast('There is no surface to check: make one with SURVEY');return null;}
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    A3D_PROP_GROUPS_OPEN['Survey Check']=true;
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Survey Check"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    var r=bimSurveyCheck(o),bad=r.items.filter(function(x){return x.status==='fail'||x.status==='warn';}).map(function(x){return x.label.toLowerCase();});
    a3dToast(o.name+': '+r.verdict.toUpperCase()+(bad.length?' - see '+bad.join(', '):' - every check passed'));
    return r;
  }
"""

rep("""  /* DATALAYERS: the group, with nothing selected */""", UI + """  /* DATALAYERS: the group, with nothing selected */""")
rep("""    h+=bimPropGroup('Dimensions',dims);""", """    h+=bimPropGroup('Dimensions',dims);
    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138 */""")
rep("""    /* __acad3dV136: the lens */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){""", """    /* __acad3dV138: the survey check */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimSurveyPropChange(ev);}catch(eSC){console.warn('[BIM] Survey check failed',eSC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimSurveyPropClick(ev);}catch(eSK){console.warn('[BIM] Survey report failed',eSK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV136: the lens */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){""")
# the dialog: a file, and the check-shot code
rep("""      '<div class="a3d-dlgrow"><label>Points, one per line</label><textarea data-a3dp="pts" rows="8" cols="46" placeholder="1, 5000.00, 2000.00, 342.10, EP"></textarea></div>'+""",
    """      '<div class="a3d-dlgrow"><label>Points, one per line</label><textarea data-a3dp="pts" rows="8" cols="46" placeholder="1, 5000.00, 2000.00, 342.10, EP"></textarea></div>'+
      '<div class="a3d-dlgrow"><button type="button" data-a3dlg="file">Open a File ...</button> <span data-a3dp="fname" class="a3d-dlgnote"></span>'+
        '<input type="file" data-a3dp="filein" accept=".txt,.csv,.pnezd,.penzd,.xyz,.asc,text/plain,text/csv" hidden></div>'+   /* __acad3dV138 */""")
rep("""      '<div class="a3d-dlgrow"><label>Elevation at model 0 (blank: 0)</label><input type="number" step="any" data-a3dp="bz" value="'+(b?b.z:'')+'"></div>'+""",
    """      '<div class="a3d-dlgrow"><label>Elevation at model 0 (blank: 0)</label><input type="number" step="any" data-a3dp="bz" value="'+(b?b.z:'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Check shots: description starts with (blank: none)</label><input type="text" data-a3dp="chk" value="'+BIM_SURVEY_CHECK_CODE+'" '+
        'title="Shots kept out of the surface and measured against it"></div>'+   /* __acad3dV138 */""")
rep("""      closeDlg();
      bimImportSurvey(res,fmt,units,base);
    }
    d.addEventListener('click',function(ev){var bt=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!bt)return;if(bt.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});""",
    """      var chk=q('chk');
      closeDlg();
      bimImportSurvey(res,fmt,units,base,chk);   /* __acad3dV138: the check shots */
    }
    /* __acad3dV138: a survey file, read into the box */
    var fin=d.querySelector('[data-a3dp="filein"]');
    fin.addEventListener('change',function(){
      var f=fin.files&&fin.files[0];if(!f)return;
      var rd=new FileReader();
      rd.onload=function(){d.querySelector('[data-a3dp="pts"]').value=String(rd.result||'');d.querySelector('[data-a3dp="fname"]').textContent=f.name;};
      rd.onerror=function(){d.querySelector('#a3d-dlgerr').textContent=f.name+' could not be read';};
      rd.readAsText(f);
    });
    d.addEventListener('click',function(ev){var bt=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!bt)return;
      if(bt.getAttribute('data-a3dlg')==='file'){fin.click();return;}
      if(bt.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});""")
rep("""    ['SURVEY',['TOPO','SURFACE'],'survey',""", """    ['SURVEYCHECK',['VERIFYSURVEY','QA'],'surveycheck','Check a survey surface: every line read, duplicates, the surface through every point, bust shots, check shots, control points, and the public terrain'],   /* __acad3dV138 */
    ['SURVEY',['TOPO','SURFACE'],'survey',""")
rep("""    survey:function(){openSurveyDlg();},              /* __acad3dV108 */""", """    survey:function(){openSurveyDlg();},              /* __acad3dV108 */
    surveycheck:function(){bimSurveyCheckCommand();},  /* __acad3dV138 */""")
rep("""SURVEY:'terrain topography topo tin contours ground',""", """SURVEY:'terrain topography topo tin contours ground',SURVEYCHECK:'verify validate qa qc quality accuracy rmse bust blunder control benchmark check shots report',""")
rep(""".a3d-dllens .a3d-ukv select{flex:1;min-width:0}""", """.a3d-dllens .a3d-ukv select{flex:1;min-width:0}
.a3d-svck{display:inline-block;min-width:14px;font-weight:700;text-align:center}
.a3d-svck-pass{color:#4caf50}.a3d-svck-warn{color:#ffb74d}.a3d-svck-fail{color:#ef5350}.a3d-svck-none{color:#8a96a3}
.a3d-svrow .a3d-pstatic{white-space:normal}""")
rep("""  /* __acad3dV137: the map on 3D terrain */
  window.__a3dTerrain3d=""", """  /* __acad3dV138: verify the survey */
  window.__a3dSurveyImport=function(text,fmt,units,base,code){
    var res=bimParseSurvey(text,fmt||'PNEZD');if(res.error)return {error:res.error};
    if(res.points.length<3)return {error:'too few points: '+res.points.length};
    var b=base||{};b={n:b.n==null?res.points[0].n:b.n,e:b.e==null?res.points[0].e:b.e,z:b.z==null?0:b.z};
    var o=bimImportSurvey(res,fmt||'PNEZD',units||'m',b,code);return o?{id:o.id,points:o.survey.length,checks:(o.checks||[]).length,bad:res.bad}:{error:'no surface'};};
  window.__a3dSurveyCheck=function(id){var o=objById(id);delete A3D_SURVEYCHK[id];return o?JSON.parse(JSON.stringify(bimSurveyCheck(o))):null;};
  window.__a3dSurveyControl=function(id,txt){var o=objById(id);return o?bimSurveySetControl(o,txt):false;};
  window.__a3dSurveyReportHtml=function(id){var o=objById(id);return o?bimSurveyReportHtml(o):'';};
  window.__a3dSurveyTol=function(){return JSON.parse(JSON.stringify(BIM_SURVEY_TOL));};
  window.__acad3dV138='surveyread,surveyduplicates,surveyfidelity,surveytriangles,surveybusts,surveychecks,surveycontrol,surveypublic,'+
    'surveyverdict,surveypanel,surveyreport,surveyfile,surveycheckcode,surveycommand';
  /* __acad3dV137: the map on 3D terrain */
  window.__a3dTerrain3d=""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
