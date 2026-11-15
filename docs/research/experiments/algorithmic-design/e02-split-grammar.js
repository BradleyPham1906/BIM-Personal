// e02 and e03: a split grammar in plain ES5 with no geometry kernel (H2), and what happens to the
// identity of generated shapes when a parameter changes (H3). Data for a research note, never a suite.
// Run: node docs/research/experiments/algorithmic-design/e02-split-grammar.js
'use strict';
// --- the grammar core -------------------------------------------------------------------------
// A shape: {rule, id, o:[x,y,z] origin, ax:[u,v,n] unit axes, s:[su,sv,sn] sizes}. A box scope.
// A rule: function(shape, P) -> [child shapes] or null for a terminal. Sizes in a split:
//   number = absolute; {rel:r} = r times the scope's size (Esri's '); {fl:f} = floating (Esri's ~):
//   the floating parts share what the absolute and relative parts leave, in proportion.
function resolve(len, sizes){
  var fixed=0, fl=0, i, out=[];
  for(i=0;i<sizes.length;i++){ var z=sizes[i];
    if(typeof z==='number') fixed+=z; else if(z.rel!=null) fixed+=z.rel*len; else fl+=z.fl; }
  var k=fl>0 ? Math.max(0,len-fixed)/fl : 0;
  for(i=0;i<sizes.length;i++){ z=sizes[i];
    out.push(typeof z==='number' ? z : z.rel!=null ? z.rel*len : z.fl*k); }
  return out;                      // not clipped here: the caller clips what overruns the scope
}
function child(sh, axis, at, size, rule, idx){
  var o=sh.o.slice(), s=sh.s.slice(), a=sh.ax[axis];
  o[0]+=a[0]*at; o[1]+=a[1]*at; o[2]+=a[2]*at; s[axis]=size;
  return {rule:rule, id:sh.id+'/'+rule+'['+idx+']', o:o, ax:sh.ax, s:s};
}
// split(shape, axis, [[size, rule], ...]) : one pass; parts that overrun the scope are cut or dropped
function split(sh, axis, parts){
  var len=sh.s[axis], sz=resolve(len, parts.map(function(p){return p[0];})), at=0, out=[], i, n={};
  for(i=0;i<parts.length;i++){ var w=Math.min(sz[i], len-at); if(w<=1e-9) break;
    var r=parts[i][1], k=n[r]||0; n[r]=k+1; out.push(child(sh, axis, at, w, r, k)); at+=w; }
  return out;
}
// repeat(shape, axis, size, rule, mode): 'ceil' as Mueller et al. 2006 print it; 'round' the nearest
// count (least stretching, as Esri describes the result without printing the rule). At least one.
function repeat(sh, axis, size, rule, mode){
  var len=sh.s[axis], n=Math.max(1, mode==='round' ? Math.round(len/size) : Math.ceil(len/size-1e-9));
  var w=len/n, out=[], i; for(i=0;i<n;i++) out.push(child(sh, axis, i*w, w, rule, i)); return out;
}
// component split of a box into its four side faces, each a thin scope lying on the face
function sides(sh, rule){
  var u=sh.ax[0], v=sh.ax[1], n=sh.ax[2], s=sh.s, o=sh.o, neg=function(a){return [-a[0],-a[1],-a[2]];};
  function add(a,b,k){ return [a[0]+b[0]*k, a[1]+b[1]*k, a[2]+b[2]*k]; }
  var f=[ {name:'front', o:o, ax:[u,n,neg(v)], s:[s[0],s[2],0]},
          {name:'right', o:add(o,u,s[0]), ax:[v,n,u], s:[s[1],s[2],0]},
          {name:'back',  o:add(add(o,u,s[0]),v,s[1]), ax:[neg(u),n,v], s:[s[0],s[2],0]},
          {name:'left',  o:add(o,v,s[1]), ax:[neg(v),n,neg(u)], s:[s[1],s[2],0]} ];
  return f.map(function(x){ return {rule:rule, id:sh.id+'/'+rule+'.'+x.name, o:x.o, ax:x.ax, s:x.s}; });
}
function derive(axiom, rules, P, limit){
  var open=[axiom], leaves=[], steps=0;
  while(open.length){ var sh=open.pop(), r=rules[sh.rule], kids=r ? r(sh, P) : null;
    if(++steps>limit) return {error:'more than '+limit+' steps'};
    if(!kids) leaves.push(sh); else for(var i=kids.length-1;i>=0;i--) open.push(kids[i]); }
  return {leaves:leaves, steps:steps};
}
// --- CORE ENDS (line count reported below) -----------------------------------------------------
// A building: a box mass, its sides, floors, bays, and in each bay a wall panel with a window.
var rules={
  Mass:   function(sh){ return sides(sh,'Facade'); },
  Facade: function(sh,P){ return split(sh,1,[[P.ground,'Ground'],[{fl:1},'Upper']]); },
  Ground: function(sh,P){ return repeat(sh,0,P.bay,'Shopfront',P.mode); },
  Upper:  function(sh,P){ return repeat(sh,1,P.floor,'Floor',P.mode); },
  Floor:  function(sh,P){ return repeat(sh,0,P.bay,'Bay',P.mode); },
  Bay:    function(sh,P){ return split(sh,0,[[{fl:1},'Pier'],[P.win,'Col'],[{fl:1},'Pier']]); },
  Col:    function(sh,P){ return split(sh,1,[[P.sill,'Spandrel'],[P.winH,'Window'],[{fl:1},'Spandrel']]); }
};
function building(P){ return derive({rule:'Mass', id:'Mass', o:[0,0,0], ax:[[1,0,0],[0,1,0],[0,0,1]],
  s:[P.w,P.d,P.h]}, rules, P, 1e6); }
var base={w:9.6, d:9.6, h:4.5+10*3.5, ground:4.5, floor:3.5, bay:1.2, win:0.8, sill:0.9, winH:1.6, mode:'ceil'};
function count(leaves){ var c={}; leaves.forEach(function(l){ c[l.rule]=(c[l.rule]||0)+1; }); return c; }
function med(a){ a=a.slice().sort(function(x,y){return x-y;}); return a[Math.floor(a.length/2)]; }
function timeIt(fn){ var t=[], i, s; for(i=0;i<200;i++) fn();
  for(i=0;i<200;i++){ s=process.hrtime.bigint(); fn(); t.push(Number(process.hrtime.bigint()-s)/1e6); } return med(t); }
function clone(o, ch){ var c={}, k; for(k in o) c[k]=o[k]; for(k in ch) c[k]=ch[k]; return c; }

var out=[], src=require('fs').readFileSync(__filename,'utf8');
var core=src.slice(src.indexOf('// --- the grammar core'), src.indexOf('// --- CORE ENDS')).split('\n').length;
out.push('node '+process.version+'; the grammar core is '+core+' lines of ES5');
var r0=building(base);
out.push('');
out.push('e02. One facade of 8 bays by 10 upper storeys and a ground floor, on four sides of a 9.6 m box:');
out.push('leaves '+r0.leaves.length+', derivation steps '+r0.steps+', by rule '+JSON.stringify(count(r0.leaves)));
out.push('median of 200 derivations: '+timeIt(function(){ building(base); }).toFixed(3)+' ms');
var big=clone(base,{w:96, d:48, h:4.5+40*3.5}), rb=building(big);
out.push('a 96 by 48 m, 40-storey box: leaves '+rb.leaves.length+', median '+timeIt(function(){ building(big); }).toFixed(3)+' ms');

// e03: identity. Tag some windows by hand (by id), change a parameter, see where each tag lands.
function windows(P){ var m={}; building(P).leaves.forEach(function(l){ if(l.rule==='Window') m[l.id]=l; }); return m; }
function centre(l){ return [l.o[0]+l.ax[0][0]*l.s[0]/2+l.ax[1][0]*l.s[1]/2, l.o[1]+l.ax[0][1]*l.s[0]/2+l.ax[1][1]*l.s[1]/2,
  l.o[2]+l.ax[0][2]*l.s[0]/2+l.ax[1][2]*l.s[1]/2]; }
function compare(name, P1){
  var a=windows(base), b=windows(P1), ids=Object.keys(a), kept=0, moved=[], lost=0;
  ids.forEach(function(id){ if(!b[id]){ lost++; return; } kept++;
    var p=centre(a[id]), q=centre(b[id]); moved.push(Math.sqrt((p[0]-q[0])*(p[0]-q[0])+(p[1]-q[1])*(p[1]-q[1])+(p[2]-q[2])*(p[2]-q[2]))); });
  var far=moved.filter(function(d){ return d>0.6; }).length;      // more than half a bay away
  out.push('| '+name+' | '+ids.length+' | '+Object.keys(b).length+' | '+kept+' | '+lost+' | '+
    (Object.keys(b).length-kept)+' | '+(moved.length?med(moved).toFixed(2):'-')+' | '+far+' |');
}
out.push('');
out.push('e03. Windows before and after one change; an id is the path of rule names and indexes.');
out.push('');
out.push('| change | windows before | after | ids kept | ids lost | new ids | median move of a kept id (m) | kept ids that moved over 0.6 m |');
out.push('|---|---|---|---|---|---|---|---|');
compare('window 0.8 to 1.0 m wide (counts the same)', clone(base,{win:1.0}));
compare('sill 0.9 to 1.1 m (counts the same)', clone(base,{sill:1.1}));
compare('building 9.6 to 10.0 m wide (8 bays become 9 on two sides: ceil)', clone(base,{w:10.0}));
compare('bay 1.2 to 1.0 m (8 bays become 10)', clone(base,{bay:1.0}));
compare('building 9.6 to 12.0 m wide (8 bays become 10 on two sides)', clone(base,{w:12.0}));
compare('one storey more (10 to 11)', clone(base,{h:base.h+3.5}));
compare('ground floor 4.5 to 5.5 m, height kept (10 storeys stay 10, each shorter)', clone(base,{ground:5.5}));
// the repeat rule itself: where ceil and round disagree
out.push('');
out.push('The repeat count, 3.5 m storeys in a given height: ceil (the 2006 paper) against round (least stretching):');
out.push('');
out.push('| height (m) | ceil: count, each (m) | round: count, each (m) |');
out.push('|---|---|---|');
[35, 35.1, 36.7, 36.8, 38.4, 1.0].forEach(function(h){ var c=Math.max(1,Math.ceil(h/3.5-1e-9)), r=Math.max(1,Math.round(h/3.5));
  out.push('| '+h+' | '+c+', '+(h/c).toFixed(3)+' | '+r+', '+(h/r).toFixed(3)+' |'); });
console.log(out.join('\n'));
