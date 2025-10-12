import glm
import unittest
from .utils import *
from SpatialTransform import Pose, Euler


class PoseProperties(unittest.TestCase):
    def test_init_default(self):
        """Test default initialization."""
        p = Pose()
        self.assertEqual(glm.vec3(0), p.Position)
        self.assertEqual(glm.quat(), p.Rotation)
        self.assertEqual(glm.vec3(1), p.Scale)
        self.assertEqual(glm.mat4(), p.Space)
        self.assertEqual(glm.vec3(0, 0, -1), p.Forward)
        self.assertEqual(glm.vec3(1, 0, 0), p.Right)
        self.assertEqual(glm.vec3(0, 1, 0), p.Up)

    def test_init_with_parameters(self):
        """Test initialization with custom parameters."""
        for _ in range(randomSamples):
            position = randomPosition()
            rotation = randomRotation()
            scale = randomScale()

            p = Pose(position=position, rotation=rotation, scale=scale)
            self.assertEqual(position, p.Position)
            self.assertEqual(rotation, p.Rotation)
            self.assertEqual(scale, p.Scale)

    def test_space_matrix(self):
        """Test the Space property calculation."""
        for _ in range(randomSamples):
            position = randomPosition()
            rotation = randomRotation()
            scale = randomScale()

            p = Pose(position=position, rotation=rotation, scale=scale)
            expected = (glm.translate(position) * glm.scale(scale)) * glm.mat4(rotation)
            self.assertEqual(expected, p.Space)

    def test_space_inverse(self):
        """Test the SpaceInverse property."""
        for _ in range(randomSamples):
            p = Pose(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            expected = glm.inverse(p.Space)
            self.assertEqual(expected, p.SpaceInverse)

    def test_position_setter(self):
        """Test Position property setter."""
        p = Pose()
        for _ in range(randomSamples):
            position = randomPosition()
            p.Position = position
            self.assertEqual(position, p.Position)

    def test_rotation_setter(self):
        """Test Rotation property setter."""
        p = Pose()
        for _ in range(randomSamples):
            rotation = randomRotation()
            p.Rotation = rotation
            self.assertEqual(rotation, p.Rotation)
            # Test directional vectors
            self.assertEqual(rotation * glm.vec3(0, 0, -1), p.Forward)
            self.assertEqual(rotation * glm.vec3(1, 0, 0), p.Right)
            self.assertEqual(rotation * glm.vec3(0, 1, 0), p.Up)

    def test_scale_setter(self):
        """Test Scale property setter."""
        p = Pose()
        for _ in range(randomSamples):
            scale = randomScale()
            p.Scale = scale
            self.assertEqual(scale, p.Scale)

    def test_directional_vectors(self):
        """Test Forward, Right, Up properties."""
        for _ in range(randomSamples):
            rotation = randomRotation()
            p = Pose(rotation=rotation)

            expected_forward = rotation * glm.vec3(0, 0, -1)
            expected_right = rotation * glm.vec3(1, 0, 0)
            expected_up = rotation * glm.vec3(0, 1, 0)

            self.assertGreater(deltaPosition, glm.distance(expected_forward, p.Forward))
            self.assertGreater(deltaPosition, glm.distance(expected_right, p.Right))
            self.assertGreater(deltaPosition, glm.distance(expected_up, p.Up))


class PoseMethods(unittest.TestCase):
    def test_reset(self):
        """Test reset method."""
        p = Pose(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        p.reset()

        self.assertEqual(glm.vec3(0), p.Position)
        self.assertEqual(glm.quat(), p.Rotation)
        self.assertEqual(glm.vec3(1), p.Scale)

    def test_duplicate(self):
        """Test duplicate method."""
        for _ in range(randomSamples):
            original = Pose(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            duplicate = original.duplicate()

            # Should be different objects
            self.assertNotEqual(id(original), id(duplicate))

            # But same values
            self.assertEqual(original.Position, duplicate.Position)
            self.assertEqual(original.Rotation, duplicate.Rotation)
            self.assertEqual(original.Scale, duplicate.Scale)

    def test_look_at(self):
        """Test lookAt method."""
        p = Pose()

        # Test basic directions
        directions = [
            glm.vec3(1, 0, 0),   # Right
            glm.vec3(-1, 0, 0),  # Left
            glm.vec3(0, 1, 0),   # Up
            glm.vec3(0, -1, 0),  # Down
            glm.vec3(0, 0, 1),   # Back
            glm.vec3(0, 0, -1),  # Forward
        ]

        for direction in directions:
            p.lookAt(direction)
            self.assertGreater(deltaPosition, glm.distance(glm.normalize(direction), p.Forward))

        # Test random directions
        for _ in range(randomSamples):
            direction = randomDirection()
            p.lookAt(direction)
            self.assertGreater(deltaPosition, glm.distance(glm.normalize(direction), p.Forward))

    def test_look_at_with_up(self):
        """Test lookAt method with custom up vector."""
        p = Pose()
        direction = glm.vec3(1, 0, 0)
        up = glm.vec3(0, 0, 1)

        p.lookAt(direction, up)
        self.assertGreater(deltaPosition, glm.distance(glm.normalize(direction), p.Forward))

    def test_get_euler(self):
        """Test getEuler method."""
        for _ in range(randomSamples):
            rotation = randomRotation()
            p = Pose(rotation=rotation)

            # Test different orders
            orders = ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']
            for order in orders:
                for extrinsic in [True, False]:
                    euler = p.getEuler(order=order, extrinsic=extrinsic)
                    self.assertIsInstance(euler, glm.vec3)

    def test_set_euler(self):
        """Test setEuler method."""
        p = Pose()

        for _ in range(randomSamples):
            euler_degrees = glm.vec3(
                random.uniform(-180, 180),
                random.uniform(-180, 180),
                random.uniform(-180, 180)
            )

            result = p.setEuler(euler_degrees)
            self.assertEqual(p, result)  # Should return self

            # Verify rotation was set
            self.assertNotEqual(glm.quat(), p.Rotation)

    def test_add_euler(self):
        """Test addEuler method."""
        p = Pose(rotation=randomRotation())
        original_rotation = p.Rotation

        euler_degrees = glm.vec3(10, 20, 30)

        # Test last=True
        result = p.addEuler(euler_degrees, last=True)
        self.assertEqual(p, result)  # Should return self
        self.assertNotEqual(original_rotation, p.Rotation)

        # Test last=False
        p.Rotation = original_rotation
        p.addEuler(euler_degrees, last=False)
        self.assertNotEqual(original_rotation, p.Rotation)

    def test_euler_round_trip(self):
        """Test setEuler and getEuler round trip."""
        p = Pose()

        for _ in range(100):  # Use fewer samples for complex test
            euler_degrees = glm.vec3(
                random.uniform(-89, 89),  # Avoid gimbal lock
                random.uniform(-89, 89),
                random.uniform(-89, 89)
            )

            p.setEuler(euler_degrees, order='XYZ', extrinsic=True)
            retrieved_euler = p.getEuler(order='XYZ', extrinsic=True)

            # Allow for small numerical differences
            self.assertGreater(1.0, glm.distance(euler_degrees, retrieved_euler))


class PoseRepresentation(unittest.TestCase):
    def test_repr(self):
        """Test __repr__ method."""
        p = Pose(position=glm.vec3(1, 2, 3), rotation=glm.quat(1, 0, 0, 0), scale=glm.vec3(2, 2, 2))
        repr_str = repr(p)
        self.assertIn("Pos:", repr_str)
        self.assertIn("Rot:", repr_str)
        self.assertIn("Scale:", repr_str)

    def test_str(self):
        """Test __str__ method."""
        p = Pose(position=glm.vec3(1, 2, 3), rotation=glm.quat(1, 0, 0, 0), scale=glm.vec3(2, 2, 2))
        str_repr = str(p)
        self.assertIn("Pos:", str_repr)
        self.assertIn("Rot:", str_repr)
        self.assertIn("Scale:", str_repr)


if __name__ == '__main__':
    unittest.main()
