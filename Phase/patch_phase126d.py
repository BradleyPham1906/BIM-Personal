"""patch_phase126d.py -- V126: the section in the analysis, in Properties, and in Assets.

The analysis reads a member's section (bimMemberSection): its type's profile when it has one, else the
rectangle of its width and depth -- which bimProfileProps gives exactly as V125's bimRectSection did,
so nothing already analysed changes. A section that cannot be read keeps its member out of the frame
and says why, as a member with no modulus does (V125).

Properties' Structural page opens with the section, read-only: its name and shape, A, Iz, Iy, J and
its mass per metre -- the same numbers the analysis uses, from the one reader (law 3) -- and the basis:
nominal dimensions, fillets not modelled.

Assets gains one group, Sections, folded like Materials: the project's profiled column and beam
types. A section goes on the selected members of its kind, or on the member it is dropped on -- the
V124 pattern for materials and wall types, and the same path as Properties' Type list
(bimAssignTypeTo), with one undo. A beam section offered to a column is refused, and says why."""
NAME = 'patch_phase126d.py'
BASE = '0060144c89614160bee1d423bb0520ab0e34669ce420bebdbc52d13d0d71087c'
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


# ---- the analysis reads the section
rep("""  function bimVSub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}""", """  /* __acad3dV126: a member's section -- its type's profile, else the rectangle of its width and depth,
     in its own y (a column's width, a beam's depth) and z */
  function bimMemberSection(o){
    var b=o.bim;
    if(b.section)return b.section;
    return b.type==='column'?{shape:'rect',d:b.width,b:b.depth}:{shape:'rect',d:b.depth,b:b.width};
  }
  function bimVSub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}""")
rep("""      var sec=bimRectSection(hy,hz);
      members.push(""", """      var pf=bimMemberSection(o),pq=bimProfileProblem(pf);   /* __acad3dV126 */
      if(pq){skipped.push({id:o.id,name:o.name,why:'its section cannot be read: '+pq});continue;}
      var sec=bimProfileProps(pf);
      members.push(""")

# ---- Properties: the section, read-only, at the top of the Structural page
rep("""  function bimStructPropsHtml(o){
    var st=bimStructOf(o),rows='',i;""", """  /* __acad3dV126: the section's rows -- the numbers the analysis uses */
  function bimSectionPropsRows(o){
    var pf=bimMemberSection(o),pq=bimProfileProblem(pf),rows='';
    if(pq)return bimPropText('Section','Cannot be read: '+pq);
    var pp=bimProfileProps(pf),mat=bimMemberMaterial(o),tn=bimTypeNameOf(o);
    rows+=bimPropText('Section',(pf.shape!=='rect'&&tn?tn+' · ':'')+BIM_PROFILE_SHAPES[pf.shape]);
    rows+=bimPropText('Area (cm²)',bimDispNum(pp.A*1e4,2));
    rows+=bimPropText('Iz (cm⁴)',bimDispNum(pp.Iz*1e8,1));
    rows+=bimPropText('Iy (cm⁴)',bimDispNum(pp.Iy*1e8,1));
    rows+=bimPropText('J (cm⁴)',bimDispNum(pp.J*1e8,1));
    rows+=bimPropText('Mass (kg/m)',mat&&mat.density?bimDispNum(pp.A*mat.density,1)+' ('+mat.name+')':'—');
    rows+=bimPropText('Basis',pf.shape==='rect'?'Solid rectangle':'Nominal dimensions; fillets not modelled');
    return rows;
  }
  function bimStructPropsHtml(o){
    var st=bimStructOf(o),rows=bimSectionPropsRows(o),i;""")

# ---- Assets: Sections, folded
rep("""  var A3D_ASSETS_UI={q:'',closed:{materials:true,walltypes:true,patterns:true}};""",
    """  var A3D_ASSETS_UI={q:'',closed:{materials:true,sections:true,walltypes:true,patterns:true}};""")
rep("""        : 'Materials, wall types and patterns go on the selection, or on what they are dropped on.')+'</div>';""",
    """        : 'Materials, sections, wall types and patterns go on the selection, or on what they are dropped on.')+'</div>';""")
rep("""    h+=grp('materials','Materials',cards.length+' card(s)',body,false);
""", """    h+=grp('materials','Materials',cards.length+' card(s)',body,false);
    // __acad3dV126: Sections -- the profiled column and beam types, onto a member of their kind
    var secs=[];
    try{bimEnsureTypes();['column','beam'].forEach(function(c){(A3D.types[c]||[]).forEach(function(ty){if(ty.params&&ty.params.profile)secs.push({cat:c,t:ty});});});}
    catch(eS){console.warn('[BIM] The section types could not be read',eS);secs=[];}
    body='';
    for(i=0;i<secs.length;i++){
      var sp=secs[i].t.params,sm=bimMaterialByName(sp.material||''),sbad=bimProfileProblem(sp.profile);
      if(!bimAssetMatch(q,[secs[i].t.name,secs[i].cat,'section',sp.material||'',BIM_PROFILE_SHAPES[sp.profile.shape]||'']))continue;
      body+=row('section',secs[i].cat+'/'+secs[i].t.id,secs[i].t.name,
        (sp.material?sp.material+' ':'')+secs[i].cat+(sm&&sm.density&&!sbad?' · '+bimDispNum(bimProfileProps(sp.profile).A*sm.density,1)+' kg/m':''),
        !sbad,'its section cannot be read: '+sbad);
    }
    h+=grp('sections','Sections',secs.length+' section(s)',body,false);
""")
rep("""    if(kind==='material'||kind==='pattern'||kind==='walltype')obj=pick(cx,cy)||null;""",
    """    if(kind==='material'||kind==='pattern'||kind==='walltype'||kind==='section')obj=pick(cx,cy)||null;""")
rep("""    if(kind==='walltype'){
      A3D.activeWallType=key;""", """    if(kind==='section'){   /* __acad3dV126 */
      var sl=key.indexOf('/'),scat=key.slice(0,sl),sty=bimFindType(scat,key.slice(sl+1));
      if(!sty){a3dToast('That section is no longer in the project');return false;}
      var tg=drop?(o?[o]:[]):bimAssetSelIds().map(objById);
      tg=tg.filter(function(x){return x&&x.bim&&x.bim.type===scat;});
      if(!tg.length){
        a3dToast(drop?(o?sty.name+' is a '+scat+' section: drop it on a '+scat:'Drop a section on a '+scat)
                     :'Select a '+scat+', or drag '+sty.name+' onto one');
        return false;
      }
      pushUndo();
      var sok=[],sno=[];
      tg.forEach(function(x){if(bimAssignTypeTo(x,scat,sty.id))sok.push(x.name);else{sno.push(x.name);console.warn('[BIM] Section '+sty.id+' could not be applied to '+x.name);}});
      A3D.meshes={};refreshTree();refreshProps();paint();saveSoon();
      a3dToast(sok.length?(sok.length===1?sok[0]+' is now '+sty.name:sok.length+' '+scat+'s are now '+sty.name)+(sno.length?'; not '+sno.join(', '):'')
                         :sty.name+' could not be applied - see the console');
      return sok.length>0;
    }
    if(kind==='walltype'){
      A3D.activeWallType=key;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
