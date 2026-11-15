// e04: which search does best with a small budget? (H6) A toy with the app's kind of objective:
// place a rectangular block (x, y, width, depth, rotation, storeys) on an L-shaped lot to get the most
// floor area, under a floor-area cap, a height plane rising from the street, and staying inside the lot.
// Data for a research note, never a suite. The published benchmarks are the evidence; this only checks
// whether a problem of this app's kind behaves the same way.
// Run: node docs/research/experiments/algorithmic-design/e04-optimise.js
'use strict';
function rng(seed){ return function(){ seed|=0; seed=seed+0x6D2B79F5|0; var t=Math.imul(seed^seed>>>15,1|seed);
  t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
var LOT=[[0,0],[40,0],[40,18],[22,18],[22,45],[0,45]], LOTAREA=40*18+22*27, FARCAP=2.6;   // street along y=0
function inside(p){ var c=false, i, j; for(i=0,j=LOT.length-1;i<LOT.length;j=i++){ var a=LOT[i], b=LOT[j];
  if((a[1]>p[1])!==(b[1]>p[1]) && p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]) c=!c; } return c; }
// x in [0,1]^6 -> the design. Storeys are whole numbers (a mixed problem).
function decode(x){ return {cx:x[0]*40, cy:x[1]*45, w:6+x[2]*34, d:6+x[3]*34, th:x[4]*Math.PI/2, n:1+Math.round(x[5]*14)}; }
function objective(x){
  var g=decode(x), c=Math.cos(g.th), s=Math.sin(g.th), out=0, minY=1e9, i, k, m;
  // sample the block's edge (corners and points between) so a re-entrant corner cannot hide inside it
  for(i=-4;i<=4;i++) for(k=-4;k<=4;k++){ if(Math.abs(i)!==4 && Math.abs(k)!==4) continue;
    var px=g.cx+c*g.w*i/8-s*g.d*k/8, py=g.cy+s*g.w*i/8+c*g.d*k/8;
    if(!inside([px,py])) out++; if(py<minY) minY=py; }
  var h=g.n*3.5, plane=10.5+1.0*Math.max(0,minY), gfa=g.w*g.d*g.n, pen=0;
  pen+=out*400; if(h>plane) pen+=(h-plane)*300;
  if(gfa>FARCAP*LOTAREA) pen+=(gfa-FARCAP*LOTAREA)*2;
  return gfa-pen;                                    // to maximise
}
var D=6;
function clamp(v){ return v<0?0:v>1?1:v; }
function randomSearch(budget, r){ var best=-1e18, i, k, x; for(i=0;i<budget;i++){ x=[]; for(k=0;k<D;k++) x.push(r());
  best=Math.max(best, objective(x)); } return best; }
function latin(budget, r){ var cols=[], k, i, best=-1e18; for(k=0;k<D;k++){ var p=[]; for(i=0;i<budget;i++) p.push(i);
    for(i=budget-1;i>0;i--){ var j=Math.floor(r()*(i+1)), t=p[i]; p[i]=p[j]; p[j]=t; } cols.push(p); }
  for(i=0;i<budget;i++){ var x=[]; for(k=0;k<D;k++) x.push((cols[k][i]+r())/budget); best=Math.max(best, objective(x)); } return best; }
// Hooke and Jeeves pattern search, restarted from the best of a small random sample when the step is spent
function pattern(budget, r){ var used=0, best=-1e18;
  function f(x){ used++; var v=objective(x); if(v>best) best=v; return v; }
  while(used<budget){ var x=null, fx=-1e18, i, k; for(i=0;i<8 && used<budget;i++){ var c=[]; for(k=0;k<D;k++) c.push(r()); var fc=f(c); if(fc>fx){ fx=fc; x=c; } }
    var step=0.25; while(step>0.01 && used<budget){ var moved=false;
      for(k=0;k<D && used<budget;k++){ var sgn; for(sgn=-1;sgn<=1 && used<budget;sgn+=2){ var y=x.slice(); y[k]=clamp(y[k]+sgn*step);
        if(y[k]===x[k]) continue; var fy=f(y); if(fy>fx){ x=y; fx=fy; moved=true; break; } } }
      if(!moved) step/=2; } }
  return best; }
// Nelder and Mead, standard coefficients, restarted at random when the simplex has shrunk
function nelderMead(budget, r){ var used=0, best=-1e18;
  function f(x){ used++; var y=x.map(clamp), v=objective(y); if(v>best) best=v; return -v; }
  while(used<budget){ var S=[], i, k; var x0=[]; for(k=0;k<D;k++) x0.push(r()); S.push({x:x0, f:f(x0)});
    for(i=0;i<D && used<budget;i++){ var xi=x0.slice(); xi[i]=clamp(xi[i]+(xi[i]>0.5?-0.25:0.25)); S.push({x:xi, f:f(xi)}); }
    var it=0; while(used<budget && it++<400){ S.sort(function(a,b){return a.f-b.f;}); var n=S.length-1;
      if(Math.abs(S[n].f-S[0].f)<1e-3) break;
      var c=[]; for(k=0;k<D;k++){ c.push(0); for(i=0;i<n;i++) c[k]+=S[i].x[k]/n; }
      var pt=function(t){ return c.map(function(v,k2){ return v+t*(S[n].x[k2]-v); }); };
      var xr=pt(-1), fr=f(xr);
      if(fr<S[0].f){ var xe=pt(-2), fe=f(xe); S[n]=fe<fr?{x:xe,f:fe}:{x:xr,f:fr}; }
      else if(fr<S[n-1].f) S[n]={x:xr,f:fr};
      else { var xc=pt(0.5), fc2=f(xc); if(fc2<S[n].f) S[n]={x:xc,f:fc2};
        else for(i=1;i<=n && used<budget;i++){ S[i].x=S[i].x.map(function(v,k2){ return S[0].x[k2]+0.5*(v-S[0].x[k2]); }); S[i].f=f(S[i].x); } } } }
  return best; }
// A plain genetic algorithm: tournament of 2, uniform crossover, Gaussian mutation, one elite
function genetic(budget, r, pop){ var P=[], i, k, used=0, best=-1e18;
  function f(x){ used++; var v=objective(x); if(v>best) best=v; return v; }
  function gauss(){ return Math.sqrt(-2*Math.log(r()+1e-12))*Math.cos(2*Math.PI*r()); }
  for(i=0;i<pop && used<budget;i++){ var x=[]; for(k=0;k<D;k++) x.push(r()); P.push({x:x, f:f(x)}); }
  while(used<budget){ var Q=[]; P.sort(function(a,b){return b.f-a.f;}); Q.push(P[0]);
    while(Q.length<pop && used<budget){ var pick=function(){ var a=P[Math.floor(r()*P.length)], b=P[Math.floor(r()*P.length)]; return a.f>b.f?a:b; };
      var m=pick(), d=pick(), c=[]; for(k=0;k<D;k++){ var v=r()<0.5?m.x[k]:d.x[k]; if(r()<1/D*2) v=clamp(v+gauss()*0.1); c.push(v); }
      Q.push({x:c, f:f(c)}); } P=Q; }
  return best; }
function med(a){ a=a.slice().sort(function(x,y){return x-y;}); return a[Math.floor(a.length/2)]; }
function q(a,p){ a=a.slice().sort(function(x,y){return x-y;}); return a[Math.floor((a.length-1)*p)]; }
// a reference optimum: a long pattern search from many starts
var ref=-1e18, s; for(s=0;s<40;s++) ref=Math.max(ref, pattern(20000, rng(9000+s)));
var methods={'random':randomSearch, 'Latin hypercube':latin, 'pattern search (Hooke-Jeeves), restarts':pattern,
  'Nelder-Mead, restarts':nelderMead, 'genetic, population 20':function(b,r){return genetic(b,r,20);},
  'genetic, population 50':function(b,r){return genetic(b,r,50);}};
var budgets=[50,100,200,500,2000], SEEDS=51, out=[];
out.push('node '+process.version+'; the cap allows '+(FARCAP*LOTAREA).toFixed(0)+' m2; best found by a long search: '+ref.toFixed(0)+' m2');
out.push('Median over '+SEEDS+' seeds of the best floor area found, as a percentage of that best (lower quartile in brackets).');
out.push('');
out.push('| method | '+budgets.map(function(b){return b+' runs';}).join(' | ')+' |');
out.push('|---|'+budgets.map(function(){return '---';}).join('|')+'|');
Object.keys(methods).forEach(function(name){ var row='| '+name+' |';
  budgets.forEach(function(b){ var v=[], i; for(i=0;i<SEEDS;i++) v.push(100*methods[name](b, rng(100+i))/ref);
    row+=' '+med(v).toFixed(1)+' ('+q(v,0.25).toFixed(1)+') |'; }); out.push(row); });
console.log(out.join('\n'));
