import itertools
import argparse
import math
import random
from typing import List

import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point as ShapPoint

from classes import Point, Edge

EPS = np.finfo(float).eps

#####################################################
############  Miscellaneous  #######################


def str2bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def generate_all_cycles(n, lengths):
    for l in lengths:
        assert l in [3, 4]
    res = []

    for l in lengths:
        for vertices in itertools.combinations(range(n), l):
            if l == 3:
                res.append(vertices)
            else:
                res.append(vertices)
                res.append((vertices[0], vertices[1], vertices[3], vertices[2]))
                res.append((vertices[0], vertices[3], vertices[1], vertices[2]))

    return res


############  Miscellaneous end  ####################
#####################################################


#####################################################
############  intersection stuff  ###################


def is_collinear(p1, p2, p3) -> bool:
    """checks if 3 points are collinear"""
    if abs((p3.y - p2.y) * (p2.x - p1.x) - (p2.y - p1.y) * (p3.x - p2.x)) < 4*EPS:
        return True
    else:
        return False


def in_general_position(points) -> bool:
    for p1, p2, p3 in list(itertools.combinations(points, 3)):
        if is_collinear(p1, p2, p3):
            return False
    return True


# edge intersection method inspired by
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/


def orientation(p, q, r) -> int:
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2


def do_intersect(e1, e2) -> bool:
    """
    Determine if two edges intersect.
    Note that we assume that the endpoints of the edges are in general position.
    """

    p1 = e1.p
    q1 = e1.q
    p2 = e2.p
    q2 = e2.q

    if p1.id == p2.id or p1.id == q2.id or q1.id == p2.id or q1.id == q2.id:
        return False

    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0 and o1 != o2 and o3 != o4:
        return True

    # remaining cases cannot happen because of general position

    return False  # Doesn't fall in any of the above cases


def generate_all_edges(points) -> List[Edge]:
    edges = []
    for p, q in itertools.combinations(points, 2):
        edges.append(Edge(id=len(edges), p=p, q=q))
    return edges


def set_crossings(edges):
    for e1, e2 in itertools.combinations(edges, 2):
        if do_intersect(e1, e2):
            e1.num_intersections += 1
            e2.num_intersections += 1
            e1.crossed_edges.append(e2)
            e2.crossed_edges.append(e1)


def remove_uncrossed_edges(edges):
    new_edges = []

    for e in edges:
        if len(e.crossed_edges) == 0:
            continue
        e.id = len(new_edges)
        new_edges.append(e)

    return new_edges


############  intersection stuff end  ###############
#####################################################


####################################################
############  prepare input  #######################


def get_input(args):

    assert args.pset in [
        "bw",
        "gw",
        "convex",
        "random",
        "random_wheel",
        "two_convex_layers",
    ]

    if args.pset == "bw":
        assert args.k > 0 and args.l > 0
        points, edges = bumpy_wheel(args.k, args.l)
        print(f"Using the bumpy wheel (k={args.k},l={args.l})")
        return points, edges

    if args.pset == "gw":
        assert len(args.group_sizes) > 0
        points, edges = generalized_wheel(args.group_sizes)
        print(f"Using the generalized wheel (sizes={args.group_sizes})")
        return points, edges

    if args.pset == "convex":
        assert args.n > 0
        points, edges = convex_position(args.n)
        print(f"Using convex position with {args.n} points")
        return points, edges

    if args.pset == "random":
        assert args.n > 0
        points, edges = random_position(args.n)
        print(f"Using random position with {args.n} points")
        return points, edges

    if args.pset == "random_wheel":
        assert args.n > 0
        points, edges = random_wheel(args.n)
        print(f"Using random wheel (n={args.n})")
        return points, edges

    if args.pset == "two_convex_layers":
        assert args.n > 0
        points, edges = two_convex_layers(args.n)
        print(f"Using two convex layers (n={args.n})")
        return points, edges


def prepare_all_edges(points, remove_uncrossed=False) -> List[Edge]:
    """
    Prepare list of edge object.
    For each edge compute its crossings.
    Optionally remove edges that are uncrossed to optimize memory.
    """
    edges = generate_all_edges(points)
    set_crossings(edges)
    if remove_uncrossed:
        print("removing uncrossed edges")
        edges = remove_uncrossed_edges(edges)

    return edges


# rotated bumpy wheel to conform with rotation in the paper
def bumpy_wheel(k, l):
    eps = 0.1
    points = [Point(id=0, x=0, y=0)]
    for i in range(k):
        for j in range(l):
            x = math.cos(2 * math.pi / k * i + j * eps - math.pi / 2.55)
            y = math.sin(2 * math.pi / k * i + j * eps - math.pi / 2.55)
            points.append(Point(id=len(points), x=x, y=y))

    edges = prepare_all_edges(points)

    return points, edges


def generalized_wheel(sizes):
    eps = 0.1
    points = [Point(id=0, x=0, y=0)]
    k = len(sizes)
    for i in range(k):
        l = sizes[i]
        for j in range(l):
            x = math.cos(2 * math.pi / k * i + j * eps)
            y = math.sin(2 * math.pi / k * i + j * eps)
            points.append(Point(id=len(points), x=x, y=y))

    edges = prepare_all_edges(points)

    return points, edges


def convex_position(n):
    points = [Point(id=i, x=math.cos(2 * math.pi / n * i), y=math.sin(2 * math.pi / n * i)) for i in range(n)]
    edges = prepare_all_edges(points)
    return points, edges


def random_position(n, size=None):
    if size is None:
        size = 10 * n

    points = []
    while len(points) == 0 or not in_general_position(points):
        points = []
        for i in range(n):
            x = random.randint(0, size)
            y = random.randint(0, size)
            points.append(Point(id=i, x=x, y=y))

    edges = prepare_all_edges(points)
    return points, edges


def random_wheel(n):
    n_outer = n - 1
    points = []
    while len(points) == 0 or not in_general_position(points):
        points = []
        for i in range(n_outer):
            alpha = random.uniform(0.0, 2 * math.pi)
            points.append(Point(id=i, x=math.cos(alpha), y=math.sin(alpha)))

        mypoly = Polygon([(p.x, p.y) for p in points])
        x, y = get_random_point_in_polygon(mypoly)
        points.append(Point(id=n_outer, x=x, y=y))

    edges = prepare_all_edges(points)
    return points, edges


def get_random_point_in_polygon(poly) -> tuple[float, float]:
    """
    Get a random point inside a polygon by sampling from the bounding box
    until we get a point inside the polygon.
    """
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = ShapPoint(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return (p.x, p.y)


def two_convex_layers(n):
    points = []
    while len(points) == 0 or not in_general_position(points):
        points = []
        for i in range(n // 2):
            alpha = random.uniform(0.0, 2 * math.pi)
            points.append(Point(id=i, x=math.cos(alpha), y=math.sin(alpha)))

        for i in range(n // 2):
            alpha = random.uniform(0.0, 2 * math.pi)
            points.append(Point(id=i + n // 2, x=4 * math.cos(alpha), y=4 * math.sin(alpha)))

    edges = prepare_all_edges(points)
    return points, edges


############  prepare input end ####################
####################################################
