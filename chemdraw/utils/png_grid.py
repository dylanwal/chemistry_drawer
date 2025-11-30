import pathlib
import math
import warnings
from typing import Sequence


def png_grid(imgs_path: str | pathlib.Path, output_path: str | pathlib.Path, shape: Sequence[int] = None):
    """
    Stitches PNGs from a directory into a single grid image.

    Parameters
    ----------
    imgs_path : str | pathlib.Path
        Folder where images are stored.
    output_path : str | pathlib.Path
        Full path where the output image will be saved (e.g., 'output/grid.png').
    shape : Sequence[int] | None
        None: an approximate square grid is calculated automatically
        Sequence len(2): (num_rows, num_columns)
        Sequence not len(2): each int is a row the value is the number of molecules in that row.
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Please install Pillow to use this function 'pip install Pillow'.")


    # files stuff
    imgs_path = pathlib.Path(imgs_path).resolve()
    if not imgs_path.exists():
        raise FileNotFoundError(imgs_path)
    output_path = pathlib.Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_files = sorted(imgs_path.glob('*.png'))
    if not img_files:
        print(f"No .png files found in {imgs_path}")
        return

    # 3. Determine Grid Dimensions
    total_images = len(img_files)

    if shape is not None and len(shape) == 2:
        if shape[0] * shape[1] > total_images:
            shape = [shape[1]] * shape[0]
        else:
            warnings.warn(
                f"`shape` for grid drawing does not match number of molecules. "
                f"Reverting to default shape."
            )
            shape = None
    elif shape is not None:
        total_grid_spots = sum(shape)
        if total_grid_spots < total_images:
            warnings.warn(
                f"`shape` for grid drawing does not match number of molecules. "
                f"Reverting to default shape."
            )
            shape = None
    if shape is None:
        # Auto-calculate a square-ish grid
        cols = math.ceil(math.sqrt(total_images))
        rows = math.ceil(total_images / cols)
        shape = [cols] * rows

    # 4. Calculate Cell Size (Scan all to find max width/height)
    # We use a context manager to peek at size without keeping files open
    max_w, max_h = 0, 0
    for f in img_files:
        with Image.open(f) as img:
            max_w = max(max_w, img.width)
            max_h = max(max_h, img.height)

    # 5. Create Canvas
    grid_width = max_w * cols
    grid_height = max_h * rows

    # Create transparent background
    canvas = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))

    # 6. Paste Images
    count = 0
    DONE = False
    for i, len_row in enumerate(shape):
        if DONE:
            break
        for j in range(len_row):
            x_pos = j * max_w
            y_pos = i * max_h
            with Image.open(img_files[count]) as img:
                center_x = (max_w - img.width) // 2
                center_y = (max_h - img.height) // 2
                canvas.paste(img, (x_pos+center_x, y_pos+center_y))
            count += 1
            if count == total_images:
                DONE = True
                break

    # 7. Save
    canvas.save(output_path)

if __name__ == "__main__":
    path = pathlib.Path(r"C:\Users\nicep\Desktop\pyth_proj\chemdraw\examples\test_imgs")
    png_grid(path, "output_grid.png")
