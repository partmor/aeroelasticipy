"""
Simple steady VLM demo
======================

Minimal example of simulation execution.
"""
import time

import matplotlib.pyplot as plt
import numpy as np

import ezaero.vlm.steady as vlm

# definition of wing, mesh and flight condition parameters
wing = vlm.WingParameters(
    root_chord=1,
    tip_chord=0.6,
    planform_wingspan=4,
    sweep_angle=30 * np.pi / 180,
    dihedral_angle=15 * np.pi / 180,
)
mesh = vlm.MeshParameters(m=4, n=16)
flcond = vlm.FlightConditions(ui=100, aoa=3 * np.pi / 180, rho=1.0)

sim = vlm.Simulation(wing=wing, mesh=mesh, flight_conditions=flcond)

start = time.time()
res = sim.run()
print(f"Wing lift coefficient: {res.cl_wing}")
print(f"Elapsed time: {time.time() - start} s")

# plot wing panels, vortex panels, and collocation points
sim.plot_wing()
plt.show()

# plot cl distribution on wing
sim.plot_cl()
plt.show()
