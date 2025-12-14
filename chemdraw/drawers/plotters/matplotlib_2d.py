import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.drawers.two_d.primitives_for_drawing import Dots, Fills, Lines, Texts, DrawingContainer
from chemdraw.utils.color_converter import convert_colors

try:
    import matplotlib.pyplot as plt
    from matplotlib.text import TextPath
    from matplotlib.path import Path
    from matplotlib.collections import PathCollection
    from matplotlib.font_manager import FontProperties
except ImportError:
    raise ImportError("Please install matplotlib with `pip install matplotlib` or use another plotting package.")


def draw_single_2d(container: DrawingContainer) -> plt.Figure:
    box = container.bounding_box()
    fig, ax = plt.subplots(figsize=(max(box[0]) - min(box[0]), max(box[1]) - min(box[1])),
                           dpi=STYLE_TEMPLATE.matplotlib_dpi)

    draw_containers(ax, container)
    apply_layout(ax, container)

    return fig


def apply_layout(ax: plt.Axes, container: DrawingContainer):
    # 1. Colors
    bg_color = convert_colors(STYLE_TEMPLATE.plot_background_color, "matplotlib")
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
    abs_buffer = STYLE_TEMPLATE.plot_buffer_abs
    ax.set_xlim(x_span[0] - dx * scale - abs_buffer, x_span[1] + dx * scale + abs_buffer)
    ax.set_ylim(y_span[0] - dy * scale - abs_buffer, y_span[1] + dy * scale +abs_buffer)

    # 3. Turn off axes (ticks, spines, labels)
    ax.axis('off')

    # 4. Aspect Ratio
    # Chemical drawings usually require an equal aspect ratio to prevent distortion
    ax.set_aspect('equal')

    # Remove margins to emulate layout margin=0
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)


def draw_containers(ax: plt.Axes, container: DrawingContainer):
    for c in container.containers:
        if c is None:
            draw_one_layer_of_container(ax, container)
        else:
            draw_containers(ax, c) # recursive call


def draw_one_layer_of_container(ax: plt.Axes, container: DrawingContainer):
    # Order matters for z-index (painters algorithm)
    draw_dots(ax, container.dots)
    draw_lines(ax, container.lines)
    draw_fills(ax, container.fills)
    if STYLE_TEMPLATE.sub_plotter == "path":
        draw_texts_path(ax, container.texts)
    else:
        draw_texts(ax, container.texts)


def draw_dots(ax: plt.Axes, dots: list[Dots]):
    for d in dots:
        # Scatter s argument is area in points^2.
        # Plotly size is often diameter. We might need to adjust 's' scaling.
        # Roughly: s = (diameter * scale)^2.
        ax.scatter(
            d.x,
            d.y,
            c=[convert_colors(d.color, "matplotlib")],
            s=np.array(d.size) ** 2,  # Squaring assuming input is diameter
            edgecolors='none',
            # zorder=10  # Ensure dots sit on top if needed
        )


def draw_lines(ax: plt.Axes, lines: list[Lines]):
    # Map Plotly dash styles to Matplotlib styles
    dash_map = {
        "solid": "-",
        "dot": ":",
        "dash": "--",
        "longdash": "--",  # MPL doesn't have distinct longdash
        "dashdot": "-.",
    }

    for l in lines:
        linestyle = dash_map.get(l.dash, "-")  # Default to solid

        # Plotly separates lines in a list if there are gaps, or uses None.
        # Assuming l.x and l.y are continuous segments here.
        ax.plot(
            l.x,
            l.y,
            color=convert_colors(l.color, "matplotlib"),
            linewidth=l.width,
            linestyle=linestyle,
            solid_capstyle='round'
        )


def draw_fills(ax: plt.Axes, fills: list[Fills]):
    for f in fills:
        ax.fill(
            f.x,
            f.y,
            color=convert_colors(f.color, "matplotlib"),
            edgecolor=None,  # line width 0 equivalent
            linewidth=0
        )


def get_ax_text_dims(ax, text_obj):
    # 1. You must have a canvas (fig.canvas)
    # 2. You must get the renderer
    renderer = ax.figure.canvas.get_renderer()

    # 3. Get the bounding box in Display Coordinates (Pixels)
    bbox = text_obj.get_window_extent(renderer)

    # 4. (Optional) Convert pixels back to Data Coordinates
    bbox_data = bbox.transformed(ax.transData.inverted())

    return bbox_data.width, bbox_data.height


# ISSUE: ax.text scales with fig size
def draw_texts(ax: plt.Axes, text_objs: list[Texts]):
    text_scaler = 65

    for t in text_objs:
        # Normalize inputs to lists if they are scalars
        xs = t.x if isinstance(t.x, (list, np.ndarray)) else [t.x]
        ys = t.y if isinstance(t.y, (list, np.ndarray)) else [t.y]
        syms = t.symbols if isinstance(t.symbols, (list, np.ndarray)) else [t.symbols]

        for x, y, s in zip(xs, ys, syms):
            tt = ax.text(
                x,
                y,
                f"{STYLE_TEMPLATE.get_text_break()}".join(s) if isinstance(s, (list, tuple)) else s,
                color=convert_colors(t.color, "matplotlib"),
                fontsize=t.size * text_scaler,
                fontfamily=t.font,
                linespacing=0.9 if isinstance(s, list) and len(s[0]) == 1 else 1.1,  # 0.9 for H and 1.1 for titles
                ha='center',  # Horizontal alignment: center (matches Plotly text mode default)
                va='center',  # Vertical alignment: center
                clip_on=False  # Allow text to overlap edges slightly like Plotly
            )


def draw_texts_path(ax: plt.Axes, text_objs: list[Texts]):
    paths = []
    colors = []

    for t in text_objs:
        t.prepare_for_drawing("\n")
        xs = t.x if isinstance(t.x, (list, np.ndarray)) else [t.x]
        ys = t.y if isinstance(t.y, (list, np.ndarray)) else [t.y]
        syms = t.symbols if isinstance(t.symbols, (list, np.ndarray)) else [t.symbols]
        fp = FontProperties(family=t.font)

        for x, y, s in zip(xs, ys, syms):
            # Use our new helper to generate the multiline path
            path = create_multiline_textpath(x, y, s, t.size, fp)

            if path:
                paths.append(path)
                colors.append(convert_colors(t.color, "matplotlib"))

    if not paths:
        return

    # Create the efficient collection
    pc = PathCollection(
        paths,
        facecolors=colors,
        edgecolors='none',
        linewidths=0
    )

    pc.set_transform(ax.transData)
    ax.add_collection(pc)


def create_multiline_textpath(x, y, s, size, prop, ha='center', va='center'):
    """
    Creates a single compound Path for multiline text, centered at (x,y).
    """
    lines = s.split('\n')
    if not lines:
        return None

    # 1. Generate raw paths for each line centered at (0,0)
    paths = []
    widths = []

    # Standard line spacing (approx 1.2x font size)
    line_spacing = size * 0.9

    for line in lines:
        # Create path for this line
        tp = TextPath((0, 0), line, size=size, prop=prop)

        # Get width for horizontal centering
        bb = tp.get_extents()
        widths.append(bb.width)
        paths.append(tp)

    # 2. Stack vertices
    all_verts = []
    all_codes = []

    # Calculate total block height to determine vertical offset
    # (lines - 1) * spacing + height of one line (approx 'size')
    total_block_height = (len(lines) - 1) * line_spacing + size

    # Starting Y position (top line) relative to vertical center
    # We shift up by half the total height to center the block
    current_y = (total_block_height / 2) - (size / 2)  # Adjust to align baseline roughly

    for i, (tp, w) in enumerate(zip(paths, widths)):
        # Get vertices (must copy because they are read-only)
        verts = tp.vertices.copy()
        codes = tp.codes

        # Horizontal Alignment (Center)
        # Shift left by half the line width
        verts[:, 0] -= w / 2

        # Vertical Alignment
        # Move this line to its slot in the stack
        verts[:, 1] += current_y

        # Move cursor down for next line
        current_y -= line_spacing

        all_verts.append(verts)
        all_codes.append(codes)

    # 3. Merge into one compound path and shift to target (x, y)
    merged_verts = np.vstack(all_verts)
    merged_verts[:, 0] += x
    merged_verts[:, 1] += y
    merged_codes = np.concatenate(all_codes)

    return Path(merged_verts, merged_codes)
