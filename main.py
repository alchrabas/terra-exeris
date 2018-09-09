import io
import math
import random
import time

from PIL import Image
from PIL import ImageDraw
from shapely import affinity
from shapely.geometry import Point, MultiPoint, LineString
from shapely.ops import linemerge, unary_union, polygonize

import helpers
import sprites
import terrain_examples
from helpers import points_located_on_center_line

PX_PER_MAP_UNIT = 50
TIME_CONSUMPTION = 1

COLORS = {
    "grassland": "green",
    "grassland_coast": "#4CBB17",
    "deep_water": "#1F75cE",
    "shallow_water": "#40a3cF",
    "road": "brown",
    "forest": "darkgreen",
    "mountains": "#aaaaaa",
}

size, all_terrains = terrain_examples.small_mountain_chain()

VIEW_SIZE = size * PX_PER_MAP_UNIT


def transpose(y):
    return VIEW_SIZE - y


def random_points_in_polygon(number, polygon):
    minx, miny, maxx, maxy = polygon.bounds
    return [pnt for pnt in [
        Point(random.uniform(minx, maxx), random.uniform(miny, maxy)) for _ in range(number)
    ] if polygon.contains(pnt)]


SPRITES = {
    "forest": [str(x) + ".png" for x in range(2, 7)],
    "grassland": [str(x) + ".png" for x in range(1, 7)],
    "deep_water": [str(x) + ".png" for x in range(1, 6)],
    "shallow_water": [str(x) + ".png" for x in range(1, 5)],
    "grassland_coast": [str(x) + ".png" for x in range(1, 2)],
    "mountains_side": [str(x) + ".png" for x in range(1, 7)],
    "mountains": [str(x) + ".png" for x in range(5, 9)],
    "river": [str(x) + ".png" for x in range(1, 4)],
}


def normal_procedure(t, im):
    uniformly_distributed_points = helpers.uniformly_distribute_points(8 / TIME_CONSUMPTION, t.poly)
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


def put_rotated_sprites_onto_image(im, is_right_side, points, terrain_type, poly, center_line=None,
                                   fadeout_threshold=40):
    for point in points:
        sprites_for_terrain = SPRITES.get(terrain_type, [])
        if sprites_for_terrain:
            if center_line:
                close_point = helpers.closest_point(point, LineString(center_line))
                angle = get_angle(LineString(center_line), close_point)
                dist = close_point.distance(point)
            else:
                angle = random.randint(0, 360)
                dist = 0
            try:
                r_poly = affinity.rotate(poly, math.degrees(-angle), origin=point)
                image_name = random.choice(sprites_for_terrain)
                sprite_image = sprites.convert_image(terrain_type + "/" + image_name, point,
                                                     r_poly, PX_PER_MAP_UNIT, fadeout_threshold)
                if is_right_side:
                    sprite_image = sprite_image.transpose(Image.FLIP_TOP_BOTTOM)
                sprite_image = sprite_image.rotate(math.degrees(angle), expand=1)
                sprite_image = helpers.image_with_affected_brigthness(dist, sprite_image)
                width, height = sprite_image.size
                temp_image_with_alpha = Image.new("RGBA", im.size, (0, 0, 0, 0))
                temp_image_with_alpha.paste(sprite_image, (
                    round(point.x * PX_PER_MAP_UNIT - width / 2),
                    round(transpose(point.y * PX_PER_MAP_UNIT) - height / 2)
                ))
                temp_image_with_alpha.putdata([x[:3] + (x[3] * 2,) for x in temp_image_with_alpha.getdata()])
                im.putdata(Image.alpha_composite(im, temp_image_with_alpha).getdata())

            except Exception as e:
                print("it failed", e)
                pass


def side_based_procedure(terrain, image):
    line = terrain.center_line.coords
    con = terrain.poly.boundary.coords
    mer = linemerge([con, line])
    uni = unary_union(mer)
    left_side, right_side = polygonize(uni)
    draw = ImageDraw.Draw(image)
    # draw.polygon(convert_to_map(v[0].boundary.coords), fill="#ff0000")
    # draw.polygon(convert_to_map(v[1].boundary.coords), fill="#00ff00")

    center_l = points_located_on_center_line(terrain.center_line, max(1, 1 / TIME_CONSUMPTION))

    left_points = helpers.uniformly_distribute_points(8 / TIME_CONSUMPTION, terrain.poly)
    left_points += random_points_in_polygon(int(3 * TIME_CONSUMPTION), left_side)
    right_points = helpers.uniformly_distribute_points(8 / TIME_CONSUMPTION, terrain.poly)
    right_points += random_points_in_polygon(int(3 * TIME_CONSUMPTION), right_side)

    put_rotated_sprites_onto_image(image, False, left_points, "mountains_side", left_side, center_l)
    put_rotated_sprites_onto_image(image, True, right_points, "mountains_side", right_side, center_l)

    if center_l:
        put_rotated_sprites_onto_image(image, False, center_l, "mountains", terrain.poly, center_l)


def draw_road(terrain, image):
    draw = ImageDraw.Draw(image)

    points = points_located_on_center_line(terrain.center_line, 0.35)
    points = convert_to_map([(point.x + random.uniform(-0.1, 0.1),
                              point.y + random.uniform(-0.1, 0.1)) for point in points])

    for x, y in points:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#93590d")
    draw.line(points, fill="#93590d", width=7)

    for x, y in points:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#856306")
    draw.line(points, fill="#856306", width=5)


def draw_river(terrain, image):
    pts_for_image = points_located_on_center_line(terrain.center_line, 1)

    put_rotated_sprites_onto_image(image, False, pts_for_image, "river", terrain.poly, fadeout_threshold=3)

    temp_image_with_alpha = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp_image_with_alpha)
    draw.line(convert_to_map(terrain.center_line.coords), fill="#000044", width=10)
    temp_image_with_alpha.putdata([x[:3] + (16 if x[3] > 128 else x[3],) for x in temp_image_with_alpha.getdata()])
    draw.line(convert_to_map(terrain.center_line.coords), fill="#000044", width=6)
    temp_image_with_alpha.putdata([x[:3] + (24 if x[3] > 16 else x[3],) for x in temp_image_with_alpha.getdata()])
    draw.line(convert_to_map(terrain.center_line.coords), fill="#000044", width=3)
    temp_image_with_alpha.putdata([x[:3] + (36 if x[3] > 24 else x[3],) for x in temp_image_with_alpha.getdata()])

    image.putdata(Image.alpha_composite(image, temp_image_with_alpha).getdata())


def convert_to_map(coords):
    return [(x * PX_PER_MAP_UNIT, transpose(y * PX_PER_MAP_UNIT)) for x, y in coords]


def get_map():
    im = Image.new("RGBA", (VIEW_SIZE, VIEW_SIZE), "white")

    draw = ImageDraw.Draw(im)
    for t in all_terrains:
        # coords = convert_to_map(t.poly.exterior.coords)

        # draw.polygon(coords, fill=COLORS[t.terrain_name])

        if t.terrain_name == "mountains":
            side_based_procedure(t, im)
        elif t.terrain_name == "road":
            draw_road(t, im)
        elif t.terrain_name == "river":
            draw_river(t, im)
        else:
            normal_procedure(t, im)

    print("CONTAINS: ", sprites.contains_time)
    print("DISTANCE: ", sprites.distance_time)
    print("hits")
    print(" inside:", sprites.inside_hits)
    print("outside:", sprites.outside_hits)
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
