#!/usr/bin/env python3
"""Synthetic bookkeeping example, NOT an app test or a construction estimate."""
import json
from decimal import Decimal as D
q=D('6')*D('4')*D('0.2')-D('1')*D('1')*D('0.2')
concrete=q*D('1.05'); material=concrete*D('120'); labor=q*D('0.5')*D('50'); nonmodel=D('100')
total=material+labor+nonmodel
alloc={'day1':material*D('.5')+labor*D('.5')+nonmodel,'day2':material*D('.5')+labor*D('.5')}
assert q==D('4.6') and total==D('794.6') and sum(alloc.values())==total
# Deliberately bad examples the proposed validator must reject.
bad_allocation=D('0.6')+D('0.6')
assert bad_allocation>D('1')
out={'inputs':'synthetic; generic currency; not an operational estimate','net_volume_m3':str(q),'order_volume_m3_at_5pct_waste':str(concrete),'material_cost':str(material),'labor_hours':str(q*D('.5')),'labor_cost':str(labor),'non_model_cost':str(nonmodel),'total':str(total),'planned_cost_by_working_day':{k:str(v) for k,v in alloc.items()},'bucket_sum':str(sum(alloc.values())),'deliberately_invalid_split_total':str(bad_allocation),'invalid_split_expected':'reject', 'notes':'Illustrative arithmetic only. Opening fully through slab, no overlap; half on each of two working days; preliminaries charged day 1. These are stipulated assumptions, not measurement or costing rules.'}
print(json.dumps(out,indent=2))
