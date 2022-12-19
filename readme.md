# spatial-transform
Libary for creating spatial space hierarchies, like game engines and renderes would do, to have diffrent rotations, scale and positions which also rely on their parent transformation.

This package is created for my master thesis and aims about integrety but not performance. For the most of the calculations the package [PyGLM](https://github.com/Zuzu-Typ/PyGLM) is used.

## Install
``` batch
pip install spatial-transform
 ```
## Features
- Space properties in local and world space
    - Position
    - Rotation (Quaternion & Euler)
    - Scale
    - Space 4x4 matrix
    - Axes direction (Forward, Up, Right)
- Hierarchical
    - Transforms can have a parent and children
    - World space depends on the parent
    - Transforms can be easily attached / detachatched
- Python
    - Every method is documented in code with docstrings
    - Every method has type hinting
- Includes a static class for euler angle conversions.
## Notes
This libary works with the same space as [openGL and GLM](https://www.evl.uic.edu/ralph/508S98/coordinates.html), which is:
- right handed
- Y+ is up
- Z- is forward
- Positive rotation is counter clockwise

Euler angles can be set with methods on the transform. ``SetEuler()`` and ``GetEuler()`` support any instrinic or extrinsic rotation order. Angles are degrees for the ``Transform`` class but radians for the ``Euler`` class.

## Examples
### Create and attach transforms
``` python
from SpatialTransform import Transform as T

# create and attach
root = T('Hips', position=(0,2,0)).attach(
    T('LeftLegUpper', position=(+.2, 0, 0)).lookAtLocal((0,-1,0)).attach(
        T('LeftLegLower', position=(0, 0, -1)).attach(
            T('LeftLegFoot', position=(0, 0, -1)).lookAtLocal((-1,0,0)))),
    T('RightLegUpper', position=(-.2, 0, 0)).lookAtLocal((0,-1,0)).attach(
        T('RightLegLower', position=(0, 0, -1)).attach(
            T('RightLegFoot', position=(0, 0, -1)).lookAtLocal((-1,0,0)))))

# print info about created structure
root.printTree()
for item, index, depth in root.layout():
    print(f'Position:{item.pointToWorld((0,0,0))} Forward:{item.ForwardWorld} {item.Name}')
```

### Change properties
``` python
# gets a transform in the hierarchy
foot = root.filter('LeftLegFoot', isEqual=True)[0]

# basic property changes
foot.Position = (0.5, 0, 0)
foot.Rotation = (1, 0, 0, 0) # quaternion
foot.Scale = (2, 1, .5)

# use methods for changes
foot.lookAtWorld((-5, 0, 0))
foot.applyRotation()
foot.setEuler((0, -90, 25))
foot.clearParent(keepPosition=True, keepRotation=True)

# transform spatial data
foot.pointToWorld((1,1,1)) # converts a point from local to world space
foot.pointToLocal((1,1,1)) # inverse of pointToWorld

foot.directionToWorld((0,0,1)) # converts a direction from local to world space
foot.directionToLocal((0,0,1)) # inverse of pointToWorld
```

### Euler angles conversions
``` python
from SpatialTransform import Euler

# rotations are in radians here
matrix = Euler.toMatFrom((1, 2, .5), 'YZX', True)
quaternion = Euler.toQuatFrom((1, 2, .5), 'YZX', True)

angles1 = Euler.fromMatTo(matrix, 'XYZ', False)
angles2 = Euler.fromQuatTo(quaternion, 'XYZ', False)

print(angles1 - angles2)
```
