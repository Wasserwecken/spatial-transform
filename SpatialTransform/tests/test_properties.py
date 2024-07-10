import glm
import unittest
from utils import *
from SpatialTransform import Transform


class Local (unittest.TestCase):
    def test_Init(self):
        t = Transform()
        self.assertEqual(glm.mat4(), t.Space)
        self.assertEqual(glm.vec3(0), t.Position)
        self.assertEqual(glm.quat(), t.Rotation)
        self.assertEqual(glm.vec3(1), t.Scale)
        self.assertEqual(glm.vec3(0,0,-1), t.Forward)
        self.assertEqual(glm.vec3(1,0,0), t.Right)
        self.assertEqual(glm.vec3(0,1,0), t.Up)

        for _ in range(randomSamples):
            position = randomPosition()
            rotation = randomRotation()
            scale = randomScale()

            expected = (glm.translate(position) * glm.scale(scale)) * glm.mat4(rotation)
            result = Transform(position=position, rotation=rotation, scale=scale)

            self.assertEqual(expected, result.Space)
            self.assertEqual(position, result.Position)
            self.assertEqual(rotation, result.Rotation)
            self.assertEqual(scale, result.Scale)
            self.assertEqual(rotation * glm.vec3(0,0,-1), result.Forward)
            self.assertEqual(rotation * glm.vec3(1,0,0), result.Right)
            self.assertEqual(rotation * glm.vec3(0,1,0), result.Up)

    def test_Reset(self):
        t = Transform().reset()
        self.assertEqual(glm.mat4(), t.Space)
        self.assertEqual(glm.vec3(0), t.Position)
        self.assertEqual(glm.quat(), t.Rotation)
        self.assertEqual(glm.vec3(1), t.Scale)

        t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale()).reset()
        self.assertEqual(glm.mat4(), t.Space)
        self.assertEqual(glm.vec3(0), t.Position)
        self.assertEqual(glm.quat(), t.Rotation)
        self.assertEqual(glm.vec3(1), t.Scale)

    def test_Space(self):
        t = Transform()
        for _ in range(randomSamples):
            t.Position = randomPosition()
            t.Rotation = randomRotation()
            t.Scale = randomScale()
            space = (glm.translate(t.Position) * glm.scale(t.Scale)) * glm.mat4(t.Rotation)
            self.assertEqual(space, t.Space)

    def test_Position(self):
        t = Transform()
        for _ in range(randomSamples):
            position = randomPosition()
            space = glm.translate(position)
            t.Position = position
            self.assertEqual(position, t.Position)
            self.assertEqual(space, t.Space)

    def test_Rotation(self):
        t = Transform()
        for _ in range(randomSamples):
            rotation = randomRotation()
            space = glm.mat4(rotation)
            t.Rotation = rotation
            self.assertGreater(deltaRotation, abs(1 - glm.length(t.Rotation)))
            self.assertEqual(rotation, t.Rotation)
            self.assertEqual(space, t.Space)
            self.assertEqual(rotation * glm.vec3(0,0,-1), t.Forward)
            self.assertEqual(rotation * glm.vec3(1,0,0), t.Right)
            self.assertEqual(rotation * glm.vec3(0,1,0), t.Up)

    def test_Scale(self):
        t = Transform()
        for _ in range(randomSamples):
            scale = randomScale()
            space = glm.scale(scale)
            t.Scale = scale
            self.assertEqual(scale, t.Scale)
            self.assertEqual(space, t.Space)

class World(unittest.TestCase):
    def test_Init(self):
        root = Transform()
        child = Transform()
        root.attach(child)

        self.assertEqual(glm.mat4(), child.SpaceWorld)
        self.assertEqual(glm.vec3(0), child.PositionWorld)
        self.assertEqual(glm.quat(), child.RotationWorld)
        self.assertEqual(glm.vec3(1), child.ScaleWorld)
        self.assertEqual(glm.vec3(0,0,-1), child.ForwardWorld)
        self.assertEqual(glm.vec3(1,0,0), child.RightWorld)
        self.assertEqual(glm.vec3(0,1,0), child.UpWorld)

        for _ in range(randomSamples):
            root = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            child = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            root.attach(child)
            self.assertEqual(root.Space * child.Space, child.SpaceWorld)
            self.assertEqual(glm.inverse(root.Space * child.Space), child.SpaceWorldInverse)

    def test_Reset(self):
        root = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        child = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
        root.attach(child)

        child.reset()
        self.assertEqual(child.SpaceWorld, root.SpaceWorld)
        self.assertEqual(child.PositionWorld, root.PositionWorld)
        self.assertEqual(child.RotationWorld, root.RotationWorld)
        self.assertEqual(child.ScaleWorld, root.ScaleWorld)

        root.reset()
        self.assertEqual(glm.mat4(), child.SpaceWorld)
        self.assertEqual(glm.vec3(0), child.PositionWorld)
        self.assertEqual(glm.quat(), child.RotationWorld)
        self.assertEqual(glm.vec3(1), child.ScaleWorld)

    def test_Space(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.Position = randomPosition()
            root.Rotation = randomRotation()
            root.Scale = randomScale()

            child.Position = randomPosition()
            child.Rotation = randomRotation()
            child.Scale = randomScale()

            self.assertEqual(root.Space * child.Space, child.SpaceWorld)
            self.assertEqual(glm.inverse(root.Space * child.Space), child.SpaceWorldInverse)

    def test_Position(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.Position = randomPosition()
            child.Position = randomPosition()
            self.assertEqual(root.Space * child.Position, child.PositionWorld)

    def test_Rotation(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.Rotation = randomRotation()
            child.Rotation = randomRotation()
            self.assertEqual(root.Rotation * child.Rotation, child.RotationWorld)
            self.assertGreater(deltaRotation, abs(1 - glm.length(child.RotationWorld)))
            self.assertEqual((root.Rotation * child.Rotation) * glm.vec3(0,0,-1), child.ForwardWorld)
            self.assertEqual((root.Rotation * child.Rotation) * glm.vec3(1,0,0), child.RightWorld)
            self.assertEqual((root.Rotation * child.Rotation) * glm.vec3(0,1,0), child.UpWorld)

    def test_Scale(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.Scale = randomScale()
            child.Scale = randomScale()
            self.assertEqual(root.Scale * child.Scale, child.ScaleWorld)

if __name__ == '__main__':
    unittest.main()
