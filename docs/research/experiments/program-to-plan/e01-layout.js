// e01: can a small deterministic layout place a 12-space programme with its areas and adjacencies,
// with and without a corridor? (research-program-to-plan.md, H2 and H3). Data for a research note,
// never a suite. Plain ES5 on purpose: the engine's contract.
// Run: node docs/research/experiments/program-to-plan/e01-layout.js
'use strict';
function rng(seed){ return function(){ seed|=0; seed=seed+0x6D2B79F5|0; var t=Math.imul(seed^seed>>>15,1|seed);
  t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }

// ---- programmes ----------------------------------------------------------------------------------
// A small clinic written by hand (areas in m2; space 0 holds the entrance).
var CLINIC={names:['Waiting','Reception','Consult 1','Consult 2','Consult 3','Treatment','Staff','WC public','WC staff','Store','Office','Plant'],
  area:[40,12,14,14,14,20,16,5,5,8,12,8],
  req:[[0,1],[1,10],[0,2],[2,3],[3,4],[4,5],[5,9],[6,8],[6,10],[5,6],[11,9],[0,7]],
  bad:[[0,6],[0,11],[2,11]]};
// Random programmes: 12 spaces, areas log-uniform 6 to 60 m2, a random tree of required pairs plus 3, 3 forbidden.
function randomProgramme(seed){
  var r=rng(seed), n=12, area=[], req=[], bad=[], key={}, i, a, b;
  for(i=0;i<n;i++) area.push(Math.round(Math.exp(Math.log(6)+r()*(Math.log(60)-Math.log(6)))));
  for(i=1;i<n;i++){ a=i; b=Math.floor(r()*i); req.push([b,a]); key[b+','+a]=key[a+','+b]=1; }
  while(req.length<n+2){ a=Math.floor(r()*n); b=Math.floor(r()*n); if(a===b||key[a+','+b]) continue; req.push([a,b]); key[a+','+b]=key[b+','+a]=1; }
  while(bad.length<3){ a=Math.floor(r()*n); b=Math.floor(r()*n); if(a===b||key[a+','+b]) continue; bad.push([a,b]); key[a+','+b]=key[b+','+a]=1; }
  return {area:area, req:req, bad:bad};
}
function sum(a){ var s=0; for(var i=0;i<a.length;i++) s+=a[i]; return s; }

// ---- geometry checks ------------------------------------------------------------------------------
// rooms: [{i, x, y, w, h}] rectangles. Two rooms are adjacent when they share a wall of 1.0 m or more (a door fits).
function shared(p, q){
  var e=1e-6, ox, oy;
  if(Math.abs(p.x+p.w-q.x)<e||Math.abs(q.x+q.w-p.x)<e){ oy=Math.min(p.y+p.h,q.y+q.h)-Math.max(p.y,q.y); return oy>0?oy:0; }
  if(Math.abs(p.y+p.h-q.y)<e||Math.abs(q.y+q.h-p.y)<e){ ox=Math.min(p.x+p.w,q.x+q.w)-Math.max(p.x,q.x); return ox>0?ox:0; }
  return 0;
}
function judge(P, rooms, roomArea, corridor){
  var at={}, i, met=0, viol=0, worst=1, dev=0, reach=0, k;
  for(i=0;i<rooms.length;i++) at[rooms[i].i]=rooms[i];
  for(i=0;i<P.req.length;i++) if(shared(at[P.req[i][0]],at[P.req[i][1]])>=1) met++;
  for(i=0;i<P.bad.length;i++) if(shared(at[P.bad[i][0]],at[P.bad[i][1]])>=1) viol++;
  var scale=roomArea/sum(P.area);
  for(i=0;i<rooms.length;i++){ var r=rooms[i], asp=Math.max(r.w/r.h,r.h/r.w);
    if(asp>worst) worst=asp;
    var d=Math.abs(r.w*r.h/(P.area[r.i]*scale)-1); if(d>dev) dev=d;
    if(corridor&&shared(r,corridor)>=1) reach++; }
  return {met:met/P.req.length, viol:viol, aspect:worst, dev:dev, reach:corridor?reach/rooms.length:0};
}
function score(j){ return j.met*100 - j.viol*100 - Math.max(0,j.aspect-3)*10 - j.dev*50 + j.reach*100; }

// ---- method A and B: an ordered squarified treemap of the whole rectangle, no corridor --------------
function treemap(order, area, X, Y, W, H){
  var tot=sum(order.map(function(i){return area[i];})), k=W*H/tot, items=order.map(function(i){return {i:i,a:area[i]*k};});
  var out=[], x=X, y=Y, w=W, h=H, row=[], j=0;
  function worstOf(row, side){ var s=0, mx=0, mn=1e18, r; for(r=0;r<row.length;r++){ s+=row[r].a; mx=Math.max(mx,row[r].a); mn=Math.min(mn,row[r].a); }
    return Math.max(side*side*mx/(s*s), s*s/(side*side*mn)); }
  function place(row){ var s=0, r, off=0; for(r=0;r<row.length;r++) s+=row[r].a;
    if(w>=h){ var cw=s/h; for(r=0;r<row.length;r++){ var rh=row[r].a/cw; out.push({i:row[r].i,x:x,y:y+off,w:cw,h:rh}); off+=rh; } x+=cw; w-=cw; }
    else { var ch=s/w; for(r=0;r<row.length;r++){ var rw=row[r].a/ch; out.push({i:row[r].i,x:x+off,y:y,w:rw,h:ch}); off+=rw; } y+=ch; h-=ch; } }
  while(j<items.length){ var side=Math.min(w,h), next=row.concat([items[j]]);
    if(!row.length||worstOf(next,side)<=worstOf(row,side)){ row=next; j++; } else { place(row); row=[]; } }
  if(row.length) place(row);
  return out;
}
// ---- method C: corridor first. A corridor along the long side; rooms on both sides in one ring order -------
// (side A left to right, side B right to left, so the order stays continuous round the corridor's end).
function corridorFirst(order, area, W, D, c, depthA){
  var dA=depthA, dB=D-c-dA, tot=sum(order.map(function(i){return area[i];})), half=0, cut=order.length, i;
  for(i=0;i<order.length;i++){ if(half+area[order[i]]/2>tot*dA/(D-c)){ cut=i; break; } half+=area[order[i]]; }
  if(cut===0) cut=1; if(cut===order.length) cut=order.length-1;
  var A=order.slice(0,cut), B=order.slice(cut), out=[], x=0, sA=sum(A.map(function(i){return area[i];})), sB=sum(B.map(function(i){return area[i];}));
  for(i=0;i<A.length;i++){ var w=W*area[A[i]]/sA; out.push({i:A[i],x:x,y:0,w:w,h:dA}); x+=w; }
  x=W; for(i=0;i<B.length;i++){ var wb=W*area[B[i]]/sB; x-=wb; out.push({i:B[i],x:x,y:dA+c,w:wb,h:dB}); }
  return {rooms:out, corridor:{x:0,y:dA,w:W,h:c}};
}
// ---- method E: double-loaded as practice sets it: a room depth (5.5 m) on each side, the length free,
// every room at least 2.4 m wide (a small room grows rather than becoming a slot).
function doubleLoaded(order, area, depth, c, minW){
  var tot=sum(order.map(function(i){return area[i];})), half=0, cut=order.length, i, wid=function(i){ return Math.max(area[i]/depth, minW); };
  for(i=0;i<order.length;i++){ if(half+area[order[i]]/2>tot/2){ cut=i; break; } half+=area[order[i]]; }
  if(cut===0) cut=1; if(cut===order.length) cut=order.length-1;
  var A=order.slice(0,cut), B=order.slice(cut), LA=0, LB=0;
  A.forEach(function(i){ LA+=wid(i); }); B.forEach(function(i){ LB+=wid(i); });
  var L=Math.max(LA,LB), out=[], x=0, fa=L/LA, fb=L/LB;   // the shorter side's rooms widen to the same length
  for(i=0;i<A.length;i++){ var w=wid(A[i])*fa; out.push({i:A[i],x:x,y:0,w:w,h:depth}); x+=w; }
  x=L; for(i=0;i<B.length;i++){ var wb=wid(B[i])*fb; x-=wb; out.push({i:B[i],x:x,y:depth+c,w:wb,h:depth}); }
  return {rooms:out, corridor:{x:0,y:depth,w:L,h:c}, L:L};
}
// ---- the order: greedy chain by adjacency, then best-swap hill climbing on the judged layout ---------
function greedyOrder(P){
  var n=P.area.length, w=[], i, j, used={}, order=[0];
  for(i=0;i<n;i++){ w.push([]); for(j=0;j<n;j++) w[i].push(0); }
  P.req.forEach(function(p){ w[p[0]][p[1]]=w[p[1]][p[0]]=1; }); P.bad.forEach(function(p){ w[p[0]][p[1]]=w[p[1]][p[0]]=-1; });
  used[0]=1;
  while(order.length<n){ var last=order[order.length-1], best=-1, bv=-9;
    for(j=0;j<n;j++) if(!used[j]){ var v=w[last][j]*2; for(i=0;i<order.length-1;i++) v+=w[order[i]][j]*0.5; if(v>bv){ bv=v; best=j; } }
    order.push(best); used[best]=1; }
  return order;
}
function climb(order, evalOrder, rounds){
  var cur=order.slice(), cs=evalOrder(cur), n=cur.length, r, i, j, evals=1;
  for(r=0;r<rounds;r++){ var bi=-1, bj=-1, bs=cs;
    for(i=0;i<n;i++) for(j=i+1;j<n;j++){ var t=cur.slice(), x=t[i]; t[i]=t[j]; t[j]=x; var s=evalOrder(t); evals++; if(s>bs+1e-9){ bs=s; bi=i; bj=j; } }
    if(bi<0) break; var y=cur[bi]; cur[bi]=cur[bj]; cur[bj]=y; cs=bs; }
  return {order:cur, evals:evals};
}

// ---- the runs -----------------------------------------------------------------------------------------
var D=18, C=1.8, GROSS=1.15;
function run(P){
  var net=sum(P.area), W=net*GROSS/D, res={};
  // A: squarified treemap, programme order, no corridor
  var progOrder=P.area.map(function(_,i){return i;});
  res.A=judge(P, treemap(progOrder,P.area,0,0,W,D), W*D, null);
  // B: treemap, adjacency order, then hill climbing
  var evB=function(o){ return score(judge(P, treemap(o,P.area,0,0,W,D), W*D, null)); };
  var cb=climb(greedyOrder(P), evB, 40); res.B=judge(P, treemap(cb.order,P.area,0,0,W,D), W*D, null); res.B.evals=cb.evals;
  // C: corridor first, equal sides, adjacency order then hill climbing
  var dA=(D-C)/2, evC=function(o){ var L=corridorFirst(o,P.area,W,D,C,dA); return score(judge(P,L.rooms,W*(D-C),L.corridor)); };
  var cc=climb(greedyOrder(P), evC, 40), LC=corridorFirst(cc.order,P.area,W,D,C,dA); res.C=judge(P,LC.rooms,W*(D-C),LC.corridor); res.C.evals=cc.evals;
  // D: corridor first, sides of 5 m and the rest, small spaces free to go on the shallow side
  var evD=function(o){ var L=corridorFirst(o,P.area,W,D,C,5); return score(judge(P,L.rooms,W*(D-C),L.corridor)); };
  var cd=climb(greedyOrder(P), evD, 40), LD=corridorFirst(cd.order,P.area,W,D,C,5); res.D=judge(P,LD.rooms,W*(D-C),LD.corridor); res.D.evals=cd.evals;
  // E: double-loaded, depth 5.5 m, length free, minimum width 2.4 m; areas judged against the programme itself
  var evE=function(o){ var L=doubleLoaded(o,P.area,5.5,C,2.4); return score(judge(P,L.rooms,sum(P.area),L.corridor)); };
  var ce=climb(greedyOrder(P), evE, 40), LE=doubleLoaded(ce.order,P.area,5.5,C,2.4);
  res.E=judge(P,LE.rooms,sum(P.area),LE.corridor); res.E.evals=ce.evals;
  res.E.gross=(LE.L*(2*5.5+C))/sum(P.area);
  return res;
}
function q(a,p){ a=a.slice().sort(function(x,y){return x-y;}); return a[Math.floor((a.length-1)*p)]; }
var names={A:'A. treemap, programme order, no corridor',B:'B. treemap, adjacency order and swaps, no corridor',
  C:'C. corridor first, two equal sides, order and swaps',D:'D. corridor first, a 5 m side and a deep side, order and swaps',E:'E. double-loaded, 5.5 m rooms, length free, 2.4 m minimum width'};
var out=[], t0=Date.now(), runs=[], s;
for(s=1;s<=200;s++) runs.push(run(randomProgramme(1000+s)));
var ms=(Date.now()-t0)/200;
var clinic=run(CLINIC);
out.push('node '+process.version+'; plan depth '+D+' m, corridor '+C+' m, gross over net '+GROSS+'; adjacency = a shared wall of 1.0 m or more');
out.push('');
out.push('The hand-written clinic (12 spaces, 12 required pairs, 3 forbidden):');
out.push('');
out.push('| method | required met | forbidden broken | worst aspect | worst area deviation | rooms on the corridor |');
out.push('|---|---|---|---|---|---|');
['A','B','C','D','E'].forEach(function(m){ var j=clinic[m];
  out.push('| '+names[m]+' | '+(j.met*100).toFixed(0)+'% | '+j.viol+' | '+j.aspect.toFixed(1)+' | '+(j.dev*100).toFixed(0)+'% | '+(j.reach*100).toFixed(0)+'% |'); });
out.push('');
out.push('200 random programmes (12 spaces, 6 to 60 m2, 14 required pairs, 3 forbidden); median [lower quartile, upper quartile]:');
out.push('');
out.push('| method | required met | forbidden broken | worst aspect | worst area deviation | rooms on the corridor | share with worst aspect over 3 |');
out.push('|---|---|---|---|---|---|---|');
['A','B','C','D','E'].forEach(function(m){
  var met=runs.map(function(r){return r[m].met*100;}), v=runs.map(function(r){return r[m].viol;}), a=runs.map(function(r){return r[m].aspect;}),
      d=runs.map(function(r){return r[m].dev*100;}), re=runs.map(function(r){return r[m].reach*100;}), o3=a.filter(function(x){return x>3;}).length/a.length*100;
  out.push('| '+names[m]+' | '+q(met,.5).toFixed(0)+'% ['+q(met,.25).toFixed(0)+', '+q(met,.75).toFixed(0)+'] | '+q(v,.5)+' ['+q(v,.25)+', '+q(v,.75)+'] | '+
    q(a,.5).toFixed(1)+' ['+q(a,.25).toFixed(1)+', '+q(a,.75).toFixed(1)+'] | '+q(d,.5).toFixed(0)+'% ['+q(d,.25).toFixed(0)+', '+q(d,.75).toFixed(0)+'] | '+
    q(re,.5).toFixed(0)+'% | '+o3.toFixed(0)+'% |'); });
out.push('');
out.push('');
out.push('E gives the plan its own length, so its gross area over the programme varies: median '+
  q(runs.map(function(r){return r.E.gross;}),.5).toFixed(2)+' ['+q(runs.map(function(r){return r.E.gross;}),.25).toFixed(2)+', '+
  q(runs.map(function(r){return r.E.gross;}),.75).toFixed(2)+'] (the others are fixed at '+GROSS+'; the clinic: '+clinic.E.gross.toFixed(2)+').');
out.push('Time: '+ms.toFixed(1)+' ms per programme for all five methods together (B to E each evaluate about '+
  q(runs.map(function(r){return r.C.evals;}),.5)+' orders).');
console.log(out.join('\n'));
