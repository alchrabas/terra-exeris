import collections
from typing import Callable

from shapely import prepared
from shapely.geometry import Point

from src import helpers


def neighbours(center_x, center_y, candidate_accepted: Callable[[int, int], bool]):
    for a in (center_x - 1, center_x, center_x + 1):
        for b in (center_y - 1, center_y, center_y + 1):
            if candidate_accepted(a, b):
                yield (a, b)


def get_points_in_terrain(terrain_poly):
    prep_inter_in_image = prepared.prep(terrain_poly)
    from_x, from_y, to_x, to_y = [int(round(x)) for x in terrain_poly.bounds]
    points_in_terrain = set()
    for x in range(from_x, to_x + 1):
        for y in range(from_y, to_y + 1):
            if prep_inter_in_image.contains(Point(x, y)):
                points_in_terrain.add((x, y))
    return points_in_terrain


def get_closest_terrain_points_for_every_point(points_in_terrain, terrain_poly, width, height):
    closest_terrain_points = {point: point for point in points_in_terrain}
    queue = collections.deque()

    minx, miny, maxx, maxy = [a for a in terrain_poly.bounds]

    TERRAIN_BOUNDS_BUFFER = 30

    def accept_candidate(x, y):
        return minx - TERRAIN_BOUNDS_BUFFER <= x <= maxx + TERRAIN_BOUNDS_BUFFER and \
               miny - TERRAIN_BOUNDS_BUFFER <= y <= maxy + TERRAIN_BOUNDS_BUFFER and \
               0 <= x <= width and 0 <= y <= height

    for (x, y) in points_in_terrain:
        queue.extend(
            [neighbour for neighbour in neighbours(x, y, accept_candidate) if neighbour not in points_in_terrain])
    processed = set(points_in_terrain)
    while queue:
        (x, y) = queue.popleft()
        if (x, y) in processed:
            continue
        processed_neighbours = [neighbour_coords for neighbour_coords in neighbours(x, y, accept_candidate) if
                                neighbour_coords in processed]
        min_dist = 1000000000
        closest_neighbour = None
        for (neigh_x, neigh_y) in processed_neighbours:
            closest_point = closest_terrain_points[(neigh_x, neigh_y)]
            candidate_distance = helpers.distance(neigh_x, neigh_y, closest_point[0], closest_point[1])
            if candidate_distance < min_dist:
                min_dist = helpers.distance(neigh_x, neigh_y, closest_point[0], closest_point[1])
                closest_neighbour = closest_point
        processed.add((x, y))
        closest_terrain_points[(x, y)] = closest_neighbour
        queue.extend([neighbour for neighbour in neighbours(x, y, accept_candidate) if neighbour not in processed])

    distance_to_closest_point = {}
    for member_coords, closest_point in closest_terrain_points.items():
        distance_to_closest_point[member_coords] = helpers.distance(member_coords[0], member_coords[1],
                                                                    closest_point[0], closest_point[1])
    return distance_to_closest_point
