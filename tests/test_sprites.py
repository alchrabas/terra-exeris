import unittest

from shapely.geometry import Point, Polygon

from sprites import get_corners_exceeding_terrain_area


class TestSprites(unittest.TestCase):
    def test_exceeding_terrain_area(self):
        area = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)])
        corners = get_corners_exceeding_terrain_area(Point(2, 2), area, 6, 6, 1.0)
        self.assertCountEqual([(0, 6), (6, 6), (0, 0)], corners)

    def test_corners_fully_contained_in_terrain_area(self):
        area = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)])
        corners = get_corners_exceeding_terrain_area(Point(3, 3), area, 2, 2, 1.0)
        self.assertEqual([], corners)
