import math
import glm

#https://en.wikipedia.org/wiki/Euler_angles
class Euler:
    """Static collection of conversions for euler angles.

    Matrices are expected to be column major, like glm.
    """

    def toQuatFrom(radians:glm.vec3, order:str, intrinsic:bool) -> glm.quat:
        """Converts euler angles to quaternion.

        Rotation order of eulers must be given as 'XYZ' in any order.

        If intrinsic the rotation will be around the axes, respecting the previous rotations"""
        result = glm.quat()
        for axis in order:
            if intrinsic:
                if axis.upper() == 'X': result = glm.rotate(result, radians.x, (1, 0, 0)); continue
                if axis.upper() == 'Y': result = glm.rotate(result, radians.y, (0, 1, 0)); continue
                if axis.upper() == 'Z': result = glm.rotate(result, radians.z, (0, 0, 1)); continue
            else:
                if axis.upper() == 'X': result = glm.rotate(result, radians.x, glm.inverse(result) * (1, 0, 0)); continue
                if axis.upper() == 'Y': result = glm.rotate(result, radians.y, glm.inverse(result) * (0, 1, 0)); continue
                if axis.upper() == 'Z': result = glm.rotate(result, radians.z, glm.inverse(result) * (0, 0, 1)); continue
        return result

    def toMatFrom(radians:glm.vec3, order:str, extrinsic:bool) -> glm.mat3:
        """Converts euler angles to 3x3 rotation matrix.

        Rotation order of eulers must be given as 'XYZ' in any order"""
        return glm.mat3_cast(Euler.toQuatFrom(radians, order, extrinsic))


    def fromQuatTo(quat:glm.quat, order:str) -> glm.vec3:
        """Converts a quaternion to intrinsic euler angles as radians.

        Rotation order of eulers must be given as 'XYZ' in any order"""
        return Euler.fromMatTo(glm.mat3_cast(quat), order)

    def fromMatTo(mat:glm.mat3, order:str) -> glm.vec3:
        """Converts a 3x3 rotation matrix to intrinsic euler angles as radians.

        Rotation order of eulers must be given as 'XYZ' in any order"""
        if order.upper() == 'XYZ': return fromMatToXYZ(mat)
        if order.upper() == 'XZY': return fromMatToXZY(mat)
        if order.upper() == 'YXZ': return fromMatToYXZ(mat)
        if order.upper() == 'YZX': return fromMatToYZX(mat)
        if order.upper() == 'ZXY': return fromMatToZXY(mat)
        if order.upper() == 'ZYX': return fromMatToZYX(mat)
        raise ValueError(f'given order "{order}" is invalid. Order must be "XYZ" in any order')


def fromMatToXZY(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(mat[1,2], mat[1,1]),
        math.atan2(mat[2,0], mat[0,0]),
        math.atan2(-mat[1,0], math.sqrt(1 - mat[1,0]**2)),
    )

def fromMatToXYZ(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(-mat[2,1], mat[2,2]),
        math.atan2(mat[2,0], math.sqrt(1 - mat[2,0]**2)),
        math.atan2(-mat[1,0], mat[0,0]),
    )

def fromMatToYXZ(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(-mat[2,1], math.sqrt(1 - mat[2,1]**2)),
        math.atan2(mat[2,0], mat[2,2]),
        math.atan2(mat[0,1], mat[1,1]),
    )

def fromMatToYZX(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(-mat[2,1], mat[1,1]),
        math.atan2(-mat[0,2], mat[0,0]),
        math.atan2(mat[0,1], math.sqrt(1 - mat[0,1]**2)),
    )

def fromMatToZYX(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(mat[1,2], mat[2,2]),
        math.atan2(-mat[0,2], math.sqrt(1 - mat[0,2]**2)),
        math.atan2(mat[0,1], mat[0,0]),
    )

def fromMatToZXY(mat:glm.mat3) -> glm.vec3:
    return glm.vec3(
        math.atan2(mat[1,2], math.sqrt(1 - mat[1,2]**2)),
        math.atan2(-mat[0,2], mat[2,2]),
        math.atan2(-mat[1,0], mat[1,1]),
    )
