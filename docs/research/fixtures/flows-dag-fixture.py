"""Isolated research toy; not application or upstream code."""
from collections import deque

def evaluate(nodes):
    deps={k:list(v.get('in', [])) for k,v in nodes.items()}
    for k,ds in deps.items():
        if len(ds)!=len(set(ds)): raise ValueError('duplicate input edge: '+k)
        if any(d not in nodes for d in ds): raise ValueError('missing node: '+k)
    indeg={k:len(ds) for k,ds in deps.items()}; queue=deque(sorted(k for k,d in indeg.items() if d==0)); order=[]
    while queue:
        n=queue.popleft(); order.append(n)
        for k in sorted(nodes):
            if n in deps[k]:
                indeg[k]-=1
                if indeg[k]==0: queue.append(k)
    if len(order)!=len(nodes): raise ValueError('cycle or downstream dependency')
    out={}
    for k in order:
        node=nodes[k]; args=[out[d] for d in deps[k]]
        if any(a is None for a in args): out[k]=None
        elif node['op']=='value': out[k]=node.get('value')
        elif node['op']=='sum': out[k]=sum(args)
        elif node['op']=='double' and len(args)==1: out[k]=2*args[0]
        else: raise ValueError('unsupported op: '+k)
    return out

def check_error(nodes, text):
    try: evaluate(nodes)
    except ValueError as e: assert text in str(e); return
    raise AssertionError('expected '+text)

g={'A':{'op':'value','value':2},'B':{'op':'value','value':3},'C':{'op':'sum','in':['A','B']},'D':{'op':'double','in':['C']}}
assert evaluate(g)['D']==10
g['A']['value']=4; assert evaluate(g)['D']==14
g['B']['value']=None; assert evaluate(g)['D'] is None
g['A']={'op':'double','in':['C']}; check_error(g,'cycle')
g['A']={'op':'value','value':4}; g['C']['in']=['A','A']; check_error(g,'duplicate')
g['C']['in']=['A','Z']; check_error(g,'missing node')
print('PASS: original=10; edited=14; unknown propagated; cycle, duplicate and missing node rejected')
