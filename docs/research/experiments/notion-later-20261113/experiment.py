import json,math
legs=[(0,100),(90,80),(180,100),(270,79.98)]
e=sum(d*math.sin(math.radians(a)) for a,d in legs); n=sum(d*math.cos(math.radians(a)) for a,d in legs); L=sum(d for a,d in legs)
# Synthetic unlevered mixed-use stabilized operating model, no financing/tax.
res=100*1800*12; retail=10000*30; gross=res+retail; eff=res*.95+retail*.90; noi=eff-300000; cost=6000000+14000000+3000000+1000000
r={'survey':{'legs_azimuth_deg_distance_m':legs,'east_m':e,'north_m':n,'misclosure_m':math.hypot(e,n),'perimeter_m':L,'ratio':L/math.hypot(e,n)},'feasibility':{'potential_gross_income_usd':gross,'effective_income_usd':eff,'operating_expense_usd':300000,'noi_usd':noi,'total_cost_usd':cost,'yield_on_cost':noi/cost,'value_at_6_percent_cap_usd':noi/.06},'generator':{'lot_m2':2000,'far':1.2,'coverage':0.5,'levels':4,'plate_cap_m2':1000,'capacity_m2':4000,'far_limit_m2':2400,'achievable_m2':2400,'plate_areas_m2':[1000,1000,400,0]}}
print(json.dumps(r,indent=2))
