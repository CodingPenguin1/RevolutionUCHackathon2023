import math
import numpy as np
import itertools


def distance(point_1=(0, 0), point_2=(0, 0)):
    return math.sqrt(
        (point_1[0] - point_2[0]) ** 2 +
        (point_1[1] - point_2[1]) ** 2)


def on_segment(p1, p2, p):
    return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])


def direction(a, b, c):
    return np.cross((a - b), (c - b))


def line_segments_intersect(line_1, line_2):
    # https://algorithmtutor.com/Computational-Geometry/Check-if-two-line-segment-intersect/
    p1 = np.array((line_1[0], line_1[1]))
    p2 = np.array((line_1[2], line_1[3]))
    p3 = np.array((line_2[0], line_2[1]))
    p4 = np.array((line_2[2], line_2[3]))
    
    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
        ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    elif d1 == 0 and on_segment(p3, p4, p1):
        return True
    elif d2 == 0 and on_segment(p3, p4, p2):
        return True
    elif d3 == 0 and on_segment(p1, p2, p3):
        return True
    elif d4 == 0 and on_segment(p1, p2, p4):
        return True
    else:
        return False


def rects_overlap(rect1, rect2):
    # Rects defined as a list of (x, y) vertex tuples
    
    # Create list of line segments for each rect
    rect1_lines = [
        (rect1[0][0], rect1[0][1], rect1[1][0], rect1[1][1]),
        (rect1[1][0], rect1[1][1], rect1[2][0], rect1[2][1]),
        (rect1[2][0], rect1[2][1], rect1[3][0], rect1[3][1]),
        (rect1[3][0], rect1[3][1], rect1[0][0], rect1[0][1])
    ]
    rect2_lines = [
        (rect2[0][0], rect2[0][1], rect2[1][0], rect2[1][1]),
        (rect2[1][0], rect2[1][1], rect2[2][0], rect2[2][1]),
        (rect2[2][0], rect2[2][1], rect2[3][0], rect2[3][1]),
        (rect2[3][0], rect2[3][1], rect2[0][0], rect2[0][1])
    ]
    
    # Check if any line segment in rect 1 intersects any line segment in rect 2
    for line1 in rect1_lines:
        for line2 in rect2_lines:
            if line_segments_intersect(line1, line2):
                return True
    return False


def define_rect(center_x, center_y, width, height, angle):
    # Takes in sprite bounding box info and returns a list of rotated rectangle verticies
    angle = -math.radians(angle)
    width = int(0.5 * width)
    height = int(0.5 * height)
    
    verticies = []
    x1 = center_x + ((width / 2) * math.cos(angle)) - ((height / 2) * math.sin(angle))
    y1 = center_y + ((width / 2) * math.sin(angle)) + ((height / 2) * math.cos(angle))
    verticies.append((x1, y1))

    x2 = center_x - ((width / 2) * math.cos(angle)) - ((height / 2) * math.sin(angle))
    y2 = center_y - ((width / 2) * math.sin(angle)) + ((height / 2) * math.cos(angle))
    verticies.append((x2, y2))

    x3 = center_x - ((width / 2) * math.cos(angle)) + ((height / 2) * math.sin(angle))
    y3 = center_y - ((width / 2) * math.sin(angle)) - ((height / 2) * math.cos(angle))
    verticies.append((x3, y3))

    x4 = center_x + ((width / 2) * math.cos(angle)) + ((height / 2) * math.sin(angle))
    y4 = center_y + ((width / 2) * math.sin(angle)) - ((height / 2) * math.cos(angle))
    verticies.append((x4, y4))
    
    return verticies
