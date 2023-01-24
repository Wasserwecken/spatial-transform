import glm
import unittest
from utils import *
from SpatialTransform import Transform, Euler

class Convertions(unittest.TestCase):
    def test_pointToWorld(self):
        for _ in range(randomSamples):
            p = randomPosition() * 10
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            self.assertEqual(c.pointToWorld(p), (t.SpaceLocal * c.SpaceLocal) * p)

    def test_pointToLocal(self):
        for _ in range(randomSamples):
            p = randomPosition() * 10
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            self.assertEqual(c.pointToLocal(p), glm.inverse(t.SpaceLocal * c.SpaceLocal) * p)

    def test_directionToWorld(self):
        for _ in range(randomSamples):
            p = randomPosition()
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            self.assertEqual(c.directionToWorld(p), (t.RotationLocal * c.RotationLocal) * p)

    def test_directionToLocal(self):
        for _ in range(randomSamples):
            p = randomPosition()
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            self.assertEqual(c.directionToLocal(p), glm.inverse((t.RotationLocal * c.RotationLocal)) * p)

class Rotations(unittest.TestCase):
    def test_setEuler(self):
        t = Transform()
        t.setEuler((+90, 0, 0), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(0,+1,0), t.ForwardLocal))
        t.setEuler((-90, 0, 0), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(0,-1,0), t.ForwardLocal))

        t.setEuler((0, +90, 0), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(-1,0,0), t.ForwardLocal))
        t.setEuler((0, -90, 0), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(+1,0,0), t.ForwardLocal))

        t.setEuler((0, 0, -90), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(0,0,-1), t.ForwardLocal))
        t.setEuler((0, 0, +90), order='ZXY', extrinsic=True)
        self.assertGreater(deltaPosition, glm.distance(glm.vec3(0,0,-1), t.ForwardLocal))

        for _ in range(randomSamples):
            r = randomRotation()
            e = glm.degrees(glm.eulerAngles(r))
            t.setEuler(e, order='XYZ', extrinsic=True)
            angle = glm.angle(r * glm.inverse(t.RotationLocal))
            self.assertFalse(0.01 < angle < (glm.two_pi()-0.01))

    def test_lookAtWorld(self):
        for _ in range(randomSamples):
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            d = randomDirection()
            c.lookAtWorld(d)
            self.assertGreater(deltaPosition, glm.distance(glm.normalize(d), c.ForwardWorld))
            self.assertGreater(deltaPosition, glm.distance(t.RotationWorldInverse * glm.normalize(d), c.ForwardLocal))

    def test_lookAtLocal(self):
        for _ in range(randomSamples):
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            d = randomDirection()
            c.lookAtLocal(d)
            self.assertGreater(deltaPosition, glm.distance(glm.normalize(d), c.ForwardLocal))
            self.assertGreater(deltaPosition, glm.distance(t.RotationWorld * glm.normalize(d), c.ForwardWorld))

    def test_applyPosition(self):
        for _ in range(randomSamples):
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            childWorld = c.PositionWorld
            t.applyPosition()
            self.assertGreater(deltaPosition, glm.distance2(glm.vec3(0), t.PositionLocal))
            self.assertGreater(deltaPosition, glm.distance2(childWorld, c.PositionWorld))

            addition = randomPosition()
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            parentLocal = t.PositionLocal
            childWorld = c.PositionWorld
            t.applyPosition(addition)
            self.assertGreater(deltaPosition, glm.distance2(parentLocal + addition, t.PositionLocal))
            self.assertGreater(deltaPosition, glm.distance2(childWorld, c.PositionWorld))

    def test_applyRotation(self):
        for _ in range(randomSamples):
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            childWorld = c.RotationWorld
            t.applyRotation()
            self.assertGreater(deltaRotation, glm.angle(t.RotationLocal))
            self.assertGreater(deltaRotation, glm.angle(glm.inverse(c.RotationWorld) * childWorld))

            addition = randomRotation()
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            parentLocal = t.RotationLocal
            childWorld = c.RotationWorld
            t.applyRotation(addition)
            self.assertGreater(deltaRotation, glm.angle((parentLocal * addition) * glm.inverse(t.RotationLocal)))
            self.assertGreater(deltaRotation, glm.angle(childWorld * glm.inverse(c.RotationWorld)))

    def test_applyScale(self):
        for _ in range(randomSamples):
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            childWorld = c.ScaleWorld
            t.appyScale()
            self.assertGreater(deltaPosition, glm.distance2(glm.vec3(1), t.ScaleLocal))
            self.assertGreater(deltaPosition, glm.distance2(childWorld, c.ScaleWorld))

            addition = randomScale()
            t = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            c = Transform(position=randomPosition(), rotation=randomRotation(), scale=randomScale())
            t.attach(c)
            parentLocal = t.ScaleLocal
            childWorld = c.ScaleWorld
            t.appyScale(addition)
            self.assertGreater(deltaPosition, glm.distance2(parentLocal * addition, t.ScaleLocal))
            self.assertGreater(deltaPosition, glm.distance2(childWorld, c.ScaleWorld))

if __name__ == '__main__':
    unittest.main()
