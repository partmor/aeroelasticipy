"""
Simple steady VLM demo
======================

Minimal example of simulation execution.
"""
import time

import numpy as np

import ezaero.vlm.steady as vlm

start = time.time()

# definition of wing, mesh and flight condition parameters
wing = vlm.WingParams(
    cr=1, ct=0.6, bp=4, theta=30 * np.pi / 180, delta=15 * np.pi / 180
)
mesh = vlm.MeshParams(m=4, n=16)
flcond = vlm.FlightConditions(ui=100, alpha=3 * np.pi / 180, rho=1.0)

# run simulation and collect results
res = vlm.run_simulation(wing=wing, mesh=mesh, flcond=flcond)

print("Elapsed time: {} s".format(time.time() - start))

print("Wing lift coefficient: {}".format(res.cl_wing))
