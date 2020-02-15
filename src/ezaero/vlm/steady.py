"""
The :mod:`ezaero.vlm.steady` module includes a Vortex Lattice Method
implementation for lifting surfaces.

References
----------
.. [1] Katz, J. et al., *Low-Speed Aerodynamics*, 2nd ed, Cambridge University
   Press, 2001: Chapter 12
"""

import numpy as np

from .plotting import plot_cl_distribution_on_wing, plot_control_points, plot_panels


class WingParameters:
    """
    Container for the geometric parameters of the analyzed wing.

    Attributes
    ----------
    root_chord : float
        Chord at root of the wing.
    tip_chord : float
        Chord at tip of the wing.
    planform_wingspan : float
        Wingspan of the planform.
    sweep_angle : float
        Sweep angle of the 1/4 chord line, expressed in radians.
    dihedral_angle : float
        Dihedral angle, expressed in radians.
    """

    def __init__(
        self,
        root_chord=1.0,
        tip_chord=1.0,
        planform_wingspan=4,
        sweep_angle=0,
        dihedral_angle=0,
    ):
        self.root_chord = root_chord
        self.tip_chord = tip_chord
        self.planform_wingspan = planform_wingspan
        self.sweep_angle = sweep_angle
        self.dihedral_angle = dihedral_angle


class MeshParameters:
    """
    Container for the wing mesh parameters.

    Attributes
    ----------
    m : int
        Number of chordwise panels.
    n : int
        Number of spanwise panels.
    """

    def __init__(self, m, n):
        self.m = m
        self.n = n


class FlightConditions:
    """
    Container for the flight conditions.

    Attributes
    ----------
    ui : float
        Free-stream flow velocity.
    angle_of_attack : float
        Angle of attack of the wing, expressed in radians.
    rho : float
        Free-stream flow density.
    """

    def __init__(self, ui=100, aoa=np.pi / 180, rho=1.0):
        self.ui = ui
        self.aoa = aoa
        self.rho = rho


class SimulationResults:
    """
    Container for the resulting distributions from the steady VLM simulation.

    Attributes
    ----------
    dp : np.ndarray, shape (m, n)
        Distribution of pressure difference between lower and upper surfaces.
    dL : np.ndarray, shape (m, n)
        Lift distribution.
    cl : np.ndarray, shape (m, n)
        Lift coefficient distribution.
    cl_wing : float
        Wing lift coefficient.
    cl_span : np.ndarray, shape (n, )
        Spanwise lift coefficient distribution.
    """

    def __init__(self, dp, dL, cl, cl_wing, cl_span):
        self.dp = dp
        self.dL = dL
        self.cl = cl
        self.cl_wing = cl_wing
        self.cl_span = cl_span


class Simulation:
    """
        Simulation runner.

        Attributes
        ----------
        wing : WingParameters
            Wing geometry definition.
        mesh : MeshParameters
            Mesh specification for the wing.
        flight_conditions : FlightConditions
            Flight conditions for the simulation.
        """

    def __init__(
        self,
        wing: WingParameters,
        mesh: MeshParameters,
        flight_conditions: FlightConditions,
    ):
        self.wing = wing
        self.mesh = mesh
        self.flight_conditions = flight_conditions

    def run(self):
        """
        Run end-to-end steady VLM simulation.

        Returns
        -------
        SimulationResults
            Object containing the results of the steady VLM simulation.
        """
        self._build_wing_panels()
        self._build_wing_vortex_panels()
        self._calculate_panel_normal_vectors()
        self._calculate_wing_planform_surface()
        self._build_wake()
        self._calculate_influence_matrix()
        self._calculate_rhs()
        self._solve_net_panel_circulation_distribution()
        self.distributions = self._calculate_aero_distributions_from_circulation()
        return self.distributions

    def plot_wing(self, **kwargs):
        """
        Generate 3D plot of wing panels, vortex panels, and panel control points.
        """
        try:
            ax = plot_panels(self.wing_panels, **kwargs)
            plot_panels(self.vortex_panels, edge_color="r", fill_color=0, ax=ax)
            plot_control_points(self.cpoints, ax=ax)
        except AttributeError as e:
            message = f"An error occurred. Make sure you have already run this simulation.\n{e}"
            raise AttributeError(message)

    def plot_cl(self):
        """
        Plot lift coefficient distribution on the wing.
        """
        try:
            plot_cl_distribution_on_wing(self.wing_panels, self.distributions)
        except AttributeError as e:
            message = f"An error occurred. Make sure you have already run this simulation.\n{e}"
            raise AttributeError(message)

    def _build_panel(self, i, j):
        """
        Build a wing panel indexed by its chord and spanwise indices.

        Parameters
        ----------
        i : int
            Panel chordwise index.
        j : int
            Panel spanwise index.

        Returns
        -------
        panel : np.ndarray, shape (4, 3)
            Array containing the (x,y,z) coordinates of the (`i`, `j`)-th panel's
            vertices (sorted A-B-D-C).
        pc : np.ndarray, shape (3, )
            (x,y,z) coordinates of the (`i`, `j`)-th panel's collocation point.
        """

        dy = self.wing.planform_wingspan / self.mesh.n
        y_A = -self.wing.planform_wingspan / 2 + j * dy
        y_B = y_A + dy
        y_C, y_D = y_A, y_B
        y_pc = y_A + dy / 2

        # chord law evaluation
        c_AC, c_BD, c_pc = [
            get_chord_at_section(
                y,
                root_chord=self.wing.root_chord,
                tip_chord=self.wing.tip_chord,
                span=self.wing.planform_wingspan,
            )
            for y in (y_A, y_B, y_pc)
        ]

        # division of the chord in m equal panels
        dx_AC, dx_BD, dx_pc = [c / self.mesh.m for c in (c_AC, c_BD, c_pc)]

        # r,s,q are the X coordinates of the quarter chord line at spanwise
        # locations: y_A, y_B and y_pc respectively
        r, s, q = [
            get_quarter_chord_x(y, cr=self.wing.root_chord, sweep=self.wing.sweep_angle)
            for y in (y_A, y_B, y_pc)
        ]

        x_A = (r - c_AC / 4) + i * dx_AC
        x_B = (s - c_BD / 4) + i * dx_BD
        x_C = x_A + dx_AC
        x_D = x_B + dx_BD
        x_pc = (q - c_pc / 4) + (i + 3 / 4) * dx_pc

        x = np.array([x_A, x_B, x_D, x_C])
        y = np.array([y_A, y_B, y_D, y_C])
        z = np.tan(self.wing.dihedral_angle) * np.abs(y)
        panel = np.stack((x, y, z), axis=-1)

        z_pc = np.tan(self.wing.dihedral_angle) * np.abs(y_pc)
        pc = np.array([x_pc, y_pc, z_pc])

        return panel, pc

    def _build_wing_panels(self):
        """
        Build wing panels and collocation points.

        Creates
        -------
        self.wing_panels : np.ndarray, shape (m, n, 4, 3)
            Array containing the (x,y,z) coordinates of all wing panel vertices.
        self.cpoints : np.ndarray, shape (m, n, 3)
            Array containing the (x,y,z) coordinates of all collocation points.
        """

        self.wing_panels = np.empty((self.mesh.m, self.mesh.n, 4, 3))
        self.cpoints = np.empty((self.mesh.m, self.mesh.n, 3))

        for i in range(self.mesh.m):
            for j in range(self.mesh.n):
                self.wing_panels[i, j], self.cpoints[i, j] = self._build_panel(i, j)

    def _build_wing_vortex_panels(self):
        """
        Creates
        -------
        aic : np.ndarray, shape (m, n, 4, 3)
            Array containing the (x,y,z) coordinates of all vortex panel vertices.
        """
        X, Y, Z = [self.wing_panels[:, :, :, i] for i in range(3)]

        dxv = (X[:, :, [3, 2, 2, 3]] - X[:, :, [0, 1, 1, 0]]) / 4
        XV = X + dxv

        YV = Y

        ZV = np.empty((self.mesh.m, self.mesh.n, 4))
        Z01 = Z[:, :, [0, 1]]
        dzv = Z[:, :, [3, 2]] - Z01
        ZV[:, :, [0, 1]] = Z01 + 1 / 4 * dzv
        ZV[:, :, [3, 2]] = Z01 + 5 / 4 * dzv

        self.vortex_panels = np.stack([XV, YV, ZV], axis=3)

    def _calculate_panel_normal_vectors(self):
        """
        Calculate the normal vector for each wing panel, approximated
        by the direction of the cross product of the panel diagonals.

        Creates
        -------
        normals : np.ndarray, shape (m, n, 3)
            Array containing the normal vectors to all wing panels.
        """
        d1 = self.wing_panels[:, :, 2] - self.wing_panels[:, :, 0]
        d2 = self.wing_panels[:, :, 1] - self.wing_panels[:, :, 3]
        nv = np.cross(d1, d2)

        self.normals = nv / np.linalg.norm(nv, ord=2, axis=2, keepdims=True)

    def _calculate_wing_planform_surface(self):
        """
        Calculate the planform projected surface of all wing panels.

        Creates
        -------
        panel_surfaces : np.ndarray, shape (m, n)
            Array containing the planform (projected) surface of each panel.
        """

        x, y = [self.wing_panels[:, :, :, i] for i in range(2)]

        # shoelace formula to calculate flat polygon area (XY projection)
        einsum_str = "ijk,ijk->ij"
        d1 = np.einsum(einsum_str, x, np.roll(y, 1, axis=2))
        d2 = np.einsum(einsum_str, y, np.roll(x, 1, axis=2))
        self.panel_surfaces = 0.5 * np.abs(d1 - d2)

    def _build_wake(self, offset=300):
        """
        Build the steady wake vortex panels.

        offset : int
            Downstream distance at which the steady wake is truncated
            (expressed in multiples of the wingspan)

        Creates
        -------
        wake : np.ndarray, shape (n, 4, 3)
            Array containing the (x,y,z) coordinates of the panel vertices that
            form the steady wake.
        """
        self.wake = np.empty((self.mesh.n, 4, 3))
        self.wake[:, [0, 1]] = self.vortex_panels[self.mesh.m - 1][:, [3, 2]]
        delta = (
            offset
            * self.wing.planform_wingspan
            * np.array(
                [
                    np.cos(self.flight_conditions.aoa),
                    0,
                    np.sin(self.flight_conditions.aoa),
                ]
            )
        )
        self.wake[:, [3, 2]] = self.wake[:, [0, 1]] + delta

    def _calculate_wing_influence_matrix(self):
        """
        Calculate influence matrix (wing contribution).

        Creates
        -------
        aic : np.ndarray, shape (m * n, m * n)
            Wing contribution to the influence matrix.
        """
        r = self.vortex_panels.reshape(
            (self.mesh.m * self.mesh.n, 1, 4, 3)
        ) - self.cpoints.reshape((1, self.mesh.m * self.mesh.n, 1, 3))

        vel = biot_savart(r)
        nv = self.normals.reshape((self.mesh.m * self.mesh.n, 3))
        self.aic_wing = np.einsum("ijk,jk->ji", vel, nv)

    def _calculate_wake_wing_influence_matrix(self):
        """
        Calculate influence matrix (steady wake contribution).

        Creates
        -------
        aic : np.ndarray, shape (m * n, m * n)
            Wake contribution to the influence matrix.
        """
        mn = self.mesh.m * self.mesh.n
        self.aic_wake = np.zeros((mn, mn))
        r = self.wake[:, np.newaxis, :, :] - self.cpoints.reshape((1, mn, 1, 3))
        vel = biot_savart(r)
        nv = self.normals.reshape((mn, 3))
        self.aic_wake[:, -self.mesh.n :] = np.einsum("ijk,jk->ji", vel, nv)

    def _calculate_influence_matrix(self):
        """
        Creates
        -------
        aic : np.ndarray, shape (m * n, m * n)
            Influence matrix, including wing and wake contributions.
        """
        self._calculate_wing_influence_matrix()
        self._calculate_wake_wing_influence_matrix()
        self.aic = self.aic_wing + self.aic_wake

    def _calculate_rhs(self):
        """
        Returns
        -------
        rhs : np.ndarray, shape (m * n, )
            RHS vector.
        """
        u = self.flight_conditions.ui * np.array(
            [np.cos(self.flight_conditions.aoa), 0, np.sin(self.flight_conditions.aoa)]
        )
        self.rhs = -np.dot(self.normals.reshape(self.mesh.m * self.mesh.n, -1), u)

    def _solve_net_panel_circulation_distribution(self):
        """
        Calculate panel net circulation by solving the linear equation:
        AIC * circulation = RHS

        Creates
        -------
        net_circulation : np.ndarray, shape (m, n)
            Array containing net circulation for each panel.
        """
        g = np.linalg.solve(self.aic, self.rhs).reshape(self.mesh.m, self.mesh.n)

        self.net_circulation = np.empty_like(g)
        self.net_circulation[0, :] = g[0, :]
        self.net_circulation[1:, :] = g[1:, :] - g[:-1, :]

    def _calculate_aero_distributions_from_circulation(self):
        m, n = self.mesh.m, self.mesh.n
        rho, ui = (
            self.flight_conditions.rho,
            self.flight_conditions.ui,
        )
        bp = self.wing.planform_wingspan
        dL = self.net_circulation * rho * ui * bp / n
        dp = dL / self.panel_surfaces
        cl = dp / (0.5 * rho * ui ** 2)
        cl_wing = dL.sum() / (0.5 * rho * ui ** 2 * self.panel_surfaces.sum())
        cl_span = cl.sum(axis=0) / m
        return SimulationResults(dL=dL, dp=dp, cl=cl, cl_wing=cl_wing, cl_span=cl_span)


def get_quarter_chord_x(y, cr, sweep):
    # slope of the quarter chord line
    p = np.tan(sweep)
    return cr / 4 + p * abs(y)


def get_chord_at_section(y, root_chord, tip_chord, span):
    c = root_chord + (tip_chord - root_chord) * abs(2 * y / span)
    return c


def norm_23_ext(v):
    return np.linalg.norm(v, ord=2, axis=3, keepdims=True)


def biot_savart(r1):
    r2 = np.roll(r1, shift=-1, axis=2)
    cp = np.cross(r1, r2)
    d1 = r2 - r1
    d2 = r1 / norm_23_ext(r1) - r2 / norm_23_ext(r2)
    vel = np.einsum("ijkl,ijkl->ijk", d1, d2)[:, :, :, np.newaxis]
    vel = -1 / (4 * np.pi) * cp / (norm_23_ext(cp) ** 2) * vel
    return vel.sum(axis=2)
