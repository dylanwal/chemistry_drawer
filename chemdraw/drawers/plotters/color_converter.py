import re
from typing import Sequence, Tuple, Union, Literal

# Type aliases for clarity
ColorValue = Union[str, Sequence[int], Sequence[float]]
TargetLib = Literal["matplotlib", "plotly"]

COLOR_TYPES = {
    'rgb1',  # string "rgb(1,1,1)"
    'rgb255',  # string "rgb(255,255,255)"
    'rgba1',  # string "rgba(1,1,1,1)"
    'rgba255',  # string "rgba(255,255,255,1)"
    'rgb_tuple1',  # tuple[int] tuple(1,1,1)
    'rgba_tuple255',  # tuple[int] tuple(255,255,255,1)
    'hex',
    'word'
}

# --- 1. FULL CSS4 COLOR MAP (Name -> Hex) ---
# This includes all named colors supported by Plotly/Browsers
NAMED_COLORS = {
    'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff', 'aquamarine': '#7fffd4',
    'azure': '#f0ffff', 'beige': '#f5f5dc', 'bisque': '#ffe4c4', 'black': '#000000',
    'blanchedalmond': '#ffebcd', 'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a',
    'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00', 'chocolate': '#d2691e',
    'coral': '#ff7f50', 'cornflowerblue': '#6495ed', 'cornsilk': '#fff8dc', 'crimson': '#dc143c',
    'cyan': '#00ffff', 'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9', 'darkgreen': '#006400', 'darkgrey': '#a9a9a9', 'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f', 'darkorange': '#ff8c00', 'darkorchid': '#9932cc',
    'darkred': '#8b0000', 'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1', 'darkviolet': '#9400d3',
    'deeppink': '#ff1493', 'deepskyblue': '#00bfff', 'dimgray': '#696969', 'dimgrey': '#696969',
    'dodgerblue': '#1e90ff', 'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22',
    'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff', 'gold': '#ffd700',
    'goldenrod': '#daa520', 'gray': '#808080', 'green': '#008000', 'greenyellow': '#adff2f',
    'grey': '#808080', 'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c',
    'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c', 'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00', 'lemonchiffon': '#fffacd', 'lightblue': '#add8e6',
    'lightcoral': '#f08080', 'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3',
    'lightgreen': '#90ee90', 'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1', 'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa', 'lightslategray': '#778899', 'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de', 'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32',
    'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000', 'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3', 'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee', 'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585', 'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080', 'oldlace': '#fdf5e6',
    'olive': '#808000', 'olivedrab': '#6b8e23', 'orange': '#ffa500', 'orangered': '#ff4500',
    'orchid': '#da70d6', 'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee',
    'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9', 'peru': '#cd853f',
    'pink': '#ffc0cb', 'plum': '#dda0dd', 'powderblue': '#b0e0e6', 'purple': '#800080',
    'red': '#ff0000', 'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513',
    'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57', 'seashell': '#fff5ee',
    'sienna': '#a0522d', 'silver': '#c0c0c0', 'skyblue': '#87ceeb', 'slateblue': '#6a5acd',
    'slategray': '#708090', 'slategrey': '#708090', 'snow': '#fffafa', 'springgreen': '#00ff7f',
    'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080', 'thistle': '#d8bfd8',
    'tomato': '#ff6347', 'turquoise': '#40e0d0', 'violet': '#ee82ee', 'wheat': '#f5deb3',
    'white': '#ffffff', 'whitesmoke': '#f5f5f5', 'yellow': '#ffff00', 'yellowgreen': '#9acd32',
    'transparent': '#00000000'  # Special case for transparency
}

PLOTTER_PREFERENCES = {
    # Matplotlib prefers tuples (0-1) or hex
    "matplotlib": ["rgba_tuple1", "rgb_tuple1", "hex"],
    # Plotly prefers CSS strings (0-255) or hex
    "plotly": ["rgba255_str", "rgb255_str", "hex"]
}


def convert_colors(color: ColorValue, lib: TargetLib) -> ColorValue:
    """
    Main entry point. Converts any color format to the library's preferred format.
    """
    # 1. Normalize input to Intermediate Representation (r, g, b, a) floats 0-1
    rgba_norm = normalize_color(color)

    # 2. Get the target format list for the library
    target = PLOTTER_PREFERENCES.get(lib)[0]

    return format_color(rgba_norm, target)


def normalize_color(color: ColorValue) -> tuple[float, float, float, float]:
    """
    Parses any input (hex, string, tuple, name) and returns a normalized
    (r, g, b, a) tuple where values are floats between 0.0 and 1.0.
    """
    try:
        # 1. Handle Strings
        if isinstance(color, str):
            color = color.lower().strip()

            # Hex
            if color.startswith('#'):
                return hex_to_rgba_norm(color)

            # Named Colors
            if color in NAMED_COLORS:
                return hex_to_rgba_norm(NAMED_COLORS[color])

            # CSS Strings (rgb/rgba)
            # Regex to capture numbers inside parenthesis
            match = re.search(r'rgba?\(([\d\s\.,%]+)\)', color)
            if match:
                parts = [float(x.strip()) for x in match.group(1).split(',')]
                # Detect scale based on string content
                is_255 = any(c > 1.0 for c in parts[:3]) or "255" in color

                r = parts[0] / 255.0 if is_255 else parts[0]
                g = parts[1] / 255.0 if is_255 else parts[1]
                b = parts[2] / 255.0 if is_255 else parts[2]
                a = parts[3] if len(parts) > 3 else 1.0
                return (r, g, b, a)

        # 2. Handle Tuples / Lists
        if isinstance(color, Sequence) and not isinstance(color, str):
            # Heuristic: If any value > 1.0, assume 0-255 scale.
            # Otherwise assume 0-1 scale.
            is_255 = any(c > 1.0 for c in color[:3])

            r = float(color[0])
            g = float(color[1])
            b = float(color[2])
            a = float(color[3]) if len(color) > 3 else 1.0

            if is_255:
                return (r / 255, g / 255, b / 255, a)
            return (r, g, b, a)
    except Exception as e:
        raise ValueError(f"Unsupported color format: {color}")


def format_color(rgba: Tuple[float, float, float, float], fmt: str) -> ColorValue:
    """
    Converts normalized (0-1) RGBA tuple to specific target string/tuple format.
    """
    r, g, b, a = rgba

    # Scale to 255 for integer formats
    r255, g255, b255 = round(r * 255), round(g * 255), round(b * 255)

    if fmt == "hex":
        # Ignore alpha for standard hex, or use {:02x} for alpha if needed
        return f"#{r255:02x}{g255:02x}{b255:02x}"

    elif fmt == "rgba255_str":
        return f"rgba({r255}, {g255}, {b255}, {a})"

    elif fmt == "rgb255_str":
        return f"rgb({r255}, {g255}, {b255})"

    elif fmt == "rgba1_str":
        return f"rgba({r:.2f}, {g:.2f}, {b:.2f}, {a:.2f})"

    elif fmt == "rgba_tuple1":
        return (r, g, b, a)

    elif fmt == "rgb_tuple1":
        return (r, g, b)

    return f"#{r255:02x}{g255:02x}{b255:02x}"  # Default to hex


def hex_to_rgba_norm(hex_str: str) -> Tuple[float, float, float, float]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)

    # Parse RGB
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0

    # Parse Alpha if exists (Hex8)
    a = 1.0
    if len(hex_str) == 8:
        a = int(hex_str[6:8], 16) / 255.0

    return (r, g, b, a)


def run_local():
    # 1. Matplotlib prefers tuples of floats (0-1)
    print(f"Matplotlib Input: 'rgb(0, 255, 0)'")
    print(f"Result: {convert_colors('rgb(0, 255, 0)', 'matplotlib')}")
    # Output: (0.0, 1.0, 0.0, 1.0) -> Standard Tuple

    print("-" * 20)

    # 2. Plotly prefers CSS Strings "rgb(...)" or "rgba(...)"
    print(f"Plotly Input: (0.5, 0.5, 0.5)")
    print(f"Result: {convert_colors((0.5, 0.5, 0.5), 'plotly')}")
    # Output: rgba(128, 128, 128, 1.0) -> String

    print("-" * 20)

    # 3. Handling Hex and Named Colors
    print(f"Plotly Input: 'red'")
    print(f"Result: {convert_colors('red', 'plotly')}")
    # Output: rgba(255, 0, 0, 1.0)


if __name__ == "__main__":
    run_local()
