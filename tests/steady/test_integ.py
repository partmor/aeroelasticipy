import numpy as np
import pytest

from ezaero.vlm.steady import (
    FlightConditions,
    MeshParameters,
    Simulation,
    WingParameters,
)


@pytest.fixture(scope="module")
def infinite_wing_setup():
    wing = WingParameters(
        root_chord=1.0,
        tip_chord=1.0,
        planform_wingspan=10000,
        sweep_angle=0.0,
        dihedral_angle=0.0,
    )
    mesh = MeshParameters(m=2, n=400)
    return wing, mesh


@pytest.mark.parametrize(
    "angle_of_attack", np.array((-2, -1, 0, 1, 2, 5)) * np.pi / 180
)
def test_cl_for_infinite_wing(infinite_wing_setup, angle_of_attack):
    """
    Thin airfoil profile (flat plate) has a theoretical cl = 2 * pi * AoA.
    This test checks the theoretical result is (approximately) verified for an "infinite"
    rectangular wing.
    """
    flcond = FlightConditions(ui=50.0, aoa=angle_of_attack, rho=1.0)
    sim = Simulation(
        wing=infinite_wing_setup[0],
        mesh=infinite_wing_setup[1],
        flight_conditions=flcond,
    )
    res = sim.run()

    assert res.cl_wing == pytest.approx(2 * np.pi * angle_of_attack, rel=5e-3)


def test_cl_slope_vs_aspect_ratio_for_slender_wing():
    """
    This test checks that in the limit where the aspect ratio of the wing is close to zero,
    the simulation yields an approximation to the slender wing theory, where the slope of
    the cl-AspectRatio curve is pi / 2.
    """
    bps = [0.25, 0.5]
    mesh = MeshParameters(8, 30)
    alpha = np.pi / 180
    flcond = FlightConditions(ui=100.0, aoa=alpha, rho=1.0)
    clas = []
    for bp in bps:
        wing = WingParameters(
            root_chord=1.0,
            tip_chord=1.0,
            planform_wingspan=bp,
            sweep_angle=0.0,
            dihedral_angle=0.0,
        )
        res = Simulation(wing=wing, mesh=mesh, flight_conditions=flcond).run()
        clas.append(res.cl_wing / alpha)

    slope = (clas[1] - clas[0]) / (bps[1] - bps[0])

    assert slope == pytest.approx(np.pi / 2, abs=1e-2)
