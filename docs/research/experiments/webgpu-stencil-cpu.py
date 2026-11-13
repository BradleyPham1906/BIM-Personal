import numpy as np, platform, json

def run(dtype):
    a=np.zeros((18,18),dtype=dtype); a[9,9]=1
    for _ in range(100):
        b=np.zeros_like(a); c=a[1:-1,1:-1]
        b[1:-1,1:-1]=c+dtype(0.24)*(a[:-2,1:-1]+a[2:,1:-1]+a[1:-1,:-2]+a[1:-1,2:]-dtype(4)*c)
        a=b
    return a
x,y=run(np.float64),run(np.float32).astype(np.float64); diff=np.abs(x-y)
print(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'interior':'16x16','steps':100,'alpha':0.24,'boundary':'zero','max_abs_error':float(diff.max()),'rms_error':float(np.sqrt(np.mean(diff**2))),'sum_f64':float(x.sum()),'sum_f32':float(y.sum()),'runs':1},indent=2))
