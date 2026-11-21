import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimIntRelation } from '../bim/interiors.js';
import { bimIntBuilding, bimIntProgOf, bimIntReport, bimIntWarnOnce } from '../bim/interiors-model.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow, bimPropText } from './palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV179: the Programme in Properties =================
     docs/work-orders/v179/SPEC.md part 1 and WO-10. With nothing selected, Properties' Project tab holds the active
     building's programme: each use, how many, the area range and why; under it the relations between uses. Each line
     carries what the model says of it (bim/interiors-model.js): ok, short, over, area out of range; met, not met or
     not evaluated, with the reason. One edit is one undo step; the programme is saved with the building. The tables
     scroll sideways on a phone. */
  var BIM_INT_RELS=['next','near','apart','access','visual','acoustic','secure','sequence'];
  var BIM_INT_REL_WORDS={next:'next to',near:'near',apart:'apart from',access:'reached from',visual:'seen from',acoustic:'quiet from',secure:'secure from',sequence:'before'};
  var BIM_INT_KINDS=['required','desired','forbidden'];
  function bimIntOpts(list,cur,words){
    return list.map(function(v){return '<option value="'+bimEsc(v)+'"'+(v===cur?' selected':'')+'>'+bimEsc(words&&words[v]?words[v]:v)+'</option>';}).join('');
  }
  function bimIntNumIn(key,v,min){
    return '<input type="number" step="any"'+(min!==undefined?' min="'+min+'"':'')+' data-intprog="'+bimEsc(key)+'" value="'+(v===null||v===undefined?'':bimEsc(String(v)))+'">';
  }
  function bimIntMatchText(m){
    if(!m)return '';
    if(m.status==='short')return 'short: '+m.have+' of '+m.need;
    if(m.status==='over')return 'over: '+m.have+' of '+m.need;
    if(m.status==='area')return 'area out of range: '+m.offArea.length+' of '+m.have;
    return 'ok: '+m.have+' of '+m.need;
  }
  function bimIntPill(st,txt){
    var c=st==='ok'||st==='met'?'ok':(st==='not evaluated'?'ne':'bad');
    return '<span class="a3d-int-st '+c+'">'+bimEsc(txt)+'</span>';
  }
  function bimIntPropsHtml(){
    var rep=bimIntReport(),h='',i,it,r,ck,uses=[],m;
    if(!rep.building)return bimPropText('Programme','No building');
    bimIntWarnOnce(rep.warnings);
    h+=bimPropText('Building',(rep.building.name||'Building')+': '+rep.rooms.length+' room'+(rep.rooms.length===1?'':'s')+' read');
    for(i=0;i<rep.warnings.length;i++)h+='<div class="a3d-prow ro"><div class="a3d-pval a3d-int-warn" role="note">'+bimEsc(rep.warnings[i])+'</div></div>';
    h+='<div class="a3d-int-scroll"><table class="a3d-int-tbl" aria-label="Programme"><thead><tr><th>Use</th><th>Count</th><th>Min m²</th><th>Max m²</th><th>Why</th><th>In the model</th><th></th></tr></thead><tbody>';
    for(i=0;i<rep.items.length;i++){
      it=rep.items[i];m=rep.matches[i];
      if(it.use&&uses.indexOf(it.use)<0)uses.push(it.use);
      h+='<tr><td><input type="text" data-intprog="i:'+bimEsc(it.id)+':use" value="'+bimEsc(it.use)+'" aria-label="Use"></td>'+
        '<td>'+bimIntNumIn('i:'+it.id+':count',it.count,1)+'</td>'+
        '<td>'+bimIntNumIn('i:'+it.id+':areaMin',it.areaMin,0)+'</td>'+
        '<td>'+bimIntNumIn('i:'+it.id+':areaMax',it.areaMax,0)+'</td>'+
        '<td><input type="text" data-intprog="i:'+bimEsc(it.id)+':rationale" value="'+bimEsc(it.rationale)+'" aria-label="Why"></td>'+
        '<td>'+bimIntPill(m.status,bimIntMatchText(m))+'</td>'+
        '<td><button type="button" class="a3d-bdel" data-intprogact="idel:'+bimEsc(it.id)+'" title="Remove this use">×</button></td></tr>';
    }
    if(!rep.items.length)h+='<tr><td colspan="7" class="a3d-int-none">No uses yet. A room is matched to a use by its usage, else by its name.</td></tr>';
    h+='</tbody></table></div>';
    h+=bimPropRow('','<button type="button" class="a3d-pedit" data-intprogact="iadd">Add use</button>');
    h+='<div class="a3d-int-scroll"><table class="a3d-int-tbl" aria-label="Relations"><thead><tr><th>Use</th><th>Relation</th><th>Use</th><th>Kind</th><th>Within m</th><th>Status</th><th>In the model</th><th></th></tr></thead><tbody>';
    for(i=0;i<rep.relations.length;i++){
      r=rep.relations[i];ck=rep.checks[i];
      h+='<tr><td><select data-intprog="r:'+i+':a" aria-label="First use">'+bimIntOpts(uses.indexOf(r.a)<0?[r.a].concat(uses):uses,r.a)+'</select></td>'+
        '<td><select data-intprog="r:'+i+':rel" aria-label="Relation">'+bimIntOpts(BIM_INT_RELS,r.rel,BIM_INT_REL_WORDS)+'</select></td>'+
        '<td><select data-intprog="r:'+i+':b" aria-label="Second use">'+bimIntOpts(uses.indexOf(r.b)<0?[r.b].concat(uses):uses,r.b)+'</select></td>'+
        '<td><select data-intprog="r:'+i+':kind" aria-label="Kind">'+bimIntOpts(BIM_INT_KINDS,r.kind)+'</select></td>'+
        '<td>'+(r.rel==='near'?bimIntNumIn('r:'+i+':nearM',r.nearM,0):'')+'</td>'+
        '<td><select data-intprog="r:'+i+':status" aria-label="Status">'+bimIntOpts(['suggested','approved','rejected'],r.status)+'</select></td>'+
        '<td>'+bimIntPill(ck.status,ck.status+': '+ck.why)+'</td>'+
        '<td><button type="button" class="a3d-bdel" data-intprogact="rdel:'+i+'" title="Remove this relation">×</button></td></tr>';
    }
    if(!rep.relations.length)h+='<tr><td colspan="8" class="a3d-int-none">No relations yet. Near is a route by the doors, room centre to centre.</td></tr>';
    h+='</tbody></table></div>';
    h+=bimPropRow('','<button type="button" class="a3d-pedit" data-intprogact="radd"'+(uses.length<2?' disabled title="Two uses first"':'')+'>Add relation</button>');
    return h;
  }
  /* one change to the programme, one undo step; refused with its reason, nothing changed */
  function bimIntProgEdit(fn){
    var b=bimIntBuilding(),c,err;
    if(!b){a3dToast('There is no building');return false;}
    c=JSON.parse(JSON.stringify(bimIntProgOf(b)));
    err=fn(c);
    if(err){a3dToast(err);refreshProps();return false;}
    pushUndo();
    b.programme=bimIntProgOf({programme:c});
    refreshProps();saveSoon();
    return true;
  }
  function bimIntItemIx(c,id){var i;for(i=0;i<c.items.length;i++)if(c.items[i].id===id)return i;return -1;}
  function bimIntProgChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-intprog]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-intprog').split(':'),v=f.value;
    if(k[0]==='i'){
      var fld=k[k.length-1],id=k.slice(1,k.length-1).join(':');
      return bimIntProgEdit(function(c){
        var ix=bimIntItemIx(c,id),it,old,x,j;
        if(ix<0)return 'That use is gone';
        it=c.items[ix];
        if(fld==='use'){
          x=String(v||'').replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,60);
          if(!x)return 'A use needs a name';
          for(j=0;j<c.items.length;j++)if(j!==ix&&c.items[j].use===x)return 'There is already a use called '+x;
          old=it.use;it.use=x;
          for(j=0;j<c.relations.length;j++){if(c.relations[j].a===old)c.relations[j].a=x;if(c.relations[j].b===old)c.relations[j].b=x;}
          return;
        }
        if(fld==='rationale'){it.rationale=String(v||'').slice(0,200);return;}
        x=v===''?null:parseFloat(v);
        if(fld==='count'){if(!(x>=1))return 'A count is 1 or more';it.count=Math.floor(x);return;}
        if(fld==='areaMin'||fld==='areaMax'){if(x!==null&&!(x>=0))return 'An area is a number, 0 or more';it[fld]=x;return;}
        return 'Unknown field';
      });
    }
    if(k[0]==='r'){
      var ri=parseInt(k[1],10),rf=k[2];
      return bimIntProgEdit(function(c){
        var r=c.relations[ri],x;
        if(!r)return 'That relation is gone';
        if(rf==='nearM'){x=parseFloat(v);if(!(x>0))return 'A distance is above 0 m';r.nearM=x;return;}
        r[rf]=v;
        if(!bimIntRelation(r))return 'A relation joins two different uses';
      });
    }
    return false;
  }
  function bimIntProgClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-intprogact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-intprogact'),cut=a.indexOf(':'),act=cut<0?a:a.slice(0,cut),arg=cut<0?'':a.slice(cut+1);
    if(act==='iadd')return bimIntProgEdit(function(c){
      var n=c.items.length+1,nm='Use '+n,j;
      for(j=0;j<c.items.length;j++)if(c.items[j].use===nm){nm='Use '+(++n);j=-1;}
      c.items.push({id:'prg-'+Date.now().toString(36)+'-'+(A3D.seq++),use:nm,count:1,areaMin:null,areaMax:null,rationale:''});
    });
    if(act==='idel')return bimIntProgEdit(function(c){
      var ix=bimIntItemIx(c,arg),u;
      if(ix<0)return 'That use is gone';
      u=c.items[ix].use;c.items.splice(ix,1);
      c.relations=c.relations.filter(function(r){return r.a!==u&&r.b!==u;});
    });
    if(act==='radd')return bimIntProgEdit(function(c){
      if(c.items.length<2)return 'A relation needs two uses';
      c.relations.push({a:c.items[0].use,b:c.items[1].use,kind:'desired',rel:'next',status:'approved'});
    });
    if(act==='rdel')return bimIntProgEdit(function(c){
      var ri=parseInt(arg,10);
      if(!c.relations[ri])return 'That relation is gone';
      c.relations.splice(ri,1);
    });
    return false;
  }
export { bimIntProgChange, bimIntProgClick, bimIntPropsHtml };
