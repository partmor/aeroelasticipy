import ezaero.vlm.steady as vlm_steady
import numpy as np
import pytest

INFINITE_WING = {
    'wing': vlm_steady.WingParams(cr=1.0, ct=1.0, bp=10000, theta=0.0,
                                  delta=0.0),
    'mesh': vlm_steady.MeshParams(m=2, n=400)
}


@pytest.mark.parametrize('alpha', np.array((-2, -1, 0, 1, 2, 5)) * np.pi / 180)
def test_cl_for_infinite_wing(alpha):
    flcond = vlm_steady.FlightConditions(ui=50.0, alpha=alpha, rho=1.0)

    sim = vlm_steady.run_simulation(
        wing=INFINITE_WING['wing'],
        mesh=INFINITE_WING['mesh'],
        flcond=flcond
    )
    cl = sim['cl_wing']

    assert cl == pytest.approx(2 * np.pi * alpha, rel=5e-3)


def test_cl_slope_for_infinite_wing():
    cls = []
    alphas = [1 * np.pi / 180, 2 * np.pi / 180]
    for alpha in alphas:
        flcond = vlm_steady.FlightConditions(ui=50.0, alpha=alpha, rho=1.0)
        sim = vlm_steady.run_simulation(
            wing=INFINITE_WING['wing'],
            mesh=INFINITE_WING['mesh'],
            flcond=flcond
        )
        cls.append(sim['cl_wing'])

    slope = (cls[1] - cls[0]) / (alphas[1] - alphas[0])

    assert slope == pytest.approx(2 * np.pi, abs=1e-2)
