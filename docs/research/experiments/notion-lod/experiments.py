import numpy as np, cv2, json, platform
r=np.random.default_rng(20261113)
# 1. Georeferenced coordinates in metres. Compare world float32 storage and rebased float32.
base=500000.0; offsets=np.array([0.0,0.01,0.02,0.05,0.1,1.0]); world=base+offsets
unbased=world.astype(np.float32).astype(float)-base
rebased=(world-base).astype(np.float32).astype(float)
# 2. single plane with 100 clean samples and 10 tall outliers, fitted all vs oracle clean.
x=r.uniform(0,10,110); y=r.uniform(0,8,110); A=np.column_stack([x,y,np.ones(110)]); truth=np.array([0.2,-0.1,5.0]); z=A@truth+r.normal(0,0.01,110); z[100:]+=3
clean=np.linalg.lstsq(A[:100],z[:100],rcond=None)[0]; allfit=np.linalg.lstsq(A,z,rcond=None)[0]
test=r.uniform([0,0],[10,8],(1000,2)); T=np.column_stack([test,np.ones(len(test))]); rmse=lambda p:float(np.sqrt(np.mean((T@p-T@truth)**2)))
# 3. Metric wall to perspective image using a known homography. Recover via 4 corners and test 9 withheld points.
H=np.array([[100.,12.,250.],[5.,-90.,650.],[0.015,0.008,1.]])
proj=lambda h,pts:cv2.perspectiveTransform(np.asarray(pts,dtype=np.float64).reshape(-1,1,2),h).reshape(-1,2)
ctrl=np.array([[0.,0.],[10.,0.],[10.,6.],[0.,6.]]); pixels=proj(H,ctrl); fit=cv2.getPerspectiveTransform(pixels.astype(np.float32),ctrl.astype(np.float32))
check=np.array([[x,y] for x in [2.,5.,8.] for y in [1.,3.,5.]])
pred=proj(fit,proj(H,check)); err=np.linalg.norm(pred-check,axis=1)
noisy=pixels.copy(); noisy[2]+=[3.,-3.]; fit2=cv2.getPerspectiveTransform(noisy.astype(np.float32),ctrl.astype(np.float32)); err2=np.linalg.norm(proj(fit2,proj(H,check))-check,axis=1)
print(json.dumps({'environment':{'python':platform.python_version(),'numpy':np.__version__,'opencv':cv2.__version__,'seed':20261113},'precision':{'base_m':base,'offsets_m':offsets.tolist(),'world_float32_offsets_m':unbased.tolist(),'rebased_float32_offsets_m':rebased.tolist(),'max_world_error_m':float(max(abs(unbased-offsets))),'max_rebased_error_m':float(max(abs(rebased-offsets)))},'plane':{'clean_fit':clean.tolist(),'all_fit':allfit.tolist(),'clean_rmse_against_truth_m':rmse(clean),'all_rmse_against_truth_m':rmse(allfit),'outliers':10,'samples':110,'holdout':1000},'homography':{'check_count':9,'exact_max_error_m':float(max(err)),'perturbed_one_control_3px_xy_max_error_m':float(max(err2)),'perturbed_mean_error_m':float(np.mean(err2))}},indent=2))
