import io
import random

from PIL import Image
from PIL import ImageDraw
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import linemerge, unary_union, polygonize

import sprites

PX_PER_MAP_UNIT = 50

VIEW_SIZE = 500

COLORS = {
    "grassland": "green",
    "grassland_coast": "#4CBB17",
    "deep_water": "#1F75cE",
    "shallow_water": "#40a3cF",
    "road": "brown",
    "forest": "darkgreen",
    "mountains": "#aaaaaa",
}


class Terrain:
    def __init__(self, poly, terrain_name, priority=1, center_line=None):
        self.poly = poly
        self.terrain_name = terrain_name
        self.priority = priority
        self.center_line = center_line


poly_grass = Polygon([(0.8, 0.8), (0.8, 2), (1, 2), (3, 0.8)])
poly_grass_coast = Polygon([(0.3, 0.3), (0.3, 2), (0.8, 2), (0.8, 0.8), (3, 0.8), (3, 0.3)])
poly_water = Polygon([(0, 0), (0, 10), (10, 10), (10, 0)])
poly_grass2 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
poly_road = Polygon([(1, 1), (0.9, 1.1), (3.9, 4.1), (4, 4), (1, 1)])
poly_forest = Polygon([(5, 2), (7, 3), (8, 5), (7, 7), (5, 8), (3, 7), (2, 5), (3, 3)])

poly_mountains = Polygon([(1, 2), (2, 1), (3, 2), (6, 1.5), (8, 4), (6.5, 5), (3, 6), (1.5, 5)])
center_line_mountains = LineString([(1, 2), (3, 4), (8, 4)])

poly_all_terrains = poly_grass.union(poly_forest).union(poly_grass_coast).union(poly_grass2)
poly_shallow_water = poly_all_terrains.buffer(0.5, resolution=2).difference(poly_all_terrains)
poly_water_except_land = poly_water.difference(poly_all_terrains.union(poly_shallow_water))

grass = Terrain(poly_grass, "grassland")
grass_coast = Terrain(poly_grass_coast, "grassland_coast")
shallow_water = Terrain(poly_shallow_water, "shallow_water", priority=0)
deep_water = Terrain(poly_water_except_land, "deep_water", priority=0)
grass2 = Terrain(poly_grass2, "grassland")
road = Terrain(poly_road, "road", priority=3)
forest = Terrain(poly_forest, "forest", priority=2)
mountains = Terrain(poly_mountains, "mountains", 1, center_line_mountains)

# all_terrains = [shallow_water, deep_water, grass_coast, grass, grass2, forest]  # , road]
all_terrains = [mountains]


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
            candidate_point = Point(x + random.uniform(- difference / 4, difference / 4),
                                    y + random.uniform(- difference / 4, difference / 4))
            if poly.contains(candidate_point):
                points += [candidate_point]
            y += difference
        x += difference
    return points


SPRITES = {
    "forest": [str(x) + ".png" for x in range(2, 7)],
    "grassland": [str(x) + ".png" for x in range(1, 7)],
    "deep_water": [str(x) + ".png" for x in range(1, 6)],
    "shallow_water": [str(x) + ".png" for x in range(1, 5)],
    "grassland_coast": [str(x) + ".png" for x in range(1, 2)],
    "left_mountains": [str(x) + ".png" for x in range(1, 7)],
    "mountains": [str(x) + ".png" for x in range(1, 5)],
}


def put_sprites_onto_image(im, points, terrain_type, poly):
    for point in points:
        sprites_for_terrain = SPRITES.get(terrain_type, [])
        if sprites_for_terrain:
            image_name = random.choice(sprites_for_terrain)
            try:
                sprite_image = sprites.convert_image(terrain_type + "/" + image_name, point, poly, PX_PER_MAP_UNIT)
                width, height = sprite_image.size
                im.paste(sprite_image,
                         (
                             round(point.x * PX_PER_MAP_UNIT - width / 2),
                             round(transpose(point.y * PX_PER_MAP_UNIT) - height / 2)
                         ), sprite_image)
            except Exception as e:
                print("it failed", e)
                pass


def normal_procedure(t, im):
    uniformly_distributed_points = uniformly_distribute_points(8, t.poly)
    put_sprites_onto_image(im, uniformly_distributed_points, t.terrain_name, t.poly)

    points = random_points_in_polygon(1, t.poly)  # make it specific to the area
    put_sprites_onto_image(im, points, t.terrain_name, t.poly)


def put_rotated_sprites_onto_image(im, is_right_side, points, terrain_type, poly):
    for point in points:
        sprites_for_terrain = SPRITES.get(terrain_type, [])
        if sprites_for_terrain:
            image_name = random.choice(sprites_for_terrain)
            try:
                sprite_image = sprites.convert_image(terrain_type + "/" + image_name, point, poly, PX_PER_MAP_UNIT)
                if is_right_side:
                    sprite_image = sprite_image.transpose(Image.FLIP_TOP_BOTTOM)
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
    v = list(polygonize(uni))
    draw = ImageDraw.Draw(im)
    draw.polygon(convert_to_map(v[0].boundary.coords), fill="#ff0000")
    draw.polygon(convert_to_map(v[1].boundary.coords), fill="#00ff00")

    left_points = uniformly_distribute_points(0.8, t.poly)
    left_points += random_points_in_polygon(50, v[0])
    right_points = uniformly_distribute_points(0.8, t.poly)
    right_points += random_points_in_polygon(50, v[1])

    put_rotated_sprites_onto_image(im, False, left_points, "left_mountains", v[0])
    put_rotated_sprites_onto_image(im, True, right_points, "left_mountains", v[1])

    center_l = [Point(1, 2), Point(2, 3), Point(3, 4), Point(4, 4), Point(5, 4), Point(6, 4), Point(7, 4), Point(8, 4)]
    put_sprites_onto_image(im, center_l, "mountains", t.poly)


def convert_to_map(coords):
    return [(x * PX_PER_MAP_UNIT, transpose(y * PX_PER_MAP_UNIT)) for x, y in coords]


def get_map():
    im = Image.new("RGB", (VIEW_SIZE, VIEW_SIZE), "white")

    draw = ImageDraw.Draw(im)
    for t in all_terrains:
        coords = convert_to_map(t.poly.exterior.coords)

        draw.polygon(coords, fill=COLORS[t.terrain_name])

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


# sprites.process_all_images("sprites")

map_bytes = get_map()

with open('myfile.png', 'wb') as f:
    f.write(map_bytes)
