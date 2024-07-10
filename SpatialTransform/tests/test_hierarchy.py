import unittest
from utils import *
from SpatialTransform import Transform

class AddRemove(unittest.TestCase):
    def test_attatch(self):
        root = Transform()
        child1 = Transform()
        child2= Transform()
        child3 = Transform()
        child4= Transform()

        root.attach(child1)
        self.assertEqual(root, child1.Parent)
        self.assertEqual(1, len(root.Children))

        root.attach(child2)
        self.assertEqual(root, child2.Parent)
        self.assertEqual(2, len(root.Children))

        root.attach(child3, child4)
        self.assertEqual(root, child3.Parent)
        self.assertEqual(root, child4.Parent)
        self.assertEqual(4, len(root.Children))

        root.attach(child1)


    def test_attatchKeepProperties(self):
        for _ in range(randomSamples):
            root = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            child1 = Transform()
            child2 = Transform()

            for _ in range(2):
                root.attach(child1, keep=None)
                self.assertGreater(deltaPosition, glm.distance2(root.SpaceWorld * glm.vec3(0), child1.PositionWorld))
                self.assertGreater(deltaRotation, glm.angle(root.RotationWorld * glm.inverse(child1.RotationWorld)))
                self.assertGreater(deltaScale, glm.distance2(root.ScaleWorld, child1.ScaleWorld))

            for _ in range(2):
                root.attach(child2, keep=['position', 'rotation', 'scale'])
                self.assertGreater(deltaPosition, glm.distance2(glm.vec3(0), child2.PositionWorld))
                self.assertGreater(deltaRotation, glm.angle(child2.RotationWorld))
                self.assertGreater(deltaScale, glm.distance2(glm.vec3(1), child2.ScaleWorld))

    def test_detatch(self):
        root = Transform()
        child1 = Transform()
        child2 = Transform()

        root.attach(child1, child2)

        root.detach(child1)
        self.assertEqual(None, child1.Parent)
        self.assertEqual(1, len(root.Children))

        root.detach(child2)
        self.assertEqual(None, child2.Parent)
        self.assertEqual(0, len(root.Children))

        otherRoot = Transform().attach(child1)
        root.clearChildren().attach(child2)
        root.detach(child1, child2)
        self.assertEqual(1, len(otherRoot.Children))
        self.assertEqual(0, len(root.Children))
        self.assertEqual(otherRoot, child1.Parent)
        self.assertEqual(None, child2.Parent)

    def test_detatch_Exceptions(self):
        child = Transform()
        root = Transform().attach(child)
        root.Children.remove(child)

        self.assertRaises(ValueError, root.detach, None)
        self.assertRaises(ValueError, root.detach, root)
        self.assertRaises(ValueError, root.detach, child)

    def test_detatchKeepProperties(self):
        for _ in range(randomSamples):
            root = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            child1 = Transform()
            child2 = Transform()
            root.attach(child1, child2, keep=None)

            for _ in range(2):
                root.detach(child1, keep=None)
                self.assertGreater(deltaPosition, glm.distance2(glm.vec3(0), child1.PositionWorld))
                self.assertGreater(deltaRotation, glm.angle(child1.RotationWorld))
                self.assertGreater(deltaScale, glm.distance2(glm.vec3(1), child1.ScaleWorld))

            for _ in range(2):
                root.detach(child2, keep=['position', 'rotation', 'scale'])
                self.assertGreater(deltaPosition, glm.distance2(root.SpaceWorld * glm.vec3(0), child2.PositionWorld))
                self.assertGreater(deltaRotation, glm.angle(root.RotationWorld * glm.inverse(child2.RotationWorld)))
                self.assertGreater(deltaScale, glm.distance2(root.ScaleWorld, child2.ScaleWorld))

    def test_clearChildren(self):
        root = Transform()
        child1 = Transform()
        child2 = Transform()

        root.attach(child1)
        root.clearChildren()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(0, len(root.Children))

        root.attach(child1, child2)
        root.clearChildren()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(None, child2.Parent)
        self.assertEqual(0, len(root.Children))

        root.clearChildren()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(None, child2.Parent)
        self.assertEqual(0, len(root.Children))

    def test_clearParent(self):
        root = Transform()
        child1 = Transform()
        child2 = Transform()

        root.attach(child1, child2)
        child1.clearParent()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(1, len(root.Children))

        child2.clearParent()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(None, child2.Parent)
        self.assertEqual(0, len(root.Children))

        child2.clearParent()
        self.assertEqual(None, child1.Parent)
        self.assertEqual(None, child2.Parent)
        self.assertEqual(0, len(root.Children))

if __name__ == '__main__':
    unittest.main()
