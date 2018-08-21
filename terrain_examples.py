from shapely.geometry import Polygon, LineString


class Terrain:
    def __init__(self, poly, terrain_name, priority=1, center_line=None):
        self.poly = poly
        self.terrain_name = terrain_name
        self.priority = priority
        self.center_line = center_line


def small_forest_island(with_road=False):
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
    forest = Terrain(poly_forest, "forest", priority=2)
    road = Terrain(poly_road, "road", priority=3)

    terrains = [deep_water, shallow_water, grass_coast, grass, grass2, forest]
    if with_road:
        terrains += [road]

    return 10, terrains


def small_mountain_chain():
    poly_mountains = Polygon([(1, 2), (2, 1), (3, 2), (6, 1.5), (8, 4), (6.5, 5), (3, 6), (1.5, 5)])
    poly_grass = Polygon([(0, 0), (0, 10), (10, 10), (10, 0)]).difference(poly_mountains)
    center_line_mountains = LineString([(1, 2), (3, 4), (8, 4)])
    mountains = Terrain(poly_mountains, "mountains", 1, center_line_mountains)
    grass = Terrain(poly_grass, "grassland")
    return 10, [grass, mountains]


def show_everything():
    poly_grass = Polygon([(0.8, 0.8), (0.8, 2), (1, 2), (3, 0.8)])
    poly_grass_coast = Polygon([(0.3, 0.3), (0.3, 2), (0.8, 2), (0.8, 0.8), (3, 0.8), (3, 0.3)])
    poly_water = Polygon([(0, 0), (0, 11), (20, 11), (20, 0)])
    poly_grass2 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
    poly_forest = Polygon([(5, 2), (7, 3), (8, 5), (7, 7), (5, 8), (3, 7), (2, 5), (3, 3)])
    poly_mountains = Polygon([(11, 2), (12, 1), (13, 2), (16, 1.5), (18, 4), (16.5, 5), (13, 6), (11.5, 5)])
    center_line_mountains = LineString([(11, 2), (13, 4), (18, 4)])
    poly_grass3_and_mountains = Polygon([(10, 0.5), (18, 1), (19, 7), (13, 7), (11, 6)])

    poly_first_island = poly_grass.union(poly_forest).union(poly_grass_coast) \
        .union(poly_grass2)
    poly_shallow_water1 = poly_first_island.buffer(0.5, resolution=2).difference(poly_first_island)
    poly_second_island = poly_grass3_and_mountains
    poly_shallow_water2 = poly_second_island.buffer(0.5, resolution=2).difference(poly_second_island)
    poly_water_except_land = poly_water.difference(poly_first_island.union(poly_second_island)
                                                   .union(poly_shallow_water1).union(poly_shallow_water2))
    poly_grass3 = poly_grass3_and_mountains.difference(poly_mountains)

    grass = Terrain(poly_grass, "grassland")
    grass_coast = Terrain(poly_grass_coast, "grassland_coast")
    shallow_water1 = Terrain(poly_shallow_water1, "shallow_water", priority=0)
    deep_water = Terrain(poly_water_except_land, "deep_water", priority=0)
    shallow_water2 = Terrain(poly_shallow_water2, "shallow_water", priority=0)
    grass2 = Terrain(poly_grass2, "grassland")
    forest = Terrain(poly_forest, "forest", priority=2)
    grass3 = Terrain(poly_grass3, "grassland")

    mountains = Terrain(poly_mountains, "mountains", 1, center_line_mountains)

    terrains = [shallow_water1, shallow_water2, deep_water, grass_coast, grass, grass2, forest, grass3, mountains]

    return 20, terrains
