import { A3D, el } from '../core/state.js';
import { bimObjOffset } from '../drawing/plan-mode-sketch.js';
import { bimInquiryShow } from './inquiry.js';
import { bimTrimNum, bimUnitDef, bimUnitDp } from '../properties/palette.js';
import { bimFlattenPoly, bimHasBulge } from '../drawing/arc-storage.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV262: MASSPROP, COUNT and CAL (D8) =================
     MASSPROP (the region properties AutoCAD reports for a REGION, here for any closed outline): area, perimeter,
     centroid, the second moments about the centroid (Ixx, Iyy, Ixy), the principal moments and their direction, the
     radii of gyration. Arcs are flattened to 2 mm chords first (bimFlattenPoly), so the figures are those of the
     curve to that tolerance. COUNT: how many inserts of each block the drawing holds. CAL (QUICKCALC, QC): an
     expression calculator, read by its own parser (no eval): + - * / ^ and brackets, numbers, pi, and sqrt, abs,
     sin, cos, tan, asin, acos, atan (degrees), ln, log, round. All the arithmetic is pure, tested without a canvas. */
  /* Polygon section properties (shoelace sums); y here is the plan's second coordinate, as LIST and ID report it. */
  function bimRegionProps(pts){
    var n=pts.length,A=0,cx=0,cy=0,i,j;
    if(n<3)return null;
    for(i=0;i<n;i++){
      j=(i+1)%n;var c=pts[i][0]*pts[j][1]-pts[j][0]*pts[i][1];
      A+=c;cx+=(pts[i][0]+pts[j][0])*c;cy+=(pts[i][1]+pts[j][1])*c;
    }
    A/=2;
    if(Math.abs(A)<1e-15)return null;
    cx/=6*A;cy/=6*A;
    var Ixx=0,Iyy=0,Ixy=0;
    for(i=0;i<n;i++){
      j=(i+1)%n;
      var x0=pts[i][0]-cx,y0=pts[i][1]-cy,x1=pts[j][0]-cx,y1=pts[j][1]-cy,a=x0*y1-x1*y0;
      Ixx+=(y0*y0+y0*y1+y1*y1)*a;Iyy+=(x0*x0+x0*x1+x1*x1)*a;Ixy+=(x0*y1+2*x0*y0+2*x1*y1+x1*y0)*a;
    }
    var s=A<0?-1:1;
    Ixx=s*Ixx/12;Iyy=s*Iyy/12;Ixy=s*Ixy/24;A=Math.abs(A);
    var avg=(Ixx+Iyy)/2,R=Math.sqrt(Math.pow((Ixx-Iyy)/2,2)+Ixy*Ixy);
    var per=0;for(i=0;i<n;i++){j=(i+1)%n;per+=Math.sqrt(Math.pow(pts[j][0]-pts[i][0],2)+Math.pow(pts[j][1]-pts[i][1],2));}
    return {area:A,perimeter:per,cx:cx,cy:cy,Ixx:Ixx,Iyy:Iyy,Ixy:Ixy,I1:avg+R,I2:avg-R,
      angle:0.5*Math.atan2(-2*Ixy,Ixx-Iyy)*180/Math.PI,rx:Math.sqrt(Ixx/A),ry:Math.sqrt(Iyy/A)};
  }
  function bimMassprop(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]),rows=[],i,o,n=0;
    for(i=0;i<ids.length;i++){
      o=objById(ids[i]);if(!o)continue;
      var pts=null,bl=null;
      if(o.t==='sketch'&&o.closed!==false&&o.pts&&(o.pts.length>2||bimHasBulge(o.bulges))){pts=o.pts;bl=o.bulges||null;}
      else if(o.t==='room'||o.t==='hatch')pts=o.pts,bl=o.bulges||null;
      else if(o.bim&&(o.bim.profile||o.bim.footprint))pts=o.bim.profile||o.bim.footprint;
      if(!pts)continue;
      var q=bimObjOffset(o),P=bimRegionProps(bimFlattenPoly(pts,bl,true).map(function(p){return [p[0]+q[0],p[1]+q[2]];}));
      if(!P)continue;
      if(n)rows.push('-');
      n++;
      var U=bimUnitDef(),s=U.scale||1,L=U.label,f=function(v,k){return bimTrimNum((v*Math.pow(s,k)).toFixed(Math.max(bimUnitDp(),3)));};
      rows.push(['Object',o.name||o.id],['Area',f(P.area,2)+' '+L+'\u00b2'],['Perimeter',f(P.perimeter,1)+' '+L],
        ['Centroid','X '+f(P.cx,1)+'  Y '+f(P.cy,1)],
        ['Ixx (about centroid)',f(P.Ixx,4)+' '+L+'\u2074'],['Iyy (about centroid)',f(P.Iyy,4)+' '+L+'\u2074'],['Ixy',f(P.Ixy,4)+' '+L+'\u2074'],
        ['Principal moments',f(P.I1,4)+', '+f(P.I2,4)+' '+L+'\u2074'],['Principal direction',P.angle.toFixed(2)+'\u00b0'],
        ['Radii of gyration','X '+f(P.rx,1)+'  Y '+f(P.ry,1)+' '+L]);
    }
    if(!n){a3dToast('MASSPROP: select closed outlines, rooms, hatches or floors');return null;}
    return bimInquiryShow('Region properties',rows);
  }
  /* COUNT: inserts of each block, an insert counted once however many objects it made. */
  function bimCountBlocks(objs){
    var seen={},count={},i,o;
    for(i=0;i<objs.length;i++){
      o=objs[i];
      if(!o.blockRef||seen[o.blockRef.ins])continue;
      seen[o.blockRef.ins]=1;
      count[o.blockRef.name]=(count[o.blockRef.name]||0)+1;
    }
    return count;
  }
  function bimCountCommand(){
    var c=bimCountBlocks(A3D.objs),names=Object.keys(c).sort(),rows=[],i,tot=0;
    for(i=0;i<names.length;i++){rows.push([names[i],String(c[names[i]])]);tot+=c[names[i]];}
    if(!names.length){a3dToast('COUNT: no block inserts in the drawing');return null;}
    rows.push('-',['Total inserts',String(tot)]);
    return bimInquiryShow('Count of blocks',rows);
  }
  /* ---------- CAL ---------- */
  var BIM_CAL_FN={sqrt:Math.sqrt,abs:Math.abs,ln:Math.log,log:function(x){return Math.log(x)/Math.LN10;},round:Math.round,
    sin:function(x){return Math.sin(x*Math.PI/180);},cos:function(x){return Math.cos(x*Math.PI/180);},
    tan:function(x){return Math.tan(x*Math.PI/180);},asin:function(x){return Math.asin(x)*180/Math.PI;},
    acos:function(x){return Math.acos(x)*180/Math.PI;},atan:function(x){return Math.atan(x)*180/Math.PI;}};
  /* A recursive-descent reader: expr = term (+|- term)*, term = unary (*|/ unary)*,
     unary = -unary | +unary | power, power = atom (^ unary)?, atom = number | pi | fn(expr) | (expr). Returns {value} or {error}. */
  function bimCalEval(src){
    var s=String(src||''),i=0;
    function ws(){while(i<s.length&&/\s/.test(s[i]))i++;}
    function fail(m){throw new Error(m);}
    function expr(){var v=term();ws();while(s[i]==='+'||s[i]==='-'){var op=s[i++];var r=term();v=op==='+'?v+r:v-r;ws();}return v;}
    function term(){var v=unary();ws();while(s[i]==='*'||s[i]==='/'){var op=s[i++];var r=unary();if(op==='/'&&r===0)fail('Division by zero');v=op==='*'?v*r:v/r;ws();}return v;}
    /* a sign applies to the power after it (-2^2 is -4, as in mathematics); an exponent may carry its own sign */
    function unary(){ws();if(s[i]==='-'){i++;return -unary();}if(s[i]==='+'){i++;return unary();}return power();}
    function power(){var b=atom();ws();if(s[i]==='^'){i++;return Math.pow(b,unary());}return b;}
    function atom(){
      ws();
      if(s[i]==='('){i++;var v=expr();ws();if(s[i]!==')')fail('A bracket is not closed');i++;return v;}
      var m=/^(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)/.exec(s.slice(i));
      if(m){i+=m[1].length;return parseFloat(m[1]);}
      var w=/^[a-zA-Z]+/.exec(s.slice(i));
      if(w){
        var name=w[0].toLowerCase();i+=w[0].length;
        if(name==='pi')return Math.PI;
        if(!BIM_CAL_FN.hasOwnProperty(name))fail('Unknown name: '+w[0]);
        ws();if(s[i]!=='(')fail(w[0]+' needs brackets: '+w[0]+'(...)');
        i++;var a=expr();ws();if(s[i]!==')')fail('A bracket is not closed');i++;
        return BIM_CAL_FN[name](a);
      }
      fail(i<s.length?'Unexpected "'+s[i]+'"':'The expression ends too soon');
    }
    try{
      var v=expr();ws();
      if(i<s.length)fail('Unexpected "'+s[i]+'"');
      if(!isFinite(v))fail('The result is not a finite number');
      return {value:v};
    }catch(e){return {error:e.message};}
  }
  function openCalDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Calculator</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Expression</label><input type="text" data-a3dcal="x" maxlength="400" placeholder="(3.2+4.8)*2^2 / sqrt(16)"></div>'+
      '<div class="a3d-dlgrow"><label>Result</label><span data-a3dcal="r" style="user-select:text"></span></div>'+
      '<div class="a3d-propnote">+ - * / ^ and brackets; pi; sqrt, abs, ln, log, round; sin, cos, tan, asin, acos, atan in degrees.</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Close</button><button data-a3dlg="ok">=</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var x=d.querySelector('[data-a3dcal="x"]'),r=d.querySelector('[data-a3dcal="r"]');
    function go(){var v=bimCalEval(x.value);r.textContent=v.error?v.error:bimTrimNum(v.value.toFixed(10));}
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')go();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();go();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
    x.focus();
    return d;
  }
export { bimCountCommand, bimMassprop, openCalDlg };
