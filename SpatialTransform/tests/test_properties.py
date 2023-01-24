import glm
import unittest
from utils import *
from SpatialTransform import Transform


class Local(unittest.TestCase):
    def test_Init(self):
        t = Transform()
        self.assertEqual(glm.mat4(), t.SpaceLocal)
        self.assertEqual(glm.vec3(0), t.PositionLocal)
        self.assertEqual(glm.quat(), t.RotationLocal)
        self.assertEqual(glm.vec3(1), t.ScaleLocal)
        self.assertEqual(glm.vec3(0,0,-1), t.ForwardLocal)
        self.assertEqual(glm.vec3(1,0,0), t.RightLocal)
        self.assertEqual(glm.vec3(0,1,0), t.UpLocal)

        for _ in range(randomSamples):
            position = randomPosition()
            rotation = randomRotation()
            scale = randomScale()

            expected = (glm.translate(position) * glm.scale(scale)) * glm.mat4(rotation)
            result = Transform(position=position, rotation=rotation, scale=scale)

            self.assertEqual(expected, result.SpaceLocal)
            self.assertEqual(position, result.PositionLocal)
            self.assertEqual(rotation, result.RotationLocal)
            self.assertEqual(scale, result.ScaleLocal)
            self.assertEqual(rotation * glm.vec3(0,0,-1), result.ForwardLocal)
            self.assertEqual(rotation * glm.vec3(1,0,0), result.RightLocal)
            self.assertEqual(rotation * glm.vec3(0,1,0), result.UpLocal)

    def test_Reset(self):
        t = Transform().reset()
        self.assertEqual(glm.mat4(), t.SpaceLocal)
        self.assertEqual(glm.vec3(0), t.PositionLocal)
        self.assertEqual(glm.quat(), t.RotationLocal)
        self.assertEqual(glm.vec3(1), t.ScaleLocal)

        t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale()).reset()
        self.assertEqual(glm.mat4(), t.SpaceLocal)
        self.assertEqual(glm.vec3(0), t.PositionLocal)
        self.assertEqual(glm.quat(), t.RotationLocal)
        self.assertEqual(glm.vec3(1), t.ScaleLocal)

    def test_Space(self):
        t = Transform()
        for _ in range(randomSamples):
            t.PositionLocal = randomPosition()
            t.RotationLocal = randomRotation()
            t.ScaleLocal = randomScale()
            space = (glm.translate(t.PositionLocal) * glm.scale(t.ScaleLocal)) * glm.mat4(t.RotationLocal)
            self.assertEqual(space, t.SpaceLocal)

    def test_Position(self):
        t = Transform()
        for _ in range(randomSamples):
            position = randomPosition()
            space = glm.translate(position)
            t.PositionLocal = position
            self.assertEqual(position, t.PositionLocal)
            self.assertEqual(space, t.SpaceLocal)

    def test_Rotation(self):
        t = Transform()
        for _ in range(randomSamples):
            rotation = randomRotation()
            space = glm.mat4(rotation)
            t.RotationLocal = rotation
            self.assertGreater(deltaRotation, abs(1 - glm.length(t.RotationLocal)))
            self.assertEqual(rotation, t.RotationLocal)
            self.assertEqual(space, t.SpaceLocal)
            self.assertEqual(rotation * glm.vec3(0,0,-1), t.ForwardLocal)
            self.assertEqual(rotation * glm.vec3(1,0,0), t.RightLocal)
            self.assertEqual(rotation * glm.vec3(0,1,0), t.UpLocal)

    def test_Scale(self):
        t = Transform()
        for _ in range(randomSamples):
            scale = randomScale()
            space = glm.scale(scale)
            t.ScaleLocal = scale
            self.assertEqual(scale, t.ScaleLocal)
            self.assertEqual(space, t.SpaceLocal)

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
            self.assertEqual(root.SpaceLocal * child.SpaceLocal, child.SpaceWorld)
            self.assertEqual(glm.inverse(root.SpaceLocal * child.SpaceLocal), child.SpaceWorldInverse)

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
            root.PositionLocal = randomPosition()
            root.RotationLocal = randomRotation()
            root.ScaleLocal = randomScale()

            child.PositionLocal = randomPosition()
            child.RotationLocal = randomRotation()
            child.ScaleLocal = randomScale()

            self.assertEqual(root.SpaceLocal * child.SpaceLocal, child.SpaceWorld)
            self.assertEqual(glm.inverse(root.SpaceLocal * child.SpaceLocal), child.SpaceWorldInverse)

    def test_Position(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.PositionLocal = randomPosition()
            child.PositionLocal = randomPosition()
            self.assertEqual(root.SpaceLocal * child.PositionLocal, child.PositionWorld)

    def test_Rotation(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.RotationLocal = randomRotation()
            child.RotationLocal = randomRotation()
            self.assertEqual(root.RotationLocal * child.RotationLocal, child.RotationWorld)
            self.assertGreater(deltaRotation, abs(1 - glm.length(child.RotationWorld)))
            self.assertEqual((root.RotationLocal * child.RotationLocal) * glm.vec3(0,0,-1), child.ForwardWorld)
            self.assertEqual((root.RotationLocal * child.RotationLocal) * glm.vec3(1,0,0), child.RightWorld)
            self.assertEqual((root.RotationLocal * child.RotationLocal) * glm.vec3(0,1,0), child.UpWorld)

    def test_Scale(self):
        root = Transform()
        child = Transform()
        root.attach(child)
        for _ in range(randomSamples):
            root.ScaleLocal = randomScale()
            child.ScaleLocal = randomScale()
            self.assertEqual(root.ScaleLocal * child.ScaleLocal, child.ScaleWorld)

if __name__ == '__main__':
    unittest.main()
