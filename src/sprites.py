import pathlib
import time

from PIL import Image
from shapely import prepared
from shapely.geometry import Polygon

from src import helpers, preprocess


def get_map_on_image(image_center, width, height, px_per_map_unit):
    return Polygon([
        (image_center.x + width / 2 / px_per_map_unit, image_center.y - height / 2 / px_per_map_unit),
        (image_center.x + width / 2 / px_per_map_unit, image_center.y + height / 2 / px_per_map_unit),
        (image_center.x - width / 2 / px_per_map_unit, image_center.y + height / 2 / px_per_map_unit),
        (image_center.x - width / 2 / px_per_map_unit, image_center.y - height / 2 / px_per_map_unit),
    ])


def alpha_channel(x, y, width, height, dist_to_line, inside, threshold):
    base_alpha_ratio = 1 - helpers.relative_distance(x, y, width / 2, height / 2, width / 2, height / 2)

    if inside:
        border_alpha_ratio = 0
    elif dist_to_line > threshold:
        border_alpha_ratio = 1
    else:
        border_alpha_ratio = (dist_to_line / threshold)

    return int(max(0, 255 * min([base_alpha_ratio - border_alpha_ratio])))


preprocess_time = 0.0
distance_time = 0.0
contains_time = 0.0
inside_hits = 0
outside_hits = 0


def convert_image(file_name, image_center, polygon, px_per_map_unit, fadeout_threshold):
    global preprocess_time
    global distance_time
    global contains_time
    global inside_hits
    global outside_hits

    img = Image.open("sprites/" + file_name)
    img = img.convert("RGBA")
    datas = img.getdata()

    width, height = img.size

    map_on_image = get_map_on_image(image_center, width, height, px_per_map_unit)

    intersection = polygon.intersection(map_on_image)

    poly_points_on_map = [((x - (image_center.x - width / 2 / px_per_map_unit)) * px_per_map_unit,
                           (-y + (image_center.y + height / 2 / px_per_map_unit)) * px_per_map_unit)
                          for x, y in intersection.exterior.coords]
    poly_points_on_map.append(poly_points_on_map[0])
    inter_in_image = prepared.prep(Polygon(poly_points_on_map))

    start = time.time()
    points_in_terrain = preprocess.get_points_in_terrain(inter_in_image, width, height)
    closest_terrain_points = preprocess.get_closest_terrain_points_for_every_point(points_in_terrain, width, height)
    preprocess_time += time.time() - start

    new_data = []
    for index, item in enumerate(datas):
        x = index % width
        y = index // width

        start = time.time()

        inside_of_polygon = (x, y) in points_in_terrain  # inter_in_image.contains(Point(x, y))
        between = time.time()
        contains_time += between - start

        min_distance_to_line_string = 0
        if not inside_of_polygon:
            outside_hits += 1
            min_distance_to_line_string = closest_terrain_points[(x, y)][
                1]  # min([line_string.distance(Point(x, y)) for line_string in line_strings])
        else:
            inside_hits += 1

        distance_time += time.time() - start

        new_data.append(tuple(item[0:3] + (alpha_channel(x, y, width, height,
                                                         min_distance_to_line_string, inside_of_polygon,
                                                         fadeout_threshold),)))

    img.putdata(new_data)

    pathlib.Path("processed_sprites/" + file_name).parent.mkdir(parents=True, exist_ok=True)
    img.save("processed_sprites/" + file_name, "PNG")
    return img
