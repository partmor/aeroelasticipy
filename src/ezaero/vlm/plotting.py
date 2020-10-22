import numpy as np
import plotly.graph_objects as go

CL_COLORSCALE = [
    "#e1f5fe",
    "#b3e5fc",
    "#81d4f4",
    "#4fc3f7",
    "#29b6f6",
    "#03a9f4",
    "#039be5",
    "#0288d1",
    "#0277bd",
    "#01579b",
]


def plot_panel(xyz, fig=None, color="blue", limit_color="black", limit_width=2):
    """Returns a graphical representation for the panels

    Parameters
    ----------
    xyz: np.ndarray
        An array of NxM size containing arrays of 4x3 for panel's boundaries
    fig: ~plotly.graph_objects.figure
        The figure used as canvas
    color: string
        Main color for the panel
    limit_color: string
        Color for representing the boundaries of the panel
    limit_width: int
        Controls the line width of the boundaries line

    """

    # Check if figure available
    if not fig:
        fig = go.Figure()
        fig.update_layout(scene_aspectmode="data")

    # Get the wing_panels matrix dimensions
    # m, n = x.shape[0], x.shape[1]

    # Add a trace for each panel
    # for i in range(m):
    # for j in range(n):

    panel_surface = go.Mesh3d(
        x=xyz[:, 0],
        y=xyz[:, 1],
        z=xyz[:, 2],
        color=color,
        showlegend=False,
    )
    panel_limits = go.Scatter3d(
        x=xyz[:, 0],
        y=xyz[:, 1],
        z=xyz[:, 2],
        line=dict(color=limit_color, width=limit_width),
        marker=dict(size=2),
        showlegend=False,
    )

    fig.add_trace(panel_surface)
    fig.add_trace(panel_limits)

    return fig


def plot_panels(wing_panels, fig=None, color="blue", limit_color="black"):
    """Returns a graphical representation for wing panels

    Parameters
    ----------
    wing_panels: np.ndarray
        A multidimensional matrix holding all panels boundaries positions
    fig: ~plotly.graph_objects.figure
        The figure used as canvas
    color: string
        The color for each panel
    limit_color:
        The color for panel boundaries

    Returns
    -------
    fig: ~plotly.graph_objects.figure
        The figure used as canvas

    """

    # Check if figure available
    if not fig:
        fig = go.Figure()
        fig.update_layout(scene_aspectmode="data")

    # Get the wing_panels matrix dimensions
    m, n = wing_panels.shape[0], wing_panels.shape[1]

    # Add a trace for each panel
    for i in range(m):
        for j in range(n):

            # Get particular panel boundaries
            xyz = wing_panels[i, j]

            # Plot a particular panel
            fig = plot_panel(xyz, fig=fig, color=color)

    return fig


def plot_control_points(cpoints, fig=None, color="red", marker_size=4):
    """Adds graphic control points graphical representation

    Parameters
    ----------
    cpoints: np.ndarray
        Matrix holding panels' control points
    fig: ~plotly.graph_objects.figure
        The figure used as canvas
    color: string
        Color for the collocations points
    marker_size: int
        Integer to represent marker size of the point

    Returns
    -------
    fig: ~plotly.graph_objects.figure
        The figure used as canvas
    """

    # Check if figure available
    if not fig:
        fig = go.Figure()
        fig.update_layout(scene_aspectmode="data")

    # Generate control points trace
    trace_cp = go.Scatter3d(
        x=cpoints[:, :, 0].ravel(),
        y=cpoints[:, :, 1].ravel(),
        z=cpoints[:, :, 2].ravel(),
        mode="markers",
        marker=dict(color=color, size=marker_size),
        showlegend=False,
    )
    fig.add_trace(trace_cp)

    return fig


def plot_cl_distribution_on_wing(wing_panels, res, fig=None, colorscale=None):
    """Generates a graphical representation for the lift coeffient distribution

    Parameters
    ----------
    wing_panels: np.ndarray
        A multidimensional matrix holding all panels boundaries positions
    res: Simulation
        A simulation instance holding results of the analysis
    fig: ~plotly.graph_objects.Figure
        A figure used as canvas
    colorscale: list
        A list of color strings in ascendent ordergradient

    Returns
    -------
    fig: ~plotly.graph_objects.Figure
        A figure used as canvas

    """

    # Check if figure available
    if not fig:
        fig = go.Figure()
        fig.update_layout(scene_aspectmode="data")

    # Unpack the lift distribution from results data
    cl_dist = res.cl

    # Check if colorscale available
    if not colorscale:
        cl_range = np.linspace(np.min(cl_dist), np.max(cl_dist), len(CL_COLORSCALE))

    # Get the wing_panels matrix dimensions
    m, n = wing_panels.shape[0], wing_panels.shape[1]

    # Add a trace for each panel
    for i in range(m):
        for j in range(n):

            # Get particular panel boundaries
            xyz = wing_panels[i, j]

            # Solve proper color
            color_idx = np.where(cl_range <= cl_dist[i, j])[0][-1]
            color = CL_COLORSCALE[color_idx]

            # Plot a particular panel
            fig = plot_panel(xyz, fig=fig, color=color)

    return fig
