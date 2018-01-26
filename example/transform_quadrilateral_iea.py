from numpy import matmul, cos, sin, pi
from numpy.linalg import solve, inv


class AreaMapping:
    # Maps any quadrilateral (real coordinates) to another specified rectangle (desired coordinates)
    def __init__(self, real_area_coords, desired_rectangle_coords):
        self.real_area_coords = real_area_coords
        self.desired_rectangle_coords = desired_rectangle_coords
        self.map_to_rectangle = self.matrix()
        self.map_to_shape = inv(self.map_to_rectangle)

    def matrix(self):
        x1 = self.real_area_coords[0][0]
        y1 = self.real_area_coords[0][1]
        x2 = self.real_area_coords[1][0]
        y2 = self.real_area_coords[1][1]
        x3 = self.real_area_coords[2][0]
        y3 = self.real_area_coords[2][1]
        x4 = self.real_area_coords[3][0]
        y4 = self.real_area_coords[3][1]
        u1 = self.desired_rectangle_coords[0][0]
        v1 = self.desired_rectangle_coords[0][1]
        u2 = self.desired_rectangle_coords[1][0]
        v2 = self.desired_rectangle_coords[1][1]
        u3 = self.desired_rectangle_coords[2][0]
        v3 = self.desired_rectangle_coords[2][1]
        u4 = self.desired_rectangle_coords[3][0]
        v4 = self.desired_rectangle_coords[3][1]
        A = [[x1, y1, 1, 0, 0, 0, - u1 * x1, - u1 * y1], [0, 0, 0, x1, y1, 1, - v1 * x1, - v1 * y1],
        [x2, y2, 1, 0, 0, 0, - u2 * x2, - u2 * y2], [0, 0, 0, x2, y2, 1, - v2 * x2, - v2 * y2],
        [x3, y3, 1, 0, 0, 0, - u3 * x3, - u3 * y3], [0, 0, 0, x3, y3, 1, - v3 * x3, - v3 * y3],
        [x4, y4, 1, 0, 0, 0, - u4 * x4, - u4 * y4], [0, 0, 0, x4, y4, 1, - v4 * x4, - v4 * y4]]
        b = [u1, v1, u2, v2, u3, v3, u4, v4]
        [a, b, c, d, e, f, g, h] = solve(A, b)
        return [[a, b, c], [d, e, f], [g, h, 1]]

    def transform_to_rectangle(self, x, y):
        non_dim = matmul(self.map_to_rectangle, [x, y, 1])
        return non_dim[0] / non_dim[2], non_dim[1] / non_dim[2]

    def transform_to_shape(self, u, v):
        non_dim = matmul(self.map_to_shape, [u, v, 1])
        return non_dim[0] / non_dim[2], non_dim[1] / non_dim[2]
