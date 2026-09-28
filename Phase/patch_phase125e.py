"""patch_phase125e.py -- V125: where the analysis is set -- Properties, and one button.

Rhino's rule (reference/research-structural-ui.md): one Properties panel whose pages follow the
selection -- the object's pages when something is selected, the viewport's when nothing is -- and a
plug-in adds a page to it rather than a window of its own. So nothing new is opened:

  a column selected     Structural: the support at its base (Automatic, Fixed, Pinned, Free), its
                        loads, and a row to add one (a lateral load at its top)
  a beam selected       Structural: its end connections (Rigid, Pinned), its loads, and a row to
                        add one (a line load, or a point load at a distance)
  nothing selected      Analysis, beside V106's Floor Loads: the combination, self-weight, what the
                        display shows (Off, bending moment, axial force, shear), the deflected shape,
                        and the last result's headline numbers -- or that it is out of date

SUPPORT and LOAD are the command-line way in: each opens Properties at the field it names (Rhino's
PropertiesPage), and says what to select first when nothing fitting is selected. The toolbar gains
one button, Analyze, in the Structure tab's strip beside the members it analyses.

Every edit is one undo step, stored under o.bim.struct (carried by bimCarryBim), and puts the
analysis display out of date until ANALYZE runs again."""
NAME = 'patch_phase125e.py'
BASE = '160776d6b10c30f258d2af0138a1ea674ac4203e9bd157c7ef09ba37dde95bf2'
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


# ---- the Structural page of a member, and the Analysis page of the model
rep("""  function bimToggleTrib(){
""", r"""  /* ================= __acad3dV125: the analysis in Properties ================= */
  function bimLoadLabel(ld){
    var s=ld.lc+'  ';
    if(ld.kind==='line')s+=bimDispNum(ld.v,2)+' kN/m along the beam';
    else if(ld.kind==='point')s+=bimDispNum(ld.v,2)+' kN at '+bimDispNum(ld.at,3)+' m';
    else s+=bimDispNum(ld.v,2)+' kN along '+(ld.dir==='z'?'Z':'X')+' at the top';
    return s;
  }
  function bimOpt(v,label,cur){return '<option value="'+v+'"'+(v===cur?' selected':'')+'>'+bimEsc(label)+'</option>';}
  function bimStructPropsHtml(o){
    var st=bimStructOf(o),rows='',i;
    if(o.bim.type==='column'){
      var auto=bimColumnSupport(o,o.bim.baseY+bimObjOffset(o)[1],true);
      var autoTxt='Automatic ('+(auto.kind?(auto.kind==='fixed'?'Fixed':'Pinned')+', '+auto.why:'none: '+auto.why)+')';
      rows+=bimPropRow('Support at base','<select data-propstr="support">'+bimOpt('',autoTxt,st.support||'')+
        bimOpt('fixed','Fixed',st.support)+bimOpt('pinned','Pinned',st.support)+bimOpt('free','Free (not held)',st.support)+'</select>');
    }else{
      rows+=bimPropRow('End connections','<select data-propstr="ends">'+bimOpt('','Rigid (moment)',st.ends==='pinned'?'x':'')+
        bimOpt('pinned','Pinned (shear only)',st.ends)+'</select>');
    }
    var loads=st.loads||[];
    for(i=0;i<loads.length;i++)
      rows+=bimPropRow('Load '+(i+1),'<span class="a3d-pstatic">'+bimEsc(bimLoadLabel(loads[i]))+'</span>'+
        '<button type="button" class="a3d-bdel" data-propstrdel="'+i+'" title="Remove this load">×</button>');
    /* the new-load row renders from a draft kept per member, so a re-render of the panel -- which any
       change in it may cause -- cannot throw away what is being typed */
    var kinds=o.bim.type==='column'?['lateral']:['line','point'],dr=bimLoadDraft(o);
    if(kinds.indexOf(dr.kind)<0)dr.kind=kinds[0];
    rows+=bimPropRow('New load','<select data-propstrnew="lc">'+bimOpt('D','Dead (D)',dr.lc)+bimOpt('L','Live (L)',dr.lc)+'</select>');
    rows+=bimPropRow('Kind','<select data-propstrnew="kind">'+kinds.map(function(k){return bimOpt(k,BIM_LOAD_KINDS[k],dr.kind);}).join('')+'</select>');
    rows+=bimPropRow('Value','<input type="number" step="any" data-propstrnew="v" value="'+bimEsc(dr.v)+'" placeholder="'+(o.bim.type==='column'?'kN':'kN/m or kN')+'">');
    if(o.bim.type==='column')rows+=bimPropRow('Direction','<select data-propstrnew="dir">'+bimOpt('x','Along X',dr.dir)+bimOpt('z','Along Z',dr.dir)+'</select>');
    else rows+=bimPropRow('At (m from start)','<input type="number" step="any" min="0" data-propstrnew="at" value="'+bimEsc(dr.at)+'" placeholder="point loads">');
    rows+=bimPropRow('','<button type="button" class="a3d-pedit" data-propstract="addload">Add load</button>');
    return bimPropGroup('Structural',rows);
  }
  function bimLoadDraft(o){
    var d=A3D_STRUCT.draft;
    if(!d||d.id!==o.id)d=A3D_STRUCT.draft={id:o.id,lc:'D',kind:'',v:'',at:'',dir:'x'};
    return d;
  }
  /* read first, in the capture phase, before any handler can re-render the panel */
  function bimLoadDraftInput(ev){
    var f=ev.target&&ev.target.getAttribute?ev.target.getAttribute('data-propstrnew'):null;
    var o=objById(A3D.sel);
    if(!f||!bimIsFrameMember(o))return;
    bimLoadDraft(o)[f]=ev.target.value;
  }
  function bimAnalysisPropsHtml(){
    var rows='',cur=A3D_STRUCT.show?(A3D_STRUCT.diagram||'M'):'off',nC=0,nB=0,i;
    for(i=0;i<A3D.objs.length;i++)if(bimIsFrameMember(A3D.objs[i])){if(A3D.objs[i].bim.type==='column')nC++;else nB++;}
    if(!nC&&!nB)return '';
    rows+=bimPropText('Frame',nC+' column(s), '+nB+' beam(s)');
    rows+=bimPropText('Basis',(bimCombo(A3D_STRUCT.combo)||BIM_COMBOS[0]).why);
    rows+=bimPropRow('Combination','<select data-propstr="combo">'+BIM_COMBOS.map(function(c){return bimOpt(c.name,c.name,A3D_STRUCT.combo);}).join('')+'</select>');
    rows+=bimPropRow('Self-weight','<select data-propstr="selfweight">'+bimOpt('1','Included in D',A3D_STRUCT.selfWeight?'1':'0')+bimOpt('0','Not included',A3D_STRUCT.selfWeight?'1':'0')+'</select>');
    rows+=bimPropRow('Display','<select data-propstr="display">'+bimOpt('off','Off',cur)+bimOpt('M','Bending moment',cur)+bimOpt('N','Axial force',cur)+bimOpt('V','Shear',cur)+'</select>');
    rows+=bimPropRow('Deflected shape','<select data-propstr="deflected">'+bimOpt('1','Shown',A3D_STRUCT.deflected?'1':'0')+bimOpt('0','Hidden',A3D_STRUCT.deflected?'1':'0')+'</select>');
    var r=A3D_STRUCT.res;
    if(r&&r.error)rows+=bimPropText('Result',r.error);
    else{
      var c=bimStructCurrent();
      if(c){
        var hd=bimStructHeadline(c);
        rows+=bimPropText('Largest moment',hd.moment?hd.moment.v.toFixed(1)+' kN·m, '+hd.moment.name:'none');
        rows+=bimPropText('Largest deflection',hd.defl?(hd.defl.v*1000).toFixed(1)+' mm'+(hd.ratio?' (L/'+hd.ratio+')':'')+', '+hd.defl.name:'none');
        rows+=bimPropText('Equilibrium',hd.balanced?'Balanced, '+hd.load.toFixed(1)+' kN':'NOT balanced: loads '+hd.load.toFixed(1)+', reactions '+hd.reaction.toFixed(1)+' kN');
      }else rows+=bimPropText('Result',r?'Out of date: run ANALYZE':'Run ANALYZE to solve the frame');
    }
    rows+=bimPropText('Not included','Floor loads, wind, seismic');
    return bimPropGroup('Analysis',rows);
  }
  /* SUPPORT and LOAD: Properties, opened at the field they name */
  function bimStructFocus(what){
    var o=objById(A3D.sel);
    if(what==='support'&&!(o&&o.bim&&o.bim.type==='column')){a3dToast('Select a column: SUPPORT sets how its base is held');return false;}
    if(what==='load'&&!bimIsFrameMember(o)){a3dToast('Select a beam or a column: LOAD adds a load to it');return false;}
    A3D_PROP_GROUPS_OPEN['Structural']=true;
    refreshProps();
    var f=document.querySelector(what==='support'?'[data-propstr="support"]':'[data-propstrnew="v"]');
    if(f){if(f.scrollIntoView)f.scrollIntoView({block:'center'});f.focus();}
    a3dToast(what==='support'?'Set the support at the base of '+o.name+' in Properties':'Add a load to '+o.name+' in Properties');
    return true;
  }
  function bimStructEdit(o,fn){
    pushUndo();
    var st=JSON.parse(JSON.stringify(bimStructOf(o)));
    fn(st);
    o.bim.struct=st;
    refreshProps();paint();saveSoon();
  }
  function bimStructPropChange(ev){
    var el2=ev.target&&ev.target.closest?ev.target.closest('[data-propstr]'):null;
    if(!el2)return false;
    var k=el2.getAttribute('data-propstr'),v=el2.value,o=objById(A3D.sel);
    if(k==='combo'||k==='selfweight'){
      if(k==='combo'&&bimCombo(v))A3D_STRUCT.combo=v;
      if(k==='selfweight')A3D_STRUCT.selfWeight=(v==='1');
      if(A3D_STRUCT.show)bimStructAnalyze();
      refreshProps();paint();return true;
    }
    if(k==='display'){
      if(v==='off'){bimAnalyzeOff();return true;}
      A3D_STRUCT.diagram=v;
      if(!A3D_STRUCT.show)bimAnalyzeCommand();else{paint();refreshProps();}
      return true;
    }
    if(k==='deflected'){A3D_STRUCT.deflected=(v==='1');paint();refreshProps();return true;}
    if(!bimIsFrameMember(o))return true;
    if(k==='support')bimStructEdit(o,function(st){if(BIM_SUPPORTS.indexOf(v)>=0)st.support=v;else delete st.support;});
    else if(k==='ends')bimStructEdit(o,function(st){if(v==='pinned')st.ends='pinned';else delete st.ends;});
    return true;
  }
  function bimStructPropClick(ev){
    var o=objById(A3D.sel);
    var del=ev.target&&ev.target.closest?ev.target.closest('[data-propstrdel]'):null;
    if(del&&bimIsFrameMember(o)){
      var ix=parseInt(del.getAttribute('data-propstrdel'),10);
      bimStructEdit(o,function(st){if(st.loads&&st.loads[ix])st.loads.splice(ix,1);});
      a3dToast('Load removed from '+o.name);
      return true;
    }
    var add=ev.target&&ev.target.closest?ev.target.closest('[data-propstract="addload"]'):null;
    if(!add||!bimIsFrameMember(o))return false;
    var dr=bimLoadDraft(o);
    var ld={lc:dr.lc,kind:dr.kind||(o.bim.type==='column'?'lateral':'line'),v:parseFloat(dr.v)};
    if(ld.kind==='point')ld.at=parseFloat(dr.at);
    if(ld.kind==='lateral')ld.dir=dr.dir;
    var bad=bimLoadProblem(o,ld);
    if(bad){a3dToast(bad);return true;}
    dr.v='';dr.at='';
    bimStructEdit(o,function(st){(st.loads=st.loads||[]).push(ld);});
    a3dToast(bimLoadLabel(ld)+' added to '+o.name);
    return true;
  }
  function bimToggleTrib(){
""")

rep("""    h+=bimPropGroup('Dimensions',dims);
""", """    h+=bimPropGroup('Dimensions',dims);
    if(bimIsFrameMember(o))h+=bimStructPropsHtml(o);   /* __acad3dV125 */
""")
rep("""    h+=bimPropGroup('Statistics',srows);
    return h;""", """    h+=bimAnalysisPropsHtml();   /* __acad3dV125: the model's Analysis page, beside its floor loads */
    h+=bimPropGroup('Statistics',srows);
    return h;""")
rep("""    /* __acad3dV103: setbacks, per side or all at once */""", """    /* __acad3dV125: the Structural and Analysis pages */
    if(el.propsbody){el.propsbody.addEventListener('input',bimLoadDraftInput,true);el.propsbody.addEventListener('change',bimLoadDraftInput,true);}
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimStructPropChange(ev);}catch(eSP){console.warn('[BIM] Analysis setting failed',eSP);a3dToast('That setting could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimStructPropClick(ev);}catch(eSC){console.warn('[BIM] Load edit failed',eSC);a3dToast('That load could not be changed - see the console');}
    });
    /* __acad3dV103: setbacks, per side or all at once */""")

# ---- SUPPORT and LOAD
rep("""    ['ANALYZEOFF',['ANALYSEOFF'],'analyzeoff','Turn the analysis display off'],""",
    """    ['ANALYZEOFF',['ANALYSEOFF'],'analyzeoff','Turn the analysis display off'],
    ['SUPPORT',['SUP'],'structsupport','Set how the selected column\\'s base is held (Properties)'],
    ['LOAD',['LD'],'structload','Add a load to the selected beam or column (Properties)'],""")
rep("""    analyzeoff:function(){bimAnalyzeOff();},""", """    analyzeoff:function(){bimAnalyzeOff();},
    structsupport:function(){bimStructFocus('support');},
    structload:function(){bimStructFocus('load');},""")

# ---- one toolbar button, beside the members it analyses
rep("""      {t:'Structure',small:['bim:column','bim:beam','bim:wall','bim:floor','bim:truss','bim:brace']},""",
    """      {t:'Structure',small:['bim:column','bim:beam','bim:wall','bim:floor','bim:truss','bim:brace','bim:analyze']},   /* __acad3dV125 */""")
rep("""    'bim:footing':ric(""", """    'bim:analyze':ric('<path d="M3 20h18"/><path d="M6 20V9M18 20V9M4 9h16"/><path d="M8 13q4 5 8 0" stroke-dasharray="2 2"/>'),   /* __acad3dV125 */
    'bim:footing':ric(""")
rep("""      'bim:beam':'Beam','bim:truss':'Truss',""", """      'bim:beam':'Beam','bim:analyze':'Analyze','bim:truss':'Truss',""")
rep("""    if(act==='bim:beam'){startBeamTool();return;}""", """    if(act==='bim:beam'){startBeamTool();return;}
    if(act==='bim:analyze'){bimAnalyzeCommand();return;}   /* __acad3dV125 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
