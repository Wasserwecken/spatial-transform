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
            self._SpaceLocal = glm.scale(self._SpaceLocal, self._Scale)
            self._SpaceLocal = self._SpaceLocal * glm.mat4_cast(self._Rotation)
            self.__isOutdatedLocal = False
        return glm.mat4(self._SpaceLocal)
    @SpaceLocal.setter
    def SpaceLocal(self, value:glm.mat4) -> None:
        self._SpaceLocal = value
        glm.decompose(value,
            self._Scale,
            self._Rotation,
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
    def Rotation(self) -> glm.quat:
        """Local Rotation of this space."""
        return glm.quat(self._Rotation)
    @Rotation.setter
    def Rotation(self, value:glm.quat) -> None:
        self._Rotation = glm.quat(value)
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
        """Current local Rotation of the Z-Axis"""
        return self._Rotation * (0,0,-1)
    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current Rotation of the Z-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (0,0,-1,0))

    @property
    def RightLocal(self) -> glm.vec3:
        """Current local Rotation of the X-Axis"""
        return self._Rotation * (1,0,0)
    @property
    def RightWorld(self) -> glm.vec3:
        """Current Rotation of the X-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (1,0,0,0))


    @property
    def UpLocal(self) -> glm.vec3:
        """Current local Rotation of the Y-Axis"""
        return self._Rotation * (0,1,0)
    @property
    def UpWorld(self) -> glm.vec3:
        """Current Rotation of the Y-Axis in world space"""
        return glm.normalize(self.SpaceWorld * (0,1,0,0))


    @property
    def Parent(self) -> "Transform":
        """Transform where this one aligns in repsect to it."""
        return self._Parent
    @property
    def Children(self) -> list["Transform"]:
        """Attachted transforms."""
        return self._Children


    def __init__(self, name:str = None, position:glm.vec3 = glm.vec3(), Rotation:glm.quat = glm.quat(), scale:glm.vec3 = glm.vec3(1)) -> None:
        """Creates a new transform. Parameters are considerd as local space"""
        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._Parent:"Transform" = None
        self._Children:list["Transform"] = []

        self.reset()
        self._Position = glm.vec3(position)
        self._Scale = glm.vec3(scale)
        self._Rotation = glm.quat(Rotation)
        self.__isOutdatedLocal = True

    def __repr__(self) -> str:
        return (f"Name: {self._Name}")

    def __str__(self) -> str:
        return (f"Name: {self._Name}"
            + f"\nPos: {self._Position}"
            + f"\nRot: {self.Rotation}"
            + f"\nScale: {self._Scale}"
            + f"\nChildren: {len(self._Children)}"
        )

    def reset(self) -> "Transform":
        """Resets the whole transform to pos: 0,0,0 scale: 1,1,1 and no rotation"""
        self._SpaceLocal = glm.mat4()
        self.__isOutdatedLocal = True
        return self

    def resetPosition(self) -> "Transform":
        """Resets the position to 0,0,0"""
        self.Position = (0,0,0)
        return self

    def resetRotation(self) -> "Transform":
        """Resets rotation"""
        self.Rotation = glm.quat()
        return self

    def resetScale(self) -> "Transform":
        """Resets scale to 1,1,1"""
        self.Scale = (1,1,1)
        return self

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


    def getEuler(self, order:str = 'ZXY') -> glm.vec3:
        """Returns the current Rotation as euler angles in the given order.

        The angles are in degrees and intrinsic."""
        return glm.degrees(Euler.fromQuatTo(self.Rotation, order))

    def setEuler(self, degrees:glm.vec3, order:str = 'ZXY', intrinsic = True) -> "Transform":
        self.Rotation = Euler.toQuatFrom(glm.radians(degrees), order, intrinsic)
        return self


    def lookAtLocal(self, direction:glm.vec3, up:glm.vec3 = glm.vec3(0,1,0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction. Direction is considered as local space. Returns the transform itself."""
        direction = glm.normalize(direction)
        dirDot = abs(glm.dot(direction, (0,1,0)))
        self._Rotation = glm.quatLookAtRH(direction, up if dirDot < 0.999 else glm.vec3(1,0,0))
        self.__isOutdatedLocal = True
        return self

    def lookAtWorld(self, direction:glm.vec3, up:glm.vec3 = glm.vec3(0,1,0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.  Direction is considered as world space Returns the transform itself."""
        parentSpace = (self._Parent.SpaceWorld if self._Parent else glm.mat4())
        self.lookAtLocal(glm.inverse(parentSpace) * direction, up)
        return self


    def remove(self, node:"Transform", keepPosition:bool = False, keepRotation:bool = False, keepScale:bool = False) -> "Transform":
        """Removes the given child transform.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        # validate given joint
        if node is None: raise ValueError(f'Given joint value is None')
        if node is self: raise ValueError(f'Joint "{self.Name}" cannot be removed from itself')

        # correct properties
        if keepPosition: node.Position = node.pointToWorld((0,0,0))
        if keepRotation: node.Rotation = node.Rotation * self.Rotation
        if keepScale: node.Scale = node.Scale * self.Scale

        # remove
        self._Children.remove(node)
        node._Parent = None
        return self

    def clearParent(self, keepPosition:bool = False, keepRotation:bool = False, keepScale:bool = False) -> "Transform":
        """Detaches/removes itself from the parent.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        if self._Parent is not None: self._Parent.remove(self, keepPosition, keepRotation, keepScale)

    def clearChildren(self, keepPosition:bool = False, keepRotation:bool = False, keepScale:bool = False) -> "Transform":
        """Removes all children of this transform.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        for child in self.Children:
            self.remove(child, keepPosition, keepRotation, keepScale)
        return self

    def append(self, *nodes:"Transform", keepPosition:bool = False, keepRotation:bool = False, keepScale:bool = False) -> "Transform":
        """Attaches the given transforms to this one as a child.

        If keep***** is true, the given transform will be modified to keep its world property.

        Returns the transform itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError(f'Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be parent of itself')

            # remove
            if node._Parent is not None:
                node._Parent.remove(node, keepPosition, keepRotation)

            # attatch
            self._Children.append(node)
            node._Parent = self

            # correct Rotation
            if keepPosition: node.Position = self.pointToLocal(node.Position)
            if keepRotation: node.Rotation = node.Rotation * (glm.inverse(self.Rotation))
            if keepScale: node.Scale = node.Scale * (1 / self.Scale)
        return self


    def applyPosition(self, position:glm.vec3 = None, recursive:bool = False) -> "Transform":
        """Changes the position of this transform and updates its children to keep them spatial unchanged.
        Will update the position of this transform and postions of its children.

        If no position is given, the transform resets its own position to (0,0,0).

        If a position is given, the position is added to this transform.

        Returns the transform itself."""
        # define position change
        change = self.Position if position is None else -position

        # apply change
        self.Position = self.Position - position
        for child in self.Children:
            child.Position = child.Position + position

            # propagatte it recursively
            if recursive: child.applyPosition(position, recursive)
        return self

    def applyRotation(self, rotation:glm.quat = None, recursive:bool = False) -> "Transform":
        """Changes the rotation of this transform and updates its children to keep them spatial unchanged.
        Will update the Rotation of this transform and postion and Rotation of its children.

        If no rotation is given, the transform resets its own rotation to none.

        If a rotation is given, the rotation is added to this transform.

        Returns the transform itself."""
        # define rotation change
        change = self.Rotation if rotation is None else glm.inverse(rotation)

        # apply change
        self.Rotation = self.Rotation * glm.inverse(change)
        for child in self.Children:
            child.Position = change * child.Position
            child.Rotation = change * child.Rotation

            # propagatte it recursively
            if recursive: child.applyRotation(rotation, recursive)
        return self

    def appyScale(self, scale:glm.vec3 = None, recursive:bool = False) -> "Transform":
        """Changes the scale of this transform and updates its children to keep them spatial unchanged.
        Will update the Scale of this transform and postion and scale of its children.

        If no scale is given, the transform resets its own scale to (1,1,1).

        If a scale is given, the scale is added to this transform.

        Returns the transform itself."""
        # define scale change
        change = self.Scale if scale is None else 1 / glm.vec3(scale)

        # apply change
        self.Scale = self.Scale * glm.div(1, change)
        for child in self.Children:
            child.Position = change * child.Position
            child.Scale = change * child.Scale

            # propagatte it recursively
            if recursive: child.appyScale(scale, recursive)
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
