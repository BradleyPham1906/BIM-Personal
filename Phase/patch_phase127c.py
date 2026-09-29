"""patch_phase127c.py -- V127: where an alignment is made and set.

Following the owner's V125 rule (Rhino's model): no new window. An alignment's settings are two
pages of Properties, and its commands act on the selection.

- ALIGNMENT makes the selected open polyline an alignment (its vertices the PIs, a curve of the
  largest radius up to 100 m that its legs leave room for at each), in its place. One button, in
  the Site panel beside the property line.
- Properties, Alignment: the start station; the stations and length; each PI's radius, and its
  curve -- deflection, which way it turns, T, L, E, PC and PT; the profile view's exaggeration.
- Properties, Profile: each PVI's station, elevation and curve length; the grades; each vertical
  curve's crest or sag, A, K and high or low point. Add PVI starts a profile on the ground (the
  surface under the ends, else the alignment's own elevation), then splits its longest grade.
- PROFILEVIEW places the selected alignment's profile view where you click. STATION reports the
  station and offset of every point you click, and marks it, until Escape.

Every edit is made to a copy first and refused, by name, when the copy's geometry is -- curves
that would overlap, a profile off the alignment -- so a bad number never lands in the model. A
changed start station moves the profile with it: its PVIs stay on the same ground."""
NAME = 'patch_phase127c.py'
BASE = 'b39fc23737d698b9b636724f97f7460aefba084e96a58f407bfed10576c5acd9'
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


rep("""  function bimSetTrueNorth(deg){""", r"""  /* ---- __acad3dV127: editing */
  /* An edit, made to a copy and checked before it is kept: fn returns a reason to refuse, or
     nothing. One undo step. */
  function bimAlignEdit(o,fn){
    var c={t:'alignment',pos:bimObjOffset(o),y:o.y,pis:JSON.parse(JSON.stringify(o.pis)),radii:(o.radii||[]).slice(),sta0:isFinite(o.sta0)?o.sta0:0,
      profile:o.profile?JSON.parse(JSON.stringify(o.profile)):null,profileView:o.profileView?JSON.parse(JSON.stringify(o.profileView)):null};
    var why=fn(c);
    if(typeof why==='string'){a3dToast(why);refreshProps();return false;}
    var g=bimAlignGeom(c);
    if(g.error){a3dToast(o.name+' was not changed: '+g.error);refreshProps();return false;}
    if(c.profile){var pg=bimProfileGeom(c.profile,g);if(pg.error){a3dToast(o.name+'\'s profile was not changed: '+pg.error);refreshProps();return false;}}
    pushUndo();
    o.pis=c.pis;o.radii=c.radii;o.sta0=c.sta0;
    if(c.profile)o.profile=c.profile;else delete o.profile;
    if(c.profileView)o.profileView=c.profileView;else delete o.profileView;
    refreshProps();paint();saveSoon();
    return true;
  }
  /* Add PVI: a profile on the ground to start with, then the longest grade split at its middle */
  function bimAlignAddPvi(c){
    var g=bimAlignGeom(c);
    if(g.error)return 'Fix the alignment first: '+g.error;
    if(!c.profile||!c.profile.pvis||c.profile.pvis.length<2){
      var gr=bimAlignGround(c,g,Math.max(g.length/200,0.25)),e0=null,e1=null,y0=(c.y||0)+bimObjOffset(c)[1];
      if(gr.length){var f=gr[0][0],l=gr[gr.length-1];if(Math.abs(f[0]-g.sta0)<1e-6)e0=f[1];if(Math.abs(l[l.length-1][0]-g.sta1)<1e-6)e1=l[l.length-1][1];}
      c.profile={pvis:[{sta:g.sta0,elev:e0!==null?+e0.toFixed(3):y0,L:0},{sta:g.sta1,elev:e1!==null?+e1.toFixed(3):y0,L:0}]};
      return;
    }
    var v=c.profile.pvis,best=0,i;
    for(i=1;i+1<v.length;i++)if(v[i+1].sta-v[i].sta>v[best+1].sta-v[best].sta)best=i;
    var sm=(v[best].sta+v[best+1].sta)/2;
    v.splice(best+1,0,{sta:+sm.toFixed(3),elev:+((v[best].elev+v[best+1].elev)/2).toFixed(3),L:0});
  }
  function bimAlignPropsHtml(o){
    var g=bimAlignGeom(o),r='',i,rp='';
    r+=bimPropRow('Start station (m)','<input type="number" step="any" data-propalign="sta0" value="'+(isFinite(o.sta0)?o.sta0:0)+'">');
    if(g.error)r+=bimPropText('Problem',g.error);
    else{
      r+=bimPropText('Stations',bimFmtStation(g.sta0)+' to '+bimFmtStation(g.sta1));
      r+=bimPropText('Length (m)',bimDispNum(g.length,3));
    }
    for(i=1;i<o.pis.length-1;i++){
      r+=bimPropRow('PI '+(i+1)+' radius (m)','<input type="number" step="any" min="0" data-propalign="r:'+(i-1)+'" value="'+((o.radii&&o.radii[i-1])||0)+'">');
      var p=g.error?null:g.pis[i];
      if(p)r+=bimPropText('PI '+(i+1)+' curve',p.T>0?
        ('Δ '+(p.D*180/Math.PI).toFixed(4)+'° '+(p.turn>0?'right':'left')+', T '+p.T.toFixed(3)+', L '+p.L.toFixed(3)+', E '+p.E.toFixed(3)+', PC '+bimFmtStation(p.pc)+', PT '+bimFmtStation(p.pt))
        :(p.D>1e-9?'no curve: Δ '+(p.D*180/Math.PI).toFixed(4)+'°, radius 0':'none: the route runs straight through'));
    }
    if(o.profileView){
      r+=bimPropRow('Profile view exaggeration','<input type="number" step="any" min="0.1" data-propalign="vx" value="'+(o.profileView.vx||10)+'">');
      r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propalignact="pv">Move profile view</button> <button type="button" class="a3d-pedit" data-propalignact="pvdel">Remove</button>');
    }else r+=bimPropRow('Profile view','<button type="button" class="a3d-pedit" data-propalignact="pv">Place profile view</button>');
    var h=bimPropGroup('Alignment',r);
    var pr=o.profile,pg=(pr&&!g.error)?bimProfileGeom(pr,g):null;
    if(pr&&pr.pvis){
      for(i=0;i<pr.pvis.length;i++){
        var v=pr.pvis[i],end=(i===0||i===pr.pvis.length-1);
        rp+=bimPropRow('PVI '+(i+1)+' sta / El / L',
          '<input type="number" step="any" style="width:31%" title="Station (m)" data-propalign="pvi:'+i+':sta" value="'+v.sta+'">'+
          '<input type="number" step="any" style="width:31%" title="Elevation (m)" data-propalign="pvi:'+i+':elev" value="'+v.elev+'">'+
          '<input type="number" step="any" min="0" style="width:24%" title="Vertical curve length (m)" data-propalign="pvi:'+i+':L" value="'+(v.L||0)+'"'+(end?' disabled':'')+'>'+
          '<button type="button" class="a3d-bdel" data-propalignact="pvidel:'+i+'" title="Remove this PVI">×</button>');
      }
      if(pg&&pg.error)rp+=bimPropText('Problem',pg.error);
      else if(pg){
        for(i=0;i<pg.grades.length;i++)rp+=bimPropText('Grade '+(i+1)+' to '+(i+2),(pg.grades[i]*100).toFixed(3)+'%');
        for(i=1;i<pg.pvis.length-1;i++){
          var q=pg.pvis[i];
          if(q.L>0)rp+=bimPropText('PVI '+(i+1)+' curve',q.kind+', A '+q.A.toFixed(3)+'%, K '+(isFinite(q.K)?q.K.toFixed(2):'—')+
            ', PVC '+bimFmtStation(q.pvc)+', PVT '+bimFmtStation(q.pvt)+(q.turnSta!==undefined?', '+(q.kind==='crest'?'high':'low')+' point '+bimFmtStation(q.turnSta)+' El '+q.turnElev.toFixed(3):''));
        }
      }
    }else rp+=bimPropText('Profile','None yet: Add PVI starts one on the ground');
    rp+=bimPropRow('','<button type="button" class="a3d-pedit" data-propalignact="pvadd">Add PVI</button>');
    h+=bimPropGroup('Profile',rp);
    return h;
  }
  function bimAlignPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propalign]'):null;
    if(!f)return false;
    var o=objById(A3D.sel);
    if(!bimIsAlignment(o))return false;
    var k=f.getAttribute('data-propalign'),v=parseFloat(f.value);
    if(!isFinite(v)){a3dToast('That must be a number');refreshProps();return true;}
    if(k==='sta0')bimAlignEdit(o,function(c){var d=v-c.sta0;c.sta0=v;if(c.profile)c.profile.pvis.forEach(function(p){p.sta=+(p.sta+d).toFixed(6);});});
    else if(k==='vx')bimAlignEdit(o,function(c){if(!(v>0))return 'The exaggeration must be more than 0';c.profileView.vx=v;});
    else if(k.indexOf('r:')===0)bimAlignEdit(o,function(c){if(!(v>=0))return 'A radius is 0 (no curve) or more';c.radii[parseInt(k.slice(2),10)]=v;});
    else if(k.indexOf('pvi:')===0){
      var bits=k.split(':'),ix=parseInt(bits[1],10),fld=bits[2];
      bimAlignEdit(o,function(c){
        if(!c.profile||!c.profile.pvis[ix])return 'That PVI is gone';
        if(fld==='L'&&!(v>=0))return 'A vertical curve\'s length is 0 or more';
        c.profile.pvis[ix][fld]=v;
      });
    }
    return true;
  }
  function bimAlignPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-propalignact]'):null;
    if(!b)return false;
    var o=objById(A3D.sel),a=b.getAttribute('data-propalignact');
    if(!bimIsAlignment(o))return false;
    if(a==='pv'){bimStartProfileViewTool(o);return true;}
    if(a==='pvdel'){if(bimAlignEdit(o,function(c){c.profileView=null;}))a3dToast(o.name+'\'s profile view removed');return true;}
    if(a==='pvadd'){if(bimAlignEdit(o,bimAlignAddPvi))a3dToast('PVI added to '+o.name+'\'s profile: set its station and elevation');return true;}
    if(a.indexOf('pvidel:')===0){
      var ix=parseInt(a.slice(7),10);
      bimAlignEdit(o,function(c){
        if(!c.profile||!c.profile.pvis[ix])return 'That PVI is gone';
        if(c.profile.pvis.length<=2){c.profile=null;return;}
        c.profile.pvis.splice(ix,1);
      });
      return true;
    }
    return false;
  }
  /* ---- commands */
  function bimAlignmentCommand(){
    var o=objById(A3D.sel);
    if(bimIsAlignment(o)){a3dToast(o.name+' is already an alignment: set it in Properties');return null;}
    if(o&&o.t==='sketch')return bimAlignmentFromSketch(o);
    a3dToast('Draw an open polyline through the PIs, select it, then ALIGNMENT');
    return null;
  }
  /* the alignment a command means: the selected one, or the only one */
  function bimAlignTarget(){
    var o=objById(A3D.sel);
    if(bimIsAlignment(o))return o;
    var all=A3D.objs.filter(bimIsAlignment);
    return all.length===1?all[0]:null;
  }
  function bimStartProfileViewTool(o){
    o=o||bimAlignTarget();
    if(!o){a3dToast('Select an alignment: PROFILEVIEW places its profile view');return false;}
    if(bimAlignProblem(o)){a3dToast(o.name+' cannot be drawn in profile: '+bimAlignProblem(o));return false;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'profileview',pts:[],y:lvl?lvl.elev:0,on:null,alignId:o.id};
    a3dToast('Profile view: click where its lower-left corner goes');
    paint();
    return true;
  }
  function bimPlaceProfileView(o,pt){
    var q=bimObjOffset(o);
    if(bimAlignEdit(o,function(c){c.profileView={at:[pt[0]-q[0],pt[1]-q[2]],vx:(c.profileView&&c.profileView.vx)||10};}))
      a3dToast(o.name+'\'s profile view placed'+(o.profile?'':': Add PVI in Properties to design its profile'));
  }
  function bimStartStationTool(){
    var o=bimAlignTarget();
    if(!o){a3dToast('Select an alignment: STATION reports a point\'s station and offset along it');return false;}
    if(bimAlignProblem(o)){a3dToast(o.name+' has no stations: '+bimAlignProblem(o));return false;}
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'station',pts:[],y:lvl?lvl.elev:0,on:null,alignId:o.id};
    A3D.stationMark=null;
    a3dToast('Station: click points to read their station and offset along '+o.name+'; Escape to finish');
    paint();
    return true;
  }
  function bimStationAt(id,pt){
    var o=objById(id);
    if(!bimIsAlignment(o)){a3dToast('The alignment is gone');A3D.sk=null;return null;}
    var g=bimAlignGeom(o);
    if(g.error){a3dToast(o.name+': '+g.error);return null;}
    var so=bimAlignStationOffset(g,pt);
    A3D.stationMark={id:id,p:[pt[0],pt[1]],foot:so.foot,sta:so.sta,off:so.off};
    a3dToast('Sta '+bimFmtStation(so.sta)+', '+Math.abs(so.off).toFixed(3)+' m '+(Math.abs(so.off)<0.0005?'on the line':(so.off>0?'right':'left'))+
      (so.beyond?' ('+so.beyond+')':'')+' -- '+o.name);
    paint();
    return so;
  }
  function drawStationMark(ctx,V,W,H){
    var m=A3D.stationMark;
    if(!m||!A3D.sk||A3D.sk.tool!=='station')return;
    var o=objById(m.id);if(!o)return;
    var y=(o.y||0)+bimObjOffset(o)[1],a=toScreen([m.p[0],y,m.p[1]],V,W,H),b=toScreen([m.foot[0],y,m.foot[1]],V,W,H);
    ctx.save();
    ctx.strokeStyle='#ffd479';ctx.fillStyle='#ffd479';ctx.lineWidth=1.2;ctx.setLineDash([4,3]);
    ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();ctx.setLineDash([]);
    ctx.beginPath();ctx.moveTo(a[0]-5,a[1]-5);ctx.lineTo(a[0]+5,a[1]+5);ctx.moveTo(a[0]+5,a[1]-5);ctx.lineTo(a[0]-5,a[1]+5);ctx.stroke();
    ctx.font='11px system-ui,sans-serif';ctx.textAlign='left';ctx.textBaseline='bottom';
    ctx.fillText(bimFmtStation(m.sta)+'  '+Math.abs(m.off).toFixed(3)+' m '+(m.off>=0?'R':'L'),a[0]+8,a[1]-6);
    ctx.restore();
  }
  function bimSetTrueNorth(deg){""")

# the clicks
rep("""    }else if(sk.tool==='text'){
      var textY=sk.y;""", """    }else if(sk.tool==='profileview'){   /* __acad3dV127 */
      var pvA=objById(sk.alignId);
      A3D.sk=null;
      if(!bimIsAlignment(pvA)){a3dToast('The alignment is gone');return;}
      bimPlaceProfileView(pvA,[gx,gz]);
    }else if(sk.tool==='station'){   /* __acad3dV127: stays live for the next point */
      bimStationAt(sk.alignId,[gx,gz]);
    }else if(sk.tool==='text'){
      var textY=sk.y;""")
rep("""    drawAlignments(ctx,V,W,H);     /* __acad3dV127 */""", """    drawAlignments(ctx,V,W,H);     /* __acad3dV127 */
    drawStationMark(ctx,V,W,H);""")

# Properties
rep("""    if(bimIsFrameMember(o))h+=bimStructPropsHtml(o);   /* __acad3dV125 */""",
    """    if(bimIsFrameMember(o))h+=bimStructPropsHtml(o);   /* __acad3dV125 */
    if(bimIsAlignment(o))h+=bimAlignPropsHtml(o);       /* __acad3dV127 */""")
rep("""    if(bimIsProperty(o))return 'Site : Property Line';   /* __acad3dV103 */""",
    """    if(bimIsProperty(o))return 'Site : Property Line';   /* __acad3dV103 */
    if(bimIsAlignment(o))return 'Site : Alignment';       /* __acad3dV127 */""")
rep("""    /* __acad3dV103: setbacks, per side or all at once */""", """    /* __acad3dV127: the Alignment and Profile pages */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimAlignPropChange(ev);}catch(eAL){console.warn('[BIM] Alignment edit failed',eAL);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimAlignPropClick(ev);}catch(eAC){console.warn('[BIM] Alignment edit failed',eAC);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV103: setbacks, per side or all at once */""")

# commands, and one button
rep("""    ['INSERT',['I','DDINSERT'],'blockinsert',""", """    /* __acad3dV127: the alignment */
    ['ALIGNMENT',['ALIGN_CREATE','ALN'],'alignment','Make the selected open polyline an alignment: its vertices become the PIs'],
    ['PROFILEVIEW',['PV'],'profileview','Place the selected alignment\\'s profile view where you click'],
    ['STATION',['STA','STAOFF'],'stationoffset','Read the station and offset of points along the selected alignment'],
    ['INSERT',['I','DDINSERT'],'blockinsert',""")
rep("""    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */""",
    """    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */
    alignment:function(){bimAlignmentCommand();},                /* __acad3dV127 */
    profileview:function(){bimStartProfileViewTool();},
    stationoffset:function(){bimStartStationTool();},""")
rep("""      {t:'Site',small:['bim:property','bim:propshape','bim:truenorth']}   /* __acad3dV103 */""",
    """      {t:'Site',small:['bim:property','bim:propshape','bim:truenorth','bim:alignment']}   /* __acad3dV103; __acad3dV127: Alignment */""")
rep("""    'bim:truenorth':ric(""", """    'bim:alignment':ric('<path d="M3 19c5 0 5-7 9-7s4-7 9-7" stroke-dasharray="6 2 1.5 2"/><path d="M6 17.5l1 2M11 13l1.6 1.4M16 7.2l.6 1.8"/>'),   /* __acad3dV127 */
    'bim:truenorth':ric(""")
rep("""'bim:truenorth':'True North',""", """'bim:truenorth':'True North','bim:alignment':'Alignment',""")
rep("""    if(act==='bim:truenorth'){openTrueNorthDlg();return;}""", """    if(act==='bim:truenorth'){openTrueNorthDlg();return;}
    if(act==='bim:alignment'){bimAlignmentCommand();return;}            /* __acad3dV127 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
