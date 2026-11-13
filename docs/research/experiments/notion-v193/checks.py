"""Research-only arithmetic checks, not an app test; Python 3, no packages."""
import math,json,sys

def friction(re,rr):
    assert re>4000 and 0<=rr<1
    lo,hi=1.0,100.0
    def fun(x): return x+2*math.log10(rr/3.7+2.51*x/re)
    assert fun(lo)<0<fun(hi)
    for _ in range(100):
        mid=(lo+hi)/2
        if fun(mid)>0: hi=mid
        else: lo=mid
    x=(lo+hi)/2
    return 1/x**2,fun(x)
def pipe(Q,D,L,rho,mu,eps):
    A=math.pi*D*D/4; v=Q/A; re=rho*v*D/mu
    f,res=friction(re,eps/D); dp=f*L/D*rho*v*v/2
    return dict(Q=Q,D=D,L=L,area=A,velocity=v,Re=re,f_D=f,loss_Pa=dp,colebrook_residual=res)
f,res=friction(100000,.001)
assert abs(f-.0225)/.0225 < .03
# TU Delft example 1; handbook uses an explicit approximation and reports 0.62m and 0.60m.
Q=.3; D=.593; L=400; eps=.0001; v=Q/(math.pi*D*D/4)
def head(nu):
 re=v*D/nu; f,_=friction(re,eps/D); return {'Re':re,'f_D':f,'head_m':f*L/D*v*v/(2*9.81)}
h5=head(1.52e-6); h25=head(.9e-6)
assert abs(h5['head_m']-.62)<.02 and abs(h25['head_m']-.60)<.02
rho=998.2;mu=.001002;D=.1;L=10;re=1000; v=re*mu/(rho*D); f=64/re
p_darcy=f*L/D*rho*v*v/2; p_poiseuille=32*mu*v*L/(D*D)
assert math.isclose(p_darcy,p_poiseuille,rel_tol=1e-14)
a=pipe(.004,.1,5,rho,mu,.0000015);b=pipe(.006,.1,8,rho,mu,.0000015);trunk=pipe(.010,.1,10,rho,mu,.0000015)
result={'python':sys.version,'checks':{'moody_purdue':{'Re':100000,'relative_roughness':.001,'colebrook_f':friction(100000,.001)[0],'chart_f_approx':.0225,'relative_difference':abs(friction(100000,.001)[0]-.0225)/.0225,'colebrook_residual':res},'delft_example_1':{'v':Q/(math.pi*.593**2/4),'at_5C':h5,'at_25C':h25,'published_head_m':[.62,.60]},'laminar_circular':{'Re':1000,'pressure_by_darcy_Pa':p_darcy,'pressure_by_poiseuille_Pa':p_poiseuille},'hypothetical_tree':{'trunk':trunk,'branch_A':a,'branch_B':b,'path_A_Pa':trunk['loss_Pa']+a['loss_Pa'],'path_B_Pa':trunk['loss_Pa']+b['loss_Pa'],'warnings':['friction only','assumed known steady branch flows','no fittings or equipment','not an app test']}}}
print(json.dumps(result,indent=2))
