import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
import numpy as np
from matplotlib import cm


def plot_panels(
    x, elev=25, azim=-160, edge_color="k", fill_color=1, transp=0.2, ax=None
):

    m, n = x.shape[0], x.shape[1]
    X, Y, Z = [x[:, :, :, i] for i in range(3)]
    bp = Y.max() - Y.min()
    new_ax = not ax
    if new_ax:
        ax = a3.Axes3D(plt.figure())
    for i in range(m):
        for j in range(n):
            vtx = np.array([X[i, j], Y[i, j], Z[i, j]]).T
            panel = a3.art3d.Poly3DCollection([vtx])
            panel.set_facecolor((0, 0, fill_color, transp))
            panel.set_edgecolor(edge_color)
            ax.add_collection3d(panel)
    if new_ax:
        limits = (-bp / 1.8, bp / 1.8)
        ax.set_xlim(limits)
        ax.set_ylim(limits)
        ax.set_zlim(limits)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(elev=elev, azim=azim)
    return ax


def plot_control_points(cpoints, ax):
    ax.scatter(
        xs=cpoints[:, :, 0].ravel(),
        ys=cpoints[:, :, 1].ravel(),
        zs=cpoints[:, :, 2].ravel(),
    )
    return ax


def plot_cl_distribution_on_wing(
    wing_panels, res, cmap=cm.coolwarm, elev=25, azim=-160
):
    m, n = wing_panels.shape[:2]
    bp = wing_panels[:, :, :, 1].max() - wing_panels[:, :, :, 1].min()
    cl_dist = res.cl

    X, Y, Z = [wing_panels[:, :, :, i] for i in range(3)]
    norm = plt.Normalize()
    face_colors = cmap(norm(cl_dist))
    fig = plt.figure()
    ax = a3.Axes3D(fig)
    for i in range(m):
        for j in range(n):
            vtx = np.array([X[i, j], Y[i, j], Z[i, j]]).T
            panel = a3.art3d.Poly3DCollection([vtx])
            panel.set_facecolor(
                (face_colors[i, j][0], face_colors[i, j][1], face_colors[i, j][2])
            )
            panel.set_edgecolor("k")
            ax.add_collection3d(panel)
    limits = (-bp / 1.8, bp / 1.8)
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.set_zlim(limits)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=elev, azim=azim)
    sm = cm.ScalarMappable(norm, cmap)
    sm.set_array(cl_dist)
    cbar = fig.colorbar(sm, shrink=0.5, aspect=6, extend="both")
    cbar.ax.set_xlabel(r"C$_{L_{wing}}$")
