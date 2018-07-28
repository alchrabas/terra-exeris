import io
import random

from PIL import Image
from PIL import ImageDraw
from shapely.geometry import Polygon, Point

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
}


class Terrain:
    def __init__(self, poly, terrain_name, priority=1):
        self.poly = poly
        self.terrain_name = terrain_name
        self.priority = priority


poly_grass = Polygon([(0.8, 0.8), (0.8, 2), (1, 2), (3, 0.8)])
poly_grass_coast = Polygon([(0.3, 0.3), (0.3, 2), (0.8, 2), (0.8, 0.8), (3, 0.8), (3, 0.3)])
poly_water = Polygon([(0, 0), (0, 10), (10, 10), (10, 0)])
poly_grass2 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
poly_road = Polygon([(1, 1), (0.9, 1.1), (3.9, 4.1), (4, 4), (1, 1)])
poly_forest = Polygon([(5, 2), (7, 3), (8, 5), (7, 7), (5, 8), (3, 7), (2, 5), (3, 3)])

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

all_terrains = [shallow_water, deep_water, grass_coast, grass, grass2, forest]  # , road]


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
}


def put_sprites_onto_image(im, points, terrain_type, poly):
    for point in points:
        sprites_for_terrain = SPRITES.get(terrain_type, [])
        if sprites_for_terrain:
            image_name = random.choice(sprites_for_terrain)
            sprite_image = sprites.convert_image(terrain_type + "/" + image_name, point, poly, PX_PER_MAP_UNIT)
            print(image_name)
            # sprite_image.thumbnail((80, 80), Image.ANTIALIAS)
            width, height = sprite_image.size
            im.paste(sprite_image,
                     (
                         round(point.x * PX_PER_MAP_UNIT - width / 2),
                         round(transpose(point.y * PX_PER_MAP_UNIT) - height / 2)
                     ), sprite_image)


def get_map():
    im = Image.new("RGB", (VIEW_SIZE, VIEW_SIZE), "white")

    draw = ImageDraw.Draw(im)
    for t in all_terrains:
        coords = t.poly.exterior.coords[:-1]
        coords = [(x * PX_PER_MAP_UNIT, transpose(y * PX_PER_MAP_UNIT)) for x, y in coords]

        draw.polygon(coords, fill=COLORS[t.terrain_name])

        points = random_points_in_polygon(250, t.poly)
        put_sprites_onto_image(im, points, t.terrain_name, t.poly)

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
