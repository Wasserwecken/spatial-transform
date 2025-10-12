import glm
import unittest
import math
from .utils import *
from SpatialTransform import Euler

class Conversions(unittest.TestCase):
    def test_toQuatFrom(self):
        for _ in range(randomSamples):
            r = randomRotation()
            e = glm.eulerAngles(r)
            angle = glm.angle(Euler.toQuatFrom(e, order='XYZ', extrinsic=True) * glm.inverse(r))
            self.assertFalse(0.01 < angle < (glm.two_pi()-0.01))

    def test_fromMatTo(self):
        for _ in range(randomSamples):
            r = randomRotation()
            e = glm.eulerAngles(r)
            m = glm.mat3_cast(r)
            self.assertGreater(0.01, glm.distance(e, Euler.fromMatTo(m, order='XYZ', extrinsic=True)))

    def test_toMatFrom(self):
        """Test toMatFrom method."""
        for _ in range(randomSamples):
            euler = glm.vec3(
                random.uniform(-math.pi, math.pi),
                random.uniform(-math.pi, math.pi),
                random.uniform(-math.pi, math.pi)
            )

            # Test different orders
            orders = ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']
            for order in orders:
                for extrinsic in [True, False]:
                    mat = Euler.toMatFrom(euler, order=order, extrinsic=extrinsic)
                    self.assertIsInstance(mat, glm.mat3)

                    # Verify it's a proper rotation matrix (determinant should be 1)
                    det = glm.determinant(mat)
                    self.assertGreater(0.01, abs(det - 1.0))

    def test_fromQuatTo(self):
        """Test fromQuatTo method."""
        for _ in range(randomSamples):
            rotation = randomRotation()

            # Test different orders
            orders = ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']
            for order in orders:
                for extrinsic in [True, False]:
                    euler = Euler.fromQuatTo(rotation, order=order, extrinsic=extrinsic)
                    self.assertIsInstance(euler, glm.vec3)

                    # Round trip test
                    recovered_quat = Euler.toQuatFrom(euler, order=order, extrinsic=extrinsic)
                    angle_diff = glm.angle(rotation * glm.inverse(recovered_quat))
                    self.assertFalse(0.01 < angle_diff < (glm.two_pi()-0.01))

    def test_all_rotation_orders(self):
        """Test all supported rotation orders."""
        orders = ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']

        for order in orders:
            for extrinsic in [True, False]:
                euler = glm.vec3(0.5, 1.0, 1.5)  # Test angles in radians

                # Test conversion chain: euler -> quat -> mat -> euler
                quat = Euler.toQuatFrom(euler, order=order, extrinsic=extrinsic)
                mat = Euler.toMatFrom(euler, order=order, extrinsic=extrinsic)

                # Verify quat and mat represent same rotation
                mat_from_quat = glm.mat3_cast(quat)
                for i in range(3):
                    for j in range(3):
                        self.assertGreater(0.01, abs(mat[i][j] - mat_from_quat[i][j]))

    def test_round_trip_conversions(self):
        """Test round trip conversions between different representations."""
        for _ in range(100):  # Fewer samples for complex test
            original_euler = glm.vec3(
                random.uniform(-math.pi/2, math.pi/2),  # Avoid gimbal lock
                random.uniform(-math.pi/2, math.pi/2),
                random.uniform(-math.pi/2, math.pi/2)
            )

            order = 'XYZ'
            extrinsic = True

            # euler -> quat -> euler
            quat = Euler.toQuatFrom(original_euler, order=order, extrinsic=extrinsic)
            recovered_euler = Euler.fromQuatTo(quat, order=order, extrinsic=extrinsic)
            self.assertGreater(0.1, glm.distance(original_euler, recovered_euler))

            # euler -> mat -> euler
            mat = Euler.toMatFrom(original_euler, order=order, extrinsic=extrinsic)
            recovered_euler_mat = Euler.fromMatTo(mat, order=order, extrinsic=extrinsic)
            self.assertGreater(0.1, glm.distance(original_euler, recovered_euler_mat))


class EulerUtilities(unittest.TestCase):
    def test_getOrders(self):
        """Test getOrders static method."""
        orders = Euler.getOrders()
        expected_orders = ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']

        self.assertEqual(len(expected_orders), len(orders))
        for order in expected_orders:
            self.assertIn(order, orders)

    def test_invalid_order(self):
        """Test behavior with invalid rotation order."""
        euler = glm.vec3(0.1, 0.2, 0.3)

        # This should raise an error for invalid order
        with self.assertRaises(ValueError):
            Euler.fromMatTo(glm.mat3(), order='INVALID', extrinsic=True)


if __name__ == '__main__':
    unittest.main()
