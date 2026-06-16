import math

def calculate_angle(a, b, c):
    """
    Calculates the angle at point b using 3 points:
    a = first point
    b = middle point
    c = third point
    """

    ax, ay = a
    bx, by = b
    cx, cy = c

    angle = math.degrees(
        math.atan2(cy - by, cx - bx) -
        math.atan2(ay - by, ax - bx)
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle

def calculate_spine_angle(shoulder_midpoint, hip_midpoint):
    """
    Calculates how much the spine leans away from vertical.
    0 degrees = straight up and down
    Larger angle = more forward/backward tilt
    """

    sx, sy = shoulder_midpoint
    hx, hy = hip_midpoint

    dx = sx - hx
    dy = sy - hy

    angle = math.degrees(math.atan2(abs(dx), abs(dy)))

    return angle

def calculate_line_tilt(point_a, point_b):
    """
    Calculates the tilt of a line segment relative to horizontal.
    0 degrees = perfectly horizontal
    90 degrees = perfectly vertical
    """

    ax, ay = point_a
    bx, by = point_b

    dx = bx - ax
    dy = by - ay

    angle = abs(math.degrees(math.atan2(dy, dx)))

    if angle > 90:
        angle = 180 - angle

    return angle