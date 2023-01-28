import re
import glm
import random
import string
from .euler import Euler


class Transform:
    """Spatial definition of an linear space with position, rotation and scale.

    Space is defined as right handed where Y+:up and X+:right and Z-:forward.

    Positive rotations are counter clockwise."""

    @property
    def Name(self) -> str:
        """Name of the transform."""
        return self._Name

    @Name.setter
    def Name(self, value: str) -> None:
        self._Name = value

    @property
    def SpaceLocal(self) -> glm.mat4:
        """Transform space with local properties only."""
        if self.__isOutdatedLocal:
            self._SpaceLocal = glm.translate(self.PositionLocal)
            self._SpaceLocal = glm.scale(self._SpaceLocal, self.ScaleLocal)
            self._SpaceLocal = self._SpaceLocal * glm.mat4_cast(self.RotationLocal)
            self.__isOutdatedLocal = False
        return glm.mat4(self._SpaceLocal)

    @property
    def SpaceWorld(self) -> glm.mat4:
        """Transform space with respect to the parent."""
        return (self.Parent.SpaceWorld if self.Parent else glm.mat4()) * self.SpaceLocal

    @property
    def SpaceWorldInverse(self) -> glm.mat4:
        """Inverted transform space with respect to the parent."""
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
        """World position of the space."""
        parentSpace = self.Parent.SpaceWorld if self.Parent else glm.mat4()
        return parentSpace * self.PositionLocal

    @PositionWorld.setter
    def PositionWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self.Parent.SpaceWorldInverse if self.Parent else glm.mat4()
        self._PositionLocal = parentSpaceInverse * value

    @property
    def RotationLocal(self) -> glm.quat:
        """Local rotation of the space."""
        return glm.quat(self._RotationLocal)

    @RotationLocal.setter
    def RotationLocal(self, value: glm.quat) -> None:
        self._RotationLocal = glm.quat(value)
        self.__isOutdatedLocal = True

    @property
    def RotationWorld(self) -> glm.quat:
        """World rotation of the space."""
        parentSpace = self.Parent.RotationWorld if self.Parent else glm.quat()
        return parentSpace * self.RotationLocal

    @RotationWorld.setter
    def RotationWorld(self, value: glm.quat) -> None:
        parentSpaceInverse = self.Parent.RotationWorldInverse if self.Parent else glm.quat()
        self._RotationLocal = parentSpaceInverse * value

    @property
    def RotationWorldInverse(self) -> glm.quat:
        """Inverse world rotation of the space."""
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
        parentSpace = self.Parent.ScaleWorld if self.Parent else glm.vec3(1)
        return parentSpace * self.ScaleLocal

    @ScaleWorld.setter
    def ScaleWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self.Parent.ScaleWorldInverse if self.Parent else glm.vec3(1)
        self._ScaleLocal = parentSpaceInverse * value

    @property
    def ScaleWorldInverse(self) -> glm.vec3:
        """Inverse world scale of the space."""
        return (1.0 / self.ScaleWorld)

    @property
    def ForwardLocal(self) -> glm.vec3:
        """Current local rotation of the Z-axis."""
        return self.RotationLocal * (0, 0, -1)

    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current rotation of the Z-axis in world space."""
        return (self.RotationWorld * (0, 0, -1, 0)).xyz

    @property
    def RightLocal(self) -> glm.vec3:
        """Current local rotation of the X-axis."""
        return self.RotationLocal * (1, 0, 0)

    @property
    def RightWorld(self) -> glm.vec3:
        """Current rotation of the X-axis in world space."""
        return (self.RotationWorld * (1, 0, 0, 0)).xyz

    @property
    def UpLocal(self) -> glm.vec3:
        """Current local rotation of the Y-axis."""
        return self.RotationLocal * (0, 1, 0)

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
        """Attachted transforms. This transform builds the parent space for those children."""
        return self._Children

    def __init__(self, name: str = None, position: glm.vec3 = None, rotation: glm.quat = None, scale: glm.vec3 = None) -> None:
        """Creates a new transform. Parameters are considerd in local space."""
        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._Parent: "Transform" = None
        self._Children: list["Transform"] = []

        self._SpaceLocal = glm.mat4(1)
        self._PositionLocal = glm.vec3() if position is None else glm.vec3(position)
        self._RotationLocal = glm.quat() if rotation is None else glm.quat(rotation)
        self._ScaleLocal = glm.vec3(1) if scale is None else glm.vec3(scale)
        self.__isOutdatedLocal = True

    def __repr__(self) -> str:
        return (f"{self.Name}")

    def __str__(self) -> str:
        return (f"Name: {self.Name}"
                + f" Pos: {self.PositionLocal}"
                + f" Rot: {self.RotationLocal}"
                + f" Scale: {self.ScaleLocal}"
                + f" Children: {len(self.Children)}"
                )

    def reset(self, recursive: bool = False) -> "Transform":
        """Resets the transform to pos: (0,0,0) scale: (1,1,1) and no rotation.

        Returns itself."""
        self.PositionLocal = glm.vec3(0)
        self.RotationLocal = glm.quat()
        self.ScaleLocal = glm.vec3(1)
        if recursive:
            for child in self.Children:
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

        - If extrinsic the rotation will be around the world axes, ignoring previous rotations."""
        return glm.degrees(Euler.fromQuatTo(self.RotationLocal, order, extrinsic))

    def setEuler(self, degrees: glm.vec3, order: str = 'ZXY', extrinsic: bool = True) -> "Transform":
        """Converts the given euler anlges to quaternion and sets the rotation property.

        - If extrinsic the rotation will be around the world axes, ignoring previous rotations.

        Returns itself."""
        self.RotationLocal = Euler.toQuatFrom(glm.radians(degrees), order, extrinsic)
        return self

    def lookAtLocal(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.

        - Direction is considered as local space.

        Returns itself."""
        direction = glm.normalize(direction)
        dirDot = abs(glm.dot(direction, (0, 1, 0)))
        upAxis = up if dirDot < 0.999 else glm.vec3(1, 0, 0)
        self.RotationLocal = glm.quatLookAtRH(direction, upAxis)
        return self

    def lookAtWorld(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.

        - Direction is considered as world space.

        Returns itself."""
        parentWorldRotationInverse = (self.Parent.RotationWorldInverse if self.Parent else glm.mat4())
        direction = parentWorldRotationInverse * direction

        return self.lookAtLocal(direction, up)

    def attach(self, *nodes: "Transform", keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Attaches the given transforms to this one as a child.

        - If keep***** is true -> the given transform will be modified to keep its spatial algiment in world space.

        - If the transform is detatched first if it already has parent.

        - Nothing will change if the node already has a relation to this transform.

        Returns itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError('Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be parent of itself')
            if node in self.Children: continue

            # detach
            if node._Parent is not None:
                node._Parent.detach(node, keepPosition, keepRotation)

            # attatch
            self.Children.append(node)
            node._Parent = self

            # correct Rotation
            if keepPosition: node.PositionLocal = self.SpaceWorldInverse * node.PositionLocal
            if keepRotation: node.RotationLocal = self.RotationWorldInverse * node.RotationLocal
            if keepScale: node.ScaleLocal = self.ScaleWorldInverse * node.ScaleLocal
        return self

    def detach(self, *nodes: "Transform", keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Detachs the given child transform.

        - If keep***** is true -> the given transform will be modified to keep its spatial algiment in world space.

        - Nothing will change if the node has no relation to this transform.

        Returns itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError('Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be detachd from itself')
            if node.Parent is self and node not in self.Children: raise ValueError(f'Joint "{node.Name}" has "{self.Name}" as parent, bust does not exist in the children list. Avoid manual child parent modifications')
            if node.Parent is None or node.Parent != self: continue

            # correct properties
            if keepPosition: node.PositionLocal = self.SpaceWorld * node.PositionLocal
            if keepRotation: node.RotationLocal = self.RotationWorld * node.RotationLocal
            if keepScale: node.ScaleLocal = self.ScaleWorld * node.ScaleLocal

            # detach
            self.Children.remove(node)
            node._Parent = None
        return self

    def clearParent(self, keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """Detaches/detachs itself from the parent.

        - If keep***** is true -> the given transform will be modified to keep its world property.

        Returns itself."""
        if self.Parent is not None:
            self.Parent.detach(self, keepPosition=keepPosition, keepRotation=keepRotation, keepScale=keepScale)
        return self

    def clearChildren(self, keepPosition: bool = False, keepRotation: bool = False, keepScale: bool = False) -> "Transform":
        """detachs all children of this transform.

        - If keep***** is true -> the given transform will be modified to keep its world property.

        Returns itself."""
        if (len(self.Children) > 0):
            self.detach(*self.Children, keepPosition=keepPosition, keepRotation=keepRotation, keepScale=keepScale)
        return self

    def applyPosition(self, position: glm.vec3 = None, recursive: bool = False) -> "Transform":
        """Changes the position of this transform and updates its children to keep them spatial unchanged.

        - If position is None -> the transform resets its position to (0, 0, 0).

        - If position IS set -> the given position is added to the current position.

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

        - If rotation is None -> the transform resets its rotation to (1, 0, 0, 0).

        - If rotation IS set -> the given rotation is added to the current rotation.

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

        - If scale is NOT set -> the transform resets its scale to (1, 1, 1).

        - If scale IS set -> the given scale is added to the current scale.

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
        """Returns the hierarchy, inclunding this transform, in order of 'depth first' with their index and depth.

        - Order of the tuple -> [transform, index, depth]"""
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

        - If isEqual is true, the name has to be equal to the pattern. Otherwise the pattern must only appear anywhere in the name."""
        result = []

        selfname = self.Name if caseSensitive else self.Name.lower()
        if not caseSensitive: pattern = pattern.lower()

        if (isEqual and pattern == selfname) or (not isEqual and pattern in selfname):
            result.append(self)
        for child in self.Children:
            result.extend(child.filter(pattern, isEqual, caseSensitive))

        return result

    def filterRegex(self, pattern: str) -> list["Transform"]:
        """Tries to find transforms that matches the pattern in their name name."""
        result = []

        if re.match(pattern, self.Name) is not None:
            result.append(self)
        for child in self.Children:
            result.extend(child.filter(pattern))

        return result
