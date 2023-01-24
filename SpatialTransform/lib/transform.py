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
        """Name of the transform."""
        return self._Name

    @Name.setter
    def Name(self, value: str) -> None:
        self._Name = value

    @property
    def SpaceLocal(self) -> glm.mat4:
        """Transform space without respect to its parent."""
        if self.__isOutdatedLocal:
            self._SpaceLocal = glm.translate(self._PositionLocal)
            self._SpaceLocal = glm.scale(self._SpaceLocal, self._ScaleLocal)
            self._SpaceLocal = self._SpaceLocal * glm.mat4_cast(self._RotationLocal)
            self.__isOutdatedLocal = False
        return glm.mat4(self._SpaceLocal)

    @property
    def SpaceWorld(self) -> glm.mat4:
        """Space of the transform with respect to its parent."""
        return (self._Parent.SpaceWorld if self._Parent else glm.mat4()) * self.SpaceLocal

    @property
    def SpaceWorldInverse(self) -> glm.mat4:
        """Space of the transform with respect to its parent. Projects items to the local space."""
        return glm.inverse(self.SpaceWorld)

    @property
    def PositionLocal(self) -> glm.vec3:
        """Local position of the space."""
        return glm.vec3(self._PositionLocal)

    @PositionLocal.setter
    def PositionLocal(self, value: glm.vec3) -> None:
        self._PositionLocal = glm.vec3(value)
        self.__isOutdatedLocal = True

    @property
    def PositionWorld(self) -> glm.vec3:
        """World position of this space."""
        parentSpace = self._Parent.SpaceWorld if self._Parent else glm.mat4()
        return parentSpace * self._PositionLocal

    @PositionWorld.setter
    def PositionWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self._Parent.SpaceWorldInverse if self._Parent else glm.mat4()
        self._PositionLocal = parentSpaceInverse * value

    @property
    def RotationLocal(self) -> glm.quat:
        """Local rotation of this space."""
        return glm.quat(self._RotationLocal)

    @RotationLocal.setter
    def RotationLocal(self, value: glm.quat) -> None:
        self._RotationLocal = glm.quat(value)
        self.__isOutdatedLocal = True

    @property
    def RotationWorld(self) -> glm.quat:
        """World rotation of this space."""
        parentSpace = self._Parent.RotationWorld if self._Parent else glm.quat()
        return parentSpace * self._RotationLocal

    @RotationWorld.setter
    def RotationWorld(self, value: glm.quat) -> None:
        parentSpaceInverse = self._Parent.RotationWorldInverse if self._Parent else glm.quat()
        self._RotationLocal = parentSpaceInverse * value

    @property
    def RotationWorldInverse(self) -> glm.quat:
        """World inverse rotation of this space."""
        return glm.inverse(self.RotationWorld)

    @property
    def ScaleLocal(self) -> glm.vec3:
        """Local scale of the space."""
        return glm.vec3(self._ScaleLocal)

    @ScaleLocal.setter
    def ScaleLocal(self, value: glm.vec3) -> None:
        self._ScaleLocal = glm.vec3(value)
        self.__isOutdatedLocal = True

    @property
    def ScaleWorld(self) -> glm.vec3:
        """World scale of the space."""
        parentSpace = self._Parent.ScaleWorld if self._Parent else glm.vec3(1)
        return parentSpace * self._ScaleLocal

    @ScaleWorld.setter
    def ScaleWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self._Parent.ScaleWorldInverse if self._Parent else glm.vec3(1)
        self._ScaleLocal = parentSpaceInverse * value

    @property
    def ScaleWorldInverse(self) -> glm.vec3:
        """World inverse scale of the space."""
        return (1.0 / self.ScaleWorld)

    @property
    def ForwardLocal(self) -> glm.vec3:
        """Current local rotation of the Z-axis."""
        return self._RotationLocal * (0, 0, -1)

    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current rotation of the Z-axis in world space."""
        return (self.RotationWorld * (0, 0, -1, 0)).xyz

    @property
    def RightLocal(self) -> glm.vec3:
        """Current local rotation of the X-axis."""
        return self._RotationLocal * (1, 0, 0)

    @property
    def RightWorld(self) -> glm.vec3:
        """Current rotation of the X-axis in world space."""
        return (self.RotationWorld * (1, 0, 0, 0)).xyz

    @property
    def UpLocal(self) -> glm.vec3:
        """Current local rotation of the Y-axis."""
        return self._RotationLocal * (0, 1, 0)

    @property
    def UpWorld(self) -> glm.vec3:
        """Current rotation of the Y-axis in world space."""
        return (self.RotationWorld * (0, 1, 0, 0)).xyz

    @property
    def Parent(self) -> "Transform":
        """Transform where this one aligns in repsect to it."""
        return self._Parent

    @property
    def Children(self) -> list["Transform"]:
        """Attachted transforms."""
        return self._Children

    def __init__(self, name: str = None, position: glm.vec3 = glm.vec3(), rotation: glm.quat = glm.quat(), scale: glm.vec3 = glm.vec3(1)) -> None:
        """Creates a new transform. Parameters are considerd as local space"""
        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._Parent: "Transform" = None
        self._Children: list["Transform"] = []

        self._PositionLocal = glm.vec3(position)
        self._ScaleLocal = glm.vec3(scale)
        self._RotationLocal = glm.quat(rotation)
        self.__isOutdatedLocal = True

    def __repr__(self) -> str:
        return (f"{self._Name}")

    def __str__(self) -> str:
        return (f"Name: {self._Name}"
                + f"\nPos: {self._PositionLocal}"
                + f"\nRot: {self.RotationLocal}"
                + f"\nScale: {self._ScaleLocal}"
                + f"\nChildren: {len(self._Children)}"
                )

    def reset(self, recursive: bool = False) -> "Transform":
        """Resets the whole transform to pos: (0,0,0) scale: (1,1,1) and no rotation."""
        self._SpaceLocal = glm.mat4()
        self._PositionLocal = glm.vec3(0)
        self._RotationLocal = glm.quat()
        self._ScaleLocal = glm.vec3(1)
        if recursive:
            for child in self._Children:
                child.reset(recursive=True)
        return self

    def pointToWorld(self, point: glm.vec3) -> glm.vec3:
        """Transforms a given point in this local space to world space."""
        return self.SpaceWorld * point

    def pointToLocal(self, point: glm.vec3) -> glm.vec3:
        """Transforms a given point in world space to this local space."""
        return self.SpaceWorldInverse * point

    def directionToWorld(self, direction: glm.vec3) -> glm.vec3:
        """Transforms a given direction in this local space to world space."""
        return self.RotationWorld * direction

    def directionToLocal(self, direction: glm.vec3) -> glm.vec3:
        """Transforms a given direction in world space to this local space."""
        return self.RotationWorldInverse * direction

    def getEuler(self, order: str = 'ZXY', extrinsic: bool = True) -> glm.vec3:
        """Returns the current Rotation as euler angles in the given order.

        If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        return glm.degrees(Euler.fromQuatTo(self.RotationLocal, order, extrinsic))

    def setEuler(self, degrees: glm.vec3, order: str = 'ZXY', extrinsic: bool = True) -> "Transform":
        """Converts the given euler anlges to quaternion and sets the rotation property.

        If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        self.RotationLocal = Euler.toQuatFrom(glm.radians(degrees), order, extrinsic)
        return self

    def lookAtLocal(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction. Direction is considered as local space.

        Returns the transform itself."""
        direction = glm.normalize(direction)
        dirDot = abs(glm.dot(direction, (0, 1, 0)))
        upAxis = up if dirDot < 0.999 else glm.vec3(1, 0, 0)

        self._RotationLocal = glm.quatLookAtRH(direction, upAxis)
        self.__isOutdatedLocal = True
        return self

    def lookAtWorld(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.  Direction is considered as world space.

        Returns the transform itself."""
        parentWorldRotationInverse = (self._Parent.RotationWorldInverse if self._Parent else glm.mat4())
        direction = parentWorldRotationInverse * direction

        return self.lookAtLocal(direction, up)

    def attach(self, *nodes: "Transform", keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Attaches the given transforms to this one as a child.

        If keep***** is true, the given transform will be modified to keep its spatial algiment in world space.

        Returns the transform itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError('Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be parent of itself')
            if node in self._Children: return self

            # detach
            if node._Parent is not None:
                node._Parent.detach(node, keepPosition, keepRotation)

            # attatch
            self._Children.append(node)
            node._Parent = self

            # correct Rotation
            if keepPosition: node.PositionLocal = self.SpaceWorldInverse * node.PositionLocal
            if keepRotation: node.RotationLocal = self.RotationWorldInverse * node.RotationLocal
            if keepScale: node.ScaleLocal = self.ScaleWorldInverse * node.ScaleLocal
        return self

    def detach(self, node: "Transform", keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Detachs the given child transform.

        If keep***** is true, the given transform will be modified to keep its spatial algiment in world space.

        Returns the transform itself."""
        # validate given joint
        if node is None: raise ValueError('Given joint value is None')
        if node is self: raise ValueError(f'Joint "{self.Name}" cannot be detachd from itself')
        if node not in self._Children: return self

        # correct properties
        if keepPosition: node.PositionLocal = self.SpaceWorld * node.PositionLocal
        if keepRotation: node.RotationLocal = self.RotationWorld * node.RotationLocal
        if keepScale: node.ScaleLocal = self.ScaleWorld * node.ScaleLocal

        # detach
        self._Children.remove(node)
        node._Parent = None
        return self

    def clearParent(self, keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Detaches/detachs itself from the parent.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        if self._Parent is not None: self._Parent.detach(self, keepPosition, keepRotation, keepScale)
        return self

    def clearChildren(self, keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """detachs all children of this transform.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        for i in reversed(range(len(self._Children))):
            self.detach(self._Children[i], keepPosition, keepRotation, keepScale)
        return self

    def applyPosition(self, position: glm.vec3 = None, recursive: bool = False) -> "Transform":
        """Changes the position of this transform and updates its children to keep them spatial unchanged.

        If position is NOT set, the transform resets its own position to (0, 0, 0).

        If position IS set, the given position is added to the current position.

        Returns itself."""
        # define positional change
        change = -self.PositionLocal if position is None else position
        changeInverse = glm.inverse(self.RotationLocal) * ((1.0 / self.ScaleLocal) * -change)

        # apply changes to itself
        self.PositionLocal += change

        # apply changes to children
        for child in self.Children:
            child.PositionLocal += changeInverse

            # may do it recursively
            if recursive: child.applyRotation(position, recursive=True)

        return self

    def applyRotation(self, rotation: glm.quat = None, recursive: bool = False) -> "Transform":
        """Changes the rotation of this transform and updates its children to keep them spatial unchanged.

        If rotation is NOT set, the transform resets its own rotation to (1, 0, 0, 0).

        If rotation IS set, the given rotation is added to the current rotation.

        if includeLocal is true, the transforms also rotates its own local position.

        Returns itself."""
        # define rotational change
        change = glm.inverse(self.RotationLocal) if rotation is None else rotation
        changeInverse = glm.inverse(change)

        # apply changes to itself
        self.RotationLocal = self.RotationLocal * change

        # apply changes to children
        for child in self.Children:
            child.PositionLocal = changeInverse * child.PositionLocal
            child.RotationLocal = changeInverse * child.RotationLocal

            # may do it recursively
            if recursive: child.applyRotation(rotation, recursive=True)

        return self

    def appyScale(self, scale: glm.vec3 = None, recursive: bool = False) -> "Transform":
        """Changes the scale of the transform and updates its children to keep them spatial unchanged.

        If scale is NOT set, the transform resets its own scale to (1, 1, 1).

        If scale IS set, the given scale is added to the current scale.

        if includeLocal is true, the transforms also scales its own local position.

        Returns itself."""
        # define change in scale
        change = (1.0 / self.ScaleLocal) if scale is None else scale
        changeInverse = (1.0 / change)

        # apply changes to itself
        self.ScaleLocal *= change

        # keep space for children
        for child in self.Children:
            child.PositionLocal *= changeInverse
            child.ScaleLocal *= changeInverse

            # may do it recursively
            if recursive: child.appyScale(scale, recursive=True)

        return self

    def layout(self, index: int = 0, depth: int = 0) -> list[tuple["Transform", int, int]]:
        """Returns the hierarchy, inclunding this transform, in order of 'depth first' with their index and depth."""
        result = [[self, index, depth]]
        for child in self.Children:
            result.extend(child.layout(result[-1][1] + 1, depth + 1))
        return result

    def printTree(self, markerStr="+- ", levelMarkers=[]) -> None:
        # src: https://simonhessner.de/python-3-recursively-print-structured-tree-including-hierarchy-markers-using-depth-first-search/
        """
        Recursive function that prints the hierarchical structure of a tree including markers that indicate parent-child relationships between nodes.

        Parameters:
        - root: Node instance, possibly containing children Nodes
        - markerStr: String to print in front of each node  ("+- " by default)
        - levelMarkers: Internally used by recursion to indicate where to
                        print markers and connections (see explanations below)
        """

        def mapper(draw): return connectionStr if draw else emptyStr
        emptyStr = " " * len(markerStr)
        connectionStr = "|" + emptyStr[:-1]
        level = len(levelMarkers)   # recursion level
        markers = "".join(map(mapper, levelMarkers[:-1]))
        markers += markerStr if level > 0 else ""
        print(f"{markers}{self.Name}")

        for i, child in enumerate(self.Children):
            isLast = i == len(self.Children) - 1
            child.printTree(markerStr, [*levelMarkers, not isLast])

    def filter(self, pattern: str, isEqual: bool = False, caseSensitive: bool = False) -> list["Transform"]:
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

    def filterRegex(self, pattern: str) -> list["Transform"]:
        """Tries to find transforms that matches the pattern in their name name."""
        result = []

        if re.match(pattern, self.Name) is not None:
            result.append(self)
        for child in self._Children:
            result.extend(child.filter(pattern))

        return result
