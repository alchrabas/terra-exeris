import unittest

from shapely.geometry import Point, Polygon

import sprites


class TestSprites(unittest.TestCase):

    #     def test_exceeding_terrain_area(self):
    #         area = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)])
    #         corners = get_border_pixels_outside_of_area(Point(2, 2), area, 6, 6, 1.0)
    #         self.assertCountEqual([(0, 6), (6, 6), (0, 0)], corners)
    #
    #     def test_corners_fully_contained_in_terrain_area(self):
    #         area = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)])
    #         corners = get_border_pixels_outside_of_area(Point(3, 3), area, 2, 2, 1.0)
    #         self.assertEqual([], corners)

    def test_non_square_image(self):
        sprites.convert_image("mountains/5.png", Point(20, 20), Polygon([(0, 0), (0, 100), (100, 100), (100, 0)]), 50)
