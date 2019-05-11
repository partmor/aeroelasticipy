from collections import namedtuple
import numpy as np


WingParams = namedtuple('WingParams', 'cr, ct, bp, theta, delta')
MeshParams = namedtuple('MeshParams', 'm, n')
FlightConditions = namedtuple('FlightConditions', 'ui, alpha, rho')


def get_quarter_chord_x(y, cr, theta):
    # slope of the quarter chord line
    p = np.tan(theta)
    return cr / 4 + p * abs(y)


def get_chord_at_section(y, cr, ct, bp):
    c = cr + (ct - cr) * abs(2 * y / bp)
    return c


def build_panel(wing: WingParams, mesh: MeshParams, i: int, j: int):
    """
        ^x    C --- D
    y   |     |     |
    <---*     A --- B

    A-B = forward segment
    C-D = rear segment
    Clockwise sequence: ABDC
    """

    dy = wing.bp / mesh.n
    y_A = - wing.bp / 2 + j * dy
    y_B = y_A + dy
    y_C, y_D = y_A, y_B
    y_pc = y_A + dy / 2

    # chord law evaluation
    c_AC = get_chord_at_section(y_A, cr=wing.cr, ct=wing.ct, bp=wing.bp)
    c_BD = get_chord_at_section(y_B, cr=wing.cr, ct=wing.ct, bp=wing.bp)
    c_pc = get_chord_at_section(y_pc, cr=wing.cr, ct=wing.ct, bp=wing.bp)

    # division of the chord in m equal panels
    dx_AC = c_AC / mesh.m
    dx_BD = c_BD / mesh.m
    dx_pc = c_pc / mesh.m

    # r,s,q are the X coordinates of the quarter chord line at spanwise
    # locations: y_A, y_B and y_pc respectively
    r = get_quarter_chord_x(y_A, cr=wing.cr, theta=wing.theta)
    s = get_quarter_chord_x(y_B, cr=wing.cr, theta=wing.theta)
    q = get_quarter_chord_x(y_pc, cr=wing.cr, theta=wing.theta)

    x_A = (r - c_AC / 4) + i * dx_AC
    x_B = (s - c_BD / 4) + i * dx_BD
    x_C = x_A + dx_AC
    x_D = x_B + dx_BD
    x_pc = (q - c_pc / 4) + (i + 3 / 4) * dx_pc

    x = np.array([x_A, x_B, x_D, x_C])
    y = np.array([y_A, y_B, y_D, y_C])
    z = np.tan(wing.delta) * np.abs(y)
    panel = np.stack((x, y, z), axis=-1)

    z_pc = np.tan(wing.delta) * np.abs(y_pc)
    pc = np.array([x_pc, y_pc, z_pc])

    return panel, pc


def build_wing_panels(wing: WingParams, mesh: MeshParams):
    """
    output:
        X[spanwise ix, chordwise ix, vertex ix, dimension ix]
        X_pc[spanwise ix, chordwise ix, dimension ix]
    """
    m, n = mesh.m, mesh.n

    X = np.empty((m, n, 4, 3))
    X_pc = np.empty((m, n, 3))

    for i in range(m):
        for j in range(n):
            X[i, j], X_pc[i, j] = build_panel(wing, mesh, i, j)

    return X, X_pc


def build_wing_vortex_panels(wing_panels: np.ndarray):
    """
    output:
        vortex_panels[spanwise ix, chordwise ix, vertex ix, dimension ix]
    """
    m, n = wing_panels.shape[:2]
    X, Y, Z = [wing_panels[:, :, :, i] for i in range(3)]

    dxv = (X[:, :, [3, 2, 2, 3]] - X[:, :, [0, 1, 1, 0]]) / 4
    XV = X + dxv

    YV = Y

    ZV = np.empty((m, n, 4))
    dzv = Z[:, :, [3, 2]] - Z[:, :, [0, 1]]
    ZV[:, :, [0, 1]] = Z[:, :, [0, 1]] + 1 / 4 * dzv
    ZV[:, :, [3, 2]] = Z[:, :, [0, 1]] + 5 / 4 * dzv

    vortex_panels = np.stack([XV, YV, ZV], axis=3)
    return vortex_panels


def get_panel_normal_vectors(wing_panels: np.ndarray):
    m, n = wing_panels.shape[:2]

    # diagonal vectors
    d1 = wing_panels[:, :, 2] - wing_panels[:, :, 0]
    d2 = wing_panels[:, :, 1] - wing_panels[:, :, 3]
    nv = np.cross(d1, d2)

    normal_vector = nv / np.linalg.norm(nv, ord=2, axis=2).reshape((m, n, 1))
    return normal_vector


def get_wing_planform_surface(wing_panels: np.ndarray):
    x, y = [wing_panels[:, :, :, i] for i in range(2)]

    # shoelace formula to calculate flat polygon area
    einsum_str = 'ijk,ijk->ij'
    d1 = np.einsum(einsum_str, x, np.roll(y, 1, axis=2))
    d2 = np.einsum(einsum_str, y, np.roll(x, 1, axis=2))
    panel_surface = 0.5 * np.abs(d1 - d2)

    return panel_surface


def build_steady_wake(flcond: FlightConditions, vortex_panels: np.ndarray,
                      offset=300):

    m, n = vortex_panels.shape[:2]
    bp = vortex_panels[:, :, :, 1].max() - vortex_panels[:, :, :, 1].min()
    alpha = flcond.alpha

    wake = np.empty((n, 4, 3))

    wake[:, [0, 1]] = vortex_panels[m - 1][:, [3, 2]]
    delta = offset * bp * np.array([np.cos(alpha), 0, np.sin(alpha)])
    wake[:, [3, 2]] = wake[:, [0, 1]] + delta

    return wake


def norm(v):
    return np.linalg.norm(v, ord=2, axis=3)[:, :, :, np.newaxis]


def biot_savart_vectorized(r1):
    r2 = np.roll(r1, shift=-1, axis=2)
    cp = np.cross(r1, r2)
    d1 = r2 - r1
    d2 = r1 / norm(r1) - r2 / norm(r2)
    vel = np.einsum('ijkl,ijkl->ijk', d1, d2)[:, :, :, np.newaxis]
    vel = -1 / (4 * np.pi) * cp / (norm(cp)**2) * vel
    return vel.sum(axis=2)


def get_wing_influence_matrix(vortex_panels: np.ndarray,
                              cpoints: np.ndarray, normals: np.ndarray):

    m, n = vortex_panels.shape[:2]

    r = (
        vortex_panels.reshape(m * n, 4, 3)[:, np.newaxis, :, :]
        - cpoints.reshape(m * n, 3)[np.newaxis, :, np.newaxis, :]
    )

    vel = biot_savart_vectorized(r)
    nv = normals.reshape(m * n, 3)[np.newaxis, :, :]
    aic = np.einsum('ijk,ijk->ij', vel, nv).T
    return aic


def get_wake_wing_influence_matrix(cpoints: np.ndarray, wake: np.ndarray,
                                   normals: np.ndarray):

    m, n = cpoints.shape[:2]

    aic_w = np.zeros((m * n, m * n))
    r = wake[:, np.newaxis, :, :] - \
        cpoints.reshape(m * n, 3)[np.newaxis, :, np.newaxis, :]
    vel = biot_savart_vectorized(r)
    nv = normals.reshape(m * n, 3)
    aic_w[:, -n:] = np.einsum('ijk,ijk->ij', vel, nv[np.newaxis, :, :]).T
    return aic_w


def get_influence_matrix(vortex_panels: np.ndarray, wake: np.ndarray,
                         cpoints: np.ndarray, normals: np.ndarray):

    aic = (
        get_wing_influence_matrix(vortex_panels, cpoints, normals)
        + get_wake_wing_influence_matrix(cpoints, wake, normals)
    )
    return aic


def get_rhs(flcond: FlightConditions, normals: np.ndarray):
    m, n = normals.shape[:2]

    u = flcond.ui * np.array([np.cos(flcond.alpha), 0, np.sin(flcond.alpha)])
    rhs = - np.dot(normals.reshape(m * n, -1), u)
    return rhs


def solve_net_panel_circulation_distribution(aic: np.ndarray, rhs: np.ndarray,
                                             m: int, n: int):

    g = np.linalg.solve(aic, rhs).reshape(m, n)

    net_g = np.empty_like(g)
    net_g[0, :] = g[0, :]
    net_g[1:, :] = g[1:, :] - g[:-1, :]

    return net_g


def get_aero_distributions(flcond: FlightConditions,
                           wing: WingParams,
                           mesh: MeshParams,
                           net_circulation: np.ndarray,
                           surface: np.ndarray):

    dL = net_circulation * flcond.rho * flcond.ui * wing.bp / mesh.n
    dp = dL / surface
    cl = dp / (0.5 * flcond.rho * flcond.ui ** 2)
    cl_wing = dL.sum() / (0.5 * flcond.rho * flcond.ui ** 2 * surface.sum())
    cl_span = cl.sum(axis=0) / mesh.m

    return {
        'dL': dL,
        'dp': dp,
        'cl': cl,
        'cl_wing': cl_wing,
        'cl_span': cl_span
    }


def run_simulation(wing: WingParams, mesh: MeshParams,
                   flcond: FlightConditions):

    wing_panels, cpoints = build_wing_panels(wing=wing, mesh=mesh)
    vortex_panels = build_wing_vortex_panels(wing_panels)
    normal_vectors = get_panel_normal_vectors(wing_panels)
    surface = get_wing_planform_surface(wing_panels)
    wake = build_steady_wake(flcond=flcond, vortex_panels=vortex_panels)
    aic = get_influence_matrix(vortex_panels=vortex_panels, wake=wake,
                               cpoints=cpoints, normals=normal_vectors)
    rhs = get_rhs(flcond=flcond, normals=normal_vectors)
    circulation = solve_net_panel_circulation_distribution(
        aic=aic,
        rhs=rhs,
        m=mesh.m,
        n=mesh.n
    )

    res = get_aero_distributions(flcond=flcond, wing=wing, mesh=mesh,
                                 net_circulation=circulation, surface=surface)
    return res
