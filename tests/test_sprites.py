import math
import unittest

from src import sprites


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

#    def test_non_square_image(self):
#        sprites.convert_image("mountains/5.png", Point(20, 20), Polygon([(20, 20.5), (0, 1), (1, 1), (1, 0)]), 50)

    def test_without_rotation(self):
        pass

    def test_with_rotation(self):
        points_in_terrain = self._fill_set_with_coords_in_rectangular_area(200, 50, 100, 70, 150)
        distance_to_closest_point = {}
        for point in points_in_terrain:
            distance_to_closest_point[point] = 0

        sprites.convert_image("grassland/1.png", (100, 100), math.pi / 2,
                              points_in_terrain, distance_to_closest_point, 0)

    @staticmethod
    def _fill_set_with_coords_in_rectangular_area(size, from_x, to_x, from_y, to_y):
        a = set()
        for x in range(0, size):
            for y in range(0, size):
                if from_x <= x <= to_x and \
                        from_y <= y <= to_y:
                    a.add((x, y))
        return a

    # def test_angle(self):
    #     line_string = LineString([(0, 0), (0, 10)])
    #     point = Point(0, 5)
    #     self.assertEqual(0, get_angle(line_string, point))
    #
    #     line_string = LineString([(0, 0), (10, 0)])
    #     point = Point(5, 0)
    #     self.assertEqual(math.pi / 2, get_angle(line_string, point))
    #
    #     line_string = LineString([(0, 0), (10, 10)])
    #     point = Point(5, 5)
    #     self.assertEqual(math.pi / 4, get_angle(line_string, point))
