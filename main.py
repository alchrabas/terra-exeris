import io
import math
import random
import time

from PIL import Image
from PIL import ImageDraw
from shapely import affinity
from shapely.geometry import Point, LineString, MultiPoint
from shapely.ops import linemerge, unary_union, polygonize

import sprites
import terrain_examples
from helpers import closest_point, image_with_affected_brigthness, points_located_on_center_line

PX_PER_MAP_UNIT = 50
TIME_CONSUMPTION = 10.0

COLORS = {
    "grassland": "green",
    "grassland_coast": "#4CBB17",
    "deep_water": "#1F75cE",
    "shallow_water": "#40a3cF",
    "road": "brown",
    "forest": "darkgreen",
    "mountains": "#aaaaaa",
}

size, all_terrains = terrain_examples.small_forest_island()

VIEW_SIZE = size * PX_PER_MAP_UNIT


def transpose(y):
    return VIEW_SIZE - y


def random_points_in_polygon(number, polygon):
    minx, miny, maxx, maxy = polygon.bounds
    return [pnt for pnt in [
        Point(random.uniform(minx, maxx), random.uniform(miny, maxy)) for _ in range(number)
    ] if polygon.contains(pnt)]


def uniformly_distribute_points(difference, poly):
    points = []
    minx, miny, maxx, maxy = poly.bounds
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            n = 0
            while n < 300:
                n += 1
                candidate_point = Point(x + random.uniform(- difference / 4, difference / 4),
                                        y + random.uniform(- difference / 4, difference / 4))
                if poly.contains(candidate_point):
                    points += [candidate_point]
                    if n > 1:
                        print("IN ", n, "th attempt")
                    break
            y += difference
        x += difference
    return points


SPRITES = {
    "forest": [str(x) + ".png" for x in range(2, 7)],
    "grassland": [str(x) + ".png" for x in range(1, 7)],
    "deep_water": [str(x) + ".png" for x in range(1, 6)],
    "shallow_water": [str(x) + ".png" for x in range(1, 5)],
    "grassland_coast": [str(x) + ".png" for x in range(1, 2)],
    "mountains_side": [str(x) + ".png" for x in range(1, 7)],
    "mountains": [str(x) + ".png" for x in range(5, 9)],
}


def normal_procedure(t, im):
    uniformly_distributed_points = uniformly_distribute_points(8 / TIME_CONSUMPTION, t.poly)
    put_rotated_sprites_onto_image(im, False, uniformly_distributed_points, t.terrain_name, t.poly)

    points = random_points_in_polygon(int(3 * TIME_CONSUMPTION), t.poly)  # make it specific to the area
    put_rotated_sprites_onto_image(im, False, points, t.terrain_name, t.poly)


def get_angle(line_string, point_on_line):
    two_points = point_on_line.buffer(0.001).exterior.intersection(line_string)

    if not isinstance(two_points, MultiPoint) or len(two_points) != 2:
        return 0
    pt1, pt2 = two_points

    dx = pt2.x - pt1.x
    dy = pt2.y - pt1.y

    return math.atan2(dy, dx)


def put_rotated_sprites_onto_image(im, is_right_side, points, terrain_type, poly, center_line=None):
    for point in points:
        sprites_for_terrain = SPRITES.get(terrain_type, [])
        if sprites_for_terrain:
            if center_line:
                close_point = closest_point(point, LineString(center_line))
                angle = get_angle(LineString(center_line), close_point)
                dist = close_point.distance(point)
            else:
                angle = random.randint(0, 360)
                dist = 0
            try:
                r_poly = affinity.rotate(poly, math.degrees(-angle), origin=point)
                image_name = random.choice(sprites_for_terrain)
                sprite_image = sprites.convert_image(terrain_type + "/" + image_name, point, r_poly, PX_PER_MAP_UNIT)
                if is_right_side:
                    sprite_image = sprite_image.transpose(Image.FLIP_TOP_BOTTOM)
                sprite_image = sprite_image.rotate(math.degrees(angle), expand=1)
                sprite_image = image_with_affected_brigthness(dist, sprite_image)
                width, height = sprite_image.size
                im.paste(sprite_image,
                         (
                             round(point.x * PX_PER_MAP_UNIT - width / 2),
                             round(transpose(point.y * PX_PER_MAP_UNIT) - height / 2)
                         ), sprite_image)
            except Exception as e:
                print("it failed", e)
                pass


def side_based_procedure(t, im):
    line = t.center_line.coords
    con = t.poly.boundary.coords
    mer = linemerge([con, line])
    uni = unary_union(mer)
    left_side, right_side = polygonize(uni)
    draw = ImageDraw.Draw(im)
    # draw.polygon(convert_to_map(v[0].boundary.coords), fill="#ff0000")
    # draw.polygon(convert_to_map(v[1].boundary.coords), fill="#00ff00")

    center_l = points_located_on_center_line(t.center_line, max(1, 1 / TIME_CONSUMPTION))

    left_points = uniformly_distribute_points(8 / TIME_CONSUMPTION, t.poly)
    left_points += random_points_in_polygon(int(3 * TIME_CONSUMPTION), left_side)
    right_points = uniformly_distribute_points(8 / TIME_CONSUMPTION, t.poly)
    right_points += random_points_in_polygon(int(3 * TIME_CONSUMPTION), right_side)

    put_rotated_sprites_onto_image(im, False, left_points, "mountains_side", left_side, center_l)
    put_rotated_sprites_onto_image(im, True, right_points, "mountains_side", right_side, center_l)

    if center_l:
        put_rotated_sprites_onto_image(im, False, center_l, "mountains", t.poly, center_l)


def convert_to_map(coords):
    return [(x * PX_PER_MAP_UNIT, transpose(y * PX_PER_MAP_UNIT)) for x, y in coords]


def get_map():
    im = Image.new("RGB", (VIEW_SIZE, VIEW_SIZE), "white")

    draw = ImageDraw.Draw(im)
    for t in all_terrains:
        coords = convert_to_map(t.poly.exterior.coords)

        # draw.polygon(coords, fill=COLORS[t.terrain_name])

        if t.terrain_name == "mountains":
            side_based_procedure(t, im)
        else:
            normal_procedure(t, im)

    print("CONTAINS: ", sprites.contains_time)
    print("DISTANCE: ", sprites.distance_time)
    # root_locs = models.RootLocation.query.all()

    # for rl in root_locs:
    #     p = rl.position.coords[0]
    #     low = (p[0] - 0.05) * MAP_PER_PX, transpose((p[1] + 0.05) * MAP_PER_PX)
    #     upp = (p[0] + 0.05) * MAP_PER_PX, transpose((p[1] - 0.05) * MAP_PER_PX)
    #
    #     draw.pieslice([low, upp], 0, 360, fill="black")

    # if character:
    #     p = character.get_position().coords[0]
    #     low = (p[0] - 0.05) * MAP_PER_PX, transpose((p[1] + 0.05) * MAP_PER_PX)
    #     upp = (p[0] + 0.05) * MAP_PER_PX, transpose((p[1] - 0.05) * MAP_PER_PX)
    #
    #     draw.pieslice([low, upp], 0, 360, fill="red")

    del draw

    b = io.BytesIO()
    im.save(b, 'png')
    return b.getvalue()


start = time.time()
map_bytes = get_map()
print("FULL TIME: ", time.time() - start)

with open('myfile.png', 'wb') as f:
    f.write(map_bytes)
