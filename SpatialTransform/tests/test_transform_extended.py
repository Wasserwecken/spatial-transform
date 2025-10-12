import glm
import unittest
import re
from .utils import *
from SpatialTransform import Transform, Pose


class TransformUtilities(unittest.TestCase):
    def test_name_property(self):
        """Test Name property getter and setter."""
        t = Transform()
        # Default name should be 8 random characters
        self.assertEqual(8, len(t.Name))

        # Test custom name
        custom_name = "TestTransform"
        t.Name = custom_name
        self.assertEqual(custom_name, t.Name)

        # Test name in constructor
        t2 = Transform(name="ConstructorName")
        self.assertEqual("ConstructorName", t2.Name)

    def test_layout(self):
        """Test layout method."""
        root = Transform(name="Root")
        child1 = Transform(name="Child1")
        child2 = Transform(name="Child2")
        grandchild = Transform(name="GrandChild")

        root.attach(child1, child2)
        child1.attach(grandchild)

        layout = root.layout()

        # Should return list of tuples [transform, index, depth]
        self.assertEqual(4, len(layout))

        # Check root
        self.assertEqual(root, layout[0][0])
        self.assertEqual(0, layout[0][1])  # index
        self.assertEqual(0, layout[0][2])  # depth

        # Check child1
        self.assertEqual(child1, layout[1][0])
        self.assertEqual(1, layout[1][1])
        self.assertEqual(1, layout[1][2])

        # Check grandchild
        self.assertEqual(grandchild, layout[2][0])
        self.assertEqual(2, layout[2][1])
        self.assertEqual(2, layout[2][2])

        # Check child2
        self.assertEqual(child2, layout[3][0])
        self.assertEqual(3, layout[3][1])
        self.assertEqual(1, layout[3][2])

    def test_filter(self):
        """Test filter method."""
        root = Transform(name="RootNode")
        child1 = Transform(name="TestChild")
        child2 = Transform(name="AnotherChild")
        child3 = Transform(name="TestNode")

        root.attach(child1, child2, child3)

        # Test partial match (default)
        results = root.filter("Test")
        self.assertEqual(2, len(results))
        self.assertIn(child1, results)
        self.assertIn(child3, results)

        # Test exact match
        results = root.filter("TestChild", isEqual=True)
        self.assertEqual(1, len(results))
        self.assertEqual(child1, results[0])

        # Test case sensitivity
        results = root.filter("test", caseSensitive=False)
        self.assertEqual(2, len(results))

        results = root.filter("test", caseSensitive=True)
        self.assertEqual(0, len(results))

        # Test no matches
        results = root.filter("NonExistent")
        self.assertEqual(0, len(results))

    def test_filter_regex(self):
        """Test filterRegex method."""
        root = Transform(name="Root")
        child1 = Transform(name="Test123")
        child2 = Transform(name="AnotherChild")
        child3 = Transform(name="Test456")

        root.attach(child1, child2, child3)

        # Test regex pattern
        results = root.filterRegex(r"Test\d+")
        self.assertEqual(2, len(results))
        self.assertIn(child1, results)
        self.assertIn(child3, results)

        # Test exact match regex
        results = root.filterRegex("^Root$")
        self.assertEqual(1, len(results))
        self.assertEqual(root, results[0])

        # Test no matches
        results = root.filterRegex(r"Node\d+")
        self.assertEqual(0, len(results))

    def test_print_tree(self):
        """Test printTree method (verify it doesn't crash)."""
        root = Transform(name="Root")
        child1 = Transform(name="Child1")
        child2 = Transform(name="Child2")
        grandchild = Transform(name="GrandChild")

        root.attach(child1, child2)
        child1.attach(grandchild)

        # This should not crash
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        root.printTree()
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Root", output)
        self.assertIn("Child1", output)
        self.assertIn("Child2", output)
        self.assertIn("GrandChild", output)

    def test_to_pose(self):
        """Test toPose method."""
        for _ in range(randomSamples):
            position = randomPosition()
            rotation = randomRotation()
            scale = randomScale()

            t = Transform(position=position, rotation=rotation, scale=scale)

            # Test local space
            pose_local = t.toPose(worldSpace=False)
            self.assertEqual(position, pose_local.Position)
            self.assertEqual(rotation, pose_local.Rotation)
            self.assertEqual(scale, pose_local.Scale)

            # Test world space with parent
            parent = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            parent.attach(t)

            pose_world = t.toPose(worldSpace=True)
            self.assertEqual(t.PositionWorld, pose_world.Position)
            self.assertEqual(t.RotationWorld, pose_world.Rotation)
            self.assertEqual(t.ScaleWorld, pose_world.Scale)

    def test_from_pose(self):
        """Test fromPose static method."""
        for _ in range(randomSamples):
            pose = Pose(position=randomPosition(), rotation=randomRotation(), scale=randomScale())

            # Test without name
            t = Transform.fromPose(pose)
            self.assertEqual(pose.Position, t.Position)
            self.assertEqual(pose.Rotation, t.Rotation)
            self.assertEqual(pose.Scale, t.Scale)

            # Test with name
            custom_name = "FromPoseTest"
            t_named = Transform.fromPose(pose, name=custom_name)
            self.assertEqual(custom_name, t_named.Name)
            self.assertEqual(pose.Position, t_named.Position)
            self.assertEqual(pose.Rotation, t_named.Rotation)
            self.assertEqual(pose.Scale, t_named.Scale)


class TransformEdgeCases(unittest.TestCase):
    def test_duplicate_recursive(self):
        """Test duplicate with recursive=True."""
        root = Transform(name="Root", position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child1 = Transform(name="Child1", position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child2 = Transform(name="Child2", position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        grandchild = Transform(name="GrandChild", position=randomPosition(), rotation=randomRotation(), scale=randomScale())

        root.attach(child1, child2)
        child1.attach(grandchild)

        # Test recursive duplicate
        duplicate = root.duplicate(recursive=True)

        # Should be different objects
        self.assertNotEqual(root, duplicate)
        self.assertNotEqual(child1, duplicate.Children[0])

        # But same properties
        self.assertEqual(root.Name, duplicate.Name)
        self.assertEqual(len(root.Children), len(duplicate.Children))
        self.assertEqual(child1.Name, duplicate.Children[0].Name)

        # Check hierarchy integrity
        self.assertEqual(duplicate, duplicate.Children[0].Parent)
        self.assertEqual(1, len(duplicate.Children[0].Children))  # grandchild

    def test_duplicate_non_recursive(self):
        """Test duplicate with recursive=False."""
        root = Transform(name="Root", position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child = Transform(name="Child", position=randomPosition(), rotation=randomRotation(), scale=randomScale())

        root.attach(child)

        # Test non-recursive duplicate
        duplicate = root.duplicate(recursive=False)

        # Should be different object
        self.assertNotEqual(root, duplicate)

        # Same properties but no children
        self.assertEqual(root.Name, duplicate.Name)
        self.assertEqual(0, len(duplicate.Children))

    def test_reset_recursive(self):
        """Test reset with recursive=True."""
        root = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())

        root.attach(child)

        # Reset recursively
        root.reset(recursive=True)

        # Both should be reset
        self.assertEqual(glm.vec3(0), root.Position)
        self.assertEqual(glm.quat(), root.Rotation)
        self.assertEqual(glm.vec3(1), root.Scale)

        self.assertEqual(glm.vec3(0), child.Position)
        self.assertEqual(glm.quat(), child.Rotation)
        self.assertEqual(glm.vec3(1), child.Scale)

    def test_world_property_setters(self):
        """Test world space property setters."""
        parent = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        parent.attach(child)

        # Test PositionWorld setter
        new_world_pos = randomPosition()
        child.PositionWorld = new_world_pos
        self.assertGreater(deltaPosition, glm.distance2(new_world_pos, child.PositionWorld))

        # Test RotationWorld setter
        new_world_rot = randomRotation()
        child.RotationWorld = new_world_rot
        self.assertGreater(deltaRotation, glm.angle(new_world_rot * glm.inverse(child.RotationWorld)))

        # Test ScaleWorld setter
        new_world_scale = randomScale()
        child.ScaleWorld = new_world_scale
        self.assertGreater(deltaPosition, glm.distance2(new_world_scale, child.ScaleWorld))


if __name__ == '__main__':
    unittest.main()
