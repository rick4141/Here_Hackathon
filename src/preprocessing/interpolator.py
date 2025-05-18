import numpy as np
from shapely.geometry import LineString, Point

def interpolate_point_on_line(line: LineString, num, min_num, max_num):
    """
    Interpolates a point on the line using the number 'num' in the range [min_num, max_num]
    """
    if np.isnan(num) or np.isnan(min_num) or np.isnan(max_num) or min_num == max_num:
        return None
    frac = (num - min_num) / (max_num - min_num)
    frac = max(0, min(frac, 1))  # Clamp to [0,1]
    return line.interpolate(frac, normalized=True)
