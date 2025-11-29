from typing import Sequence
from functools import lru_cache

HAS_MATPLOTLIB = False
HAS_PIL = False

try:
    from matplotlib.text import TextPath
    from matplotlib.font_manager import FontProperties
    HAS_MATPLOTLIB = True
except ImportError:
    pass

try:
    from PIL import ImageFont, ImageDraw, Image
    HAS_PIL = True
except ImportError:
    pass

from chemdraw.config.style_template import STYLE_TEMPLATE


# Loading fonts is slow (IO). We cache the font objects to speed up repeated calls.
@lru_cache(maxsize=32)
def _get_pil_font(font_path: str, font_size: int):
    """Loads and caches a PIL ImageFont object."""
    if not HAS_PIL:
        return None
    try:
        return ImageFont.truetype(font_path, font_size)
    except OSError:
        # Fallback to default if custom font fails
        print(f"Warning: Could not load font at {font_path}. Using default.")
        return ImageFont.load_default()


def _measure_matplotlib(text: str, font: str, size: float) -> tuple[float, float]:
    """Calculates dimensions using Matplotlib TextPath."""
    fp = FontProperties(family=font)
    # Position (0,0) doesn't matter for extent calculation
    tp = TextPath((0, 0), text, size=size, prop=fp)
    bbox = tp.get_extents()
    return bbox.width, bbox.height


def _measure_pil(text: str, font_path: str, size: float) -> tuple[float, float]:
    """Calculates dimensions using Pillow."""
    font = _get_pil_font(font_path, int(size))

    # Create a dummy image for the drawing context
    # (We don't need to cache the image, creation is fast)
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)

    # textbbox returns (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def _measure_heuristic(text: str, size: int | float) -> tuple[float, float]:
    """Fallback calculation based on average character size."""
    multiplier = size/10
    return STYLE_TEMPLATE.text_width * len(text) * multiplier, STYLE_TEMPLATE.text_height * multiplier


def get_text_dimensions(text: str | Sequence[str], font: str, size: float) -> tuple[float, float]:
    """
    Calculates the width and height of text.

    Args:
        text: A single string or a list of strings (multiline).
        font: Font family name (if matplotlib) or file path (if PIL).
        size: Font size.

    Returns:
        (width, height)
    """

    # 1. Normalize input to a list for unified processing
    lines = [text] if isinstance(text, str) else text

    # 2. Define the measurement strategy
    def measure_line(line_str):
        if HAS_MATPLOTLIB and STYLE_TEMPLATE.text_calculator == "auto":
            return _measure_matplotlib(line_str, font, size)
        elif HAS_PIL and STYLE_TEMPLATE.text_calculator == "auto":
            return _measure_pil(line_str, font, size)
        else:
            return _measure_heuristic(line_str, size)

    # 3. Calculate dimensions for all lines
    # If list is empty, return 0
    if not lines:
        return 0.0, 0.0

    widths = []
    heights = []

    for line in lines:
        w, h = measure_line(line)
        widths.append(w)
        heights.append(h)

    # 4. Aggregate results
    # Width is the widest line
    total_width = max(widths)
    # Height is the sum of all lines (plus optional leading/spacing logic if desired)
    total_height = sum(heights)

    return total_width, total_height


def get_max_of_all_letters(font: str, size: float):
    import string
    upper_letter = list(string.ascii_uppercase)
    width = []
    height = []
    for letter in upper_letter:
        w, h = _measure_matplotlib(letter, font, size)
        width.append(w)
        height.append(h)

    return max(width), max(height)



def run_local():
    for i in (2,4,8, 10, 16, 28):
        print(i, get_max_of_all_letters("arial", i))

    for i in (2,4,8, 10, 16, 28):
        print(i, _measure_matplotlib("O", "arial", i))


if __name__ == "__main__":
    run_local()
