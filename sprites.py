import time

import pathlib
from PIL import Image
from shapely import prepared
from shapely.geometry import Point, LineString, Polygon


def get_map_on_image(image_center, width, height, px_per_map_unit):
    return Polygon([
        (image_center.x + width / 2 / px_per_map_unit, image_center.y - height / 2 / px_per_map_unit),
        (image_center.x + width / 2 / px_per_map_unit, image_center.y + height / 2 / px_per_map_unit),
        (image_center.x - width / 2 / px_per_map_unit, image_center.y + height / 2 / px_per_map_unit),
        (image_center.x - width / 2 / px_per_map_unit, image_center.y - height / 2 / px_per_map_unit),
    ])


def distance_to_center(w, h, width, height):
    return distance(w, h, width / 2, height / 2)


def distance(x1, y1, x2, y2, exp=2):
    return (abs(x1 - x2) ** exp + abs(y1 - y2) ** exp) ** (1 / exp)


def relative_distance(x1, y1, x2, y2, width, height, exp=2):
    rel = ((abs(x1 - x2) / width) ** exp + (abs(y1 - y2) / height) ** exp)
    return min([1, max([0, rel])])


def alpha_channel(x, y, width, height, dist_to_line, inside):
    base_alpha_ratio = 1 - relative_distance(x, y, width / 2, height / 2, width / 2, height / 2)

    if inside:
        border_alpha_ratio = 0
    elif dist_to_line > 40:
        border_alpha_ratio = 1
    else:
        border_alpha_ratio = (dist_to_line / 40)

    return int(max(0, 255 * min([base_alpha_ratio - border_alpha_ratio])))


distance_time = 0.0
contains_time = 0.0


def convert_image(file_name, image_center, polygon, px_per_map_unit):
    global distance_time
    global contains_time
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

    line_strings = []
    for i in range(len(poly_points_on_map) - 1):
        if poly_points_on_map[i] == poly_points_on_map[i + 1]:
            continue
        line_strings += [LineString([poly_points_on_map[i], poly_points_on_map[i + 1]])]
    inter_in_image = prepared.prep(Polygon(poly_points_on_map))

    new_data = []
    for index, item in enumerate(datas):
        x = index % width
        y = index // width

        start = time.time()

        inside_of_polygon = inter_in_image.contains(Point(x, y))
        between = time.time()
        contains_time += between - start

        min_distance_to_line_string = 0
        if not inside_of_polygon:
            min_distance_to_line_string = min([line_string.distance(Point(x, y)) for line_string in line_strings])

        distance_time += time.time() - start

        new_data.append(tuple(item[0:3] + (alpha_channel(x, y, width, height,
                                                         min_distance_to_line_string, inside_of_polygon),)))

    img.putdata(new_data)

    pathlib.Path("processed_sprites/" + file_name).parent.mkdir(parents=True, exist_ok=True)
    img.save("processed_sprites/" + file_name, "PNG")
    return img
