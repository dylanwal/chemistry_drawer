import matplotlib.pyplot as plt
import numpy as np

# Assuming these imports exist in your environment as per your original code
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.drawers.two_d.primitives_for_drawing import Dots, Fills, Lines, Texts, DrawingContainer

def draw_single_2d(container: DrawingContainer) -> plt.Figure:
    # Create figure and axes
    # Matplotlib sizes are in inches, so we convert pixels to inches using a DPI
    dpi = 100
    w = STYLE_TEMPLATE.plot_width / dpi
    h = STYLE_TEMPLATE.plot_height / dpi

    fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)

    draw_containers(ax, container)
    apply_layout(ax, container)

    return fig

def apply_layout(ax: plt.Axes, container: DrawingContainer):
    # 1. Colors
    bg_color = STYLE_TEMPLATE.plot_background_color
    ax.set_facecolor(bg_color)
    ax.figure.set_facecolor(bg_color)

    # 2. Calculate Limits (Bounding Box)
    points = container.bounding_box()
    x_span = np.array([np.min(points[0]), np.max(points[0])])
    y_span = np.array([np.min(points[1]), np.max(points[1])])
    dx = x_span[1] - x_span[0]
    dy = y_span[1] - y_span[0]
    scale = STYLE_TEMPLATE.plot_buffer

    # Apply limits with buffer
    ax.set_xlim(x_span[0] - dx * scale, x_span[1] + dx * scale)
    ax.set_ylim(y_span[0] - dy * scale, y_span[1] + dy * scale)

    # 3. Turn off axes (ticks, spines, labels)
    ax.axis('off')

    # 4. Aspect Ratio
    # Chemical drawings usually require an equal aspect ratio to prevent distortion
    ax.set_aspect('equal')

    # Remove margins to emulate layout margin=0
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)


def draw_containers(ax: plt.Axes, container: DrawingContainer):
    # Order matters for z-index (painters algorithm)
    draw_dots(ax, container.dots)
    draw_lines(ax, container.lines)
    draw_fills(ax, container.fills)
    draw_texts(ax, container.texts)

def draw_dots(ax: plt.Axes, dots: list[Dots]):
    for d in dots:
        # Scatter s argument is area in points^2.
        # Plotly size is often diameter. We might need to adjust 's' scaling.
        # Roughly: s = (diameter * scale)^2.
        ax.scatter(
            d.x,
            d.y,
            c=d.color,
            s=np.array(d.size)**2, # Squaring assuming input is diameter
            edgecolors='none',
            zorder=10 # Ensure dots sit on top if needed
        )

def draw_lines(ax: plt.Axes, lines: list[Lines]):
    # Map Plotly dash styles to Matplotlib styles
    dash_map = {
        "solid": "-",
        "dot": ":",
        "dash": "--",
        "longdash": "--", # MPL doesn't have distinct longdash
        "dashdot": "-.",
    }

    for l in lines:
        linestyle = dash_map.get(l.dash, "-") # Default to solid

        # Plotly separates lines in a list if there are gaps, or uses None.
        # Assuming l.x and l.y are continuous segments here.
        ax.plot(
            l.x,
            l.y,
            color=l.color,
            linewidth=l.width,
            linestyle=linestyle,
            solid_capstyle='round'
        )

def draw_fills(ax: plt.Axes, fills: list[Fills]):
    for f in fills:
        # fill argument fills the polygon defined by x and y
        ax.fill(
            f.x,
            f.y,
            color=f.color,
            edgecolor=None, # line width 0 equivalent
            linewidth=0
        )

def draw_texts(ax: plt.Axes, text_objs: list[Texts]):
    for t in text_objs:
        # Matplotlib text() does not accept arrays for x/y/text.
        # We must iterate if the primitive contains lists of coordinates.

        # Normalize inputs to lists if they are scalars
        xs = t.x if isinstance(t.x, (list, np.ndarray)) else [t.x]
        ys = t.y if isinstance(t.y, (list, np.ndarray)) else [t.y]
        syms = t.symbols if isinstance(t.symbols, (list, np.ndarray)) else [t.symbols]

        for x, y, s in zip(xs, ys, syms):
            ax.text(
                x,
                y,
                s,
                color=t.color,
                fontsize=t.size,
                fontfamily=t.font,
                ha='center', # Horizontal alignment: center (matches Plotly text mode default)
                va='center', # Vertical alignment: center
                clip_on=False # Allow text to overlap edges slightly like Plotly
            )