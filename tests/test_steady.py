import numpy as np
import pytest

from ezaero.vlm.steady import (
    FlightConditions,
    MeshParameters,
    Simulation,
    WingParameters,
)

INFINITE_WING = {
    "wing": WingParameters(
        root_chord=1.0,
        tip_chord=1.0,
        planform_wingspan=10000,
        sweep_angle=0.0,
        dihedral_angle=0.0,
    ),
    "mesh": MeshParameters(m=2, n=400),
}


@pytest.fixture(scope="module")
def rectangular_wing_simulation():
    wing_params = WingParameters()
    mesh_params = MeshParameters(m=4, n=10)
    flight_cond = FlightConditions()
    sim = Simulation(wing=wing_params, mesh=mesh_params, flight_conditions=flight_cond,)
    return sim


def test_instantiate_simulation(rectangular_wing_simulation):
    _ = rectangular_wing_simulation


def test_plot_wing_not_available_yet(rectangular_wing_simulation):
    with pytest.raises(AttributeError):
        rectangular_wing_simulation.plot_wing()


def test_plot_result_not_available_yet(rectangular_wing_simulation):
    with pytest.raises(AttributeError):
        rectangular_wing_simulation.plot_cl()


def test_wing_panels_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._build_wing_panels()
    assert rectangular_wing_simulation.wing_panels.shape == (
        rectangular_wing_simulation.mesh.m,
        rectangular_wing_simulation.mesh.n,
        4,
        3,
    )


def test_wing_vortex_panels_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._build_wing_vortex_panels()
    assert rectangular_wing_simulation.vortex_panels.shape == (
        rectangular_wing_simulation.mesh.m,
        rectangular_wing_simulation.mesh.n,
        4,
        3,
    )


def test_panel_normal_vectors_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_panel_normal_vectors()
    assert rectangular_wing_simulation.normals.shape == (
        rectangular_wing_simulation.mesh.m,
        rectangular_wing_simulation.mesh.n,
        3,
    )


def test_calculate_wing_planform_surface(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_wing_planform_surface()
    assert rectangular_wing_simulation.panel_surfaces.shape == (
        rectangular_wing_simulation.mesh.m,
        rectangular_wing_simulation.mesh.n,
    )


def test_total_planform_surface(rectangular_wing_simulation):
    expected_rectangular_surface = (
        rectangular_wing_simulation.wing.root_chord
        * rectangular_wing_simulation.wing.planform_wingspan
    )
    calculated_rectangular_surface = rectangular_wing_simulation.panel_surfaces.sum()
    np.testing.assert_almost_equal(
        calculated_rectangular_surface, expected_rectangular_surface
    )


def test_wake_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._build_wake()
    assert rectangular_wing_simulation.wake.shape == (
        rectangular_wing_simulation.mesh.n,
        4,
        3,
    )


def test_wing_aic_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_wing_influence_matrix()
    mn = rectangular_wing_simulation.mesh.m * rectangular_wing_simulation.mesh.n
    assert rectangular_wing_simulation.aic_wing.shape == (mn, mn)


def test_aic_wake_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_wake_wing_influence_matrix()
    mn = rectangular_wing_simulation.mesh.m * rectangular_wing_simulation.mesh.n
    assert rectangular_wing_simulation.aic_wake.shape == (mn, mn)


def test_aic_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_influence_matrix()
    mn = rectangular_wing_simulation.mesh.m * rectangular_wing_simulation.mesh.n
    assert rectangular_wing_simulation.aic.shape == (mn, mn)


def test_rhs_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._calculate_rhs()
    mn = rectangular_wing_simulation.mesh.m * rectangular_wing_simulation.mesh.n
    rectangular_wing_simulation.rhs.shape = (mn,)


def test_panel_circulation_shape(rectangular_wing_simulation):
    rectangular_wing_simulation._solve_net_panel_circulation_distribution()
    rectangular_wing_simulation.net_circulation.shape = (
        rectangular_wing_simulation.mesh.m,
        rectangular_wing_simulation.mesh.n,
    )


def test_run(rectangular_wing_simulation):
    rectangular_wing_simulation.run()


def test_plot_wing_can_run(rectangular_wing_simulation):
    rectangular_wing_simulation.plot_wing()


def test_plot_cl_can_run(rectangular_wing_simulation):
    rectangular_wing_simulation.plot_cl()


@pytest.mark.parametrize(
    "angle_of_attack", np.array((-2, -1, 0, 1, 2, 5)) * np.pi / 180
)
def test_cl_for_infinite_wing(angle_of_attack):
    flcond = FlightConditions(ui=50.0, aoa=angle_of_attack, rho=1.0)
    sim = Simulation(
        wing=INFINITE_WING["wing"],
        mesh=INFINITE_WING["mesh"],
        flight_conditions=flcond,
    )
    res = sim.run()

    assert res.cl_wing == pytest.approx(2 * np.pi * angle_of_attack, rel=5e-3)


def test_cl_slope_vs_aspect_ratio_for_slender_wing():
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
