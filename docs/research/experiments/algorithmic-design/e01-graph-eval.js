// e01: what does it cost to re-evaluate a node graph? (research-algorithmic-design.md, H1)
// Data for a research note, never a suite. Plain ES5 on purpose: the engine's contract.
// Run: node docs/research/experiments/algorithmic-design/e01-graph-eval.js
'use strict';
function rng(seed){ return function(){ seed|=0; seed=seed+0x6D2B79F5|0; var t=Math.imul(seed^seed>>>15,1|seed);
  t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }

// A random layered DAG: node i reads only lower-numbered nodes, so index order is a topological order.
function makeGraph(n, seed){
  var r=rng(seed), nodes=[], i, k, ins, ops=['sum','mul','min','max'];
  var nSrc=Math.max(4, Math.floor(n*0.1));
  for(i=0;i<n;i++){
    if(i<nSrc){ nodes.push({op:'value', v:1+r()*9, ins:[], outs:[]}); continue; }
    ins=[]; var want=1+Math.floor(r()*3);
    for(k=0;k<want;k++){ var j=Math.floor(r()*i); if(ins.indexOf(j)<0) ins.push(j); }
    nodes.push({op:ops[Math.floor(r()*4)], ins:ins, outs:[], v:0});
  }
  for(i=0;i<n;i++) for(k=0;k<nodes[i].ins.length;k++) nodes[nodes[i].ins[k]].outs.push(i);
  return {nodes:nodes, nSrc:nSrc};
}
function evalNode(nodes, i){
  var nd=nodes[i], a=nd.ins, k, x;
  if(nd.op==='value') return nd.v;
  if(nd.op==='sum'){ x=0; for(k=0;k<a.length;k++) x+=nodes[a[k]].v; return x; }
  if(nd.op==='mul'){ x=1; for(k=0;k<a.length;k++) x*=1+nodes[a[k]].v%3*0.01; return x; }
  if(nd.op==='min'){ x=Infinity; for(k=0;k<a.length;k++) x=Math.min(x,nodes[a[k]].v); return x; }
  x=-Infinity; for(k=0;k<a.length;k++) x=Math.max(x,nodes[a[k]].v); return x;
}
// Kahn's algorithm, as V215's bimFlowOrder does it (without the sorted tie-break).
function kahn(nodes){
  var n=nodes.length, deg=new Array(n), q=[], order=[], i, k, h=0;
  for(i=0;i<n;i++){ deg[i]=nodes[i].ins.length; if(!deg[i]) q.push(i); }
  while(h<q.length){ i=q[h++]; order.push(i); var o=nodes[i].outs;
    for(k=0;k<o.length;k++) if(--deg[o[k]]===0) q.push(o[k]); }
  return order;
}
function evalAll(nodes, order){ for(var t=0;t<order.length;t++) nodes[order[t]].v=evalNode(nodes, order[t]); }
// Incremental: push dirty marks downstream of the changed node, then recompute the dirty ones in
// topological order, stopping a branch when a node's value did not change (the early cutoff).
function evalDirty(nodes, changed, rank){
  var stack=[changed], dirty=[], seen={}, i, k, count=0;
  seen[changed]=1;
  while(stack.length){ i=stack.pop(); dirty.push(i); var o=nodes[i].outs;
    for(k=0;k<o.length;k++) if(!seen[o[k]]){ seen[o[k]]=1; stack.push(o[k]); } }
  dirty.sort(function(a,b){ return rank[a]-rank[b]; });
  var live={}; live[changed]=1;
  for(k=0;k<dirty.length;k++){ i=dirty[k]; var nd=nodes[i], need=live[i], m;
    if(!need) for(m=0;m<nd.ins.length;m++) if(live[nd.ins[m]]){ need=1; break; }
    if(!need) continue;
    var v=evalNode(nodes,i); count++;
    if(v!==nd.v || i===changed){ nd.v=v; live[i]=1; } }
  return {marked:dirty.length, recomputed:count};
}
function median(a){ a=a.slice().sort(function(x,y){return x-y;}); return a[Math.floor(a.length/2)]; }
function timeIt(fn, runs){ var t=[], i, s; for(i=0;i<300;i++) fn();   // warm up, so the JIT has compiled it
  for(i=0;i<runs;i++){ s=process.hrtime.bigint(); fn(); t.push(Number(process.hrtime.bigint()-s)/1e6); }
  return median(t); }

// A stand-in for a geometry node: the vertex and index arrays of `count` boxes (a facade's panels).
function boxes(count, w){
  var pos=new Float32Array(count*24*3), idx=new Uint32Array(count*36), c, p=0, q=0, f, base;
  var F=[[0,1,2,3],[5,4,7,6],[4,0,3,7],[1,5,6,2],[3,2,6,7],[4,5,1,0]];
  for(c=0;c<count;c++){ var x0=c%40*w, y0=Math.floor(c/40)*3.5, x1=x0+w*0.9, y1=y0+3.2, z0=0, z1=0.2;
    var V=[[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1],[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]];
    for(f=0;f<6;f++){ base=p/3; for(var k=0;k<4;k++){ var v=V[F[f][k]]; pos[p++]=v[0]; pos[p++]=v[1]; pos[p++]=v[2]; }
      idx[q++]=base; idx[q++]=base+1; idx[q++]=base+2; idx[q++]=base; idx[q++]=base+2; idx[q++]=base+3; } }
  return {pos:pos, idx:idx};
}

var out=[], sizes=[100,1000,10000,100000], si;
out.push('node '+process.version+', '+process.platform+' '+process.arch+'; medians of 200 runs (ms)');
out.push('');
out.push('| nodes | Kahn order | whole re-evaluation | order + whole | one source changed: marked | recomputed | incremental |');
out.push('|---|---|---|---|---|---|---|');
for(si=0;si<sizes.length;si++){
  var n=sizes[si], g=makeGraph(n, 7), order=kahn(g.nodes), rank=new Array(n), i;
  for(i=0;i<n;i++) rank[order[i]]=i;
  evalAll(g.nodes, order);
  var runs=n>=100000?40:200;
  var tK=timeIt(function(){ kahn(g.nodes); }, runs);
  var tA=timeIt(function(){ evalAll(g.nodes, order); }, runs);
  var r=rng(11), marks=[], recs=[];
  var tI=timeIt(function(){ var s=Math.floor(r()*g.nSrc); g.nodes[s].v=1+r()*9;
    var d=evalDirty(g.nodes, s, rank); marks.push(d.marked); recs.push(d.recomputed); }, runs);
  out.push('| '+n+' | '+tK.toFixed(4)+' | '+tA.toFixed(4)+' | '+(tK+tA).toFixed(4)+' | '+median(marks)+' | '+median(recs)+' | '+tI.toFixed(4)+' |');
}
out.push('');
out.push('A stand-in geometry node (the arrays of N boxes, 24 vertices and 12 triangles each):');
out.push('');
out.push('| boxes | build (ms) | key of its inputs, JSON (ms) |');
out.push('|---|---|---|');
var counts=[100,1000,10000], ci;
for(ci=0;ci<counts.length;ci++){
  var c=counts[ci];
  var tB=timeIt(function(){ boxes(c, 1.2); }, 100);
  var inputs={count:c, w:1.2, h:3.5, d:0.2, mat:'glass', storeys:10, bays:8, list:[1,2,3,4,5,6,7,8]};
  var tH=timeIt(function(){ JSON.stringify(inputs); }, 100);
  out.push('| '+c+' | '+tB.toFixed(4)+' | '+tH.toFixed(5)+' |');
}
console.log(out.join('\n'));
