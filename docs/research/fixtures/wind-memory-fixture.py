#!/usr/bin/env python3
"""Arithmetic-only storage estimates, not a CFD or WebGPU test."""
for n in (64,128,256):
    one=n**3*19*4
    print(f'{n}^3: one f32 D3Q19 population buffer={one:,} bytes ({one/2**20:.0f} MiB); double={2*one:,} bytes ({2*one/2**20:.0f} MiB)')
    assert one == n*n*n*19*4
assert 128**3*19*4 == 159383552
assert 128**3*19*4*2 == 318767104
assert 256**3*19*4*2 == 2550136832
print('PASS: arithmetic only; allocations, rendering and solver not tested')
