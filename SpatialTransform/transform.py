import glm
import random
import string
from .euler import Euler


class Transform:
    """Spatial definition of an linear space with position, rotation and scale.

    Space is defined as Y:up and right handed and positive rotations are counter clockwise."""

    @property
    def Name(self) -> str:
        """Name of this transform. Does not affect anything."""
        return self._Name
    @Name.setter
    def Name(self, value:str) -> None:
        self._Name = value


    @property
    def SpaceLocal(self) -> glm.mat4:
        """Space of this transform without respect to its parent."""
        if self.__isOutdatedLocal:
            self._SpaceLocal = glm.translate(self._Position)
            self._SpaceLocal = glm.scale(self._SpaceLocal, self._Scale)
            self._SpaceLocal = self._SpaceLocal * glm.mat4_cast(self._Orientation)
            self.__isOutdatedLocal = False
        return glm.mat4(self._SpaceLocal)
    @SpaceLocal.setter
    def SpaceLocal(self, value:glm.mat4) -> None:
        self._SpaceLocal = value
        glm.decompose(value,
            self._Scale,
            self._Orientation,
            self._Position,
            glm.vec3(),
            glm.vec4())
        self.__isOutdatedLocal = False


    @property
    def SpaceWorld(self) -> glm.mat4:
        """Space of this with respect to its parent"""
        return (self._Parent.SpaceWorld if self._Parent else glm.mat4()) * self.SpaceLocal
    @property
    def SpaceWorldInverse(self) -> glm.mat4:
        """Space of this transform with respect to its parent. Projects items to this local space."""
        return glm.inverse(self.SpaceWorld)


    @property
    def Position(self) -> glm.vec3:
        """Local offset of the space."""
        return glm.vec3(self._Position)
    @Position.setter
    def Position(self, value:glm.vec3) -> None:
        self._Position = glm.vec3(value)
        self.__isOutdatedLocal = True


    @property
    def Orientation(self) -> glm.quat:
        """Local orientation of this space."""
        return glm.quat(self._Orientation)
    @Orientation.setter
    def Orientation(self, value:glm.quat) -> None:
        self._Orientation = glm.quat(value)
        self.__isOutdatedLocal = True


    @property
    def Scale(self) -> glm.vec3:
        """Local scale of the space."""
        return glm.vec3(self._Scale)
    @Scale.setter
    def Scale(self, value:glm.vec3) -> None:
        self._Scale = glm.vec3(value)
        self.__isOutdatedLocal = True


    @property
    def ForwardLocal(self) -> glm.vec3:
        """Current local orientation of the Z-Axis"""
        return self._Orientation * (0,0,1)
    @ForwardLocal.setter
    def ForwardLocal(self, direction:glm.vec3) -> None:
        self._Orientation = glm.quatLookAtLH(glm.normalize(direction), (0,1,0))
        self.__isOutdatedLocal = True
    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current orientation of the Z-Axis in world space"""
        return glm.quat(self.SpaceWorld) * (0,0,1)
    @ForwardWorld.setter
    def ForwardWorld(self, direction:glm.vec3) -> None:
        self.ForwardLocal = glm.quat(self.SpaceWorldInverse) * direction
        self.__isOutdatedLocal = True

    @property
    def RightLocal(self) -> glm.vec3:
        """Current local orientation of the X-Axis"""
        return self._Orientation * (1,0,0)
    @property
    def RightWorld(self) -> glm.vec3:
        """Current orientation of the X-Axis in world space"""
        return glm.quat(self.SpaceWorld) * (1,0,0)


    @property
    def UpLocal(self) -> glm.vec3:
        """Current local orientation of the Y-Axis"""
        return self._Orientation * (0,1,0)
    @property
    def UpWorld(self) -> glm.vec3:
        """Current orientation of the Y-Axis in world space"""
        return glm.quat(self.SpaceWorld) * (0,1,0)


    @property
    def Parent(self) -> object:
        """Transform where this one aligns in repsect to it."""
        return self._Parent
    @property
    def Children(self) -> list[object]:
        """Attachted transforms."""
        return self._Children


    def __init__(self, name:str = None, position:glm.vec3 = glm.vec3(), orientation:glm.quat = glm.quat(), scale:glm.vec3 = glm.vec3(1)) -> None:
        """Creates a new transform. Parameters are considerd as local space"""
        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._SpaceLocal = glm.mat4()
        self._Parent = None
        self._Children = []

        self._Position = glm.vec3(position)
        self._Scale = glm.vec3(scale)
        self._Orientation = glm.quat(orientation)
        self.__isOutdatedLocal = True

    def __repr__(self) -> str:
        return (f"Name: {self._Name}")

    def __str__(self) -> str:
        return (f"Name: {self._Name}"
            + f"\nPos: {self._Position}"
            + f"\nRot: {self.Orientation}"
            + f"\nScale: {self._Scale}"
            + f"\nChildren: {len(self._Children)}"
        )

    def pointToWorld(self, point:glm.vec3) -> glm.vec3:
        """Transforms a given point in this local space to world space"""
        return self.SpaceWorld * point

    def pointToLocal(self, point:glm.vec3) -> glm.vec3:
        """Transforms a given point in world space to this local space"""
        return self.SpaceWorldInverse * point


    def directionToWorld(self, direction:glm.vec3) -> glm.vec3:
        """Transforms a given direction in this local space to world space"""
        return glm.quat(self.SpaceWorld) * direction

    def directionToLocal(self, direction:glm.vec3) -> glm.vec3:
        """Transforms a given direction in world space to this local space"""
        return glm.quat(self.SpaceWorldInverse) * direction


    def GetEuler(self, order:str = 'ZXY') -> glm.vec3:
        """Returns the current orientation as euler angles in the given order.

        The angles are in degrees and intrinsic."""
        return glm.degrees(Euler.fromQuatTo(self.Orientation, order))

    def SetEuler(self, degrees:glm.vec3, order:str = 'ZXY', intrinsic = True) -> None:
        self.Orientation = Euler.toQuatFrom(glm.radians(degrees), order, intrinsic)


    def remove(self, node:object, keepPosition:bool = False, keepOrientation:bool = False) -> None:
        """Removes the given child transform.

        If keep***** is true, the given transform will be modified to keep its world property."""
        # validate given joint
        if node is None: raise ValueError(f'Given joint value is None')
        if node is self: raise ValueError(f'Joint "{self.Name}" cannot be removed from itself')

        # correct properties
        if keepPosition: node.Position = node.pointToWorld((0,0,0))
        if keepOrientation: node.Orientation = node.Orientation * self.Orientation

        # remove
        self._Children.remove(node)
        node._Parent = None

    def append(self, node:object, keepPosition:bool = False, keepOrientation:bool = False) -> None:
        """Attaches the given transform to this one as a child.

        If keep***** is true, the given transform will be modified to keep its world property."""
        # validate given joint
        if node is None: raise ValueError(f'Given joint value is None')
        if node is self: raise ValueError(f'Joint "{self.Name}" cannot be parent of itself')

        # remove
        if node._Parent is not None:
            node._Parent.remove(node, keepPosition, keepOrientation)

        # attatch
        self._Children.append(node)
        node._Parent = self

        # correct orientation
        if keepPosition: node.Position = self.pointToLocal(node.Position)
        if keepOrientation: node.Orientation = node.Orientation * (glm.inverse(self.Orientation))

    def applyPosition(self, position:glm.vec3 = None, recursive:bool = False) -> None:
        """Changes the position of this transform and updates its children to keep them spatial unchanged.
        Will update the position of this transform and postions of its children.

        If no position is given, the transform resets its own position to (0,0,0)

        If a position is given, the position is added to this transform"""
        # define position change
        change = self.Position if position is None else -position

        # apply change
        self.Position = self.Position - position
        for child in self.Children:
            child.Position = child.Position + position

            # propagatte it recursively
            if recursive: child.applyPosition(position, recursive)

    def applyRotation(self, rotation:glm.quat = None, recursive:bool = False) -> None:
        """Changes the rotation of this transform and updates its children to keep them spatial unchanged.
        Will update the orientation of this transform and postion and orientation of its children.

        If no rotation is given, the transform resets its own rotation to none

        If a rotation is given, the rotation is added to this transform"""
        # define rotation change
        change = self.Orientation if rotation is None else glm.inverse(rotation)

        # apply change
        self.Orientation = self.Orientation * glm.inverse(change)
        for child in self.Children:
            child.Position = change * child.Position
            child.Orientation = change * child.Orientation

            # propagatte it recursively
            if recursive: child.applyRotation(rotation, recursive)
