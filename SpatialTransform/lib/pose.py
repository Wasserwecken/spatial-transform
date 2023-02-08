import glm
from .euler import Euler


class Pose:
    """Spatial definition of an linear space with position, rotation and scale.
    - ONLY provides properties and methods for local space.
    - There is no parent child relation between poses
    - Space is defined as right handed where -> Y+ is up, and X+ is right and Z- is forward.
    - Positive rotations are counter clockwise."""

    @property
    def Space(self) -> glm.mat4:
        """Transform space with properties."""
        if self.__isOutdated:
            self._Space = glm.translate(self.Position)
            self._Space = glm.scale(self._Space, self.Scale)
            self._Space = self._Space * glm.mat4_cast(self.Rotation)
            self.__isOutdated = False
        return glm.mat4(self._Space)

    @property
    def SpaceInverse(self) -> glm.mat4:
        """Inverted transform space."""
        return glm.inverse(self.Space)

    @property
    def Position(self) -> glm.vec3:
        """Position of the space."""
        return glm.vec3(self._Position)

    @Position.setter
    def Position(self, value: glm.vec3) -> None:
        self._Position = glm.vec3(value)
        self.__isOutdated = True

    @property
    def Rotation(self) -> glm.quat:
        """Rotation of the space."""
        return glm.quat(self._Rotation)

    @Rotation.setter
    def Rotation(self, value: glm.quat) -> None:
        self._Rotation = glm.quat(value)
        self.__isOutdated = True

    @property
    def Scale(self) -> glm.vec3:
        """Scale of the space."""
        return glm.vec3(self._Scale)

    @Scale.setter
    def Scale(self, value: glm.vec3) -> None:
        self._Scale = glm.vec3(value)
        self.__isOutdated = True

    @property
    def Forward(self) -> glm.vec3:
        """Current alignment of the Z-axis."""
        return self.Rotation * (0, 0, -1)

    @property
    def Right(self) -> glm.vec3:
        """Current alignment of the X-axis."""
        return self.Rotation * (1, 0, 0)

    @property
    def Up(self) -> glm.vec3:
        """Current alignment of the Y-axis."""
        return self.Rotation * (0, 1, 0)

    def __init__(self, position: glm.vec3 = None, rotation: glm.quat = None, scale: glm.vec3 = None) -> None:
        """Creates a new pose."""

        self._Space = glm.mat4(1)
        self._Position = glm.vec3() if position is None else glm.vec3(position)
        self._Rotation = glm.quat() if rotation is None else glm.quat(rotation)
        self._Scale = glm.vec3(1) if scale is None else glm.vec3(scale)
        self.__isOutdated = True

    def __repr__(self) -> str:
        return (f"Pos: {self.Position}, Rot: {self.Rotation}, Scale: {self.Scale}")

    def __str__(self) -> str:
        return self.__repr__()

    def reset(self) -> "Pose":
        self.Position = glm.vec3(0)
        self.Rotation = glm.quat()
        self.Scale = glm.vec3(1)

    def getEuler(self, order: str = 'ZXY', extrinsic: bool = True) -> glm.vec3:
        """Returns the current Rotation as euler angles in the given order.
        - If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        return glm.degrees(Euler.fromQuatTo(self.Rotation, order, extrinsic))

    def setEuler(self, degrees: glm.vec3, order: str = 'ZXY', extrinsic: bool = True) -> "Pose":
        """Converts the given euler anlges to quaternion and sets the rotation property.
        - If extrinsic the rotation will be around the world axes, ignoring previous rotations.

        Returns itself."""
        self.Rotation = Euler.toQuatFrom(glm.radians(degrees), order, extrinsic)
        return self

    def addEuler(self, degrees: glm.vec3, order: str = 'ZXY', extrinsic: bool = True, last: bool = True) -> "Pose":
        """Adds an euler rotation to the current rotation.
        - If extrinsic the rotation will be around the world axes, ignoring previous rotations.
        - If last is True -> The rotation is added after the current rotation.

        Returns itself."""
        if last:
            self.Rotation = Euler.toQuatFrom(glm.radians(degrees), order, extrinsic) * self.Rotation
        else:
            self.Rotation = self.Rotation * Euler.toQuatFrom(glm.radians(degrees), order, extrinsic)

        return self

    def lookAt(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Pose":
        """Sets Rotation so the Z- axis aligns with the given direction.
        - Direction is considered as local space.

        Returns itself."""
        direction = glm.normalize(direction)
        dirDot = abs(glm.dot(direction, (0, 1, 0)))
        upAxis = up if dirDot < 0.999 else glm.vec3(1, 0, 0)
        self.Rotation = glm.quatLookAtRH(direction, upAxis)

        return self

    def duplicate(self) -> "Pose":
        """Returns a duplicate of this pose."""
        return Pose(self.Position, self.Rotation, self.Scale)
