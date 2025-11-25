import matplotlib.pyplot as plt

def get_ax_text_dims(ax, text_obj):
    # 1. You must have a canvas (fig.canvas)
    # 2. You must get the renderer
    renderer = ax.figure.canvas.get_renderer()

    # 3. Get the bounding box in Display Coordinates (Pixels)
    bbox = text_obj.get_window_extent(renderer)

    # 4. (Optional) Convert pixels back to Data Coordinates
    bbox_data = bbox.transformed(ax.transData.inverted())

    return bbox_data.width, bbox_data.height

# Usage
fig, ax = plt.subplots()
t = ax.text(0.5, 0.5, "Hello", fontsize=12)

# WARNING: This might fail if the plot hasn't been drawn yet.
# You often need to call fig.canvas.draw() once before this works reliably.
w, h = get_ax_text_dims(ax, t)
print(w, h)