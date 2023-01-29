import re
import glm
import random
import string
from .pose import Pose


class Transform(Pose):
    """Spatial definition of an linear space with position, rotation and scale.

    - Based on 'Pose' class, extended with parent child relation ship propertis and methods.
    - Space is defined as right handed where -> Y+ is up, and X+ is right and Z- is forward.
    - Positive rotations are counter clockwise."""

    @property
    def Name(self) -> str:
        """Name of the transform."""
        return self._Name

    @Name.setter
    def Name(self, value: str) -> None:
        self._Name = value

    @property
    def SpaceWorld(self) -> glm.mat4:
        """Transform space with respect to the parent."""
        return (self.Parent.SpaceWorld if self.Parent else glm.mat4()) * self.Space

    @property
    def SpaceWorldInverse(self) -> glm.mat4:
        """Inverted transform space with respect to the parent."""
        return glm.inverse(self.SpaceWorld)

    @property
    def PositionWorld(self) -> glm.vec3:
        """World position of the space."""
        parentSpace = self.Parent.SpaceWorld if self.Parent else glm.mat4()
        return parentSpace * self.Position

    @PositionWorld.setter
    def PositionWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self.Parent.SpaceWorldInverse if self.Parent else glm.mat4()
        self._Position = parentSpaceInverse * value

    @property
    def RotationWorld(self) -> glm.quat:
        """World rotation of the space."""
        parentSpace = self.Parent.RotationWorld if self.Parent else glm.quat()
        return parentSpace * self.Rotation

    @RotationWorld.setter
    def RotationWorld(self, value: glm.quat) -> None:
        parentSpaceInverse = self.Parent.RotationWorldInverse if self.Parent else glm.quat()
        self._Rotation = parentSpaceInverse * value

    @property
    def RotationWorldInverse(self) -> glm.quat:
        """Inverse world rotation of the space."""
        return glm.inverse(self.RotationWorld)

    @property
    def ScaleWorld(self) -> glm.vec3:
        """World scale of the space."""
        parentSpace = self.Parent.ScaleWorld if self.Parent else glm.vec3(1)
        return parentSpace * self.Scale

    @ScaleWorld.setter
    def ScaleWorld(self, value: glm.vec3) -> None:
        parentSpaceInverse = self.Parent.ScaleWorldInverse if self.Parent else glm.vec3(1)
        self._Scale = parentSpaceInverse * value

    @property
    def ScaleWorldInverse(self) -> glm.vec3:
        """Inverse world scale of the space."""
        return (1.0 / self.ScaleWorld)

    @property
    def ForwardWorld(self) -> glm.vec3:
        """Current rotation of the Z-axis in world space."""
        return (self.RotationWorld * (0, 0, -1, 0)).xyz

    @property
    def RightWorld(self) -> glm.vec3:
        """Current rotation of the X-axis in world space."""
        return (self.RotationWorld * (1, 0, 0, 0)).xyz

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
        """Creates a new transform. Parameters are considered as local space properties."""
        super().__init__(position, rotation, scale)

        self.Name = name if name is not None else ''.join(random.choice(string.ascii_letters) for _ in range(8))
        self._Parent: "Transform" = None
        self._Children: list["Transform"] = []

    def __repr__(self) -> str:
        return (f"{self.Name}")

    def __str__(self) -> str:
        return (f"Name: {self.Name}, Children: {len(self.Children)}, {super().__str__()}")

    def reset(self, recursive: bool = False) -> "Transform":
        """Resets the transform to pos: (0,0,0) scale: (1,1,1) and no rotation.

        Returns itself."""
        super().reset()

        if recursive:
            for child in self.Children:
                child.reset(recursive=True)

        return self

    def pointToWorld(self, point: glm.vec3) -> glm.vec3:
        """Transforms a given point in this  space to world space."""
        return self.SpaceWorld * point

    def pointToLocal(self, point: glm.vec3) -> glm.vec3:
        """Transforms a given point in world space to this  space."""
        return self.SpaceWorldInverse * point

    def directionToWorld(self, direction: glm.vec3) -> glm.vec3:
        """Transforms a given direction in this  space to world space."""
        return self.RotationWorld * direction

    def directionToLocal(self, direction: glm.vec3) -> glm.vec3:
        """Transforms a given direction in world space to this  space."""
        return self.RotationWorldInverse * direction

    def lookAt(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        return super().lookAt(direction, up)

    def lookAtWorld(self, direction: glm.vec3, up: glm.vec3 = glm.vec3(0, 1, 0)) -> "Transform":
        """Sets Rotation so the Z- axis aligns with the given direction.

        - Direction is considered as world space.

        Returns itself."""
        parentWorldRotationInverse = (self.Parent.RotationWorldInverse if self.Parent else glm.mat4())
        direction = parentWorldRotationInverse * direction

        return super().lookAt(direction, up)

    def setEuler(self, degrees: glm.vec3, order: str = 'ZXY', extrinsic: bool = True) -> "Transform":
        return super().setEuler(degrees, order, extrinsic)

    def attach(self, *nodes: "Transform", keep: list[str] = ['position', 'rotation', 'scale']) -> "Transform":
        """Attaches the given transforms to this one as a child.

        - If keep contains properties -> the property is modified to keep its spatial algiment in world space.
        - If keep is None or empty -> Local space propteries do not change.
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
                node._Parent.detach(node, keep=keep)

            # attatch
            self.Children.append(node)
            node._Parent = self

            # correct world space alignment
            if keep is not None:
                if 'position' in keep: node.Position = self.SpaceWorldInverse * node.Position
                if 'rotation' in keep: node.Rotation = self.RotationWorldInverse * node.Rotation
                if 'scale' in keep: node.Scale = self.ScaleWorldInverse * node.Scale
        return self

    def detach(self, *nodes: "Transform", keep: list[str] = ['position', 'rotation', 'scale']) -> "Transform":
        """Detachs the given child transform.

        - If keep contains properties -> the property is modified to keep its spatial algiment in world space.
        - If keep is None or empty -> Local space propteries do not change.
        - Nothing will change if the node has no relation to this transform.

        Returns itself."""
        for node in nodes:
            # validate given joint
            if node is None: raise ValueError('Given joint value is None')
            if node is self: raise ValueError(f'Joint "{self.Name}" cannot be detachd from itself')
            if node.Parent is self and node not in self.Children: raise ValueError(f'Joint "{node.Name}" has "{self.Name}" as parent, bust does not exist in the children list. Avoid manual child parent modifications')
            if node.Parent is None or node.Parent != self: continue

            # correct world space alignment
            if keep is not None:
                if 'position' in keep: node.Position = self.SpaceWorld * node.Position
                if 'rotation' in keep: node.Rotation = self.RotationWorld * node.Rotation
                if 'scale' in keep: node.Scale = self.ScaleWorld * node.Scale

            # detach
            self.Children.remove(node)
            node._Parent = None
        return self

    def clearParent(self, keep: list[str] = ['position', 'rotation', 'scale']) -> "Transform":
        """Detaches/detachs itself from the parent.

        - If keep contains properties -> the property is modified to keep its spatial algiment in world space.
        - If keep is None or empty -> Local space propteries do not change.

        Returns itself."""
        if self.Parent is not None:
            self.Parent.detach(self, keep=keep)
        return self

    def clearChildren(self, keep: list[str] = ['position', 'rotation', 'scale']) -> "Transform":
        """detachs all children of this transform.

        - If keep contains properties -> the property is modified to keep its spatial algiment in world space.
        - If keep is None or empty -> Local space propteries do not change.

        Returns itself."""
        if (len(self.Children) > 0):
            self.detach(*self.Children, keep=keep)
        return self

    def applyPosition(
            self,
            position: glm.vec3 = None,
            recursive: bool = False,
            includeParentChange: list[Pose] = [],
            includeChildChange: list[Pose] = []) -> "Transform":
        """Changes the position of this transform and updates its children to keep them spatial unchanged.

        - If position is None -> the transform resets its position to (0, 0, 0).
        - If position IS set -> the given position is added to the current position.
        - If includeParentChange contains poses -> Those poses recieve the same change as this transfrom.
        - If includeChildChange contains poses -> Those poses recieve the same change as the children.

        Returns itself."""
        # define positional change
        change = -self.Position if position is None else position
        changeInverse = glm.inverse(self.Rotation) * ((1.0 / self.Scale) * -change)

        # apply changes to itself
        self.Position += change
        for pose in includeParentChange:
            pose.Position += change

        # apply changes to children
        for child in self.Children:
            child.Position += changeInverse
            for pose in includeChildChange:
                pose.Position *= changeInverse

            # may do it recursively
            if recursive: child.applyRotation(position, recursive=True)

        return self

    def applyRotation(
            self,
            rotation: glm.quat = None,
            recursive: bool = False,
            includeParentChange: list[Pose] = [],
            includeChildChange: list[Pose] = []) -> "Transform":
        """Changes the rotation of this transform and updates its children to keep them spatial unchanged.

        - If rotation is None -> the transform resets its rotation to (1, 0, 0, 0).
        - If rotation IS set -> the given rotation is added to the current rotation.
        - If includeParentChange contains poses -> Those poses recieve the same change as this transfrom.
        - If includeChildChange contains poses -> Those poses recieve the same change as the children.

        Returns itself."""
        # define rotational change
        change = glm.inverse(self.Rotation) if rotation is None else rotation
        changeInverse = glm.inverse(change)

        # apply changes to itself
        self.Rotation = self.Rotation * change
        for pose in includeParentChange:
            pose.Rotation = pose.Rotation * change

        # apply changes to children
        for child in self.Children:
            child.Position = changeInverse * child.Position
            child.Rotation = changeInverse * child.Rotation
            for pose in includeChildChange:
                pose.Position = changeInverse * pose.Position
                pose.Rotation = changeInverse * pose.Rotation

            # may do it recursively
            if recursive: child.applyRotation(rotation, recursive=True)

        return self

    def appyScale(
            self,
            scale: glm.vec3 = None,
            recursive: bool = False,
            includeParentChange: list[Pose] = [],
            includeChildChange: list[Pose] = []) -> "Transform":
        """Changes the scale of the transform and updates its children to keep them spatial unchanged.

        - If scale is NOT set -> the transform resets its scale to (1, 1, 1).
        - If scale IS set -> the given scale is added to the current scale.
        - If includeParentChange contains poses -> Those poses recieve the same change as this transfrom.
        - If includeChildChange contains poses -> Those poses recieve the same change as the children.

        Returns itself."""
        # define change in scale
        change = (1.0 / self.Scale) if scale is None else scale
        changeInverse = (1.0 / change)

        # apply changes to itself
        self.Scale = self.Scale * change
        for pose in includeParentChange:
            pose.Scale = pose.Scale * change

        # keep space for children
        for child in self.Children:
            child.Position = changeInverse * child.Position
            child.Scale = changeInverse * child.Scale
            for pose in includeChildChange:
                pose.Position = changeInverse * pose.Position
                pose.Scale = changeInverse * pose.Scale

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

    def duplicate(self, recursive: bool = False) -> "Transform":
        """Returns a duplicate of this transform.

        - If recursive is True -> All child transfroms are duplicated too, into this duplicate."""

        newChildren = [child.duplicate(recursive=True) for child in self.Children] if recursive else []
        newDuplicate = Transform(self.Name, self.Position, self.Rotation, self.Scale)
        return newDuplicate.attach(*newChildren, keep=None)
