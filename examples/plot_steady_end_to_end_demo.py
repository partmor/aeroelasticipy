"""
Detailed steady VLM demo
========================

A step by step example of simulation execution.
"""
import time

import matplotlib.pyplot as plt
import numpy as np

import ezaero.vlm.plotting as plot_utils
import ezaero.vlm.steady as vlm

start = time.time()

# definition of wing, mesh and flight condition parameters
wing = vlm.WingParams(
    cr=1, ct=0.6, bp=4, theta=30 * np.pi / 180, delta=15 * np.pi / 180
)
mesh = vlm.MeshParams(m=4, n=16)
flcond = vlm.FlightConditions(ui=100, alpha=1 * np.pi / 180, rho=1.0)

# step by step execution of the simulation (equivalent to running
# the run_simulation method)
wing_panels, cpoints = vlm.build_wing_panels(wing=wing, mesh=mesh)
vortex_panels = vlm.build_wing_vortex_panels(wing_panels)
normal_vectors = vlm.calculate_panel_normal_vectors(wing_panels)
surface = vlm.calculate_wing_planform_surface(wing_panels)
wake = vlm.build_steady_wake(flcond=flcond, vortex_panels=vortex_panels)
aic = vlm.calculate_influence_matrix(
    vortex_panels=vortex_panels, wake=wake, cpoints=cpoints, normals=normal_vectors
)
rhs = vlm.calculate_rhs(flcond=flcond, normals=normal_vectors)
circulation = vlm.solve_net_panel_circulation_distribution(
    aic=aic, rhs=rhs, m=mesh.m, n=mesh.n
)

res = vlm.get_aero_distributions(
    flcond=flcond, wing=wing, mesh=mesh, net_circulation=circulation, surface=surface
)

end = time.time()
print("Elapsed time: {} s".format(end - start))

# plot wing panels, vortex panels, and collocation points
ax = plot_utils.plot_panels(wing_panels)
plot_utils.plot_panels(vortex_panels, edge_color="r", fill_color=0, ax=ax)
plot_utils.plot_control_points(cpoints, ax)
plt.show()

# plot cl distribution on wing
plot_utils.plot_cl_distribution_on_wing(wing_panels, res)
plt.show()
