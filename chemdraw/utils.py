
def shorten_line(x0: float, x1: float, y0: float, y1: float, short_percent: float) -> (float, float, float, float):
    if short_percent == 1 or short_percent < 0:
        return x0, x1, y0, y1

    if (x1 - x0) == 0:
        # vertical line
        length = y0 - y1
        cut_distance = (1 - short_percent) / 2 * length
        return x0, x1, y0 + cut_distance, y1 - cut_distance

    if (y1 - y0) == 0:
        # horizontal line
        length = x0 - x1
        cut_distance = (1 - short_percent) / 2 * length
        return x0 - cut_distance, x1 + cut_distance, y0, y1

    # line with slope
    slope = (y1 - y0) / (x1 - x0)
    intercept = y0 - slope * x0
    length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    cut_distance = (1 - short_percent) / 2 * length

    # quadratic formula
    a = 1 + slope ** 2
    b = 2 * intercept * slope - 2 * y0 * slope - 2 * x0
    c = x0 ** 2 + intercept ** 2 - 2 * y0 * intercept + y0 ** 2 - cut_distance ** 2
    x0_new = (-b + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    if short_percent < 1:
        if not (x0 < x0_new < x1):
            # use second solution to quadratic formula
            x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    else:  # if short_percent > 1
        if x0 < x0_new < x1:
            # use second solution to quadratic formula
            x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)

    y0_new = slope * x0_new + intercept
    x1_new = x1 - (x0_new - x0)
    y1_new = slope * x1_new + intercept

    return x0_new, x1_new, y0_new, y1_new
