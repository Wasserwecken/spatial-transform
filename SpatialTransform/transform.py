import re
import glm
import random
import string
from .euler import Euler
class Transform:
    """Spatial definition of an linear space with position, rotation and scale.

    Space is defined as right handed where Y+:up and X+:right and Z-:forward. Positive rotations are counter clockwise."""

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
            self._SpaceLocal = glm.scale(self._SpaceLocal, self._ScaleLocal)
            self._SpaceLocal = self._SpaceLocal * glm.mat4_cast(self._RotationLocal)
            self.__isOutdatedLocal = False
        return glm.mat4(self._SpaceLocal)
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
    def RotationLocal(self) -> glm.quat:
        """Local rotation of this space."""
        return glm.quat(self._RotationLocal)
    @RotationLocal.setter
    def RotationLocal(self, value:glm.quat) -> None:
        self._RotationLocal = glm.quat(value)
        self.__isOutdatedLocal = True
    @property
    def RotationWorld(self) -> glm.quat:
        """World rotation of this space."""
        return (self._Parent.RotationWorld if self._Parent else glm.quat()) * self._RotationLocal
    @RotationWorld.setter
    def RotationWorld(self, value:glm.quat) -> None:
        self._RotationLocal = self._Parent.RotationWorldInverse if self._Parent else glm.quat() * value
    @property
    def RotationWorldInverse(self) -> glm.quat:
        """World inverse rotation of this space."""
        return glm.inverse(self._Parent.RotationWorld if self._Parent else glm.quat()) * self._RotationLocal

    @property
    def ScaleLocal(self) -> glm.vec3:
        """Local scale of the space."""
        return glm.vec3(self._ScaleLocal)
    @ScaleLocal.setter
    def ScaleLocal(self, value:glm.vec3) -> None:
        self._ScaleLocal = glm.vec3(value)
        self.__isOutdatedLocal = True
    @property
    def ScaleWorld(self) -> glm.vec3:
        """World scale of the space."""
        return (self._Parent.ScaleWorld if self._Parent else glm.quat()) * self._ScaleLocal
    @ScaleWorld.setter
    def ScaleWorld(self, value:glm.vec3) -> None:
        self._ScaleLocal = self._Parent.ScaleWorldInverse if self._Parent else glm.vec3(1) * value
    @property
    def ScaleWorldInverse(self) -> glm.vec3:
        """World inverse scale of the space."""
        return (glm.div(1, self._Parent.ScaleWorld) if self._Parent else glm.vec3(1)) * self._ScaleLocal


    @property
    def ForwardLocal(self) -> glm.vec3:
        """Current local Rotation of the Z-Axis"""
        return self._RotationLocal * (0,0,-1)
    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current Rotation of the Z-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (0,0,-1,0)).xyz

    @property
    def RightLocal(self) -> glm.vec3:
        """Current local Rotation of the X-Axis"""
        return self._RotationLocal * (1,0,0)
    @property
    def RightWorld(self) -> glm.vec3:
        """Current Rotation of the X-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (1,0,0,0)).xyz


    @property
    def UpLocal(self) -> glm.vec3:
        """Current local Rotation of the Y-Axis"""
        return self._RotationLocal * (0,1,0)
    @property
    def UpWorld(self) -> glm.vec3:
        """Current Rotation of the Y-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (0,1,0,0)).xyz


    @property
    def Parent(self) -> "Transform":
        """Transform where this one aligns in repsect to it."""
        return self._Parent
    @property
    def Children(self) -> list["Transform"]:
        """Attachted transforms."""
        return self._Children


    def __init__(self, name:str = None, position:glm.vec3 = glm.vec3(), rotation:glm.quat = glm.quat(), scale:glm.vec3 = glm.vec3(1)) -> None:
        """Creates a new transform. Parameters are considerd as local space"""
        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._Parent:"Transform" = None
        self._Children:list["Transform"] = []

        self._Position = glm.vec3(position)
        self._ScaleLocal = glm.vec3(scale)
        self._RotationLocal = glm.quat(rotation)
        self.__isOutdatedLocal = True

    def __repr__(self) -> str:
        return (f"{self._Name}")

    def __str__(self) -> str:
        return (f"Name: {self._Name}"
            + f"\nPos: {self._Position}"
            + f"\nRot: {self.RotationLocal}"
            + f"\nScale: {self._ScaleLocal}"
            + f"\nChildren: {len(self._Children)}"
        )

    def reset(self, recursive:bool = False) -> "Transform":
        """Resets the whole transform to pos: (0,0,0) scale: (1,1,1) and no rotation"""
        self.SpaceLocal = glm.mat4()
        if recursive:
            for child in self._Children:
                child.reset(recursive=True)
        return self

    def resetPosition(self, recursive:bool = False) -> "Transform":
        """Resets the position to 0,0,0"""
        self.Position = (0,0,0)
        if recursive:
            for child in self._Children:
                child.resetPosition(recursive=True)
        return self

    def resetRotation(self, recursive:bool = False) -> "Transform":
        """Resets rotation"""
        self.RotationLocal = glm.quat()
        if recursive:
            for child in self._Children:
                child.resetRotation(recursive=True)
        return self

    def resetScale(self, recursive:bool = False) -> "Transform":
        """Resets scale to 1,1,1"""
        self.ScaleLocal = (1,1,1)
        if recursive:
            for child in self._Children:
                child.resetScale(recursive=True)
        return self

    def pointToWorld(self, point:glm.vec3 = glm.vec3(0)) -> glm.vec3:
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


    def getEuler(self, order:str = 'ZXY', extrinsic:bool = True) -> glm.vec3:
        """Returns the current Rotation as euler angles in the given order.

        If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        return glm.degrees(Euler.fromQuatTo(self.RotationLocal, order))

    def setEuler(self, degrees:glm.vec3, order:str = 'ZXY', extrinsic:bool = True) -> "Transform":
        """Converts the given euler anlges to quaternion and sets the rotation property.

        If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        self.RotationLocal = Euler.toQuatFrom(glm.radians(degrees), order, extrinsic)


    def lookAtLocal(self, direction:glm.vec3, up:glm.vec3 = glm.vec3(0,1,0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction. Direction is considered as local space. Returns the transform itself."""
        direction = glm.normalize(direction)
        dirDot = abs(glm.dot(direction, (0,1,0)))
        self._RotationLocal = glm.quatLookAtRH(direction, up if dirDot < 0.999 else glm.vec3(1,0,0))
        self.__isOutdatedLocal = True
        return self

    def lookAtWorld(self, direction:glm.vec3, up:glm.vec3 = glm.vec3(0,1,0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.  Direction is considered as world space Returns the transform itself."""
        parentSpace = (self._Parent.SpaceWorld if self._Parent else glm.mat4())
        self.lookAtLocal(glm.inverse(parentSpace) * direction, up)
        return self


    def attach(self, *nodes:"Transform", keepPosition:bool = True, keepRotation:bool = True, keepScale:bool = True) -> "Transform":
        """Attaches the given transforms to this one as a child.

        If keep***** is true, the given transform will be modified to keep its spatial algiment in world space.

        Returns the transform itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError(f'Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be parent of itself')

            # detach
            if node._Parent is not None:
                node._Parent.detach(node, keepPosition, keepRotation)

            # attatch
            self._Children.append(node)
            node._Parent = self

            # correct Rotation
            if keepPosition: node.Position = self.SpaceWorldInverse * node.Position
            if keepRotation: node.RotationLocal = self.RotationWorldInverse * node.RotationLocal
            if keepScale: node.ScaleLocal = self.ScaleWorldInverse * node.ScaleLocal
        return self

    def detach(self, node:"Transform", keepPosition:bool = True, keepRotation:bool = True, keepScale:bool = True) -> "Transform":
        """Detachs the given child transform.

        If keep***** is true, the given transform will be modified to keep its spatial algiment in world space.

        Returns the transform itself."""
        # validate given joint
        if node is None: raise ValueError(f'Given joint value is None')
        if node is self: raise ValueError(f'Joint "{self.Name}" cannot be detachd from itself')

        # correct properties
        if keepPosition: node.Position = self.SpaceWorld * node.Position
        if keepRotation: node.RotationLocal = self.RotationWorld * node.RotationLocal
        if keepScale: node.ScaleLocal = self.ScaleWorld * node.ScaleLocal

        # detach
        self._Children.remove(node)
        node._Parent = None
        return self

    def clearParent(self, keepPosition:bool = True, keepRotation:bool = True, keepScale:bool = True) -> "Transform":
        """Detaches/detachs itself from the parent.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        if self._Parent is not None: self._Parent.detach(self, keepPosition, keepRotation, keepScale)
        return self

    def clearChildren(self, keepPosition:bool = True, keepRotation:bool = True, keepScale:bool = True) -> "Transform":
        """detachs all children of this transform.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        for child in self.Children:
            self.detach(child, keepPosition, keepRotation, keepScale)
        return self


    def applyPosition(self, position:glm.vec3 = glm.vec3()) -> "Transform":
        """Resets the position of this transform for (0,0,0) and updates its children to keep them spatial unchanged.

        If a position is given, the position is before values are modified.

        Returns itself."""
        self.Position += position

        for child in self.Children:
            child.Position = self.Position + child.Position

        self.Position = glm.vec3()
        return self

    def applyRotation(self, rotation:glm.quat = glm.quat(), recursive:bool = False, includeLocal:bool = False) -> "Transform":
        """Resets the rotation of this transform for (0,0,-1) and updates its children to keep them spatial unchanged.

        If rotation is set, the transform is rotated before values are modified.

        if includeLocal is true, the transforms also rotates its own local position.

        Returns itself."""
        # define rotation change
        self.RotationLocal *= rotation
        if includeLocal:
            self.Position = self.RotationLocal * self.Position

        for child in self.Children:
            child.Position = self.RotationLocal * child.Position
            child.RotationLocal = self.RotationLocal * child.RotationLocal

            # may do it recursively
            if recursive: child.applyRotation(recursive=True, includeLocal=False)

        self.RotationLocal = glm.quat()
        return self

    def appyScale(self, scale:glm.vec3 = glm.vec3(1), recursive:bool = False, includeLocal:bool = False) -> "Transform":
        """Resets the scale of the transform to (1,1,1) and updates its children to keep them spatial unchanged.

        if scale is set, the transform is scaled before values are modified.

        if includeLocal is true, the transforms also scales its own local position.

        Returns itself."""
        self.ScaleLocal *= scale
        if includeLocal:
            self.Position *= self.ScaleLocal

        # keep space for children
        for child in self.Children:
            child.Position *= self.ScaleLocal
            child.ScaleLocal *= self.ScaleLocal

            # may do it recursively
            if recursive: child.appyScale(recursive=True, includeLocal=False)

        self.ScaleLocal = glm.vec3(1)
        return self


    def layout(self, index:int = 0, depth:int = 0) -> list[tuple["Transform", int, int]]:
        """Returns the hierarchy, inclunding this transform, in order of 'depth first' with their index and depth"""
        result = [[self, index, depth]]
        for child in self.Children:
            result.extend(child.layout(result[-1][1] + 1, depth + 1))
        return result

    def printTree(self, markerStr="+- ", levelMarkers=[]) -> None:
        # src: https://simonhessner.de/python-3-recursively-print-structured-tree-including-hierarchy-markers-using-depth-first-search/
        """
        Recursive function that prints the hierarchical structure of a tree including markers that indicate
        parent-child relationships between nodes.

        Parameters:
        - root: Node instance, possibly containing children Nodes
        - markerStr: String to print in front of each node  ("+- " by default)
        - levelMarkers: Internally used by recursion to indicate where to
                        print markers and connections (see explanations below)
        """

        emptyStr = " "*len(markerStr)
        connectionStr = "|" + emptyStr[:-1]
        level = len(levelMarkers)   # recursion level
        mapper = lambda draw: connectionStr if draw else emptyStr
        markers = "".join(map(mapper, levelMarkers[:-1]))
        markers += markerStr if level > 0 else ""
        print(f"{markers}{self.Name}")

        for i, child in enumerate(self.Children):
            isLast = i == len(self.Children) - 1
            child.printTree(markerStr, [*levelMarkers, not isLast])


    def filter(self, pattern:str, isEqual:bool = False, caseSensitive:bool = False) -> list["Transform"]:
        """Tries to find transforms that matches the pattern in their name name.

        If isEqual is true, the name has to be equal to the pattern. Otherwise the pattern must only appear anywhere in the name."""
        result = []

        selfname = self.Name if caseSensitive else self.Name.lower()
        if not caseSensitive: pattern = pattern.lower()

        if (isEqual and pattern == selfname) or (not isEqual and pattern in selfname):
            result.append(self)
        for child in self._Children:
            result.extend(child.filter(pattern, isEqual, caseSensitive))

        return result

    def filterRegex(self, pattern:str) -> list["Transform"]:
        """Tries to find transforms that matches the pattern in their name name."""
        result = []

        if re.match(pattern, self.Name) is not None:
            result.append(self)
        for child in self._Children:
            result.extend(child.filter(pattern))

        return result
