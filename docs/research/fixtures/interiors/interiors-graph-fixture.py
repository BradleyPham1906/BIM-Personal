import json, heapq

def distance(edges, source, target):
    q=[(0,source)]; seen=set()
    while q:
        d,u=heapq.heappop(q)
        if u in seen: continue
        if u==target: return d
        seen.add(u)
        for a,b,w in edges:
            if a==u and b not in seen: heapq.heappush(q,(d+w,b))
    return None
edges=[('roomA','corridor',4),('roomB','corridor',3),('corridor','exit',6)]
result={'fixture_type':'synthetic graph arithmetic only; not a BIM app or accessibility assessment','units':'m','edge_inputs':edges,'roomA_to_exit':distance(edges,'roomA','exit'),'roomB_to_exit':distance(edges,'roomB','exit'),'roomA_to_exit_without_door':distance(edges[1:],'roomA','exit'),'adjacent_rooms_direct_edge':any(a=='roomA' and b=='roomB' for a,b,_ in edges),'isolated_32in_clear_width_predicate':{str(x):x>=32 for x in (31.9,32.,32.1)},'unknown_measured_clear_width':'not evaluated'}
assert result['roomA_to_exit']==10 and result['roomB_to_exit']==9 and result['roomA_to_exit_without_door'] is None and not result['adjacent_rooms_direct_edge']
with open('/data/interiors/interiors-graph-fixture-results.json','w') as f: json.dump(result,f,indent=2)
print('Fixture assertions passed; results saved.')
