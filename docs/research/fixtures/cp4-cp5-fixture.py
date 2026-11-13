"""Synthetic CP4/CP5 arithmetic; no app or AI service used."""
from datetime import date,timedelta
from decimal import Decimal

def previous_workdays(need,n,holidays):
    d=need
    for _ in range(n):
        d-=timedelta(days=1)
        while d.weekday()>=5 or d in holidays: d-=timedelta(days=1)
    return d

def allocate(amount, splits):
    if any(x<0 for x in splits) or sum(splits)>Decimal(1): raise ValueError('invalid allocation')
    assigned=[amount*x for x in splits]
    return assigned, amount-sum(assigned)

need=date(2026,1,16); holiday={date(2026,1,12)}
assert previous_workdays(need,5,holiday)==date(2026,1,8)
a,u=allocate(Decimal('1000'),[Decimal('.6'),Decimal('.4')]); assert a==[Decimal('600'),Decimal('400')] and u==0
a2,u2=allocate(Decimal('1000'),[Decimal('.6')]); assert u2==400
try: allocate(Decimal('1000'),[Decimal('.6'),Decimal('.6')])
except ValueError: pass
else: raise AssertionError('over-allocation accepted')
tp,fp,fn=8,2,2; assert tp/(tp+fp)==0.8 and tp/(tp+fn)==0.8
print('PASS: working-day deadline 2026-01-08; 600+400=1000; unallocated=400; 120% rejected; toy precision=0.8 recall=0.8')
