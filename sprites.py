from PIL import Image
from shapely.geometry import Point


def get_corners_exceeding_terrain_area(image_center, terrain_area, width, height, px_per_map_unit):
    width_on_map = width / px_per_map_unit
    height_on_map = height / px_per_map_unit

    bottom_right_corner = Point(image_center.x + width_on_map / 2, image_center.y - height_on_map / 2)
    bottom_left_corner = Point(image_center.x - width_on_map / 2, image_center.y - height_on_map / 2)
    top_right_corner = Point(image_center.x + width_on_map / 2, image_center.y + height_on_map / 2)
    top_left_corner = Point(image_center.x - width_on_map / 2, image_center.y + height_on_map / 2)

    exceeding_corners = []
    if not terrain_area.contains(bottom_right_corner):
        exceeding_corners += [(width, height)]
    if not terrain_area.contains(bottom_left_corner):
        exceeding_corners += [(0, height)]
    if not terrain_area.contains(top_right_corner):
        exceeding_corners += [(width, 0)]
    if not terrain_area.contains(top_left_corner):
        exceeding_corners += [(0, 0)]

    return exceeding_corners


def distance(x1, y1, x2, y2, exp=2):
    return (abs(x1 - x2) ** exp + abs(y1 - y2) ** exp) ** (1 / exp)


def distance_to_center(w, h, width, height):
    return distance(w, h, width / 2, height / 2)


def alpha_channel(x, y, width, height, corners_to_avoid):
    base_alpha_ratio = 1 - (distance_to_center(x, y, width, height) / (width / 2)) ** 2
    distances_to_corners = [distance(x, y, x0, y0) for x0, y0 in corners_to_avoid]

    border_alpha_ratio = (min([width / 2, *distances_to_corners]) / (width / 2)) ** 5
    return int(max(0, 255 * min([base_alpha_ratio, border_alpha_ratio])))


def convert_image(file_name, position, polygon, px_per_map_unit):
    img = Image.open("sprites/" + file_name)
    img = img.convert("RGBA")
    datas = img.getdata()

    width, height = img.size

    corners_exceeding_area = get_corners_exceeding_terrain_area(position, polygon, width, height, px_per_map_unit)

    new_data = []
    for index, item in enumerate(datas):
        x = index % width
        y = index / height

        new_data.append(tuple(item[0:3] + (alpha_channel(x, y, width, height, corners_exceeding_area),)))

    img.putdata(new_data)
    img.save("processed_sprites/" + file_name, "PNG")
    return img
