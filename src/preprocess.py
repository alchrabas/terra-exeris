import collections

from shapely.geometry import Point

from src import helpers


def neighbours(center_x, center_y, width, height):
    for a in (center_x - 1, center_x, center_x + 1):
        for b in (center_y - 1, center_y, center_y + 1):
            if 0 <= a < width and 0 <= b < height:
                yield (a, b)


def get_points_in_terrain(inter_in_image, width, height):
    points_in_terrain = set()
    for x in range(0, width):
        for y in range(0, height):
            if inter_in_image.contains(Point(x, y)):
                points_in_terrain.add((x, y))
    return points_in_terrain


def get_closest_terrain_points_for_every_point(points_in_terrain, width, height):
    closest_terrain_points = {point: (point, 0) for point in points_in_terrain}
    queue = collections.deque()
    for (x, y) in points_in_terrain:
        queue.extend([neighbour for neighbour in neighbours(x, y, width, height) if neighbour not in points_in_terrain])
    processed = set(points_in_terrain)
    while queue:
        (x, y) = queue.popleft()
        if (x, y) in processed:
            continue
        processed_neighbours = [neighbour_coords for neighbour_coords in neighbours(x, y, width, height) if
                                neighbour_coords in processed]
        min_dist = 1000000000
        closest_neighbour = None
        for (neigh_x, neigh_y) in processed_neighbours:
            closest_point, dist_to_its_closest = closest_terrain_points[(neigh_x, neigh_y)]
            candidate_distance = helpers.distance(neigh_x, neigh_y, closest_point[0], closest_point[1])
            if candidate_distance < min_dist:
                min_dist = helpers.distance(neigh_x, neigh_y, closest_point[0], closest_point[1])
                closest_neighbour = closest_point
        processed.add((x, y))
        closest_terrain_points[(x, y)] = (closest_neighbour,
                                          helpers.distance(x, y, closest_neighbour[0], closest_neighbour[1]))
        queue.extend([neighbour for neighbour in neighbours(x, y, width, height) if neighbour not in processed])
    return closest_terrain_points
