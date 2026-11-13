import json, math, struct, pathlib
f=lambda v:struct.unpack('f',struct.pack('f',v))[0]
base=6378137.0; delta=.01
r={'base_m':base,'offset_m':delta,'global_float32_delta_m':f(base+delta)-f(base),'local_float32_delta_m':f(delta)-f(0),'y_up_vector_to_z_up':[0,0,1],'model':'IEEE binary32; synthetic equatorial coordinate, not a renderer test'}
assert r['global_float32_delta_m']==0 and r['local_float32_delta_m']>0
print(json.dumps(r,indent=2));pathlib.Path(__file__).with_name('results.json').write_text(json.dumps(r,indent=2)+'\n')
