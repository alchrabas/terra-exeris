from PIL import ImageEnhance
from shapely.geometry import Point


def closest_point(point, line_string_coords):
    distance_from_start_to_closest_point = line_string_coords.project(point)
    p = line_string_coords.interpolate(distance_from_start_to_closest_point)
    closest_point_coords = list(p.coords)[0]
    return Point(closest_point_coords)


def image_with_affected_brigthness(dist, sprite_image):
    enh = ImageEnhance.Brightness(sprite_image)
    return enh.enhance(1.15 - min(0.15, dist / 6))


def points_located_on_center_line(center_line, diff):
    if not center_line:
        return []
    distance_from_start = 0.01
    points = []
    line_length = center_line.length
    while distance_from_start < line_length:
        points += [center_line.interpolate(distance_from_start)]
        distance_from_start += diff
    return points