import pathlib

from PIL import Image

from src import helpers


def alpha_channel(x, y, width, height, dist_to_line, inside, threshold):
    base_alpha_ratio = 1 - helpers.relative_distance(x, y, width / 2, height / 2, width / 2, height / 2)

    if inside:
        border_alpha_ratio = 0
    elif dist_to_line > threshold:
        border_alpha_ratio = 1
    else:
        border_alpha_ratio = (dist_to_line / threshold)

    return int(max(0, 255 * min([base_alpha_ratio - border_alpha_ratio])))


def convert_image(file_name, center_point, angle, points_in_terrain, distance_to_closest_point, fadeout_threshold):
    img = Image.open("sprites/" + file_name)
    img = img.convert("RGBA")
    datas = img.getdata()

    width, height = img.size

    new_data = []
    for index, item in enumerate(datas):
        x = index % width
        y = index // width
        whole_x = x + center_point[0] - width / 2
        whole_y = y + center_point[1] - height / 2
        rot_x, rot_y = [int(round(a)) for a in helpers.rotate(center_point, (whole_x, whole_y), -angle)]

        inside_of_polygon = (rot_x, rot_y) in points_in_terrain  # inter_in_image.contains(Point(x, y))
        min_distance_to_line_string = 0
        if not inside_of_polygon:
            default_distance = 1000
            min_distance_to_line_string = distance_to_closest_point.get((rot_x, rot_y), default_distance)
            # min([line_string.distance(Point(x, y)) for line_string in line_strings])

        new_data.append(tuple(item[0:3] + (alpha_channel(x, y, width, height,
                                                         min_distance_to_line_string, inside_of_polygon,
                                                         fadeout_threshold),)))
    img.putdata(new_data)

    pathlib.Path("processed_sprites/" + file_name).parent.mkdir(parents=True, exist_ok=True)
    img.save("processed_sprites/" + file_name, "PNG")
    return img
