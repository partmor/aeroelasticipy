import numpy as np
import pytest

import ezaero.vlm.steady as vlm_steady

INFINITE_WING = {
    "wing": vlm_steady.WingParams(cr=1.0, ct=1.0, bp=10000, theta=0.0, delta=0.0),
    "mesh": vlm_steady.MeshParams(m=2, n=400),
}


@pytest.mark.parametrize("alpha", np.array((-2, -1, 0, 1, 2, 5)) * np.pi / 180)
def test_cl_for_infinite_wing(alpha):
    flcond = vlm_steady.FlightConditions(ui=50.0, alpha=alpha, rho=1.0)

    sim = vlm_steady.run_simulation(
        wing=INFINITE_WING["wing"], mesh=INFINITE_WING["mesh"], flcond=flcond
    )

    assert sim.cl_wing == pytest.approx(2 * np.pi * alpha, rel=5e-3)


def test_cl_slope_vs_aspect_ratio_for_slender_wing():
    bps = [0.25, 0.5]
    mesh = vlm_steady.MeshParams(8, 30)
    alpha = np.pi / 180
    flcond = vlm_steady.FlightConditions(ui=100.0, alpha=alpha, rho=1.0)
    clas = []
    for bp in bps:
        wing = vlm_steady.WingParams(cr=1.0, ct=1.0, bp=bp, theta=0.0, delta=0.0)
        sim = vlm_steady.run_simulation(wing=wing, mesh=mesh, flcond=flcond)
        clas.append(sim.cl_wing / alpha)

    slope = (clas[1] - clas[0]) / (bps[1] - bps[0])

    assert slope == pytest.approx(np.pi / 2, abs=1e-2)
