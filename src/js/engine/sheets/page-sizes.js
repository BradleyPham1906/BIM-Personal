import { bimEsc } from '../layers/layer-manager.js';
import { bimStd } from '../standards/registry.js';
import { SHEET_SIZES } from './sheets.js';


  /* ================= __acad3dV174c: pages, from the standards registry =================
     docs/research/research-presentation-boards.md, 4.5, 5.5 (D12 to D14). Every size is a registry record with its
     edition (paper.iso216, paper.ansi, paper.arch), stored once, short side by long side, and turned by an
     orientation. The gallery lists ISO A0 to A4, ANSI A to E and Architectural A to E1 (D13). A key is
     'family-name' ('iso-A3', 'ansi-D', 'arch-E1'); an orientation 'l' or 'p'. ISO 5457 draws A0 to A3 landscape and
     A4 portrait only: another orientation is allowed and said to be outside it (D14). The sheets' old V116 sizes stay
     readable: 'ANSI-D' was always 24 x 36 in, which is Arch D, and is now called so (D12). */
  function bimPgFamilies(){
    return [['iso','ISO A','paper.iso216',['A0','A1','A2','A3','A4']],['ansi','ANSI','paper.ansi',['A','B','C','D','E']],
      ['arch','Architectural','paper.arch',['A','B','C','D','E1','E']]];
  }
  function bimPgFamily(f){var L=bimPgFamilies(),i;for(i=0;i<L.length;i++)if(L[i][0]===f)return L[i];return null;}
  /* {key, fam, name, label, s (short mm), l (long mm), topic} or null */
  function bimPgSize(key){
    var m=/^(iso|ansi|arch)-([A-Z0-9]{1,3})$/.exec(String(key||'')),F,v;
    if(!m)return null;
    F=bimPgFamily(m[1]);
    if(!F||F[3].indexOf(m[2])<0)return null;
    v=bimStd(F[2],m[2]);
    if(!v||v.length!==2)return null;
    return {key:key,fam:m[1],name:m[2],label:(m[1]==='iso'?'':F[1]+' ')+m[2],s:v[0],l:v[1],topic:F[2]};
  }
  /* width and height in mm for an orientation */
  function bimPgDims(key,o){
    var P=bimPgSize(key);
    if(!P)return null;
    return o==='p'?{w:P.s,h:P.l}:{w:P.l,h:P.s};
  }
  function bimPgInches(mm){var v=Math.round(mm/25.4*100)/100;return String(v);}
  function bimPgLabel(key,o){
    var P=bimPgSize(key);
    if(!P)return '';
    var d=bimPgDims(key,o),inch=P.fam!=='iso';
    return P.label+(o==='p'?' portrait':' landscape')+' ('+(inch?bimPgInches(d.w)+' x '+bimPgInches(d.h)+' in':Math.round(d.w)+' x '+Math.round(d.h)+' mm')+')';
  }
  /* ISO 5457: A0 to A3 landscape, A4 portrait (D14) */
  function bimPgIso5457Ok(key,o){
    var P=bimPgSize(key);
    if(!P||P.fam!=='iso')return false;
    return P.name==='A4'?o==='p':o!=='p';
  }
  /* ---- a board's page ---- */
  function bimPgValid(p){
    if(!p||typeof p!=='object'||!bimPgSize(p.key))return null;
    return {key:p.key,o:p.o==='p'?'p':'l'};
  }
  /* {key, o, w, h, label} of a board with a page, or null (a board without one flows, as before V174) */
  function bimPgBoardPage(B){
    var p=B&&B.page,d;
    if(!p||!p.key)return null;
    d=bimPgDims(p.key,p.o);
    if(!d)return null;
    return {key:p.key,o:p.o,w:d.w,h:d.h,label:bimPgLabel(p.key,p.o)};
  }
  /* ---- the sheets: a size from the gallery as a sheet size, 'pg:iso-A3:l', made known to SHEET_SIZES ---- */
  /* a sheet size already known at exactly this size keeps its V116 key ('ANSI-B-L'), so nothing that reads it changes */
  function bimPgSheetKey(key,o){
    var d=bimPgDims(key,o),k;
    if(d)for(k in SHEET_SIZES)if(SHEET_SIZES.hasOwnProperty(k)&&k!=='Custom'&&!/^pg:/.test(k)&&Math.abs(SHEET_SIZES[k].w-d.w)<0.01&&Math.abs(SHEET_SIZES[k].h-d.h)<0.01)return k;
    return 'pg:'+key+':'+(o==='p'?'p':'l');
  }
  function bimPgEnsureSheetSize(sk){
    var m=/^pg:([a-z]+-[A-Z0-9]+):([lp])$/.exec(String(sk||'')),d;
    if(SHEET_SIZES[sk])return true;
    if(!m)return false;
    d=bimPgDims(m[1],m[2]);
    if(!d)return false;
    SHEET_SIZES[sk]={label:bimPgLabel(m[1],m[2]),w:d.w,h:d.h};
    return true;
  }
  /* ---- the gallery: the families, each size as a card drawn to scale; picked with its orientation ---- */
  function bimPgGalleryHtml(cur,o){
    var h='<div class="a3d-pgg" role="radiogroup" aria-label="Page size">';
    bimPgFamilies().forEach(function(F){
      h+='<div class="a3d-pggf"><div class="a3d-pggh">'+bimEsc(F[1])+'</div><div class="a3d-pggrow">';
      F[3].forEach(function(n){
        var key=F[0]+'-'+n,P=bimPgSize(key),d,sc,on=key===cur;
        if(!P)return;
        d=bimPgDims(key,o);sc=46/1219.2;
        h+='<button type="button" class="a3d-pggc'+(on?' on':'')+'" role="radio" aria-checked="'+on+'" data-pgkey="'+key+'" title="'+bimEsc(bimPgLabel(key,o))+'">'+
          '<span class="a3d-pggp" style="width:'+Math.max(6,Math.round(d.w*sc))+'px;height:'+Math.max(6,Math.round(d.h*sc))+'px"></span><span class="a3d-pggn">'+bimEsc(P.label)+'</span></button>';
      });
      h+='</div></div>';
    });
    return h+'</div><div class="a3d-pggo" role="group" aria-label="Orientation">'+
      '<label><input type="radio" name="a3dpgo" value="l"'+(o!=='p'?' checked':'')+'> Landscape</label> '+
      '<label><input type="radio" name="a3dpgo" value="p"'+(o==='p'?' checked':'')+'> Portrait</label></div>'+
      '<div class="a3d-pggs" data-pgsay="1">'+bimEsc(cur?bimPgLabel(cur,o)+(bimPgSize(cur)&&bimPgSize(cur).fam==='iso'&&!bimPgIso5457Ok(cur,o)?': not to ISO 5457, which draws A0 to A3 landscape and A4 portrait':''):'')+'</div>';
  }
  /* wires a gallery inside root: picking a card or an orientation; onPick(key, o) */
  function bimPgGalleryWire(root,cur,o,onPick){
    var st={key:cur,o:o};
    function redraw(){
      var g=root.querySelector('[data-pggal]');
      if(g)g.innerHTML=bimPgGalleryHtml(st.key,st.o);
      if(onPick)onPick(st.key,st.o);
    }
    root.addEventListener('click',function(ev){var c=ev.target&&ev.target.closest?ev.target.closest('[data-pgkey]'):null;if(!c||!root.contains(c))return;st.key=c.getAttribute('data-pgkey');redraw();});
    root.addEventListener('change',function(ev){var t=ev.target;if(t&&t.name==='a3dpgo'){st.o=t.value;redraw();}});
    return st;
  }
export {
  bimPgBoardPage, bimPgDims, bimPgEnsureSheetSize, bimPgGalleryHtml, bimPgGalleryWire, bimPgIso5457Ok,
  bimPgLabel, bimPgSheetKey, bimPgSize, bimPgValid
};
