import math,json,platform
# A two-cell thought fixture matching the relevant operations in bimRainFlow,
# NOT an execution of BIM-Personal.  Discovery-order IDs are not rewritten by sorting.
ponds=[{'pid':1,'volume':1.0},{'pid':2,'volume':9.0}]
pid_grid=[1,2]; ordered=sorted(ponds,key=lambda p:p['volume'],reverse=True)
old_area=1.0
ratios={str(a):old_area/a for a in [1.0,0.25,0.01,0.000001]}
n1,n2=1.0,1.333; f0=((n1-n2)/(n1+n2))**2
out={'python':platform.python_version(),'runs':1,'pond_fixture':{'discovery_ids':pid_grid,'volumes_in_discovery_order':[1.0,9.0],'sorted_ids':[p['pid'] for p in ordered],'pid_1_at_sorted_index_zero_matches':ordered[pid_grid[0]-1]['pid']==pid_grid[0]},'caustic_area_ratio_unit_old_area':ratios,'schlick_f0_for_example_indices':f0,'caveat':'CPU arithmetic examples only; no GPU, renderer, app, hydrology or physical validation'}
print(json.dumps(out,indent=2))
