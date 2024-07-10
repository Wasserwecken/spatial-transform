import glm
import unittest
from utils import *
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

if __name__ == '__main__':
    unittest.main()
