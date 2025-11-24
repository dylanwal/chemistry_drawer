from typing import Sequence

COLOR_TYPES = {
    'rgb',  # string "rgb(0,0,0)"
    'rgba',  # string "rgba(0,0,0,0)"
    'rgb_tuple',  # tuple[int] tuple(0,0,0)
    'rgba_tuple',  # tuple[int] tuple(0,0,0,0)
    'hex',
    'word'
}

COLOR_WORDS = {
    'aliceblue',
    'antiquewhite',
    'aqua',
    'aquamarine',
    'azure',
    'beige',
    'bisque',
    'black',
    'blanchedalmond',
    'blue',
    'blueviolet',
    'brown',
    'burlywood',
    'cadetblue',
    'chartreuse',
    'chocolate',
    'coral',
    'cornflowerblue',
    'cornsilk',
    'crimson',
    'cyan',
    'darkblue',
    'darkcyan',
    'darkgoldenrod',
    'darkgray',
    'darkgrey',
    'darkgreen',
    'darkkhaki',
    'darkmagenta',
    'darkolivegreen',
    'darkorange',
    'darkorchid',
    'darkred',
    'darksalmon',
    'darkseagreen',
    'darkslateblue',
    'darkslategray',
    'darkslategrey',
    'darkturquoise',
    'darkviolet',
    'deeppink',
    'deepskyblue',
    'dimgray',
    'dimgrey',
    'dodgerblue',
    'firebrick',
    'floralwhite',
    'forestgreen',
    'fuchsia',
    'gainsboro',
    'ghostwhite',
    'gold',
    'goldenrod',
    'gray',
    'grey',
    'green',
    'greenyellow',
    'honeydew',
    'hotpink',
    'indianred',
    'indigo',
    'ivory',
    'khaki',
    'lavender',
    'lavenderblush',
    'lawngreen',
    'lemonchiffon',
    'lightblue',
    'lightcoral',
    'lightcyan',
    'lightgoldenrodyellow',
    'lightgray',
    'lightgrey',
    'lightgreen',
    'lightpink',
    'lightsalmon',
    'lightseagreen',
    'lightskyblue',
    'lightslategray',
    'lightslategrey',
    'lightsteelblue',
    'lightyellow',
    'lime',
    'limegreen',
    'linen',
    'magenta',
    'maroon',
    'mediumaquamarine',
    'mediumblue',
    'mediumorchid',
    'mediumpurple',
    'mediumseagreen',
    'mediumslateblue',
    'mediumspringgreen',
    'mediumturquoise',
    'mediumvioletred',
    'midnightblue',
    'mintcream',
    'mistyrose',
    'moccasin',
    'navajowhite',
    'navy',
    'oldlace',
    'olive',
    'olivedrab',
    'orange',
    'orangered',
    'orchid',
    'palegoldenrod',
    'palegreen',
    'paleturquoise',
    'palevioletred',
    'papayawhip',
    'peachpuff',
    'peru',
    'pink',
    'plum',
    'powderblue',
    'purple',
    'red',
    'rosybrown',
    'royalblue',
    'saddlebrown',
    'salmon',
    'sandybrown',
    'seagreen',
    'seashell',
    'sienna',
    'silver',
    'skyblue',
    'slateblue',
    'slategray',
    'slategrey',
    'snow',
    'springgreen',
    'steelblue',
    'tan',
    'teal',
    'thistle',
    'tomato',
    'turquoise',
    'violet',
    'wheat',
    'white',
    'whitesmoke',
    'yellow',
    'yellowgreen',
}


def convert_colors(color: str | Sequence[int] | Sequence[float], lib: str) -> str:
    color_type, range_ = get_color_type(color)
    if lib == 'matplotlib':
        if 'tuple' in color_type and range_ == 1:
            return color

        # Otherwise, convert to a tuple with range 0-1
        target_type = 'rgba_tuple' if 'rgba' in color_type or len(color) == 4 else 'rgb_tuple'
        return convert_color(color, target_type, 1)

    if lib == 'plotly':
        p


def get_color_type(color: str | Sequence[int] | Sequence[float]) -> tuple[str, int]:
    """

    Parameters
    ----------
    color

    Returns
    -------
    color_type:
    range_:
        0: unknown
        1: zero-1
        2: zero-255

    """
    if isinstance(color, str):
        color = color.lower().strip()
        if color.startswith('rgba'):
            type_ = 'rgba'
            color = color.replace('rgba(', '').replace(')', '').split(",")
            values = (float(c) for c in color)
        elif color.startswith('rgb'):
            type_ = 'rgb'
            color = color.replace('rgba(', '').replace(')', '').split(",")
            values = (float(c) for c in color)
        elif color.startswith('#'):
            return 'hex', 0
        elif color in COLOR_WORDS:
            return 'word', 0
        else:
            raise ValueError("not a valid color type")

    elif isinstance(color, (list, tuple, np.ndarray)):
        length = len(color)
        type_ = 'rgba_tuple' if length == 4 else 'rgb_tuple'
        values = color

    else:
        raise ValueError("not a valid color type")

    if max(values) == 0:
        range_ = 0
    elif any(0 < v < 1 for v in values):
        range_ = 1
    else:
        range_ = 2

    return type_, range_


def convert_color(color: str | Sequence[int] | Sequence[float], color_type: str, range_: int) -> str:
    """
    Converts any supported color format to the target type and range.
    """
    current_type, current_range = get_color_type(color)

    r, g, b, a = 0.0, 0.0, 0.0, 1.0

    # --- STEP 1: EXTRACT VALUES & NORMALIZE TO 0-1 FLOATS ---

    if 'tuple' in current_type:
        # Unpack tuple
        vals = list(color)
        if len(vals) == 3:
            r, g, b = vals
        elif len(vals) == 4:
            r, g, b, a = vals

        # Normalize if currently 0-255
        if current_range == 2:
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            # Alpha in 255-tuples is rare, but if present, normalize it too
            if len(vals) == 4 and a > 1.0:
                a = a / 255.0

    elif 'rgb' in current_type:  # String formats
        # Parse "rgba(r, g, b, a)" or "rgb(r, g, b)"
        # Remove prefix and parentheses
        content = color.split('(')[1].split(')')[0]
        parts = [float(x.strip()) for x in content.split(',')]

        r = parts[0] / 255.0
        g = parts[1] / 255.0
        b = parts[2] / 255.0

        if len(parts) > 3:
            # CSS Alpha is usually 0-1 already, even in rgb(255,255,255, 0.5) strings
            a = parts[3]

    # --- STEP 2: CONVERT TO TARGET FORMAT ---

    # Scale values if target range is 255
    if target_range == 2:
        r_out, g_out, b_out = int(r * 255), int(g * 255), int(b * 255)
        a_out = a  # Alpha usually stays 0-1 in strings, but maybe 255 in tuples?
        # Let's keep alpha 0-1 for strings, and standard behavior for tuples
    else:
        r_out, g_out, b_out, a_out = r, g, b, a

    # Construct Output
    if target_type == 'rgb_tuple':
        return (r_out, g_out, b_out)

    elif target_type == 'rgba_tuple':
        return (r_out, g_out, b_out, a_out)

    elif target_type == 'rgb':
        return f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"

    elif target_type == 'rgba':
        return f"rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {a})"

    return color


def to_mpl_color(color_str: str):
    """
    Converts Plotly/CSS color strings (rgba/rgb) to Matplotlib tuples.
    """
    if not isinstance(color_str, str):
        return color_str

    color_str = color_str.lower().strip()

    # Handle rgba(r, g, b, a)
    if color_str.startswith('rgba'):
        # Remove 'rgba(' and ')' and split
        parts = color_str[5:-1].split(',')
        r = float(parts[0]) / 255.0
        g = float(parts[1]) / 255.0
        b = float(parts[2]) / 255.0
        a = float(parts[3])  # Alpha is usually already 0-1 in CSS
        return (r, g, b, a)

    # Handle rgb(r, g, b)
    elif color_str.startswith('rgb'):
        parts = color_str[4:-1].split(',')
        r = float(parts[0]) / 255.0
        g = float(parts[1]) / 255.0
        b = float(parts[2]) / 255.0
        return (r, g, b, 1.0)  # Default alpha to 1.0

    # Return original if it's hex or named color (e.g. 'red', '#FFF')
    return color_str
